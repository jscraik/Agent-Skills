from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import shutil
import tempfile
import hashlib
import time
from collections.abc import Mapping
from pathlib import Path
from ask.envelope import CallResult, ErrorObject
from ask.commands.skills_impl import _python_command_supports_packages, _subprocess_env_with_uv_cache
from ask.skill_review_dashboard import render_skill_review_dashboard
from ask.skills_sdk.tessl_eval_quality import (
    normalize_tessl_acceptance_item,
    tessl_eval_quality_findings,
)
from ask.skills_sdk.generated_eval_fixtures import parse_generated_eval_fixtures
from ask.skills_sdk.handoff_readiness import default_handoff_readiness_path


SKILL_BUILDER_SCRIPTS = "Plugins/skill-factory/scripts/skill-builder"
SMOKE_CASE_TIMEOUT_SECONDS = 600
SMOKE_EVAL_TIMEOUT_SECONDS = 10800
RELEASE_EVAL_TIMEOUT_SECONDS = 21600
QWEN_OSS_LOCAL_MAX_BATCH_CASES = 2
SMOKE_EVAL_MODEL = "gpt-5.3-codex-spark"
# Codex CLI selects `[profiles.fast]` with the plain profile name.
SMOKE_EVAL_PROFILE = "fast"
DEFAULT_MACRO_EVAL_REPORTS_GLOB = "Infrastructure/artifacts/skills/*/*/summary.json"
TESSL_SCENARIO_TOOL_TILE = "tessl-labs/tessl-skill-eval-scenarios"
TESSL_SCENARIO_TOOL_VERSION = "0.1.0"
TESSL_DEFAULT_WORKSPACE = "jscraik"
TESSL_TILE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
TESSL_LIVE_PRIVATE_MIN_SCENARIOS = 20
TESSL_LIVE_PRIVATE_MAX_SCENARIOS = 20
TESSL_LIVE_PRIVATE_VARIANT_COUNT = 2
TESSL_LIVE_PRIVATE_MODEL_TASKS_PER_VARIANT = 2
TESSL_WORKSPACE_RUN_LIMIT = 300
TESSL_WORKSPACE_RUN_LIMIT_SOURCE = "operator_provided_limit"
TESSL_WORKSPACE_RUN_RESERVE = 20
TESSL_LIVE_PRIVATE_MIN_SCORE = 0.90
TESSL_LIVE_PRIVATE_TARGET_SCORE = 0.95
TESSL_LOCAL_REVIEW_MIN_SCORE = 95
TESSL_LIVE_PRIVATE_VIEW_POLL_SECONDS = 10
TESSL_LIVE_PRIVATE_VIEW_TIMEOUT_SECONDS = 900
TESSL_PROJECT_LINK_TIMEOUT_SECONDS = 60


def _pyyaml_eval_python_command() -> list[str]:
    """Return a PyYAML-capable Python command without invoking mise project resolution."""
    candidates: list[list[str]] = []
    configured = os.environ.get("PYTHON_BIN", "").strip()
    if configured:
        candidates.append(shlex.split(configured))

    candidates.append([sys.executable])

    pyyaml_venv_python = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if pyyaml_venv_python.exists():
        candidates.append([str(pyyaml_venv_python)])

    for name in ["python3", "python"]:
        python_path = shutil.which(name)
        if python_path:
            candidates.append([python_path])

    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        key = tuple(candidate)
        if key in seen:
            continue
        seen.add(key)
        if _python_command_supports_packages(candidate, ["pyyaml"]):
            return candidate

    return ["uv", "run", "--no-project", "--with", "PyYAML", "python"]


EVAL_BLOCKER_TAXONOMY = {
    "blocked_user_input": "The runner requested user input and should not be treated as hung.",
    "blocked_auth": "The runner stopped on authentication or credential setup.",
    "blocked_runtime": "The runner was blocked by local runtime, sandbox, or model-capacity limits.",
    "timeout_no_output": "The eval timed out without producing final output.",
    "timeout_partial_output": "The eval timed out after producing partial output.",
    "blocked_missing_tool": "A required local command, runtime, package, or validator is unavailable.",
    "blocked_missing_artifact": "An expected report, transcript, output, or generated artifact is absent.",
    "blocked_environment": "The selected workspace, sandbox, cwd, or permission profile cannot run the check.",
    "blocked_validation": "A structural or policy validation gate failed for the capability.",
}


EVAL_LIFECYCLE_EVENT_TYPES = {
    "eval_started": "A workout, smoke eval, or proof run started for a capability.",
    "eval_blocked": "A workout, smoke eval, or proof run stopped on a classified blocker.",
    "eval_completed": "A workout, smoke eval, or proof run completed with pass or fail status.",
}


EVAL_CLOSEOUT_SCHEMA_VERSION = "skills-sdk.eval-closeout.v1"
EVAL_CLOSEOUT_REQUIRED_FIELDS = {
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


def _qwen_oss_local_batch_blocker(
    *,
    mode: str,
    runner: str,
    codex_profile: str | None,
    selected_cases: list[str],
) -> dict[str, object] | None:
    """Block oversized qwen oss-local batches before runtime degrades into prompt-only artifacts."""
    if mode not in {"smoke", "release"} or runner != "codex" or codex_profile != "oss-local":
        return None
    if not selected_cases:
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "failure_category": "runtime_mismatch",
            "profile": codex_profile,
            "given": f"unfiltered qwen oss-local {mode} run",
            "should": f"run at most {QWEN_OSS_LOCAL_MAX_BATCH_CASES} cases per qwen oss-local shard",
            "actual": "no --case filter supplied",
            "expected": "split the selected cases into smaller --case batches before widening the qwen eval lane",
            "evidence_refs": [
                "Infrastructure/artifacts/skills/improve-agent-native/20260703-193025-822290/workflow-closeout.json",
                ".harness/evidence/handoff/improve-agent-native/qwen-smoke-coverage-map.json",
            ],
            "reproduce_command": (
                "./bin/ask sdk eval run <skill> --runner internal --mode smoke "
                "--codex-profile oss-local --timeout-seconds 120 --case <up-to-two-cases> --json --robot"
            ),
        }
    if len(selected_cases) <= QWEN_OSS_LOCAL_MAX_BATCH_CASES:
        return None

    return {
        "status": "blocked",
        "blocker_class": "blocked_validation",
        "failure_category": "runtime_mismatch",
        "profile": codex_profile,
        "given": f"{len(selected_cases)} selected cases for qwen oss-local {mode}",
        "should": f"run at most {QWEN_OSS_LOCAL_MAX_BATCH_CASES} cases per qwen oss-local shard",
        "actual": selected_cases,
        "expected": "split the selected cases into smaller --case batches before widening the qwen eval lane",
        "evidence_refs": [
            "Infrastructure/artifacts/skills/improve-agent-native/20260703-193025-822290/workflow-closeout.json",
            ".harness/evidence/handoff/improve-agent-native/qwen-smoke-coverage-map.json",
        ],
        "reproduce_command": (
            "./bin/ask sdk eval run <skill> --runner internal --mode smoke "
            "--codex-profile oss-local --timeout-seconds 120 --case <up-to-two-cases> --json --robot"
        ),
    }


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "skill"


def _frontmatter_scalar(value: str) -> str:
    scalar = value.strip()
    if len(scalar) >= 2 and scalar[0] == scalar[-1] and scalar[0] in {'"', "'"}:
        return scalar[1:-1]
    return scalar


def _read_skill_frontmatter(source_root: Path) -> dict[str, object]:
    skill_md = source_root / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}

    frontmatter: dict[str, object] = {}
    current_mapping: str | None = None
    for raw_line in text[3:end].splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line[:1].isspace():
            if current_mapping is None or ":" not in raw_line:
                continue
            key, value = raw_line.strip().split(":", 1)
            mapping = frontmatter.setdefault(current_mapping, {})
            if isinstance(mapping, dict):
                mapping[key.strip()] = _frontmatter_scalar(value)
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        if value.strip():
            frontmatter[key] = _frontmatter_scalar(value)
            current_mapping = None
        else:
            frontmatter[key] = {}
            current_mapping = key
    return frontmatter


def _skill_tessl_tile_version(source_root: Path) -> str:
    frontmatter = _read_skill_frontmatter(source_root)
    metadata = frontmatter.get("metadata")
    version = None
    if isinstance(metadata, dict):
        version = metadata.get("version")
    if not version:
        version = frontmatter.get("version")
    if not isinstance(version, str) or not TESSL_TILE_VERSION_RE.fullmatch(version.strip()):
        raise ValueError(
            "Tessl live private evals require a SemVer SKILL.md frontmatter version "
            "at metadata.version or version."
        )
    return version.strip()


def _canonical_skill_identifier(repo_root: Path, skill_path: str) -> str:
    candidate = Path(skill_path)
    if candidate.name == "SKILL.md":
        candidate = candidate.parent
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(repo_root.resolve())
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix()


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_text(value, encoding="utf-8") -> str:
    """Convert subprocess output to text, handling bytes/None safely.

    Returns:
        - "" for None
        - Decoded string for bytes (with errors="replace")
        - String as-is for str values
    """
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(encoding, errors="replace")
    return str(value)


def _parse_json_value_from_text(text: str) -> object | None:
    stripped = text.strip()
    if not stripped:
        return None
    decoder = json.JSONDecoder()
    for start, char in enumerate(stripped):
        if char not in {"{", "["}:
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[start:])
        except json.JSONDecodeError:
            continue
        return parsed
    return None


def _parse_json_object_from_text(text: str) -> dict[str, object] | None:
    parsed = _parse_json_value_from_text(text)
    if isinstance(parsed, dict):
        return parsed
    return None


