from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import shutil
import tempfile
import hashlib
from pathlib import Path
from ask.envelope import CallResult, ErrorObject
from ask.skill_review_dashboard import render_skill_review_dashboard


SKILL_BUILDER_SCRIPTS = "Plugins/skill-factory/scripts/skill-builder"
SMOKE_CASE_TIMEOUT_SECONDS = 600
SMOKE_EVAL_TIMEOUT_SECONDS = 10800
RELEASE_EVAL_TIMEOUT_SECONDS = 21600
SMOKE_EVAL_MODEL = "gpt-5.3-codex-spark"
# Codex CLI selects `[profiles.fast]` with the plain profile name.
SMOKE_EVAL_PROFILE = "fast"


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


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return slug or "skill"


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


def _tessl_policy() -> dict:
    """
    Repository-specific Tessl safety contract used to stage and run local evals.
    
    Provides a stable, minimal policy controlling what the Tessl runner may do during
    an eval: restricts to native Tessl, disables publishing/registry/npm operations,
    limits staged inputs to a small allowlist, and exposes stable staging and
    evidence-retention metadata for post-run inspection.
    
    Returns:
        policy (dict): Mapping of policy fields, including:
            - native_tessl_only (bool): require native Tessl CLI usage.
            - no_npx / no_publish / no_registry_upload (bool): forbid package publish/upload.
            - temp_staged_project_input_only (bool): limit inputs to staged project files.
            - stable_staging_root (str): path template for deterministic staging root.
            - evidence_retention (str): human-readable guidance about retained staging evidence.
            - tessl_project_marker (str): filename used as project marker (e.g., "tessl.json").
            - staged_inputs (list[str]): allowed relative input paths to be staged.
            - network_permission_required_by_repo (bool): whether network access is required.
            - project_save_may_use_tessl_service (bool): whether project save may call Tessl service.
            - project_save_default (str): default behavior flag for project-save compatibility.
    """
    temp_root = tempfile.gettempdir()
    return {
        "native_tessl_only": True,
        "no_npx": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_project_input_only": True,
        "stable_staging_root": f"{temp_root}/ask-tessl-evals/<skill-path>-<sha12>",
        "evidence_retention": "stable tmp staging is intentionally left for post-run inspection",
        "tessl_project_marker": "tessl.json",
        "staged_inputs": [
            "SKILL.md",
            "references/evals.yaml",
            "references/contract.yaml",
            "references/task-profile.json",
            "scenarios/<case-id>/task.md",
        ],
        "network_permission_required_by_repo": False,
        "project_save_may_use_tessl_service": False,
        "project_save_default": "compatibility_flag_not_required",
    }


def _copy_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if not source.exists():
        return []
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return [relative_path]


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


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


