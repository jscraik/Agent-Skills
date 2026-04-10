#!/usr/bin/env python3
"""Deterministic benchmark checks for the skill-authoring family.

This script enforces equivalent contract/eval/security baseline requirements for:
- plugins/skill-factory/skills/skill-builder
- plugins/skill-factory/skills/skill-creator
- plugins/skill-factory/skills/skill-installer
- plugins/plugin-factory/skills/plugin-creator

It is designed for CI and local gates where live LLM eval execution is not required.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set

try:
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    already_reexec = os.environ.get("SKILL_FAMILY_PYYAML_REEXEC") == "1"
    if not already_reexec and __name__ == "__main__":
        env = dict(os.environ)
        env["SKILL_FAMILY_PYYAML_REEXEC"] = "1"
        uv_bin = shutil.which("uv")
        if uv_bin:
            os.execvpe(
                uv_bin,
                [
                    uv_bin,
                    "run",
                    "--python",
                    "3.12",
                    "--with",
                    "pyyaml",
                    "--with",
                    "jsonschema",
                    "python",
                    __file__,
                    *sys.argv[1:],
                ],
                env,
            )
        preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
        if preferred.exists():
            os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    raise SystemExit(
        "PyYAML is required for validate_skill_authoring_family_benchmarks.py. "
        "Run with `uv run --python 3.12 --with pyyaml --with jsonschema python ...`."
    ) from exc

_JSONSCHEMA_AVAILABLE = importlib.util.find_spec("jsonschema") is not None


REPO_ROOT = Path(__file__).resolve().parents[1]

# Severity ranking for baseline regression comparison (higher = worse)
SEVERITY_RANK = {"INFO": 0, "WARN": 1, "FAIL": 2}
_SCHEMA_DIR = REPO_ROOT / "plugins" / "skill-factory" / "skills" / "skill-builder" / "references"
_CONTRACT_SCHEMA_PATH = _SCHEMA_DIR / "contract.schema.yaml"
_EVALS_SCHEMA_PATH = _SCHEMA_DIR / "evals.schema.yaml"
DEFAULT_FAMILY_SKILLS = (
    "plugins/skill-factory/skills/skill-builder",
    "plugins/skill-factory/skills/skill-creator",
    "plugins/skill-factory/skills/skill-installer",
    "plugins/plugin-factory/skills/plugin-creator",
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

# Indirect PI tokens to scan in non-eval reference files and SKILL.md body.
# evals.yaml is intentionally excluded — PI language there is test coverage, not injection.
_INDIRECT_PI_TOKENS = re.compile(
    r"ignore (all |previous )?instructions|disregard (all )?previous|"
    r"forget (your|all) instructions|bypass (safety|all checks)|"
    r"you are now|your new instructions are|act as if",
    re.IGNORECASE,
)

# Minimum ratio of cases that must carry deterministic_checks (non-trivial dict).
_DET_CHECK_COVERAGE_WARN_THRESHOLD = 0.30

# rubric_version staleness: WARN if older than this many days.
_RUBRIC_VERSION_STALE_DAYS = 180

# rubric_version family divergence: WARN if spread across members exceeds this many days.
_RUBRIC_VERSION_DIVERGENCE_DAYS = 90

# Optional contract fields expected at gold standard; absence produces WARN (not FAIL).
_RECOMMENDED_CONTRACT_KEYS = {"rollback_procedure", "observability"}


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


def _load_schema(schema_path: Path) -> Any:
    """Load a YAML schema file; return None if unavailable."""
    if not schema_path.exists():
        return None
    try:
        return yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _validate_with_schema(
    skill_rel: str,
    data: Dict[str, Any],
    schema_path: Path,
    fail_code: str,
    context: str,
) -> List[Finding]:
    """Validate *data* against a JSON Schema YAML file using jsonschema.

    Returns a FAIL finding for each schema violation, or a WARN if jsonschema
    is not installed (soft dependency so CI without the package still runs).
    """
    findings: List[Finding] = []
    if not _JSONSCHEMA_AVAILABLE:
        findings.append(
            Finding(
                "WARN",
                f"{fail_code}_NO_JSONSCHEMA",
                skill_rel,
                f"jsonschema not installed; skipping schema validation for {context}. "
                "Install via: uv pip install jsonschema (or run with `uv run --python 3.12 --with jsonschema ...`).",
            )
        )
        return findings

    schema = _load_schema(schema_path)
    if schema is None:
        findings.append(
            Finding(
                "WARN",
                f"{fail_code}_SCHEMA_MISSING",
                skill_rel,
                f"schema file not found at {schema_path.relative_to(REPO_ROOT)}; "
                "skipping JSON Schema validation",
            )
        )
        return findings

    import jsonschema as _js  # type: ignore  # noqa: PLC0415

    validator_cls = _js.Draft202012Validator
    try:
        validator_cls.check_schema(schema)
    except _js.SchemaError as exc:  # noqa: BLE001
        findings.append(
            Finding("WARN", f"{fail_code}_SCHEMA_INVALID", skill_rel, f"schema file is invalid: {exc.message}")
        )
        return findings

    for error in sorted(validator_cls(schema).iter_errors(data), key=lambda e: list(e.path)):
        path = " > ".join(str(p) for p in error.path) if error.path else "(root)"
        findings.append(
            Finding("FAIL", fail_code, skill_rel, f"{context} schema violation at {path}: {error.message}")
        )

    return findings


def _normalize_skill_name(skill_dir: Path) -> str:
    return skill_dir.name


def _canonical_skill_rel(skill_rel: str) -> str:
    """Return canonical repo-relative skill path for the given relative path."""
    repo_root = REPO_ROOT.resolve()
    requested = (repo_root / skill_rel).resolve()
    try:
        return requested.relative_to(repo_root).as_posix()
    except ValueError:
        return skill_rel.strip("/")


def _dedupe_requested_skills(skills: Sequence[str]) -> tuple[str, ...]:
    """Deduplicate requested skills by canonical resolved path while preserving order."""
    seen: set[str] = set()
    deduped: list[str] = []
    for skill in skills:
        canonical = _canonical_skill_rel(skill)
        if canonical in seen:
            continue
        seen.add(canonical)
        deduped.append(skill)
    return tuple(deduped)


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

    # P2.5: Gold-standard recommended fields (WARN, not FAIL)
    missing_recommended = sorted(_RECOMMENDED_CONTRACT_KEYS - set(contract.keys()))
    if missing_recommended:
        findings.append(
            Finding(
                "WARN",
                "CONTRACT_RECOMMENDED_KEYS",
                skill_rel,
                f"contract.yaml missing recommended gold-standard keys: {', '.join(missing_recommended)} "
                "(add rollback_procedure and observability for operational readiness)",
            )
        )

    # Item 3: JSON Schema structural validation
    findings.extend(_validate_with_schema(skill_rel, contract, _CONTRACT_SCHEMA_PATH, "CONTRACT_SCHEMA", "contract.yaml"))

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
    cases_with_det_checks = 0
    happy_missing_smoke: List[str] = []

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
            # P1.3: happy-path cases without smoke can't catch regressions in quick runs
            if category == "happy" and "smoke" not in normalized_modes:
                happy_missing_smoke.append(case_id or f"#{idx}")

        if _case_has_pi_language(case):
            has_pi_case = True

        if category == "pressure":
            commands = _case_forbidden_commands(case)
            if commands and commands.intersection(RISKY_COMMAND_TOKENS):
                has_pressure_command_guard = True

        # P1.1: track deterministic_checks coverage
        det = case.get("deterministic_checks")
        if isinstance(det, dict) and det:
            cases_with_det_checks += 1

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

    # P1.1: deterministic_checks coverage ratio
    total_valid = len([c for c in cases if isinstance(c, dict)])
    if total_valid > 0:
        coverage = cases_with_det_checks / total_valid
        if coverage < _DET_CHECK_COVERAGE_WARN_THRESHOLD:
            findings.append(
                Finding(
                    "WARN",
                    "EVALS_DET_CHECK_COVERAGE",
                    skill_rel,
                    f"only {cases_with_det_checks}/{total_valid} cases ({coverage:.0%}) have deterministic_checks; "
                    f"aim for ≥{_DET_CHECK_COVERAGE_WARN_THRESHOLD:.0%} to reduce reliance on LLM-graded outputs alone",
                )
            )

    # P1.3: happy-path cases without smoke mode
    if happy_missing_smoke:
        findings.append(
            Finding(
                "WARN",
                "EVALS_HAPPY_NO_SMOKE",
                skill_rel,
                f"{len(happy_missing_smoke)} happy-path case(s) lack smoke eval_mode and won't catch regressions "
                f"in quick runs: {', '.join(happy_missing_smoke)}",
            )
        )

    # Item 3: JSON Schema structural validation
    findings.extend(_validate_with_schema(skill_rel, evals, _EVALS_SCHEMA_PATH, "EVALS_SCHEMA", "evals.yaml"))

    return findings


def _validate_task_profile(skill_rel: str, skill_dir: Path, *, expected_scope_skill: str) -> List[Finding]:
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
    if scope_skill != expected_scope_skill:
        findings.append(
            Finding(
                "FAIL",
                "TASK_PROFILE_SCOPE",
                skill_rel,
                f"scope_skill must equal {expected_scope_skill} (found: {scope_skill or 'missing'})",
            )
        )

    # P2.6: rubric_version must be a valid ISO date and not stale
    rubric_version = str(profile.get("rubric_version", "")).strip()
    if rubric_version:
        try:
            rubric_date = datetime.strptime(rubric_version, "%Y-%m-%d").date()
            today = date.today()
            age_days = (today - rubric_date).days
            if age_days > _RUBRIC_VERSION_STALE_DAYS:
                findings.append(
                    Finding(
                        "WARN",
                        "TASK_PROFILE_RUBRIC_STALE",
                        skill_rel,
                        f"rubric_version {rubric_version} is {age_days} days old "
                        f"(threshold: {_RUBRIC_VERSION_STALE_DAYS} days); review and update rubric",
                    )
                )
        except ValueError:
            findings.append(
                Finding(
                    "WARN",
                    "TASK_PROFILE_RUBRIC_FORMAT",
                    skill_rel,
                    f"rubric_version '{rubric_version}' is not a valid ISO date (expected YYYY-MM-DD)",
                )
            )

    return findings


def _validate_reference_pi(skill_rel: str, skill_dir: Path) -> List[Finding]:
    """P2.4: Scan SKILL.md body and non-eval reference files for indirect PI language.

    evals.yaml is intentionally excluded — PI language there is test coverage.
    """
    findings: List[Finding] = []

    # SKILL.md body (everything after closing frontmatter ---)
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        raw = skill_md.read_text(encoding="utf-8", errors="replace")
        # Strip frontmatter before scanning
        parts = raw.split("---", 2)
        body = parts[2] if len(parts) >= 3 else raw
        if _INDIRECT_PI_TOKENS.search(body):
            findings.append(
                Finding(
                    "WARN",
                    "SKILL_MD_INDIRECT_PI",
                    skill_rel,
                    "SKILL.md body contains language matching indirect prompt injection patterns; "
                    "verify this is intentional (e.g., documenting attack patterns)",
                )
            )

    # References directory — scan .md and .yaml but skip evals.yaml
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_file in sorted(refs_dir.iterdir()):
            if ref_file.name == "evals.yaml":
                continue  # PI language in evals is deliberate test coverage
            if ref_file.suffix not in {".md", ".yaml", ".yml"}:
                continue
            try:
                text = ref_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if _INDIRECT_PI_TOKENS.search(text):
                findings.append(
                    Finding(
                        "WARN",
                        "REFERENCE_INDIRECT_PI",
                        skill_rel,
                        f"reference file {ref_file.name} contains indirect prompt injection patterns; "
                        "review for unintended instructions that could influence skill behaviour",
                    )
                )

    return findings


def _validate_skill(skill_rel: str) -> List[Finding]:
    skill_dir = (REPO_ROOT / skill_rel).resolve()
    canonical_rel = _canonical_skill_rel(skill_rel)
    findings: List[Finding] = []

    if not skill_dir.exists():
        return [Finding("FAIL", "SKILL_DIR_MISSING", skill_rel, "skill directory not found")]

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        findings.append(Finding("FAIL", "SKILL_MD_MISSING", skill_rel, "missing SKILL.md"))

    findings.extend(_validate_contract(skill_rel, skill_dir))
    findings.extend(_validate_evals(skill_rel, skill_dir))
    findings.extend(_validate_task_profile(skill_rel, skill_dir, expected_scope_skill=canonical_rel))
    findings.extend(_validate_reference_pi(skill_rel, skill_dir))
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
    _default_baseline = REPO_ROOT / "artifacts" / "validation" / "baselines" / "family-gate-baseline.json"
    parser.add_argument(
        "--write-baseline",
        metavar="PATH",
        nargs="?",
        const=str(_default_baseline),
        help="Write current findings as the regression baseline (default path if no arg given)",
    )
    parser.add_argument(
        "--check-baseline",
        metavar="PATH",
        nargs="?",
        const=str(_default_baseline),
        help="Compare current findings against a saved baseline and fail on regressions",
    )
    args = parser.parse_args(list(argv))

    skills = _dedupe_requested_skills(tuple(args.skill) if args.skill else DEFAULT_FAMILY_SKILLS)
    findings: List[Finding] = []
    for skill in skills:
        findings.extend(_validate_skill(skill))

    # P2.6: family-level rubric_version divergence check
    rubric_dates: List[tuple[str, date]] = []
    for skill in skills:
        skill_dir = (REPO_ROOT / skill).resolve()
        profile_path = skill_dir / "references" / "task-profile.json"
        if profile_path.exists():
            try:
                profile = _load_json(profile_path)
                rv = str(profile.get("rubric_version", "")).strip()
                rubric_dates.append((skill, datetime.strptime(rv, "%Y-%m-%d").date()))
            except (ValueError, Exception):  # noqa: BLE001
                pass
    if len(rubric_dates) >= 2:
        dates_only = [d for _, d in rubric_dates]
        spread_days = (max(dates_only) - min(dates_only)).days
        if spread_days > _RUBRIC_VERSION_DIVERGENCE_DAYS:
            oldest = min(rubric_dates, key=lambda x: x[1])
            newest = max(rubric_dates, key=lambda x: x[1])
            findings.append(
                Finding(
                    "WARN",
                    "TASK_PROFILE_RUBRIC_DIVERGENCE",
                    "family",
                    f"rubric_version spread across family is {spread_days} days "
                    f"(oldest: {oldest[0]} at {oldest[1]}, newest: {newest[0]} at {newest[1]}); "
                    f"align family rubric versions within {_RUBRIC_VERSION_DIVERGENCE_DAYS} days",
                )
            )

    # Item 5: Baseline write/check
    if args.write_baseline:
        baseline_path = Path(args.write_baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_data = {
            "schema_version": 1,
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "skills": list(skills),
            "findings": [{"level": f.level, "code": f.code, "skill": f.skill} for f in findings],
            "summary": {
                "fail_count": sum(1 for f in findings if f.level == "FAIL"),
                "warn_count": sum(1 for f in findings if f.level == "WARN"),
            },
        }
        baseline_path.write_text(json.dumps(baseline_data, indent=2) + "\n", encoding="utf-8")
        print(f"[family-benchmark] baseline written: {baseline_path}")

    regression_findings: List[Finding] = []
    if args.check_baseline:
        baseline_path = Path(args.check_baseline)
        if not baseline_path.exists():
            print(f"[family-benchmark] ERROR: baseline not found at {baseline_path}; regression check required", file=sys.stderr)
            return 1
        else:
            try:
                baseline_data = _load_json(baseline_path)
                # Group baseline findings by (code, skill) -> max severity rank
                baseline_by_code: Dict[tuple, int] = {}
                for f in baseline_data.get("findings", []):
                    if isinstance(f, dict):
                        key = (f["code"], f["skill"])
                        rank = SEVERITY_RANK.get(f["level"], 0)
                        baseline_by_code[key] = max(baseline_by_code.get(key, 0), rank)

                # Group current findings by (code, skill) -> max severity rank
                current_by_code: Dict[tuple, int] = {}
                for f in findings:
                    key = (f.code, f.skill)
                    rank = SEVERITY_RANK.get(f.level, 0)
                    current_by_code[key] = max(current_by_code.get(key, 0), rank)

                # Find regressions: new findings or worsened severity
                regressions = []
                for key, current_rank in current_by_code.items():
                    code, skill = key
                    baseline_rank = baseline_by_code.get(key, -1)
                    if current_rank > baseline_rank:
                        # Severity increased or completely new finding
                        level_name = {v: k for k, v in SEVERITY_RANK.items()}.get(current_rank, "UNKNOWN")
                        regressions.append((level_name, code, skill))

                if regressions:
                    for level, code, skill in sorted(regressions):
                        regression_findings.append(
                            Finding("FAIL", "BASELINE_REGRESSION", skill, f"new or worsened finding vs baseline: {level} {code}")
                        )
                else:
                    print("[family-benchmark] baseline check: no regressions detected")
            except Exception as exc:  # noqa: BLE001
                print(f"[family-benchmark] ERROR: could not load/parse baseline: {exc}", file=sys.stderr)
                return 1

    all_findings = list(findings) + regression_findings

    if args.format == "json":
        _print_json(all_findings, skills)
    else:
        _print_text(all_findings, skills)

    fails = [f for f in all_findings if f.level == "FAIL"]
    return 2 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
