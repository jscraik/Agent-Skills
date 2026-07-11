#!/usr/bin/env python3
"""
run_skill_evals.py

Run evaluation cases for a Codex skill using Codex CLI, Codex (Kimi/Zai), and/or OpenAI CLI.

Capabilities:
- Loads SKILL.md -> skill name
- Loads Infrastructure/references/evals.yaml (v1 compatible; v2 fields optional)
- Per case, runs one runner (`--runner`), dual legacy mode (`--dual-run`), or explicit multi-runner list (`--runners`)
- Captures final output and optional Codex JSONL traces
- Applies acceptance assertions (text and JSON)
- Applies deterministic Codex trace checks (tier 1 hard / tier 2 budgets)
- Produces merged scorecards and exits non-zero on configured gate failures

Usage:
  ~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>

Exit codes:
  0  all required gates passed
  1  parsing/IO/configuration error
  2  one or more required eval gates failed
"""

from __future__ import annotations

import argparse
import atexit
import datetime as dt
import html
import json
import math
import os
import re
import shutil
import shlex
import subprocess as sp
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
WORKSPACE_ROOT = SCRIPT_DIR.parents[3]
for path_entry in (str(REPO_ROOT), str(SCRIPT_DIR)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    already_reexec = os.environ.get("SKILL_CREATOR_PYYAML_REEXEC") == "1"
    preferred_site_packages: Optional[Path] = None
    if preferred.exists():
        lib_root = preferred.parent.parent / "lib"
        for candidate in sorted(lib_root.glob("python*/site-packages")):
            if candidate.exists():
                preferred_site_packages = candidate
                break

    # Import-safe fallback: when this module is imported by tests from a Python
    # interpreter without PyYAML, pull PyYAML from the dedicated helper venv
    # instead of re-executing the CLI entrypoint.
    if preferred_site_packages is not None and str(preferred_site_packages) not in sys.path:
        sys.path.insert(0, str(preferred_site_packages))
        import yaml  # type: ignore
    elif preferred.exists() and not already_reexec and __name__ == "__main__":
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        os.execve(str(preferred), [str(preferred), __file__, *sys.argv[1:]], env)
    else:
        sys.stderr.write(
            "ERROR: PyYAML is required to run run_skill_evals.py.\n\n"
            "Fix:\n"
            "  ~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <path/to/skill-dir-or-SKILL.md>\n"
        )
        raise SystemExit(1)

from deterministic_trace_checks import evaluate_trace, load_jsonl_events  # noqa: E402
from eval_signal_contract import (  # noqa: E402
    EXPECTED_SIGNAL_FLOW_KEY,
    EXPECTED_SIGNAL_FORBIDDEN_DIMENSIONS,
    EXPECTED_SIGNAL_COMPOSITE_KEY,
    EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY,
    EXPECTED_SIGNAL_METRIC_KEY,
    EXPECTED_SIGNAL_MISSING_KEY,
    EXPECTED_SIGNAL_RISK_FACTORS_KEY,
    EXPECTED_SIGNAL_REQUIRED_DIMENSIONS,
    expected_signal_items,
    parse_min_expected_signal_score,
)

_FM_DELIM = re.compile(r"^\s*---\s*$")
_CODEX_HELP_CACHE: Dict[str, Optional[str]] = {}
_RUNNER_CHOICES = ["codex", "codex-kimi", "codex-zai", "openai", "discovery-smoke"]
_TIMEOUT_PROFILE_CHOICES = ["default", "codex-heavy", "discovery-heavy"]
_EVAL_MODE_CHOICES = ["standard", "smoke", "release"]
_CODEX_AUTH_ENV_VARS = ("OPENAI_API_KEY", "OPENAI_API_TOKEN", "OPENAI_ACCESS_TOKEN")
_BASELINE_TYPE_CHOICES = {
    "no_skill",
    "previous_version",
    "prior_skill_snapshot",
    "neutral_repo_baseline",
    "competing_skill",
    "human_reference",
}
_KNOWN_HARD_GATES = {
    "no_false_completion",
    "no_validation_bypass",
    "no_unsafe_command",
    "no_missing_required_artifact",
    "no_unredacted_secret",
    "no_unresolved_source_projection_ownership",
    "versioned_release_evidence",
}
_ROUND_STATE_CHOICES = {
    "prepared",
    "running",
    "evidence_captured",
    "reviewed",
    "decision_recorded",
    "blocked",
}
_READINESS_STATE_CHOICES = {
    "starter_valid",
    "comparison_incomplete",
    "comparison_blocked",
    "downstream_ready",
}
_METRIC_AVAILABILITY_CHOICES = {"available", "unavailable"}
RUNNER_BLOCKER_TAXONOMY: Dict[str, str] = {
    "blocked_validation": "The selected eval configuration was invalid or produced no executable case evidence.",
    "blocked_user_input": "The runner requested user input and should not be classified as a hang.",
    "blocked_auth": "The runner stopped on authentication or credential setup.",
    "blocked_runtime": "The runner was blocked by local runtime, sandbox, or model-capacity limits.",
    "timeout_no_output": "The runner timed out without producing final output.",
    "timeout_partial_output": "The runner timed out after producing partial output.",
}
SNYK_MANIFEST_NAMES: Set[str] = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "Gemfile.lock",
    "composer.json",
    "composer.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradle.lockfile",
    "settings.gradle",
    "settings.gradle.kts",
    "packages.config",
    "Paket.dependencies",
    "pubspec.yaml",
    "Package.swift",
}
SNYK_MANIFEST_SUFFIXES: Tuple[str, ...] = (".csproj", ".fsproj", ".vbproj")
SNYK_MANIFEST_EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".venv",
    "__pycache__",
    "budget-archive",
    "node_modules",
    "cache",
    "artifacts",
    "fixtures",
    "tmp",
}

# Script-level options (used to disambiguate `--codex-arg --foo` intent).
_SCRIPT_OPTIONS: Set[str] = {
    "--list-cases",
    "--runner",
    "--runners",
    "--dual-run",
    "--smoke",
    "--case",
    "--eval-mode",
    "--category",
    "--workspace",
    "--sandbox",
    "--ask-for-approval",
    "--timeout-sec",
    "--timeout-profile",
    "--model",
    "--profile",
    "--codex-fallback-profile",
    "--codex-home",
    "--codex-bin",
    "--codex-bin",
    "--openai-bin",
    "--codex-output-format",
    "--openai-output-format",
    "--codex-settings",
    "--codex-kimi-settings",
    "--codex-zai-settings",
    "--codex-kimi-command",
    "--codex-zai-command",
    "--codex-arg",
    "--openai-arg",
    "--capture-jsonl",
    "--reports-dir",
    "--scorecard-out",
    "--format",
    "--tier2-mode",
    "--codex-arg",
    "-h",
    "--help",
}


def _resolve_skill_md_path(path_like: str) -> Path:
    p = Path(path_like).expanduser().resolve()
    return (p / "SKILL.md") if p.is_dir() else p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _parse_frontmatter(raw: str) -> Tuple[Dict[str, Any], str]:
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise ValueError("SKILL.md is empty")

    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip():
            start_idx = i
            break
    if start_idx is None or not _FM_DELIM.match(lines[start_idx]):
        raise ValueError("Missing YAML frontmatter. Expected `---` as first non-empty line.")

    end_idx: Optional[int] = None
    for j in range(start_idx + 1, len(lines)):
        if _FM_DELIM.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError("Unterminated YAML frontmatter. Missing closing `---`.")

    yaml_text = "".join(lines[start_idx + 1 : end_idx])
    fm_obj = yaml.safe_load(yaml_text)
    if fm_obj is None:
        fm: Dict[str, Any] = {}
    elif isinstance(fm_obj, dict):
        fm = fm_obj
    else:
        raise ValueError("Frontmatter YAML must be a mapping/object.")

    body = "".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm, body


def load_skill_name(skill_md_path: Path) -> str:
    raw = _read_text(skill_md_path)
    fm, _ = _parse_frontmatter(raw)
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("SKILL.md frontmatter missing valid `name`.")
    return name.strip()


def load_skill_frontmatter(skill_md_path: Path) -> Dict[str, Any]:
    raw = _read_text(skill_md_path)
    fm, _ = _parse_frontmatter(raw)
    return fm