def _extract_tessl_eval_run_id(text: str) -> str | None:
    parsed = _parse_json_value_from_text(text)
    candidates: list[object] = []
    if isinstance(parsed, dict):
        candidates.extend([
            parsed.get("id"),
            parsed.get("evalRunId"),
            parsed.get("eval_run_id"),
            parsed.get("runId"),
        ])
        data = parsed.get("data")
        if isinstance(data, dict):
            candidates.extend([
                data.get("id"),
                data.get("evalRunId"),
                data.get("eval_run_id"),
                data.get("runId"),
            ])
    elif isinstance(parsed, list):
        for item in parsed:
            if not isinstance(item, dict):
                continue
            candidates.extend([
                item.get("id"),
                item.get("evalRunId"),
                item.get("eval_run_id"),
                item.get("runId"),
            ])
            data = item.get("data")
            if isinstance(data, dict):
                candidates.extend([
                    data.get("id"),
                    data.get("evalRunId"),
                    data.get("eval_run_id"),
                    data.get("runId"),
                ])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    match = re.search(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", text, re.I)
    return match.group(0) if match else None


def _score_solution(solution: dict[str, object]) -> tuple[float, float]:
    score = 0.0
    max_score = 0.0
    assessment_results = solution.get("assessmentResults")
    if not isinstance(assessment_results, list):
        return score, max_score
    for result in assessment_results:
        if not isinstance(result, dict):
            continue
        raw_score = result.get("score")
        raw_max = result.get("max_score", 1)
        if isinstance(raw_score, (int, float)):
            score += float(raw_score)
        if isinstance(raw_max, (int, float)):
            max_score += float(raw_max)
    return score, max_score


def _tessl_solution_failed_criteria(solution: dict[str, object]) -> list[dict[str, object]]:
    failed: list[dict[str, object]] = []
    assessment_results = solution.get("assessmentResults")
    if not isinstance(assessment_results, list):
        return failed
    for result in assessment_results:
        if not isinstance(result, dict):
            continue
        raw_score = result.get("score")
        raw_max = result.get("max_score", 1)
        if not isinstance(raw_score, (int, float)) or not isinstance(raw_max, (int, float)):
            continue
        if raw_score >= raw_max:
            continue
        failed.append({
            "name": result.get("name"),
            "score": raw_score,
            "max_score": raw_max,
            "reasoning": result.get("reasoning"),
        })
    return failed


def _tessl_solution_missing_observable_output(solution: dict[str, object]) -> bool:
    failed = _tessl_solution_failed_criteria(solution)
    if not failed:
        return False
    text = " ".join(str(item.get("reasoning") or "") for item in failed).lower()
    return (
        "no agent response" in text
        or "no response artifact" in text
        or "no transcript" in text
        or "only the fixture/context files" in text
        or "only the fixture/skill package files" in text
        or "only the vendored skill package" in text
    )


def _tessl_eval_view_status(payload: dict[str, object]) -> str | None:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    status = attributes.get("status") if isinstance(attributes, dict) else None
    return status.strip().lower() if isinstance(status, str) and status.strip() else None


def _tessl_eval_view_failure_reason(payload: dict[str, object]) -> tuple[str, str] | None:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    reason = attributes.get("failureReason") if isinstance(attributes, dict) else None
    if not isinstance(reason, dict):
        return None
    code = str(reason.get("code") or "EVAL_FAILED").strip()
    message = str(reason.get("message") or "Tessl eval failed before scored results were available.").strip()
    return code, message


def _tessl_eval_view_has_complete_scores(payload: dict[str, object]) -> bool:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    scenarios = attributes.get("scenarios") if isinstance(attributes, dict) else None
    if not isinstance(scenarios, list) or not scenarios:
        return False
    scored_scenarios = 0
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        solutions = scenario.get("solutions")
        if not isinstance(solutions, list) or not solutions:
            return False
        usage_solution = next((s for s in solutions if isinstance(s, dict) and s.get("variant") == "usage-spec"), None)
        baseline_solution = next((s for s in solutions if isinstance(s, dict) and s.get("variant") == "baseline"), None)
        if not isinstance(usage_solution, dict) or not isinstance(baseline_solution, dict):
            return False
        usage_results = usage_solution.get("assessmentResults")
        baseline_results = baseline_solution.get("assessmentResults")
        if not isinstance(usage_results, list) or not usage_results:
            return False
        if not isinstance(baseline_results, list) or not baseline_results:
            return False
        scored_scenarios += 1
    return scored_scenarios > 0


def _write_tessl_live_view_evidence(repo_root: Path, skill_path: str, run_id: str | None, view_raw_output: str) -> str | None:
    if not run_id or not view_raw_output.strip():
        return None
    view_path = _tessl_live_evidence_file(repo_root, skill_path, run_id, "tessl-eval-view.json")
    if view_path is None:
        return None
    sanitized_output = _sanitize_tessl_live_private_payload(view_raw_output)
    if not _write_tessl_live_evidence_text(repo_root, view_path, str(sanitized_output)):
        return None
    return str(view_path.relative_to(repo_root))


def _write_tessl_live_submission_evidence(
    repo_root: Path,
    skill_path: str,
    *,
    run_id: str | None,
    workspace: str,
    staged_source: Path,
    project_identity: Mapping[str, object],
) -> str | None:
    if not run_id:
        return None
    submission_path = _tessl_live_evidence_file(repo_root, skill_path, run_id, "tessl-eval-submission.json")
    if submission_path is None:
        return None
    if not _write_tessl_live_evidence_text(
        repo_root,
        submission_path,
        json.dumps(
            {
                "status": "submitted_pending_view",
                "run_id": run_id,
                "workspace": workspace,
                "skill_path": skill_path,
                "staged_source": str(_sanitize_tessl_live_private_payload(str(staged_source))),
                "project_identity": _sanitize_tessl_live_private_payload(dict(project_identity)),
                "next_action": "poll tessl eval view through the Skills SDK wrapper until scored or blocked",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    ):
        return None
    return str(submission_path.relative_to(repo_root))


def _tessl_live_evidence_file(repo_root: Path, skill_path: str, run_id: str, filename: str) -> Path | None:
    run_segment = _tessl_evidence_segment(run_id)
    if run_segment is None:
        return None
    handle = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(skill_path).name).strip("-") or "skill"
    root = repo_root / ".harness" / "evidence" / "tessl"
    if _path_has_symlink_component_under(root, repo_root):
        return None
    root_resolved = root.resolve(strict=False)
    evidence_dir = (root / handle / run_segment).resolve(strict=False)
    try:
        evidence_dir.relative_to(root_resolved)
    except ValueError:
        return None
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / filename
    return None if path.is_symlink() else path


def _path_has_symlink_component_under(path: Path, root: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    current = root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _tessl_evidence_segment(value: str) -> str | None:
    segment = value.strip()
    if segment in {"", ".", ".."}:
        return None
    return segment if re.fullmatch(r"[A-Za-z0-9_.-]+", segment) else None


def _write_tessl_live_evidence_text(repo_root: Path, path: Path, value: str) -> bool:
    root = (repo_root / ".harness" / "evidence" / "tessl").resolve(strict=False)
    try:
        path.parent.resolve(strict=False).relative_to(root)
    except ValueError:
        return False
    archived_previous_path = _archive_existing_tessl_live_evidence(repo_root, path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        file_descriptor = os.open(path, flags, 0o600)
    except OSError:
        return False
    with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
        handle.write(value)
    _record_tessl_live_evidence_index(repo_root, path, value, archived_previous_path)
    return True


def _archive_existing_tessl_live_evidence(repo_root: Path, path: Path) -> str | None:
    if not path.exists() or not path.is_file() or path.is_symlink():
        return None
    try:
        if path.stat().st_size <= 0:
            return None
    except OSError:
        return None

    root = repo_root / ".harness" / "evidence" / "tessl"
    try:
        relative_path = path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return None
    archive_dir = root / "_archive" / relative_path.parent
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{_tessl_archive_suffix()}-{path.name}"
    try:
        shutil.copy2(path, archive_path)
    except OSError:
        return None
    return str(archive_path.relative_to(repo_root))


def _record_tessl_live_evidence_index(
    repo_root: Path,
    path: Path,
    value: str,
    archived_previous_path: str | None,
) -> None:
    root = repo_root / ".harness" / "evidence" / "tessl"
    try:
        relative_path = path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return
    parts = relative_path.parts
    if len(parts) < 3 or parts[0] == "_archive":
        return

    parsed = _parse_json_object_from_text(value)
    status = _tessl_eval_view_status(parsed) if isinstance(parsed, dict) else None
    summary: dict[str, object] | None = None
    if isinstance(parsed, dict) and _tessl_eval_view_has_complete_scores(parsed):
        try:
            score_summary = _summarize_tessl_live_eval_view(parsed)
        except ValueError:
            score_summary = None
        if score_summary is not None:
            summary = {
                "score": score_summary.get("score"),
                "baseline_score": score_summary.get("baseline_score"),
                "score_delta_vs_baseline": score_summary.get("score_delta_vs_baseline"),
                "meets_min_score": score_summary.get("meets_min_score"),
                "meets_target_score": score_summary.get("meets_target_score"),
                "beats_baseline": score_summary.get("beats_baseline"),
                "regression_count": len(score_summary.get("regressions") or []),
            }

    index_path = root / "index.jsonl"
    entry = {
        "schema_version": "skills-sdk.tessl-live-evidence-index.v1",
        "recorded_at": _utc_now_iso(),
        "skill_handle": parts[0],
        "run_id": parts[1],
        "artifact_type": parts[-1],
        "raw_evidence_path": str(path.relative_to(repo_root)),
        "raw_evidence_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "raw_evidence_bytes": len(value.encode("utf-8")),
        "status": status,
        "summary": summary,
        "archived_previous_path": archived_previous_path,
        "retention_policy": (
            "raw Tessl JSON is local forensic evidence; preserve it for failure analysis and "
            "track compact index rows for handoff/review."
        ),
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with index_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
    except OSError:
        return


def _collect_tessl_metric_fields(value: object, *, tokens: tuple[str, ...]) -> dict[str, object]:
    metrics: dict[str, object] = {}

    def visit(current: object, path: tuple[str, ...]) -> None:
        if isinstance(current, dict):
            for key, child in current.items():
                if isinstance(key, str):
                    visit(child, (*path, key))
            return
        if isinstance(current, list):
            for index, child in enumerate(current):
                visit(child, (*path, str(index)))
            return
        if not isinstance(current, int | float) or isinstance(current, bool):
            return
        joined_path = ".".join(path)
        lower_path = joined_path.lower()
        if any(token in lower_path for token in tokens):
            metrics[joined_path] = current

    visit(value, ())
    return metrics


def _is_discovery_smoke_filter_blocker(raw_error: object) -> bool:
    return "discovery-smoke runner requires eval cases with `smoke_mode`" in _as_text(raw_error)


def _summarize_tessl_live_eval_view(payload: dict[str, object]) -> dict[str, object]:
    data = payload.get("data")
    attributes = data.get("attributes") if isinstance(data, dict) else None
    scenarios = attributes.get("scenarios") if isinstance(attributes, dict) else None
    if not isinstance(scenarios, list):
        raise ValueError("Tessl eval view JSON did not include data.attributes.scenarios.")
    attributes = attributes if isinstance(attributes, dict) else {}

    usage_score = 0.0
    baseline_score = 0.0
    max_score = 0.0
    scenario_summaries: list[dict[str, object]] = []

    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        solutions = scenario.get("solutions")
        if not isinstance(solutions, list):
            continue
        usage_solution = next((s for s in solutions if isinstance(s, dict) and s.get("variant") == "usage-spec"), None)
        baseline_solution = next((s for s in solutions if isinstance(s, dict) and s.get("variant") == "baseline"), None)
        if not isinstance(usage_solution, dict) or not isinstance(baseline_solution, dict):
            continue

        scenario_usage, scenario_max = _score_solution(usage_solution)
        scenario_baseline, baseline_max = _score_solution(baseline_solution)
        if scenario_max <= 0:
            scenario_max = baseline_max
        usage_score += scenario_usage
        baseline_score += scenario_baseline
        max_score += scenario_max

        scenario_summaries.append({
            "id": scenario.get("id"),
            "path": scenario.get("path"),
            "description": scenario.get("shortDescription"),
            "usage_score": scenario_usage,
            "baseline_score": scenario_baseline,
            "max_score": scenario_max,
            "regression": scenario_usage < scenario_baseline,
            "usage_failed_criteria": _tessl_solution_failed_criteria(usage_solution),
            "baseline_failed_criteria": _tessl_solution_failed_criteria(baseline_solution),
            "usage_missing_observable_output": _tessl_solution_missing_observable_output(usage_solution),
            "baseline_missing_observable_output": _tessl_solution_missing_observable_output(baseline_solution),
        })

    if max_score <= 0:
        raise ValueError("Tessl eval view JSON did not include scored baseline and usage-spec solutions.")

    usage_rate = usage_score / max_score
    baseline_rate = baseline_score / max_score
    improvement = None if baseline_rate == 0 else usage_rate / baseline_rate
    regressions = [s for s in scenario_summaries if s.get("regression")]
    evidence_shape_regressions = [
        s for s in regressions
        if s.get("usage_missing_observable_output") and not s.get("baseline_missing_observable_output")
    ]
    baseline_ties = [
        s for s in scenario_summaries
        if s.get("usage_score") == s.get("baseline_score")
    ]
    turn_metrics = _collect_tessl_metric_fields(attributes, tokens=("turn",))
    token_metrics = _collect_tessl_metric_fields(attributes, tokens=("token",))
    cost_metrics = _collect_tessl_metric_fields(attributes, tokens=("cost", "price", "spend"))
    return {
        "score": usage_rate,
        "baseline_score": baseline_rate,
        "improvement": improvement,
        "comparative_quality": {
            "with_skill_score": usage_rate,
            "without_skill_score": baseline_rate,
            "improvement": improvement,
            "beats_baseline": usage_rate > baseline_rate,
            "baseline_ties_count": len(baseline_ties),
            "regressions_count": len(regressions),
        },
        "model_selection": {
            "agent": attributes.get("agent"),
            "model": attributes.get("model"),
            "scorer_agent": attributes.get("scorerAgent") or attributes.get("scorer_agent"),
            "scorer_model": attributes.get("scorerModel") or attributes.get("scorer_model"),
            "quality_floor_before_cost": True,
            "cost_is_secondary_to_score": True,
        },
        "cost_observability": {
            "turn_metrics_available": bool(turn_metrics),
            "token_metrics_available": bool(token_metrics),
            "cost_metrics_available": bool(cost_metrics),
            "turn_metrics": turn_metrics,
            "token_metrics": token_metrics,
            "cost_metrics": cost_metrics,
        },
        "usage_points": usage_score,
        "baseline_points": baseline_score,
        "max_points": max_score,
        "scenarios_count": len(scenario_summaries),
        "regressions_count": len(regressions),
        "regressions": regressions,
        "evidence_shape_regressions_count": len(evidence_shape_regressions),
        "evidence_shape_regressions": evidence_shape_regressions,
        "baseline_ties_count": len(baseline_ties),
        "baseline_ties": baseline_ties,
        "min_score_required": TESSL_LIVE_PRIVATE_MIN_SCORE,
        "target_score": TESSL_LIVE_PRIVATE_TARGET_SCORE,
        "meets_min_score": usage_rate >= TESSL_LIVE_PRIVATE_MIN_SCORE,
        "beats_baseline": usage_rate > baseline_rate,
    }


def _tessl_staging_root_template() -> str:
    """Return the human-readable template for stable Tessl eval staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-evals" / "<skill-path>-<sha12>")


def _tessl_live_staging_root_template() -> str:
    """Return the human-readable template for private Tessl live tile staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-evals" / "<skill-path>-<sha12>")


def _tessl_policy() -> dict:
    """Return the repo's Tessl safety contract for eval runs."""
    return {
        "native_tessl_only": True,
        "no_npx": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_project_input_only": True,
        "stable_staging_root": _tessl_staging_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "tessl_project_marker": "tessl.json",
        "staged_inputs": [
            "SKILL.md",
            "references/evals.yaml",
            "references/contract.yaml",
            "references/task-profile.json",
            "assets/**/*",
            "evals/<case-id>/task.md",
            "evals/<case-id>/criteria.json",
        ],
        "network_permission_required_by_repo": False,
        "project_save_may_use_tessl_service": "only_for_project_link_when_workspace_provided",
        "project_save_default": "compatibility_flag_not_required",
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "when --tessl-workspace is provided, repair/link existing project first and create only when needed",
    }


def _tessl_live_private_policy(workspace: str | None = None) -> dict:
    """Return the repo's opt-in private Tessl plugin eval contract."""
    return {
        "enabled_by": "--tessl-live-private",
        "visibility": "private",
        "plugin_private_required": True,
        "workspace_required": True,
        "workspace": workspace,
        "tile_name_format": "workspace/tile-name",
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "repair/link existing project first and create only when needed",
        "native_tessl_only": True,
        "no_npx": True,
        "no_install": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_plugin_input_only": True,
        "stable_staging_root": _tessl_live_staging_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "tessl_project_marker": "tessl.json",
        "plugin_manifest": ".tessl-plugin/plugin.json",
        "eval_layout": "evals/<case-id>/{task.md,criteria.json}",
        "staged_inputs": [
            ".tessl-plugin/plugin.json",
            "tessl.json",
            "skills/<skill-name>/SKILL.md",
            "skills/<skill-name>/references/evals.yaml",
            "skills/<skill-name>/references/evals/*.md",
            "skills/<skill-name>/references/eval-scenarios.json",
            "skills/<skill-name>/references/contract.yaml",
            "skills/<skill-name>/references/task-profile.json",
            "skills/<skill-name>/references/**/*",
            "skills/<skill-name>/assets/**/*",
            "evals/<case-id>/task.md",
            "evals/<case-id>/criteria.json",
        ],
        "command_shape": "tessl eval run --json --workspace <workspace> <staged-plugin-dir>",
        "scenario_gate": "skill-owned references/evals.yaml plus reviewed generated scenarios are required before live scoring; behavioral skills need at least 20 gold-standard scenarios; structure-only checks must opt out explicitly",
        "min_scenarios_required": TESSL_LIVE_PRIVATE_MIN_SCENARIOS,
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "scenario_count_policy": (
            "oss-local uses a 12-case 9+3 repair canary; oss-cloud expands to "
            "the 20-case 15+5 Tessl rehearsal set; Tessl live is capped to the "
            "same 20-case 15+5 confirmation set by default."
        ),
        "oss_cloud_alignment_policy": (
            "oss-cloud is the Tessl rehearsal lane and must prove the same case "
            "set Tessl live will upload, not a looser subset or wider historical "
            "ledger."
        ),
        "generated_scenario_policy": (
            "generated-eval.* scenarios are blocked from Tessl live by default "
            "unless a later budgeted lane explicitly opts them in with OSS local "
            "and cloud proof plus cost profile evidence."
        ),
        "expected_variants": ["baseline", "usage-spec"],
        "duplicate_run_guard": "before live scoring, block when a pending eval run already exists for the same workspace/project",
        "pre_tessl_feedback_loop": {
            "required_order": [
                "deterministic_local_gates",
                "oss_local_internal_judge",
                "patch_oss_local_failures",
                "oss_cloud_internal_judge",
                "patch_oss_cloud_failures",
                "tessl_local_proof",
                "tessl_live_dry_run",
                "tessl_live_run",
                "patch_tessl_failures",
            ],
            "deterministic_local_gates": [
                "skills audit",
                "sdk eval scenario-quality",
                "sdk eval scorer-quality",
                "sdk eval scorer-calibration",
                "sdk eval regression-plan when prior Tessl or internal judge regressions exist",
            ],
            "internal_judge_sequence": [
                {
                    "profile": "oss-local",
                    "role": "cheap internal remediation judge",
                    "required_before": "oss-cloud",
                    "failure_rule": "owner-classify failures in their source lane; rerun oss-local only when classification shows a local skill regression",
                },
                {
                    "profile": "oss-cloud",
                    "role": "higher-confidence internal remediation judge",
                    "required_before": "tessl_live_dry_run",
                    "failure_rule": "owner-classify failures in their source lane; rerun oss-local only when classification shows a local skill regression",
                },
            ],
            "tessl_sequence": [
                {
                    "stage": "tessl_local_proof",
                    "role": "local Tessl lint, pack, temp install, and optional review proof before staged external scoring",
                },
                {
                    "stage": "tessl_live_dry_run",
                    "role": "package and scenario staging proof before external scoring",
                },
                {
                    "stage": "tessl_live_run",
                    "role": "external confirmation lane after internal judges pass",
                },
            ],
            "failure_loop": "Any oss-local, oss-cloud, Tessl local-proof, dry-run, or live Tessl failure stays in its source lane until owner classification identifies the repair surface; rerun oss-local only for classified local skill regressions.",
            "live_blocked_until": "deterministic gates, oss-local, oss-cloud, Tessl local-proof, and Tessl dry-run all pass for the current candidate or an explicit skip/blocker receipt is recorded.",
        },
        "model_selection_gate": {
            "quality_floor_before_cost": True,
            "cost_is_secondary_to_score": True,
            "required_summary_fields": [
                "model_selection",
                "comparative_quality",
                "cost_observability",
            ],
            "acceptance": "with-skill score must meet the quality floor and beat baseline before model cost can be treated as a selection advantage",
        },
        "cost_observability": {
            "track_turns_when_available": True,
            "track_tokens_when_available": True,
            "track_cost_when_available": True,
            "missing_metrics_are_explicit": True,
            "pre_live_budget_receipt": "skills-sdk.tessl-live-budget-preflight.v1",
            "expected_model_tasks": "scenario_count * 2 variants * (solve + score)",
        },
        "run_limit_policy": {
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "limit_source": TESSL_WORKSPACE_RUN_LIMIT_SOURCE,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "verification_commands": [
                "tessl eval list --json --workspace <workspace>",
                "tessl eval view --json <run-id>",
            ],
            "preflight": "before live scoring, check remaining Tessl workspace run capacity when the API/list surface is available; otherwise use the operator-provided 300-run cap and preserve reserve for rerun/remediation",
            "block_when": "remaining run capacity cannot be checked and the run is nonessential, or known remaining capacity is at/below reserve; use dry-run staging and local scenario gates instead",
        },
        "readiness_gate": "after run completion, fetch tessl eval view --json and require usage score >= 90% and usage score > baseline; 95% remains the target",
        "min_score_required": TESSL_LIVE_PRIVATE_MIN_SCORE,
        "target_score": TESSL_LIVE_PRIVATE_TARGET_SCORE,
        "usage_data_opt_out": "tessl config set shareUsageData false",
    }


def _tessl_live_handoff_readiness(repo_root: Path, skill_path: str) -> dict:
    from ask.skills_sdk.handoff_readiness import build_handoff_readiness_receipt  # noqa: PLC0415

    return build_handoff_readiness_receipt(
        repo_root,
        source_path=repo_root / skill_path,
        query=skill_path,
    )


def _tessl_scenario_generation_root_template() -> str:
    """Return the human-readable template for Tessl scenario-generation staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-scenario-generation" / "<skill-path>-<sha12>")


def _tessl_scenario_generation_policy(workspace: str | None = None) -> dict:
    """Return the repo's Tessl scenario-generation safety contract."""
    return {
        "enabled_by": "ask evals prepare-tessl-scenarios",
        "purpose": "stage a target tile and install Tessl's public scenario-generation skill without installing Tessl state into the repo root",
        "agent_must_generate_scenarios_after_prepare": True,
        "workspace_required": True,
        "workspace": workspace,
        "project_identity_rule": "plugin skills use the plugin project name; standalone skills use the skill name",
        "project_link_check": "repair/link existing project first and create only when needed",
        "scenario_tool_tile": TESSL_SCENARIO_TOOL_TILE,
        "scenario_tool_version": TESSL_SCENARIO_TOOL_VERSION,
        "allowed_install": f"{TESSL_SCENARIO_TOOL_TILE}@{TESSL_SCENARIO_TOOL_VERSION}",
        "allowed_install_scope": "temp tool project only",
        "native_tessl_only": True,
        "no_npx": True,
        "no_repo_root_install": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_tile_input_only": True,
        "stable_staging_root": _tessl_scenario_generation_root_template(),
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection; reruns archive previous staged evidence under evidence-archive/",
        "target_tile": "target-tile",
        "tool_project": "tool-project",
        "scenario_skill_path": ".tessl/plugins/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/SKILL.md",
        "legacy_scenario_skill_path": ".tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/SKILL.md",
        "scenario_reference_path": ".tessl/plugins/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/references/scenario-generation.md",
        "legacy_scenario_reference_path": ".tessl/tiles/tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios/references/scenario-generation.md",
        "generated_output": "target-tile/evals/",
        "canonical_import_target": "references/evals.yaml plus references/evals/*.md after review",
        "live_eval_gate": "the later --tessl-live-private lane stages only reviewed canonical skill assets; generate and import bespoke scenarios before running it",
    }


TESSL_STAGING_IGNORED_NAMES = {".DS_Store"}
TESSL_STAGING_IGNORED_DIRS = {"__MACOSX", ".AppleDouble"}


def _should_skip_tessl_staging_path(source_root: Path, source_path: Path) -> bool:
    try:
        relative_parts = source_path.relative_to(source_root).parts
    except ValueError:
        relative_parts = source_path.parts
    return any(part in TESSL_STAGING_IGNORED_NAMES or part in TESSL_STAGING_IGNORED_DIRS for part in relative_parts)


def _copy_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if not source.exists():
        return []
    _reject_tessl_staging_symlink(source_root, source)
    if _should_skip_tessl_staging_path(source_root, source):
        return []
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return [relative_path]


def _copy_tree_files_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if source.is_symlink():
        _reject_tessl_staging_symlink(source_root, source)
    if not source.is_dir():
        return []

    copied: list[str] = []
    for source_file in sorted(source.rglob("*")):
        if source_file.is_symlink():
            _reject_tessl_staging_symlink(source_root, source_file)
        if not source_file.is_file():
            continue
        if _should_skip_tessl_staging_path(source_root, source_file):
            continue
        child_relative = source_file.relative_to(source_root).as_posix()
        target = target_root / child_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
        copied.append(child_relative)
    return copied


def _copy_tree_files_to_relative_root(
    source_root: Path,
    relative_path: str,
    target_root: Path,
    target_relative_root: str,
) -> list[str]:
    source = source_root / relative_path
    if source.is_symlink():
        _reject_tessl_staging_symlink(source_root, source)
    if not source.is_dir():
        return []

    copied: list[str] = []
    for source_file in sorted(source.rglob("*")):
        if source_file.is_symlink():
            _reject_tessl_staging_symlink(source_root, source_file)
        if not source_file.is_file():
            continue
        if _should_skip_tessl_staging_path(source_root, source_file):
            continue
        child_relative = source_file.relative_to(source_root).as_posix()
        target_relative = f"{target_relative_root.rstrip('/')}/{child_relative}"
        target = target_root / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
        copied.append(target_relative)
    return copied


def _reject_tessl_staging_symlink(source_root: Path, source_path: Path) -> None:
    if not source_path.is_symlink():
        return
    try:
        label = source_path.relative_to(source_root).as_posix()
    except ValueError:
        label = source_path.as_posix()
    raise ValueError(f"Tessl staging refuses symlinked support path: {label}")


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _yaml_compat_value(value: str) -> object:
    scalar = _yaml_scalar(value)
    lowered = scalar.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    return scalar


def _consume_yaml_block(lines: list[str], index: int, parent_indent: int, style: str) -> tuple[str, int]:
    raw_block_lines: list[str] = []
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            raw_block_lines.append("")
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        raw_block_lines.append(raw_line)
        index += 1

    non_empty_indents = [
        len(line) - len(line.lstrip(" "))
        for line in raw_block_lines
        if line.strip()
    ]
    block_indent = min(non_empty_indents) if non_empty_indents else parent_indent + 1
    block_lines = [
        line[block_indent:] if line.strip() else ""
        for line in raw_block_lines
    ]

    if style.startswith(">"):
        folded: list[str] = []
        paragraph: list[str] = []
        for line in block_lines:
            if line.strip():
                paragraph.append(line.strip())
                continue
            if paragraph:
                folded.append(" ".join(paragraph))
                paragraph = []
        if paragraph:
            folded.append(" ".join(paragraph))
        return "\n".join(folded), index
    return "\n".join(block_lines), index


def _consume_yaml_plain_scalar(lines: list[str], index: int, parent_indent: int, raw_value: str) -> tuple[str, int]:
    parts = [_yaml_scalar(raw_value)]
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            break
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent <= parent_indent or stripped.startswith("- "):
            break
        if re.match(r"^[A-Za-z0-9_-]+\s*:", stripped):
            break
        parts.append(stripped)
        index += 1
    return " ".join(part for part in parts if part), index


def _consume_yaml_sequence_dicts(lines: list[str], index: int, parent_indent: int) -> tuple[list[dict[str, str]], int]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        stripped = raw_line.strip()
        if current is not None and not stripped.startswith("- ") and indent <= parent_indent + 1:
            break
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[2:].strip()
            if not stripped:
                index += 1
                continue
        if current is not None and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value.startswith((">", "|")):
                current[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
                continue
            current[key], index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)
            continue
        index += 1

    if current:
        items.append(current)
    return items, index


def _consume_yaml_mapping(lines: list[str], index: int, parent_indent: int) -> tuple[dict[str, object], int]:
    item: dict[str, object] = {}
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        stripped = raw_line.strip()
        if stripped.startswith("- ") or ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value.startswith((">", "|")):
            item[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
            continue
        if raw_value:
            value, index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)
            item[key] = _yaml_compat_value(value)
            continue
        item[key] = {}
        index += 1
    return item, index


def _parse_inline_acceptance_sequence(raw_value: str) -> list[dict[str, str]]:
    text = raw_value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return []
    items: list[dict[str, str]] = []
    raw_items: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escaped = False
    for char in text[1:-1]:
        if quote:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            if depth:
                current.append(char)
            quote = char
            continue
        if char == "{":
            if depth:
                current.append(char)
            depth += 1
            continue
        if char == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth:
                current.append(char)
            else:
                raw_items.append("".join(current))
                current = []
            continue
        if depth:
            current.append(char)

    for raw_item in raw_items:
        item: dict[str, str] = {}
        for match in re.finditer(
            r"(type|value|expected_skill)\s*:\s*(.*?)(?=,\s*(?:type|value|expected_skill)\s*:|$)",
            raw_item,
        ):
            item[match.group(1)] = match.group(2).strip().strip("\"'")
        if item:
            items.append(item)
    return items


def _parse_tessl_eval_cases_compat(text: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_cases = False
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if stripped == "cases:":
            in_cases = True
            index += 1
            continue
        if not in_cases:
            index += 1
            continue
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if not item_text.startswith("id:") and current is not None:
                index += 1
                continue
            if current and current.get("id") and current.get("prompt"):
                cases.append(current)
            current = {}
            stripped = item_text
        if current is None or ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if key == "acceptance":
            if raw_value:
                acceptance = _parse_inline_acceptance_sequence(raw_value)
                index += 1
            else:
                sequence_parent_indent = indent
                for lookahead in lines[index + 1:]:
                    if not lookahead.strip():
                        continue
                    lookahead_indent = len(lookahead) - len(lookahead.lstrip(" "))
                    if lookahead.strip().startswith("- "):
                        sequence_parent_indent = lookahead_indent - 1
                    break
                acceptance, index = _consume_yaml_sequence_dicts(lines, index + 1, sequence_parent_indent)
            current[key] = acceptance  # type: ignore[assignment]
            continue
        if key == "tessl":
            if raw_value:
                index += 1
                continue
            tessl, index = _consume_yaml_mapping(lines, index + 1, indent)
            current[key] = tessl
            continue
        if key not in {
            "id",
            "prompt",
            "unit",
            "given",
            "should",
            "actual_artifact",
            "expected_artifact",
            "reproduce",
            "raw_response_artifact",
            "judge_detail_artifact",
            "judge_raw_output_artifact",
            "judge_parse_error_artifact",
            "judge_schema_error_artifact",
            "positive_example_artifact",
            "negative_example_artifact",
            "source_policy_artifact",
            "risk_dimension",
            "label",
            "synthetic",
            "judge_temperature",
            "judge_runs",
            "sample_count",
            "pass_rate_calibration_artifact",
            "pass_rate_threshold",
            "tessl_live_private",
        }:
            index += 1
            continue
        if raw_value.startswith((">", "|")):
            current[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
            continue
        current[key], index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)

    if current and current.get("id") and current.get("prompt"):
        cases.append(current)
    return cases


def _parse_tessl_eval_cases(evals_path: Path) -> list[dict[str, object]]:
    if not evals_path.exists():
        return []

    text = evals_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_tessl_eval_cases_compat(text)

    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        compat_cases = _parse_tessl_eval_cases_compat(text)
        if compat_cases and (
            "while parsing a block mapping" in str(e)
            or "expected <block end>" in str(e)
        ):
            return compat_cases
        raise ValueError(f"Failed to parse Tessl eval cases from {evals_path}: {e}") from e
    raw_cases = loaded.get("cases", []) if isinstance(loaded, dict) else []
    cases: list[dict[str, object]] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            continue
        case_id = raw_case.get("id")
        prompt = raw_case.get("prompt")
        if case_id is None or prompt is None:
            continue
        case = {"id": str(case_id), "prompt": str(prompt)}
        for field in (
            "unit",
            "given",
            "should",
            "actual_artifact",
            "expected_artifact",
            "reproduce",
            "raw_response_artifact",
            "judge_detail_artifact",
            "judge_raw_output_artifact",
            "judge_parse_error_artifact",
            "judge_schema_error_artifact",
            "positive_example_artifact",
            "negative_example_artifact",
            "source_policy_artifact",
            "risk_dimension",
            "label",
            "synthetic",
            "judge_temperature",
            "judge_runs",
            "sample_count",
            "pass_rate_threshold",
            "pass_rate_calibration_artifact",
            "tessl_live_private",
        ):
            if raw_case.get(field) is not None:
                case[field] = raw_case[field]  # type: ignore[assignment]
        acceptance = raw_case.get("acceptance")
        if isinstance(acceptance, list):
            case["acceptance"] = acceptance  # type: ignore[assignment]
        tessl = raw_case.get("tessl")
        if isinstance(tessl, dict):
            case["tessl"] = tessl  # type: ignore[assignment]
        cases.append(case)
    return cases


FIXTURE_FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z ]+):\s*(.*)$")


def _parse_generated_eval_fixture(fixture_path: Path, source_root: Path) -> dict[str, object] | None:
    """Convert a reviewed KnowledgeOS/Tessl markdown fixture into a Tessl case."""
    text = fixture_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = ""
    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        match = FIXTURE_FIELD_RE.match(line)
        if match:
            current_key = match.group(1).strip().lower().replace(" ", "_")
            fields[current_key] = match.group(2).strip()
            continue
        if current_key and line.strip() and not line.startswith(("-", "#")):
            fields[current_key] = f"{fields[current_key]} {line.strip()}".strip()

    given = fields.get("given", "")
    should = fields.get("should", "")
    good = fields.get("expected_agent_move") or fields.get("good_answer_patterns") or should
    bad = fields.get("expected_failure") or fields.get("bad_answer_patterns") or fields.get("failure_mode", "")
    if not given or not should or not good:
        return None

    relative_path = fixture_path.relative_to(source_root).as_posix()
    raw_id = title.split(":", 1)[0].strip() if title else fixture_path.stem
    case_id = f"generated-{_safe_slug(raw_id)}"
    display_name = title.split(":", 1)[1].strip() if ":" in title else raw_id
    behavior = fields.get("behavior_under_test") or fields.get("knowledge_claim") or should
    prompt = "\n".join([
        "Evaluate whether the installed skill package covers the reviewed operator boundary case described by the hidden checklist.",
        "Score the package instructions and references, not a freshly generated chat response. Look for the safest next action, the boundary that must be preserved, and the proof or check that would make the next step reliable.",
    ])
    acceptance: list[dict[str, str]] = [
        {
            "type": "expected_signal",
            "value": f"The skill package instructs agents to {good}",
        },
        {
            "type": "expected_signal",
            "value": "The skill package names the proof or validation boundary and cites observable package evidence.",
        },
        {
            "type": "expected_signal",
            "value": "The skill package avoids the expected failure mode and blocks readiness overclaims when proof is missing.",
        },
    ]
    if bad:
        acceptance.append({
            "type": "must_not",
            "value": f"The skill package encourages or permits this failure mode: {bad}",
        })
    return {
        "id": case_id,
        "prompt": prompt,
        "unit": display_name or raw_id,
        "given": given,
        "should": GENERIC_GENERATED_SHOULD,
        "hidden_expected_behavior": should,
        "hidden_review_focus": behavior,
        "expected_artifact": relative_path,
        "reproduce": relative_path,
        "acceptance": acceptance,
        "tessl": {
            "generated": True,
            "reviewed_fixture": relative_path,
            "source": "references/evals/*.md",
        },
        "source": relative_path,
        "source_kind": "generated_fixture",
    }


def _parse_generated_eval_fixtures(source_root: Path) -> list[dict[str, object]]:
    return parse_generated_eval_fixtures(source_root)


def _tessl_structure_only_scenario_policy(source_root: Path) -> bool:
    contract_path = source_root / "references" / "contract.yaml"
    if not contract_path.exists():
        return False
    text = contract_path.read_text(encoding="utf-8")

    def compat_policy_enabled() -> bool:
        in_policy = False
        policy_indent = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            if re.match(r"^tessl_scenario_policy\s*:\s*$", stripped):
                in_policy = True
                policy_indent = indent
                continue
            if in_policy and indent <= policy_indent:
                in_policy = False
            if in_policy and re.match(r"^(structure_only|structure_check_only)\s*:\s*true\s*$", stripped):
                return True
        return False

    try:
        import yaml  # type: ignore
    except ImportError:
        return compat_policy_enabled()
    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return compat_policy_enabled()
    policy = loaded.get("tessl_scenario_policy") if isinstance(loaded, dict) else None
    return isinstance(policy, dict) and (
        policy.get("structure_only") is True
        or policy.get("structure_check_only") is True
    )


def _merge_tessl_cases_with_generated_fixtures(
    source_root: Path,
    base_cases: list[dict[str, object]],
    *,
    require_generated: bool,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    generated_cases = _parse_generated_eval_fixtures(source_root)
    generated_yaml_cases = [
        case
        for case in base_cases
        if isinstance(case.get("tessl"), dict) and case["tessl"].get("generated") is True
    ]
    by_id: dict[str, dict[str, object]] = {str(case.get("id")): case for case in base_cases}
    duplicate_ids: list[str] = []
    for case in generated_cases:
        case_id = str(case.get("id"))
        if case_id in by_id:
            duplicate_ids.append(case_id)
            continue
        by_id[case_id] = case
    merged = list(by_id.values())
    manifest = {
        "schema_version": "ask-tessl-scenario-sources.v1",
        "skill_owned_cases": len(base_cases),
        "generated_yaml_cases": len(generated_yaml_cases),
        "generated_fixture_cases": len(generated_cases),
        "duplicate_generated_case_ids": duplicate_ids,
        "structure_only_exception": _tessl_structure_only_scenario_policy(source_root),
        "sources": [
            {"path": "references/evals.yaml", "case_count": len(base_cases), "kind": "skill_owned"},
            {"path": "references/evals/*.md", "case_count": len(generated_cases), "kind": "generated_reviewed"},
        ],
    }
    if (
        require_generated
        and not manifest["structure_only_exception"]
        and not generated_cases
        and not generated_yaml_cases
    ):
        raise ValueError(
            "Tessl live-private evals require reviewed generated scenarios before scoring. "
            "Run ./bin/ask evals prepare-tessl-scenarios <skill> --tessl-workspace <workspace> --json --robot, "
            "generate bespoke scenarios with the Tessl scenario skill, review/import them into references/evals/*.md "
            "or references/evals.yaml, then rerun the live Tessl lane. Structure-only packages may set "
            "tessl_scenario_policy.structure_only: true in references/contract.yaml."
        )
    return merged, manifest


def _select_default_tessl_live_cases(
    base_cases: list[dict[str, object]],
    merged_cases: list[dict[str, object]],
    scenario_manifest: dict[str, object],
) -> list[dict[str, object]]:
    if scenario_manifest.get("structure_only_exception"):
        scenario_manifest["default_live_selection"] = {
            "policy": "structure_only_all_reviewed_scenarios",
            "staged_case_count": len(merged_cases),
            "excluded_generated_fixture_case_ids": [],
            "excluded_over_cap_case_ids": [],
        }
        return merged_cases

    base_by_id = {str(case.get("id")): case for case in base_cases}
    generated_fixture_ids = [
        str(case.get("id"))
        for case in merged_cases
        if str(case.get("id")) not in base_by_id
    ]
    selected = list(base_cases)
    over_cap_cases = selected[TESSL_LIVE_PRIVATE_MAX_SCENARIOS:]
    selected = selected[:TESSL_LIVE_PRIVATE_MAX_SCENARIOS]
    scenario_manifest["default_live_selection"] = {
        "policy": "yaml_confirmation_set_capped_before_live_budget",
        "staged_case_count": len(selected),
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "excluded_generated_fixture_case_ids": generated_fixture_ids,
        "excluded_over_cap_case_ids": [str(case.get("id")) for case in over_cap_cases],
    }
    return selected


BEHAVIORAL_TESSL_ACCEPTANCE_TYPES = {
    "expected_signal",
    "skill_selected",
    "artifact_exists",
    "artifact_contains",
    "command_success",
    "forbidden_signal",
    "must_not",
    "must_not_claim",
    "must_not_do",
    "not_contains",
    "output_schema",
}
KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES = {"regex", "not_regex", "contains", "not_contains"}
PROVENANCE_FIXTURE_PATH_RE = re.compile(r"(?i)\breferences/evals/[^\s]+\.md\b")
PROVENANCE_ONLY_VERBS_RE = re.compile(r"(?i)\b(names?|cites?|references?|points?\s+to|lists?)\b")
GENERIC_EXPECTED_SIGNAL_RE = re.compile(
    r"(?is)^\s*demonstrates\s+the\s+skill-specific\s+behavior\s+in\s+this\s+case\s+should\s+contract\s*:"
)
GENERIC_GENERATED_SHOULD = (
    "Expose package instructions or references that encode the reviewed behavior "
    "under test, preserve safety boundaries, and name the next verifiable action."
)
SHALLOW_EXPECTED_SIGNAL_VALUES = {
    "mission-grounded next step",
    "direct non-workspace handling",
    "skill-specific next step",
    "safe next step",
    "validation evidence",
}
GUARDRAIL_CASE_RE = re.compile(r"(?i)\b(?:guardrail|hallucinat(?:e|ion|ions|ed|ing))\b")
GUARDRAIL_LABEL_RE = re.compile(
    r"(?i)\b(?:label(?:ed|led)?|human labels?|pass/fail|ordinary|adversarial|"
    r"true-positive|true-negative|false-positive|false-negative|precision|recall|held-out|calibrat(?:e|ed|ion))\b"
)
GUARDRAIL_DIMENSION_RE = re.compile(
    r"(?i)\b(?:sentence-level|per-sentence|factual accuracy|knowledge accuracy|"
    r"source-of-truth|relevance|policy compliance|contextual coherence)\b"
)
GUARDRAIL_STRUCTURED_OUTPUT_RE = re.compile(r"(?i)\b(?:machine-readable|structured|json|schema)\b")
GUARDRAIL_OUTCOME_TERMS = ("judge_parse_error", "judge_schema_error", "judge_semantic_fail", "judge_pass")
GUARDRAIL_RESPONSE_SCHEMA_TERMS = (
    "sentence_results",
    "overall_verdict",
    "failure_reason",
    "source_references",
)
GUARDRAIL_FAIL_CLOSED_RE = re.compile(
    r"(?i)\b(?:fail-closed|fail closed|unsupported factual claim|unsupported claim)\b"
)
SOURCE_REFERENCE_PASS_RE = re.compile(
    r"(?is)\b(?:exact|supporting)\b.*\b(?:source_references|source references|references?)\b.*\bpass\b|"
    r"\bpass\b.*\b(?:exact|supporting)\b.*\b(?:source_references|source references|references?)\b"
)
FAIL_RATIONALE_RE = re.compile(r"(?is)\b(?:rationale|failure_reason|reason)\b.*\bfail\b|\bfail\b.*\b(?:rationale|failure_reason|reason)\b")
JUDGE_CASE_RE = re.compile(r"(?i)\b(?:judge|grader|guardrail|hallucinat(?:e|ion|ions|ed|ing)|faithfulness)\b")
ROLE_TERMS = ("assistant", "agent", "model", "skill")
UNSTAGED_TESSL_REPO_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?:Infrastructure|Skills|Plugins|Docs|docs|skills-system|runtime|\.agents|\.codex|\.harness|\.skillsets)"
    r"/[^\s,;:)\]}\"']+"
)


def _acceptance_type(item: object) -> str:
    if not isinstance(item, dict):
        return ""
    return str(_normalize_tessl_acceptance_item(item).get("type") or "acceptance").strip().lower()


def _is_provenance_only_signal(value: str) -> bool:
    normalized = " ".join(value.split())
    return (
        bool(PROVENANCE_FIXTURE_PATH_RE.search(normalized))
        and bool(PROVENANCE_ONLY_VERBS_RE.search(normalized))
        and "evidence" in normalized.lower()
    )


def _case_has_behavioral_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    types = {_acceptance_type(item) for item in acceptance}
    return bool(types & BEHAVIORAL_TESSL_ACCEPTANCE_TYPES)


def _case_has_skill_lift_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        item_type = str(normalized.get("type") or "acceptance").strip().lower()
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if item_type in {"skill_selected", "artifact_exists", "artifact_contains", "command_success", "output_schema"}:
            return True
        if item_type.startswith(("forbidden", "must_not")):
            return True
        if (
            item_type == "expected_signal"
            and value
            and not _is_provenance_only_signal(value)
            and not GENERIC_EXPECTED_SIGNAL_RE.match(value)
        ):
            return True
    return False


def _case_has_keyword_only_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        return False
    types = {_acceptance_type(item) for item in acceptance}
    return bool(types) and types <= KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES


def _case_has_shallow_routing_oracle(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        return False
    normalized_items = [
        _normalize_tessl_acceptance_item(item)
        for item in acceptance
        if isinstance(item, dict)
    ]
    types = {str(item.get("type") or "acceptance").strip().lower() for item in normalized_items}
    if not types or not types <= {"skill_selected", "skill_not_selected", "expected_signal"}:
        return False
    expected_values = [
        str(item.get("value") or "").strip().lower()
        for item in normalized_items
        if str(item.get("type") or "").strip().lower() == "expected_signal"
    ]
    if not expected_values:
        return True
    return all(value in SHALLOW_EXPECTED_SIGNAL_VALUES for value in expected_values)


def _case_has_fixture_path_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if _is_provenance_only_signal(value):
            return True
    return False


def _case_has_prompt_scoring_mechanics(case: dict[str, object]) -> bool:
    prompt = str(case.get("prompt") or "")
    scoring_mechanics = (
        "Use the skill to handle this reviewed generated scenario",
        "Scenario fixture:",
        "Uses the generated scenario fixture as evidence",
    )
    return any(mechanic in prompt for mechanic in scoring_mechanics)


def _case_has_answer_leakage(case: dict[str, object]) -> bool:
    visible_text = "\n".join(
        str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")
    ).lower()
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        item_type = str(normalized.get("type") or "acceptance").strip().lower()
        if item_type.startswith(("must_not", "forbidden")):
            continue
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if len(value) >= 80 and value.lower() in visible_text:
            return True
    return False


def _case_has_unstaged_repo_path_reference(case: dict[str, object]) -> bool:
    text_parts = [
        str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")
    ]
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for item in acceptance:
            if not isinstance(item, dict):
                continue
            normalized = _normalize_tessl_acceptance_item(item)
            text_parts.extend([
                str(normalized.get("value") or ""),
                str(normalized.get("expected_skill") or ""),
            ])
    return bool(UNSTAGED_TESSL_REPO_PATH_RE.search("\n".join(text_parts)))


def _case_text_for_quality(case: dict[str, object]) -> str:
    text_parts = [
        str(case.get(field) or "")
        for field in (
            "id",
            "name",
            "category",
            "unit",
            "given",
            "should",
            "prompt",
            "expected_artifact",
            "raw_response_artifact",
            "judge_detail_artifact",
            "judge_raw_output_artifact",
            "judge_parse_error_artifact",
            "judge_schema_error_artifact",
            "positive_example_artifact",
            "negative_example_artifact",
            "source_policy_artifact",
            "risk_dimension",
            "label",
        )
    ]
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for item in acceptance:
            if not isinstance(item, dict):
                continue
            normalized = _normalize_tessl_acceptance_item(item)
            text_parts.extend([
                str(normalized.get("type") or ""),
                str(normalized.get("value") or ""),
                str(normalized.get("expected_skill") or ""),
            ])
    expected_signals = case.get("expected_signals")
    if isinstance(expected_signals, dict):
        for value in expected_signals.values():
            if isinstance(value, list):
                text_parts.extend(str(item) for item in value)
            else:
                text_parts.append(str(value))
    return "\n".join(text_parts)


def _case_has_guardrail_calibration_shape(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    has_structured_output = bool(GUARDRAIL_STRUCTURED_OUTPUT_RE.search(case_text))
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        has_structured_output = has_structured_output or any(
            _acceptance_type(item) == "output_schema" for item in acceptance
        )
    return (
        bool(GUARDRAIL_LABEL_RE.search(case_text))
        and bool(GUARDRAIL_DIMENSION_RE.search(case_text))
        and has_structured_output
    )


def _case_has_paired_calibration_examples(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return True
    positive = case.get("positive_example_artifact") or case.get("passing_example_artifact")
    negative = case.get("negative_example_artifact") or case.get("failing_example_artifact")
    if positive and negative:
        return True
    return not GUARDRAIL_CASE_RE.search(case_text)


def _terms_present(text: str, terms: tuple[str, ...]) -> set[str]:
    present: set[str] = set()
    for term in terms:
        pattern = r"(?i)(?<![A-Za-z0-9_-])" + re.escape(term) + r"(?![A-Za-z0-9_-])"
        if re.search(pattern, text):
            present.add(term)
    return present


def _case_has_mixed_guardrail_terms(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return False
    role_terms = _terms_present(case_text, ROLE_TERMS)
    # In guardrail/judge prompts, multiple role names often make the scorer's
    # target ambiguous. Source-authority terms are intentionally not enforced
    # here because "source-of-truth policy" is a useful composite phrase.
    return len(role_terms) > 1


def _case_has_guardrail_failure_outcomes(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    raw_output = case.get("judge_raw_output_artifact") or case.get("raw_response_artifact")
    return bool(raw_output) and all(term in case_text.lower() for term in GUARDRAIL_OUTCOME_TERMS)


def _case_has_guardrail_response_schema(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    normalized = case_text.lower()
    return (
        all(term in normalized for term in GUARDRAIL_RESPONSE_SCHEMA_TERMS)
        and bool(GUARDRAIL_FAIL_CLOSED_RE.search(case_text))
    )


def _case_has_source_reference_quality(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    return bool(SOURCE_REFERENCE_PASS_RE.search(case_text)) and bool(FAIL_RATIONALE_RE.search(case_text))


def _has_sampling_count(case: dict[str, object]) -> bool:
    return bool(case.get("judge_runs") or case.get("sample_count"))


def _case_has_judge_sampling_policy(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return True
    if case.get("judge_temperature") is not None and not _has_sampling_count(case):
        return False
    return True


def _truthy_metadata(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _synthetic_guardrail_label_balance_findings(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    synthetic_cases = [
        case
        for case in cases
        if _truthy_metadata(case.get("synthetic"))
        and GUARDRAIL_CASE_RE.search(_case_text_for_quality(case))
    ]
    labeled_cases = [
        case
        for case in synthetic_cases
        if str(case.get("label") or "").strip().lower() in {"pass", "fail"}
    ]
    labels = {str(case.get("label") or "").strip().lower() for case in labeled_cases}
    if len(labeled_cases) < 2 or len(labels) >= 2:
        return []
    case_ids = ", ".join(str(case.get("id") or "unknown") for case in labeled_cases[:8])
    return [{
        "case_id": "synthetic_guardrail_suite",
        "code": "guardrail_synthetic_label_imbalance",
        "message": (
            "Synthetic guardrail eval selections must include both pass and fail labels "
            f"before acting as release evidence; selected one-class cases: {case_ids}."
        ),
    }]


def _case_has_scenario_context(case: dict[str, object]) -> bool:
    fields = [str(case.get(field) or "").strip() for field in ("unit", "given", "should")]
    if all(fields):
        return True
    prompt = str(case.get("prompt") or "").strip()
    return prompt.count("\n") >= 3 and len(prompt) >= 240


def _tessl_eval_quality_findings(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    return tessl_eval_quality_findings(cases)


def _assert_tessl_eval_quality(cases: list[dict[str, object]], *, source: Path) -> None:
    if not cases:
        raise ValueError(
            f"Tessl eval quality gate failed for {source}: no Tessl eval cases were selected. "
            "Add structured behavioural scenarios before staging or uploading Tessl assessments."
        )
    findings = _tessl_eval_quality_findings(cases)
    if not findings:
        return
    summary = "; ".join(
        f"{finding['case_id']}:{finding['code']}" for finding in findings[:12]
    )
    if len(findings) > 12:
        summary += f"; +{len(findings) - 12} more"
    raise ValueError(
        f"Tessl eval quality gate failed for {source}: {summary}. "
        "Convert seed or internal evals into structured, skill-specific behavioural scenarios "
        "before staging or uploading Tessl assessments."
    )


def _case_tessl_enabled(raw_case: dict[object, object], *, lane: str) -> bool:
    flat_key = f"tessl_{lane}"
    flat_value = raw_case.get(flat_key)
    if flat_value is False or str(flat_value).strip().lower() == "false":
        return False
    tessl = raw_case.get("tessl")
    if not isinstance(tessl, dict):
        return True
    lane_value = tessl.get(lane)
    if lane_value is False:
        return False
    enabled = tessl.get("enabled")
    return enabled is not False


def _write_tessl_scenarios_from_evals(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    evals_path = source_root / "references" / "evals.yaml"
    cases, scenario_manifest = _merge_tessl_cases_with_generated_fixtures(
        source_root,
        _parse_tessl_eval_cases(evals_path),
        require_generated=False,
    )
    scenario_manifest_path = staged_root / "scenario-sources.json"
    scenario_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_manifest_path.write_text(json.dumps(scenario_manifest, indent=2) + "\n", encoding="utf-8")
    copied.append(str(scenario_manifest_path.relative_to(staged_root)))
    for case in cases:
        case_id = str(case["id"]).replace("/", "-")
        case_root = staged_root / "scenarios" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        task_path = case_root / "task.md"
        task_path.write_text(_tessl_task_markdown(case), encoding="utf-8")
        criteria_path = case_root / "criteria.json"
        criteria_path.write_text(json.dumps(_tessl_criteria_from_case(case), indent=2) + "\n", encoding="utf-8")
        copied.extend([
            str(task_path.relative_to(staged_root)),
            str(criteria_path.relative_to(staged_root)),
        ])
    return copied


def _tessl_plugin_project_slug(source_root: Path) -> str | None:
    parts = source_root.parts
    for index, part in enumerate(parts):
        if part == "Plugins" and index + 2 < len(parts) and parts[index + 2] == "skills":
            return _safe_slug(parts[index + 1].lower())
    return None


def _tessl_project_slug(source_root: Path) -> str:
    plugin_slug = _tessl_plugin_project_slug(source_root)
    if plugin_slug:
        return plugin_slug
    return _safe_slug(source_root.name.lower())


def _tessl_project_identity(source_root: Path, workspace: str | None = None) -> dict[str, str | None]:
    slug = _tessl_project_slug(source_root)
    owner_type = "plugin" if _tessl_plugin_project_slug(source_root) else "standalone_skill"
    return {
        "owner_type": owner_type,
        "project": slug,
        "workspace": workspace,
        "name": f"{workspace}/{slug}" if workspace else slug,
    }


def _write_tessl_project_marker(
    source_root: Path,
    staged_root: Path,
    workspace: str | None = None,
) -> list[str]:
    marker_path = staged_root / "tessl.json"
    identity = _tessl_project_identity(source_root, workspace)
    marker_path.write_text(
        json.dumps({"name": identity["name"], "mode": "managed", "dependencies": {}}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _validate_tessl_workspace(workspace: str | None) -> str:
    if workspace is None or not workspace.strip():
        raise ValueError(f"Tessl live-private evals require workspace {TESSL_DEFAULT_WORKSPACE}.")
    normalized = workspace.strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", normalized):
        raise ValueError(
            "Tessl workspace must be lowercase and contain only letters, numbers, '.', '_', or '-'."
        )
    if "/" in normalized:
        raise ValueError("Tessl workspace must be the workspace name only, not workspace/tile.")
    if normalized != TESSL_DEFAULT_WORKSPACE:
        raise ValueError(
            f"Skills SDK Tessl lanes must use workspace {TESSL_DEFAULT_WORKSPACE}; "
            f"received {normalized}."
        )
    return normalized


def _default_tessl_workspace_from_env() -> tuple[str | None, str | None]:
    for name in ("ASK_TESSL_WORKSPACE", "TESSL_WORKSPACE", "TESSL_WORKSPACE_NAME"):
        value = os.environ.get(name)
        if value is not None and value.strip():
            return _validate_tessl_workspace(value), name
    return TESSL_DEFAULT_WORKSPACE, "default"


def _tessl_eval_case_id(case_id: str) -> str:
    return _safe_slug(case_id.replace("/", "-"))


def _tessl_task_markdown(case: dict[str, object]) -> str:
    lines: list[str] = []
    for label, field in (("Unit", "unit"), ("Given", "given"), ("Should", "should")):
        value = str(case.get(field) or "").strip()
        if value:
            lines.append(f"{label}: {value}")
    if lines:
        lines.append("")
    lines.append(str(case.get("prompt") or "").rstrip())
    return "\n".join(lines).rstrip() + "\n"


def _normalize_tessl_acceptance_item(item: dict[object, object]) -> dict[str, str]:
    return normalize_tessl_acceptance_item(item)


def _tessl_acceptance_description(item: dict[str, str], case: dict[str, object]) -> str:
    criterion_type = str(item.get("type") or "").strip().lower()
    if criterion_type.startswith("text_field_"):
        field = str(item.get("field") or item.get("path") or item.get("name") or "").strip()
        expected_values = str(
            item.get("value")
            or item.get("expected")
            or item.get("expected_value")
            or item.get("values")
            or ""
        ).strip()
        parts = [f"type={criterion_type}"]
        if field:
            parts.append(f"field={field}")
        if expected_values:
            parts.append(f"expected={expected_values}")
        return "; ".join(parts)
    return str(
        item.get("value")
        or item.get("expected_skill")
        or case.get("expected_artifact")
        or "Satisfies acceptance criterion."
    ).strip()


def _tessl_case_source(case: dict[str, object]) -> str:
    return str(case.get("source") or "references/evals.yaml")


def _tessl_criteria_from_case(case: dict[str, object]) -> dict:
    checklist: list[dict[str, object]] = []
    source = _tessl_case_source(case)
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for index, item in enumerate(acceptance, start=1):
            if not isinstance(item, dict):
                continue
            normalized_item = _normalize_tessl_acceptance_item(item)
            criterion_type = str(normalized_item.get("type") or "acceptance").strip().lower()
            value = _tessl_acceptance_description(normalized_item, case)
            category = "MUST_NOT" if criterion_type.startswith(("forbidden", "must_not")) else "INTENT"
            criterion = {
                "name": _safe_slug(f"{criterion_type}-{index}"),
                "description": value,
                "max_score": 1,
                "category": category,
                "source": source,
            }
            if criterion_type.startswith("text_field_"):
                criterion["metadata"] = {
                    "acceptance": {
                        key: normalized_item[key]
                        for key in sorted(normalized_item)
                        if key in {"type", "field", "fields", "value", "values", "expected", "expected_values"}
                    }
                }
            checklist.append({
                **criterion,
            })

    if not checklist:
        checklist.append({
            "name": "task-satisfaction",
            "description": "The agent response satisfies task.md and the skill contract.",
            "max_score": 1,
            "category": "INTENT",
            "source": source,
        })
    criteria_obligation_hash = hashlib.sha256(
        json.dumps(checklist, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    return {
        "context": f"Evaluation criteria adapted from {source} for {case.get('id') or 'unknown'}.",
        "type": "weighted_checklist",
        "checklist": checklist,
        "metadata": {
            "schema_version": "ask-tessl-criteria-adapter.v1",
            "source_case_id": str(case.get("id") or "unknown"),
            "source": source,
            "criteria_obligation_hash": criteria_obligation_hash,
            "source_kind": case.get("source_kind") or "skill_owned",
            "riteway": {
                "unit": case.get("unit"),
                "given": case.get("given"),
                "should": case.get("should"),
                "actual_artifact": case.get("actual_artifact"),
                "expected_artifact": case.get("expected_artifact"),
                "reproduce": case.get("reproduce"),
            },
            "agent_eval_artifacts": {
                "raw_response": case.get("raw_response_artifact"),
                "judge_details": case.get("judge_detail_artifact"),
                "judge_raw_output": case.get("judge_raw_output_artifact")
                or case.get("raw_response_artifact"),
                "judge_parse_error": case.get("judge_parse_error_artifact"),
                "judge_schema_error": case.get("judge_schema_error_artifact"),
            },
            "calibration_examples": {
                "positive": case.get("positive_example_artifact"),
                "negative": case.get("negative_example_artifact"),
            },
            "judge_failure_outcomes": {
                "parse_error": "judge_parse_error",
                "schema_error": "judge_schema_error",
                "semantic_fail": "judge_semantic_fail",
                "pass": "judge_pass",
            },
            "guardrail_output_contract": {
                "sentence_results": "required",
                "overall_verdict": "required",
                "failure_reason": "required",
                "source_references": "required_for_pass_decisions",
                "unsupported_factual_claim": "fail_closed",
                "fail_rationale": "separate_from_pass_reference",
            },
            "synthetic_case": {
                "enabled": case.get("synthetic"),
                "label": case.get("label"),
                "risk_dimension": case.get("risk_dimension"),
                "source_policy_artifact": case.get("source_policy_artifact"),
            },
            "judge_sampling": {
                "temperature": case.get("judge_temperature"),
                "runs": case.get("judge_runs"),
                "sample_count": case.get("sample_count"),
            },
            "pass_rate_policy": {
                "threshold": case.get("pass_rate_threshold"),
                "calibration_artifact": case.get("pass_rate_calibration_artifact"),
                "gate_status": "calibrated_gate" if case.get("pass_rate_calibration_artifact") else "advisory",
            },
        },
    }


def _write_tessl_live_evals_from_references(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    evals_path = source_root / "references" / "evals.yaml"
    base_cases = [
        case for case in _parse_tessl_eval_cases(evals_path)
        if _case_tessl_enabled(case, lane="live_private")
    ]
    cases, scenario_manifest = _merge_tessl_cases_with_generated_fixtures(
        source_root,
        base_cases,
        require_generated=True,
    )
    _assert_tessl_eval_quality(cases, source=evals_path)
    if (
        not scenario_manifest.get("structure_only_exception")
        and len(cases) < TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    ):
        raise ValueError(
            "Tessl live-private evals require at least "
            f"{TESSL_LIVE_PRIVATE_MIN_SCENARIOS} gold-standard structured scenarios for behavioral skills. "
            f"Found {len(cases)}. Add bespoke generated scenarios, review/import them into references/evals.yaml "
            "or references/evals/*.md, then rerun the dry-run staging lane before using Tessl live runs."
        )
    cases = _select_default_tessl_live_cases(base_cases, cases, scenario_manifest)
    scenario_manifest["min_scenarios_required"] = TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    scenario_manifest["meets_min_scenarios"] = len(cases) >= TESSL_LIVE_PRIVATE_MIN_SCENARIOS
    scenario_manifest["run_limit_policy"] = {
        "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
        "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
        "preflight_required": True,
    }
    scenario_manifest_path = staged_root / "scenario-sources.json"
    scenario_manifest_path.write_text(json.dumps(scenario_manifest, indent=2) + "\n", encoding="utf-8")
    copied.append(str(scenario_manifest_path.relative_to(staged_root)))
    for case in cases:
        case_id = _tessl_eval_case_id(str(case["id"]))
        case_root = staged_root / "evals" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        task_path = case_root / "task.md"
        task_path.write_text(_tessl_task_markdown(case), encoding="utf-8")
        criteria_path = case_root / "criteria.json"
        criteria_path.write_text(json.dumps(_tessl_criteria_from_case(case), indent=2) + "\n", encoding="utf-8")
        copied.extend([
            str(task_path.relative_to(staged_root)),
            str(criteria_path.relative_to(staged_root)),
        ])
    return copied


def _write_tessl_live_project_marker(staged_root: Path, workspace: str, tile_slug: str) -> list[str]:
    marker_path = staged_root / "tessl.json"
    marker_path.write_text(
        json.dumps({"name": f"{workspace}/{tile_slug}", "mode": "managed", "dependencies": {}}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _tessl_live_tile_slug(source_root: Path) -> str:
    return _tessl_project_slug(source_root)


def _write_tessl_live_plugin_manifest(source_root: Path, staged_root: Path, workspace: str) -> list[str]:
    tile_slug = _tessl_live_tile_slug(source_root)
    tile_version = _skill_tessl_tile_version(source_root)
    summary = f"Private live eval plugin for {source_root.name}."
    tessl_plugin_manifest = staged_root / ".tessl-plugin" / "plugin.json"
    tessl_plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
    tessl_plugin_payload = {
        "schema_version": 1,
        "name": f"{workspace}/{tile_slug}",
        "version": tile_version,
        "description": summary,
        "private": True,
        "skills": "./skills/",
    }
    tessl_plugin_manifest.write_text(json.dumps(tessl_plugin_payload, indent=2) + "\n", encoding="utf-8")
    return [
        ".tessl-plugin/plugin.json",
        *_write_tessl_live_project_marker(staged_root, workspace, tile_slug),
    ]


def _write_tessl_registry_readme(source_root: Path, staged_root: Path, workspace: str) -> list[str]:
    source_readme = source_root / "README.md"
    readme_target = staged_root / "README.md"
    tile_slug = _tessl_live_tile_slug(source_root)
    if source_readme.exists():
        _reject_tessl_staging_symlink(source_root, source_readme)
        shutil.copy2(source_readme, readme_target)
        _append_tessl_registry_readme_section(readme_target, workspace, tile_slug)
    else:
        readme_target.write_text(
            (
                f"# {source_root.name}\n\n"
                f"Registry presentation for the private Tessl package `{workspace}/{tile_slug}`.\n\n"
                "Agent runtime instructions live in `skills/` and `SKILL.md`; this README is "
                "for registry presentation and should not be treated as agent context.\n\n"
                "## GitHub Badge\n\n"
                "When this package is public in the Tessl registry, paste the registry-provided "
                "GitHub badge Markdown here so repository readers can see the current Tessl score.\n\n"
                "## Score Improvement And CI Gate\n\n"
                "Use `tessl skill review --optimize` to improve a weak registry score before "
                "promotion. Use `tessl review run` in CI when the package needs a score "
                "threshold gate.\n"
            ),
            encoding="utf-8",
        )
    return ["README.md"]


def _append_tessl_registry_readme_section(readme_target: Path, workspace: str, tile_slug: str) -> None:
    text = readme_target.read_text(encoding="utf-8")
    required = ("GitHub Badge", "Tessl registry", "tessl skill review --optimize", "tessl review run")
    if all(phrase in text for phrase in required):
        return
    suffix = (
        "\n\n## Tessl Registry Presentation\n\n"
        f"Registry presentation for the private Tessl package `{workspace}/{tile_slug}`. "
        "Agent runtime instructions live in `skills/` and `SKILL.md`; this README is "
        "for registry presentation and should not be treated as agent context.\n\n"
        "### GitHub Badge\n\n"
        "When this package is public in the Tessl registry, paste the registry-provided "
        "GitHub badge Markdown here so repository readers can see the current Tessl score.\n\n"
        "### Score Improvement And CI Gate\n\n"
        "Use `tessl skill review --optimize` to improve a weak registry score before "
        "promotion. Use `tessl review run` in CI when the package needs a score threshold gate.\n"
    )
    readme_target.write_text(text.rstrip() + suffix, encoding="utf-8")


def _write_tesslignore(staged_root: Path) -> list[str]:
    tesslignore = staged_root / ".tesslignore"
    tesslignore.write_text(
        (
            "# Generated by Skills SDK Tessl staging.\n"
            "# Agent host context is project-local and not plugin package context.\n"
            "AGENTS.md\n"
            "CLAUDE.md\n"
            "GEMINI.md\n"
            "notes.md\n"
            "TODO.md\n"
            "*.draft.md\n"
            "test-data/\n"
            ".harness/\n"
            ".agents/\n"
            ".codex/\n"
            ".tessl/\n"
            "dist/\n"
        ),
        encoding="utf-8",
    )
    return [".tesslignore"]


def _validate_tessl_live_private_manifest(plugin_path: Path, workspace: str, project_slug: str | None = None) -> None:
    manifest = _load_json_object_file(plugin_path, label="staged Tessl plugin manifest")
    plugin_name = manifest.get("name")
    if not isinstance(plugin_name, str) or not plugin_name.startswith(f"{workspace}/"):
        raise ValueError("Staged Tessl plugin name must use workspace/plugin-name format for the requested workspace.")
    if project_slug is not None and plugin_name != f"{workspace}/{project_slug}":
        raise ValueError(
            "Staged Tessl plugin name must match the requested workspace/project "
            f"{workspace}/{project_slug}."
        )
    description = manifest.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Staged Tessl plugin manifest must include a non-empty description.")
    if manifest.get("private") is not True:
        raise ValueError("Staged Tessl plugin manifest must set private: true.")
    version = manifest.get("version")
    if not isinstance(version, str) or not TESSL_TILE_VERSION_RE.fullmatch(version):
        raise ValueError("Staged Tessl plugin manifest must include a SemVer version.")
    skills = manifest.get("skills")
    if skills != "./skills/":
        raise ValueError('Staged Tessl plugin manifest skills must be "./skills/".')
    if "rules" in manifest:
        raise ValueError(
            "Skills SDK Tessl skill projections must keep skill support context in references/, not map it to Tessl rules/."
        )
    if "mcpServers" in manifest and manifest["mcpServers"] not in (".mcp.json", "./.mcp.json"):
        raise ValueError("Staged Tessl plugin manifest mcpServers must point to .mcp.json or ./.mcp.json.")


def _load_json_object_file(path: Path, *, label: str) -> dict[str, object]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to read {label}: {e}") from e
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return loaded


def _validate_tessl_bundled_mcp(staged_root: Path, manifest: dict[str, object]) -> None:
    mcp_path = staged_root / ".mcp.json"
    if "mcpServers" in manifest and not mcp_path.is_file():
        raise ValueError("Staged Tessl plugin manifest declares mcpServers but .mcp.json is missing.")
    if not mcp_path.exists():
        return
    mcp_payload = _load_json_object_file(mcp_path, label="staged Tessl bundled .mcp.json")
    servers = mcp_payload.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        raise ValueError("Staged Tessl bundled .mcp.json must contain a non-empty top-level mcpServers map.")
    for server_name, server_config in servers.items():
        if not isinstance(server_name, str) or not isinstance(server_config, dict):
            raise ValueError("Staged Tessl bundled .mcp.json server entries must be named objects.")
        server_type = server_config.get("type")
        if server_type == "stdio":
            command = server_config.get("command")
            if not isinstance(command, str) or not command.strip():
                raise ValueError("Staged Tessl stdio MCP servers must declare a command.")
        elif server_type == "http":
            url = server_config.get("url")
            if not isinstance(url, str) or not re.fullmatch(r"https?://.+", url):
                raise ValueError("Staged Tessl http MCP servers must declare an http or https url.")
        else:
            raise ValueError("Staged Tessl bundled .mcp.json server type must be stdio or http.")


def _validate_tessl_registry_readme(staged_root: Path) -> None:
    readme_path = staged_root / "README.md"
    try:
        text = readme_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Failed to read staged Tessl README.md: {e}") from e
    required = (
        "GitHub Badge",
        "Tessl registry",
        "tessl skill review --optimize",
        "tessl review run",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ValueError(
            "Staged Tessl README.md must document registry presentation, badge placement, "
            f"score optimization, and CI review gating; missing: {', '.join(missing)}"
        )


def _validate_tessl_project_marker(staged_root: Path, workspace: str, project_slug: str) -> None:
    marker = _load_json_object_file(staged_root / "tessl.json", label="staged Tessl project marker")
    name = marker.get("name")
    expected_name = f"{workspace}/{project_slug}"
    if name != expected_name:
        raise ValueError(
            "Staged Tessl tessl.json must include the exact workspace/project name "
            f"{expected_name}."
        )
    if marker.get("mode") not in ("managed", "vendored"):
        raise ValueError("Staged Tessl tessl.json must declare mode as managed or vendored.")


def _validate_tesslignore(staged_root: Path) -> None:
    ignore_path = staged_root / ".tesslignore"
    try:
        text = ignore_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Failed to read staged Tessl .tesslignore: {e}") from e
    required = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".harness/", ".agents/", ".codex/", "dist/")
    missing = [entry for entry in required if entry not in text]
    if missing:
        raise ValueError("Staged Tessl .tesslignore is missing required exclusions: " + ", ".join(missing))
    forbidden = ("skills", "skills/", "rules", "rules/", "docs", "docs/")
    active_lines = {line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")}
    blocked_entrypoints = sorted(entry for entry in forbidden if entry in active_lines)
    if blocked_entrypoints:
        raise ValueError(
            "Staged Tessl .tesslignore must not ignore manifest entrypoints: "
            + ", ".join(blocked_entrypoints)
        )


def _validate_tessl_eval_directories(staged_root: Path, *, require_evals: bool) -> None:
    evals_root = staged_root / "evals"
    if require_evals and not evals_root.is_dir():
        raise ValueError("Staged Tessl package must include evals/<case-id>/task.md and criteria.json.")
    if not evals_root.exists():
        return
    case_dirs = [path for path in evals_root.iterdir() if path.is_dir()]
    if require_evals and not case_dirs:
        raise ValueError("Staged Tessl package evals/ must contain at least one case directory.")
    missing: list[str] = []
    for case_dir in sorted(case_dirs):
        for filename in ("task.md", "criteria.json"):
            if not (case_dir / filename).is_file():
                missing.append(str((case_dir / filename).relative_to(staged_root)))
    if missing:
        raise ValueError("Staged Tessl eval cases are missing required files: " + ", ".join(missing))


def _validate_tessl_projection_shape(
    staged_root: Path,
    *,
    skill_name: str,
    workspace: str,
    project_slug: str,
    require_evals: bool,
) -> None:
    _validate_tessl_workspace(workspace)
    required_paths = [
        ".tessl-plugin/plugin.json",
        "README.md",
        ".tesslignore",
        "tessl.json",
        f"skills/{skill_name}/SKILL.md",
    ]
    missing = [relative for relative in required_paths if not (staged_root / relative).is_file()]
    if missing:
        raise ValueError("Staged Tessl package is missing required projection files: " + ", ".join(missing))
    if (staged_root / "rules").exists():
        raise ValueError(
            "Skills SDK Tessl skill projections must not place skill support context in root rules/; use references/."
        )
    manifest_path = staged_root / ".tessl-plugin" / "plugin.json"
    _validate_tessl_live_private_manifest(manifest_path, workspace, project_slug)
    manifest = _load_json_object_file(manifest_path, label="staged Tessl plugin manifest")
    _validate_tessl_bundled_mcp(staged_root, manifest)
    _validate_tessl_registry_readme(staged_root)
    _validate_tessl_project_marker(staged_root, workspace, project_slug)
    _validate_tesslignore(staged_root)
    _validate_tessl_eval_directories(staged_root, require_evals=require_evals)


def _copy_tessl_live_reference_support_files(
    source_root: Path,
    staged_root: Path,
    already_copied: set[str],
) -> list[str]:
    references_root = source_root / "references"
    if not references_root.exists():
        return []

    copied: list[str] = []
    for source_file in sorted(references_root.rglob("*")):
        if not source_file.is_file():
            continue
        relative_path = source_file.relative_to(source_root).as_posix()
        if relative_path in already_copied:
            continue
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
        already_copied.add(relative_path)
    return copied


def _copy_tessl_live_skill_package(source_root: Path, staged_root: Path) -> list[str]:
    skill_package_root = f"skills/{source_root.name}"
    copied: list[str] = []
    copied.extend(_copy_tree_files_to_relative_root(source_root, "agents", staged_root, skill_package_root))
    copied.extend(_copy_tree_files_to_relative_root(source_root, "assets", staged_root, skill_package_root))
    copied.extend(_copy_tree_files_to_relative_root(source_root, "references", staged_root, skill_package_root))

    skill_source = source_root / "SKILL.md"
    if skill_source.exists():
        _reject_tessl_staging_symlink(source_root, skill_source)
        skill_target = staged_root / skill_package_root / "SKILL.md"
        skill_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_source, skill_target)
        copied.append(f"{skill_package_root}/SKILL.md")
    return copied


def _stable_tessl_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stable_tessl_live_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stable_tessl_local_install_workspace(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-local-install" / f"{safe_name}-{digest}"


def _tessl_archive_suffix() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _unique_archive_dir(archive_root: Path, label: str) -> Path:
    archive_root.mkdir(parents=True, exist_ok=True)
    safe_label = _safe_slug(label)
    archive_dir = archive_root / f"{_tessl_archive_suffix()}-{safe_label}"
    while archive_dir.exists():
        archive_dir = archive_root / f"{_tessl_archive_suffix()}-{safe_label}"
    return archive_dir


def _sanitize_tessl_archive_ingestable_dirs(archive_root: Path) -> None:
    if not archive_root.exists():
        return
    for child in sorted((path for path in archive_root.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True):
        if child.name not in {"evals", "scenarios"}:
            continue
        target = child.with_name(f"archived-{child.name}")
        suffix = 1
        while target.exists():
            target = child.with_name(f"archived-{child.name}-{suffix}")
            suffix += 1
        shutil.move(str(child), target)


def _archive_stage_children(stage_root: Path, label: str) -> Path | None:
    if not stage_root.exists():
        return None
    archive_root = stage_root.parent / f"{stage_root.name}-evidence-archive"
    legacy_archive_root = stage_root / "evidence-archive"
    if legacy_archive_root.exists():
        legacy_archive_dir = _unique_archive_dir(archive_root, "legacy-evidence-archive")
        legacy_archive_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy_archive_root), legacy_archive_dir)
    _sanitize_tessl_archive_ingestable_dirs(archive_root)
    children = list(stage_root.iterdir())
    if not children:
        return None
    archive_dir = _unique_archive_dir(archive_root, label)
    archive_dir.mkdir()
    for child in children:
        archived_name = f"archived-{child.name}" if child.name in {"evals", "scenarios"} else child.name
        shutil.move(str(child), archive_dir / archived_name)
    _sanitize_tessl_archive_ingestable_dirs(archive_root)
    return archive_dir


def _archive_stage_directory(stage_dir: Path, label: str) -> Path | None:
    if not stage_dir.exists() or not any(stage_dir.iterdir()):
        return None
    archive_dir = _unique_archive_dir(stage_dir.parent / "evidence-archive", label)
    shutil.move(str(stage_dir), archive_dir)
    return archive_dir


def _json_or_text(text_value: str) -> object:
    try:
        return json.loads(text_value)
    except json.JSONDecodeError:
        return text_value


def _tessl_json_status(process: subprocess.CompletedProcess[str]) -> str | None:
    parsed = _json_or_text(process.stdout.strip()) if process.stdout.strip() else None
    if isinstance(parsed, dict):
        status = parsed.get("status") or parsed.get("outcome")
        if isinstance(status, str):
            return status.lower()
    return None


def _tessl_process_succeeded(process: subprocess.CompletedProcess[str]) -> bool:
    if process.returncode != 0:
        return False
    return _tessl_json_status(process) != "error"


def _tessl_auth_blocked(*texts: str) -> bool:
    combined = "\n".join(texts).lower()
    return "authenticate with tessl" in combined


def _run_tessl_project_command(
    tessl_path: str,
    args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [tessl_path, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=TESSL_PROJECT_LINK_TIMEOUT_SECONDS,
        env=env,
    )


def _signal_name_for_returncode(returncode: int) -> str | None:
    if returncode >= 0:
        return None
    signal_number = abs(returncode)
    try:
        return signal.Signals(signal_number).name
    except ValueError:
        return f"signal {signal_number}"


def _tessl_signal_blocker(process: subprocess.CompletedProcess[str], *, lane: str) -> str | None:
    signal_name = _signal_name_for_returncode(process.returncode)
    if not signal_name:
        return None
    return (
        f"Tessl {lane} command was terminated by {signal_name} "
        f"(return code {process.returncode}) before completing. This is a local "
        "native CLI, sandbox, or OS runtime blocker, not a skill assessment result."
    )


def _tessl_project_link_matches(stdout: str, *, workspace: str, project: str) -> bool:
    parsed = _json_or_text(stdout.strip()) if stdout.strip() else None
    if not isinstance(parsed, dict):
        return False

    def values_for(key: str, obj: object) -> set[str]:
        values: set[str] = set()
        if isinstance(obj, dict):
            for item_key, item_value in obj.items():
                if item_key in {key, f"{key}Name", f"{key}_name"} and isinstance(item_value, str):
                    values.add(item_value)
                values.update(values_for(key, item_value))
        elif isinstance(obj, list):
            for item in obj:
                values.update(values_for(key, item))
        return values

    workspace_values = values_for("workspace", parsed)
    project_values = values_for("project", parsed)
    name_values = values_for("name", parsed)
    return (
        workspace in workspace_values
        and (project in project_values or f"{workspace}/{project}" in name_values)
    )


def _tessl_eval_list_count(stdout: str) -> int | None:
    parsed = _parse_json_value_from_text(stdout) if stdout.strip() else None
    if isinstance(parsed, list):
        return len(parsed)
    if not isinstance(parsed, dict):
        return None
    if parsed.get("status") == "error" or parsed.get("ok") is False:
        return None
    for key in ("evals", "runs", "items", "nodes", "data", "results"):
        value = parsed.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            nested = _tessl_eval_list_count(json.dumps(value))
            if nested is not None:
                return nested
    return None


def _tessl_eval_list_runs(stdout: str) -> list[dict[str, object]] | None:
    parsed = _parse_json_value_from_text(stdout) if stdout.strip() else None
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if not isinstance(parsed, dict):
        return None
    if parsed.get("status") == "error" or parsed.get("ok") is False:
        return None
    for key in ("evals", "runs", "items", "nodes", "data", "results"):
        value = parsed.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _tessl_eval_list_runs(json.dumps(value))
            if nested is not None:
                return nested
    return None


def _tessl_run_field(run: dict[str, object], *keys: str) -> object:
    for key in keys:
        value = run.get(key)
        if value is not None:
            return value
    attributes = run.get("attributes")
    if isinstance(attributes, dict):
        for key in keys:
            value = attributes.get(key)
            if value is not None:
                return value
    return None


def _tessl_run_metadata_field(run: dict[str, object], key: str) -> object:
    metadata = run.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    attributes = run.get("attributes")
    if isinstance(attributes, dict):
        metadata = attributes.get("metadata")
        if isinstance(metadata, dict):
            return metadata.get(key)
    return None


def _tessl_pending_run_ids_for_project(stdout: str, *, project: str) -> list[str] | None:
    runs = _tessl_eval_list_runs(stdout)
    if runs is None:
        return None
    pending_ids: list[str] = []
    for run in runs:
        run_status = _tessl_run_field(run, "status")
        if not isinstance(run_status, str) or run_status.strip().lower() != "pending":
            continue
        tile_name = _tessl_run_metadata_field(run, "tileName")
        subject = _tessl_run_field(run, "subject")
        if not any(isinstance(value, str) and value.rsplit("/", 1)[-1] == project for value in (tile_name, subject)):
            continue
        run_id = _tessl_run_field(run, "id", "evalRunId", "runId")
        if isinstance(run_id, str) and run_id.strip():
            pending_ids.append(run_id.strip())
    return pending_ids


def _tessl_pending_run_preflight(
    tessl_path: str,
    workspace: str,
    project: str,
    staged_root: Path,
    env: dict[str, str],
) -> dict[str, object]:
    command_text = _tessl_eval_list_command_text(tessl_path, workspace)
    try:
        process, command_text = _run_tessl_eval_list_for_workspace(tessl_path, workspace, staged_root, env)
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl pending-run preflight timed out before live scoring; refusing to submit another run.",
            "command": command_text,
            "raw_output": _as_text(exc.stdout),
            "raw_error": _as_text(exc.stderr),
        }
    except OSError as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": f"Failed to run Tessl pending-run preflight; refusing to submit another run: {exc}",
            "command": command_text,
            "raw_output": "",
            "raw_error": str(exc),
        }

    if blocker := _tessl_signal_blocker(process, lane="eval list pending-run preflight"):
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": blocker,
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if _tessl_auth_blocked(process.stdout, process.stderr):
        return {
            "status": "blocked",
            "blocker_class": "blocked_auth",
            "blocker": "Tessl authentication is required before pending-run preflight can protect live eval credits.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if process.returncode != 0:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl pending-run preflight could not fetch run history; refusing to submit another live eval run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }

    pending_ids = _tessl_pending_run_ids_for_project(process.stdout, project=project)
    if pending_ids is None:
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": "Tessl pending-run preflight could not parse run history; refusing to submit another live eval run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if pending_ids:
        return {
            "status": "blocked",
            "blocker_class": "blocked_environment",
            "blocker": "A pending Tessl eval run already exists for this workspace/project; inspect that run instead of spending another.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "pending_eval_run_ids": pending_ids,
        }
    return {
        "status": "pass",
        "blocker": None,
        "blocker_class": None,
        "command": command_text,
        "exit_code": process.returncode,
        "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
        "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        "pending_eval_run_ids": [],
    }


def _tessl_run_budget_preflight(
    tessl_path: str,
    workspace: str,
    staged_root: Path,
    env: dict[str, str],
) -> dict[str, object]:
    try:
        process, command_text = _run_tessl_eval_list_for_workspace(tessl_path, workspace, staged_root, env)
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": "Tessl workspace run-budget preflight timed out before live scoring.",
            "command": _tessl_eval_list_command_text(tessl_path, workspace),
            "raw_output": _as_text(exc.stdout),
            "raw_error": _as_text(exc.stderr),
        }
    except OSError as exc:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": f"Failed to run Tessl workspace run-budget preflight: {exc}",
            "command": _tessl_eval_list_command_text(tessl_path, workspace),
            "raw_output": "",
            "raw_error": str(exc),
        }

    if blocker := _tessl_signal_blocker(process, lane="eval list run-budget preflight"):
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": blocker,
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if _tessl_auth_blocked(process.stdout, process.stderr):
        return {
            "status": "blocked",
            "blocker_class": "blocked_auth",
            "blocker": "Tessl CLI is installed locally, but authentication is required before run-budget preflight can run.",
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        }
    if process.returncode != 0:
        return {
            "status": "blocked",
            "blocker_class": "blocked_runtime",
            "blocker": (
                "Tessl workspace run-budget preflight could not fetch run history; "
                "blocking live scoring because remaining workspace capacity could not "
                "be checked."
            ),
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "capacity_source": "unavailable_eval_list",
        }

    used_runs = _tessl_eval_list_count(process.stdout)
    if used_runs is None:
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": (
                "Tessl workspace run-budget preflight could not determine remaining "
                "capacity; blocking live scoring because workspace reserve could not "
                "be enforced."
            ),
            "command": command_text,
            "exit_code": process.returncode,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
            "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
            "capacity_source": "unparseable_eval_list",
        }

    remaining_runs = max(TESSL_WORKSPACE_RUN_LIMIT - used_runs, 0)
    status = "pass" if remaining_runs > TESSL_WORKSPACE_RUN_RESERVE else "blocked"
    blocker = None
    blocker_class = None
    if status == "blocked":
        blocker = (
            f"Tessl workspace {workspace} has {remaining_runs} of "
            f"{TESSL_WORKSPACE_RUN_LIMIT} runs remaining, which is at or below the "
            f"{TESSL_WORKSPACE_RUN_RESERVE}-run reserve. Use dry-run/local evidence "
            "before spending another live eval run."
        )
        blocker_class = "blocked_environment"
    return {
        "status": status,
        "blocker": blocker,
        "blocker_class": blocker_class,
        "command": command_text,
        "exit_code": process.returncode,
        "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
        "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
        "workspace_run_limit": TESSL_WORKSPACE_RUN_LIMIT,
        "reserve_runs": TESSL_WORKSPACE_RUN_RESERVE,
        "used_runs": used_runs,
        "remaining_runs": remaining_runs,
    }


def _tessl_eval_list_command(tessl_path: str, workspace: str) -> list[str]:
    return [tessl_path, "eval", "list", "--json", "--workspace", workspace]


def _tessl_eval_list_command_text(tessl_path: str, workspace: str) -> str:
    return " ".join(shlex.quote(_portable_command_part(str(part))) for part in _tessl_eval_list_command(tessl_path, workspace))


def _run_tessl_eval_list_for_workspace(
    tessl_path: str,
    workspace: str,
    staged_root: Path,
    env: dict[str, str],
) -> tuple[subprocess.CompletedProcess[str], str]:
    command = _tessl_eval_list_command(tessl_path, workspace)
    process = subprocess.run(
        command,
        cwd=str(staged_root),
        capture_output=True,
        text=True,
        timeout=TESSL_PROJECT_LINK_TIMEOUT_SECONDS,
        env=env,
    )
    return process, " ".join(shlex.quote(str(part)) for part in command)


def _tessl_live_private_eval_run_command(
    tessl_path: str,
    workspace: str,
    staged_source: Path,
) -> list[str]:
    return [
        tessl_path,
        "eval",
        "run",
        "--json",
        "--workspace",
        workspace,
        str(staged_source),
    ]


def _ensure_tessl_project_link(
    tessl_path: str,
    staged_root: Path,
    identity: dict[str, str | None],
) -> dict[str, object]:
    workspace = identity.get("workspace")
    project = identity.get("project")
    common = {
        "identity": identity,
        "staged_source": str(staged_root),
        "checked": True,
    }
    if not workspace or not project:
        return {
            **common,
            "status": "skipped",
            "action": "workspace_not_provided",
            "blocker": None,
            "blocker_class": None,
            "commands": [],
        }

    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    commands: list[dict[str, object]] = []

    def record(action: str, process: subprocess.CompletedProcess[str]) -> None:
        process_args = getattr(process, "args", [])
        if not isinstance(process_args, (list, tuple)):
            process_args = []
        signal_name = _signal_name_for_returncode(process.returncode)
        commands.append({
            "action": action,
            "command": " ".join(shlex.quote(_portable_command_part(str(part))) for part in process_args),
            "exit_code": process.returncode,
            "signal": signal_name,
            "raw_output": _sanitize_tessl_live_private_payload(process.stdout),
            "raw_error": _sanitize_tessl_live_private_payload(process.stderr),
            "parsed_output": (
                _sanitize_tessl_live_private_payload(_json_or_text(process.stdout.strip()))
                if process.stdout.strip()
                else None
            ),
        })

    try:
        check = _run_tessl_project_command(tessl_path, ["project", "repair", "--json", "--yes"], staged_root, tessl_env)
        record("check", check)
        if blocker := _tessl_signal_blocker(check, lane="project repair check"):
            return {
                **common,
                "status": "blocked",
                "action": "check",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(check.stdout, check.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "check",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project link checks can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if check.returncode == 0 and _tessl_project_link_matches(check.stdout, workspace=workspace, project=project):
            return {
                **common,
                "status": "pass",
                "action": "already_linked",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }

        relink = _run_tessl_project_command(
            tessl_path,
            ["project", "repair", "--relink", "--workspace", workspace, "--project", project, "--yes", "--json"],
            staged_root,
            tessl_env,
        )
        record("relink", relink)
        if blocker := _tessl_signal_blocker(relink, lane="project relink"):
            return {
                **common,
                "status": "blocked",
                "action": "relink",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(relink.stdout, relink.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "relink",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project relink can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if _tessl_process_succeeded(relink):
            update_source = _run_tessl_project_command(
                tessl_path,
                ["project", "repair", "--update-source", "--yes", "--json"],
                staged_root,
                tessl_env,
            )
            record("update_source", update_source)
            if blocker := _tessl_signal_blocker(update_source, lane="project source repair"):
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": blocker,
                    "blocker_class": "blocked_runtime",
                    "commands": commands,
                }
            if _tessl_auth_blocked(update_source.stdout, update_source.stderr):
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": "Tessl CLI is installed locally, but authentication is required before project source repair can run.",
                    "blocker_class": "blocked_auth",
                    "commands": commands,
                }
            if update_source.returncode != 0:
                return {
                    **common,
                    "status": "blocked",
                    "action": "update_source",
                    "blocker": (
                        f"Relinked Tessl project {workspace}/{project}, but failed to update "
                        "the recorded source for the temp-staged eval directory."
                    ),
                    "blocker_class": "blocked_validation",
                    "commands": commands,
                }
            return {
                **common,
                "status": "pass",
                "action": "relinked_existing_project_updated_source",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }

        create = _run_tessl_project_command(
            tessl_path,
            ["project", "create", "--new", "--workspace", workspace, project],
            staged_root,
            tessl_env,
        )
        record("create", create)
        if blocker := _tessl_signal_blocker(create, lane="project create"):
            return {
                **common,
                "status": "blocked",
                "action": "create",
                "blocker": blocker,
                "blocker_class": "blocked_runtime",
                "commands": commands,
            }
        if _tessl_auth_blocked(create.stdout, create.stderr):
            return {
                **common,
                "status": "blocked",
                "action": "create",
                "blocker": "Tessl CLI is installed locally, but authentication is required before project create can run.",
                "blocker_class": "blocked_auth",
                "commands": commands,
            }
        if _tessl_process_succeeded(create):
            return {
                **common,
                "status": "pass",
                "action": "created_project",
                "blocker": None,
                "blocker_class": None,
                "commands": commands,
            }
        return {
            **common,
            "status": "blocked",
            "action": "create",
            "blocker": (
                f"Unable to relink or create Tessl project {workspace}/{project} "
                "for the temp-staged eval directory."
            ),
            "blocker_class": "blocked_validation",
            "commands": commands,
        }
    except subprocess.TimeoutExpired as e:
        return {
            **common,
            "status": "blocked",
            "action": "project_link",
            "blocker": f"Tessl project link check timed out after {TESSL_PROJECT_LINK_TIMEOUT_SECONDS} seconds.",
            "blocker_class": "blocked_runtime",
            "commands": commands,
            "raw_output": _as_text(e.stdout),
            "raw_error": _as_text(e.stderr),
        }
    except OSError as e:
        return {
            **common,
            "status": "blocked",
            "action": "project_link",
            "blocker": f"Failed to run Tessl project link check: {e}",
            "blocker_class": "blocked_runtime",
            "commands": commands,
        }


def _stage_tessl_eval_source(
    repo_root: Path,
    path: str,
    temp_root: Path | None = None,
    workspace: str | None = None,
) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl eval source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    _archive_stage_children(staged_root, "local-eval")

    copied: list[str] = []
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
    copied.extend(_copy_tree_files_if_present(source_root, "references/evals", staged_root))
    copied.extend(_copy_tree_files_if_present(source_root, "assets", staged_root))
    copied.extend(_write_tessl_scenarios_from_evals(source_root, staged_root))
    copied.extend(_write_tessl_project_marker(source_root, staged_root, workspace))

    if not copied:
        raise FileNotFoundError(f"No Tessl eval staging files found under: {path}")
    return staged_root, copied


def _stage_tessl_live_private_source(
    repo_root: Path,
    path: str,
    workspace: str,
    temp_root: Path | None = None,
) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl live eval source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl live eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_live_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    _archive_stage_children(staged_root, "live-private")

    copied: list[str] = []
    copied.extend(_write_tessl_live_plugin_manifest(source_root, staged_root, workspace))
    copied.extend(_write_tessl_registry_readme(source_root, staged_root, workspace))
    copied.extend(_write_tesslignore(staged_root))
    copied.extend(_copy_tessl_live_skill_package(source_root, staged_root))
    copied.extend(_write_tessl_live_evals_from_references(source_root, staged_root))
    _validate_tessl_projection_shape(
        staged_root,
        skill_name=source_root.name,
        workspace=workspace,
        project_slug=_tessl_project_slug(source_root),
        require_evals=True,
    )

    if f"skills/{source_root.name}/SKILL.md" not in copied:
        raise FileNotFoundError(f"No SKILL.md found under Tessl live eval source: {path}")
    return staged_root, copied


def _tessl_live_staged_case_ids(staged_source: Path) -> list[str]:
    """Return the exact scenario ids that would be submitted to Tessl live."""
    case_ids: set[str] = set()
    for dirname in ("evals", "scenarios"):
        root = staged_source / dirname
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if (child / "task.md").is_file() and (child / "criteria.json").is_file():
                case_ids.add(child.name)
    return sorted(case_ids)


def _case_ids_with_pass_status(payload: object) -> set[str]:
    """Collect case ids that carry direct pass evidence in SDK OSS receipts."""
    passed: set[str] = set()
    if isinstance(payload, dict):
        case_id = payload.get("case_id")
        status = payload.get("status")
        latest = payload.get("latest_evidence")
        latest_status = latest.get("status") if isinstance(latest, dict) else None
        if isinstance(case_id, str) and (status == "pass" or latest_status == "pass"):
            passed.add(case_id)
        for value in payload.values():
            passed.update(_case_ids_with_pass_status(value))
    elif isinstance(payload, list):
        for item in payload:
            passed.update(_case_ids_with_pass_status(item))
    return passed


def _tessl_live_readiness_lanes(repo_root: Path, source_path: str) -> dict[str, dict[str, object]]:
    readiness_path = default_handoff_readiness_path(repo_root, repo_root / source_path)
    readiness = _load_json_file(readiness_path)
    lanes = readiness.get("lanes")
    if not isinstance(lanes, list):
        return {}
    lane_map: dict[str, dict[str, object]] = {}
    for lane in lanes:
        if isinstance(lane, dict) and isinstance(lane.get("id"), str):
            lane_map[str(lane["id"])] = lane
    return lane_map


def _resolve_tessl_live_evidence_path(repo_root: Path, raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _oss_pass_case_ids_for_live(repo_root: Path, receipt_path: Path | None, seen: set[Path] | None = None) -> set[str]:
    if receipt_path is None:
        return set()
    resolved = receipt_path.resolve()
    if seen is None:
        seen = set()
    if resolved in seen:
        return set()
    seen.add(resolved)

    payload = _load_json_file(receipt_path)
    passed = _case_ids_with_pass_status(payload)
    source_receipt = payload.get("source_receipt") if isinstance(payload, dict) else None
    source_path = _resolve_tessl_live_evidence_path(repo_root, source_receipt)
    if source_path is not None and source_path.is_file():
        passed.update(_oss_pass_case_ids_for_live(repo_root, source_path, seen))
    return passed


def _tessl_live_oss_scenario_parity(
    repo_root: Path,
    source_path: str,
    staged_source: Path,
) -> dict[str, object]:
    """Block Tessl live when staged cases outrun OSS local/cloud pass evidence."""
    staged_case_ids = _tessl_live_staged_case_ids(staged_source)
    lanes = _tessl_live_readiness_lanes(repo_root, source_path)
    lane_case_ids: dict[str, list[str]] = {}
    missing_by_lane: dict[str, list[str]] = {}
    extra_by_lane: dict[str, list[str]] = {}
    lane_receipts: dict[str, dict[str, object]] = {}
    staged_case_set = set(staged_case_ids)
    for lane_id in ("oss-local", "oss-cloud"):
        lane = lanes.get(lane_id) or {}
        receipt_path = _resolve_tessl_live_evidence_path(repo_root, lane.get("receipt_path"))
        receipt_found = receipt_path is not None and receipt_path.is_file()
        passed = _oss_pass_case_ids_for_live(repo_root, receipt_path)
        lane_receipts[lane_id] = {
            "receipt_path": str(receipt_path.relative_to(repo_root)) if receipt_path and receipt_path.is_relative_to(repo_root) else str(receipt_path) if receipt_path else None,
            "receipt_found": receipt_found,
        }
        lane_case_ids[lane_id] = sorted(passed)
        missing_by_lane[lane_id] = sorted(staged_case_set - passed)
        extra_by_lane[lane_id] = sorted(passed - staged_case_set)

    unproven = sorted(set().union(*(set(items) for items in missing_by_lane.values())))
    extra = sorted(set().union(*(set(items) for items in extra_by_lane.values())))
    ok = bool(staged_case_ids) and not unproven and not extra
    return {
        "schema_version": "skills-sdk.tessl-live-oss-scenario-parity.v1",
        "status": "pass" if ok else "blocked",
        "staged_case_count": len(staged_case_ids),
        "staged_case_ids": staged_case_ids,
        "oss_local_pass_count": len(lane_case_ids.get("oss-local", [])),
        "oss_cloud_pass_count": len(lane_case_ids.get("oss-cloud", [])),
        "missing_by_lane": missing_by_lane,
        "extra_by_lane": extra_by_lane,
        "lane_receipts": lane_receipts,
        "unproven_case_count": len(unproven),
        "unproven_case_ids": unproven,
        "extra_case_count": len(extra),
        "extra_case_ids": extra,
        "rule": (
            "The Tessl live scenario set must exactly match both oss-local and "
            "oss-cloud pass evidence for the current live candidate."
        ),
    }


def _tessl_live_budget_preflight(staged_source: Path) -> dict[str, object]:
    """Return the paid-live Tessl scenario/cost-shape gate for staged input."""
    staged_case_ids = _tessl_live_staged_case_ids(staged_source)
    generated_case_ids = sorted(case_id for case_id in staged_case_ids if case_id.startswith("generated-eval."))
    scenario_count = len(staged_case_ids)
    expected_solution_runs = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT
    expected_score_runs = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT
    expected_model_tasks = scenario_count * TESSL_LIVE_PRIVATE_VARIANT_COUNT * TESSL_LIVE_PRIVATE_MODEL_TASKS_PER_VARIANT
    blockers: list[str] = []
    if scenario_count > TESSL_LIVE_PRIVATE_MAX_SCENARIOS:
        blockers.append(
            f"scenario_count {scenario_count} exceeds the default {TESSL_LIVE_PRIVATE_MAX_SCENARIOS}-case Tessl live cost cap"
        )
    if generated_case_ids:
        blockers.append("generated-eval.* scenarios require an explicit budgeted live lane before upload")

    return {
        "schema_version": "skills-sdk.tessl-live-budget-preflight.v1",
        "status": "pass" if not blockers else "blocked",
        "blocker_class": None if not blockers else "blocked_validation",
        "blockers": blockers,
        "scenario_count": scenario_count,
        "min_scenarios_required": TESSL_LIVE_PRIVATE_MIN_SCENARIOS,
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "staged_case_ids": staged_case_ids,
        "generated_case_count": len(generated_case_ids),
        "generated_case_ids": generated_case_ids,
        "expected_variants": ["baseline", "usage-spec"],
        "expected_variant_count": TESSL_LIVE_PRIVATE_VARIANT_COUNT,
        "expected_solution_runs": expected_solution_runs,
        "expected_score_runs": expected_score_runs,
        "expected_model_tasks": expected_model_tasks,
        "rule": (
            "Tessl live is capped to the 20-case OSS-proven confirmation set by default; "
            "use smaller internal canaries before live and require an explicit budgeted "
            "lane for larger or generated scenario uploads."
        ),
    }


def _stable_tessl_scenario_generation_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-scenario-generation" / f"{safe_name}-{digest}"


def _tessl_local_proof_policy(workspace: str | None = None) -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.tessl-local-proof-policy.v1",
        "workspace": workspace,
        "stage": "Tessl Distribution -> Local Runtime Truth bridge",
        "proves": [
            "controlled Tessl plugin package shape",
            "local Tessl plugin lint compatibility",
            "temporary plugin archive packability",
            "file: install command compatibility inside a temporary project workspace",
            "optional Tessl review threshold command result when explicitly requested",
        ],
        "does_not_prove": [
            "live Tessl eval score",
            "public registry publication",
            "persistent user runtime activation",
            "oss-local or oss-cloud behavioral proof",
        ],
        "no_publish": True,
        "no_registry_upload": True,
        "no_live_repo_source": True,
        "install_scope": "temporary project workspace under /tmp/ask-tessl-local-install",
    }


def _tessl_local_command_payload(
    command: list[str],
    process: subprocess.CompletedProcess[str],
    *,
    cwd: Path,
) -> dict[str, object]:
    def redact(value: str) -> str:
        return re.sub(r"[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}", "<redacted-email>", value)

    return {
        "status": "success" if process.returncode == 0 else "error",
        "command": " ".join(shlex.quote(_portable_command_part(part)) for part in command),
        "cwd": str(cwd),
        "exit_code": process.returncode,
        "stdout": redact(process.stdout),
        "stderr": redact(process.stderr),
    }


def _portable_command_part(part: str) -> str:
    if Path(part).is_absolute():
        return Path(part).name
    return part


def _sanitize_tessl_live_private_payload(value: object) -> object:
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key, item in value.items():
            if key in {"createdBy", "user", "userId", "firstName", "lastName"}:
                sanitized[key] = "<redacted-actor>"
            elif key in {"command", "cliInvocation", "cwd", "path", "staged_source"}:
                sanitized[key] = _sanitize_tessl_live_private_payload(item)
            else:
                sanitized[key] = _sanitize_tessl_live_private_payload(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_tessl_live_private_payload(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, (dict, list)):
                return json.dumps(_sanitize_tessl_live_private_payload(parsed), indent=2, sort_keys=True)
        redacted = re.sub(r"/Users/[^\s\"']+", "<user-path>", value)
        redacted = re.sub(r"[-A-Za-z0-9._%+]+@[-A-Za-z0-9.]+\.[A-Za-z]{2,}", "<redacted-email>", redacted)
        return redacted
    return value


def _run_tessl_local_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: int,
) -> dict[str, object]:
    try:
        process = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "status": "blocked",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
            "timeout_seconds": timeout_seconds,
            "stdout": _as_text(e.stdout),
            "stderr": _as_text(e.stderr),
            "blocker": f"Tessl local proof command timed out after {timeout_seconds} seconds.",
            "blocker_class": "blocked_runtime",
        }
    except OSError as e:
        return {
            "status": "blocked",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
            "stdout": "",
            "stderr": str(e),
            "blocker": f"Failed to run Tessl local proof command: {e}",
            "blocker_class": "blocked_runtime",
        }

    payload = _tessl_local_command_payload(command, process, cwd=cwd)
    if signal_blocker := _tessl_signal_blocker(process, lane="local proof"):
        payload["status"] = "blocked"
        payload["blocker"] = signal_blocker
        payload["blocker_class"] = "blocked_runtime"
    elif process.returncode != 0 and _tessl_auth_blocked(process.stdout, process.stderr):
        payload["status"] = "blocked"
        payload["blocker"] = "Tessl CLI is installed locally, but authentication is required before this local proof can run."
        payload["blocker_class"] = "blocked_auth"
    return payload


def run_tessl_local_proof(
    repo_root: Path,
    path: str,
    *,
    workspace: str,
    execute: bool = False,
    include_review: bool = False,
    review_threshold: int = TESSL_LOCAL_REVIEW_MIN_SCORE,
    timeout_seconds: int = 180,
) -> dict[str, object]:
    """Stage a Tessl package and optionally run local lint, pack, file install, and review checks."""
    source_path = Path(path)
    proof_path = str(source_path.parent) if source_path.name == "SKILL.md" else path
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, proof_path, normalized_workspace)
    except (OSError, ValueError) as e:
        return {
            "schema_version": "skills-sdk.tessl-local-proof.v1",
            "status": "blocked",
            "source_path": path,
            "proof_path": proof_path,
            "workspace": workspace,
            "execute": execute,
            "blocker": f"Failed to stage Tessl local proof source: {e}",
            "blocker_class": "blocked_validation" if isinstance(e, ValueError) else "blocked_runtime",
            "policy": _tessl_local_proof_policy(workspace),
        }

    tessl_path = shutil.which("tessl") or "tessl"
    safe_name = proof_path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(proof_path.encode("utf-8")).hexdigest()[:12]
    install_workspace = Path(tempfile.gettempdir()) / "ask-tessl-local-install" / f"{safe_name}-{digest}"
    source_root_name = (repo_root.resolve() / proof_path).resolve().name
    dist_dir = staged_source / "dist"
    dist_path = dist_dir / f"{source_root_name}.tgz"
    review_path = staged_source / "skills" / source_root_name
    lint_command = [tessl_path, "plugin", "lint", str(staged_source)]
    pack_command = [tessl_path, "plugin", "pack", "--output", str(dist_path), str(staged_source)]
    install_command = [tessl_path, "install", f"file:{staged_source}", "--agent", "codex", "--yes", "--strict"]
    review_command = [
        tessl_path,
        "review",
        "run",
        str(review_path),
        "--workspace",
        normalized_workspace,
        "--json",
        "--threshold",
        str(review_threshold),
    ]
    planned_commands = {
        "plugin_lint": " ".join(shlex.quote(part) for part in lint_command),
        "plugin_pack": " ".join(shlex.quote(part) for part in pack_command),
        "install_file": " ".join(shlex.quote(part) for part in install_command),
        "review_run": " ".join(shlex.quote(part) for part in review_command),
    }
    receipt: dict[str, object] = {
        "schema_version": "skills-sdk.tessl-local-proof.v1",
        "status": "preview" if not execute else "pass",
        "source_path": path,
        "proof_path": proof_path,
        "workspace": normalized_workspace,
        "execute": execute,
        "include_review": include_review,
        "review_threshold": review_threshold,
        "staged_source": str(staged_source),
        "staged_files": copied_files,
        "staged_file_count": len(copied_files),
        "install_workspace": str(install_workspace),
        "dist_dir": str(dist_dir),
        "dist_path": str(dist_path),
        "planned_commands": planned_commands,
        "commands": {},
        "policy": _tessl_local_proof_policy(normalized_workspace),
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
    }
    if not execute:
        return receipt

    if not shutil.which("tessl"):
        receipt["status"] = "blocked"
        receipt["blocker"] = "Installed native tessl CLI was not found on PATH."
        receipt["blocker_class"] = "blocked_runtime"
        return receipt

    _clear_directory(install_workspace)
    dist_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    commands: dict[str, object] = {}
    for key, command, cwd in (
        ("plugin_lint", lint_command, staged_source),
        ("plugin_pack", pack_command, staged_source),
        ("install_file", install_command, install_workspace),
    ):
        payload = _run_tessl_local_command(command, cwd=cwd, env=env, timeout_seconds=timeout_seconds)
        commands[key] = payload
        if payload.get("status") != "success":
            receipt["status"] = "blocked" if payload.get("status") == "blocked" else "fail"
            receipt["blocker"] = payload.get("blocker") or f"Tessl local proof step failed: {key}"
            receipt["blocker_class"] = payload.get("blocker_class") or "failed_validation"
            receipt["commands"] = commands
            return receipt

    if include_review:
        payload = _run_tessl_local_command(review_command, cwd=staged_source, env=env, timeout_seconds=timeout_seconds)
        commands["review_run"] = payload
        if payload.get("status") != "success":
            receipt["status"] = "blocked" if payload.get("status") == "blocked" else "fail"
            receipt["blocker"] = payload.get("blocker") or "Tessl review run did not meet the requested threshold."
            receipt["blocker_class"] = payload.get("blocker_class") or "failed_validation"
            receipt["commands"] = commands
            return receipt

    receipt["commands"] = commands
    receipt["installed_project_manifest"] = str(install_workspace / "tessl.json")
    return receipt


def _clear_directory(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for child in target.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _stage_tessl_scenario_target_tile(
    repo_root: Path,
    path: str,
    workspace: str,
    target_tile: Path,
) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl scenario source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl scenario source is not a directory: {path}")

    _archive_stage_directory(target_tile, "target-tile")
    _clear_directory(target_tile)

    copied: list[str] = []
    copied.extend(_write_tessl_live_plugin_manifest(source_root, target_tile, workspace))
    copied.extend(_write_tessl_registry_readme(source_root, target_tile, workspace))
    copied.extend(_write_tesslignore(target_tile))
    copied.extend(_copy_tessl_live_skill_package(source_root, target_tile))
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, target_tile))
    copied.extend(_copy_tree_files_if_present(source_root, "assets", target_tile))
    copied.extend(_copy_tessl_live_reference_support_files(source_root, target_tile, set(copied)))
    _validate_tessl_projection_shape(
        target_tile,
        skill_name=source_root.name,
        workspace=workspace,
        project_slug=_tessl_project_slug(source_root),
        require_evals=False,
    )

    if f"skills/{source_root.name}/SKILL.md" not in copied:
        raise FileNotFoundError(f"No SKILL.md found under Tessl scenario source: {path}")
    return target_tile, copied


def _write_tessl_scenario_tool_project(tool_project: Path) -> list[str]:
    _archive_stage_directory(tool_project, "tool-project")
    _clear_directory(tool_project)
    manifest = {
        "name": "tessl-scenario-tools",
        "mode": "managed",
        "dependencies": {},
    }
    manifest_path = tool_project / "tessl.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return ["tessl.json"]


def _write_tessl_scenario_generation_brief(
    staged_root: Path,
    *,
    source_path: str,
    workspace: str,
    target_tile: Path,
    tool_project: Path,
) -> Path:
    brief_path = staged_root / "scenario-generation-brief.md"
    scenario_skill, scenario_reference = _tessl_scenario_tool_paths(tool_project)
    brief_path.write_text(
        "\n".join([
            "# Tessl Scenario Generation Brief",
            "",
            f"Source skill: {source_path}",
            f"Workspace: {workspace}",
            f"Target staged tile: {target_tile}",
            f"Tessl scenario skill: {scenario_skill}",
            f"Tessl scenario workflow reference: {scenario_reference}",
            "",
            "## Agent Procedure",
            "",
            "1. Read the Tessl scenario skill and workflow reference above.",
            "2. Treat the staged target tile as disposable input; do not edit the live repo source.",
            "3. Generate scenarios into target-tile/evals/ using the Tessl scenario skill format.",
            "4. Make scenarios bespoke to this skill's behavioral contract, evidence assets, and failure modes.",
            "5. Review the generated scenarios for instruction leakage, feasibility, baseline lift, and criteria totals.",
            "6. Import only reviewed, useful cases back into canonical skill assets: references/evals.yaml for the skill-owned case index and references/evals/*.md for generated fixture evidence.",
            "7. Run the repo eval wrapper after import. The --tessl-live-private lane stages only canonical skill assets and fails if generated scenarios are missing unless the package is explicitly structure-only.",
            "8. Do not publish or upload packages from this lane.",
            "",
            "## Hard Boundaries",
            "",
            "- Do not run Tessl install from the repository root.",
            "- Do not run tessl publish, tessl tile publish, tessl skill publish, or package upload commands.",
            "- Do not copy generated scenarios into canonical sources until they have been reviewed.",
            "- Do not run live Tessl scoring from unreviewed target-tile/evals output.",
            "- Preserve this staging directory as evidence for the scenario-generation pass.",
            "",
        ])
        + "\n",
        encoding="utf-8",
    )
    return brief_path


def _tessl_scenario_tool_paths(tool_project: Path) -> tuple[Path, Path]:
    """Return scenario-tool paths for both current and legacy Tessl install layouts."""
    relative_suffix = Path("tessl-labs/tessl-skill-eval-scenarios/creating-eval-scenarios")
    roots = [
        tool_project / ".tessl/plugins",
        tool_project / ".tessl/tiles",
    ]
    candidates = [root / relative_suffix for root in roots]
    scenario_root = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    return (
        scenario_root / "SKILL.md",
        scenario_root / "references/scenario-generation.md",
    )


def prepare_tessl_scenario_generation(
    repo_root: Path,
    path: str,
    *,
    workspace: str | None,
    dry_run: bool = False,
) -> CallResult:
    """Prepare a temp Tessl scenario-generation workspace for a skill."""
    policy = _tessl_scenario_generation_policy(workspace)
    tool_spec = f"{TESSL_SCENARIO_TOOL_TILE}@{TESSL_SCENARIO_TOOL_VERSION}"
    command_display = f"tessl install {tool_spec} --agent codex --yes"
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_root = _stable_tessl_scenario_generation_parent(path)
        staged_root.mkdir(parents=True, exist_ok=True)
        target_tile = staged_root / "target-tile"
        tool_project = staged_root / "tool-project"
        target_tile, target_files = _stage_tessl_scenario_target_tile(
            repo_root,
            path,
            normalized_workspace,
            target_tile,
        )
        tool_files = _write_tessl_scenario_tool_project(tool_project)
    except (OSError, ValueError) as e:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "raw_output": "",
                "raw_error": str(e),
                "blocker": f"Failed to prepare Tessl scenario-generation staging: {e}",
                "blocker_class": "blocked_validation",
                "policy": policy,
            },
            errors=[ErrorObject(code="ERR_VALIDATION", message=str(e))],
        )

    common = {
        "source_path": path,
        "staged_root": str(staged_root),
        "target_tile": str(target_tile),
        "tool_project": str(tool_project),
        "target_plugin_manifest": str(target_tile / ".tessl-plugin" / "plugin.json"),
        "target_tessl_project_marker": str(target_tile / "tessl.json"),
        "target_staged_files": target_files,
        "tool_project_files": tool_files,
        "workspace": normalized_workspace,
        "project_identity": _tessl_project_identity((repo_root / path).resolve(), normalized_workspace),
        "dry_run": dry_run,
        "scenario_tool_tile": TESSL_SCENARIO_TOOL_TILE,
        "scenario_tool_version": TESSL_SCENARIO_TOOL_VERSION,
        "staging_policy": "stable_tmp_scenario_generation_evidence",
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-scenario-generation for inspection",
        "policy": _tessl_scenario_generation_policy(normalized_workspace),
    }

    if dry_run:
        brief_path = _write_tessl_scenario_generation_brief(
            staged_root,
            source_path=path,
            workspace=normalized_workspace,
            target_tile=target_tile,
            tool_project=tool_project,
        )
        return CallResult(
            status="success",
            data={
                "status": "pass",
                **common,
                "command": command_display,
                "scenario_generation_brief": str(brief_path),
                "raw_output": "",
                "raw_error": "",
                "exit_code": 0,
                "blocker": None,
                "blocker_class": None,
            },
        )

    tessl_path = shutil.which("tessl")
    if not tessl_path:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                **common,
                "command": command_display,
                "raw_output": "",
                "raw_error": "",
                "blocker": "Installed native tessl CLI was not found on PATH.",
                "blocker_class": "blocked_runtime",
            },
            errors=[ErrorObject(code="ERR_RUNTIME", message="Installed native tessl CLI was not found on PATH.")],
        )

    project_link = _ensure_tessl_project_link(
        tessl_path,
        target_tile,
        common["project_identity"],
    )
    common["project_link"] = project_link
    if project_link.get("status") == "blocked":
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                **common,
                "command": command_display,
                "raw_output": "",
                "raw_error": "",
                "blocker": project_link.get("blocker"),
                "blocker_class": project_link.get("blocker_class"),
            },
            errors=[ErrorObject(
                code="ERR_RUNTIME" if project_link.get("blocker_class") == "blocked_runtime" else "ERR_VALIDATION",
                message=str(project_link.get("blocker") or "Tessl project link check failed."),
            )],
        )

    cmd = [tessl_path, "install", tool_spec, "--agent", "codex", "--yes"]
    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    try:
        process = subprocess.run(
            cmd,
            cwd=str(tool_project),
            capture_output=True,
            text=True,
            timeout=600,
            env=tessl_env,
        )
    except subprocess.TimeoutExpired as e:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                **common,
                "command": command_display,
                "raw_output": _as_text(e.stdout),
                "raw_error": _as_text(e.stderr),
                "blocker": "Tessl scenario tool install timed out after 600 seconds.",
                "blocker_class": "blocked_runtime",
            },
            errors=[ErrorObject(code="ERR_RUNTIME", message="Tessl scenario tool install timed out after 600 seconds.")],
        )
    except OSError as e:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                **common,
                "command": command_display,
                "raw_output": "",
                "raw_error": str(e),
                "blocker": f"Failed to run Tessl scenario tool install: {e}",
                "blocker_class": "blocked_runtime",
            },
            errors=[ErrorObject(code="ERR_RUNTIME", message=f"Failed to run Tessl scenario tool install: {e}")],
        )

    raw_output = process.stdout
    raw_error = process.stderr
    combined = f"{raw_output}\n{raw_error}".lower()
    if process.returncode != 0 and "authenticate with tessl" in combined:
        status = "blocked"
        blocker = "Tessl CLI is installed locally, but authentication is required before scenario tool install can run."
        blocker_class = "blocked_auth"
    else:
        status = "pass" if process.returncode == 0 else "fail"
        blocker = None
        blocker_class = None

    scenario_skill, scenario_reference = _tessl_scenario_tool_paths(tool_project)
    brief_path = _write_tessl_scenario_generation_brief(
        staged_root,
        source_path=path,
        workspace=normalized_workspace,
        target_tile=target_tile,
        tool_project=tool_project,
    )
    data = {
        "status": status,
        **common,
        "command": command_display,
        "exit_code": process.returncode,
        "raw_output": raw_output,
        "raw_error": raw_error,
        "blocker": blocker,
        "blocker_class": blocker_class,
        "scenario_skill": str(scenario_skill) if scenario_skill.exists() else None,
        "scenario_reference": str(scenario_reference) if scenario_reference.exists() else None,
        "scenario_generation_brief": str(brief_path),
        "generated_output": str(target_tile / "evals"),
        "prepared_only": True,
    }
    if status == "pass":
        return CallResult(status="success", data=data)
    return CallResult(
        status="error",
        data=data,
        errors=[ErrorObject(code="ERR_RUNTIME" if blocker_class == "blocked_runtime" else "ERR_VALIDATION", message=blocker or "Tessl scenario tool install failed.")],
    )


def _tessl_eval_result_common(
    *,
    command: str,
    source_path: str,
    staged_source: Path,
    copied_files: list[str],
    workspace: str,
    project_identity: dict[str, str | None],
    dry_run: bool,
) -> dict:
    plugin_version = None
    try:
        manifest = json.loads((staged_source / ".tessl-plugin" / "plugin.json").read_text(encoding="utf-8"))
        raw_version = manifest.get("version") if isinstance(manifest, dict) else None
        if isinstance(raw_version, str):
            plugin_version = raw_version
    except (OSError, json.JSONDecodeError):
        plugin_version = None
    return {
        "command": command,
        "source_path": source_path,
        "staged_source": str(staged_source),
        "plugin_manifest": str(staged_source / ".tessl-plugin" / "plugin.json"),
        "plugin_version": plugin_version,
        "tessl_project_marker": str(staged_source / "tessl.json") if (staged_source / "tessl.json").exists() else None,
        "staged_files": copied_files,
        "staging_policy": "stable_tmp_private_plugin_evidence",
        "workspace": workspace,
        "project_identity": project_identity,
        "visibility": "private",
        "dry_run": dry_run,
        "live_private": True,
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
        "policy": _tessl_live_private_policy(workspace),
    }


def _run_tessl_live_private_eval(
    repo_root: Path,
    path: str,
    *,
    workspace: str | None,
    dry_run: bool = False,
) -> dict:
    """Run or preview the opt-in private Tessl plugin eval lane."""
    command_display = "tessl eval run --json --workspace <workspace> <staged-plugin-dir>"
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, path, normalized_workspace)
        command_display = f"tessl eval run --json --workspace {normalized_workspace} {staged_source}"
    except (OSError, ValueError) as e:
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to stage private Tessl plugin eval source: {e}",
            "blocker_class": "blocked_validation",
            "policy": _tessl_live_private_policy(workspace),
            "live_private": True,
            "dry_run": dry_run,
        }

    common = _tessl_eval_result_common(
        command=command_display,
        source_path=path,
        staged_source=staged_source,
        copied_files=copied_files,
        workspace=normalized_workspace,
        project_identity=_tessl_project_identity((repo_root / path).resolve(), normalized_workspace),
        dry_run=dry_run,
    )
    parity = _tessl_live_oss_scenario_parity(repo_root, path, staged_source)
    budget_preflight = _tessl_live_budget_preflight(staged_source)
    common["oss_scenario_parity"] = parity
    common["budget_preflight"] = budget_preflight
    if parity.get("status") != "pass":
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": (
                "Tessl live scenario set includes scenarios without both oss-local "
                "and oss-cloud pass evidence."
            ),
            "blocker_class": "blocked_validation",
        }
    if budget_preflight.get("status") != "pass":
        blockers = budget_preflight.get("blockers")
        blocker_text = "; ".join(str(item) for item in blockers) if isinstance(blockers, list) else None
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": blocker_text or "Tessl live budget preflight blocked the staged scenario set.",
            "blocker_class": budget_preflight.get("blocker_class") or "blocked_validation",
        }
    if dry_run:
        return {
            "status": "pass",
            **common,
            "raw_output": "",
            "raw_error": "",
            "exit_code": 0,
            "blocker": None,
            "blocker_class": None,
        }

    tessl_path = shutil.which("tessl")
    if not tessl_path:
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": "Installed native tessl CLI was not found on PATH.",
            "blocker_class": "blocked_runtime",
        }

    project_link = _ensure_tessl_project_link(
        tessl_path,
        staged_source,
        common["project_identity"],
    )
    common["project_link"] = project_link
    if project_link.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": "",
            "blocker": project_link.get("blocker"),
            "blocker_class": project_link.get("blocker_class"),
        }

    tessl_env = dict(os.environ)
    tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
    project_name = str(common["project_identity"].get("project") or _tessl_live_tile_slug(repo_root / path))
    pending_run_preflight = _tessl_pending_run_preflight(
        tessl_path,
        normalized_workspace,
        project_name,
        staged_source,
        tessl_env,
    )
    common["pending_run_preflight"] = pending_run_preflight
    if pending_run_preflight.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": str(pending_run_preflight.get("raw_output") or ""),
            "raw_error": str(pending_run_preflight.get("raw_error") or ""),
            "blocker": pending_run_preflight.get("blocker"),
            "blocker_class": pending_run_preflight.get("blocker_class"),
        }
    run_budget_preflight = _tessl_run_budget_preflight(
        tessl_path,
        normalized_workspace,
        staged_source,
        tessl_env,
    )
    common["run_budget_preflight"] = run_budget_preflight
    if run_budget_preflight.get("status") == "blocked":
        return {
            "status": "blocked",
            **common,
            "raw_output": str(run_budget_preflight.get("raw_output") or ""),
            "raw_error": str(run_budget_preflight.get("raw_error") or ""),
            "blocker": run_budget_preflight.get("blocker"),
            "blocker_class": run_budget_preflight.get("blocker_class"),
        }

    cmd = _tessl_live_private_eval_run_command(tessl_path, normalized_workspace, staged_source)
    try:
        process = subprocess.run(
            cmd,
            cwd=str(staged_source),
            capture_output=True,
            text=True,
            timeout=600,
            env=tessl_env,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "status": "blocked",
            **common,
            "raw_output": _as_text(e.stdout),
            "raw_error": _as_text(e.stderr),
            "blocker": "Tessl private plugin eval timed out after 600 seconds.",
            "blocker_class": "blocked_runtime",
        }
    except OSError as e:
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to run Tessl private plugin eval: {e}",
            "blocker_class": "blocked_runtime",
        }

    raw_output = process.stdout
    raw_error = process.stderr
    auth_text = f"{raw_output}\n{raw_error}".lower()
    if process.returncode != 0 and "authenticate with tessl" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI is installed locally, but authentication is required before private plugin evals can run."
        blocker_class = "blocked_auth"
    elif process.returncode != 0 and "no existing project safely matches this directory" in auth_text:
        status = "blocked"
        blocker = (
            "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the "
            "temp-staged private plugin eval directory. Run tessl project create/link/repair for a live project lane."
        )
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "no tessl project found" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI could not find a tessl.json project marker in the staged private plugin eval directory."
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "project that was not found or is not accessible" in auth_text:
        status = "blocked"
        blocker = (
            f"Tessl project {normalized_workspace}/{_tessl_live_tile_slug(repo_root / path)} "
            f"was not found or is not accessible. Create, link, or repair that project "
            f"in workspace {normalized_workspace} before running live evals."
        )
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "points at a different repository or directory path" in auth_text:
        status = "blocked"
        blocker = (
            "Tessl project binding points at a different source directory than the "
            "temp-staged private eval directory."
        )
        blocker_class = "blocked_validation"
    else:
        status = "pass" if process.returncode == 0 else "fail"
        blocker = None
        blocker_class = None

    eval_run_id = _extract_tessl_eval_run_id(raw_output)
    submission_evidence_path = _write_tessl_live_submission_evidence(
        repo_root,
        path,
        run_id=eval_run_id,
        workspace=normalized_workspace,
        staged_source=staged_source,
        project_identity=common["project_identity"],
    )
    live_result_summary = None
    view_raw_output = ""
    view_raw_error = ""
    view_evidence_path = None
    view_attempts = 0
    view_status = None
    if status == "pass":
        if not eval_run_id:
            status = "blocked"
            blocker = "Tessl private plugin eval completed but did not return an eval run id for score/baseline verification."
            blocker_class = "blocked_validation"
        else:
            view_cmd = [tessl_path, "eval", "view", "--json", eval_run_id]
            try:
                deadline = time.monotonic() + TESSL_LIVE_PRIVATE_VIEW_TIMEOUT_SECONDS
                view_payload = None
                while True:
                    view_attempts += 1
                    view_process = subprocess.run(
                        view_cmd,
                        cwd=str(staged_source),
                        capture_output=True,
                        text=True,
                        timeout=600,
                        env=tessl_env,
                    )
                    view_raw_output = view_process.stdout
                    view_raw_error = view_process.stderr
                    if view_process.returncode != 0:
                        break
                    view_payload = _parse_json_object_from_text(view_raw_output)
                    if view_payload is None:
                        break
                    view_status = _tessl_eval_view_status(view_payload)
                    if _tessl_eval_view_has_complete_scores(view_payload):
                        break
                    if view_status in {"failed", "error", "cancelled", "canceled"}:
                        break
                    if time.monotonic() >= deadline:
                        break
                    time.sleep(TESSL_LIVE_PRIVATE_VIEW_POLL_SECONDS)
            except subprocess.TimeoutExpired as e:
                status = "blocked"
                blocker = "Tessl private plugin eval view timed out while waiting for scored results."
                blocker_class = "blocked_runtime"
                view_raw_output = _as_text(e.stdout)
                view_raw_error = _as_text(e.stderr)
            except OSError as e:
                status = "blocked"
                blocker = f"Failed to inspect Tessl private plugin eval results: {e}"
                blocker_class = "blocked_runtime"
                view_raw_error = str(e)
            else:
                if view_process.returncode != 0:
                    status = "blocked"
                    blocker = "Tessl private plugin eval completed but result inspection failed."
                    blocker_class = "blocked_validation"
                else:
                    try:
                        if view_payload is None:
                            raise ValueError("No JSON object found in Tessl eval view output.")
                        if not _tessl_eval_view_has_complete_scores(view_payload):
                            failure_reason = _tessl_eval_view_failure_reason(view_payload)
                            if failure_reason:
                                failure_code, failure_message = failure_reason
                                if failure_code == "EVAL_QUOTA_EXCEEDED":
                                    blocker_class = "blocked_environment"
                                else:
                                    blocker_class = "blocked_validation"
                                raise ValueError(
                                    f"Tessl eval run failed before scoring: {failure_code}: {failure_message}"
                                )
                            if time.monotonic() >= deadline:
                                raise ValueError("Tessl eval view did not reach complete scored results before timeout.")
                            raise ValueError(f"Tessl eval view is not scored yet (status={view_status or 'unknown'}).")
                        live_result_summary = _summarize_tessl_live_eval_view(view_payload)
                    except ValueError as e:
                        status = "blocked"
                        blocker = f"Failed to parse Tessl private plugin eval score summary: {e}"
                        blocker_class = blocker_class or "blocked_validation"
                    else:
                        if not live_result_summary["meets_min_score"] or not live_result_summary["beats_baseline"]:
                            status = "fail"
                            score_pct = round(float(live_result_summary["score"]) * 100, 2)
                            baseline_pct = round(float(live_result_summary["baseline_score"]) * 100, 2)
                            blocker = (
                                "Tessl private plugin eval completed but failed readiness: "
                                f"score {score_pct}% vs baseline {baseline_pct}%."
                            )
                            blocker_class = None

    view_evidence_path = _write_tessl_live_view_evidence(repo_root, path, eval_run_id, view_raw_output)

    return {
        "status": status,
        **common,
        "exit_code": process.returncode,
        "eval_run_id": eval_run_id,
        "submission_evidence_path": submission_evidence_path,
        "live_result_summary": live_result_summary,
        "view_attempts": view_attempts,
        "view_status": view_status,
        "view_evidence_path": view_evidence_path,
        "view_raw_output": _sanitize_tessl_live_private_payload(view_raw_output),
        "view_raw_error": _sanitize_tessl_live_private_payload(view_raw_error),
        "raw_output": _sanitize_tessl_live_private_payload(raw_output),
        "raw_error": _sanitize_tessl_live_private_payload(raw_error),
        "blocker": blocker,
        "blocker_class": blocker_class,
    }


