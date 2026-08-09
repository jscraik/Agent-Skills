from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, List
from ask.bootstrap import run_bootstrap_checks
from ask.envelope import CallResult, ErrorCode, ErrorObject
from ask.catalog_parity import compute_catalog_parity
from ask.commands.skills import skills_budget, skills_events, skills_handles, skills_memory, skills_package, skills_profiles
from ask.commands.skills_impl import _subprocess_env_with_uv_cache
from ask.golden_path import build_golden_path_payload

SCRIPT_TIMEOUT_SECONDS = 60
DOCTOR_SIGNAL_PRIORITY = {
    "repo_status": 10,
    "ask_bootstrap": 15,
    "projection_sync": 20,
    "catalog_parity": 30,
    "runtime_budget": 40,
    "sdk_handles": 50,
    "command_handles": 50,
    "capability_readiness": 55,
    "memory_readiness": 56,
    "package_readiness": 57,
    "repo_surface": 60,
}
# Plugin router skills are intentionally hidden from SDK-flat public handle
# resolution, so closeout must validate package readiness through source truth.
PACKAGE_READINESS_SENTINEL = "Plugins/skill-factory/skills/code_quality_review/skill-builder"
SDK_HANDLE_CHECK_COMMAND = "./bin/ask skills list --json --robot"
COMMAND_HANDLE_CHECK_COMMAND = SDK_HANDLE_CHECK_COMMAND
SKILLS_SYNC_COMMAND = "./bin/ask skills sync --scope workspace --projection flat --json --robot"
GENERATED_SURFACE_PREFIXES = (
    ".agents/skills/",
    ".skillsets/",
    ".skill-telemetry/",
)
CANONICAL_SKILL_PREFIXES = (
    "Skills/",
)
RUNTIME_EVIDENCE_ROOT = ".harness/evidence/runtime-proof"
RUNTIME_EVIDENCE_VALIDATOR = Path("Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py")


def _repo_validation_command(action: str, *args: str, **flags: bool) -> str:
    """Build a shell-quoted repository command with machine-readable output."""
    parts = ["./bin/ask", "repo", action, *args]
    for flag, enabled in flags.items():
        if enabled:
            parts.append(f"--{flag.replace('_', '-')}")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def repo_status(repo_root: Path, verbose: bool = False, baseline_path: str | None = None) -> CallResult:
    """Return repository identity and the non-mutating workspace projection state."""
    result = CallResult()
    result.data["validation_commands"] = [_repo_validation_command("status", verbose=verbose)]
    result.data["repo_root"] = "."
    result.data["repo_root_resolved"] = str(repo_root.resolve())
    result.data["is_git"] = (repo_root / ".git").exists()

    skills_dir = repo_root / ".agents" / "skills"
    projection_state, is_synced = _skills_projection_state(repo_root, skills_dir)
    result.data["skills_synced"] = is_synced
    result.data["skills_projection_state"] = projection_state

    if baseline_path is not None:
        try:
            result.data["shape_baseline"] = _shape_baseline(repo_root, baseline_path)
        except RuntimeError as exc:
            result.status = "error"
            result.errors.append(ErrorObject(code=ErrorCode.ERR_VALIDATION, message=str(exc)))
            return result

    result.status = "success"
    return result


def _skills_projection_state(repo_root: Path, skills_dir: Path) -> tuple[str, bool]:
    """Classify the workspace runtime projection without creating or repairing it."""
    if skills_dir.is_dir():
        try:
            return ("synced", True) if any(skills_dir.iterdir()) else ("empty", False)
        except OSError:
            return "corrupt", False
    if skills_dir.exists() or skills_dir.is_symlink():
        return "corrupt", False
    if _is_linked_worktree(repo_root):
        return "unmaterialized_linked_worktree", False
    return "missing", False


def _is_linked_worktree(repo_root: Path) -> bool:
    """Return whether Git represents this checkout with a gitdir pointer file."""
    git_path = repo_root / ".git"
    if not git_path.is_file():
        return False
    try:
        return git_path.read_text(encoding="utf-8").startswith("gitdir: ")
    except OSError:
        return False