def _git_metadata(path: Path) -> Dict[str, Optional[str]]:
    repo_hint = str(path)
    metadata: Dict[str, Optional[str]] = {"commit": None, "branch": None}
    for key, args in {
        "commit": ["rev-parse", "HEAD"],
        "branch": ["rev-parse", "--abbrev-ref", "HEAD"],
    }.items():
        try:
            proc = sp.run(
                ["git", "-C", repo_hint, *args],
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception:
            metadata[key] = None
            continue
        if proc.returncode == 0:
            metadata[key] = proc.stdout.strip() or None
    return metadata


Assertion = Union[str, Dict[str, Any]]


@dataclass(frozen=True)
class EvalCase:
    id: str
    name: str
    prompt: str
    acceptance: List[Assertion]
    output_schema: Optional[str] = None
    should_trigger: Optional[bool] = None
    category: Optional[str] = None
    deterministic_checks: Optional[Dict[str, Any]] = None
    expected_signals: Optional[Dict[str, Any]] = None
    budgets: Optional[Dict[str, Any]] = None
    prepend_skill: bool = True
    timeout_sec: Optional[float] = None
    timeout_profile: Optional[str] = None
    smoke_mode: Optional[str] = None
    eval_modes: Optional[Tuple[str, ...]] = None
    baseline_type: Optional[str] = None
    comparison_inputs: Optional[Dict[str, Any]] = None
    iteration_round_state: Optional[str] = None
    metric_availability: Optional[str] = None
    readiness_state: Optional[str] = None
    comparison_review_artifact: Optional[str] = None
    neutral_baseline_approval_id: Optional[str] = None
    claim_ids: Tuple[str, ...] = ()
    realistic: Optional[bool] = None
    why_realistic: Optional[str] = None
    baseline_id: Optional[str] = None
    hard_gates: Tuple[str, ...] = ()
    expected_evidence: Tuple[str, ...] = ()
    unit: Optional[str] = None
    given: Optional[str] = None
    should: Optional[str] = None
    actual_artifact: Optional[str] = None
    expected_artifact: Optional[str] = None
    reproduce: Optional[str] = None
    raw_response_artifact: Optional[str] = None
    judge_detail_artifact: Optional[str] = None
    pass_rate_threshold: Optional[float] = None
    pass_rate_calibration_artifact: Optional[str] = None


_VALID_CATEGORIES = {"happy", "edge", "negative", "pressure"}
_RITEWAY_CASE_FIELDS = ("unit", "given", "should", "actual_artifact", "expected_artifact", "reproduce")
_GENERIC_ACCEPTANCE_TERMS = {
    "done",
    "pass",
    "passes",
    "success",
    "successful",
    "valid",
    "validation",
    "complete",
    "completed",
    "works",
    "routes",
    "uses the skill",
    "uses skill",
    "skill selected",
    "expected skill",
}


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_optional_case_artifact_path(case_dir: Path, artifact: Optional[str], workspace_root: Optional[Path] = None) -> Optional[str]:
    if artifact is None:
        return None
    candidate = Path(artifact)
    if candidate.is_absolute():
        raise ValueError("Eval case artifact paths must be repo-relative or case-relative, not absolute.")
    result = (case_dir / candidate).resolve()
    if workspace_root:
        try:
            return str(result.relative_to(workspace_root))
        except ValueError:
            pass
    return str(result)


def _resolve_existing_optional_case_artifact_path(
    case_dir: Path,
    artifact: Optional[str],
    workspace_root: Optional[Path] = None,
) -> Optional[str]:
    if artifact is None:
        return None
    candidate = Path(artifact)
    if candidate.is_absolute():
        raise ValueError("Eval case artifact paths must be repo-relative or case-relative, not absolute.")
    result = (case_dir / candidate).resolve()
    if not result.is_file():
        return None
    if workspace_root:
        try:
            return str(result.relative_to(workspace_root))
        except ValueError:
            pass
    return str(result)


def _optional_case_string(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _optional_case_artifact_string(raw: Any, *, field_name: str, case_number: int) -> Optional[str]:
    text = _optional_case_string(raw)
    if text is None:
        return None
    if Path(text).is_absolute():
        raise ValueError(f"Case #{case_number} `{field_name}` must be repo-relative or case-relative.")
    return text


def _optional_float(raw: Any, *, field_name: str, case_number: int) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise ValueError(f"Case #{case_number} `{field_name}` must be numeric when provided.")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Case #{case_number} `{field_name}` must be numeric when provided.") from exc
    if value < 0 or value > 1:
        raise ValueError(f"Case #{case_number} `{field_name}` must be between 0 and 1 when provided.")
    return value


def _normalize_eval_modes(raw: Any, *, case_number: int) -> Optional[Tuple[str, ...]]:
    if raw is None:
        return None
    if not isinstance(raw, list) or not raw:
        raise ValueError(
            f"Case #{case_number} `eval_modes` must be a non-empty list when provided; "
            f"allowed: {', '.join(_EVAL_MODE_CHOICES[1:])}."
        )
    normalized: List[str] = []
    for mode in raw:
        mode_text = str(mode).strip().lower()
        if mode_text not in {"smoke", "release"}:
            raise ValueError(
                f"Case #{case_number} `eval_modes` entries must be one of smoke, release; got {mode!r}."
            )
        if mode_text not in normalized:
            normalized.append(mode_text)
    return tuple(normalized)


def _load_evals_document(evals_path: Path) -> Dict[str, Any]:
    obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or "cases" not in obj or not isinstance(obj["cases"], list):
        raise ValueError("evals.yaml must be a mapping with `cases: [...]`.")
    generated_cases = _parse_reviewed_generated_eval_fixtures(evals_path)
    if generated_cases:
        existing_ids = {str(case.get("id") or "") for case in obj["cases"] if isinstance(case, dict)}
        obj = dict(obj)
        obj["cases"] = [
            *obj["cases"],
            *(case for case in generated_cases if str(case.get("id") or "") not in existing_ids),
        ]
    return obj


def _parse_reviewed_generated_eval_fixtures(evals_path: Path) -> List[Dict[str, Any]]:
    fixture_root = evals_path.parent / "evals"
    if not fixture_root.is_dir():
        return []
    cases: List[Dict[str, Any]] = []
    for fixture_path in sorted(fixture_root.glob("eval.*.md")):
        parsed = _parse_reviewed_generated_eval_fixture(fixture_path, evals_path.parent)
        if parsed is not None:
            cases.append(parsed)
    return cases


def _parse_reviewed_generated_eval_fixture(fixture_path: Path, references_root: Path) -> Optional[Dict[str, Any]]:
    fields: Dict[str, str] = {}
    title = fixture_path.stem.removeprefix("eval.").replace("-", " ").title()
    for raw_line in fixture_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("# "):
            title = line[2:].strip().split(":", 1)[-1].strip() or title
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {
            "Knowledge claim",
            "Behavior under test",
            "Expected agent move",
            "Failure mode",
            "Given",
            "Should",
            "Expected failure",
        }:
            fields[key] = value.strip()
    given = fields.get("Given")
    should = fields.get("Should")
    expected_move = fields.get("Expected agent move") or should
    failure_mode = fields.get("Failure mode") or fields.get("Expected failure")
    if not given or not should or not expected_move:
        return None
    raw_id = fixture_path.stem.removeprefix("eval.")
    relative_path = fixture_path.relative_to(references_root.parent).as_posix()
    artifact_name = f"{raw_id}.md"
    prompt = "\n".join([
        f"Generated reviewed scenario: {title}",
        f"Knowledge claim: {fields.get('Knowledge claim', '')}",
        f"Behavior under test: {fields.get('Behavior under test', '')}",
        f"Given: {given}",
        f"Should: {should}",
        "Produce the named artifact with observable evidence and preserve the documented failure boundary.",
    ])
    acceptance: List[Dict[str, str]] = [{"type": "expected_signal", "value": expected_move}]
    if failure_mode:
        acceptance.append({"type": "not_contains", "value": failure_mode})
    return {
        "id": f"generated-eval.{raw_id}",
        "name": title,
        "category": "edge",
        "eval_modes": ["release"],
        "realistic": True,
        "why_realistic": "Reviewed generated fixture imported from references/evals for OSS and Tessl scenario parity.",
        "unit": title,
        "given": given,
        "should": should,
        "actual_artifact": artifact_name,
        "expected_artifact": artifact_name,
        "reproduce": relative_path,
        "prompt": prompt,
        "acceptance": acceptance,
    }


def _normalize_string_list(raw: Any, *, field_name: str, case_number: Optional[int] = None) -> Tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        prefix = f"Case #{case_number} " if case_number is not None else ""
        raise ValueError(f"{prefix}`{field_name}` must be a list when provided.")
    values: List[str] = []
    for item in raw:
        text = str(item).strip()
        if text:
            values.append(text)
    return tuple(values)


def _load_claims(obj: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw = obj.get("claims")
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("`claims` must be a list when provided.")
    claims: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"claims entry #{i} must be a mapping.")
        claim_id = str(item.get("id") or "").strip()
        if not claim_id:
            raise ValueError(f"claims entry #{i} missing non-empty `id`.")
        if claim_id in claims:
            raise ValueError(f"duplicate claim id in evals.yaml: {claim_id}")
        evidence_required = item.get("evidence_required")
        if evidence_required is not None:
            _normalize_string_list(evidence_required, field_name=f"claims[{claim_id}].evidence_required")
        claims[claim_id] = dict(item)
    return claims


def _load_baselines(obj: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw = obj.get("baselines")
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("`baselines` must be a list when provided.")
    baselines: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"baselines entry #{i} must be a mapping.")
        baseline_id = str(item.get("id") or "").strip()
        if not baseline_id:
            raise ValueError(f"baselines entry #{i} missing non-empty `id`.")
        if baseline_id in baselines:
            raise ValueError(f"duplicate baseline id in evals.yaml: {baseline_id}")
        baseline_type = str(item.get("baseline_type") or "").strip().lower()
        if baseline_type and baseline_type not in _BASELINE_TYPE_CHOICES:
            raise ValueError(
                f"baselines entry #{i} `baseline_type` must be one of {sorted(_BASELINE_TYPE_CHOICES)}; "
                f"got {baseline_type!r}."
            )
        normalized = dict(item)
        if baseline_type:
            normalized["baseline_type"] = baseline_type
        baselines[baseline_id] = normalized
    return baselines


def _case_evidence_surfaces(case: EvalCase) -> List[str]:
    surfaces: List[str] = []
    if case.expected_evidence:
        surfaces.append("expected_evidence")
    if case.deterministic_checks:
        surfaces.append("deterministic_checks")
    if case.expected_signals:
        surfaces.append("expected_signals")
    if case.output_schema:
        surfaces.append("output_schema")
    if case.hard_gates:
        surfaces.append("hard_gates")
    return surfaces


def _riteway_shape_missing_fields(case: EvalCase) -> List[str]:
    return [field for field in _RITEWAY_CASE_FIELDS if not getattr(case, field)]


def _case_uses_smoke_or_release(case: EvalCase, *, eval_mode: str) -> bool:
    if eval_mode in {"smoke", "release"}:
        return True
    return bool(case.eval_modes and any(mode in {"smoke", "release"} for mode in case.eval_modes))


def _acceptance_value(item: Assertion) -> str:
    if isinstance(item, str):
        text = item.strip()
        if text.lower().startswith("regex "):
            text = text[6:].strip().strip('"').strip("'")
        return text
    if isinstance(item, dict):
        item_type = str(item.get("type") or "").strip().lower()
        if item_type in {"jsonpath_exists", "jsonpath_equals"} and item.get("path"):
            return str(item.get("path") or "").strip()
        for key in ("value", "contains", "not_contains", "regex", "expected_skill", "path"):
            if key in item:
                return str(item.get(key) or "").strip()
    return ""


def _weak_acceptance_reasons(case: EvalCase) -> List[str]:
    if case.deterministic_checks or case.expected_signals or case.output_schema or case.hard_gates:
        return []
    if not case.acceptance:
        return ["no concrete acceptance assertions"]
    values = [_acceptance_value(item).lower() for item in case.acceptance]
    weak_values = [value for value in values if value in _GENERIC_ACCEPTANCE_TERMS or len(value) < 8]
    if weak_values and len(weak_values) == len(values):
        return ["acceptance only checks trigger words or generic phrases"]
    return []


def _riteway_case_warnings(case: EvalCase, *, eval_mode: str) -> List[str]:
    warnings: List[str] = []
    if _case_uses_smoke_or_release(case, eval_mode=eval_mode):
        missing = _riteway_shape_missing_fields(case)
        if missing:
            emphasis = " realistic case" if case.realistic is True else ""
            warnings.append(
                "riteway_shape_missing"
                f"{emphasis}: add {', '.join(missing)} so failures report unit/given/should/actual/expected/reproduce"
            )
    if case.pass_rate_threshold is not None and not case.pass_rate_calibration_artifact:
        warnings.append(
            "pass_rate_threshold_advisory: threshold is advisory until pass_rate_calibration_artifact is provided"
        )
    warnings.extend(f"migration_weak_acceptance: {reason}" for reason in _weak_acceptance_reasons(case))
    return warnings


def _riteway_case_report(
    case: EvalCase,
    *,
    case_dir: Path,
    workspace_root: Path,
    runner_records: Mapping[str, Any],
) -> Dict[str, Any]:
    actual_artifact = _resolve_optional_case_artifact_path(case_dir, case.actual_artifact, workspace_root)
    expected_artifact = _resolve_optional_case_artifact_path(case_dir, case.expected_artifact, workspace_root)
    if actual_artifact is None:
        for record in runner_records.values():
            artifacts = record.get("artifacts") if isinstance(record, dict) else None
            if isinstance(artifacts, dict) and artifacts.get("final"):
                actual_artifact = str(artifacts["final"])
                break
    return {
        "unit": case.unit or case.name,
        "given": case.given,
        "should": case.should,
        "actual": actual_artifact,
        "expected": expected_artifact,
        "reproduce": case.reproduce,
        "missing_fields": _riteway_shape_missing_fields(case),
        "complete": not _riteway_shape_missing_fields(case),
    }


def _case_has_check_surface(case: EvalCase) -> bool:
    return bool(case.deterministic_checks or case.expected_signals or case.output_schema)


def _case_has_executed_check_evidence(case: EvalCase, runner_records: Mapping[str, Any]) -> bool:
    if not _case_has_check_surface(case):
        return False
    for raw_record in runner_records.values():
        if not isinstance(raw_record, dict) or not raw_record.get("passed") or raw_record.get("blocked"):
            continue
        metrics = raw_record.get("metrics") if isinstance(raw_record.get("metrics"), dict) else {}
        if case.deterministic_checks and isinstance(metrics.get("trace"), dict):
            return True
        if case.expected_signals and isinstance(metrics.get(EXPECTED_SIGNAL_METRIC_KEY), dict):
            return True
        if case.output_schema and raw_record.get("used_schema") is True:
            return True
    return False


def _case_requires_no_skill_baseline(case: EvalCase) -> bool:
    return case.baseline_type == "no_skill" and bool(case.prepend_skill)


def _baseline_comparison_from_records(
    *,
    runner_record: Mapping[str, Any],
    baseline_record: Mapping[str, Any],
) -> Dict[str, Any]:
    if baseline_record.get("status") != "executed":
        return {
            "baseline_type": baseline_record.get("baseline_type"),
            "status": baseline_record.get("status") or "unavailable",
            "reason": baseline_record.get("reason"),
        }

    with_skill_passed = bool(runner_record.get("passed"))
    baseline_passed = bool(baseline_record.get("passed"))
    skill_lift = int(with_skill_passed) - int(baseline_passed)
    return {
        "baseline_type": baseline_record.get("baseline_type"),
        "status": "compared",
        "with_skill_passed": with_skill_passed,
        "baseline_passed": baseline_passed,
        "skill_lift": skill_lift,
        "is_beneficial": with_skill_passed and not baseline_passed,
        "regression": baseline_passed and not with_skill_passed,
    }


def _evaluate_baseline_output(
    *,
    runner_name: str,
    case: EvalCase,
    skill_name: str,
    exit_code: int,
    stdout_text: str,
    stderr_text: str,
    output_text: str,
    schema_path: Optional[Path],
    codex_output_format: str,
    openai_output_format: str,
) -> Dict[str, Any]:
    failures: List[str] = []
    findings: List[str] = []
    warnings: List[str] = []
    metrics: Dict[str, Any] = {}

    blocker_class = _classify_runner_blocker(
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        exit_code=exit_code,
    )
    blocked = blocker_class is not None
    if blocked:
        failures.append(f"{blocker_class}: no-skill baseline runner was blocked before comparison.")
    elif exit_code != 0:
        failures.append(f"{runner_name} no-skill baseline returned non-zero exit code: {exit_code}")

    selected_skill = detect_skill_selected(
        skill_name=skill_name,
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        events=None,
    )
    metrics["selected_skill"] = selected_skill

    parsed_json: Optional[Any] = None
    used_json_assertions = False
    acceptance_skip_reason = _acceptance_skip_reason(exit_code=exit_code, output_text=output_text)
    if blocked:
        pass
    elif acceptance_skip_reason is not None:
        warnings.append(acceptance_skip_reason)
    else:
        expects_json = (
            (schema_path is not None and runner_name == "codex")
            or (runner_name in {"codex-kimi", "codex-zai"} and codex_output_format == "json")
            or (runner_name == "openai" and openai_output_format == "json")
        )
        if expects_json:
            try:
                parsed_json = json.loads(output_text)
            except Exception as e:  # noqa: BLE001
                failures.append(f"expected JSON output from no-skill baseline, but parsing failed: {e}")
            else:
                used_json_assertions = True

        if used_json_assertions and parsed_json is not None:
            failures.extend(
                evaluate_assertions_json(
                    parsed_json,
                    case.acceptance,
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )
        else:
            failures.extend(
                evaluate_assertions_text(
                    output_text,
                    case.acceptance,
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )

    rubric = extract_rubric_metrics(parsed_json) if parsed_json is not None else None
    if rubric:
        metrics["rubric"] = rubric

    if not blocked and case.expected_signals:
        try:
            expected_signal_result = evaluate_expected_signals(output_text, case.expected_signals)
        except ValueError as exc:
            failures.append(str(exc))
            expected_signal_result = None
        if expected_signal_result is not None:
            metrics[EXPECTED_SIGNAL_METRIC_KEY] = expected_signal_result
            min_expected_score = _extract_min_expected_signal_score(case.budgets)
            if (
                min_expected_score is not None
                and expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY] < min_expected_score
            ):
                findings.append(
                    "expected signal score below budget: "
                    f"got {expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY]} < "
                    f"min_expected_signal_score {min_expected_score:g}"
                )

    return {
        "baseline_type": "no_skill",
        "status": "executed",
        "runner": runner_name,
        "exit_code": exit_code,
        "passed": (len(failures) == 0) and not blocked,
        "blocked": blocked,
        "blocker_class": blocker_class,
        "tier1_failures": failures,
        "tier2_findings": findings,
        "warnings": warnings,
        "metrics": metrics,
        "used_schema": bool(schema_path and runner_name == "codex"),
    }


def _hard_gate_gaps_for_case(case: EvalCase, *, eval_mode: str) -> List[Dict[str, Any]]:
    if eval_mode != "release" or not case.hard_gates:
        return []
    gaps: List[Dict[str, Any]] = []
    for gate in case.hard_gates:
        if gate not in _KNOWN_HARD_GATES:
            gaps.append({
                "type": "unknown_hard_gate",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": f"release case references unknown hard_gate={gate!r}",
            })
            continue
        if not _case_has_check_surface(case):
            gaps.append({
                "type": "hard_gate_without_required_evidence",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": (
                    f"hard_gate={gate!r} requires deterministic_checks, expected_signals, "
                    "or output_schema evidence in release mode"
                ),
            })
        elif not _case_evidence_surfaces(case):
            gaps.append({
                "type": "hard_gate_without_evidence_surface",
                "case_id": case.id,
                "hard_gate": gate,
                "severity": "blocking",
                "message": "hard-gated release case must declare a concrete evidence surface",
            })
    return gaps


def load_neutral_baseline_approvals(evals_path: Path) -> Dict[str, Dict[str, Any]]:
    obj = _load_evals_document(evals_path)
    raw = obj.get("neutral_baseline_approvals")
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("`neutral_baseline_approvals` must be a list when provided.")

    approvals: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError(f"neutral_baseline_approvals entry #{i} must be a mapping.")
        approval_id = str(item.get("id") or "").strip()
        if not approval_id:
            raise ValueError(f"neutral_baseline_approvals entry #{i} missing non-empty `id`.")
        if approval_id in approvals:
            raise ValueError(f"duplicate neutral_baseline_approval id in evals.yaml: {approval_id}")
        approvals[approval_id] = dict(item)
    return approvals


def load_evals(evals_path: Path) -> List[EvalCase]:
    obj = _load_evals_document(evals_path)
    claims = _load_claims(obj)
    baselines = _load_baselines(obj)

    cases: List[EvalCase] = []
    for i, c in enumerate(obj["cases"], 1):
        if not isinstance(c, dict):
            raise ValueError(f"Case #{i} must be a mapping.")
        for k in ("name", "prompt", "acceptance"):
            if k not in c:
                raise ValueError(f"Case #{i} missing `{k}`.")
        if not isinstance(c["acceptance"], list):
            raise ValueError(f"Case #{i} `acceptance` must be a list.")

        case_id_raw = c.get("id", f"case-{i:02d}")
        case_id = str(case_id_raw).strip() or f"case-{i:02d}"

        category = c.get("category")
        if category is not None:
            category = str(category).strip().lower()
            if category and category not in _VALID_CATEGORIES:
                raise ValueError(
                    f"Case #{i} category must be one of {sorted(_VALID_CATEGORIES)}; got {category!r}."
                )

        should_trigger = c.get("should_trigger")
        if should_trigger is not None and not isinstance(should_trigger, bool):
            raise ValueError(f"Case #{i} `should_trigger` must be boolean when provided.")

        deterministic_checks = c.get("deterministic_checks")
        if deterministic_checks is not None and not isinstance(deterministic_checks, dict):
            raise ValueError(f"Case #{i} `deterministic_checks` must be a mapping when provided.")

        expected_signals = c.get("expected_signals")
        if expected_signals is not None and not isinstance(expected_signals, dict):
            raise ValueError(f"Case #{i} `expected_signals` must be a mapping when provided.")

        budgets = c.get("budgets")
        if budgets is not None and not isinstance(budgets, dict):
            raise ValueError(f"Case #{i} `budgets` must be a mapping when provided.")

        prepend_skill = c.get("prepend_skill", True)
        if not isinstance(prepend_skill, bool):
            raise ValueError(f"Case #{i} `prepend_skill` must be boolean when provided.")

        timeout_sec = c.get("timeout_sec")
        if timeout_sec is not None:
            try:
                timeout_sec = float(timeout_sec)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Case #{i} `timeout_sec` must be numeric when provided.") from exc
            if timeout_sec <= 0:
                raise ValueError(f"Case #{i} `timeout_sec` must be > 0 when provided.")

        timeout_profile = c.get("timeout_profile")
        if timeout_profile is not None:
            timeout_profile = str(timeout_profile).strip().lower()
            if timeout_profile and timeout_profile not in _TIMEOUT_PROFILE_CHOICES:
                raise ValueError(
                    f"Case #{i} `timeout_profile` must be one of {_TIMEOUT_PROFILE_CHOICES}; "
                    f"got {timeout_profile!r}."
                )

        smoke_mode = c.get("smoke_mode")
        if smoke_mode is not None:
            smoke_mode = str(smoke_mode).strip()
            if not smoke_mode:
                smoke_mode = None
        eval_modes = _normalize_eval_modes(c.get("eval_modes"), case_number=i)

        baseline_type = c.get("baseline_type")
        if baseline_type is not None:
            baseline_type = str(baseline_type).strip().lower()
            if baseline_type and baseline_type not in _BASELINE_TYPE_CHOICES:
                raise ValueError(
                    f"Case #{i} `baseline_type` must be one of {sorted(_BASELINE_TYPE_CHOICES)}; "
                    f"got {baseline_type!r}."
                )

        comparison_inputs = c.get("comparison_inputs")
        if comparison_inputs is not None and not isinstance(comparison_inputs, dict):
            raise ValueError(f"Case #{i} `comparison_inputs` must be a mapping when provided.")

        iteration_round_state = c.get("iteration_round_state")
        if iteration_round_state is not None:
            iteration_round_state = str(iteration_round_state).strip().lower()
            if iteration_round_state and iteration_round_state not in _ROUND_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `iteration_round_state` must be one of {sorted(_ROUND_STATE_CHOICES)}; "
                    f"got {iteration_round_state!r}."
                )

        metric_availability = c.get("metric_availability")
        if metric_availability is not None:
            metric_availability = str(metric_availability).strip().lower()
            if metric_availability and metric_availability not in _METRIC_AVAILABILITY_CHOICES:
                raise ValueError(
                    f"Case #{i} `metric_availability` must be one of {sorted(_METRIC_AVAILABILITY_CHOICES)}; "
                    f"got {metric_availability!r}."
                )

        readiness_state = c.get("readiness_state")
        if readiness_state is not None:
            readiness_state = str(readiness_state).strip().lower()
            if readiness_state and readiness_state not in _READINESS_STATE_CHOICES:
                raise ValueError(
                    f"Case #{i} `readiness_state` must be one of {sorted(_READINESS_STATE_CHOICES)}; "
                    f"got {readiness_state!r}."
                )

        comparison_review_artifact = c.get("comparison_review_artifact")
        if comparison_review_artifact is not None:
            comparison_review_artifact = str(comparison_review_artifact).strip()
            if not comparison_review_artifact:
                comparison_review_artifact = None

        neutral_baseline_approval_id = c.get("neutral_baseline_approval_id")
        if neutral_baseline_approval_id is not None:
            neutral_baseline_approval_id = str(neutral_baseline_approval_id).strip()
            if not neutral_baseline_approval_id:
                neutral_baseline_approval_id = None

        claim_ids = _normalize_string_list(c.get("claim_ids"), field_name="claim_ids", case_number=i)
        unknown_claim_ids = [claim_id for claim_id in claim_ids if claims and claim_id not in claims]
        if unknown_claim_ids:
            raise ValueError(
                f"Case #{i} references unknown claim_ids: {', '.join(unknown_claim_ids)}."
            )

        realistic = c.get("realistic")
        if realistic is not None and not isinstance(realistic, bool):
            raise ValueError(f"Case #{i} `realistic` must be boolean when provided.")

        why_realistic = c.get("why_realistic")
        if why_realistic is not None:
            why_realistic = str(why_realistic).strip()
            if not why_realistic:
                why_realistic = None

        baseline_id = c.get("baseline_id")
        if baseline_id is not None:
            baseline_id = str(baseline_id).strip()
            if not baseline_id:
                baseline_id = None
            elif baseline_id not in baselines:
                raise ValueError(f"Case #{i} references unknown baseline_id={baseline_id!r}.")

        hard_gates = _normalize_string_list(c.get("hard_gates"), field_name="hard_gates", case_number=i)
        expected_evidence = _normalize_string_list(
            c.get("expected_evidence"),
            field_name="expected_evidence",
            case_number=i,
        )
        pass_rate_threshold = _optional_float(
            c.get("pass_rate_threshold"),
            field_name="pass_rate_threshold",
            case_number=i,
        )
        if pass_rate_threshold is not None and not math.isfinite(pass_rate_threshold):
            raise ValueError(f"Case #{i} `pass_rate_threshold` must be a finite number.")

        if baseline_type == "neutral_repo_baseline" and not neutral_baseline_approval_id:
            raise ValueError(
                f"Case #{i} uses baseline_type=neutral_repo_baseline but is missing `neutral_baseline_approval_id`."
            )

        cases.append(
            EvalCase(
                id=case_id,
                name=str(c["name"]),
                prompt=str(c["prompt"]),
                acceptance=list(c["acceptance"]),
                output_schema=str(c["output_schema"]) if c.get("output_schema") else None,
                should_trigger=should_trigger,
                category=category if category else None,
                deterministic_checks=deterministic_checks,
                expected_signals=expected_signals,
                budgets=budgets,
                prepend_skill=prepend_skill,
                timeout_sec=timeout_sec,
                timeout_profile=timeout_profile if timeout_profile else None,
                smoke_mode=smoke_mode,
                eval_modes=eval_modes,
                baseline_type=baseline_type if baseline_type else None,
                comparison_inputs=dict(comparison_inputs) if isinstance(comparison_inputs, dict) else None,
                iteration_round_state=iteration_round_state if iteration_round_state else None,
                metric_availability=metric_availability if metric_availability else None,
                readiness_state=readiness_state if readiness_state else None,
                comparison_review_artifact=comparison_review_artifact,
                neutral_baseline_approval_id=neutral_baseline_approval_id,
                claim_ids=claim_ids,
                realistic=realistic,
                why_realistic=why_realistic,
                baseline_id=baseline_id,
                hard_gates=hard_gates,
                expected_evidence=expected_evidence,
                unit=_optional_case_string(c.get("unit")),
                given=_optional_case_string(c.get("given")),
                should=_optional_case_string(c.get("should")),
                actual_artifact=_optional_case_artifact_string(c.get("actual_artifact"), field_name="actual_artifact", case_number=i),
                expected_artifact=_optional_case_artifact_string(c.get("expected_artifact"), field_name="expected_artifact", case_number=i),
                reproduce=_optional_case_string(c.get("reproduce")),
                raw_response_artifact=_optional_case_artifact_string(c.get("raw_response_artifact"), field_name="raw_response_artifact", case_number=i),
                judge_detail_artifact=_optional_case_artifact_string(c.get("judge_detail_artifact"), field_name="judge_detail_artifact", case_number=i),
                pass_rate_threshold=pass_rate_threshold,
                pass_rate_calibration_artifact=_optional_case_artifact_string(c.get("pass_rate_calibration_artifact"), field_name="pass_rate_calibration_artifact", case_number=i),
            )
        )
    return cases


def _case_matches_eval_mode(case: EvalCase, *, eval_mode: str) -> bool:
    if eval_mode == "standard":
        return True
    if case.eval_modes:
        return eval_mode in case.eval_modes
    if eval_mode == "release":
        return True
    if case.category in {"negative", "pressure"}:
        return False
    if case.deterministic_checks or case.budgets:
        return False
    return True


def _filter_cases_for_eval_mode(cases: Sequence[EvalCase], *, eval_mode: str) -> List[EvalCase]:
    return [case for case in cases if _case_matches_eval_mode(case, eval_mode=eval_mode)]


def _reporting_metadata(obj: Dict[str, Any]) -> Dict[str, Any]:
    raw = obj.get("reporting")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("`reporting` must be a mapping when provided.")
    reporting = dict(raw)
    preferred_source_format = reporting.get("preferred_source_format")
    if preferred_source_format is not None:
        if not isinstance(preferred_source_format, str):
            raise ValueError("`reporting.preferred_source_format` must be a string when provided.")
        normalized = preferred_source_format.strip().lower()
        if normalized and normalized not in {"mdx", "markdown", "json"}:
            raise ValueError("`reporting.preferred_source_format` must be one of: mdx, markdown, json.")
        reporting["preferred_source_format"] = normalized
    for path_field in ("report_template", "component_bundle"):
        raw_path = reporting.get(path_field)
        if raw_path is not None and not isinstance(raw_path, str):
            raise ValueError(f"`reporting.{path_field}` must be a string when provided.")
        if isinstance(raw_path, str) and raw_path.strip():
            report_path = Path(raw_path)
            if report_path.is_absolute():
                raise ValueError(f"`reporting.{path_field}` must be a repo-relative path.")
            if ".." in report_path.parts:
                raise ValueError(f"`reporting.{path_field}` must not contain path traversal.")
    return reporting


def _reporting_artifact_exists(relative_path: str, *, search_roots: Sequence[Path]) -> bool:
    for root in search_roots:
        root_resolved = root.resolve()
        candidate = root / relative_path
        if not candidate.is_file():
            continue
        try:
            candidate_resolved = candidate.resolve()
            candidate_resolved.relative_to(root_resolved)
        except (OSError, ValueError):
            continue
        return True
    return False


def _claim_to_evidence_summary(
    evals_doc: Dict[str, Any],
    cases: Sequence[EvalCase],
    *,
    eval_mode: str,
    skill_dir: Path,
    focused_subset: bool = False,
) -> Dict[str, Any]:
    claims = _load_claims(evals_doc)
    baselines = _load_baselines(evals_doc)
    reporting = _reporting_metadata(evals_doc)
    claim_records: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    if eval_mode == "release" and cases and not claims:
        gaps.append({
            "type": "missing_claim_registry",
            "severity": "blocking",
            "message": "release evals must define top-level claims before claim evidence can pass",
        })

    for claim_id, claim in sorted(claims.items()):
        covering = [case for case in cases if claim_id in case.claim_ids]
        hard_gate = bool(claim.get("hard_gate"))
        risk = str(claim.get("risk") or "medium").strip().lower()
        blocking = (
            eval_mode == "release"
            and not focused_subset
            and hard_gate
            and risk in {"critical", "high"}
        )
        evidence_required = _normalize_string_list(
            claim.get("evidence_required"),
            field_name=f"claims[{claim_id}].evidence_required",
        )
        evidence_surfaces = sorted({surface for case in covering for surface in _case_evidence_surfaces(case)})

        record = {
            "id": claim_id,
            "claim_type": claim.get("claim_type"),
            "risk": risk,
            "hard_gate": hard_gate,
            "source": claim.get("source"),
            "evidence_required": list(evidence_required),
            "evidence_surfaces": evidence_surfaces,
            "cases": [case.id for case in covering],
        }
        claim_records.append(record)

        if not covering:
            gaps.append({
                "type": "claim_without_case",
                "claim_id": claim_id,
                "severity": "blocking" if blocking else "advisory",
                "message": "claim has no eval case linked through claim_ids",
            })
            continue

        if blocking and not any(case.acceptance for case in covering):
            gaps.append({
                "type": "claim_without_acceptance",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "high-risk hard-gate claim lacks acceptance checks",
            })
        if blocking and not evidence_surfaces:
            gaps.append({
                "type": "claim_without_evidence_surface",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "high-risk hard-gate claim lacks deterministic, signal, schema, hard-gate, or expected-evidence coverage",
            })
        if blocking and evidence_required and not evidence_surfaces:
            gaps.append({
                "type": "claim_evidence_required_unmapped",
                "claim_id": claim_id,
                "severity": "blocking",
                "message": "claim declares evidence_required but no covering case declares an evidence surface",
            })

    for case in cases:
        if claims and not case.claim_ids:
            gaps.append({
                "type": "case_without_claim",
                "case_id": case.id,
                "severity": "advisory",
                "message": "case is not linked to a claim_id",
            })
        if eval_mode == "release" and case.claim_ids:
            if case.realistic is not True:
                gaps.append({
                    "type": "missing_realism_evidence",
                    "case_id": case.id,
                    "severity": "blocking",
                    "message": "release claim-linked case must set realistic: true",
                })
            if not case.why_realistic:
                gaps.append({
                    "type": "missing_realism_rationale",
                    "case_id": case.id,
                    "severity": "blocking",
                    "message": "release claim-linked case must explain why_realistic",
                })
        if case.baseline_id and case.baseline_id not in baselines:
            gaps.append({
                "type": "unknown_baseline",
                "case_id": case.id,
                "severity": "blocking",
                "message": f"case references unknown baseline_id={case.baseline_id!r}",
            })
        if _case_uses_smoke_or_release(case, eval_mode=eval_mode):
            missing_shape = _riteway_shape_missing_fields(case)
            if missing_shape:
                gaps.append({
                    "type": "missing_riteway_shape",
                    "case_id": case.id,
                    "severity": "advisory",
                    "missing_fields": missing_shape,
                    "realistic": case.realistic,
                    "message": (
                        "smoke/release eval should declare unit, given, should, actual_artifact, "
                        "expected_artifact, and reproduce"
                    ),
                })
        weak_reasons = _weak_acceptance_reasons(case)
        if weak_reasons:
            gaps.append({
                "type": "weak_acceptance_shape",
                "case_id": case.id,
                "severity": "advisory",
                "reasons": weak_reasons,
                "message": "migration pass found acceptance that only checks trigger words or generic phrases",
            })
        if case.pass_rate_threshold is not None and not case.pass_rate_calibration_artifact:
            gaps.append({
                "type": "uncalibrated_pass_rate_threshold",
                "case_id": case.id,
                "severity": "advisory",
                "message": "pass-rate threshold is advisory until calibrated against labeled examples",
            })
        gaps.extend(_hard_gate_gaps_for_case(case, eval_mode=eval_mode))

    report_template = str(reporting.get("report_template") or "").strip()
    report_template_exists: Optional[bool] = None
    component_bundle = str(reporting.get("component_bundle") or "").strip()
    component_bundle_exists: Optional[bool] = None
    preferred_source_format = str(reporting.get("preferred_source_format") or "").strip().lower()
    search_roots = [WORKSPACE_ROOT, REPO_ROOT, skill_dir, SCRIPT_DIR]
    if eval_mode == "release" and preferred_source_format == "mdx" and not report_template:
        gaps.append({
            "type": "missing_report_template",
            "severity": "blocking",
            "message": "release MDX reporting must declare report_template",
        })
    if preferred_source_format == "mdx" and report_template and Path(report_template).suffix != ".mdx":
        gaps.append({
            "type": "invalid_report_template_type",
            "severity": "blocking" if eval_mode == "release" else "advisory",
            "message": f"MDX report_template must point to a .mdx file: {report_template}",
        })
    if preferred_source_format == "mdx" and component_bundle and Path(component_bundle).suffix not in {".tsx", ".jsx"}:
        gaps.append({
            "type": "invalid_report_component_bundle_type",
            "severity": "blocking" if eval_mode == "release" else "advisory",
            "message": f"MDX component_bundle must point to a .tsx or .jsx file: {component_bundle}",
        })
    if report_template:
        report_template_exists = _reporting_artifact_exists(report_template, search_roots=search_roots)
        if report_template_exists is False:
            gaps.append({
                "type": "missing_report_template",
                "severity": "blocking" if eval_mode == "release" else "advisory",
                "message": f"report_template does not exist: {report_template}",
            })
    if component_bundle:
        component_bundle_exists = _reporting_artifact_exists(component_bundle, search_roots=search_roots)
        if component_bundle_exists is False:
            gaps.append({
                "type": "missing_report_component_bundle",
                "severity": "blocking" if eval_mode == "release" else "advisory",
                "message": f"component_bundle does not exist: {component_bundle}",
            })
    elif eval_mode == "release" and preferred_source_format == "mdx":
        gaps.append({
            "type": "missing_report_component_bundle",
            "severity": "blocking",
            "message": "release MDX reporting must declare component_bundle",
        })

    blocking_gaps = [gap for gap in gaps if gap.get("severity") == "blocking"]
    return {
        "schema_version": "claim-to-evidence.v1",
        "claims": claim_records,
        "baselines": sorted(baselines),
        "reporting": reporting,
        "report_template_exists": report_template_exists,
        "component_bundle_exists": component_bundle_exists,
        "gaps": gaps,
        "blocking_gaps": blocking_gaps,
        "passed": not blocking_gaps,
    }


def _attach_claim_execution_results(
    claim_summary: Dict[str, Any],
    case_results: Sequence[Dict[str, Any]],
    *,
    eval_mode: str,
    focused_subset: bool = False,
) -> None:
    cases_by_id = {str(case.get("id")): case for case in case_results}
    gaps = list(claim_summary.get("gaps") or [])
    existing_gap_keys = {
        (gap.get("type"), gap.get("claim_id"), gap.get("case_id"))
        for gap in gaps
        if isinstance(gap, dict)
    }
    for claim in claim_summary.get("claims", []):
        if not isinstance(claim, dict):
            continue
        claim_id = str(claim.get("id") or "")
        linked_results: List[Dict[str, Any]] = []
        for case_id in claim.get("cases") or []:
            case = cases_by_id.get(str(case_id))
            if not case:
                continue
            runner_artifacts = []
            for runner in (case.get("runners") or {}).values():
                if isinstance(runner, dict):
                    artifacts = runner.get("artifacts")
                    if isinstance(artifacts, dict) and any(value for value in artifacts.values()):
                        runner_artifacts.append({
                            "runner": runner.get("runner"),
                            "artifacts": artifacts,
                        })
            linked_results.append({
                "case_id": case.get("id"),
                "passed": bool(case.get("passed")),
                "blocked": bool(case.get("blocked")),
                "tier1_failed": bool(case.get("tier1_failed")),
                "tier2_failed": bool(case.get("tier2_failed")),
                "evidence_surfaces": case.get("evidence_surfaces") or [],
                "check_evidence": bool(case.get("check_evidence")),
                "runner_artifacts": runner_artifacts,
            })
        claim["case_results"] = linked_results
        if (
            eval_mode == "release"
            and not focused_subset
            and claim.get("hard_gate")
            and str(claim.get("risk") or "").lower() in {"critical", "high"}
            and not any(
                result.get("passed")
                and result.get("runner_artifacts")
                and result.get("check_evidence")
                for result in linked_results
            )
        ):
            key = ("claim_without_passing_case", claim_id, None)
            if key not in existing_gap_keys:
                gaps.append({
                    "type": "claim_without_passing_case",
                    "claim_id": claim_id,
                    "severity": "blocking",
                    "message": "high-risk hard-gate claim has no passing case with runner artifacts",
                })
                existing_gap_keys.add(key)
    blocking_gaps = [gap for gap in gaps if isinstance(gap, dict) and gap.get("severity") == "blocking"]
    claim_summary["gaps"] = gaps
    claim_summary["blocking_gaps"] = blocking_gaps
    claim_summary["passed"] = not blocking_gaps


def _eval_contract_migration_summary(cases: Sequence[EvalCase], *, eval_mode: str) -> Dict[str, Any]:
    missing_shape: List[Dict[str, Any]] = []
    weak_acceptance: List[Dict[str, Any]] = []
    uncalibrated_thresholds: List[Dict[str, Any]] = []
    for case in cases:
        missing = _riteway_shape_missing_fields(case)
        if _case_uses_smoke_or_release(case, eval_mode=eval_mode) and missing:
            missing_shape.append({
                "case_id": case.id,
                "missing_fields": missing,
                "realistic": case.realistic,
            })
        weak_reasons = _weak_acceptance_reasons(case)
        if weak_reasons:
            weak_acceptance.append({
                "case_id": case.id,
                "reasons": weak_reasons,
            })
        if case.pass_rate_threshold is not None and not case.pass_rate_calibration_artifact:
            uncalibrated_thresholds.append({
                "case_id": case.id,
                "pass_rate_threshold": case.pass_rate_threshold,
                "policy": "advisory_until_calibrated",
            })
    return {
        "schema_version": "eval-contract-migration.v1",
        "riteway_shape_missing_cases": missing_shape,
        "weak_acceptance_cases": weak_acceptance,
        "uncalibrated_pass_rate_thresholds": uncalibrated_thresholds,
    }


def _is_smoke_only_case(case: EvalCase) -> bool:
    if not case.smoke_mode:
        return False
    if case.eval_modes is None:
        return True
    return case.eval_modes == ("smoke",)


def _write_junit_report(summary: Dict[str, Any], destination: Path) -> None:
    tier2_fail_mode = str(summary.get("tier2_mode") or "warn") == "fail"
    junit_failures = sum(
        1
        for case in summary.get("cases", [])
        if case.get("tier1_failed") or (tier2_fail_mode and case.get("tier2_failed"))
    )
    suite_attrs = {
        "name": str(summary.get("skill") or "skill-evals"),
        "tests": str(len(summary.get("cases", []))),
        "failures": str(junit_failures),
        "errors": "0",
    }
    if summary.get("generated_at"):
        suite_attrs["timestamp"] = str(summary["generated_at"])
    if summary.get("run_id"):
        suite_attrs["id"] = str(summary["run_id"])

    lines: List[str] = ['<?xml version="1.0" encoding="utf-8"?>']
    suite_open = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in suite_attrs.items())
    lines.append(f"<testsuite {suite_open}>")
    for case in summary.get("cases", []):
        case_attrs = {
            "name": str(case.get("id") or case.get("name") or "unknown"),
            "classname": str(summary.get("skill") or "skill-evals"),
            "time": str(case.get("timeout_sec") or 0),
        }
        case_open = " ".join(f'{k}="{html.escape(v, quote=True)}"' for k, v in case_attrs.items())
        lines.append(f"  <testcase {case_open}>")
        if case.get("tier1_failed"):
            detail = "\n".join(case.get("tier1_failures") or []) or "tier1 failure"
            lines.append('    <failure message="tier1 failure">')
            lines.append(html.escape(detail))
            lines.append("    </failure>")
        elif case.get("tier2_failed"):
            detail = "\n".join(case.get("tier2_findings") or []) or "tier2 findings"
            if tier2_fail_mode:
                lines.append('    <failure message="tier2 findings in fail mode">')
                lines.append(html.escape(detail))
                lines.append("    </failure>")
            else:
                lines.append('    <skipped message="tier2 findings in warn/off mode">')
                lines.append(html.escape(detail))
                lines.append("    </skipped>")

        chunks: List[str] = []
        if case.get("warnings"):
            chunks.append("warnings:\n" + "\n".join(case["warnings"]))
        if case.get("tier2_findings"):
            chunks.append("tier2_findings:\n" + "\n".join(case["tier2_findings"]))
        riteway = case.get("riteway") if isinstance(case.get("riteway"), dict) else None
        if riteway:
            chunks.append(
                "riteway_failure_report:\n"
                f"unit: {riteway.get('unit') or ''}\n"
                f"given: {riteway.get('given') or ''}\n"
                f"should: {riteway.get('should') or ''}\n"
                f"actual: {riteway.get('actual') or ''}\n"
                f"expected: {riteway.get('expected') or ''}\n"
                f"reproduce: {riteway.get('reproduce') or ''}"
            )
        if case.get("dir"):
            chunks.append(f"artifacts_dir:\n{case['dir']}")
        lines.append("    <system-out>")
        lines.append(html.escape("\n\n".join(chunks)))
        lines.append("    </system-out>")
        lines.append("  </testcase>")
    lines.append("</testsuite>")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mark_no_case_evidence_blocked(summary: Dict[str, Any]) -> bool:
    if summary.get("cases"):
        return False
    summary["blocked_class_summary"]["blocked_validation"] = (
        summary["blocked_class_summary"].get("blocked_validation", 0) + 1
    )
    summary["no_case_evidence"] = True
    return True