def _run_tessl_eval(
    repo_root: Path,
    path: str,
    *,
    allow_project_save: bool = False,
    workspace: str | None = None,
) -> dict:
    """Run the local Tessl eval lane without any registry publish/upload command."""
    _ = allow_project_save  # Compatibility flag retained; temp-staged local runs are default-safe.
    tessl_path = shutil.which("tessl")
    command_display = "tessl eval run --json <staged-temp-source>"
    if not tessl_path:
        return {
            "status": "blocked",
            "command": command_display,
            "blocker": "Installed native tessl CLI was not found on PATH.",
            "blocker_class": "blocked_runtime",
            "policy": _tessl_policy(),
        }

    try:
        normalized_workspace = _validate_tessl_workspace(workspace) if workspace else None
        staged_source, copied_files = _stage_tessl_eval_source(repo_root, path, workspace=normalized_workspace)
        project_identity = _tessl_project_identity((repo_root / path).resolve(), normalized_workspace)
        project_link = _ensure_tessl_project_link(tessl_path, staged_source, project_identity)
        if project_link.get("status") == "blocked":
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "staging_policy": "stable_tmp_evidence",
                "tessl_project_marker": str(staged_source / "tessl.json"),
                "project_identity": project_identity,
                "project_link": project_link,
                "workspace": normalized_workspace,
                "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
                "raw_output": "",
                "raw_error": "",
                "blocker": project_link.get("blocker"),
                "blocker_class": project_link.get("blocker_class"),
                "policy": _tessl_policy(),
            }
        command_display = f"tessl eval run --json {staged_source}"
        cmd = [tessl_path, "eval", "run", "--json", str(staged_source)]
        tessl_env = dict(os.environ)
        tessl_env["TESSL_AUTO_UPDATE_INTERVAL_MINUTES"] = "0"
        try:
            process = subprocess.run(
                cmd,
                cwd=str(staged_source),
                capture_output=True,
                text=True,
                timeout=600,
                env=tessl_env,
            )
        except subprocess.TimeoutExpired as e:
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "staging_policy": "stable_tmp_evidence",
                "tessl_project_marker": str(staged_source / "tessl.json"),
                "project_identity": project_identity,
                "project_link": project_link,
                "workspace": normalized_workspace,
                "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
                "raw_output": _as_text(e.stdout),
                "raw_error": _as_text(e.stderr),
                "blocker": "Tessl eval timed out after 600 seconds.",
                "blocker_class": "blocked_runtime",
                "policy": _tessl_policy(),
            }
        except OSError as e:
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "staging_policy": "stable_tmp_evidence",
                "tessl_project_marker": str(staged_source / "tessl.json"),
                "project_identity": project_identity,
                "project_link": project_link,
                "workspace": normalized_workspace,
                "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
                "raw_output": "",
                "raw_error": str(e),
                "blocker": f"Failed to run Tessl eval: {e}",
                "blocker_class": "blocked_runtime",
                "policy": _tessl_policy(),
            }

        raw_output = process.stdout
        raw_error = process.stderr
        auth_text = f"{raw_output}\n{raw_error}".lower()
        if signal_blocker := _tessl_signal_blocker(process, lane="eval"):
            status = "blocked"
            blocker = signal_blocker
            blocker_class = "blocked_runtime"
        elif process.returncode != 0 and "authenticate with tessl" in auth_text:
            status = "blocked"
            blocker = "Tessl CLI is installed locally, but authentication is required before evals can run."
            blocker_class = "blocked_auth"
        elif process.returncode != 0 and "no existing project safely matches this directory" in auth_text:
            status = "blocked"
            blocker = (
                "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the "
                "temp-staged eval directory. Create or link a Tessl project/workspace before rerunning."
            )
            blocker_class = "blocked_validation"
        elif process.returncode != 0 and "no tessl project found" in auth_text:
            status = "blocked"
            blocker = "Tessl CLI could not find a tessl.json project marker in the staged eval directory."
            blocker_class = "blocked_validation"
        else:
            status = "pass" if process.returncode == 0 else "fail"
            blocker = None
            blocker_class = None

        return {
            "status": status,
            "command": command_display,
            "source_path": path,
            "staged_source": str(staged_source),
            "staged_files": copied_files,
            "staging_policy": "stable_tmp_evidence",
            "tessl_project_marker": str(staged_source / "tessl.json"),
            "project_identity": project_identity,
            "project_link": project_link,
            "workspace": normalized_workspace,
            "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-evals for inspection",
            "exit_code": process.returncode,
            "raw_output": raw_output,
            "raw_error": raw_error,
            "blocker": blocker,
            "blocker_class": blocker_class,
            "policy": _tessl_policy(),
        }
    except (OSError, ValueError) as e:
        blocker_class = "blocked_validation" if isinstance(e, FileNotFoundError) else "blocked_runtime"
        if isinstance(e, ValueError):
            blocker_class = "blocked_validation"
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to stage Tessl eval source: {e}",
            "blocker_class": blocker_class,
            "policy": _tessl_policy(),
        }


