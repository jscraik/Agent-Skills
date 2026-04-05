#!/usr/bin/env python3
"""Deterministic benchmark checks for the skill-authoring family.

This script enforces equivalent contract/eval/security baseline requirements for:
- utilities/skill-builder
- skills-system/skill-creator
- skills-system/skill-installer
- skills-system/plugin-creator

It is designed for CI and local gates where live LLM eval execution is not required.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set

try:
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_FAMILY_PYYAML_REEXEC") == "1"
    if preferred.exists() and not already_reexec and __name__ == "__main__":
        env = dict(os.environ)
        env["SKILL_FAMILY_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    raise SystemExit("PyYAML is required for validate_skill_authoring_family_benchmarks.py") from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FAMILY_SKILLS = (
    "utilities/skill-builder",
    "skills-system/skill-creator",
    "skills-system/skill-installer",
    "skills-system/plugin-creator",
)

REQUIRED_CONTRACT_KEYS = {
    "purpose",
    "triggers",
    "inputs",
    "outputs",
    "non_goals",
    "risks",
}
REQUIRED_CASE_CATEGORIES = {"happy", "edge", "negative", "pressure"}
REQUIRED_TASK_PROFILE_KEYS = {
    "schema_version",
    "profile_id",
    "scope_skill",
    "scope_profile",
    "rubric_version",
    "evaluator_version",
    "persona_set_id",
    "thresholds",
    "criteria",
    "delegation",
    "learning_posture",
}
RISKY_COMMAND_TOKENS = {"curl", "wget", "rm -rf", "netcat", "nc"}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    skill: str
    message: str


def _load_yaml(path: Path) -> Dict[str, Any]:
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("expected a YAML mapping/object")
    return obj


def _load_json(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("expected a JSON object")
    return obj


def _normalize_skill_name(skill_dir: Path) -> str:
    return skill_dir.name


def _case_has_pi_language(case: Dict[str, Any]) -> bool:
    haystacks = [str(case.get("name", "")), str(case.get("prompt", ""))]
    low = "\n".join(haystacks).lower()
    return any(token in low for token in ("prompt injection", "jailbreak", "ignore previous instructions", "bypass safety"))


def _case_forbidden_commands(case: Dict[str, Any]) -> Set[str]:
    deterministic = case.get("deterministic_checks")
    if not isinstance(deterministic, dict):
        return set()
    raw = deterministic.get("forbidden_commands")
    if not isinstance(raw, list):
        return set()
    out: Set[str] = set()
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.add(item.strip().lower())
    return out


def _validate_contract(skill_rel: str, skill_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    contract_path = skill_dir / "references" / "contract.yaml"
    if not contract_path.exists():
        findings.append(Finding("FAIL", "CONTRACT_MISSING", skill_rel, "missing references/contract.yaml"))
        return findings

    try:
        contract = _load_yaml(contract_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "CONTRACT_PARSE", skill_rel, f"could not parse contract.yaml: {exc}"))
        return findings

    missing = sorted(REQUIRED_CONTRACT_KEYS - set(contract.keys()))
    if missing:
        findings.append(
            Finding("FAIL", "CONTRACT_KEYS", skill_rel, f"contract.yaml missing required keys: {', '.join(missing)}")
        )

    schema_version = str(contract.get("schema_version", "")).strip()
    if not schema_version:
        findings.append(Finding("FAIL", "CONTRACT_SCHEMA_VERSION", skill_rel, "contract.yaml missing schema_version"))

    return findings


def _validate_evals(skill_rel: str, skill_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        findings.append(Finding("FAIL", "EVALS_MISSING", skill_rel, "missing references/evals.yaml"))
        return findings

    try:
        evals = _load_yaml(evals_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "EVALS_PARSE", skill_rel, f"could not parse evals.yaml: {exc}"))
        return findings

    schema_version = str(evals.get("schema_version", "")).strip()
    if schema_version != "2.0":
        findings.append(
            Finding("FAIL", "EVALS_SCHEMA_VERSION", skill_rel, f"evals schema_version must be 2.0 (found: {schema_version or 'missing'})")
        )

    expected_skill_name = _normalize_skill_name(skill_dir)
    skill_name = str(evals.get("skill_name", "")).strip()
    if skill_name != expected_skill_name:
        findings.append(
            Finding("FAIL", "EVALS_SKILL_NAME", skill_rel, f"evals skill_name mismatch: expected {expected_skill_name}, found {skill_name or 'missing'}")
        )

    cases = evals.get("cases")
    if not isinstance(cases, list) or not cases:
        findings.append(Finding("FAIL", "EVALS_CASES", skill_rel, "evals.yaml must include a non-empty cases list"))
        return findings

    if len(cases) < 7:
        findings.append(Finding("FAIL", "EVALS_CASE_COUNT", skill_rel, f"evals must include at least 7 cases (found {len(cases)})"))
    elif len(cases) <= 8:
        findings.append(Finding("WARN", "EVALS_CASE_COUNT_MINIMAL", skill_rel, f"evals meet the minimum with only {len(cases)} cases; aim for ≥9 for meaningful coverage across all 4 required categories"))

    seen_ids: Set[str] = set()
    categories: Set[str] = set()
    has_pi_case = False
    has_negative_should_trigger_false = False
    has_pressure_command_guard = False

    for idx, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            findings.append(Finding("FAIL", "EVALS_CASE_SHAPE", skill_rel, f"case #{idx} is not an object"))
            continue

        case_id = str(case.get("id", "")).strip()
        if not case_id:
            findings.append(Finding("FAIL", "EVALS_CASE_ID", skill_rel, f"case #{idx} missing id"))
        elif case_id in seen_ids:
            findings.append(Finding("FAIL", "EVALS_CASE_ID_DUP", skill_rel, f"duplicate case id: {case_id}"))
        else:
            seen_ids.add(case_id)

        category = str(case.get("category", "")).strip().lower()
        if category:
            categories.add(category)

        should_trigger = case.get("should_trigger")
        if category == "negative" and should_trigger is False:
            has_negative_should_trigger_false = True

        eval_modes = case.get("eval_modes")
        if not isinstance(eval_modes, list) or not eval_modes:
            findings.append(Finding("FAIL", "EVALS_EVAL_MODES", skill_rel, f"case {case_id or idx} missing non-empty eval_modes"))
        else:
            normalized_modes = {str(mode).strip().lower() for mode in eval_modes}
            invalid_modes = sorted(normalized_modes - {"smoke", "release"})
            if invalid_modes:
                findings.append(
                    Finding(
                        "FAIL",
                        "EVALS_EVAL_MODES_INVALID",
                        skill_rel,
                        f"case {case_id or idx} has invalid eval_modes: {', '.join(invalid_modes)}",
                    )
                )

        if _case_has_pi_language(case):
            has_pi_case = True

        if category == "pressure":
            commands = _case_forbidden_commands(case)
            if commands and commands.intersection(RISKY_COMMAND_TOKENS):
                has_pressure_command_guard = True

    missing_categories = sorted(REQUIRED_CASE_CATEGORIES - categories)
    if missing_categories:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_CATEGORY_COVERAGE",
                skill_rel,
                f"missing eval categories: {', '.join(missing_categories)}",
            )
        )

    if not has_negative_should_trigger_false:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_NEGATIVE_SHOULD_TRIGGER",
                skill_rel,
                "missing negative case with should_trigger: false",
            )
        )

    if not has_pi_case:
        findings.append(Finding("FAIL", "EVALS_PI_CASE", skill_rel, "missing explicit prompt injection/jailbreak pressure coverage"))

    if not has_pressure_command_guard:
        findings.append(
            Finding(
                "FAIL",
                "EVALS_PRESSURE_COMMAND_GUARD",
                skill_rel,
                "missing pressure case with deterministic forbidden command guard (curl/wget/rm -rf/netcat)",
            )
        )

    return findings


def _validate_task_profile(skill_rel: str, skill_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    profile_path = skill_dir / "references" / "task-profile.json"
    if not profile_path.exists():
        findings.append(Finding("FAIL", "TASK_PROFILE_MISSING", skill_rel, "missing references/task-profile.json"))
        return findings

    try:
        profile = _load_json(profile_path)
    except Exception as exc:  # noqa: BLE001
        findings.append(Finding("FAIL", "TASK_PROFILE_PARSE", skill_rel, f"could not parse task-profile.json: {exc}"))
        return findings

    missing = sorted(REQUIRED_TASK_PROFILE_KEYS - set(profile.keys()))
    if missing:
        findings.append(
            Finding(
                "FAIL",
                "TASK_PROFILE_KEYS",
                skill_rel,
                f"task-profile.json missing required keys: {', '.join(missing)}",
            )
        )

    scope_skill = str(profile.get("scope_skill", "")).strip()
    if scope_skill != skill_rel:
        findings.append(
            Finding(
                "FAIL",
                "TASK_PROFILE_SCOPE",
                skill_rel,
                f"scope_skill must equal {skill_rel} (found: {scope_skill or 'missing'})",
            )
        )

    return findings


def _validate_skill(skill_rel: str) -> List[Finding]:
    skill_dir = (REPO_ROOT / skill_rel).resolve()
    findings: List[Finding] = []

    if not skill_dir.exists():
        return [Finding("FAIL", "SKILL_DIR_MISSING", skill_rel, "skill directory not found")]

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        findings.append(Finding("FAIL", "SKILL_MD_MISSING", skill_rel, "missing SKILL.md"))

    findings.extend(_validate_contract(skill_rel, skill_dir))
    findings.extend(_validate_evals(skill_rel, skill_dir))
    findings.extend(_validate_task_profile(skill_rel, skill_dir))
    return findings


def _print_text(findings: Sequence[Finding], checked: Sequence[str]) -> None:
    print("[family-benchmark] checked skills:")
    for skill in checked:
        print(f"  - {skill}")

    fails = [f for f in findings if f.level == "FAIL"]
    warns = [f for f in findings if f.level == "WARN"]

    if not fails:
        print("[family-benchmark] pass: all family benchmark checks satisfied")
    else:
        print("[family-benchmark] failures:")
        for finding in fails:
            print(f"  - {finding.level} {finding.code} [{finding.skill}] {finding.message}")

    if warns:
        print("[family-benchmark] warnings:")
        for finding in warns:
            print(f"  - {finding.level} {finding.code} [{finding.skill}] {finding.message}")


def _print_json(findings: Sequence[Finding], checked: Sequence[str]) -> None:
    fails = [f for f in findings if f.level == "FAIL"]
    payload = {
        "checked": list(checked),
        "findings": [
            {
                "level": finding.level,
                "code": finding.code,
                "skill": finding.skill,
                "message": finding.message,
            }
            for finding in findings
        ],
        "pass": not fails,
    }
    print(json.dumps(payload, indent=2))


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate equivalent family benchmark requirements.")
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Skill path relative to repo root (repeatable). Defaults to all family members.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(list(argv))

    skills = tuple(args.skill) if args.skill else DEFAULT_FAMILY_SKILLS
    findings: List[Finding] = []
    for skill in skills:
        findings.extend(_validate_skill(skill))

    if args.format == "json":
        _print_json(findings, skills)
    else:
        _print_text(findings, skills)

    fails = [f for f in findings if f.level == "FAIL"]
    return 2 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