def _json_get_path(obj: Any, path: str) -> Any:
    cur = obj
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\[\d+\]", path)
    for t in tokens:
        if t.startswith("["):
            idx = int(t[1:-1])
            if not isinstance(cur, list) or idx >= len(cur):
                raise KeyError(path)
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or t not in cur:
                raise KeyError(path)
            cur = cur[t]
    return cur


def _normalize_assert(a: Assertion) -> Dict[str, Any]:
    if isinstance(a, str):
        s = a.strip()
        bare_match = re.match(r"^(contains|not_contains|regex|not_regex)\s+(.+)$", s, flags=re.IGNORECASE)
        if bare_match:
            assertion_type = bare_match.group(1).lower()
            value = bare_match.group(2).strip()
            if value.startswith(("'", '"')):
                try:
                    parts = shlex.split(value)
                except ValueError as exc:
                    raise ValueError(f"Invalid quoted assertion value: {value!r}") from exc
                if len(parts) != 1:
                    raise ValueError(
                        f"Assertion shorthand expects one value for {assertion_type}, "
                        f"got {len(parts)} tokens: {value!r}"
                    )
                value = parts[0]
            return {"type": assertion_type, "value": value}
        for prefix, t in [
            ("regex:", "regex"),
            ("not_regex:", "not_regex"),
            ("not_contains:", "not_contains"),
            ("contains:", "contains"),
        ]:
            if s.lower().startswith(prefix):
                return {"type": t, "value": s[len(prefix) :].strip()}
        return {"type": "contains", "value": s}

    if isinstance(a, dict):
        if "type" in a:
            return dict(a)

        # Back-compat single-key shorthand, e.g. {contains: "x"}
        if len(a) == 1:
            key, value = next(iter(a.items()))
            t = str(key)
            if t in {"contains", "not_contains", "regex", "not_regex"}:
                return {"type": t, "value": value}
            if t == "jsonpath_exists":
                if isinstance(value, dict):
                    return {"type": t, "path": value.get("path")}
                return {"type": t, "path": value}
            if t == "jsonpath_equals":
                if isinstance(value, dict):
                    return {"type": t, "path": value.get("path"), "value": value.get("value")}
                raise ValueError("jsonpath_equals shorthand must be mapping with {path, value}.")
            if t in {"skill_selected", "skill_not_selected"}:
                if isinstance(value, dict):
                    payload = {"type": t}
                    payload.update(value)
                    return payload
                return {"type": t, "expected_skill": value}

    raise ValueError("Assertion must be a string, typed mapping, or supported shorthand mapping.")


def _to_text_blob(data: Any) -> str:
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2)


def _contains_text(haystack: str, needle: str) -> bool:
    return needle.casefold() in haystack.casefold()


def _normalize_text_field_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().casefold()).strip("_")


def _text_field_map(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\\s+", "", line)
        line = line.replace(chr(96), "")
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = _normalize_text_field_key(key)
        if normalized_key:
            fields[normalized_key] = value.strip().strip("'\\\"")
    return fields


def _text_field_candidate_keys(assertion: Dict[str, Any]) -> List[str]:
    raw_fields = assertion.get("fields")
    candidates: List[str] = []
    if isinstance(raw_fields, list):
        candidates.extend(str(item) for item in raw_fields if str(item).strip())
    path = assertion.get("path") or assertion.get("field") or assertion.get("key")
    if isinstance(path, str) and path.strip():
        candidates.append(path)
    return candidates


def _evaluate_text_field_assertion(text: str, assertion: Dict[str, Any]) -> Optional[str]:
    t = str(assertion.get("type") or "")
    candidates = _text_field_candidate_keys(assertion)
    if not candidates:
        return f"{t} missing field/path"
    fields = _text_field_map(text)
    normalized_candidates = [_normalize_text_field_key(path) for path in candidates]
    present_key = next((key for key in normalized_candidates if key in fields), "")
    present = bool(present_key)
    path_label = "|".join(candidates)
    if t == "text_field_present":
        return None if present else f"text_field_present missing field: {path_label}"
    if t == "text_field_absent":
        return f"text_field_absent found field: {path_label}" if present else None
    if not present:
        return f"{t} missing field: {path_label}"
    got = fields[present_key]
    if t == "text_field_equals":
        expected = _to_text_blob(assertion.get("value", ""))
        if got.casefold() != expected.casefold():
            return f"text_field_equals failed at {path_label}: got={got!r} expected={expected!r}"
        return None
    if t == "text_field_in":
        values = assertion.get("values", assertion.get("value", []))
        if not isinstance(values, list):
            values = [values]
        expected_values = [_to_text_blob(value) for value in values]
        if got.casefold() not in {value.casefold() for value in expected_values}:
            return f"text_field_in failed at {path_label}: got={got!r} expected one of {expected_values!r}"
        return None
    return f"unsupported text field assertion type: {t!r}"


def _json_text_field_map(obj: Any) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for raw_key, child in value.items():
                key = str(raw_key)
                normalized_key = _normalize_text_field_key(key)
                dotted_key = f"{prefix}.{key}" if prefix else key
                normalized_dotted_key = _normalize_text_field_key(dotted_key)
                if not isinstance(child, (dict, list)):
                    text_value = _to_text_blob(child)
                    if normalized_key:
                        fields.setdefault(normalized_key, text_value)
                    if normalized_dotted_key:
                        fields.setdefault(normalized_dotted_key, text_value)
                visit(child, dotted_key)
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{prefix}[{index}]" if prefix else f"[{index}]")

    visit(obj)
    return fields


def _evaluate_json_text_field_assertion(obj: Any, assertion: Dict[str, Any]) -> Optional[str]:
    t = str(assertion.get("type") or "")
    candidates = _text_field_candidate_keys(assertion)
    if not candidates:
        return f"{t} missing field/path"
    fields = _json_text_field_map(obj)
    normalized_candidates = [_normalize_text_field_key(path) for path in candidates]
    present_key = next((key for key in normalized_candidates if key in fields), "")
    present = bool(present_key)
    path_label = "|".join(candidates)
    if t == "text_field_present":
        return None if present else f"text_field_present missing field: {path_label}"
    if t == "text_field_absent":
        return f"text_field_absent found field: {path_label}" if present else None
    if not present:
        return f"{t} missing field: {path_label}"
    got = fields[present_key]
    if t == "text_field_equals":
        expected = _to_text_blob(assertion.get("value", ""))
        if got.casefold() != expected.casefold():
            return f"text_field_equals failed at {path_label}: got={got!r} expected={expected!r}"
        return None
    if t == "text_field_in":
        values = assertion.get("values", assertion.get("value", []))
        if not isinstance(values, list):
            values = [values]
        expected_values = [_to_text_blob(value) for value in values]
        if got.casefold() not in {value.casefold() for value in expected_values}:
            return f"text_field_in failed at {path_label}: got={got!r} expected one of {expected_values!r}"
        return None
    return f"unsupported text field assertion type: {t!r}"


_EXPECTED_SIGNAL_STOPWORDS = {
    "about",
    "after",
    "against",
    "available",
    "before",
    "being",
    "between",
    "could",
    "does",
    "from",
    "into",
    "instead",
    "keeps",
    "names",
    "should",
    "that",
    "their",
    "them",
    "then",
    "this",
    "treats",
    "until",
    "when",
    "with",
    "without",
}


def _expected_signal_terms(value: Any) -> List[str]:
    text = _to_text_blob(value).casefold()
    terms: List[str] = []
    seen = set()
    for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text):
        term = token[:-1] if len(token) > 4 and token.endswith("s") else token
        if term in _EXPECTED_SIGNAL_STOPWORDS:
            continue
        if term not in seen:
            seen.add(term)
            terms.append(term)
    return terms