def _repo_relative_text(repo_root: Path, text: str) -> str:
    if not text:
        return text
    root = str(repo_root.resolve())
    return text.replace(root + "/", "").replace(root, ".")


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _evals_run_validation_command(
    path: str,
    *,
    mode: str,
    runner: str,
    dashboard: bool,
    codex_profile: str | None = None,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
    timeout_seconds: int | None = None,
) -> str:
    parts = ["./bin/ask", "evals", "run", path, "--mode", mode, "--runner", runner]
    if codex_profile:
        parts.extend(["--profile", codex_profile])
    if tessl_live_private:
        parts.append("--tessl-live-private")
    if tessl_workspace:
        parts.extend(["--tessl-workspace", tessl_workspace])
    if tessl_live_dry_run:
        parts.append("--tessl-live-dry-run")
    if timeout_seconds is not None:
        parts.extend(["--timeout-seconds", str(timeout_seconds)])
    if not dashboard:
        parts.append("--no-dashboard")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _evals_validation_command(action: str) -> str:
    return " ".join(shlex.quote(part) for part in ["./bin/ask", "evals", action, "--json", "--robot"])


def _macro_eval_validation_command(output_dir: str | None = None, summaries_glob: str | None = None) -> str:
    parts = ["./bin/ask", "evals", "macro-report"]
    if output_dir:
        parts.extend(["--output-dir", output_dir])
    if summaries_glob:
        parts.extend(["--summaries-glob", summaries_glob])
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _load_json_file(path: Path) -> dict:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _macro_case_type(case: dict) -> str:
    category = case.get("category")
    if isinstance(category, str) and category.strip():
        return category.strip()
    case_id = str(case.get("id") or "unknown")
    return re.split(r"[-_:]", case_id, maxsplit=1)[0] or "unknown"