def _can_import_yaml_with(command: List[str]) -> bool:
    try:
        completed = subprocess.run(
            [*command, "-c", "import yaml"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=_subprocess_env_with_uv_cache(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def _managed_pyyaml_python_command() -> List[str]:
    candidates: List[List[str]] = []
    python_bin = os.environ.get("PYTHON_BIN")
    if python_bin:
        candidates.append([python_bin])
    candidates.append([sys.executable])

    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if preferred.exists():
        candidates.append([str(preferred)])

    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        key = tuple(candidate)
        if key in seen:
            continue
        seen.add(key)
        if _can_import_yaml_with(candidate):
            return candidate

    return ["uv", "run", "--no-project", "--with", "PyYAML", "python"]


def repo_yaml_inspect(repo_root: Path, path: str, query: str | None = None) -> CallResult:
    """Parse a repo YAML file through the managed PyYAML interpreter.

    This command exists so agents do not reach for ad hoc system-python snippets
    that depend on the system interpreter having PyYAML installed.
    """
    result = CallResult()
    target = (repo_root / path).resolve()
    try:
        target.relative_to(repo_root.resolve())
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_PATH_TRAVERSAL,
                message=f"YAML path must stay inside the repository: {path}",
                fix_suggestion="Pass a repo-relative YAML file path.",
            )
        )
        return result
    if not target.exists() or not target.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=f"YAML file not found: {path}",
                fix_suggestion="Pass an existing repo-relative YAML file path.",
            )
        )
        return result

    python_cmd = _managed_pyyaml_python_command()
    command_display = " ".join(shlex.quote(part) for part in [*python_cmd, "-"])
    result.data["validation_commands"] = [
        " ".join(
            [
                "./bin/ask",
                "repo",
                "yaml-inspect",
                shlex.quote(path),
                *( ["--query", shlex.quote(query)] if query else [] ),
                "--json",
                "--robot",
            ]
        )
    ]
    result.data["python_command"] = command_display
    result.data["path"] = str(target.relative_to(repo_root.resolve()))

    inspector = '''
import json
import sys
from pathlib import Path
import yaml

path = Path(sys.argv[1])
query = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None

def project(value, query):
    current = value
    if not query:
        return current
    for raw_part in query.split("."):
        if not raw_part:
            raise KeyError("empty query segment")
        part = raw_part
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(part)
            current = current[part]
            continue
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError as exc:
                raise KeyError(part) from exc
            current = current[index]
            continue
        raise KeyError(part)
    return current

def to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)

payload = yaml.safe_load(path.read_text(encoding="utf-8"))
selected = project(payload, query)
summary = {
    "root_type": type(payload).__name__,
    "query": query,
    "query_type": type(selected).__name__,
    "query_value": to_jsonable(selected),
}
if isinstance(payload, dict):
    summary["top_level_keys"] = sorted(str(key) for key in payload.keys())
if isinstance(payload, list):
    summary["item_count"] = len(payload)
if isinstance(selected, dict):
    summary["query_keys"] = sorted(str(key) for key in selected.keys())
if isinstance(selected, list):
    summary["query_item_count"] = len(selected)
print(json.dumps(summary, ensure_ascii=False))
'''
    try:
        completed = subprocess.run(
            [*python_cmd, "-", str(target), query or ""],
            input=inspector,
            capture_output=True,
            text=True,
            check=False,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            env=_subprocess_env_with_uv_cache(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_DEPENDENCY,
                message=f"Unable to inspect YAML with managed PyYAML interpreter: {exc}",
                fix_suggestion="Run ./bin/ask repo doctor --json --robot and verify uv or a PyYAML-capable Python is available.",
            )
        )
        return result

    if completed.returncode != 0:
        result.status = "error"
        result.data["stderr"] = completed.stderr
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=f"YAML inspection failed for {path}.",
                fix_suggestion=completed.stderr.strip() or "Check YAML syntax and query path.",
            )
        )
        return result

    try:
        result.data["yaml"] = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        result.status = "error"
        result.data["stdout"] = completed.stdout
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_RUNTIME,
                message=f"YAML inspector returned non-JSON output: {exc}",
                fix_suggestion="Inspect the managed Python command output and rerun repo yaml-inspect.",
            )
        )
        return result

    result.status = "success"
    return result

def repo_validate(
    repo_root: Path,
    ephemeral: bool = False,
    fail_fast: bool = False,
    scope: str = "all",
    changed_files: List[str] | None = None,
) -> CallResult:
    """Run the repository validation wrapper and return its parsed result."""
    result = CallResult()

    cmd = ["bash", "Infrastructure/scripts/validate_all.sh"]
    if ephemeral:
        cmd.append("--ephemeral")
    else:
        cmd.append("--persistent")
    if fail_fast:
        cmd.append("--fail-fast")
    if scope and scope != "all":
        cmd.extend(["--scope", scope])
    if changed_files:
        cmd.append("--changed-files")
        cmd.extend(changed_files)

    VALIDATE_TIMEOUT = 300  # 5 minutes
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=VALIDATE_TIMEOUT,
        )
        stdout = completed.stdout or ""
        if stdout:
            print(stdout, end="", file=sys.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        timeout_msg = f"Validation timed out after {VALIDATE_TIMEOUT} seconds."
        stdout += timeout_msg + "\n"
        print(stdout, end="", file=sys.stderr)
        completed = subprocess.CompletedProcess(cmd, returncode=124, stdout=stdout)
    except OSError as exc:
        result.status = "error"
        result.data["required_failures"] = 1
        result.data["warn_only_issues"] = 0
        result.data["raw_output"] = str(exc)
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Unable to start validation command: {exc}",
            fix_suggestion="Verify bash and Infrastructure/scripts/validate_all.sh are available."
        ))
        return result

    # Parse output for summary
    required_failures = 0
    warn_only_issues = 0

    # Handle early exit case where validation script fails before producing summary
    if "- required_failures:" not in stdout or "- warn_only_issues:" not in stdout:
        result.data["required_failures"] = 1  # Assume failure if any summary field is missing
        result.data["warn_only_issues"] = 0
        result.data["raw_output"] = stdout
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Validation script failed before producing summary output.",
            fix_suggestion="Check validation logs for script errors."
        ))
        return result

    for line in stdout.splitlines():
        if "- required_failures:" in line:
            required_failures = int(line.split(":")[-1].strip())
        elif "- warn_only_issues:" in line:
            warn_only_issues = int(line.split(":")[-1].strip())

    result.data["required_failures"] = required_failures
    result.data["warn_only_issues"] = warn_only_issues
    result.data["raw_output"] = stdout
    result.data["ephemeral"] = ephemeral
    result.data["fail_fast"] = fail_fast
    result.data["scope"] = scope
    result.data["changed_files"] = changed_files or []

    if completed.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Validation failed with {required_failures} required failures.",
            fix_suggestion="Review the validation logs in Infrastructure/artifacts/validation/latest/"
        ))

    return result
__all__ = [name for name in globals() if not name.startswith("__")]