def _evaluate_expected_signal_assertion(output_text: str, expected: Any) -> Optional[str]:
    expected_text = _to_text_blob(expected)
    if _contains_text(output_text, expected_text):
        return None

    expected_terms = _expected_signal_terms(expected_text)
    if not expected_terms:
        if not _contains_text(output_text, expected_text):
            return f"expected_signal failed: {expected_text!r}"
        return None

    output_terms = set(_expected_signal_terms(output_text))
    matched = [term for term in expected_terms if term in output_terms]
    required_count = max(1, (len(expected_terms) + 1) // 2)
    if len(expected_terms) >= 8:
        required_count = max(4, required_count)

    if len(matched) >= required_count:
        return None

    missing = [term for term in expected_terms if term not in output_terms]
    preview = ", ".join(missing[:6])
    return (
        "expected_signal failed: "
        f"matched {len(matched)}/{len(expected_terms)} signal terms "
        f"(required {required_count}); missing: {preview}"
    )


def _evaluate_skill_selection_assertion(
    assertion: Dict[str, Any],
    *,
    skill_name: str,
    selected: Optional[bool],
) -> Optional[str]:
    t = assertion.get("type")
    expected_skill = assertion.get("expected_skill") or assertion.get("value") or skill_name
    expected_skill = str(expected_skill)

    if expected_skill and expected_skill != skill_name:
        # This eval runner validates the active skill; if another skill is expected, flag explicitly.
        return f"{t} expected_skill mismatch: expected {expected_skill!r}, active skill is {skill_name!r}"

    if selected is None:
        if t == "skill_not_selected":
            return None
        expectation = "selected" if t == "skill_selected" else "not selected"
        return (
            f"{t} failed: expected {skill_name!r} to be {expectation}, "
            "but selection signal was unavailable"
        )

    if t == "skill_selected" and not selected:
        return f"skill_selected failed: expected {skill_name!r} to be selected"

    if t == "skill_not_selected" and selected:
        return f"skill_not_selected failed: expected {skill_name!r} to NOT be selected"

    return None


_DISCOVERY_SCOPE_RE = re.compile(
    r"(?i)\b(?:doc(?:umentation)?|docs?|readme|runbook|surface|scope|path|target|canonical|generated|projection|publication|audit-only|audit only|edit goal)\b"
)
_DISCOVERY_PRE_EDIT_RE = re.compile(
    r"(?i)\b(?:before|prior to|first|start|initial|clarif(?:y|ication)|discovery|smallest|bounded|no edits|without edits)\b"
)
_DISCOVERY_EDIT_CLAIM_RE = re.compile(
    r"(?i)\b(?:I changed|I've changed|I updated|I've updated|patched|rewrote|saved|committed)\b"
)


def _evaluate_discovery_question_assertion(text: str) -> Optional[str]:
    if _DISCOVERY_EDIT_CLAIM_RE.search(text):
        return "discovery_question failed: response claimed an edit before discovery"
    if "?" not in text:
        return "discovery_question failed: response did not ask a question"
    if not _DISCOVERY_SCOPE_RE.search(text):
        return "discovery_question failed: response did not name a documentation scope, path, target, or surface"
    if not _DISCOVERY_PRE_EDIT_RE.search(text):
        return "discovery_question failed: response did not preserve a before-edit discovery boundary"
    return None


def evaluate_assertions_text(
    text: str,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]
        v = a.get("value", "")

        if t == "contains":
            needle = _to_text_blob(v)
            if not _contains_text(text, needle):
                failures.append(f"contains failed: {needle!r}")
        elif t == "not_contains":
            needle = _to_text_blob(v)
            if _contains_text(text, needle):
                failures.append(f"not_contains failed: {needle!r}")
        elif t == "regex":
            pattern = _to_text_blob(v)
            if not re.search(pattern, text, flags=re.MULTILINE):
                failures.append(f"regex failed: /{pattern}/")
        elif t == "not_regex":
            pattern = _to_text_blob(v)
            if re.search(pattern, text, flags=re.MULTILINE):
                failures.append(f"not_regex failed: /{pattern}/")
        elif t in {"skill_selected", "skill_not_selected"}:
            msg = _evaluate_skill_selection_assertion(
                a,
                skill_name=skill_name,
                selected=selected_skill,
            )
            if msg:
                failures.append(msg)
        elif t in {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}:
            msg = _evaluate_text_field_assertion(text, a)
            if msg:
                failures.append(msg)
        elif t == "expected_signal":
            msg = _evaluate_expected_signal_assertion(text, v)
            if msg:
                failures.append(msg)
        elif t == "discovery_question":
            msg = _evaluate_discovery_question_assertion(text)
            if msg:
                failures.append(msg)
        else:
            failures.append(f"unsupported assertion type for text output: {t!r}")
    return failures


def evaluate_assertions_json(
    obj: Any,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        a = _normalize_assert(raw)
        t = a["type"]

        if t in {
            "contains",
            "not_contains",
            "regex",
            "not_regex",
            "skill_selected",
            "skill_not_selected",
            "expected_signal",
            "discovery_question",
        }:
            text = json.dumps(obj, ensure_ascii=False, indent=2)
            failures.extend(
                evaluate_assertions_text(
                    text,
                    [a],
                    skill_name=skill_name,
                    selected_skill=selected_skill,
                )
            )
            continue
        if t in {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}:
            msg = _evaluate_json_text_field_assertion(obj, a)
            if msg:
                failures.append(msg)
            continue

        if t == "jsonpath_equals":
            path = a.get("path")
            expected = a.get("value")
            if not isinstance(path, str) or path.strip() == "":
                failures.append("jsonpath_equals missing `path`")
                continue
            try:
                got = _json_get_path(obj, path)
            except KeyError:
                failures.append(f"jsonpath_equals missing path: {path}")
                continue
            if got != expected:
                failures.append(f"jsonpath_equals failed at {path}: got={got!r} expected={expected!r}")
        elif t == "jsonpath_exists":
            path = a.get("path")
            if not isinstance(path, str) or path.strip() == "":
                failures.append("jsonpath_exists missing `path`")
                continue
            try:
                _json_get_path(obj, path)
            except KeyError:
                failures.append(f"jsonpath_exists failed (missing): {path}")
        else:
            failures.append(f"unsupported assertion type for json output: {t!r}")
    return failures


def _normalize_signal_text(value: Any) -> str:
    text = _to_text_blob(value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _score_required_signals(output_index: str, expected: List[str]) -> Dict[str, Any]:
    matched = [item for item in expected if _normalize_signal_text(item) in output_index]
    missing = [item for item in expected if item not in matched]
    score = 100 if not expected else round((len(matched) / len(expected)) * 100)
    return {"score": score, "matched": matched, "missing": missing}


def _score_forbidden_signals(output_index: str, forbidden: List[str]) -> Dict[str, Any]:
    found = [item for item in forbidden if _normalize_signal_text(item) in output_index]
    score = 100 if not forbidden else round(((len(forbidden) - len(found)) / len(forbidden)) * 100)
    return {"score": score, "found": found}


def _score_flow_steps(output_index: str, expected: List[str]) -> Dict[str, Any]:
    positions: List[int] = []
    missing: List[str] = []
    for item in expected:
        pos = output_index.find(_normalize_signal_text(item))
        if pos < 0:
            missing.append(item)
        positions.append(pos)

    present_positions = [pos for pos in positions if pos >= 0]
    present_score = 100 if not expected else round((len(present_positions) / len(expected)) * 100)
    in_order = bool(expected) and not missing and present_positions == sorted(present_positions)
    order_score = 100 if not expected or in_order else 0
    score = round((present_score * 0.65) + (order_score * 0.35))
    return {
        "score": score,
        "expected": expected,
        "missing": missing,
        "positions": positions,
        "in_order": True if not expected else in_order,
    }


def evaluate_expected_signals(output_text: str, expected_signals: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not expected_signals:
        return None

    output_index = _normalize_signal_text(output_text)
    dimensions: Dict[str, Dict[str, Any]] = {}
    missing_signals: List[str] = []
    forbidden_signals_found: List[str] = []
    risk_factors: List[str] = []

    for key, label in EXPECTED_SIGNAL_REQUIRED_DIMENSIONS.items():
        items = expected_signal_items(expected_signals, key)
        if not items:
            continue
        result = _score_required_signals(output_index, items)
        dimensions[key] = result
        missing_signals.extend(f"{label}: {item}" for item in result["missing"])

    for key, label in EXPECTED_SIGNAL_FORBIDDEN_DIMENSIONS.items():
        items = expected_signal_items(expected_signals, key)
        if not items:
            continue
        result = _score_forbidden_signals(output_index, items)
        dimensions[key] = result
        forbidden_signals_found.extend(f"{label}: {item}" for item in result["found"])

    flow_steps = expected_signal_items(expected_signals, EXPECTED_SIGNAL_FLOW_KEY)
    if flow_steps:
        flow_result = _score_flow_steps(output_index, flow_steps)
        dimensions[EXPECTED_SIGNAL_FLOW_KEY] = flow_result
        missing_signals.extend(f"flow step: {item}" for item in flow_result["missing"])
        if not flow_result["in_order"]:
            risk_factors.append("flow_steps out of order or incomplete")

    scores = [int(d["score"]) for d in dimensions.values() if isinstance(d.get("score"), int)]
    composite = round(sum(scores) / len(scores)) if scores else 100
    if composite < 80:
        risk_factors.append("expected signal score below 80")
    if forbidden_signals_found:
        risk_factors.append("forbidden signals present")

    return {
        EXPECTED_SIGNAL_COMPOSITE_KEY: composite,
        "dimensions": dimensions,
        EXPECTED_SIGNAL_MISSING_KEY: missing_signals,
        EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY: forbidden_signals_found,
        EXPECTED_SIGNAL_RISK_FACTORS_KEY: risk_factors,
    }


def summarize_expected_signal_results(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    scores: List[int] = []
    risky_cases: List[Dict[str, Any]] = []
    for case in cases:
        for runner_name, runner in (case.get("runners") or {}).items():
            expected = ((runner.get("metrics") or {}).get(EXPECTED_SIGNAL_METRIC_KEY) or {})
            score = expected.get(EXPECTED_SIGNAL_COMPOSITE_KEY)
            if not isinstance(score, int):
                continue
            scores.append(score)
            risk_factors = expected.get(EXPECTED_SIGNAL_RISK_FACTORS_KEY) or []
            if score < 80 or risk_factors:
                risky_cases.append(
                    {
                        "case": case.get("id"),
                        "runner": runner_name,
                        "score": score,
                        EXPECTED_SIGNAL_RISK_FACTORS_KEY: risk_factors,
                    }
                )

    return {
        "runs": len(scores),
        "average": round(sum(scores) / len(scores)) if scores else None,
        "minimum": min(scores) if scores else None,
        "risky_cases": risky_cases,
    }


def detect_skill_selected(
    *,
    skill_name: str,
    output_text: str,
    stdout_text: str,
    stderr_text: str,
    events: Optional[List[Dict[str, Any]]],
) -> Optional[bool]:
    """
    Best-effort skill-selection detection from runner artifacts.

    Returns True/False when signals are present, or None when unknown.
    """

    skill_l = skill_name.lower().strip()
    if not skill_l:
        return None

    final_text = output_text or ""
    final_low = final_text.lower()

    explicit_negative_patterns = [
        rf"\b{re.escape(skill_l)}\b\s+is\s+overkill\b",
        rf"\boverkill\b[^\n]{{0,32}}\b{re.escape(skill_l)}\b",
        rf"\b(?:do not|don't|did not|didn't|not)\b[^\n]{{0,32}}\b(?:use|trigger|select|invoke)\b[^\n]{{0,48}}\b{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_negative_patterns):
        return False

    explicit_positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoked|selected|triggered|routed to)\b[^\n]{{0,48}}\$?{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_positive_patterns):
        return True

    blobs = [final_text, stdout_text or "", stderr_text or ""]
    if events:
        event_blob = json.dumps(events, ensure_ascii=False, sort_keys=True)
        blobs.append(event_blob)
    blob = "\n".join(blobs)
    low = blob.lower()

    positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoke(?:d)?|select(?:ed)?|trigger(?:ed)?|route(?:d)?)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\bskill(?:_name| name)?\b[^\n]{{0,40}}{re.escape(skill_l)}\b",
        rf"\b{re.escape(skill_l)}\b[^\n]{{0,30}}\bskill\b",
    ]

    negative_patterns = [
        rf"\b(?:did not|didn't|not|failed to|unable to)\b[^\n]{{0,50}}\b(?:trigger|select|invoke)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\b(?:not selected|not triggered)\b[^\n]{{0,40}}\$?{re.escape(skill_l)}\b",
    ]

    pos = any(re.search(p, low, flags=re.IGNORECASE) for p in positive_patterns)
    neg = any(re.search(p, low, flags=re.IGNORECASE) for p in negative_patterns)

    if pos and not neg:
        return True
    if neg and not pos:
        return False
    if pos and neg:
        # conflicting signal; unknown
        return None

    for event in events or []:
        if not isinstance(event, dict):
            continue

        for key in ("skill", "skill_name", "selected_skill", "selected", "tool_name"):
            value = event.get(key)
            if isinstance(value, str) and skill_l in value.lower():
                event_value = value.strip().lower()
                if key in {"selected", "selected_skill"}:
                    return event_value == skill_l
                if key in {"skill", "skill_name", "tool_name"}:
                    return True

        metadata = event.get("metadata")
        if isinstance(metadata, dict):
            meta_skill = metadata.get("skill") if "skill" in metadata else metadata.get("selected_skill")
            if isinstance(meta_skill, str) and skill_l in meta_skill.lower():
                return True

        tool = event.get("tool")
        if isinstance(tool, dict):
            tool_name = tool.get("name")
            if isinstance(tool_name, str) and skill_l in tool_name.lower():
                return True

    return None


def extract_rubric_metrics(parsed_json: Any) -> Optional[Dict[str, Any]]:
    """
    Extracts rubric-style metrics from a parsed JSON object.

    When the input is a mapping containing any of the keys "overall_pass", "score", or "checks",
    this returns a dictionary with the extracted metrics. The returned mapping may include:
    - "overall_pass": the boolean value from the input when present.
    - "score": the numeric score coerced to a float when present.
    - "checks_count": the number of entries in the "checks" list when present.
    - "checks_passed": count of check entries with a boolean `"pass": true`.
    - "checks_failed": count of check entries with a boolean `"pass": false`.

    Returns:
        A dict with the extracted metrics as described above, or `None` if the input is not a mapping
        or contains none of the recognized rubric fields.
    """
    if not isinstance(parsed_json, dict):
        return None

    has_any = any(k in parsed_json for k in ("overall_pass", "score", "checks"))
    if not has_any:
        return None

    metrics: Dict[str, Any] = {}
    if isinstance(parsed_json.get("overall_pass"), bool):
        metrics["overall_pass"] = parsed_json["overall_pass"]
    if isinstance(parsed_json.get("score"), (int, float)):
        metrics["score"] = float(parsed_json["score"])
    checks = parsed_json.get("checks")
    if isinstance(checks, list):
        metrics["checks_count"] = len(checks)
        passed = 0
        failed = 0
        for item in checks:
            if isinstance(item, dict) and isinstance(item.get("pass"), bool):
                if item["pass"]:
                    passed += 1
                else:
                    failed += 1
        metrics["checks_passed"] = passed
        metrics["checks_failed"] = failed

    return metrics or None


def _parse_agent_self_assessment(output_text: str) -> Optional[bool]:
    """
    Parse agent's explicit self-assessment from output text.

    Looks for patterns like:
    - "Pass/fail: - Fail"
    - "Pass/fail: Pass"
    - "Result: Fail"
    etc.

    Returns:
        True if agent reports pass, False if agent reports fail, None if no clear signal.
    """
    verdict_pattern = re.compile(
        r"(?im)^\s*(?:pass\s*/\s*fail|result|status)\s*:?\s*-?\s*(pass|fail)\b"
    )
    verdicts = verdict_pattern.findall(output_text)
    if not verdicts:
        return None

    return verdicts[-1].lower() == "pass"


def _acceptance_skip_reason(*, exit_code: int, output_text: str) -> Optional[str]:
    """
    Return a skip reason when acceptance assertions should be skipped because the runner failed and produced no final output.

    Parameters:
        exit_code (int): The runner process exit code.
        output_text (str): The runner's final output text.

    Returns:
        Optional[str]: A human-readable skip reason when acceptance checks should be skipped, or `None` when they should be performed.
    """
    if exit_code == 0:
        return None
    if output_text.strip():
        return None
    return "skipped acceptance assertions because the runner exited non-zero and produced no final output"


def run_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    output_schema_path: Optional[Path],
    sandbox: str,
    ask_for_approval: Optional[str],
    model: Optional[str],
    profile: Optional[str],
    codex_home: Optional[Path],
    jsonl_path: Optional[Path],
    codex_bin: Optional[Path],
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
    fallback_profile: Optional[str] = None,
) -> Tuple[int, str, str, List[str]]:
    """
    Run the Codex CLI `exec` command with the provided prompt and capture outputs and warnings.

    Parameters:
        workspace_root (Path): Working directory for the Codex subprocess.
        prompt (str): Prompt text supplied to Codex via stdin.
        output_last_message_path (Path): File path where the CLI's "last message" output will be written.
        output_schema_path (Optional[Path]): Path to an output schema file to pass via `--output-schema` (if any).
        sandbox (str): Sandbox name to pass via `--sandbox`.
        ask_for_approval (Optional[str]): Legacy value for `--ask-for-approval` when supported by the Codex CLI.
        model (Optional[str]): Model name to pass via `--model`.
        profile (Optional[str]): Active Codex profile name to pass via `--profile`.
        codex_home (Optional[Path]): Directory to set as `CODEX_HOME` in the subprocess environment.
        jsonl_path (Optional[Path]): When provided, the raw CLI stdout is written to this path as JSONL.
        codex_bin (Optional[Path]): Path to a Codex binary; its parent directory is prepended to `PATH`.
        timeout_sec (Optional[float]): Explicit timeout in seconds for the subprocess; if omitted, resolved from profile/env.
        timeout_profile (str): Timeout profile name used when `timeout_sec` is not provided.
        extra_codex_args (Optional[List[str]]): Additional CLI arguments appended to the command.
        fallback_profile (Optional[str]): If the first run fails due to unsupported reasoning.summary, retry with this profile.

    Returns:
        Tuple[int, str, str, List[str]]: A tuple of `(exit_code, stdout, stderr, warnings)`. `exit_code` may be
        127 when the Codex CLI is not found and 124 on timeout. `stdout` and `stderr` are the subprocess outputs;
        `warnings` contains non-fatal diagnostics (e.g., unsupported flags, automatic fallback retries).
    """
    warnings: List[str] = []
    env = os.environ.copy()
    if codex_home:
        env["CODEX_HOME"] = str(codex_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    def _invoke(effective_profile: Optional[str]) -> Tuple[int, str, str]:
        cmd = _codex_exec_prefix(codex_bin)
        # Eval cases pass prompt/context explicitly. When a named runtime lane
        # profile is requested, keep profile config available while still using
        # the isolated CODEX_HOME copied below.
        ignore_user_config_support = _codex_supports_exec_flag(codex_bin, "--ignore-user-config")
        if effective_profile:
            if ignore_user_config_support is not False:
                cmd.append("--ignore-user-config")
                warnings.append(
                    "Ignored base Codex user config while preserving the explicit --profile for noninteractive eval subprocesses."
                )
            else:
                warnings.append(
                    "Codex CLI does not support --ignore-user-config; profile eval subprocess may inherit base user config."
                )
            disable_support = _codex_supports_exec_flag(codex_bin, "--disable")
            if disable_support is not False:
                cmd.extend(["--disable", "apps"])
                warnings.append("Disabled Codex apps for noninteractive profile eval subprocesses.")
            else:
                warnings.append("Codex CLI does not support --disable; eval runner could not disable apps.")
        elif ignore_user_config_support is not False:
            cmd.append("--ignore-user-config")
        else:
            warnings.append("Codex CLI does not support --ignore-user-config; eval runner continued without it.")
        cmd.extend(["--sandbox", sandbox])

        if ask_for_approval:
            supports = _codex_supports_exec_flag(codex_bin, "--ask-for-approval")
            if supports is not False:
                cmd.extend(["--ask-for-approval", ask_for_approval])

        cmd.extend([
            "--output-last-message",
            str(output_last_message_path),
        ])

        if extra_codex_args:
            cmd.extend(extra_codex_args)

        if effective_profile:
            cmd.extend(["--profile", effective_profile])
        if model:
            cmd.extend(["--model", model])
        if output_schema_path:
            cmd.extend(["--output-schema", str(output_schema_path)])

        if jsonl_path:
            cmd.append("--json")

        cmd.append("-")

        try:
            proc = sp.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                env=env,
                cwd=workspace_root,
                timeout=timeout,
                start_new_session=True,
            )
        except FileNotFoundError:
            return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
        except sp.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            if jsonl_path and stdout:
                jsonl_path.parent.mkdir(parents=True, exist_ok=True)
                jsonl_path.write_text(stdout, encoding="utf-8")
            timeout_message = f"codex exec timed out after {timeout} seconds."
            stderr = f"{stderr.rstrip()}\n{timeout_message}".strip()
            # Preserve partial JSONL data before returning
            if jsonl_path and stdout:
                jsonl_path.parent.mkdir(parents=True, exist_ok=True)
                jsonl_path.write_text(stdout, encoding="utf-8")
            return 124, stdout, stderr

        if jsonl_path:
            jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            jsonl_path.write_text(proc.stdout, encoding="utf-8")

        return proc.returncode, proc.stdout, proc.stderr

    rc, stdout, stderr = _invoke(profile)

    has_last_message_artifact = output_last_message_path.exists() and output_last_message_path.read_text(encoding="utf-8").strip()
    if rc == 124 and not stdout.strip() and not has_last_message_artifact and stderr.startswith("codex exec timed out after "):
        warnings.append("Codex timed out without output; retrying once with a fresh exec process.")
        # Only delete output_last_message_path if no usable artifact exists
        if output_last_message_path.exists():
            try:
                content = output_last_message_path.read_text(encoding="utf-8").strip()
                if not content:
                    output_last_message_path.unlink()
            except Exception:
                output_last_message_path.unlink()
        if jsonl_path and jsonl_path.exists():
            jsonl_path.unlink()
        rc, stdout, stderr = _invoke(profile)

    if (
        rc != 0
        and fallback_profile
        and fallback_profile != profile
        and _is_codex_reasoning_summary_unsupported(f"{stderr}\n{stdout}")
    ):
        warnings.append(
            "Codex rejected reasoning.summary for the active profile/model; "
            f"retrying with fallback profile `{fallback_profile}`."
        )
        rc, stdout, stderr = _invoke(fallback_profile)

    return rc, stdout, stderr, warnings


def run_alt_codex_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    codex_bin: Optional[Path],
    output_format: str,
    settings_path: Optional[Path],
    cli_command: Optional[str],
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_codex_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    command_name = (cli_command or "").strip() or "codex"
    use_shell_function = command_name != "codex"

    base_args: List[str] = [command_name, "-p"]
    if settings_path:
        base_args.extend(["--settings", str(settings_path)])
    base_args.extend(["--output-format", output_format])
    if extra_codex_args:
        base_args.extend(extra_codex_args)

    if use_shell_function:
        command_str = " ".join(shlex.quote(x) for x in base_args)
        cmd = ["zsh", "-ic", command_str]
    else:
        if codex_bin:
            cmd = [str(codex_bin), *base_args[1:]]
        else:
            cmd = base_args

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
            start_new_session=True,
        )
    except FileNotFoundError:
        if use_shell_function:
            return 127, "", f"{command_name} is not available in interactive zsh. Check your shell setup."
        return 127, "", "codex CLI not found on PATH. Install Codex CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"codex headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr = proc.stderr or ""
    stdout = proc.stdout or ""

    if proc.returncode != 0 and ("not logged in" in stdout.lower() or "/login" in stdout.lower()):
        hint = (
            "Codex CLI appears to be unauthenticated.\n"
            "Fix:\n"
            "  1) Run `codex` interactively and execute `/login`, then re-run evals.\n"
            "  2) Or run `codex setup-token` if you use token-based auth.\n"
            "Note: if you maintain multiple Codex setups/profiles, ensure the intended one is active.\n"
        )
        stderr = (hint + "\n" + stderr).strip() + "\n"

    return proc.returncode, stdout, stderr


def run_openai_exec(
    *,
    workspace_root: Path,
    prompt: str,
    output_last_message_path: Path,
    openai_bin: Optional[Path],
    output_format: str,
    timeout_sec: Optional[float],
    timeout_profile: str,
    extra_openai_args: Optional[List[str]] = None,
) -> Tuple[int, str, str]:
    if openai_bin:
        cmd = [str(openai_bin)]
    else:
        cmd = ["openai"]

    cmd.extend(["--prompt", prompt, "--output-format", output_format])
    if extra_openai_args:
        cmd.extend(extra_openai_args)

    timeout = _eval_timeout_seconds(timeout_sec=timeout_sec, timeout_profile=timeout_profile)

    try:
        proc = sp.run(
            cmd,
            text=True,
            capture_output=True,
            cwd=workspace_root,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", "openai CLI not found on PATH. Install OpenAI CLI and ensure it is on PATH."
    except sp.TimeoutExpired:
        return 124, "", f"openai headless timed out after {timeout} seconds."

    output_last_message_path.write_text(proc.stdout or "", encoding="utf-8")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _eval_timeout_seconds(
    *,
    timeout_sec: Optional[float],
    timeout_profile: str,
) -> float:
    if timeout_sec is not None:
        return float(timeout_sec)

    raw = os.environ.get("SKILL_EVAL_TIMEOUT_SEC")
    if raw is None:
        raw = os.environ.get("CODEX_EVAL_TIMEOUT_SEC")
    if raw is not None and str(raw).strip():
        return float(raw)

    if timeout_profile == "codex-heavy":
        return 180.0
    if timeout_profile == "discovery-heavy":
        return 300.0
    return 60.0


def _resolve_case_timeout(
    case: EvalCase,
    *,
    cli_timeout_sec: Optional[float],
    cli_timeout_profile: str,
) -> Tuple[Optional[float], str]:
    if cli_timeout_sec is not None:
        return float(cli_timeout_sec), cli_timeout_profile

    resolved_timeout_sec = case.timeout_sec if case.timeout_sec is not None else None
    resolved_timeout_profile = cli_timeout_profile

    if case.timeout_profile and cli_timeout_profile == "default":
        resolved_timeout_profile = case.timeout_profile

    return resolved_timeout_sec, resolved_timeout_profile


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def _rewrite_dash_prefixed_codex_args(argv: Sequence[str]) -> List[str]:
    """
    Allow ergonomic `--*-arg --flag` usage by rewriting it to
    `--*-arg=--flag` before argparse runs.

    We only rewrite when the next token is not a known script option.
    """
    out: List[str] = []
    i = 0
    n = len(argv)
    rewritable = {"--codex-arg", "--codex-arg", "--openai-arg"}
    while i < n:
        tok = argv[i]
        if tok in rewritable and i + 1 < n:
            nxt = argv[i + 1]
            if nxt.startswith("-") and nxt not in _SCRIPT_OPTIONS:
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out


def _parse_runners(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)

    if not expanded:
        raise ValueError("--runners provided but no runner names were parsed.")

    invalid = [x for x in expanded if x not in _RUNNER_CHOICES]
    if invalid:
        raise ValueError(
            f"Invalid runner(s): {', '.join(invalid)}. Allowed: {', '.join(_RUNNER_CHOICES)}."
        )
    return expanded


def _parse_csv_args(raw: Sequence[str]) -> List[str]:
    expanded: List[str] = []
    for item in raw:
        for piece in str(item).split(","):
            token = piece.strip()
            if token:
                expanded.append(token)
    return expanded


def _build_next_reproduce_command(
    args: argparse.Namespace,
    *,
    selected_runners: Sequence[str],
    capture_jsonl: bool,
) -> str:
    parts = [
        "python3",
        "Plugins/skill-factory/scripts/skill-builder/run_skill_evals.py",
        args.path,
        "--eval-mode",
        args.eval_mode,
    ]
    if args.runners:
        for raw_runners in args.runners:
            parts.extend(["--runners", raw_runners])
    elif args.dual_run:
        parts.append("--dual-run")
    elif args.smoke:
        parts.append("--smoke")
    else:
        parts.extend(["--runner", ",".join(selected_runners)])
    for case_filter in args.case:
        parts.extend(["--case", case_filter])
    for category_filter in args.category:
        parts.extend(["--category", category_filter])
    if args.timeout_sec is not None:
        parts.extend(["--timeout-sec", str(args.timeout_sec)])
    if args.timeout_profile != "default":
        parts.extend(["--timeout-profile", args.timeout_profile])
    if capture_jsonl:
        parts.append("--capture-jsonl")
    if args.model:
        parts.extend(["--model", args.model])
    if args.profile:
        parts.extend(["--profile", args.profile])
    return " ".join(shlex.quote(part) for part in parts)


def _filter_cases(
    cases: List[EvalCase],
    *,
    case_filters: Sequence[str],
    categories: Sequence[str],
    exact_case_ids: bool = False,
) -> List[EvalCase]:
    """
    Filter eval cases by case id/name substring and by category.

    Parameters:
        case_filters (Sequence[str]): Terms used to match case ids or names. An empty sequence disables id/name filtering.
        categories (Sequence[str]): Category names to include (case-insensitive). An empty sequence disables category filtering.
        exact_case_ids (bool): When true, case filters must match the exact case id. Release scenario-set
            expansion uses this to prevent substring leakage into generated fixture ids.

    Returns:
        List[EvalCase]: The subset of `cases` that match all provided filters.

    Raises:
        ValueError: If any provided category is not in the allowed set, or if no cases match the supplied filters.
    """
    if not case_filters and not categories:
        return cases

    category_set = {c.lower() for c in categories if c}
    invalid_categories = sorted(category_set - _VALID_CATEGORIES)
    if invalid_categories:
        raise ValueError(
            f"Unknown category filter(s): {', '.join(invalid_categories)}. "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        )

    case_terms = [term.lower() for term in case_filters if term]
    filtered: List[EvalCase] = []
    for case in cases:
        haystack = f"{case.id} {case.name}".lower()
        if exact_case_ids:
            match_case = not case_terms or case.id.lower() in case_terms
        else:
            match_case = not case_terms or any(term in haystack for term in case_terms)
        match_category = not category_set or ((case.category or "").lower() in category_set)
        if match_case and match_category:
            filtered.append(case)

    if not filtered:
        available = ", ".join(f"{c.id}({c.category or 'uncategorized'})" for c in cases)
        raise ValueError(
            "No eval cases matched the supplied filters. "
            f"Available cases: {available}"
        )

    return filtered


def _codex_cli_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Builds the command prefix to invoke the Codex CLI, preferring a bundled `node` executable when present.

    Parameters:
        codex_bin (Optional[Path]): Path to a specific `codex` binary. If `None`, the system `codex` command name is used.

    Returns:
        List[str]: Sequence of command tokens to run the CLI:
            - `["node", "<codex_bin>"]` if a sibling `node` executable exists next to `codex_bin`,
            - `["<codex_bin>"]` if `codex_bin` is provided without a sibling `node`,
            - `["codex"]` if `codex_bin` is `None`.
    """
    effective_codex_bin = codex_bin or _mise_codex_bin()
    if effective_codex_bin:
        node_bin = effective_codex_bin.parent / "node"
        if not node_bin.exists() and _is_node_launcher(effective_codex_bin):
            node_bin = _mise_repo_node_bin()
        if node_bin and node_bin.exists():
            return [str(node_bin), str(effective_codex_bin)]
        return [str(effective_codex_bin)]
    return ["codex"]


def _is_node_launcher(path: Path) -> bool:
    try:
        first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except (OSError, IndexError):
        return False
    return "node" in first_line and first_line.startswith("#!")


def _mise_codex_bin() -> Optional[Path]:
    codex_bin = Path.home() / ".local" / "share" / "mise" / "installs" / "npm-openai-codex" / "latest" / "bin" / "codex"
    return codex_bin.resolve() if codex_bin.exists() else None


def _mise_repo_node_bin() -> Optional[Path]:
    version = _repo_mise_node_version()
    if not version:
        return None
    node_bin = Path.home() / ".local" / "share" / "mise" / "installs" / "node" / version / "bin" / "node"
    return node_bin if node_bin.exists() else None


def _repo_mise_node_version() -> Optional[str]:
    config_path = WORKSPACE_ROOT / ".mise.toml"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except OSError:
        return None
    except tomllib.TOMLDecodeError:
        return None
    tools = config.get("tools")
    if not isinstance(tools, dict):
        return None
    value = tools.get("node")
    return value if isinstance(value, str) and value.strip() else None
    return None


def _codex_exec_prefix(codex_bin: Optional[Path]) -> List[str]:
    """
    Build the command token prefix for invoking the Codex CLI `exec` subcommand.

    Parameters:
        codex_bin (Optional[Path]): Optional path to a specific `codex` binary to prefer; if `None` the default resolver is used.

    Returns:
        List[str]: A list of command tokens forming the prefix (e.g. `["codex", "exec"]` or `["node", "...", "codex", "exec"]`).
    """
    return [*_codex_cli_prefix(codex_bin), "exec"]


def _effective_codex_home(codex_home: Optional[Path]) -> Path:
    """
    Resolve the effective CODEX_HOME directory to use for Codex operations.

    If `codex_home` is provided, it is used; otherwise the `CODEX_HOME` environment variable is used if set; if neither is present, defaults to `~/.codex`. The returned Path is expanded and resolved to an absolute path.

    Parameters:
        codex_home (Optional[Path]): Optional override path for CODEX_HOME.

    Returns:
        Path: Absolute, expanded, resolved path to the Codex home directory.
    """
    raw = str(codex_home) if codex_home else (os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    return Path(raw).expanduser().resolve()


def _copy_codex_home_file(source_home: Path, target_home: Path, name: str) -> Optional[str]:
    source = source_home / name
    if not source.exists():
        return None
    target = target_home / name
    try:
        if name == "config.toml":
            target.write_text(_scrub_mcp_servers_from_toml(source.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(source, target)
    except OSError as exc:
        return f"Could not copy {source} into isolated Codex eval home: {exc}"
    return None


def _scrub_mcp_servers_from_toml(text: str) -> str:
    """
    Remove MCP server tables from copied Codex eval config.

    Live evals verify skill behavior through prompts and filesystem artifacts.
    Inheriting the operator's MCP servers can make unrelated remote OAuth
    failures look like skill failures, so isolated eval homes keep ordinary
    Codex config but drop all [mcp_servers.*] tables.
    """
    kept: List[str] = []
    skipping_mcp = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("["):
            section_name = stripped.lstrip("[").rstrip("]").strip()
            skipping_mcp = section_name == "mcp_servers" or section_name.startswith("mcp_servers.")
        if not skipping_mcp:
            kept.append(line)
    return "".join(kept)


def _isolated_codex_home_for_eval(profile: Optional[str] = None) -> Tuple[Path, List[str]]:
    """
    Build a temporary CODEX_HOME for live eval runs.

    Codex evals need authenticated state, but they should not write sessions into
    the operator's real ~/.codex tree. The temporary home receives only the small
    auth/config files needed to run `codex exec`; sessions and logs stay isolated.
    """
    warnings: List[str] = []
    source_home = _effective_codex_home(None)
    temp_home_ctx = tempfile.TemporaryDirectory(prefix="skill-evals-codex-home-")
    atexit.register(temp_home_ctx.cleanup)
    target_home = Path(temp_home_ctx.name).resolve()

    for child in ("sessions", "logs", "worktrees"):
        (target_home / child).mkdir(parents=True, exist_ok=True)

    if source_home.exists():
        profile_config = f"{profile}.config.toml" if profile else None
        names = ("auth.json", profile_config) if profile_config and (source_home / profile_config).is_file() else (
            "auth.json", "config.toml", "oss-local.config.toml", "oss-cloud.config.toml"
        )
        for name in names:
            warning = _copy_codex_home_file(source_home, target_home, name)
            if warning:
                warnings.append(warning)
    else:
        warnings.append(f"Default Codex home does not exist, using empty isolated eval home: {source_home}")

    warnings.append(f"Using isolated CODEX_HOME for live eval session writes: {target_home}")
    return target_home, warnings


def _codex_env(*, codex_bin: Optional[Path], codex_home: Optional[Path]) -> Dict[str, str]:
    """
    Builds an environment mapping configured for running the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary; when provided, its parent directory is prepended to the `PATH`.
        codex_home (Optional[Path]): Desired Codex home directory; when `None` an effective home is resolved via `_effective_codex_home`.

    Returns:
        Dict[str, str]: A copy of the current environment with `CODEX_HOME` set and `PATH` modified if `codex_bin` was provided.
    """
    env = os.environ.copy()
    effective_home = _effective_codex_home(codex_home)
    env["CODEX_HOME"] = str(effective_home)
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"
    return env


def _codex_auth_env_keys(env: Dict[str, str]) -> List[str]:
    """
    Return the Codex authentication environment variable names that are present and non-empty in the provided environment mapping.

    Parameters:
        env (Dict[str, str]): Mapping of environment variable names to their values (typically os.environ).

    Returns:
        List[str]: Keys from `_CODEX_AUTH_ENV_VARS` whose corresponding value in `env` is non-empty after trimming.
    """
    return [key for key in _CODEX_AUTH_ENV_VARS if str(env.get(key) or "").strip()]


def _codex_login_status(
    *,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[int, str, str]:
    """
    Check the Codex CLI authentication status by running `codex login status`.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to use; if None the system PATH is used.
        codex_home (Optional[Path]): Codex home directory to set via the `CODEX_HOME` environment variable.

    Returns:
        Tuple[int, str, str]: A tuple of `(exit_code, stdout, stderr)`.
            - `exit_code`: the subprocess return code; `127` if the Codex CLI was not found, `124` if the command timed out.
            - `stdout`: the command's standard output as a string (empty string if none).
            - `stderr`: the command's standard error as a string (contains a user-facing message when CLI is missing or timed out).
    """
    cmd = [*_codex_cli_prefix(codex_bin), "login", "status"]
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=120)
    except FileNotFoundError:
        return 127, "", "codex CLI not found on PATH. Install it (for example: npm i -g @openai/codex)."
    except sp.TimeoutExpired:
        return 124, "", "codex login status timed out after 120 seconds."
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _preflight_codex_live_runner(
    *,
    workspace_root: Path,
    codex_bin: Optional[Path],
    codex_home: Optional[Path],
) -> Tuple[List[str], List[str]]:
    """
    Validate that the configured Codex home/bin provide authenticated state required for live `codex exec` runs.

    Performs checks for the existence of the effective CODEX_HOME, presence of an auth.json file or auth-related environment variables, and attempts a short `codex login status` probe. Collects any blocking error messages and non-blocking warnings but does not raise exceptions.

    Parameters:
        workspace_root (Path): Repository/workspace root used to detect repo-local `.codex`.
        codex_bin (Optional[Path]): Optional path to a Codex binary to use for login status probing.
        codex_home (Optional[Path]): Optional explicit Codex home directory; if omitted an effective default is used.

    Returns:
        Tuple[List[str], List[str]]: A pair (errors, warnings).
            - errors: blocking issues that should prevent live Codex execution (e.g., missing home or missing authentication).
            - warnings: non-blocking diagnostics or guidance (e.g., env-based auth present despite login status).
    """
    errors: List[str] = []
    warnings: List[str] = []
    effective_home = _effective_codex_home(codex_home)
    env = _codex_env(codex_bin=codex_bin, codex_home=codex_home)
    auth_env_keys = _codex_auth_env_keys(env)
    auth_file = effective_home / "auth.json"
    default_home = (Path.home() / ".codex").resolve()
    default_auth_file = default_home / "auth.json"
    repo_local_home = (workspace_root / ".codex").resolve()

    if not effective_home.exists():
        errors.append(f"Selected Codex home does not exist: {effective_home}")
        return errors, warnings

    if not auth_file.exists() and not auth_env_keys:
        message = (
            f"Selected Codex home is missing authenticated Codex state for live Codex runs: {effective_home}. "
            "`--codex-home` replaces CODEX_HOME for `codex exec`."
        )
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is provisioned with authenticated Codex state."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += (
                f" The default home {default_home} has auth.json, but the selected home does not inherit it."
            )
        message += " Use an authenticated Codex home for `--runner codex`, or omit `--codex-home` to use the default home."
        errors.append(message)
        return errors, warnings

    status_code, status_stdout, status_stderr = _codex_login_status(codex_bin=codex_bin, codex_home=effective_home)
    status_text = " ".join(part.strip() for part in (status_stdout, status_stderr) if part.strip()).strip()
    if status_code == 0:
        return errors, warnings

    if "not logged in" in status_text.lower():
        if auth_env_keys:
            warnings.append(
                "Codex login status reported 'Not logged in', but auth environment variables are present "
                f"({', '.join(auth_env_keys)}). Live exec may still work if this environment intentionally uses env-based auth."
            )
            return errors, warnings

        message = f"Selected Codex home is not logged in for live Codex runs: {effective_home}."
        if effective_home == repo_local_home:
            message += (
                " Repo-local `.codex` is suitable for discovery/static smoke, not full live smoke unless "
                "it is authenticated."
            )
        if effective_home != default_home and default_auth_file.exists():
            message += f" The default home {default_home} has auth.json, but the selected home does not inherit it."
        message += (
            " Run `CODEX_HOME=<that-home> codex login` for the selected home, or omit `--codex-home` to use the default authenticated home."
        )
        errors.append(message)
        return errors, warnings

    warnings.append(
        f"Unable to confirm Codex login status for {effective_home}: {status_text or f'exit code {status_code}'}"
    )
    return errors, warnings


def _codex_help_text(codex_bin: Optional[Path]) -> Optional[str]:
    """
    Retrieve and cache the combined help text for the Codex CLI.

    Parameters:
        codex_bin (Optional[Path]): Path to the Codex binary to query. If omitted, the system "codex" command will be used.

    Returns:
        Optional[str]: Combined stdout and stderr produced by running the help command, or `None` if the executable is not available or the help invocation failed.
    """
    key = str(codex_bin.resolve()) if codex_bin else "codex"
    if key in _CODEX_HELP_CACHE:
        return _CODEX_HELP_CACHE[key]

    cmd = _codex_exec_prefix(codex_bin) + ["--help"]
    env = os.environ.copy()
    if codex_bin:
        env["PATH"] = f"{codex_bin.parent}{os.pathsep}{env.get('PATH', '')}"

    try:
        proc = sp.run(cmd, text=True, capture_output=True, env=env, timeout=10, start_new_session=True)
    except Exception:  # noqa: BLE001
        _CODEX_HELP_CACHE[key] = None
        return None

    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    _CODEX_HELP_CACHE[key] = text
    return text


def _codex_supports_exec_flag(codex_bin: Optional[Path], flag: str) -> Optional[bool]:
    help_text = _codex_help_text(codex_bin)
    if help_text is None:
        return None
    return flag in help_text


def _is_codex_untrusted_repo_error(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("not inside a trusted directory" in low) and ("skip-git-repo-check" in low)


def _is_runner_runtime_blocked(*, output_text: str, stdout_text: str, stderr_text: str) -> bool:
    return _classify_runner_blocker(
        output_text=output_text,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
    ) is not None


def _classify_runner_blocker(
    *,
    output_text: str,
    stdout_text: str,
    stderr_text: str,
    exit_code: Optional[int] = None,
) -> Optional[str]:
    """
    Determine whether a runner's combined output indicates a runtime blocker and return its blocker taxonomy key.

    Scans the concatenated output, stdout, and stderr for known marker phrases and maps matches to one of:
    - "blocked_user_input" — runner is awaiting user input.
    - "blocked_auth" — authentication/login is required.
    - "timeout_partial_output" or "timeout_no_output" — process timed out (exit_code == 124); chosen depending on whether any output text is present.
    - "blocked_runtime" — sandbox/permission/capacity/runtime failures were detected.

    Parameters:
        output_text (str): Final output text or last message from the runner.
        stdout_text (str): Captured standard output from the runner process.
        stderr_text (str): Captured standard error from the runner process.
        exit_code (Optional[int]): Process exit code; when equal to 124 it is treated as a timeout.

    Returns:
        Optional[str]: One of the blocker keys listed above, or `None` if no blocker markers are found.
    """
    if exit_code == 124:
        runner_text = "\n".join([output_text or "", stdout_text or ""])
        return "timeout_partial_output" if runner_text.strip() else "timeout_no_output"

    process_text = "\n".join([stdout_text or "", stderr_text or ""])
    low = process_text.lower()

    hard_runtime_markers = [
        "ran out of room in the model's context window",
        "selected model is at capacity",
        "model is at capacity",
        "you've hit your usage limit",
        "you have hit your usage limit",
        "usage limit for",
        "switch to another model",
    ]
    conditional_runtime_markers = [
        "sandbox_apply: operation not permitted",
        "host_execution_untrusted",
        "sandbox-exec",
        "operation not permitted",
        "blocked_runtime",
    ]
    model_refresh_runtime_markers = [
        "failed to refresh available models",
        "error sending request for url (http://localhost:11434",
        "stream disconnected before completion",
    ]
    weak_runtime_markers = ["try again at", "start a new thread"]
    usage_context_markers = [
        "usage limit",
        "model is at capacity",
        "selected model is at capacity",
        "context window",
    ]
    if any(marker in low for marker in hard_runtime_markers):
        return "blocked_runtime"
    if (exit_code != 0 or not (output_text or "").strip()) and any(
        marker in low for marker in model_refresh_runtime_markers
    ):
        return "blocked_runtime"
    if any(marker in low for marker in weak_runtime_markers) and any(
        marker in low for marker in usage_context_markers
    ):
        return "blocked_runtime"

    if exit_code == 0 and (output_text or "").strip():
        return None

    text = "\n".join([output_text or "", process_text])
    low = text.lower()
    tool_schema_markers = [
        "failed to parse function arguments",
        "tool exec invoked with incompatible payload",
        "unknown input item type",
        "no last agent message",
        "wrote empty content to",
    ]
    if not (output_text or "").strip() and any(marker in low for marker in tool_schema_markers):
        return "blocked_runtime"
    if any(marker in low for marker in hard_runtime_markers):
        return "blocked_runtime"
    if any(marker in low for marker in conditional_runtime_markers):
        return "blocked_runtime"
    if (exit_code != 0 or not (output_text or "").strip()) and any(
        marker in low for marker in model_refresh_runtime_markers
    ):
        return "blocked_runtime"
    if any(marker in low for marker in weak_runtime_markers) and any(
        marker in low for marker in usage_context_markers
    ):
        return "blocked_runtime"

    user_input_markers = [
        "user_input_requested_during_turn",
        "request_user_input",
        "requested user input",
        "waiting on user",
        "needs user input",
        "blocked_user_input",
    ]
    if any(marker in low for marker in user_input_markers):
        return "blocked_user_input"

    auth_markers = [
        "not logged in",
        "/login",
        "unauthenticated",
        "authentication required",
        "invalid_grant",
        "tokenrefreshfailed",
        "invalid refresh token",
        "missing authenticated codex state",
        "blocked_auth",
    ]
    if any(marker in low for marker in auth_markers):
        return "blocked_auth"

    return None


def _is_codex_reasoning_summary_unsupported(stderr_text: str) -> bool:
    low = (stderr_text or "").lower()
    return ("unsupported parameter" in low) and ("reasoning.summary" in low)


def _has_skip_git_repo_check(extra_codex_args: Optional[Sequence[str]]) -> bool:
    if not extra_codex_args:
        return False
    return any(arg.strip() == "--skip-git-repo-check" for arg in extra_codex_args if isinstance(arg, str))


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Builds and returns the command-line argument parser for run_skill_evals.py.

    The parser includes options for selecting cases and runners, eval suite mode and categories,
    timeout and runtime configuration, Codex/Codex/OpenAI CLI overrides and extra flags,
    JSONL capture and reporting paths, and tier2 gating behavior.

    Returns:
        argparse.ArgumentParser: A parser configured with the script's CLI options.
    """
    p = argparse.ArgumentParser(
        prog="run_skill_evals.py",
        description="Run skill evals using Codex, Codex (Kimi/Zai), and/or OpenAI CLI runners.",
    )
    p.add_argument("path", help="Path to a skill directory or SKILL.md.")
    p.add_argument(
        "--list-cases",
        action="store_true",
        help="List available eval cases (respects --case/--category filters) and exit.",
    )

    p.add_argument("--runner", choices=_RUNNER_CHOICES, default="codex", help="Single-run mode runner.")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Shortcut for `--runner discovery-smoke` for fast contract-level discovery smoke checks.",
    )
    p.add_argument(
        "--runners",
        action="append",
        default=[],
        help=(
            "Explicit runner list (repeatable or comma-separated). "
            "Examples: --runners codex,codex-kimi --runners openai"
        ),
    )
    p.add_argument("--dual-run", action="store_true", help="Run both Codex and Codex-Kimi for every eval case.")
    p.add_argument(
        "--case",
        action="append",
        default=[],
        help=(
            "Run only matching eval case ids/names (repeatable or comma-separated). "
            "Substring match against case id and name."
        ),
    )
    p.add_argument(
        "--eval-mode",
        choices=_EVAL_MODE_CHOICES,
        default="standard",
        help=(
            "Eval suite mode. `standard` preserves current behavior, "
            "`smoke` runs a faster contract/regression subset, and `release` runs the full release-grade suite."
        ),
    )
    p.add_argument(
        "--category",
        action="append",
        default=[],
        help=(
            "Run only evals in matching category (repeatable or comma-separated). "
            f"Allowed: {', '.join(sorted(_VALID_CATEGORIES))}."
        ),
    )

    p.add_argument("--workspace", default=None, help="Workspace root to run commands in (defaults to repo root guess).")
    p.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    p.add_argument(
        "--ask-for-approval",
        default=None,
        choices=["untrusted", "on-request", "never"],
        help=(
            "Legacy Codex approval mode flag. Prefer configuring approval policy via profile/config; "
            "ignored when the active Codex CLI does not support --ask-for-approval."
        ),
    )
    p.add_argument(
        "--timeout-sec",
        type=float,
        default=None,
        help="Per-runner subprocess timeout in seconds. Overrides env vars and timeout profile.",
    )
    p.add_argument(
        "--timeout-profile",
        choices=_TIMEOUT_PROFILE_CHOICES,
        default="default",
        help=(
            "Timeout preset. `codex-heavy` raises the default timeout for slow Codex startup paths; "
            "`discovery-heavy` is a longer preset for interview/discovery prompts."
        ),
    )
    p.add_argument("--model", default=None, help="Override model for codex exec.")
    p.add_argument("--profile", default=None, help="Codex config profile name.")
    p.add_argument(
        "--codex-fallback-profile",
        default="d",
        help=(
            "Auto-retry profile for Codex when active profile/model rejects reasoning.summary "
            "(default: d). Set empty string to disable."
        ),
    )
    p.add_argument(
        "--codex-home",
        default=None,
        help="Set CODEX_HOME. This replaces the full Codex home; live Codex runs need authenticated state in the selected home.",
    )
    p.add_argument("--codex-bin", default=None, help="Override codex CLI path.")
    p.add_argument("--openai-bin", default=None, help="Override openai CLI path.")
    p.add_argument(
        "--codex-output-format",
        choices=["text", "json"],
        default="text",
        help="Codex output format (default: text).",
    )
    p.add_argument(
        "--openai-output-format",
        choices=["text", "json", "stream-json"],
        default="text",
        help="OpenAI output format (default: text).",
    )
    p.add_argument(
        "--codex-settings",
        default=None,
        help="DEPRECATED: plain `codex` runner was removed. Use --codex-kimi-settings / --codex-zai-settings.",
    )
    p.add_argument(
        "--codex-kimi-settings",
        default="kimi_settings.json",
        help="Settings JSON used by runner `codex-kimi` (default: kimi_settings.json).",
    )
    p.add_argument(
        "--codex-zai-settings",
        default="zai_settings.json",
        help="Settings JSON used by runner `codex-zai` (default: zai_settings.json).",
    )
    p.add_argument(
        "--codex-kimi-command",
        default="codex-kimi",
        help="Interactive shell command used for runner `codex-kimi` (default: codex-kimi).",
    )
    p.add_argument(
        "--codex-zai-command",
        default="codex-zai",
        help="Interactive shell command used for runner `codex-zai` (default: codex-zai).",
    )
    p.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra flag to pass to codex CLI (repeatable; supports `--codex-arg --flag`).",
    )
    p.add_argument(
        "--openai-arg",
        action="append",
        default=[],
        help="Extra flag to pass to openai CLI (repeatable; supports `--openai-arg --flag`).",
    )
    p.add_argument(
        "--capture-jsonl",
        action="store_true",
        help="Capture Codex JSONL event stream (--json). Auto-enabled when deterministic checks or budgets are present; required for --dual-run.",
    )
    p.add_argument("--reports-dir", default="Infrastructure/artifacts/skills", help="Base directory for eval reports.")
    p.add_argument("--scorecard-out", default=None, help="Optional explicit path for merged scorecard JSON.")
    p.add_argument("--junit-out", default=None, help="Optional explicit path for JUnit XML output (default: <run>/junit.xml).")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument(
        "--tier2-mode",
        choices=["warn", "fail", "off"],
        default="warn",
        help="How to treat tier-2 findings (rubric/efficiency budgets).",
    )
    return p