def _macro_run_outcome(summary: dict, case: dict) -> str:
    decision = str(summary.get("decision") or "").strip().lower()
    if decision == "blocked":
        return "blocked"
    if case.get("blocked") is True:
        return "blocked"
    blockers = case.get("blocker_classes")
    if isinstance(blockers, list) and blockers:
        return "blocked"
    if case.get("passed") is True:
        return "passed"
    if case.get("passed") is False:
        return "failed"
    if decision in {"pass", "passed"}:
        return "passed"
    return "failed" if decision == "fail" else "unknown"


def _first_string(values: object) -> str | None:
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _macro_eval_finding(summary: dict, case: dict) -> str:
    for key in ("blocker_classes", "tier1_failures", "tier2_findings", "warnings"):
        finding = _first_string(case.get(key))
        if finding:
            return finding
    runners = case.get("runners")
    if isinstance(runners, dict):
        for runner_name in sorted(runners):
            runner = runners.get(runner_name)
            if not isinstance(runner, dict):
                continue
            for key in ("blocker_classes", "tier1_failures", "tier2_findings", "warnings"):
                finding = _first_string(runner.get(key))
                if finding:
                    return f"[{runner_name}] {finding}"
    claim_to_evidence = summary.get("claim_to_evidence")
    if isinstance(claim_to_evidence, dict):
        blocking_gaps = claim_to_evidence.get("blocking_gaps")
        if isinstance(blocking_gaps, list) and blocking_gaps:
            first_gap = blocking_gaps[0]
            if isinstance(first_gap, dict):
                return str(first_gap.get("type") or first_gap.get("claim_id") or "claim_to_evidence_gap")
            return str(first_gap)
    return "none"