def _parse_tessl_eval_cases_compat(text: str) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    current: dict[str, str] | None = None
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
            if current and current.get("id") and current.get("prompt"):
                cases.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is None or ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if key not in {"id", "prompt"}:
            index += 1
            continue
        if key == "prompt" and raw_value.startswith((">", "|")):
            current[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
            continue
        current[key] = _yaml_scalar(raw_value)
        index += 1

    if current and current.get("id") and current.get("prompt"):
        cases.append(current)
    return cases


def _parse_tessl_eval_cases(evals_path: Path) -> list[dict[str, str]]:
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
        raise ValueError(f"Failed to parse Tessl eval cases from {evals_path}: {e}") from e
    raw_cases = loaded.get("cases", []) if isinstance(loaded, dict) else []
    cases: list[dict[str, str]] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            continue
        case_id = raw_case.get("id")
        prompt = raw_case.get("prompt")
        if case_id is None or prompt is None:
            continue
        cases.append({"id": str(case_id), "prompt": str(prompt)})
    return cases


def _write_tessl_scenarios_from_evals(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    for case in _parse_tessl_eval_cases(source_root / "references" / "evals.yaml"):
        case_id = case["id"].replace("/", "-")
        task_path = staged_root / "scenarios" / case_id / "task.md"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(case["prompt"].rstrip() + "\n", encoding="utf-8")
        copied.append(str(task_path.relative_to(staged_root)))
    return copied


def _write_tessl_project_marker(source_root: Path, staged_root: Path) -> list[str]:
    marker_path = staged_root / "tessl.json"
    if marker_path.exists():
        return ["tessl.json"]
    marker_path.write_text(
        json.dumps({"name": source_root.name}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _stable_tessl_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stage_tessl_eval_source(repo_root: Path, path: str, temp_root: Path | None = None) -> tuple[Path, list[str]]:
    repo_root_resolved = repo_root.resolve()
    source_root = (repo_root_resolved / path).resolve()
    if not source_root.is_relative_to(repo_root_resolved):
        raise FileNotFoundError("Tessl eval source must be inside repo_root")
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    preserved_marker = staged_root / "tessl.json"
    for child in staged_root.iterdir():
        if child == preserved_marker:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    copied: list[str] = []
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
    copied.extend(_write_tessl_scenarios_from_evals(source_root, staged_root))
    copied.extend(_write_tessl_project_marker(source_root, staged_root))

    if not copied:
        raise FileNotFoundError(f"No Tessl eval staging files found under: {path}")
    return staged_root, copied


def _run_tessl_eval(repo_root: Path, path: str, *, allow_project_save: bool = False) -> dict:
    """
    Run a local Tessl "eval" lane against a staged copy of a skill directory.
    
    Stages a Tessl-compatible project from the given skill path and invokes the native
    `tessl eval run --json` command in that staged workspace. The function returns a
    summary dictionary describing the outcome, staging metadata, raw CLI output, and
    any blocker classification when the run could not complete.
    
    Parameters:
        repo_root (Path): Repository root directory used to resolve and stage the skill.
        path (str): Skill path to stage and evaluate (as provided to the caller).
        allow_project_save (bool): Compatibility flag retained for callers; ignored by this implementation.
    
    Returns:
        dict: A result object containing keys such as:
            - status: "pass", "fail", or "blocked".
            - command: human-readable tessl command that was (or would be) executed.
            - source_path: original requested `path`.
            - staged_source: filesystem path to the staged workspace (when available).
            - staged_files: list of files copied/written into the staged workspace.
            - staging_policy / tessl_project_marker / evidence_retention: metadata about staging and evidence handling.
            - exit_code: numeric process exit code (when available).
            - raw_output, raw_error: captured stdout/stderr from the tessl run.
            - blocker: human-readable blocker message when status == "blocked".
            - blocker_class: taxonomy id for the blocker (e.g., "blocked_runtime", "blocked_auth", "blocked_validation").
            - policy: the Tessl policy dictionary returned by _tessl_policy().
    """
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
        staged_source, copied_files = _stage_tessl_eval_source(repo_root, path)
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
        if process.returncode != 0 and "authenticate with tessl" in auth_text:
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


def _evals_run_validation_command(path: str, *, mode: str, runner: str, dashboard: bool) -> str:
    parts = ["./bin/ask", "evals", "run", path, "--mode", mode, "--runner", runner]
    if not dashboard:
        parts.append("--no-dashboard")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _evals_validation_command(action: str) -> str:
    return " ".join(shlex.quote(part) for part in ["./bin/ask", "evals", action, "--json", "--robot"])


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
    """
    Classify an evaluation blocker ID by scanning combined stdout/stderr for known marker phrases.
    
    Parameters:
        raw_output (str): Captured standard output text to inspect.
        raw_error (str): Captured standard error text to inspect.
        timed_out (bool): When True, classify as a timeout blocker based on whether any output exists.
    
    Returns:
        str | None: Blocker class ID (for example, "blocked_auth" or "timeout_partial_output") when a matching marker is found, `None` otherwise.
    """
    text = "\n".join([raw_output or "", raw_error or ""])
    low = text.lower()

    if timed_out:
        return "timeout_partial_output" if text.strip() else "timeout_no_output"

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

    runtime_markers = [
        "sandbox_apply: operation not permitted",
        "host_execution_untrusted",
        "sandbox-exec",
        "operation not permitted",
        "selected model is at capacity",
        "model is at capacity",
        "context window",
        "start a new thread",
        "blocked_runtime",
    ]
    if any(marker in low for marker in runtime_markers):
        return "blocked_runtime"

    validation_markers = [
        "blocked_validation",
        "validation failed",
        "strict audit failed",
        "policy validation",
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


def _read_scorecard(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


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
    """
    Create an "eval-only" skill review JSON report under Infrastructure/artifacts/skill-reviews and return its filesystem path.
    
    The report documents a synthesized review for a skill when no prior review exists: it records the target skill path, generation timestamp, `review_mode: "eval_only"`, recommended policy thresholds (Codex smoke profile, Tessl thresholds, Snyk defaults, and a deterministic Tessl staging marker), per-lane `review_mode_details` describing which local checks would run, and placeholder results for `ask_audit`, `plugin_eval`, and `tessl_review`. The report file is written as <safe_slug(skill_name)>-eval-latest.json under repo_root/Infrastructure/artifacts/skill-reviews.
    
    Parameters:
    	repo_root (Path): Repository root directory where the artifacts folder will be created.
    	skill_name (str): Human-readable skill name used to construct the filename.
    	skill_path (str): Canonical or requested skill path recorded as the report target.
    
    Returns:
    	Path: The path to the written JSON report file.
    """
    review_root = repo_root / "Infrastructure" / "artifacts" / "skill-reviews"
    review_root.mkdir(parents=True, exist_ok=True)
    report_path = review_root / f"{_safe_slug(skill_name)}-eval-latest.json"
    temp_root = tempfile.gettempdir()
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
                "tessl_review_min_score": 95,
                "codex_smoke_profile": "[profiles.fast]",
                "tessl_eval_staging_root": f"{temp_root}/ask-tessl-evals/<skill-path>-<sha12>",
                "tessl_project_marker": "tessl.json",
                "snyk_default": "disabled_until_requested",
                "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
            },
            "review_mode_details": {
                "local_evals": {
                    "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
                    "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates",
                    "profile": "[profiles.fast] for Codex smoke runs",
                    "tessl_evidence": f"stages copied eval inputs under {temp_root}/ask-tessl-evals with tessl.json",
                    "status": "run_for_this_dashboard",
                },
                "plugin_eval": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "static budget and ergonomics guardrail; not a substitute for local evals",
                    "status": "not_run_in_eval_only_dashboard",
                },
                "tessl_lint": {
                    "command": "./bin/ask skills external-review <path> --json --robot",
                    "role": "disposable tile.json package-shape check, not a direct content finding",
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
    model: str | None = None,
    cases: list[str] | None = None,
) -> CallResult:
    """
    Run eval cases for a skill, optionally run a local Tessl eval lane, and (optionally) render a dashboard.
    
    Parameters:
        repo_root (Path): Repository root directory used to relativize paths and run subprocesses.
        path (str): Skill or eval path to run; may be a generated runtime path and will be resolved to a canonical skill source.
        mode (str): Eval mode, either "smoke" or "release". Affects timeouts and runner/profile behavior.
        dashboard (bool): When True, attempt to render an HTML dashboard from any produced scorecard.
        runner (str): Eval runner identifier (e.g., "codex"); influences command-line args and profile selection.
        skip_tessl (bool): When True, skip running the local Tessl eval lane.
        allow_tessl_project_save (bool): Passed to the Tessl runner for compatibility; controls project save behavior when staging.
        model (str | None): Optional model override used for Codex smoke runs.
        cases (list[str] | None): Optional list of case spec strings; each string may contain comma-separated case ids.
    
    Returns:
        CallResult: Aggregated result object containing:
          - status: "success" or "error"
          - data: keys such as `validation_commands`, `profile_contract`, `raw_output`, `raw_error`,
            `eval_status`, `blocker_class`, `blocker_taxonomy`, lifecycle events, and `tessl_eval`
            (when run) including tessl staging/evidence metadata.
          - errors: list of ErrorObject entries describing runtime/validation issues encountered.
    """
    result = CallResult()
    requested_path = path
    path = _resolve_eval_skill_path(repo_root, path)
    if path != requested_path:
        result.data["requested_path"] = requested_path
        result.data["resolved_skill_path"] = path
    result.data["validation_commands"] = [
        _evals_run_validation_command(path, mode=mode, runner=runner, dashboard=dashboard)
    ]
    result.data["profile_contract"] = {
        "codex_profile": SMOKE_EVAL_PROFILE if mode == "smoke" and runner == "codex" else None,
        "codex_profile_config": "[profiles.fast]" if mode == "smoke" and runner == "codex" else None,
        "codex_profile_required_for_smoke": runner == "codex",
        "tessl_policy": _tessl_policy(),
    }

    cmd = [
        sys.executable, f"{SKILL_BUILDER_SCRIPTS}/run_skill_evals.py",
        path,
        "--eval-mode", mode,
        "--runner", runner,
    ]
    timeout = RELEASE_EVAL_TIMEOUT_SECONDS if mode == "release" else 300
    if mode == "smoke" and runner == "codex":
        smoke_model = model or SMOKE_EVAL_MODEL
        cmd.extend([
            "--profile",
            SMOKE_EVAL_PROFILE,
            "--model",
            smoke_model,
            "--timeout-sec",
            str(SMOKE_CASE_TIMEOUT_SECONDS),
            "--codex-arg",
            "--ignore-user-config",
        ])
        timeout = SMOKE_EVAL_TIMEOUT_SECONDS
    elif mode == "smoke":
        timeout = SMOKE_EVAL_TIMEOUT_SECONDS

    for raw_case in cases or []:
        for case in raw_case.split(","):
            case = case.strip()
            if case:
                cmd.extend(["--case", case])

    _start_eval_lifecycle(result, path=path, mode=mode, runner=runner)

    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=timeout)
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
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Evaluation run failed."))
            if dashboard and _scorecard_path_from_output(repo_root, process.stdout) is not None:
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
        result.status = "error"
        result.data["raw_output"] = raw_output
        result.data["raw_error"] = raw_error
        result.data["eval_status"] = blocker_class
        result.data["blocker_class"] = blocker_class
        result.data["blocker_taxonomy"] = EVAL_BLOCKER_TAXONOMY
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
        tessl_eval = _run_tessl_eval(repo_root, path, allow_project_save=allow_tessl_project_save)
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
