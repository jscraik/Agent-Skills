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
sys.path.insert(0, str(WORKSPACE_ROOT / "Infrastructure" / "scripts" / "lib"))

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
    elif preferred.exists() and not already_reexec:
        env = dict(os.environ)
        env["SKILL_CREATOR_PYYAML_REEXEC"] = "1"
        facade = SCRIPT_DIR / "run_skill_evals.py"
        os.execve(str(preferred), [str(preferred), str(facade), *sys.argv[1:]], env)
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
from ask.skills_sdk.release_rubric_checks import evaluate_semantic_requirements  # noqa: E402
from ask.skills_sdk.ab_transport_contracts import (  # noqa: E402
    OSS_CLOUD_MODEL,
    actual_opaque_env_path,
    configs_auth_backed_invocation,
    configs_oss_cloud_exec_command,
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

__all__ = [name for name in globals() if not name.startswith("__")]