def _macro_behavior_pattern(case_type: str, run_outcome: str, eval_finding: str) -> str:
    finding_slug = _safe_slug(eval_finding.lower())[:80] if eval_finding != "none" else "none"
    return f"{_safe_slug(case_type.lower())}:{run_outcome}:{finding_slug}"


def _macro_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _macro_runner_metric_keys(case: dict) -> set[str]:
    metric_keys: set[str] = set()
    runners = case.get("runners")
    if not isinstance(runners, dict):
        return metric_keys
    for runner in runners.values():
        if not isinstance(runner, dict):
            continue
        metrics = runner.get("metrics")
        if not isinstance(metrics, dict):
            continue
        metric_keys.update(str(key) for key in metrics.keys())
    return metric_keys


def _macro_verifier_types(case: dict) -> list[str]:
    verifier_types: set[str] = set(_macro_string_list(case.get("evidence_surfaces")))
    metric_keys = _macro_runner_metric_keys(case)
    if "trace" in metric_keys:
        verifier_types.add("trace_metrics")
    if "expected_signals" in metric_keys or case.get("expected_signals") is True:
        verifier_types.add("expected_signals")
    if "rubric" in metric_keys:
        verifier_types.add("rubric")
    if _macro_string_list(case.get("hard_gates")):
        verifier_types.add("hard_gates")
    if _macro_string_list(case.get("expected_evidence")):
        verifier_types.add("expected_evidence")
    if case.get("check_evidence") is True:
        verifier_types.add("executed_check_evidence")
    return sorted(verifier_types)


