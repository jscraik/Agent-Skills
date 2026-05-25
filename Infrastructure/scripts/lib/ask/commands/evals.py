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
DEFAULT_MACRO_EVAL_REPORTS_GLOB = "artifacts/reports/skills/*/*/summary.json"


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


def _tessl_staging_root_template() -> str:
    """Return the human-readable template for stable Tessl eval staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-evals" / "<skill-path>-<sha12>")


def _tessl_live_staging_root_template() -> str:
    """Return the human-readable template for private Tessl live tile staging."""
    return str(Path(tempfile.gettempdir()) / "ask-tessl-live" / "<skill-path>-<sha12>")


def _tessl_policy() -> dict:
    """Return the repo's Tessl safety contract for eval runs."""
    return {
        "native_tessl_only": True,
        "no_npx": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_project_input_only": True,
        "stable_staging_root": _tessl_staging_root_template(),
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


def _tessl_live_private_policy(workspace: str | None = None) -> dict:
    """Return the repo's opt-in private Tessl tile eval contract."""
    return {
        "enabled_by": "--tessl-live-private",
        "visibility": "private",
        "tile_private_required": True,
        "workspace_required": True,
        "workspace": workspace,
        "tile_name_format": "workspace/tile-name",
        "native_tessl_only": True,
        "no_npx": True,
        "no_install": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_tile_input_only": True,
        "stable_staging_root": _tessl_live_staging_root_template(),
        "tessl_project_marker": "tessl.json",
        "tile_manifest": "tile.json",
        "eval_layout": "evals/<case-id>/{task.md,criteria.json}",
        "staged_inputs": [
            "tile.json",
            "tessl.json",
            "SKILL.md",
            "references/evals.yaml",
            "references/contract.yaml",
            "references/task-profile.json",
            "references/**/*",
            "evals/<case-id>/task.md",
            "evals/<case-id>/criteria.json",
        ],
        "command_shape": "tessl eval run --json <staged-tile-json>",
        "usage_data_opt_out": "tessl config set shareUsageData false",
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
            current[key.strip()] = _yaml_scalar(raw_value.strip())
        index += 1

    if current:
        items.append(current)
    return items, index


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
        if key == "acceptance":
            acceptance, index = _consume_yaml_sequence_dicts(lines, index + 1, indent)
            current[key] = acceptance  # type: ignore[assignment]
            continue
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
        compat_cases = _parse_tessl_eval_cases_compat(text)
        if compat_cases and (
            "while parsing a block mapping" in str(e)
            or "expected <block end>" in str(e)
        ):
            return compat_cases
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
        case = {"id": str(case_id), "prompt": str(prompt)}
        acceptance = raw_case.get("acceptance")
        if isinstance(acceptance, list):
            case["acceptance"] = acceptance  # type: ignore[assignment]
        cases.append(case)
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


def _validate_tessl_workspace(workspace: str | None) -> str:
    if workspace is None or not workspace.strip():
        raise ValueError("Tessl live-private evals require --tessl-workspace <workspace>.")
    normalized = workspace.strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", normalized):
        raise ValueError(
            "Tessl workspace must be lowercase and contain only letters, numbers, '.', '_', or '-'."
        )
    if "/" in normalized:
        raise ValueError("Tessl workspace must be the workspace name only, not workspace/tile.")
    return normalized


def _tessl_eval_case_id(case_id: str) -> str:
    return _safe_slug(case_id.replace("/", "-"))


def _tessl_criteria_from_case(case: dict[str, object]) -> dict:
    checklist: list[dict[str, object]] = []
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for index, item in enumerate(acceptance, start=1):
            if not isinstance(item, dict):
                continue
            criterion_type = str(item.get("type") or "acceptance").strip()
            value = str(item.get("value", item.get("expected_skill", "Satisfies acceptance criterion."))).strip()
            category = "MUST_NOT" if criterion_type.startswith(("forbidden", "must_not")) else "INTENT"
            checklist.append({
                "name": _safe_slug(f"{criterion_type}-{index}"),
                "description": value,
                "max_score": 1,
                "category": category,
                "source": "references/evals.yaml",
            })

    if not checklist:
        checklist.append({
            "name": "task-satisfaction",
            "description": "The agent response satisfies task.md and the skill contract.",
            "max_score": 1,
            "category": "INTENT",
            "source": "references/evals.yaml",
        })

    return {
        "context": f"Evaluation criteria adapted from references/evals.yaml for {case.get('id') or 'unknown'}.",
        "type": "weighted_checklist",
        "checklist": checklist,
        "metadata": {
            "schema_version": "ask-tessl-criteria-adapter.v1",
            "source_case_id": str(case.get("id") or "unknown"),
        },
    }


def _write_tessl_live_evals_from_references(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    for case in _parse_tessl_eval_cases(source_root / "references" / "evals.yaml"):
        case_id = _tessl_eval_case_id(str(case["id"]))
        case_root = staged_root / "evals" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        task_path = case_root / "task.md"
        task_path.write_text(case["prompt"].rstrip() + "\n", encoding="utf-8")
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


def _write_tessl_live_tile_manifest(source_root: Path, staged_root: Path, workspace: str) -> list[str]:
    tile_slug = _safe_slug(source_root.name.lower())
    manifest = {
        "name": f"{workspace}/{tile_slug}",
        "version": "0.0.0",
        "summary": f"Private live eval tile for {source_root.name}.",
        "entrypoint": "SKILL.md",
        "private": True,
        "skills": {
            source_root.name: {
                "path": "SKILL.md",
            },
        },
    }
    tile_path = staged_root / "tile.json"
    tile_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return ["tile.json", *_write_tessl_live_project_marker(staged_root, workspace, tile_slug)]


def _validate_tessl_live_private_manifest(tile_path: Path, workspace: str) -> None:
    try:
        manifest = json.loads(tile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to read staged Tessl tile manifest: {e}") from e
    if not isinstance(manifest, dict):
        raise ValueError("Staged Tessl tile manifest must be a JSON object.")
    tile_name = manifest.get("name")
    if not isinstance(tile_name, str) or not tile_name.startswith(f"{workspace}/"):
        raise ValueError("Staged Tessl tile name must use workspace/tile-name format for the requested workspace.")
    if manifest.get("private") is not True:
        raise ValueError("Staged Tessl tile manifest must set private: true.")
    if not any(key in manifest for key in ("docs", "steering", "skills")):
        raise ValueError("Staged Tessl tile manifest must include docs, steering, or skills.")


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


def _stable_tessl_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stable_tessl_live_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-live" / f"{safe_name}-{digest}"


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
    for child in staged_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    copied: list[str] = []
    copied.extend(_write_tessl_live_tile_manifest(source_root, staged_root, workspace))
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
    copied.extend(_copy_tessl_live_reference_support_files(source_root, staged_root, set(copied)))
    copied.extend(_write_tessl_live_evals_from_references(source_root, staged_root))
    _validate_tessl_live_private_manifest(staged_root / "tile.json", workspace)

    if "SKILL.md" not in copied:
        raise FileNotFoundError(f"No SKILL.md found under Tessl live eval source: {path}")
    return staged_root, copied


def _tessl_eval_result_common(
    *,
    command: str,
    source_path: str,
    staged_source: Path,
    copied_files: list[str],
    workspace: str,
    dry_run: bool,
) -> dict:
    return {
        "command": command,
        "source_path": source_path,
        "staged_source": str(staged_source),
        "tile_manifest": str(staged_source / "tile.json"),
        "tessl_project_marker": str(staged_source / "tessl.json") if (staged_source / "tessl.json").exists() else None,
        "staged_files": copied_files,
        "staging_policy": "stable_tmp_private_tile_evidence",
        "workspace": workspace,
        "visibility": "private",
        "dry_run": dry_run,
        "live_private": True,
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-live for inspection",
        "policy": _tessl_live_private_policy(workspace),
    }


def _run_tessl_live_private_eval(
    repo_root: Path,
    path: str,
    *,
    workspace: str | None,
    dry_run: bool = False,
) -> dict:
    """Run or preview the opt-in private Tessl tile eval lane."""
    command_display = "tessl eval run --json <staged-tile-json>"
    try:
        normalized_workspace = _validate_tessl_workspace(workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, path, normalized_workspace)
        tile_path = staged_source / "tile.json"
        command_display = f"tessl eval run --json {tile_path}"
    except (OSError, ValueError) as e:
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to stage private Tessl tile eval source: {e}",
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
        dry_run=dry_run,
    )
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

    cmd = [tessl_path, "eval", "run", "--json", str(tile_path)]
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
            **common,
            "raw_output": _as_text(e.stdout),
            "raw_error": _as_text(e.stderr),
            "blocker": "Tessl private tile eval timed out after 600 seconds.",
            "blocker_class": "blocked_runtime",
        }
    except OSError as e:
        return {
            "status": "blocked",
            **common,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to run Tessl private tile eval: {e}",
            "blocker_class": "blocked_runtime",
        }

    raw_output = process.stdout
    raw_error = process.stderr
    auth_text = f"{raw_output}\n{raw_error}".lower()
    if process.returncode != 0 and "authenticate with tessl" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI is installed locally, but authentication is required before private tile evals can run."
        blocker_class = "blocked_auth"
    elif process.returncode != 0 and "no existing project safely matches this directory" in auth_text:
        status = "blocked"
        blocker = (
            "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the "
            "temp-staged private tile eval directory. Run tessl project create/link/repair for a live project lane."
        )
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "no tessl project found" in auth_text:
        status = "blocked"
        blocker = "Tessl CLI could not find a tessl.json project marker in the staged private tile eval directory."
        blocker_class = "blocked_validation"
    elif process.returncode != 0 and "project that was not found or is not accessible" in auth_text:
        status = "blocked"
        blocker = (
            f"Tessl project {normalized_workspace}/{_safe_slug(Path(path).name.lower())} "
            f"was not found or is not accessible. Create, link, or repair that project "
            f"in workspace {normalized_workspace} before running live evals."
        )
        blocker_class = "blocked_validation"
    else:
        status = "pass" if process.returncode == 0 else "fail"
        blocker = None
        blocker_class = None

    return {
        "status": status,
        **common,
        "exit_code": process.returncode,
        "raw_output": raw_output,
        "raw_error": raw_error,
        "blocker": blocker,
        "blocker_class": blocker_class,
    }


def _run_tessl_eval(repo_root: Path, path: str, *, allow_project_save: bool = False) -> dict:
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
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
) -> str:
    parts = ["./bin/ask", "evals", "run", path, "--mode", mode, "--runner", runner]
    if tessl_live_private:
        parts.append("--tessl-live-private")
    if tessl_workspace:
        parts.extend(["--tessl-workspace", tessl_workspace])
    if tessl_live_dry_run:
        parts.append("--tessl-live-dry-run")
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
                "tessl_review_min_score": 95,
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
    tessl_live_private: bool = False,
    tessl_workspace: str | None = None,
    tessl_live_dry_run: bool = False,
    model: str | None = None,
    cases: list[str] | None = None,
) -> CallResult:
    """Runs evaluation cases for a skill."""
    result = CallResult()
    requested_path = path
    path = _resolve_eval_skill_path(repo_root, path)
    if path != requested_path:
        result.data["requested_path"] = requested_path
        result.data["resolved_skill_path"] = path
    result.data["validation_commands"] = [
        _evals_run_validation_command(
            path,
            mode=mode,
            runner=runner,
            dashboard=dashboard,
            tessl_live_private=tessl_live_private,
            tessl_workspace=tessl_workspace,
            tessl_live_dry_run=tessl_live_dry_run,
        )
    ]
    result.data["profile_contract"] = {
        "codex_profile": SMOKE_EVAL_PROFILE if mode == "smoke" and runner == "codex" else None,
        "codex_profile_config": "[profiles.fast]" if mode == "smoke" and runner == "codex" else None,
        "codex_profile_required_for_smoke": mode == "smoke" and runner == "codex",
        "tessl_policy": _tessl_policy(),
        "tessl_live_private_policy": _tessl_live_private_policy(tessl_workspace) if tessl_live_private else None,
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
        if tessl_live_private:
            tessl_eval = _run_tessl_live_private_eval(
                repo_root,
                path,
                workspace=tessl_workspace,
                dry_run=tessl_live_dry_run,
            )
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