def _guess_repo_root(start: Path) -> Path:
    cur = start
    for _ in range(20):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


def _resolve_path(path_like: str, *, base: Path) -> Path:
    p = Path(path_like).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (base / p).resolve()


def _make_relative(path: Optional[Path], base: Path) -> str:
    """Convert absolute path to relative path from base, or return as-is if not possible."""
    if path is None:
        return ""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


WORKFLOW_CLOSEOUT_SCHEMA_VERSION = "skills-sdk.eval-closeout.v1"


def _case_status_from_summary(case: Dict[str, Any]) -> str:
    if case.get("blocked") is True:
        return "blocked"
    if case.get("passed") is True:
        return "pass"
    return "fail"


def _case_closeout_from_summary(case: Dict[str, Any]) -> Dict[str, Any]:
    status = _case_status_from_summary(case)
    entry: Dict[str, Any] = {
        "id": str(case.get("id") or case.get("name") or "unknown"),
        "status": status,
    }
    if case.get("dir"):
        entry["result_path"] = str(case.get("dir"))
    blocker_classes = case.get("blocker_classes")
    if status == "blocked" and isinstance(blocker_classes, list) and blocker_classes:
        entry["blocker_class"] = str(blocker_classes[0])
    if status != "pass":
        failures = case.get("tier1_failures")
        if isinstance(failures, list) and failures:
            entry["failures"] = [str(item) for item in failures]
        blocked_reasons = case.get("blocked_reasons")
        if isinstance(blocked_reasons, list) and blocked_reasons:
            entry["blocked_reasons"] = [str(item) for item in blocked_reasons]
    return entry