def _macro_verification_strategy(case: dict) -> str:
    verifier_types = set(_macro_verifier_types(case))
    if "executed_check_evidence" in verifier_types:
        return "executed_deterministic"
    if verifier_types & {"deterministic_checks", "expected_signals", "output_schema", "hard_gates"}:
        return "declared_not_executed"
    if case.get("passed") is not None:
        return "acceptance_only"
    return "unknown"


def _macro_baseline_status(case: dict) -> str:
    baseline_type = str(case.get("baseline_type") or "").strip()
    baseline_id = str(case.get("baseline_id") or "").strip()
    if not baseline_type and not baseline_id:
        return "none_declared"
    comparisons = case.get("baseline_comparisons")
    if isinstance(comparisons, dict) and comparisons:
        statuses = {
            str(comparison.get("status") or "")
            for comparison in comparisons.values()
            if isinstance(comparison, dict)
        }
        if "compared" in statuses:
            return "executed_compared"
        if statuses:
            return "declared_unexecuted"
    if case.get("comparison_review_artifact") or case.get("comparison_inputs") or case.get("neutral_baseline_approval"):
        return "declared_with_review_surface"
    return "declared_unverified"


def _macro_summary_paths(repo_root: Path, summaries_glob: str) -> list[Path]:
    return sorted(path for path in repo_root.glob(summaries_glob) if path.is_file())


def _macro_eval_events_from_summary(repo_root: Path, summary_path: Path) -> list[dict]:
    summary = _load_json_file(summary_path)
    cases = summary.get("cases")
    if not isinstance(cases, list):
        return []
    release_manifest_path = summary_path.with_name("release_manifest.json")
    release_manifest = _load_json_file(release_manifest_path) if release_manifest_path.is_file() else {}
    events: list[dict] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            continue
        case_type = _macro_case_type(case)
        run_outcome = _macro_run_outcome(summary, case)
        eval_finding = _macro_eval_finding(summary, case)
        behavior_pattern = _macro_behavior_pattern(case_type, run_outcome, eval_finding)
        verifier_types = _macro_verifier_types(case)
        event = {
            "schema_version": "1.0",
            "source": "ask_evals_macro_report",
            "skill": summary.get("skill") or (summary.get("skill_release") or {}).get("name"),
            "run_id": summary.get("run_id"),
            "generated_at": summary.get("generated_at"),
            "eval_mode": summary.get("eval_mode"),
            "runner_mode": summary.get("runner_mode"),
            "summary_decision": summary.get("decision"),
            "case_id": case.get("id") or f"case-{index}",
            "case_name": case.get("name"),
            "case_type": case_type,
            "run_outcome": run_outcome,
            "eval_finding": eval_finding,
            "behavior_pattern": behavior_pattern,
            "tier1_failed": bool(case.get("tier1_failed")),
            "tier2_failed": bool(case.get("tier2_failed")),
            "blocked": run_outcome == "blocked",
            "baseline_type": case.get("baseline_type"),
            "baseline_id": case.get("baseline_id"),
            "baseline_status": _macro_baseline_status(case),
            "skill_lift": case.get("skill_lift"),
            "is_beneficial": case.get("is_beneficial"),
            "baseline_regression": case.get("baseline_regression"),
            "readiness_state": case.get("readiness_state"),
            "metric_availability": case.get("metric_availability"),
            "check_evidence": bool(case.get("check_evidence")),
            "verification_strategy": _macro_verification_strategy(case),
            "verifier_types": verifier_types,
            "summary_path": _repo_relative_path(repo_root, summary_path),
            "release_manifest_path": _repo_relative_path(repo_root, release_manifest_path) if release_manifest else None,
        }
        events.append(event)
    return events


def _macro_group_counts(events: list[dict], fields: tuple[str, ...]) -> list[dict]:
    counts: dict[tuple[str, ...], int] = {}
    for event in events:
        key = tuple(str(event.get(field) or "unknown") for field in fields)
        counts[key] = counts.get(key, 0) + 1
    rows = [
        {**{field: key[index] for index, field in enumerate(fields)}, "trace_count": count}
        for key, count in counts.items()
    ]
    return sorted(rows, key=lambda row: (-int(row["trace_count"]), tuple(str(row[field]) for field in fields)))


def _macro_group_list_counts(events: list[dict], field: str) -> list[dict]:
    counts: dict[str, int] = {}
    for event in events:
        values = event.get(field)
        if not isinstance(values, list) or not values:
            values = ["none"]
        for value in values:
            key = str(value or "unknown")
            counts[key] = counts.get(key, 0) + 1
    return sorted(
        [{field[:-1] if field.endswith("s") else field: key, "trace_count": count} for key, count in counts.items()],
        key=lambda row: (-int(row["trace_count"]), tuple(str(value) for value in row.values())),
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _write_macro_mdx_report(path: Path, report: dict) -> None:
    report_json = json.dumps(report, indent=2, sort_keys=True)
    lines = [
        "---",
        "title: Skill Macro Eval Report",
        "schema_version: skill-macro-eval-report.mdx.v1",
        f"generated_at: {report['generated_at']}",
        "---",
        "",
        "import {",
        "  MacroEvalArtifacts,",
        "  MacroEvalFlowTable,",
        "  MacroEvalLeaderboard,",
        "  MacroEvalTotals,",
        "} from \"./components/eval-report\";",
        "",
        f"export const macroReport = {report_json};",
        "",
        "# Skill Macro Eval Report",
        "",
        "This deterministic report converts saved skill eval summaries into compact macro-eval events for population-level review.",
        "",
        "## Totals",
        "",
        "<MacroEvalTotals totals={macroReport.totals} />",
        "",
        "## Artifacts",
        "",
        "<MacroEvalArtifacts artifacts={macroReport.artifacts} />",
        "",
        "## Top Behavior Patterns",
        "",
        "<MacroEvalLeaderboard rows={macroReport.groups.by_behavior_pattern} labelField=\"behavior_pattern\" />",
        "",
        "",
        "## Top Findings",
        "",
        "<MacroEvalLeaderboard rows={macroReport.groups.by_eval_finding} labelField=\"eval_finding\" />",
        "",
        "## Case Outcome Finding Flow",
        "",
        "<MacroEvalFlowTable rows={macroReport.groups.by_case_outcome_finding} />",
        "",
        "## Skill Pattern Concentration",
        "",
        "<MacroEvalFlowTable rows={macroReport.groups.by_skill_behavior_pattern} />",
        "",
        "## Boundary",
        "",
        "This is a deterministic evidence export and review dashboard. It does not perform semantic clustering, BERTopic-style topic discovery, or AgentTrace-style root-cause diagnosis.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _copy_macro_mdx_components(repo_root: Path, target_dir: Path) -> Path | None:
    component_source = repo_root / "Infrastructure" / "templates" / "components" / "eval-report.tsx"
    if not component_source.is_file():
        return None
    component_target = target_dir / "components" / "eval-report.tsx"
    component_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(component_source, component_target)
    return component_target


def macro_eval_report(
    repo_root: Path,
    *,
    output_dir: str | None = None,
    summaries_glob: str = DEFAULT_MACRO_EVAL_REPORTS_GLOB,
) -> CallResult:
    """Export deterministic macro-eval events from saved skill eval summaries."""
    result = CallResult()
    result.data["validation_commands"] = [_macro_eval_validation_command(output_dir, summaries_glob)]
    summary_paths = _macro_summary_paths(repo_root, summaries_glob)
    events: list[dict] = []
    for summary_path in summary_paths:
        events.extend(_macro_eval_events_from_summary(repo_root, summary_path))

    target_dir = repo_root / (output_dir or "Infrastructure/artifacts/evals/macro")
    events_path = target_dir / "macro-eval-events.jsonl"
    report_path = target_dir / "macro-eval-report.json"
    mdx_path = target_dir / "macro-eval-report.mdx"
    _write_jsonl(events_path, events)
    components_path = _copy_macro_mdx_components(repo_root, target_dir)

    report = {
        "schema_version": "1.0",
        "generated_at": _utc_now_iso(),
        "source": "ask_evals_macro_report",
        "summaries_glob": summaries_glob,
        "totals": {
            "summaries_scanned": len(summary_paths),
            "events": len(events),
            "skills": len({event.get("skill") for event in events if event.get("skill")}),
            "behavior_patterns": len({event.get("behavior_pattern") for event in events if event.get("behavior_pattern")}),
        },
        "artifacts": {
            "events_jsonl": _repo_relative_path(repo_root, events_path),
            "report_json": _repo_relative_path(repo_root, report_path),
            "report_mdx": _repo_relative_path(repo_root, mdx_path),
            "report_components": _repo_relative_path(repo_root, components_path) if components_path else None,
        },
        "groups": {
            "by_skill": _macro_group_counts(events, ("skill",)),
            "by_case_type": _macro_group_counts(events, ("case_type",)),
            "by_run_outcome": _macro_group_counts(events, ("run_outcome",)),
            "by_eval_finding": _macro_group_counts(events, ("eval_finding",)),
            "by_behavior_pattern": _macro_group_counts(events, ("behavior_pattern",)),
            "by_verification_strategy": _macro_group_counts(events, ("verification_strategy",)),
            "by_baseline_status": _macro_group_counts(events, ("baseline_status",)),
            "by_verifier_type": _macro_group_list_counts(events, "verifier_types"),
            "by_case_outcome_finding": _macro_group_counts(events, ("case_type", "run_outcome", "eval_finding")),
            "by_skill_behavior_pattern": _macro_group_counts(events, ("skill", "behavior_pattern")),
        },
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_macro_mdx_report(mdx_path, report)

    result.status = "success"
    result.data.update(report)
    return result


def _resolve_eval_skill_path(repo_root: Path, path: str) -> str:
    """Resolve generated runtime skill paths back to canonical eval sources."""
    requested = Path(path)
    parts = requested.parts
    if len(parts) >= 3 and parts[0] == ".agents" and parts[1] == "skills":
        handle = parts[2]
        source_roots = [
            repo_root / "Skills",
            repo_root / "Plugins",
            repo_root / "skills-system",
        ]
        for source_root in source_roots:
            if not source_root.is_dir():
                continue
            if source_root.name == "Plugins":
                candidates = source_root.glob(f"*/skills/**/{handle}")
            elif source_root.name == "skills-system":
                candidates = [source_root / handle]
            else:
                candidates = source_root.glob(f"*/{handle}")
            for candidate in sorted(candidates):
                if (candidate / "references" / "evals.yaml").is_file():
                    return candidate.relative_to(repo_root).as_posix()

    if (repo_root / requested / "references" / "evals.yaml").is_file():
        return path

    return path


def _eval_lifecycle_event(
    *,
    event_type: str,
    path: str,
    mode: str,
    runner: str,
    status: str,
    blocker_class: str | None = None,
) -> dict:
    return {
        "schema_version": "capability-lifecycle-event.v1",
        "event_type": event_type,
        "event_definition": EVAL_LIFECYCLE_EVENT_TYPES.get(event_type),
        "occurred_at": _utc_now_iso(),
        "subject": {
            "query": path,
            "target_kind": "skill_path",
            "handle": Path(path).name,
            "canonical_source_path": path,
            "eval_mode": mode,
            "runner": runner,
        },
        "outcome": {
            "status": status,
            "blocker_classes": [blocker_class] if blocker_class else [],
            "warning_classes": [],
        },
    }


def _start_eval_lifecycle(result: CallResult, *, path: str, mode: str, runner: str) -> None:
    started = _eval_lifecycle_event(
        event_type="eval_started",
        path=path,
        mode=mode,
        runner=runner,
        status="running",
    )
    result.data["lifecycle_events"] = [started]
    result.data["lifecycle_event"] = started
    result.data["lifecycle_event_types"] = EVAL_LIFECYCLE_EVENT_TYPES


def _finish_eval_lifecycle(
    result: CallResult,
    *,
    path: str,
    mode: str,
    runner: str,
    eval_status: str,
    blocker_class: str | None = None,
) -> None:
    final_event_type = "eval_blocked" if blocker_class else "eval_completed"
    final_event = _eval_lifecycle_event(
        event_type=final_event_type,
        path=path,
        mode=mode,
        runner=runner,
        status=eval_status,
        blocker_class=blocker_class,
    )
    result.data.setdefault("lifecycle_events", []).append(final_event)
    result.data["lifecycle_event"] = final_event


def _classify_eval_blocker(*, raw_output: str, raw_error: str, timed_out: bool = False) -> str | None:
    text = "\n".join([raw_output or "", raw_error or ""])
    low = text.lower()

    if timed_out:
        return "timeout_partial_output" if text.strip() else "timeout_no_output"

    runtime_markers = [
        "sandbox_apply: operation not permitted",
        "host_execution_untrusted",
        "sandbox-exec",
        "operation not permitted",
        "selected model is at capacity",
        "model is at capacity",
        "you've hit your usage limit",
        "you have hit your usage limit",
        "usage limit for",
        "switch to another model",
        "try again at",
        "context window",
        "start a new thread",
        "blocked_runtime",
    ]
    if any(marker in low for marker in runtime_markers):
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
        "missing authenticated codex state",
        "blocked_auth",
    ]
    if any(marker in low for marker in auth_markers):
        return "blocked_auth"

    missing_tool_markers = [
        "command not found",
        "no such file or directory",
        "missing binary",
        "missing executable",
        "blocked_missing_tool",
    ]
    if any(marker in low for marker in missing_tool_markers):
        return "blocked_missing_tool"

    missing_artifact_markers = [
        "missing artifact",
        "expected artifact",
        "scorecard not found",
        "no scorecard",
        "blocked_missing_artifact",
    ]
    if any(marker in low for marker in missing_artifact_markers):
        return "blocked_missing_artifact"

    environment_markers = [
        "wrong cwd",
        "repo mismatch",
        "workspace root",
        "permission profile",
        "blocked_environment",
    ]
    if any(marker in low for marker in environment_markers):
        return "blocked_environment"

    validation_markers = [
        "blocked_validation",
        "validation failed",
        "strict audit failed",
        "policy validation",
        "no eval cases matched the selected filters",
        "selected case filters matched only smoke-only discovery contract cases",
        "requires eval cases",
        "none matched the selected filters",
        "add discovery-specific smoke_mode cases",
    ]
    if any(marker in low for marker in validation_markers):
        return "blocked_validation"

    return None


def _scorecard_path_from_output(repo_root: Path, raw_output: str) -> Path | None:
    for line in raw_output.splitlines():
        match = re.match(r"^Scorecard:\s+(.+?)\s*$", line)
        if not match:
            continue
        candidate = Path(match.group(1)).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()
    return None


def _reports_path_from_output(repo_root: Path, raw_output: str) -> Path | None:
    for line in raw_output.splitlines():
        match = re.match(r"^Reports:\s+(.+?)\s*$", line)
        if not match:
            continue
        candidate = Path(match.group(1)).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()
    return None


def _eval_skill_source_root(path: str) -> Path:
    source = Path(path).expanduser()
    if source.name == "SKILL.md":
        return source.parent
    return source


def _eval_skill_name_for_reports(path: str) -> str:
    source_root = _eval_skill_source_root(path)
    try:
        frontmatter = _read_skill_frontmatter(source_root)
    except OSError:
        frontmatter = {}
    name = str(frontmatter.get("name") or "").strip()
    return name or source_root.name


def _newest_report_dir_for_skill(repo_root: Path, *, skill_name: str, started_at: float) -> Path | None:
    reports_root = repo_root / "Infrastructure" / "artifacts" / "skills" / skill_name
    if not reports_root.is_dir():
        return None
    candidates = [
        path
        for path in reports_root.iterdir()
        if path.is_dir() and path.stat().st_mtime >= started_at - 1
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _eval_report_dir(
    repo_root: Path,
    *,
    skill_path: str,
    raw_output: str,
    started_at: float,
) -> Path | None:
    reports_path = _reports_path_from_output(repo_root, raw_output)
    if reports_path is not None and reports_path.is_dir():
        return reports_path
    scorecard_path = _scorecard_path_from_output(repo_root, raw_output)
    if scorecard_path is not None:
        return scorecard_path.parent
    skill_name = _eval_skill_name_for_reports(skill_path)
    return _newest_report_dir_for_skill(repo_root, skill_name=skill_name, started_at=started_at)


def _eval_closeout_status(eval_status: str, blocker_class: str | None) -> str:
    if blocker_class:
        return "blocked"
    normalized = str(eval_status or "").strip().lower()
    if normalized == "pass":
        return "pass"
    if normalized.startswith("blocked") or normalized.startswith("timeout"):
        return "blocked"
    return "fail"


def _case_status_from_record(case: dict) -> str:
    if case.get("blocked") is True:
        return "blocked"
    if case.get("passed") is True:
        return "pass"
    return "fail"


def _case_closeout_from_record(case: dict) -> dict[str, object]:
    case_id = str(case.get("id") or case.get("name") or "unknown")
    status = _case_status_from_record(case)
    result = {
        "id": case_id,
        "status": status,
    }
    if case.get("dir"):
        result["result_path"] = str(case.get("dir"))
    blocker_classes = case.get("blocker_classes")
    if status == "blocked" and isinstance(blocker_classes, list) and blocker_classes:
        result["blocker_class"] = str(blocker_classes[0])
    if status != "pass":
        failures = case.get("tier1_failures")
        if isinstance(failures, list) and failures:
            result["failures"] = [str(item) for item in failures]
        blocked_reasons = case.get("blocked_reasons")
        if isinstance(blocked_reasons, list) and blocked_reasons:
            result["blocked_reasons"] = [str(item) for item in blocked_reasons]
    return result


def _case_closeout_from_partial_dir(case_dir: Path, repo_root: Path) -> dict[str, object]:
    case_id = re.sub(r"^\d+-", "", case_dir.name)
    result_path = case_dir / "result.json"
    if result_path.is_file():
        try:
            case = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            case = {}
        if isinstance(case, dict):
            return _case_closeout_from_record(case)
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
        "result_path": _repo_relative_path(repo_root, case_dir),
    }


def _load_eval_summary(report_dir: Path) -> dict:
    for name in ("summary.json", "scorecard.json"):
        path = report_dir / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            return data
    return {}


def _eval_closeout_validation_checks(closeout: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    missing = sorted(field for field in EVAL_CLOSEOUT_REQUIRED_FIELDS if field not in closeout)
    checks.append({
        "id": "required_fields_present",
        "status": "blocker" if missing else "pass",
        "message": "workflow-closeout/v1 receipts must include required contract fields.",
        "evidence": missing,
    })
    schema_version = closeout.get("schema_version")
    checks.append({
        "id": "schema_version_valid",
        "status": "pass" if schema_version == EVAL_CLOSEOUT_SCHEMA_VERSION else "blocker",
        "message": "workflow-closeout receipt must use skills-sdk.eval-closeout.v1.",
        "evidence": [] if schema_version == EVAL_CLOSEOUT_SCHEMA_VERSION else [str(schema_version)],
    })
    status = str(closeout.get("status") or "")
    cases = closeout.get("cases")
    case_list = cases if isinstance(cases, list) else []
    checks.append({
        "id": "cases_array_valid",
        "status": "pass" if isinstance(cases, list) else "blocker",
        "message": "workflow-closeout receipt must carry cases as an array.",
        "evidence": [] if isinstance(cases, list) else [type(cases).__name__],
    })
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
    non_pass_status = status != "pass"
    mutation_allowed = closeout.get("mutation_allowed")
    registry_update_allowed = closeout.get("registry_update_allowed")
    checks.append({
        "id": "non_pass_blocks_source_mutation",
        "status": "blocker" if non_pass_status and mutation_allowed is not False else "pass",
        "message": "Non-pass closeouts must set mutation_allowed=false.",
        "evidence": [f"mutation_allowed={mutation_allowed!r}"] if non_pass_status and mutation_allowed is not False else [],
    })
    checks.append({
        "id": "non_pass_blocks_registry_promotion",
        "status": "blocker" if non_pass_status and registry_update_allowed is not False else "pass",
        "message": "Non-pass closeouts must set registry_update_allowed=false.",
        "evidence": [f"registry_update_allowed={registry_update_allowed!r}"] if non_pass_status and registry_update_allowed is not False else [],
    })
    missing_suite_artifacts = closeout.get("missing_suite_artifacts") is True
    blocker_class = closeout.get("blocker_class")
    checks.append({
        "id": "missing_artifacts_have_blocker_class",
        "status": "blocker" if missing_suite_artifacts and not blocker_class else "pass",
        "message": "Closeouts with missing suite artifacts must include blocker_class.",
        "evidence": ["missing_suite_artifacts=true"] if missing_suite_artifacts and not blocker_class else [],
    })
    no_case_reason = closeout.get("no_case_reason")
    checks.append({
        "id": "pass_has_case_evidence",
        "status": "blocker" if status == "pass" and not case_list and not no_case_reason else "pass",
        "message": "Pass closeouts must include complete case evidence or an explicit no_case_reason.",
        "evidence": ["cases=[]"] if status == "pass" and not case_list and not no_case_reason else [],
    })
    return checks


def validate_eval_closeout_payload(closeout: dict[str, object]) -> dict[str, object]:
    checks = _eval_closeout_validation_checks(closeout)
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": "skills-sdk.eval-closeout-validation.v1",
        "status": "blocked" if blockers else "pass",
        "checks": checks,
        "blockers": blockers,
    }


def _load_eval_closeout(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc}"
    if not isinstance(payload, dict):
        return None, "closeout_json_not_object"
    return payload, None


def _closeout_path_for_doctor(path: Path) -> Path:
    return path / "workflow-closeout.json" if path.is_dir() else path


def eval_closeout_doctor(repo_root: Path, path: str) -> CallResult:
    result = CallResult()
    requested = Path(path).expanduser()
    if not requested.is_absolute():
        requested = repo_root / requested
    closeout_path = _closeout_path_for_doctor(requested)
    result.data["validation_commands"] = [
        " ".join(shlex.quote(part) for part in ["./bin/ask", "evals", "closeout", "doctor", path, "--json", "--robot"])
    ]
    closeout, load_error = _load_eval_closeout(closeout_path)
    report_dir = closeout_path.parent
    case_dirs = [
        item
        for item in sorted(report_dir.iterdir())
        if report_dir.is_dir() and item.is_dir() and re.match(r"^\d+-", item.name)
    ] if report_dir.is_dir() else []
    missing_result_cases = [
        re.sub(r"^\d+-", "", item.name)
        for item in case_dirs
        if not (item / "result.json").is_file()
    ]
    summary_present = (report_dir / "summary.json").is_file()
    scorecard_present = (report_dir / "scorecard.json").is_file()
    validation = (
        validate_eval_closeout_payload(closeout)
        if closeout is not None
        else {
            "schema_version": "skills-sdk.eval-closeout-validation.v1",
            "status": "blocked",
            "checks": [],
            "blockers": [{"id": "closeout_load", "status": "blocker", "message": load_error or "missing closeout", "evidence": [str(closeout_path)]}],
        }
    )
    doctor = {
        "schema_version": "skills-sdk.eval-closeout-doctor.v1",
        "status": "blocked" if validation["status"] != "pass" or missing_result_cases else "pass",
        "requested_path": path,
        "closeout_path": _repo_relative_path(repo_root, closeout_path),
        "report_dir": _repo_relative_path(repo_root, report_dir),
        "summary_present": summary_present,
        "scorecard_present": scorecard_present,
        "case_count": len(case_dirs),
        "missing_result_cases": missing_result_cases,
        "closeout_validation": validation,
        "next_reproduce_command": closeout.get("next_reproduce_command") if isinstance(closeout, dict) else None,
    }
    result.data["eval_closeout_doctor"] = doctor
    if doctor["status"] != "pass":
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Eval closeout doctor detected blocked or incomplete closeout evidence.",
            fix_suggestion=str(doctor.get("next_reproduce_command") or result.data["validation_commands"][0]),
        ))
    return result


