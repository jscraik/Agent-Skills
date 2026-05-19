#!/usr/bin/env python3
"""Validate HE stage skills carry the Skill Factory operator shape."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in minimal runtimes.
    yaml = None


REQUIRED_CONTRACT_MARKERS = {
    "operator_contract:": "missing operator_contract block",
    "description_contract:": "missing description contract",
    "immediate_operator_path:": "missing immediate operator path",
    "source_order:": "missing source order",
    "tool_resolution:": "missing tool resolution",
    "freshness_rule:": "missing freshness rule",
    "boundaries:": "missing boundaries",
    "retry_and_stop:": "missing retry/stop rule",
    "validation_tiers:": "missing validation tiers",
    "concise_output:": "missing concise output contract",
}

REQUIRED_CONTRACT_KEYS = {
    key.removesuffix(":")
    for key in REQUIRED_CONTRACT_MARKERS
    if key != "operator_contract:"
}
REQUIRED_OUTPUT_FIELDS = {
    "changed_artifacts",
    "important_decisions",
    "validation",
    "residual_risks",
    "next_stage_or_blocker",
}
REQUIRED_VALIDATION_TIERS = {"fast", "standard", "deep"}
REQUIRED_BOUNDARIES = {
    "external": "external write boundary missing",
    "destructive": "destructive action boundary missing",
    "closure": "closure proof boundary missing",
}
FORBIDDEN_ACTIVE_AUTHORITY = ("archive", "deferred", "cache")

REQUIRED_EVAL_ORIGIN_KEYS = {"type", "source", "protects_against"}

REQUIRED_EVAL_CASES = {
    "happy-operator-path": "missing happy operator-path eval",
    "edge-missing-inputs-proceed": "missing missing-input proceed eval",
    "pressure-no-governance-bloat": "missing governance-bloat pressure eval",
    "pressure-live-not-archive": "missing live-source pressure eval",
    "negative-neighboring-lane": "missing neighboring-lane negative eval",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def iter_skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills"
    if not skills_root.exists():
        return []
    return sorted(path.parent for path in skills_root.glob("*/SKILL.md"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def add_finding(findings: list[dict[str, str]], path: Path, code: str, message: str) -> None:
    findings.append({"path": rel(path), "code": code, "message": message})


def load_yaml(path: Path, findings: list[dict[str, str]]) -> dict:
    if yaml is None:
        return {"__raw__": path.read_text(encoding="utf-8")}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # pragma: no cover - exact parser messages vary.
        add_finding(findings, path, "YAML_PARSE", f"YAML parse failed: {exc}")
        return {}
    if not isinstance(data, dict):
        add_finding(findings, path, "YAML_SHAPE", "YAML root must be a mapping")
        return {}
    return data


def check_operator_contract(contract: Path, findings: list[dict[str, str]]) -> None:
    data = load_yaml(contract, findings)
    raw = data.get("__raw__")
    if isinstance(raw, str):
        for marker, message in REQUIRED_CONTRACT_MARKERS.items():
            if marker not in raw:
                add_finding(findings, contract, "CONTRACT_SHAPE", message)
        if "first_action:" not in raw:
            add_finding(findings, contract, "CONTRACT_SEMANTIC", "immediate_operator_path.first_action must be non-empty")
        lowered = raw.lower()
        if not any(term in lowered for term in ("live", "current", "readback")):
            add_finding(findings, contract, "CONTRACT_SEMANTIC", "contract must require current/live/readback evidence")
        if not all(term in lowered for term in FORBIDDEN_ACTIVE_AUTHORITY):
            add_finding(findings, contract, "CONTRACT_SEMANTIC", "contract must reject archive, deferred, and cache paths as active authority")
        if not all(f"{tier}:" in lowered for tier in REQUIRED_VALIDATION_TIERS):
            add_finding(findings, contract, "CONTRACT_SEMANTIC", "validation_tiers must contain fast, standard, and deep")
        return

    operator = data.get("operator_contract")
    if not isinstance(operator, dict):
        add_finding(findings, contract, "CONTRACT_SHAPE", "operator_contract must be a mapping")
        return

    for key in REQUIRED_CONTRACT_KEYS:
        if key not in operator:
            add_finding(findings, contract, "CONTRACT_SEMANTIC", f"operator_contract missing {key}")

    immediate = operator.get("immediate_operator_path")
    if not isinstance(immediate, dict) or not str(immediate.get("first_action", "")).strip():
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "immediate_operator_path.first_action must be non-empty")

    source_order = operator.get("source_order")
    source_text = " ".join(str(item) for item in source_order or [])
    if not isinstance(source_order, list) or not source_order:
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "source_order must be a non-empty list")
    if not any(term in source_text.lower() for term in ("live", "current", "readback")):
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "source_order must require current/live/readback evidence")

    action_state = str((operator.get("freshness_rule") or {}).get("action_state", "")).lower()
    if not any(term in action_state for term in ("live", "targeted", "current")):
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "freshness_rule.action_state must require live/current targeted reads")

    boundary_text = json.dumps(operator.get("boundaries", {}), sort_keys=True).lower()
    for needle, message in REQUIRED_BOUNDARIES.items():
        if needle not in boundary_text:
            add_finding(findings, contract, "CONTRACT_SEMANTIC", message)
    if not all(term in boundary_text for term in FORBIDDEN_ACTIVE_AUTHORITY):
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "boundaries must reject archive, deferred, and cache paths as active authority")

    tiers = operator.get("validation_tiers")
    if not isinstance(tiers, dict) or set(tiers) != REQUIRED_VALIDATION_TIERS:
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "validation_tiers must contain exactly fast, standard, and deep")

    default_fields = set((operator.get("concise_output") or {}).get("default_fields") or [])
    if default_fields != REQUIRED_OUTPUT_FIELDS:
        add_finding(findings, contract, "CONTRACT_SEMANTIC", "concise_output.default_fields must stay short and standard")


def check_eval_contract(evals: Path, findings: list[dict[str, str]]) -> None:
    data = load_yaml(evals, findings)
    raw = data.get("__raw__")
    if isinstance(raw, str):
        lowered = raw.lower()
        for case_id, message in REQUIRED_EVAL_CASES.items():
            if f"id: {case_id}" not in raw:
                add_finding(findings, evals, "EVAL_SHAPE", message)
        if lowered.count("origin:") < len(REQUIRED_EVAL_CASES):
            add_finding(findings, evals, "EVAL_ORIGIN", "operator-shape evals must include origin metadata")
        if not all(term in lowered for term in FORBIDDEN_ACTIVE_AUTHORITY):
            add_finding(findings, evals, "EVAL_SEMANTIC", "pressure-live-not-archive must name archive, deferred, and cache risks")
        return

    cases = data.get("cases")
    if not isinstance(cases, list):
        add_finding(findings, evals, "EVAL_SHAPE", "cases must be a list")
        return

    cases_by_id = {case.get("id"): case for case in cases if isinstance(case, dict)}
    for case_id, message in REQUIRED_EVAL_CASES.items():
        case = cases_by_id.get(case_id)
        if not case:
            add_finding(findings, evals, "EVAL_SHAPE", message)
            continue
        origin = case.get("origin")
        if not isinstance(origin, dict):
            add_finding(findings, evals, "EVAL_ORIGIN", f"{case_id} missing origin metadata")
            continue
        missing = REQUIRED_EVAL_ORIGIN_KEYS - set(origin)
        if missing:
            add_finding(findings, evals, "EVAL_ORIGIN", f"{case_id} origin missing {', '.join(sorted(missing))}")

    live_case = cases_by_id.get("pressure-live-not-archive") or {}
    live_text = json.dumps(live_case, sort_keys=True).lower()
    if not all(term in live_text for term in FORBIDDEN_ACTIVE_AUTHORITY):
        add_finding(findings, evals, "EVAL_SEMANTIC", "pressure-live-not-archive must name archive, deferred, and cache risks")


def check_skill(skill_dir: Path, _root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    contract = skill_dir / "references" / "contract.yaml"
    evals = skill_dir / "references" / "evals.yaml"

    if not contract.exists():
        add_finding(findings, skill_dir, "CONTRACT_MISSING", "missing references/contract.yaml")
    else:
        text = contract.read_text(encoding="utf-8")
        for marker, message in REQUIRED_CONTRACT_MARKERS.items():
            if marker not in text:
                add_finding(findings, contract, "CONTRACT_SHAPE", message)
        check_operator_contract(contract, findings)

    if not evals.exists():
        add_finding(findings, skill_dir, "EVALS_MISSING", "missing references/evals.yaml")
    else:
        text = evals.read_text(encoding="utf-8")
        for case_id, message in REQUIRED_EVAL_CASES.items():
            if f"id: {case_id}" not in text:
                add_finding(findings, evals, "EVAL_SHAPE", message)
        check_eval_contract(evals, findings)

    return findings


def check_cross_skill_semantics(skill_dirs: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    first_actions: dict[str, list[Path]] = {}
    for skill_dir in skill_dirs:
        contract = skill_dir / "references" / "contract.yaml"
        if not contract.exists() or yaml is None:
            continue
        data = load_yaml(contract, findings)
        operator = data.get("operator_contract")
        if not isinstance(operator, dict):
            continue
        first_action = str((operator.get("immediate_operator_path") or {}).get("first_action", "")).strip()
        if first_action:
            first_actions.setdefault(first_action, []).append(contract)

    for first_action, paths in first_actions.items():
        if len(paths) > 1:
            joined = ", ".join(rel(path.parent.parent) for path in paths)
            add_finding(
                findings,
                paths[0],
                "CONTRACT_DUPLICATE_FIRST_ACTION",
                f"immediate_operator_path.first_action is reused across stages: {joined}",
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    skill_dirs = iter_skill_dirs(root)
    findings: list[dict[str, str]] = []
    for skill_dir in skill_dirs:
        findings.extend(check_skill(skill_dir, root))
    findings.extend(check_cross_skill_semantics(skill_dirs))

    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not findings else "fail",
        "checked_skills": len(skill_dirs),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for finding in findings:
            print(f"{finding['code']}: {finding['path']}: {finding['message']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
