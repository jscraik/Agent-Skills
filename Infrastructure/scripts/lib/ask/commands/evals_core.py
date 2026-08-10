from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import signal  # noqa: F401 - compatibility facade export
import subprocess  # noqa: F401 - compatibility facade export
import sys
import shutil
import tempfile  # noqa: F401 - compatibility facade export
import hashlib
import time  # noqa: F401 - compatibility facade export
from collections.abc import Mapping
from pathlib import Path
from ask.envelope import CallResult, ErrorObject  # noqa: F401 - compatibility facade export
from ask.commands.skills_impl import _python_command_supports_packages, _subprocess_env_with_uv_cache  # noqa: F401 - compatibility facade export
from ask.skill_review_dashboard import render_skill_review_dashboard  # noqa: F401 - compatibility facade export
from ask.skills_sdk.tessl_eval_quality import (
    normalize_tessl_acceptance_item,  # noqa: F401 - compatibility facade export
    tessl_eval_quality_findings,  # noqa: F401 - compatibility facade export
)  # noqa: F401 - compatibility facade export
from ask.skills_sdk.generated_eval_fixtures import parse_generated_eval_fixtures  # noqa: F401 - compatibility facade export
from ask.skills_sdk.handoff_readiness import build_candidate_identity, default_handoff_readiness_path  # noqa: F401 - compatibility facade export
from ask.skills_sdk.release_scenario_sets import (
    RELEASE_SCENARIO_MAXIMUM,
    RELEASE_SCENARIO_MINIMUM,
    RELEASE_SCENARIO_TARGET,
    release_scenario_set_case_ids,  # noqa: F401 - compatibility facade export
)  # noqa: F401 - compatibility facade export
from .evals_shared import (
    _summarize_tessl_live_eval_view as _build_tessl_live_eval_view,
    _load_json_file,  # noqa: F401 - compatibility facade export
    _portable_command_part,  # noqa: F401 - compatibility facade export
    _sanitize_tessl_live_private_payload,
    _tessl_archive_suffix,
)  # noqa: F401 - compatibility facade export
from .evals_core_exports import EVALS_CORE_EXPORTS


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
TESSL_LIVE_PRIVATE_MIN_SCENARIOS = RELEASE_SCENARIO_MINIMUM
TESSL_LIVE_PRIVATE_TARGET_SCENARIOS = RELEASE_SCENARIO_TARGET
TESSL_LIVE_PRIVATE_MAX_SCENARIOS = RELEASE_SCENARIO_MAXIMUM
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


def _eval_blocker_taxonomy() -> dict[str, str]:
    """Return a serializable blocker taxonomy without shared mutable state."""
    return {
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


def _eval_lifecycle_event_types() -> dict[str, str]:
    """Return serializable lifecycle labels without shared mutable state."""
    return {
        "eval_started": "A workout, smoke eval, or proof run started for a capability.",
        "eval_blocked": "A workout, smoke eval, or proof run stopped on a classified blocker.",
        "eval_completed": "A workout, smoke eval, or proof run completed with pass or fail status.",
    }


EVAL_BLOCKER_TAXONOMY = _eval_blocker_taxonomy()
EVAL_LIFECYCLE_EVENT_TYPES = _eval_lifecycle_event_types()
EVAL_CLOSEOUT_SCHEMA_VERSION = "skills-sdk.eval-closeout.v1"
EVAL_CLOSEOUT_REQUIRED_FIELDS = frozenset({
    "schema_version",
    "status",
    "skill_path",
    "mode",
    "runner",
    "cases",
    "mutation_allowed",
    "registry_update_allowed",
    "next_reproduce_command",
})


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


def _summarize_tessl_live_eval_view(payload: dict[str, object]) -> dict[str, object]:
    return _build_tessl_live_eval_view(
        payload,
        score_solution=_score_solution,
        failed_criteria=_tessl_solution_failed_criteria,
        missing_observable_output=_tessl_solution_missing_observable_output,
        collect_metrics=_collect_tessl_metric_fields,
        minimum_score=TESSL_LIVE_PRIVATE_MIN_SCORE,
        target_score=TESSL_LIVE_PRIVATE_TARGET_SCORE,
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


def _tessl_project_link_receipt_path(
    repo_root: Path,
    skill_path: str,
    candidate: Mapping[str, str],
) -> Path | None:
    handle = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(skill_path).name).strip("-") or "skill"
    digest = candidate.get("candidate_digest")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        return None
    root = repo_root / ".harness" / "evidence" / "tessl-project-links"
    if _path_has_symlink_component_under(root, repo_root):
        return None
    path = root / handle / f"{digest}.json"
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return None
    return path


def _write_tessl_project_link_receipt(
    repo_root: Path,
    skill_path: str,
    *,
    workspace: str,
    identity: Mapping[str, object],
    project_link: Mapping[str, object],
) -> str | None:
    candidate = build_candidate_identity(repo_root, repo_root / skill_path)
    path = _tessl_project_link_receipt_path(repo_root, skill_path, candidate)
    if path is None:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        return None
    payload = {
        "schema_version": "skills-sdk.tessl-project-link.v1",
        "status": "pass",
        "workspace": workspace,
        "project": identity.get("project"),
        "candidate": candidate,
        "staged_source": project_link.get("staged_source"),
        "action": project_link.get("action"),
        "commands": project_link.get("commands", []),
        "issued_at": _utc_now_iso(),
        "purpose": "explicit_project_link_setup_before_live_eval",
    }
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except OSError:
        return None
    return str(path.relative_to(repo_root))


def _validate_tessl_project_link_receipt(
    repo_root: Path,
    skill_path: str,
    workspace: str,
    identity: Mapping[str, object],
) -> dict[str, object]:
    candidate = build_candidate_identity(repo_root, repo_root / skill_path)
    path = _tessl_project_link_receipt_path(repo_root, skill_path, candidate)
    if path is None or not path.is_file() or path.is_symlink():
        return {
            "status": "blocked",
            "blocker_class": "blocked_validation",
            "blocker": "Live Tessl requires a current explicit project-link receipt; the live evaluator does not repair, relink, update, or create Tessl projects.",
            "receipt_path": str(path.relative_to(repo_root)) if path else None,
        }
    try:
        parsed_payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        parsed_payload = None
    payload = parsed_payload if isinstance(parsed_payload, dict) else None
    expected_project = identity.get("project")
    valid = (
        isinstance(payload, dict)
        and payload.get("schema_version") == "skills-sdk.tessl-project-link.v1"
        and payload.get("status") == "pass"
        and payload.get("workspace") == workspace
        and payload.get("project") == expected_project
        and payload.get("candidate") == candidate
    )
    return {
        "status": "pass" if valid else "blocked",
        "blocker_class": None if valid else "blocked_validation",
        "blocker": None if valid else "Live Tessl requires a project-link receipt bound to the current source, scenarios, workspace, and project.",
        "receipt_path": str(path.relative_to(repo_root)),
    }


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

__all__ = EVALS_CORE_EXPORTS