def _write_eval_closeout(
    repo_root: Path,
    *,
    skill_path: str,
    mode: str,
    runner: str,
    raw_output: str,
    raw_error: str,
    eval_status: str,
    blocker_class: str | None,
    started_at: float,
    timeout_seconds: int | None = None,
) -> dict[str, object]:
    report_dir = _eval_report_dir(
        repo_root,
        skill_path=skill_path,
        raw_output=raw_output,
        started_at=started_at,
    )
    summary = _load_eval_summary(report_dir) if report_dir is not None else {}
    cases: list[dict[str, object]] = []
    if isinstance(summary.get("cases"), list):
        cases = [
            _case_closeout_from_record(case)
            for case in summary["cases"]
            if isinstance(case, dict)
        ]
    elif report_dir is not None and report_dir.is_dir():
        case_dirs = [
            path
            for path in sorted(report_dir.iterdir())
            if path.is_dir() and re.match(r"^\d+-", path.name)
        ]
        cases = [_case_closeout_from_partial_dir(path, repo_root) for path in case_dirs]

    closeout_blocker = blocker_class
    status = _eval_closeout_status(eval_status, blocker_class)
    missing_suite_artifacts = report_dir is None or not summary
    if missing_suite_artifacts:
        status = "blocked"
        closeout_blocker = closeout_blocker or "blocked_missing_artifact"
    if not cases:
        status = "blocked"
        closeout_blocker = closeout_blocker or "blocked_missing_artifact"
    if cases and any(case.get("status") == "blocked" for case in cases):
        status = "blocked"
        closeout_blocker = closeout_blocker or "blocked_missing_artifact"
    elif cases and status == "pass" and any(case.get("status") == "fail" for case in cases):
        status = "fail"

    closeout_path = None
    if report_dir is not None:
        closeout_path = report_dir / "workflow-closeout.json"
    elif raw_output.strip() or raw_error.strip():
        closeout_root = repo_root / "Infrastructure" / "artifacts" / "evals" / "closeouts"
        closeout_root.mkdir(parents=True, exist_ok=True)
        stamp = _utc_now_iso().replace(":", "").replace("-", "")
        closeout_path = closeout_root / f"{stamp}-{_safe_slug(skill_path)}-{_safe_slug(mode)}-{_safe_slug(runner)}.json"

    closeout: dict[str, object] = {
        "schema_version": EVAL_CLOSEOUT_SCHEMA_VERSION,
        "status": status,
        "skill_path": skill_path,
        "mode": mode,
        "runner": runner,
        "report_dir": _repo_relative_path(repo_root, report_dir) if report_dir is not None else None,
        "cases_expected": [str(case.get("id")) for case in cases],
        "cases": cases,
        "blocker_class": closeout_blocker,
        "mutation_allowed": status == "pass",
        "registry_update_allowed": status == "pass" and mode == "release",
        "raw_output_present": bool(raw_output.strip()),
        "raw_error_present": bool(raw_error.strip()),
        "missing_suite_artifacts": missing_suite_artifacts,
        "case_evidence_present": bool(cases),
        "next_reproduce_command": _evals_run_validation_command(
            skill_path,
            mode=mode,
            runner=runner,
            dashboard=True,
            tessl_live_private=False,
            tessl_workspace=None,
            tessl_live_dry_run=False,
            timeout_seconds=timeout_seconds,
        ),
    }
    if closeout_path is not None:
        closeout["closeout_validation"] = validate_eval_closeout_payload(closeout)
        closeout_path.parent.mkdir(parents=True, exist_ok=True)
        closeout["path"] = _repo_relative_path(repo_root, closeout_path)
        closeout_path.write_text(json.dumps(closeout, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        closeout["closeout_validation"] = validate_eval_closeout_payload(closeout)
    return closeout


def _write_timeout_partial_artifact(
    repo_root: Path,
    *,
    skill_path: str,
    mode: str,
    runner: str,
    raw_output: str,
    raw_error: str,
) -> str | None:
    if not (raw_output.strip() or raw_error.strip()):
        return None
    artifact_root = repo_root / "Infrastructure" / "artifacts" / "evals" / "timeouts"
    artifact_root.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now_iso().replace(":", "").replace("-", "")
    artifact_path = artifact_root / f"{stamp}-{_safe_slug(skill_path)}-{_safe_slug(mode)}-{_safe_slug(runner)}.txt"
    sanitized_output = _repo_relative_text(repo_root, raw_output)
    sanitized_error = _repo_relative_text(repo_root, raw_error)
    artifact_path.write_text(
        "timeout_classification: timeout_partial_output\n\n"
        "stdout:\n"
        f"{sanitized_output}\n\n"
        "stderr:\n"
        f"{sanitized_error}\n",
        encoding="utf-8",
    )
    return _repo_relative_path(repo_root, artifact_path)


def _read_scorecard(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _scorecard_blocker_class(scorecard: dict) -> str | None:
    decision = str(scorecard.get("decision") or "").strip().lower()
    if decision != "blocked":
        return None

    summary = scorecard.get("blocked_class_summary")
    if isinstance(summary, dict):
        for blocker_class, count in summary.items():
            if blocker_class in EVAL_BLOCKER_TAXONOMY and isinstance(count, int) and count > 0:
                return str(blocker_class)

    for case in scorecard.get("cases") or []:
        if not isinstance(case, dict):
            continue
        for blocker_class in case.get("blocker_classes") or []:
            if blocker_class in EVAL_BLOCKER_TAXONOMY:
                return str(blocker_class)
        runners = case.get("runners")
        if isinstance(runners, dict):
            for runner in runners.values():
                if not isinstance(runner, dict):
                    continue
                blocker_class = runner.get("blocker_class")
                if blocker_class in EVAL_BLOCKER_TAXONOMY:
                    return str(blocker_class)
    return "blocked_validation"


def _latest_review_report(repo_root: Path, skill_identifier: str) -> Path | None:
    review_root = repo_root / "Infrastructure" / "artifacts" / "skill-reviews"
    if not review_root.exists():
        return None
    candidates: list[Path] = []
    fallback_candidates: list[Path] = []
    skill_name = Path(skill_identifier).name
    for report_path in review_root.rglob("*.json"):
        if report_path.name.endswith("-eval-latest.json"):
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data = report.get("data") if isinstance(report, dict) else None
        if not isinstance(data, dict):
            continue
        target = str(data.get("target") or "")
        if not target:
            continue
        target_identifier = _canonical_skill_identifier(repo_root, target)
        if target_identifier == skill_identifier:
            candidates.append(report_path)
        elif Path(target_identifier).name == skill_name:
            fallback_candidates.append(report_path)
    if not candidates:
        candidates = fallback_candidates
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _write_eval_only_review_report(repo_root: Path, skill_name: str, skill_path: str) -> Path:
    review_root = repo_root / "Infrastructure" / "artifacts" / "skill-reviews"
    review_root.mkdir(parents=True, exist_ok=True)
    report_path = review_root / f"{_safe_slug(skill_name)}-eval-latest.json"
    tessl_staging_root = _tessl_staging_root_template()
    report = {
        "status": "success",
        "data": {
            "target": skill_path,
            "generated_at": _utc_now_iso(),
            "review_mode": "eval_only",
            "policy": {
                "mode": "local_internal_only",
                "primary_gate": "local_eval_ask_audit",
                "plugin_eval_min_acceptable_grade": "B+",
                "tessl_review_min_score": 90,
                "tessl_review_target_score": 95,
                "codex_smoke_profile": "[profiles.fast]",
                "tessl_eval_staging_root": tessl_staging_root,
                "tessl_project_marker": "tessl.json",
                "snyk_default": "disabled_until_requested",
                "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
            },
            "review_mode_details": {
                "local_evals": {
                    "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
                    "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates",
                    "profile": "[profiles.fast] for Codex smoke runs",
                    "tessl_evidence": f"stages copied eval inputs under {tessl_staging_root} with tessl.json",
                    "status": "run_for_this_dashboard",
                },
                "plugin_eval": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "static budget and ergonomics guardrail; not a substitute for local evals",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "tessl_lint": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "disposable .tessl-plugin/plugin.json package-shape check, not a direct content finding",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "tessl_review": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "local best-practice/content review for private or work-in-progress skills",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "snyk": {
                    "command": "./bin/ask skills external-review <path> --include-snyk --json --robot",
                    "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
                    "status": "not_run_by_default",
                },
            },
            "ask_audit": {
                "data": {
                    "openclaw": {
                        "status": "not_run",
                        "stdout": "Summary: 0 critical · 0 warn",
                    }
                }
            },
            "plugin_eval": {
                "status": "not_run",
                "stdout": (
                    "Plugin Eval was not run for this eval-only dashboard. "
                    "Run ./bin/ask skills external-review <path> --json --robot for the static budget and ergonomics lane."
                ),
            },
            "tessl_review": {
                "status": "not_run",
                "stdout": (
                    "Tessl review was not run for this eval-only dashboard. "
                    "Run ./bin/ask skills external-review <path> --json --robot for the local best-practice review lane."
                ),
            },
        },
        "errors": [],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path


def _render_eval_dashboard(repo_root: Path, skill_path: str, mode: str, raw_output: str) -> dict:
    scorecard_path = _scorecard_path_from_output(repo_root, raw_output)
    scorecard = _read_scorecard(scorecard_path)
    source_skill_path = str(scorecard.get("skill_path") or skill_path)
    skill_identifier = _canonical_skill_identifier(repo_root, source_skill_path)
    skill_name = str(scorecard.get("skill") or Path(skill_identifier).name)
    report_path = _latest_review_report(repo_root, skill_identifier)
    if report_path is None:
        report_path = _write_eval_only_review_report(repo_root, skill_name, source_skill_path)

    dashboard_path = repo_root / "Infrastructure" / "artifacts" / "skill-reviews" / f"{_safe_slug(skill_name)}-dashboard-{mode}.html"
    rendered = render_skill_review_dashboard(report_path=report_path, output_path=dashboard_path, repo_root=repo_root)
    relative_dashboard = rendered.relative_to(repo_root).as_posix() if rendered.is_relative_to(repo_root) else str(rendered)
    return {
        "dashboard_path": relative_dashboard,
        "dashboard_url": rendered.resolve().as_uri(),
        "dashboard_tab": "evals",
        "dashboard_source_report": report_path.relative_to(repo_root).as_posix() if report_path.is_relative_to(repo_root) else str(report_path),
        "scorecard_path": scorecard_path.relative_to(repo_root).as_posix() if scorecard_path and scorecard_path.is_relative_to(repo_root) else (str(scorecard_path) if scorecard_path else None),
        "browser_instruction": "Open dashboard_url in the Codex in-app browser after evals complete.",
    }


def run_evals(
    repo_root: Path,
    path: str,
    mode: str = "smoke",
    dashboard: bool = True,
    runner: str = "codex",
    skip_tessl: bool = False,
    allow_tessl_project_save: bool = False,
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
    model: str | None = None,
    codex_profile: str | None = None,
    cases: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> CallResult:
    """Runs evaluation cases for a skill."""
    result = CallResult()
    requested_path = path
    path = _resolve_eval_skill_path(repo_root, path)
    if path != requested_path:
        result.data["requested_path"] = requested_path
        result.data["resolved_skill_path"] = path
    effective_tessl_workspace = None
    tessl_workspace_source = None
    if tessl_workspace:
        try:
            effective_tessl_workspace = _validate_tessl_workspace(tessl_workspace)
            tessl_workspace_source = "argument"
        except ValueError as e:
            if not skip_tessl or tessl_live_private:
                result.status = "error"
                result.data["raw_output"] = ""
                result.data["raw_error"] = str(e)
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": str(e),
                    "blocker_class": "blocked_validation",
                    "workspace_source": "argument",
                }
                result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(e)))
                return result
    if not effective_tessl_workspace:
        try:
            effective_tessl_workspace, tessl_workspace_source = _default_tessl_workspace_from_env()
        except ValueError as e:
            if not skip_tessl or tessl_live_private:
                result.status = "error"
                result.data["raw_output"] = ""
                result.data["raw_error"] = str(e)
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": str(e),
                    "blocker_class": "blocked_validation",
                    "workspace_source": "environment",
                }
                result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(e)))
                return result
            effective_tessl_workspace = None
            tessl_workspace_source = None
    if tessl_live_private and not effective_tessl_workspace:
        message = "Tessl live-private evals require --tessl-workspace <workspace> or an explicit Tessl workspace environment variable."
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = message
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["tessl_eval"] = {
            "status": "blocked",
            "blocker": message,
            "blocker_class": "blocked_validation",
            "workspace_source": "missing",
        }
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message))
        return result
    result.data["tessl_workspace"] = effective_tessl_workspace
    result.data["tessl_workspace_source"] = tessl_workspace_source
    result.data["validation_commands"] = [
        _evals_run_validation_command(
            path,
            mode=mode,
            runner=runner,
            dashboard=dashboard,
            codex_profile=codex_profile,
            tessl_live_private=tessl_live_private,
            tessl_workspace=effective_tessl_workspace,
            tessl_live_dry_run=tessl_live_dry_run,
        )
    ]
    effective_codex_profile = codex_profile or SMOKE_EVAL_PROFILE
    codex_profile_invoked = runner == "codex" and (mode == "smoke" or codex_profile is not None)
    codex_profile_config = f"[profiles.{effective_codex_profile}]" if codex_profile_invoked else None
    result.data["profile_contract"] = {
        "codex_profile": effective_codex_profile if codex_profile_invoked else None,
        "codex_profile_config": codex_profile_config,
        "codex_profile_source": "argument" if codex_profile else "default",
        "codex_profile_required_for_smoke": mode == "smoke" and runner == "codex",
        "codex_exec_invoked": codex_profile_invoked,
        "codex_exec_command_shape": ["codex", "exec", "--profile", effective_codex_profile] if codex_profile_invoked else None,
        "codex_profile_proof_lane": effective_codex_profile if effective_codex_profile in {"oss-local", "oss-cloud"} else None,
        "tessl_policy": _tessl_policy(),
        "tessl_live_private_policy": _tessl_live_private_policy(effective_tessl_workspace) if tessl_live_private else None,
    }

    if tessl_live_dry_run and not tessl_live_private:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["tessl_eval"] = {
            "status": "blocked",
            "blocker": "--tessl-live-dry-run requires --tessl-live-private.",
            "blocker_class": "blocked_validation",
        }
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="--tessl-live-dry-run requires --tessl-live-private.",
        ))
        return result

    if tessl_live_private:
        _start_eval_lifecycle(result, path=path, mode=mode, runner=runner)
        result.status = "success"
        result.data["raw_output"] = ""
        result.data["raw_error"] = ""
        result.data["eval_status"] = "pass"
        result.data["local_eval_status"] = (
            "skipped_tessl_live_dry_run" if tessl_live_dry_run else "skipped_tessl_live_private"
        )
        result.data["blocker_class"] = None
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        if tessl_live_dry_run:
            result.data["tessl_dry_run_note"] = (
                "Tessl live-private dry-run validates the staged private Tessl payload only. "
                "Run without --tessl-live-dry-run only after deterministic local gates, oss-local, "
                "oss-cloud, and this dry-run pass for the current candidate."
            )
        else:
            result.data["tessl_live_private_note"] = (
                "Tessl live-private scoring uses the staged private Tessl payload directly. "
                "Run deterministic local gates, oss-local, oss-cloud, and Tessl dry-run separately before live scoring; "
                "live Tessl quota, auth, project-link, or external scoring blockers remain Tessl-lane blockers, "
                "and oss-local is rerun only for classified local skill regressions."
            )
            handoff_readiness = _tessl_live_handoff_readiness(repo_root, path)
            result.data["handoff_readiness"] = handoff_readiness
            if not handoff_readiness.get("ready_for_live_tessl"):
                result.status = "error"
                result.data["eval_status"] = "blocked_validation"
                result.data["blocker_class"] = "blocked_validation"
                result.data["tessl_eval_status"] = "blocked_validation"
                result.data["tessl_blocker_class"] = "blocked_validation"
                result.data["tessl_eval"] = {
                    "status": "blocked",
                    "blocker": handoff_readiness.get("agent_summary") or "handoff readiness is blocked",
                    "blocker_class": "blocked_validation",
                    "handoff_readiness_path": handoff_readiness.get("readiness_path"),
                    "handoff_readiness_blockers": handoff_readiness.get("blockers", []),
                    "required_next_actions": handoff_readiness.get("required_next_actions", []),
                }
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Tessl live-private blocked: {result.data['tessl_eval']['blocker']}",
                    fix_suggestion="./bin/ask sdk eval handoff-readiness --skill <skill> --preview --json --robot",
                ))
                _finish_eval_lifecycle(
                    result,
                    path=path,
                    mode=mode,
                    runner=runner,
                    eval_status="blocked_validation",
                    blocker_class="blocked_validation",
                )
                return result
        tessl_eval = _run_tessl_live_private_eval(
            repo_root,
            path,
            workspace=effective_tessl_workspace,
            dry_run=tessl_live_dry_run,
        )
        result.data["tessl_eval"] = tessl_eval
        if tessl_eval.get("status") != "pass":
            blocker_class = tessl_eval.get("blocker_class") or "blocked_validation"
            result.status = "error"
            result.data["eval_status"] = blocker_class or str(tessl_eval.get("status") or "fail")
            result.data["blocker_class"] = blocker_class
            result.data["tessl_eval_status"] = result.data["eval_status"]
            result.data["tessl_blocker_class"] = blocker_class
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION",
                    message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}",
                ))
            _finish_eval_lifecycle(
                result,
                path=path,
                mode=mode,
                runner=runner,
                eval_status=result.data["eval_status"],
                blocker_class=blocker_class,
            )
        else:
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")
        return result

    selected_cases: list[str] = []
    for raw_case in cases or []:
        for case_part in raw_case.split(","):
            selected_case = case_part.strip()
            if selected_case:
                selected_cases.append(selected_case)

    qwen_batch_blocker = _qwen_oss_local_batch_blocker(
        mode=mode,
        runner=runner,
        codex_profile=codex_profile,
        selected_cases=selected_cases,
    )
    if qwen_batch_blocker is not None:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = json.dumps(qwen_batch_blocker, indent=2)
        result.data["eval_status"] = "blocked_validation"
        result.data["blocker_class"] = "blocked_validation"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["qwen_oss_local_smoke_batch"] = qwen_batch_blocker
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=(
                f"qwen oss-local {mode} selected {len(selected_cases)} cases; "
                f"maximum shard size is {QWEN_OSS_LOCAL_MAX_BATCH_CASES}."
            ),
            fix_suggestion=qwen_batch_blocker["expected"],
        ))
        return result

    cmd = [
        *_pyyaml_eval_python_command(),
        f"{SKILL_BUILDER_SCRIPTS}/run_skill_evals.py",
        path,
        "--eval-mode", mode,
        "--runner", runner,
    ]
    timeout = RELEASE_EVAL_TIMEOUT_SECONDS if mode == "release" else 300
    if runner == "codex" and (mode == "smoke" or codex_profile is not None):
        sandbox = "read-only" if codex_profile in {"oss-local", "oss-cloud", "codex-fast"} else "workspace-write"
        case_timeout = timeout_seconds or SMOKE_CASE_TIMEOUT_SECONDS
        cmd.extend([
            "--profile",
            effective_codex_profile,
            "--sandbox",
            sandbox,
            "--timeout-sec",
            str(case_timeout),
        ])
        if mode == "smoke" and (model or not codex_profile):
            cmd.extend(["--model", model or SMOKE_EVAL_MODEL])
        selected_case_count = max(len(selected_cases), 1)
        timeout_floor = SMOKE_EVAL_TIMEOUT_SECONDS if mode == "smoke" else RELEASE_EVAL_TIMEOUT_SECONDS
        timeout = max(timeout_floor, int(case_timeout) * selected_case_count + 60)
    elif mode == "smoke":
        timeout = SMOKE_EVAL_TIMEOUT_SECONDS
    if timeout_seconds is not None and not (runner == "codex" and (mode == "smoke" or codex_profile is not None)):
        timeout = timeout_seconds

    for case in selected_cases:
        cmd.extend(["--case", case])

    _start_eval_lifecycle(result, path=path, mode=mode, runner=runner)
    eval_started_at = time.time()

    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_subprocess_env_with_uv_cache(),
            start_new_session=True,
        )
        result.data["raw_output"] = _repo_relative_text(repo_root, process.stdout)
        result.data["raw_error"] = _repo_relative_text(repo_root, process.stderr)
        result.data["eval_status"] = "pass" if process.returncode == 0 else "fail"
        result.data["blocker_class"] = None
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY

        if process.returncode == 0:
            result.status = "success"
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")
            if dashboard:
                try:
                    result.data.update(_render_eval_dashboard(repo_root, path, mode, process.stdout))
                except Exception as e:  # noqa: BLE001
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Evaluation passed, but dashboard rendering failed: {e}",
                        fix_suggestion="Inspect raw_output and rerun ./bin/ask skills external-review <skill> --dashboard if the dashboard report is malformed.",
                    ))
        else:
            blocker_class = _classify_eval_blocker(raw_output=process.stdout, raw_error=process.stderr)
            scorecard_path = _scorecard_path_from_output(repo_root, process.stdout)
            scorecard_blocker_class = _scorecard_blocker_class(_read_scorecard(scorecard_path))
            if blocker_class is None:
                blocker_class = scorecard_blocker_class
            if blocker_class is not None:
                result.data["eval_status"] = blocker_class
                result.data["blocker_class"] = blocker_class
            result.status = "error"
            _finish_eval_lifecycle(
                result,
                path=path,
                mode=mode,
                runner=runner,
                eval_status=result.data["eval_status"],
                blocker_class=blocker_class,
            )
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if blocker_class == "blocked_runtime" else "ERR_VALIDATION",
                message="Evaluation run blocked." if blocker_class is not None else "Evaluation run failed.",
            ))
            if dashboard and scorecard_path is not None:
                try:
                    result.data.update(_render_eval_dashboard(repo_root, path, mode, process.stdout))
                except Exception as e:  # noqa: BLE001
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Evaluation failed, and dashboard rendering also failed: {e}",
                        fix_suggestion="Inspect raw_output and raw_error; the scorecard path may be malformed or unreadable.",
                    ))
    except subprocess.TimeoutExpired as e:
        raw_output = _as_text(e.stdout)
        raw_error = _as_text(e.stderr)
        blocker_class = _classify_eval_blocker(raw_output=raw_output, raw_error=raw_error, timed_out=True)
        partial_artifact = _write_timeout_partial_artifact(
            repo_root,
            skill_path=path,
            mode=mode,
            runner=runner,
            raw_output=raw_output,
            raw_error=raw_error,
        )
        result.status = "error"
        result.data["raw_output"] = raw_output
        result.data["raw_error"] = raw_error
        result.data["eval_status"] = blocker_class
        result.data["blocker_class"] = blocker_class
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        result.data["timeout_classification"] = {
            "class": blocker_class,
            "partial_output_artifact": partial_artifact,
        }
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status=blocker_class or "timeout",
            blocker_class=blocker_class,
        )
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Evaluation timed out after {timeout} seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.data["eval_status"] = "blocked_runtime"
        result.data["blocker_class"] = "blocked_runtime"
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status="blocked_runtime",
            blocker_class="blocked_runtime",
        )
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run evaluation: {e}"))

    if skip_tessl:
        result.data["tessl_eval"] = {
            "status": "skipped",
            "reason": "--skip-tessl",
            "policy": _tessl_policy(),
        }
    else:
        if tessl_live_private:
            tessl_eval = _run_tessl_live_private_eval(
                repo_root,
                path,
                workspace=effective_tessl_workspace,
                dry_run=tessl_live_dry_run,
            )
        else:
            tessl_eval = _run_tessl_eval(
                repo_root,
                path,
                allow_project_save=allow_tessl_project_save,
                workspace=effective_tessl_workspace,
            )
        result.data["tessl_eval"] = tessl_eval
        if tessl_eval.get("status") != "pass":
            tessl_status = str(tessl_eval.get("status") or "fail")
            blocker_class = tessl_eval.get("blocker_class")
            eval_status = blocker_class or tessl_status
            result.data["tessl_eval_status"] = eval_status
            result.data["tessl_blocker_class"] = blocker_class
            if result.status != "error":
                result.data["eval_status"] = eval_status
                result.data["blocker_class"] = blocker_class
                lifecycle_events = result.data.setdefault("lifecycle_events", [])
                if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
                    lifecycle_events.pop()
                _finish_eval_lifecycle(
                    result,
                    path=path,
                    mode=mode,
                    runner=runner,
                    eval_status=eval_status,
                    blocker_class=blocker_class,
                )
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION",
                message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}",
            ))
        elif (
            tessl_live_private
            and tessl_live_dry_run
            and result.status == "error"
            and runner == "discovery-smoke"
            and _is_discovery_smoke_filter_blocker(result.data.get("raw_error"))
        ):
            result.status = "success"
            result.data["local_eval_status"] = result.data.get("eval_status")
            result.data["eval_status"] = "pass"
            result.data["blocker_class"] = None
            result.data["tessl_dry_run_note"] = (
                "Tessl live-private dry-run staged successfully. The discovery-smoke "
                "runner had no smoke_mode cases, so it is recorded as local_eval_status "
                "instead of failing the Tessl staging lane."
            )
            result.errors = [
                error
                for error in result.errors
                if not (
                    error.code == "ERR_VALIDATION"
                    and error.message == "Evaluation run failed."
                )
            ]
            lifecycle_events = result.data.setdefault("lifecycle_events", [])
            if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
                lifecycle_events.pop()
            _finish_eval_lifecycle(result, path=path, mode=mode, runner=runner, eval_status="pass")

    closeout = _write_eval_closeout(
        repo_root,
        skill_path=path,
        mode=mode,
        runner=runner,
        raw_output=str(result.data.get("raw_output") or ""),
        raw_error=str(result.data.get("raw_error") or ""),
        eval_status=str(result.data.get("eval_status") or ("pass" if result.status == "success" else "fail")),
        blocker_class=result.data.get("blocker_class") if isinstance(result.data.get("blocker_class"), str) else None,
        started_at=eval_started_at,
        timeout_seconds=timeout_seconds,
    )
    result.data["eval_closeout"] = closeout
    if closeout.get("path"):
        result.data["eval_closeout_path"] = closeout["path"]
    if closeout.get("status") == "blocked" and result.status != "error":
        blocker_class = str(closeout.get("blocker_class") or "blocked_missing_artifact")
        result.status = "error"
        result.data["eval_status"] = blocker_class
        result.data["blocker_class"] = blocker_class
        lifecycle_events = result.data.setdefault("lifecycle_events", [])
        if lifecycle_events and lifecycle_events[-1].get("event_type") in {"eval_completed", "eval_blocked"}:
            lifecycle_events.pop()
        _finish_eval_lifecycle(
            result,
            path=path,
            mode=mode,
            runner=runner,
            eval_status=blocker_class,
            blocker_class=blocker_class,
        )
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Evaluation run blocked by closeout contract: {blocker_class}.",
            fix_suggestion=str(closeout.get("next_reproduce_command") or result.data["validation_commands"][0]),
        ))

    return result

def benchmark_portfolio(repo_root: Path) -> CallResult:
    """Runs the full repository skill benchmark suite."""
    result = CallResult()
    result.data["validation_commands"] = [_evals_validation_command("benchmark")]

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/benchmark_skill_portfolio.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark suite failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run benchmark: {e}"))

    return result

def dashboard_report(repo_root: Path) -> CallResult:
    """Generates the skill evaluation dashboard."""
    result = CallResult()
    result.data["validation_commands"] = [_evals_validation_command("dashboard")]

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/build_skill_eval_dashboard.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
            result.data["message"] = "Dashboard generated successfully."
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run dashboard generation: {e}"))

    return result