def _case_closeout_from_artifact_dir(case_dir: Path, workspace_root: Path) -> Dict[str, Any]:
    case_id = re.sub(r"^\d+-", "", case_dir.name)
    result_path = case_dir / "result.json"
    if result_path.is_file():
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, dict):
            return _case_closeout_from_summary(payload)
    actual_artifacts = [
        path.relative_to(case_dir).as_posix()
        for path in sorted(case_dir.rglob("*"))
        if path.is_file()
    ]
    return {
        "id": case_id,
        "status": "blocked",
        "blocker_class": "blocked_missing_artifact",
        "expected_artifacts": ["result.json"],
        "actual_artifacts": actual_artifacts,
        "result_path": _make_relative(case_dir, workspace_root),
    }


def _workflow_closeout_validation(closeout: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    required = {
        "schema_version",
        "status",
        "skill_path",
        "mode",
        "runner",
        "cases",
        "mutation_allowed",
        "registry_update_allowed",
        "next_reproduce_command",
    }
    missing = sorted(required - set(closeout))
    checks.append({
        "id": "required_fields_present",
        "status": "blocker" if missing else "pass",
        "message": "workflow-closeout/v1 receipts must include required contract fields.",
        "evidence": missing,
    })
    schema_version = closeout.get("schema_version")
    checks.append({
        "id": "schema_version_valid",
        "status": "pass" if schema_version == WORKFLOW_CLOSEOUT_SCHEMA_VERSION else "blocker",
        "message": "workflow-closeout receipt must use skills-sdk.eval-closeout.v1.",
        "evidence": [] if schema_version == WORKFLOW_CLOSEOUT_SCHEMA_VERSION else [str(schema_version)],
    })
    cases = closeout.get("cases")
    case_list = cases if isinstance(cases, list) else []
    checks.append({
        "id": "cases_array_valid",
        "status": "pass" if isinstance(cases, list) else "blocker",
        "message": "workflow-closeout receipt must carry cases as an array.",
        "evidence": [] if isinstance(cases, list) else [type(cases).__name__],
    })
    status = str(closeout.get("status") or "")
    blocked_cases = [
        str(case.get("id") or index)
        for index, case in enumerate(case_list, start=1)
        if isinstance(case, dict) and str(case.get("status") or "") == "blocked"
    ]
    checks.append({
        "id": "blocked_cases_block_suite",
        "status": "blocker" if blocked_cases and status != "blocked" else "pass",
        "message": "Any blocked case must make the suite closeout status blocked.",
        "evidence": blocked_cases if blocked_cases and status != "blocked" else [],
    })
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": "skills-sdk.eval-closeout-validation.v1",
        "status": "blocked" if blockers else "pass",
        "checks": checks,
        "blockers": blockers,
    }


def _write_workflow_closeout(
    *,
    reports_base: Path,
    workspace_root: Path,
    skill_dir: Path,
    eval_mode: str,
    runner_mode: str,
    status: str,
    cases: List[Dict[str, Any]],
    blocker_class: Optional[str],
    missing_suite_artifacts: bool,
    next_reproduce_command: str,
) -> Path:
    closeout: Dict[str, Any] = {
        "schema_version": WORKFLOW_CLOSEOUT_SCHEMA_VERSION,
        "status": status,
        "skill_path": _make_relative(skill_dir, workspace_root),
        "mode": eval_mode,
        "runner": runner_mode,
        "report_dir": _make_relative(reports_base, workspace_root),
        "cases_expected": [str(case.get("id") or "unknown") for case in cases],
        "cases": cases,
        "blocker_class": blocker_class,
        "mutation_allowed": status == "pass",
        "registry_update_allowed": status == "pass" and eval_mode == "release",
        "raw_output_present": False,
        "raw_error_present": False,
        "missing_suite_artifacts": missing_suite_artifacts,
        "case_evidence_present": bool(cases),
        "next_reproduce_command": next_reproduce_command,
    }
    closeout["closeout_validation"] = _workflow_closeout_validation(closeout)
    path = reports_base / "workflow-closeout.json"
    path.write_text(json.dumps(closeout, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_provisional_workflow_closeout(
    *,
    reports_base: Path,
    workspace_root: Path,
    skill_dir: Path,
    eval_mode: str,
    runner_mode: str,
    next_reproduce_command: str,
) -> Path:
    case_dirs = [
        path
        for path in sorted(reports_base.iterdir())
        if path.is_dir() and re.match(r"^\d+-", path.name)
    ]
    cases = [_case_closeout_from_artifact_dir(path, workspace_root) for path in case_dirs]
    return _write_workflow_closeout(
        reports_base=reports_base,
        workspace_root=workspace_root,
        skill_dir=skill_dir,
        eval_mode=eval_mode,
        runner_mode=runner_mode,
        status="blocked",
        cases=cases,
        blocker_class="blocked_missing_artifact",
        missing_suite_artifacts=True,
        next_reproduce_command=next_reproduce_command,
    )


def _release_dependency_scan_roots(skill_dir: Path) -> List[Path]:
    roots = [skill_dir]
    parts = skill_dir.parts
    if "Plugins" in parts:
        idx = parts.index("Plugins")
        if len(parts) > idx + 2 and "skills" in parts[idx + 2 :]:
            plugin_root = Path(*parts[: idx + 2])
            if plugin_root not in roots:
                roots.append(plugin_root)
    return roots


def _is_snyk_manifest(path: Path) -> bool:
    return path.name in SNYK_MANIFEST_NAMES or path.name.endswith(SNYK_MANIFEST_SUFFIXES)


def _dependency_manifest_paths(skill_dir: Path, *, limit: int = 25) -> List[Path]:
    manifests: List[Path] = []
    seen: Set[Path] = set()
    for root in _release_dependency_scan_roots(skill_dir):
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file() or not _is_snyk_manifest(candidate):
                continue
            relative_parts = candidate.relative_to(root).parts[:-1]
            if any(part in SNYK_MANIFEST_EXCLUDED_DIRS for part in relative_parts):
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            manifests.append(candidate)
            if len(manifests) >= limit:
                return manifests
    return manifests


def _snyk_release_gate(
    *,
    skill_dir: Path,
    workspace_root: Path,
    timeout_seconds: int = 180,
) -> Dict[str, Any]:
    scan_roots = _release_dependency_scan_roots(skill_dir)
    scan_target = scan_roots[-1]
    manifests = _dependency_manifest_paths(skill_dir)
    gate: Dict[str, Any] = {
        "schema_version": "skill-release-snyk-gate.v1",
        "required": bool(manifests),
        "status": "not_applicable",
        "reason": "No supported dependency manifest found under the skill package.",
        "manifest_paths": [_make_relative(path, workspace_root) for path in manifests],
        "command": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
    }
    if not manifests:
        return gate

    snyk_bin = shutil.which("snyk")
    if not snyk_bin:
        gate.update({
            "status": "blocked_missing_binary",
            "reason": "Snyk CLI is required for release evals of manifest-backed skill packages.",
            "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
        })
        return gate

    command = [
        snyk_bin,
        "test",
        "--all-projects",
        "--detection-depth=6",
        "--severity-threshold=high",
        "--exclude=node_modules,cache,artifacts,tmp,fixtures,budget-archive",
        "--json",
        str(scan_target),
    ]
    gate["command"] = command
    try:
        proc = sp.run(command, cwd=str(workspace_root), capture_output=True, text=True, timeout=timeout_seconds)
    except sp.TimeoutExpired as exc:
        gate.update({
            "status": "timeout",
            "reason": f"Snyk timed out after {timeout_seconds} seconds.",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        })
        return gate

    gate.update({"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    combined_output = f"{proc.stdout}\n{proc.stderr}".lower()
    if proc.returncode == 0:
        gate["status"] = "success"
        gate["reason"] = "Snyk dependency screening passed for the manifest-backed skill package."
    elif (
        "use snyk auth" in combined_output
        or "not authenticated" in combined_output
        or "authentication required" in combined_output
        or "snyk_token" in combined_output
    ):
        gate["status"] = "blocked_auth"
        gate["reason"] = "Snyk authentication is required for release evals of manifest-backed skill packages."
    elif "could not detect supported target files" in combined_output or "no supported files" in combined_output:
        gate["status"] = "blocked_no_supported_projects"
        gate["reason"] = "Dependency manifests were present, but Snyk did not detect a supported project."
    elif proc.returncode == 1:
        gate["status"] = "advisory"
        gate["reason"] = "Snyk reported high-severity dependency advisories."
    else:
        gate["status"] = "error"
        gate["reason"] = "Snyk failed during release dependency screening."
    return gate


def _snyk_release_gate_passed(gate: Dict[str, Any]) -> bool:
    if not gate.get("required"):
        return True
    return gate.get("status") == "success"


def _extract_min_rubric_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    if not budgets:
        return None
    v = budgets.get("min_rubric_score")
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _extract_min_expected_signal_score(budgets: Optional[Dict[str, Any]]) -> Optional[float]:
    return parse_min_expected_signal_score(budgets)


def _extract_require_overall_pass(budgets: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not budgets:
        return None
    v = budgets.get("require_overall_pass")
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        text = v.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def _extract_bool_budget(budgets: Optional[Dict[str, Any]], key: str) -> Optional[bool]:
    if not budgets:
        return None
    value = budgets.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "yes", "1"}:
            return True
        if text in {"false", "no", "0"}:
            return False
    return None


def _extract_min_skill_lift(budgets: Optional[Dict[str, Any]]) -> Optional[int]:
    if not budgets:
        return None
    value = budgets.get("min_skill_lift")
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _print_case_listing(cases: Sequence[EvalCase]) -> None:
    print("Available eval cases:")
    for case in cases:
        category = case.category or "uncategorized"
        smoke = case.smoke_mode or "-"
        eval_modes = ",".join(case.eval_modes) if case.eval_modes else "auto"
        timeout_profile = case.timeout_profile or "-"
        timeout_sec = (
            f"{case.timeout_sec:g}" if isinstance(case.timeout_sec, (int, float)) else "-"
        )
        print(
            f"- {case.id} [{category}] "
            f"(prepend_skill={str(case.prepend_skill).lower()}, smoke_mode={smoke}, eval_modes={eval_modes}, "
            f"timeout_profile={timeout_profile}, timeout_sec={timeout_sec})"
        )
        print(f"  name: {case.name}")


def _contains_any(text: str, patterns: Sequence[str]) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in patterns)


def _extract_first_question(text: str, patterns: Sequence[str], fallback: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())
    return fallback


def run_discovery_smoke(
    *,
    skill_md_path: Path,
    skill_dir: Path,
    case: EvalCase,
    output_last_message_path: Path,
    include_skill_context: bool = True,
) -> Tuple[int, str, str, List[str]]:
    """
    Fast, deterministic smoke check for discovery-first-turn behavior.

    This bypasses external model execution and verifies that the skill contract
    encodes the expected interview UX. It emits a contract-derived first-turn
    response so normal acceptance assertions can run against it.
    """

    warnings: List[str] = []

    if not include_skill_context:
        response = "\n".join(
            [
                "## Inputs",
                "- Skill context was intentionally withheld for this no-skill baseline run.",
                "- The response can only use the task prompt and generic repository expectations.",
                "",
                "## Outputs",
                "- Baseline response recorded for comparison against the skill-enabled runner.",
                "- No skill-specific routing, discovery contract, or reference-file evidence is available.",
                "",
                "## Next step",
                "- Compare this control output with the normal skill-enabled output before claiming skill lift.",
                "",
                "## Failure mode",
                "- Passing this baseline means the case may not prove the skill added value.",
            ]
        )
        output_last_message_path.write_text(response, encoding="utf-8")
        return 0, response, "", warnings

    skill_text = _read_text(skill_md_path)
    discovery_ref = skill_dir / "references" / "discovery-interview.md"
    discovery_text = _read_text(discovery_ref) if discovery_ref.exists() else ""

    missing: List[str] = []
    if not _contains_any(skill_text, ["## Discovery interview"]):
        missing.append("SKILL.md missing discovery interview section")
    if not _contains_any(
        skill_text,
        [
            "ask one round at a time",
            "one round at a time",
        ],
    ):
        missing.append("SKILL.md missing one-round-at-a-time guidance")
    if not _contains_any(
        skill_text,
        [
            "plain-language question",
            "plain language question",
        ],
    ):
        missing.append("SKILL.md missing plain-language question guidance")
    if not _contains_any(
        skill_text,
        [
            "why the round matters",
            "explain why the round matters",
            "why this matters",
        ],
    ):
        missing.append("SKILL.md missing why-this-matters guidance")
    if not _contains_any(
        skill_text,
        [
            "avoid dumping the whole interview plan at once",
            "avoid dumping the full interview plan at once",
        ],
    ):
        missing.append("SKILL.md missing no-full-plan-dump guidance")
    if not discovery_text:
        missing.append("discovery-interview.md not found")
    else:
        if "## Request user input mini-templates" not in discovery_text:
            missing.append("discovery-interview.md missing mini-templates section")
        if not _contains_any(
            discovery_text,
            [
                "## Copy-paste payload examples",
                "## Copy paste payload examples",
            ],
        ):
            missing.append("discovery-interview.md missing payload examples section")
        if not _contains_any(
            discovery_text,
            [
                "what should this skill help you do?",
                "what kind of help should this skill provide?",
                "which documentation surface should we improve first?",
                "which documentation surface should this update target first?",
                "what should this docs work help you do?",
            ],
        ):
            missing.append("discovery-interview.md missing intuitive round-1 question")

    smoke_mode = case.smoke_mode or "discovery-round-one"
    round_one_question = _extract_first_question(
        discovery_text,
        patterns=[
            r"which documentation surface should(?: we improve first| this update target first)?\?",
            r"what should this docs work help you do\?",
            r"what should this skill help you do\?",
            r"what kind of help should this skill provide\?",
        ],
        fallback="What should this work help you do?",
    )

    if smoke_mode == "discovery-round-one":
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: the exact target surface, primary reader, and job-to-be-done for this documentation work.",
                "- Why this matters: keeping the goal clear prevents scope creep and makes the later validation and ownership decisions more reliable.",
                "",
                "## Outputs",
                "- After discovery confirms the goal, return a tight docs plan or patch scoped to the right surface.",
                "",
                "## Next step",
                f"- Round 1 question: {round_one_question}",
                "",
                "## Failure mode",
                "- Do not draft or rewrite the docs yet when the workflow is still underspecified; finish round 1 first.",
            ]
        )
    elif smoke_mode == "discovery-round-six":
        if "## Round 6: Confirmation" not in discovery_text:
            missing.append("discovery-interview.md missing round-6 confirmation section")
        if not _contains_any(
            discovery_text,
            [
                "does this capture it",
                "does this capture the docs work well enough for me to implement",
                "anything to add or change before i implement it",
                "anything to add or change before i build it",
            ],
        ):
            missing.append("discovery-interview.md missing explicit confirmation question guidance")
        primary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"does this capture[^?]*\?",
                r"ready to implement\?",
            ],
            fallback="Does this capture the work well enough for me to implement?",
        )
        secondary_confirmation = _extract_first_question(
            discovery_text,
            patterns=[
                r"anything to add or change before i (?:implement|build) it\?",
            ],
            fallback="Anything to add or change before I implement it?",
        )
        response = "\n".join(
            [
                "## Inputs",
                "- No major discovery gaps remain; this turn is for confirmation before implementation starts.",
                "",
                "## Outputs",
                "- Provide a compact docs work summary and wait for confirmation before making edits.",
                "",
                "## Next step",
                "- Ask for confirmation before implementation begins.",
                "",
                "## Failure mode",
                "- Do not assume approval from silence; ask for confirmation before implementing.",
                "",
                "## Skill Summary: docs-expert",
                "",
                "**Goal:** Help audit or rewrite documentation with a clear target surface, reader, and verification path.",
                "**Trigger:** natural requests about improving README, docs, runbooks, or in-code documentation.",
                "**Arguments:** target doc path or surface, audience, source of truth, and validation expectations",
                "",
                "**Process:**",
                "1. Confirm the target documentation surface and audience.",
                "2. Confirm the governing source of truth and constraints.",
                "3. Confirm the validation and handoff expectations.",
                "4. Return a concise docs summary and wait for approval to implement.",
                "",
                "**Inputs:** target doc surface, audience, source material, and constraints",
                "**Outputs:** compact docs summary plus the agreed implementation path",
                "**Dependencies:** none required for the smoke example",
                "**Guardrails:** avoid inventing commands or policy and do not implement before confirmation",
                "",
                "Assumptions: this is a docs workflow summary and not the final documentation patch.",
                "",
                primary_confirmation,
                secondary_confirmation,
            ]
        )
    else:
        response = "\n".join(
            [
                "## Inputs",
                "- Missing: a supported smoke mode.",
                "",
                "## Outputs",
                "- None until the smoke mode is corrected.",
                "",
                "## Next step",
                "- Correct the smoke mode and rerun the eval.",
                "",
                "## Failure mode",
                "- Unsupported discovery smoke mode.",
            ]
        )
    output_last_message_path.write_text(response, encoding="utf-8")

    stderr = ""
    if missing:
        stderr = "discovery-smoke contract gaps: " + "; ".join(missing)
        warnings.append(stderr)
        return 2, response, stderr, warnings

    if case.smoke_mode and case.smoke_mode not in {"discovery-round-one", "discovery-round-six"}:
        msg = f"Unsupported smoke_mode for discovery-smoke runner: {case.smoke_mode}"
        warnings.append(msg)
        return 2, response, msg, warnings

    return 0, response, stderr, warnings


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run the full skill evaluation workflow from parsed CLI arguments, execute selected runners against eval cases, and write evaluation reports.

    This function parses and validates CLI arguments (or the provided argv list), loads the skill and eval cases, selects and runs configured runners for each case (including deterministic trace evaluation when enabled), aggregates per-runner and per-case results, emits artifacts (reports, scorecard, junit, release manifest), and determines an overall pass/fail decision.

    Parameters:
        argv (Optional[Sequence[str]]): Optional list of CLI arguments to parse instead of sys.argv[1:].

    Returns:
        int: Exit code: `0` when required gates pass; `1` for configuration/IO/preflight errors; `2` when evaluation gates fail.
    """
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    normalized_argv = _rewrite_dash_prefixed_codex_args(raw_argv)
    args = build_arg_parser().parse_args(normalized_argv)

    if args.dual_run and args.runners:
        print("ERROR: --dual-run cannot be combined with --runners. Choose one mode.", file=sys.stderr)
        return 1
    if args.smoke and args.dual_run:
        print("ERROR: --smoke cannot be combined with --dual-run.", file=sys.stderr)
        return 1
    if args.smoke and args.runners:
        print("ERROR: --smoke cannot be combined with --runners. Use one shortcut or the explicit runner list.", file=sys.stderr)
        return 1
    if args.smoke and args.runner != "codex":
        print("ERROR: --smoke cannot be combined with an explicit non-default --runner. Use one or the other.", file=sys.stderr)
        return 1
    if args.codex_settings:
        print(
            "ERROR: --codex-settings is deprecated because plain `codex` runner was removed. "
            "Use --codex-kimi-settings or --codex-zai-settings.",
            file=sys.stderr,
        )
        return 1

    skill_md = _resolve_skill_md_path(args.path)
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at: {skill_md}", file=sys.stderr)
        return 1

    skill_dir = skill_md.parent
    skill_frontmatter = load_skill_frontmatter(skill_md)
    skill_name = str(skill_frontmatter.get("name") or "").strip()
    if not skill_name:
        print(f"ERROR: SKILL.md frontmatter missing valid `name`: {skill_md}", file=sys.stderr)
        return 1
    skill_contract_text = skill_md.read_text(encoding="utf-8")

    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        print(f"ERROR: Missing evals file: {evals_path}", file=sys.stderr)
        return 1

    try:
        evals_doc = _load_evals_document(evals_path)
        cases = load_evals(evals_path)
        neutral_baseline_approvals = load_neutral_baseline_approvals(evals_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    case_filters = _parse_csv_args(args.case)
    category_filters = _parse_csv_args(args.category)
    try:
        cases = _filter_cases(
            cases,
            case_filters=case_filters,
            categories=category_filters,
            exact_case_ids=args.eval_mode == "release" and bool(case_filters),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    cases = _filter_cases_for_eval_mode(cases, eval_mode=args.eval_mode)
    try:
        claim_to_evidence = _claim_to_evidence_summary(
            evals_doc,
            cases,
            eval_mode=args.eval_mode,
            skill_dir=skill_dir,
            focused_subset=bool(case_filters),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.list_cases:
        _print_case_listing(cases)
        return 0
    if not cases:
        print(f"ERROR: No eval cases matched the selected filters and eval mode `{args.eval_mode}`.", file=sys.stderr)
        return 1

    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else _guess_repo_root(skill_dir)
    codex_home = Path(args.codex_home).expanduser().resolve() if args.codex_home else None
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and not codex_bin.exists():
        print(f"ERROR: --codex-bin not found: {codex_bin}", file=sys.stderr)
        return 1
    codex_bin = Path(args.codex_bin).expanduser() if args.codex_bin else None
    if codex_bin and not codex_bin.exists():
        print(f"ERROR: --codex-bin not found: {codex_bin}", file=sys.stderr)
        return 1
    openai_bin = Path(args.openai_bin).expanduser() if args.openai_bin else None
    if openai_bin and not openai_bin.exists():
        print(f"ERROR: --openai-bin not found: {openai_bin}", file=sys.stderr)
        return 1

    if args.runners:
        try:
            selected_runners = _parse_runners(args.runners)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    elif args.dual_run:
        selected_runners = ["codex", "codex-kimi"]
    elif args.smoke:
        selected_runners = ["discovery-smoke"]
    else:
        selected_runners = [args.runner]
    codex_fallback_profile = str(args.codex_fallback_profile or "").strip() or None
    codex_kimi_command = str(args.codex_kimi_command or "").strip() or "codex-kimi"
    codex_zai_command = str(args.codex_zai_command or "").strip() or "codex-zai"
    preflight_warnings: List[str] = []

    if "codex" in selected_runners and codex_home is None:
        codex_home, isolation_warnings = _isolated_codex_home_for_eval(args.profile)
        preflight_warnings.extend(isolation_warnings)

    # Smoke-profile routing:
    # - For discovery-smoke runs, prefer cases that declare a smoke_mode.
    # - For live/model runners, ignore only smoke-only discovery contract cases.
    smoke_runners_only = bool(selected_runners) and all(r == "discovery-smoke" for r in selected_runners)
    has_smoke_cases = any(c.smoke_mode for c in cases)
    if smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if c.smoke_mode]
    elif smoke_runners_only:
        print(
            "ERROR: discovery-smoke runner requires eval cases with `smoke_mode`; "
            "none matched the selected filters. Use a live runner such as `codex` "
            "for behavior evals, or add discovery-specific smoke_mode cases.",
            file=sys.stderr,
        )
        return 1
    elif not smoke_runners_only and has_smoke_cases:
        cases = [c for c in cases if not _is_smoke_only_case(c)]
        if case_filters and not cases:
            print(
                "ERROR: selected case filters matched only smoke-only discovery contract cases, "
                "which live/model runners skip. Use --runner discovery-smoke for discovery "
                "contract cases or select a behavior smoke case for live/model runners.",
                file=sys.stderr,
            )
            return 1

    capture_jsonl = bool(
        args.capture_jsonl
        or any((c.deterministic_checks or c.budgets) for c in cases)
        or (args.eval_mode == "release" and "codex" in selected_runners)
    )

    if "codex" in selected_runners and args.dual_run and not capture_jsonl:
        print("ERROR: --dual-run requires --capture-jsonl for deterministic Codex checks.", file=sys.stderr)
        return 1

    codex_kimi_settings: Optional[Path] = None
    if "codex-kimi" in selected_runners:
        if codex_kimi_command == "codex":
            codex_kimi_settings = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if not codex_kimi_settings.exists():
                print(
                    f"ERROR: codex-kimi settings file not found: {codex_kimi_settings} "
                    "(override with --codex-kimi-settings)",
                    file=sys.stderr,
                )
                return 1
        else:
            candidate = _resolve_path(args.codex_kimi_settings, base=workspace_root)
            if candidate.exists():
                codex_kimi_settings = candidate

    codex_zai_settings: Optional[Path] = None
    if "codex-zai" in selected_runners:
        if codex_zai_command == "codex":
            codex_zai_settings = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if not codex_zai_settings.exists():
                print(
                    f"ERROR: codex-zai settings file not found: {codex_zai_settings} "
                    "(override with --codex-zai-settings)",
                    file=sys.stderr,
                )
                return 1
        else:
            candidate = _resolve_path(args.codex_zai_settings, base=workspace_root)
            if candidate.exists():
                codex_zai_settings = candidate

    preflight_errors: List[str] = []
    if "codex" in selected_runners:
        if not (workspace_root / ".git").exists() and not _has_skip_git_repo_check(args.codex_arg):
            preflight_warnings.append(
                "Workspace does not appear to be a trusted git repository. "
                "Codex may fail with 'Not inside a trusted directory'. "
                "If this is an ephemeral directory, add --codex-arg=--skip-git-repo-check."
            )
        auth_errors, auth_warnings = _preflight_codex_live_runner(
            workspace_root=workspace_root,
            codex_bin=codex_bin,
            codex_home=codex_home,
        )
        preflight_errors.extend(auth_errors)
        preflight_warnings.extend(auth_warnings)

    if preflight_errors:
        for message in preflight_errors:
            print(f"ERROR: {message}", file=sys.stderr)
        for message in preflight_warnings:
            print(f"WARNING: {message}", file=sys.stderr)
        return 1

    reports_root = Path(args.reports_dir).expanduser().resolve() / skill_name
    reports_root.mkdir(parents=True, exist_ok=True)
    reports_base: Optional[Path] = None
    run_id = ""
    for _ in range(8):
        candidate = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        candidate_path = reports_root / candidate
        try:
            candidate_path.mkdir(parents=False, exist_ok=False)
            reports_base = candidate_path
            run_id = candidate
            break
        except FileExistsError:
            continue
    if reports_base is None or not run_id:
        print("ERROR: unable to allocate unique report directory run_id", file=sys.stderr)
        return 1
    git_meta = _git_metadata(skill_dir)


    readiness_summary: Dict[str, int] = {state: 0 for state in sorted(_READINESS_STATE_CHOICES)}
    readiness_summary["unknown"] = 0
    round_state_summary: Dict[str, int] = {state: 0 for state in sorted(_ROUND_STATE_CHOICES)}
    round_state_summary["unknown"] = 0
    comparison_review_paths: List[str] = []
    used_neutral_baseline_approvals: Set[str] = set()

    summary: Dict[str, Any] = {
        "schema_version": "2.1",
        "tool": "run_skill_evals",
        "generated_at": _utc_now_iso(),
        "skill": skill_name,
        "skill_path": _make_relative(skill_dir, workspace_root),
        "skill_release": {
            "name": skill_name,
            "version": str(skill_frontmatter.get("version") or "0.0.0+local"),
            "compatibility": skill_frontmatter.get("compatibility") or "codex",
            "release_channel": skill_frontmatter.get("release_channel") or "local",
            "schema_version": str(skill_frontmatter.get("schema_version") or "1"),
            "source_commit": git_meta.get("commit"),
            "source_branch": git_meta.get("branch"),
        },
        "workspace_root": str(workspace_root),
        "runner_mode": ",".join(selected_runners),
        "eval_mode": args.eval_mode,
        "tier2_mode": args.tier2_mode,
        "run_id": run_id,
        "case_filters": case_filters,
        "category_filters": category_filters,
        "timeout_profile": args.timeout_profile,
        "timeout_sec": _eval_timeout_seconds(timeout_sec=args.timeout_sec, timeout_profile=args.timeout_profile),
        "capture_jsonl": capture_jsonl,
        "cases": [],
        "passed": True,
        "tier1_failures": 0,
        "tier2_findings": 0,
        "blocked_cases": 0,
        "blocked_class_summary": {key: 0 for key in RUNNER_BLOCKER_TAXONOMY},
        "blocker_taxonomy": RUNNER_BLOCKER_TAXONOMY,
        "preflight_warnings": preflight_warnings,
        "readiness_summary": readiness_summary,
        "round_state_summary": round_state_summary,
        "neutral_baseline_approvals_used": [],
        "claim_to_evidence": claim_to_evidence,
        "eval_contract_migration": _eval_contract_migration_summary(cases, eval_mode=args.eval_mode),
    }
    if args.eval_mode == "release":
        summary["security_dependency_screening"] = _snyk_release_gate(
            skill_dir=skill_dir,
            workspace_root=workspace_root,
        )
    else:
        summary["security_dependency_screening"] = {
            "schema_version": "skill-release-snyk-gate.v1",
            "required": False,
            "status": "skipped",
            "reason": "Snyk dependency screening is required only for release evals of manifest-backed skill packages.",
            "manifest_paths": [],
            "command": None,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
        }

    any_tier1_failed = False
    any_tier2_failed = False
    any_blocked = False
    next_reproduce_command = _build_next_reproduce_command(
        args,
        selected_runners=selected_runners,
        capture_jsonl=capture_jsonl,
    )

    for idx, c in enumerate(cases, 1):
        case_slug = _safe_slug(c.id or c.name)
        case_dir = reports_base / f"{idx:02d}-{case_slug}"
        case_dir.mkdir(parents=True, exist_ok=True)

        schema_path: Optional[Path] = None
        if c.output_schema:
            schema_path = Path(c.output_schema)
            if not schema_path.is_absolute():
                schema_path = (skill_dir / schema_path).resolve()
            if not schema_path.exists():
                print(f"ERROR: Case {c.name}: output_schema not found: {schema_path}", file=sys.stderr)
                return 1

        prompt_body = c.prompt.strip() + "\n"
        if c.prepend_skill:
            try:
                skill_label = skill_md.relative_to(workspace_root)
            except ValueError:
                skill_label = skill_md.name
            composed_prompt = (
                f"${skill_name}\n\n"
                "The local skill handle may not expand inside this isolated eval runner. "
                "Apply this SKILL.md content directly; do not try to read the skill file.\n\n"
                f"<SKILL.md path=\"{skill_label}\">\n{skill_contract_text}\n</SKILL.md>\n\n"
                f"Task:\n{prompt_body}"
            )
        else:
            composed_prompt = prompt_body
        (case_dir / "prompt.txt").write_text(composed_prompt, encoding="utf-8")
        _write_provisional_workflow_closeout(
            reports_base=reports_base,
            workspace_root=workspace_root,
            skill_dir=skill_dir,
            eval_mode=args.eval_mode,
            runner_mode=summary["runner_mode"],
            next_reproduce_command=next_reproduce_command,
        )
        case_timeout_sec, case_timeout_profile = _resolve_case_timeout(
            c,
            cli_timeout_sec=args.timeout_sec,
            cli_timeout_profile=args.timeout_profile,
        )
        comparison_review_artifact = _resolve_optional_case_artifact_path(case_dir, c.comparison_review_artifact, workspace_root)
        neutral_baseline_approval: Optional[Dict[str, Any]] = None
        if c.baseline_type == "neutral_repo_baseline":
            approval_id = c.neutral_baseline_approval_id or ""
            neutral_baseline_approval = neutral_baseline_approvals.get(approval_id)
            if neutral_baseline_approval is None:
                print(
                    "ERROR: case "
                    f"{c.id} references missing neutral_baseline_approval_id={approval_id!r} in {evals_path}",
                    file=sys.stderr,
                )
                return 1

        case_tier1_failures: List[str] = []
        case_tier2_findings: List[str] = []
        case_warnings: List[str] = _riteway_case_warnings(c, eval_mode=args.eval_mode)
        case_blocked_reasons: List[str] = []
        case_notes: List[str] = []
        runner_records: Dict[str, Any] = {}

        for runner_name in selected_runners:
            runner_dir = case_dir / runner_name
            runner_dir.mkdir(parents=True, exist_ok=True)

            output_path = runner_dir / "output_last_message.txt"
            jsonl_path = (runner_dir / "codex_events.jsonl") if (runner_name == "codex" and capture_jsonl) else None

            if runner_name in {"codex-kimi", "codex-zai"}:
                if runner_name == "codex-kimi":
                    runner_settings = codex_kimi_settings
                    runner_command = codex_kimi_command
                elif runner_name == "codex-zai":
                    runner_settings = codex_zai_settings
                    runner_command = codex_zai_command
                rc, stdout, stderr = run_alt_codex_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    codex_bin=codex_bin,
                    output_format=args.codex_output_format,
                    settings_path=runner_settings,
                    cli_command=runner_command,
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_codex_args=args.codex_arg or None,
                )
                runner_exec_warnings: List[str] = []
            elif runner_name == "openai":
                rc, stdout, stderr = run_openai_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    openai_bin=openai_bin,
                    output_format=args.openai_output_format,
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_openai_args=args.openai_arg or None,
                )
                runner_exec_warnings = []
            elif runner_name == "discovery-smoke":
                rc, stdout, stderr, runner_exec_warnings = run_discovery_smoke(
                    skill_md_path=skill_md,
                    skill_dir=skill_dir,
                    case=c,
                    output_last_message_path=output_path,
                )
            else:
                rc, stdout, stderr, runner_exec_warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt=composed_prompt,
                    output_last_message_path=output_path,
                    output_schema_path=schema_path,
                    sandbox=args.sandbox,
                    ask_for_approval=args.ask_for_approval,
                    model=args.model,
                    profile=args.profile,
                    codex_home=codex_home,
                    jsonl_path=jsonl_path,
                    codex_bin=codex_bin,
                    timeout_sec=case_timeout_sec,
                    timeout_profile=case_timeout_profile,
                    extra_codex_args=args.codex_arg or None,
                    fallback_profile=codex_fallback_profile,
                )

            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
            (runner_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")

            output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            runner_dir.mkdir(parents=True, exist_ok=True)
            (runner_dir / "final.txt").write_text(output_text, encoding="utf-8")

            runner_tier1_failures: List[str] = []
            runner_tier2_findings: List[str] = []
            runner_warnings: List[str] = list(runner_exec_warnings)
            runner_notes: List[str] = []
            runner_metrics: Dict[str, Any] = {}
            runner_blocked_runtime = False
            events: Optional[List[Dict[str, Any]]] = None

            if runner_name == "codex" and jsonl_path is not None:
                events, parse_warnings = load_jsonl_events(jsonl_path)
                runner_warnings.extend(parse_warnings)

                if c.deterministic_checks or c.budgets:
                    trace_result = evaluate_trace(
                        events,
                        deterministic_checks=c.deterministic_checks,
                        budgets=c.budgets,
                    )
                    runner_metrics["trace"] = trace_result.to_dict()["metrics"]
                    runner_tier1_failures.extend(trace_result.hard_failures)
                    if args.tier2_mode != "off":
                        runner_tier2_findings.extend(trace_result.soft_failures)
                    runner_warnings.extend(trace_result.warnings)
                else:
                    # still emit basic trace metrics when JSONL is available
                    trace_result = evaluate_trace(events, deterministic_checks=None, budgets=None)
                    runner_metrics["trace"] = trace_result.to_dict()["metrics"]

            if runner_name == "codex" and (c.deterministic_checks or c.budgets) and jsonl_path is None:
                runner_tier1_failures.append(
                    "deterministic_checks/budgets requested but Codex JSONL was not captured (enable --capture-jsonl)."
                )

            selected_skill = detect_skill_selected(
                skill_name=skill_name,
                output_text=output_text,
                stdout_text=stdout,
                stderr_text=stderr,
                events=events,
            )
            if runner_name == "discovery-smoke" and selected_skill is None and c.smoke_mode:
                selected_skill = True
            runner_metrics["selected_skill"] = selected_skill

            if c.should_trigger is not None and selected_skill is not None and selected_skill != c.should_trigger:
                runner_tier1_failures.append(
                    f"should_trigger failed: expected {c.should_trigger}, detected {selected_skill}"
                )
            budgets = c.budgets if isinstance(c.budgets, dict) else {}
            require_selection_signal = bool(budgets.get("require_selection_signal"))
            if c.should_trigger is True and selected_skill is None:
                message = (
                    f"should_trigger={c.should_trigger} but selection signal unavailable (selected_skill is None). "
                    f"Cannot verify selection expectation without signal evidence."
                )
                if require_selection_signal:
                    runner_tier1_failures.append(message)
                else:
                    runner_notes.append(
                        message
                        + " Discovery-smoke or budgets.require_selection_signal=true should own hard selection proof."
                    )
            if c.should_trigger is False and selected_skill is None:
                runner_notes.append(
                    "should_trigger=false and selection signal unavailable; treating absence of positive "
                    "selection evidence as acceptable for this negative case."
                )

            runner_blocker_class = _classify_runner_blocker(
                output_text=output_text,
                stdout_text=stdout,
                stderr_text=stderr,
                exit_code=rc,
            )
            runner_blocked_runtime = runner_blocker_class is not None
            runner_blocked_reasons: List[str] = []
            if runner_blocked_runtime:
                definition = RUNNER_BLOCKER_TAXONOMY.get(
                    runner_blocker_class or "blocked_runtime",
                    "The eval runner was blocked before skill behavior could be judged.",
                )
                runner_blocked_reasons.append(
                    f"{runner_blocker_class}: {definition} "
                    "This is an eval runner blocker, not a skill behavior failure."
                )
            elif rc != 0:
                runner_tier1_failures.append(f"{runner_name} returned non-zero exit code: {rc}")
                if runner_name == "codex" and _is_codex_untrusted_repo_error(stderr):
                    runner_warnings.append(
                        "Codex rejected this workspace as untrusted. "
                        "Use a trusted git repo as --workspace, or pass "
                        "--codex-arg=--skip-git-repo-check for ephemeral temp directories."
                    )

            # Assertions + rubric parsing
            parsed_json: Optional[Any] = None
            used_json_assertions = False
            acceptance_skip_reason = _acceptance_skip_reason(exit_code=rc, output_text=output_text)

            if runner_blocked_runtime:
                pass
            elif acceptance_skip_reason is not None:
                runner_warnings.append(acceptance_skip_reason)
            else:
                if schema_path and runner_name == "codex":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (schema used), but parsing failed: {e}")
                    else:
                        used_json_assertions = True
                elif runner_name in {"codex-kimi", "codex-zai"} and args.codex_output_format == "json":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (Codex json format), but parsing failed: {e}")
                    else:
                        used_json_assertions = True
                elif runner_name == "openai" and args.openai_output_format == "json":
                    try:
                        parsed_json = json.loads(output_text)
                    except Exception as e:  # noqa: BLE001
                        runner_tier1_failures.append(f"expected JSON output (OpenAI json format), but parsing failed: {e}")
                    else:
                        used_json_assertions = True

                if used_json_assertions and parsed_json is not None:
                    runner_tier1_failures.extend(
                        evaluate_assertions_json(
                            parsed_json,
                            c.acceptance,
                            skill_name=skill_name,
                            selected_skill=selected_skill,
                        )
                    )
                else:
                    runner_tier1_failures.extend(
                        evaluate_assertions_text(
                            output_text,
                            c.acceptance,
                            skill_name=skill_name,
                            selected_skill=selected_skill,
                        )
                    )

            # Check agent self-assessment: if agent explicitly reports "Fail", treat as hard failure
            agent_self_assessment = _parse_agent_self_assessment(output_text)
            if agent_self_assessment is False and not runner_blocked_runtime:
                runner_tier1_failures.append(
                    "Agent self-assessment reports explicit failure (e.g., 'Pass/fail: Fail'). "
                    "Treating this as a hard failure regardless of exit_code."
                )

            rubric = extract_rubric_metrics(parsed_json) if parsed_json is not None else None
            if rubric:
                runner_metrics["rubric"] = rubric
                min_score = _extract_min_rubric_score(c.budgets)
                if (
                    args.tier2_mode != "off"
                    and min_score is not None
                    and isinstance(rubric.get("score"), (int, float))
                    and float(rubric["score"]) < min_score
                ):
                    runner_tier2_findings.append(
                        f"rubric score below budget: got {rubric['score']} < min_rubric_score {min_score}"
                    )

                require_overall_pass = _extract_require_overall_pass(c.budgets)
                if args.tier2_mode != "off" and require_overall_pass is True and rubric.get("overall_pass") is False:
                    runner_tier2_findings.append("rubric overall_pass is false but require_overall_pass budget is true")

            if not runner_blocked_runtime and c.expected_signals:
                try:
                    expected_signal_result = evaluate_expected_signals(output_text, c.expected_signals)
                except ValueError as exc:
                    runner_tier1_failures.append(str(exc))
                    expected_signal_result = None
                if expected_signal_result is not None:
                    runner_metrics[EXPECTED_SIGNAL_METRIC_KEY] = expected_signal_result
                    min_expected_score = _extract_min_expected_signal_score(c.budgets)
                    if (
                        args.tier2_mode != "off"
                        and min_expected_score is not None
                        and expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY] < min_expected_score
                    ):
                        runner_tier2_findings.append(
                            "expected signal score below budget: "
                            f"got {expected_signal_result[EXPECTED_SIGNAL_COMPOSITE_KEY]} < "
                            f"min_expected_signal_score {min_expected_score:g}"
                        )

            runner_record = {
                "runner": runner_name,
                "exit_code": rc,
                "passed": (len(runner_tier1_failures) == 0) and not runner_blocked_runtime,
                "blocked": runner_blocked_runtime,
                "blocker_class": runner_blocker_class,
                "blocked_reasons": runner_blocked_reasons,
                "tier1_failures": runner_tier1_failures,
                "tier2_findings": runner_tier2_findings,
                "warnings": runner_warnings,
                "notes": runner_notes,
                "artifacts": {
                    "dir": _make_relative(runner_dir, workspace_root),
                    "final": _make_relative(runner_dir / "final.txt", workspace_root),
                    "raw_response": _make_relative(runner_dir / "final.txt", workspace_root),
                    "stdout": _make_relative(runner_dir / "stdout.txt", workspace_root),
                    "stderr": _make_relative(runner_dir / "stderr.txt", workspace_root),
                    "jsonl": _make_relative(jsonl_path, workspace_root) if jsonl_path else None,
                    "judge_details": _make_relative(runner_dir / "result.json", workspace_root),
                },
                "metrics": runner_metrics,
                "used_schema": bool(schema_path and runner_name == "codex"),
            }

            if _case_requires_no_skill_baseline(c):
                baseline_record: Dict[str, Any]
                baseline_dir = runner_dir / "baseline-no-skill"
                baseline_dir.mkdir(parents=True, exist_ok=True)
                baseline_output_path = baseline_dir / "output_last_message.txt"
                baseline_jsonl_path = (
                    (baseline_dir / "codex_events.jsonl")
                    if (runner_name == "codex" and capture_jsonl)
                    else None
                )
                if runner_name in {"codex-kimi", "codex-zai"}:
                    if runner_name == "codex-kimi":
                        runner_settings = codex_kimi_settings
                        runner_command = codex_kimi_command
                    else:
                        runner_settings = codex_zai_settings
                        runner_command = codex_zai_command
                    baseline_rc, baseline_stdout, baseline_stderr = run_alt_codex_exec(
                        workspace_root=workspace_root,
                        prompt=prompt_body,
                        output_last_message_path=baseline_output_path,
                        codex_bin=codex_bin,
                        output_format=args.codex_output_format,
                        settings_path=runner_settings,
                        cli_command=runner_command,
                        timeout_sec=case_timeout_sec,
                        timeout_profile=case_timeout_profile,
                        extra_codex_args=args.codex_arg or None,
                    )
                    baseline_exec_warnings = []
                elif runner_name == "openai":
                    baseline_rc, baseline_stdout, baseline_stderr = run_openai_exec(
                        workspace_root=workspace_root,
                        prompt=prompt_body,
                        output_last_message_path=baseline_output_path,
                        openai_bin=openai_bin,
                        output_format=args.openai_output_format,
                        timeout_sec=case_timeout_sec,
                        timeout_profile=case_timeout_profile,
                        extra_openai_args=args.openai_arg or None,
                    )
                    baseline_exec_warnings = []
                elif runner_name == "discovery-smoke":
                    baseline_rc, baseline_stdout, baseline_stderr, baseline_exec_warnings = run_discovery_smoke(
                        skill_md_path=skill_md,
                        skill_dir=skill_dir,
                        case=c,
                        output_last_message_path=baseline_output_path,
                        include_skill_context=False,
                    )
                else:
                    baseline_rc, baseline_stdout, baseline_stderr, baseline_exec_warnings = run_codex_exec(
                        workspace_root=workspace_root,
                        prompt=prompt_body,
                        output_last_message_path=baseline_output_path,
                        output_schema_path=schema_path,
                        sandbox=args.sandbox,
                        ask_for_approval=args.ask_for_approval,
                        model=args.model,
                        profile=args.profile,
                        codex_home=codex_home,
                        jsonl_path=baseline_jsonl_path,
                        codex_bin=codex_bin,
                        timeout_sec=case_timeout_sec,
                        timeout_profile=case_timeout_profile,
                        extra_codex_args=args.codex_arg or None,
                        fallback_profile=codex_fallback_profile,
                    )

                (baseline_dir / "stdout.txt").write_text(baseline_stdout or "", encoding="utf-8")
                (baseline_dir / "stderr.txt").write_text(baseline_stderr or "", encoding="utf-8")
                baseline_output_text = (
                    baseline_output_path.read_text(encoding="utf-8")
                    if baseline_output_path.exists()
                    else ""
                )
                (baseline_dir / "final.txt").write_text(baseline_output_text, encoding="utf-8")
                baseline_record = _evaluate_baseline_output(
                    runner_name=runner_name,
                    case=c,
                    skill_name=skill_name,
                    exit_code=baseline_rc,
                    stdout_text=baseline_stdout,
                    stderr_text=baseline_stderr,
                    output_text=baseline_output_text,
                    schema_path=schema_path,
                    codex_output_format=args.codex_output_format,
                    openai_output_format=args.openai_output_format,
                )
                baseline_record["warnings"] = list(baseline_exec_warnings) + list(baseline_record.get("warnings") or [])
                baseline_record["artifacts"] = {
                    "dir": _make_relative(baseline_dir, workspace_root),
                    "final": _make_relative(baseline_dir / "final.txt", workspace_root),
                    "raw_response": _make_relative(baseline_dir / "final.txt", workspace_root),
                    "stdout": _make_relative(baseline_dir / "stdout.txt", workspace_root),
                    "stderr": _make_relative(baseline_dir / "stderr.txt", workspace_root),
                    "jsonl": _make_relative(baseline_jsonl_path, workspace_root) if baseline_jsonl_path else None,
                    "judge_details": _make_relative(baseline_dir / "result.json", workspace_root),
                }
                (baseline_dir / "result.json").write_text(
                    json.dumps(baseline_record, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

                runner_record["baseline"] = baseline_record
                runner_record["baseline_comparison"] = _baseline_comparison_from_records(
                    runner_record=runner_record,
                    baseline_record=baseline_record,
                )
            (runner_dir / "result.json").write_text(json.dumps(runner_record, indent=2, ensure_ascii=False), encoding="utf-8")

            runner_records[runner_name] = runner_record
            case_tier1_failures.extend([f"[{runner_name}] {x}" for x in runner_tier1_failures])
            case_tier2_findings.extend([f"[{runner_name}] {x}" for x in runner_tier2_findings])
            case_warnings.extend([f"[{runner_name}] {x}" for x in runner_warnings])
            case_blocked_reasons.extend([f"[{runner_name}] {x}" for x in runner_blocked_reasons])
            case_notes.extend([f"[{runner_name}] {x}" for x in runner_notes])

        case_blocked = any(bool(record.get("blocked")) for record in runner_records.values())
        case_blocker_classes = sorted(
            {
                str(record.get("blocker_class"))
                for record in runner_records.values()
                if record.get("blocker_class")
            }
        )
        baseline_comparisons = {
            runner_name: record["baseline_comparison"]
            for runner_name, record in runner_records.items()
            if isinstance(record, dict) and isinstance(record.get("baseline_comparison"), dict)
        }
        compared_baselines = [
            comparison
            for comparison in baseline_comparisons.values()
            if comparison.get("status") == "compared"
        ]
        skill_lift: Optional[int] = None
        is_beneficial = False
        baseline_regression = False
        if compared_baselines:
            skill_lift = max(int(comparison.get("skill_lift") or 0) for comparison in compared_baselines)
            is_beneficial = any(bool(comparison.get("is_beneficial")) for comparison in compared_baselines)
            baseline_regression = any(bool(comparison.get("regression")) for comparison in compared_baselines)

        require_skill_lift = _extract_bool_budget(c.budgets, "require_skill_lift")
        min_skill_lift = _extract_min_skill_lift(c.budgets)
        if require_skill_lift is True or min_skill_lift is not None:
            if not compared_baselines:
                case_tier1_failures.append(
                    "skill lift budget requested but no executed no-skill baseline comparison was available"
                )
            else:
                if require_skill_lift is True and not is_beneficial:
                    case_tier1_failures.append(
                        "require_skill_lift failed: skill-enabled run did not beat the no-skill baseline"
                    )
                if min_skill_lift is not None and (skill_lift is None or skill_lift < min_skill_lift):
                    case_tier1_failures.append(
                        f"min_skill_lift failed: got {skill_lift if skill_lift is not None else 'none'} < {min_skill_lift}"
                    )

        case_tier1_failed = len(case_tier1_failures) > 0
        case_tier2_failed = len(case_tier2_findings) > 0
        case_pass = (not case_tier1_failed) and (
            args.tier2_mode != "fail" or (not case_tier2_failed)
        )
        case_pass = case_pass and not case_blocked
        riteway_report = _riteway_case_report(
            c,
            case_dir=case_dir,
            workspace_root=workspace_root,
            runner_records=runner_records,
        )

        case_record = {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "eval_modes": list(c.eval_modes) if c.eval_modes else None,
            "should_trigger": c.should_trigger,
            "prepend_skill": c.prepend_skill,
            "baseline_type": c.baseline_type,
            "baseline_id": c.baseline_id,
            "claim_ids": list(c.claim_ids),
            "realistic": c.realistic,
            "why_realistic": c.why_realistic,
            "hard_gates": list(c.hard_gates),
            "expected_evidence": list(c.expected_evidence),
            "riteway": riteway_report,
            "pass_rate_policy": {
                "threshold": c.pass_rate_threshold,
                "calibration_artifact": _resolve_optional_case_artifact_path(
                    case_dir,
                    c.pass_rate_calibration_artifact,
                    workspace_root,
                ),
                "gate_status": "calibrated_gate" if _resolve_existing_optional_case_artifact_path(
                    case_dir,
                    c.pass_rate_calibration_artifact,
                    workspace_root,
                ) else "advisory",
            } if c.pass_rate_threshold is not None else None,
            "agent_eval_artifacts": {
                "raw_response": _resolve_optional_case_artifact_path(
                    case_dir,
                    c.raw_response_artifact,
                    workspace_root,
                ),
                "judge_details": _resolve_optional_case_artifact_path(
                    case_dir,
                    c.judge_detail_artifact,
                    workspace_root,
                ),
            },
            "evidence_surfaces": _case_evidence_surfaces(c),
            "check_evidence": _case_has_executed_check_evidence(c, runner_records),
            "comparison_inputs": dict(c.comparison_inputs) if c.comparison_inputs else None,
            "iteration_round_state": c.iteration_round_state,
            "metric_availability": c.metric_availability,
            "readiness_state": c.readiness_state,
            "comparison_review_artifact": comparison_review_artifact,
            "neutral_baseline_approval": neutral_baseline_approval,
            "baseline_comparisons": baseline_comparisons,
            "skill_lift": skill_lift,
            "is_beneficial": is_beneficial,
            "baseline_regression": baseline_regression,
            "expected_signals": bool(c.expected_signals),
            "timeout_profile": case_timeout_profile,
            "timeout_sec": _eval_timeout_seconds(
                timeout_sec=case_timeout_sec,
                timeout_profile=case_timeout_profile,
            ),
            "dir": _make_relative(case_dir, workspace_root),
            "runners": runner_records,
            "passed": case_pass,
            "blocked": case_blocked,
            "blocker_classes": case_blocker_classes,
            "blocked_reasons": case_blocked_reasons,
            "tier1_failed": case_tier1_failed,
            "tier2_failed": case_tier2_failed,
            "tier1_failures": case_tier1_failures,
            "tier2_findings": case_tier2_findings,
            "warnings": case_warnings,
            "notes": case_notes,
        }

        (case_dir / "result.json").write_text(json.dumps(case_record, indent=2, ensure_ascii=False), encoding="utf-8")

        summary["cases"].append(case_record)

        if c.readiness_state:
            summary["readiness_summary"][c.readiness_state] = summary["readiness_summary"].get(c.readiness_state, 0) + 1
        else:
            summary["readiness_summary"]["unknown"] += 1

        if c.iteration_round_state:
            summary["round_state_summary"][c.iteration_round_state] = (
                summary["round_state_summary"].get(c.iteration_round_state, 0) + 1
            )
        else:
            summary["round_state_summary"]["unknown"] += 1

        if comparison_review_artifact:
            comparison_review_paths.append(comparison_review_artifact)
        if c.neutral_baseline_approval_id:
            used_neutral_baseline_approvals.add(c.neutral_baseline_approval_id)

        if case_tier1_failed:
            any_tier1_failed = True
            summary["tier1_failures"] += 1
        if case_blocked:
            any_blocked = True
            summary["blocked_cases"] += 1
            for blocker_class in case_blocker_classes:
                summary["blocked_class_summary"][blocker_class] = summary["blocked_class_summary"].get(blocker_class, 0) + 1
        if case_tier2_failed:
            any_tier2_failed = True
            summary["tier2_findings"] += 1

    summary["expected_signal_summary"] = summarize_expected_signal_results(summary["cases"])
    _attach_claim_execution_results(
        summary["claim_to_evidence"],
        summary["cases"],
        eval_mode=args.eval_mode,
        focused_subset=bool(case_filters),
    )
    snyk_gate_passed = _snyk_release_gate_passed(summary["security_dependency_screening"])
    claim_gate_passed = bool(summary["claim_to_evidence"].get("passed", True))
    if _mark_no_case_evidence_blocked(summary):
        any_blocked = True
    summary["passed"] = (not any_blocked) and (not any_tier1_failed) and snyk_gate_passed and (
        args.tier2_mode != "fail" or (not any_tier2_failed)
    )
    summary["passed"] = summary["passed"] and claim_gate_passed
    summary["decision"] = "pass" if summary["passed"] else "fail"
    if any_blocked:
        summary["decision"] = "blocked"
    if not snyk_gate_passed:
        snyk_status = str(summary["security_dependency_screening"].get("status", ""))
        summary["decision"] = "blocked" if snyk_status.startswith("blocked") else "fail"
    if not claim_gate_passed:
        summary["decision"] = "blocked"
    summary["exit_code"] = 0 if summary["passed"] else 2

    summary_path = reports_base / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    scorecard_path = Path(args.scorecard_out).expanduser().resolve() if args.scorecard_out else (reports_base / "scorecard.json")
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(workspace_root))
        except ValueError:
            return str(p)

    summary["artifacts"] = {
        "reports_base": _rel(reports_base),
        "summary": _rel(summary_path),
        "scorecard": _rel(scorecard_path),
    }
    if comparison_review_paths:
        unique_paths = sorted(set(comparison_review_paths))
        summary["artifacts"]["comparison_review"] = unique_paths[0] if len(unique_paths) == 1 else unique_paths
    summary["neutral_baseline_approvals_used"] = sorted(used_neutral_baseline_approvals)
    release_manifest_path = reports_base / "release_manifest.json"
    junit_path = Path(args.junit_out).expanduser().resolve() if args.junit_out else (reports_base / "junit.xml")
    summary["artifacts"]["release_manifest"] = _rel(release_manifest_path)
    summary["artifacts"]["junit"] = _rel(junit_path)
    _write_junit_report(summary, junit_path)
    release_manifest = {
        "schema_version": "1.0",
        "tool": "run_skill_evals",
        "generated_at": summary["generated_at"],
        "skill": summary["skill_release"],
        "run": {
            "run_id": run_id,
            "eval_mode": args.eval_mode,
            "runner_mode": summary["runner_mode"],
            "tier2_mode": args.tier2_mode,
            "capture_jsonl": capture_jsonl,
            "readiness_summary": summary["readiness_summary"],
            "round_state_summary": summary["round_state_summary"],
            "neutral_baseline_approvals_used": summary["neutral_baseline_approvals_used"],
            "security_dependency_screening": summary["security_dependency_screening"],
            "claim_to_evidence": summary["claim_to_evidence"],
            "reports_base": _rel(reports_base),
        },
        "artifacts": summary["artifacts"],
    }
    release_manifest_path.write_text(json.dumps(release_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    scorecard_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    final_closeout_cases = [
        _case_closeout_from_summary(case)
        for case in summary["cases"]
        if isinstance(case, dict)
    ]
    final_blocker_class = None
    if summary["decision"] == "blocked":
        for case in final_closeout_cases:
            if case.get("blocker_class"):
                final_blocker_class = str(case.get("blocker_class"))
                break
        final_blocker_class = final_blocker_class or "blocked_missing_artifact"
    _write_workflow_closeout(
        reports_base=reports_base,
        workspace_root=workspace_root,
        skill_dir=skill_dir,
        eval_mode=args.eval_mode,
        runner_mode=summary["runner_mode"],
        status="pass" if summary["decision"] == "pass" else ("blocked" if summary["decision"] == "blocked" else "fail"),
        cases=final_closeout_cases,
        blocker_class=final_blocker_class,
        missing_suite_artifacts=False,
        next_reproduce_command=next_reproduce_command,
    )

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Skill evals: {skill_name}")
        print(f"Reports: {reports_base}")
        print(f"Scorecard: {scorecard_path}")
        print(f"Release manifest: {release_manifest_path}")
        print(f"JUnit: {junit_path}")
        print(f"Runner mode: {summary['runner_mode']}")
        print(f"Eval mode: {args.eval_mode}")
        if case_filters:
            print(f"Case filters: {', '.join(case_filters)}")
        if category_filters:
            print(f"Category filters: {', '.join(category_filters)}")
        print(f"Timeout profile: {args.timeout_profile}")
        print(f"Timeout seconds: {summary['timeout_sec']}")
        print(f"Tier-2 mode: {args.tier2_mode}")
        for gap in summary.get("claim_to_evidence", {}).get("blocking_gaps", []):
            print(f"CLAIM-GATE: {gap.get('type')}: {gap.get('message')}")
        for w in summary.get("preflight_warnings", []):
            print(f"WARNING: {w}")
        for c in summary["cases"]:
            status = "PASS" if c["passed"] else "FAIL"
            print(f"- {status}: {c['id']} ({c['name']})")
            for f in c["tier1_failures"]:
                print(f"    - TIER1: {f}")
            for f in c["tier2_findings"]:
                print(f"    - TIER2: {f}")
        if summary["passed"] and any_tier2_failed and args.tier2_mode == "warn":
            print("RESULT: PASS (tier-2 findings present; warn mode)")
        elif summary["passed"]:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")

    return int(summary["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
