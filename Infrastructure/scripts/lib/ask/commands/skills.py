import os
import json
import shlex
import shutil
import subprocess
import re
import sys
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "lifecycle-and-sync") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "lifecycle-and-sync"))

from ask.envelope import CallResult, ErrorObject  # noqa: E402
from ask.commands.plugins import (  # noqa: E402
    _copy_directory_contents,
    _load_local_marketplace,
    _materialize_first_level_skill_aliases,
)
from skill_discovery import discover_catalog_entries, discover_skill_entries, get_policy_identity, render_index  # noqa: E402
from selection_policy import REPO_SCAN_ROOTS, SYSTEM_BRIDGE_SKILL_NAMES  # noqa: E402
from projection_engine import (  # noqa: E402
    ProjectionModeError,
    build_projection_plan_metadata,
    normalize_projection_mode,
)
from command_surface import (  # noqa: E402
    check_command_handles,
    handles_report,
    parse_command_handles,
    resolve_reviewer_handle,
    resolve_skill_handle,
    write_command_handles,
    write_command_surface_projection,
)
from generate_root_skill_sets import build_roots, write_roots  # noqa: E402
from generate_skillset_manifests import build_manifest_report, write_manifests  # noqa: E402
from rooted_projection_runtime import prune_unowned_skillset_files, validate_workspace_runtime  # noqa: E402
from ask.catalog_parity import compute_catalog_parity  # noqa: E402
from ask.selection_contract import (  # noqa: E402
    EligibleCandidate,
    build_decision_payload,
    build_goal_decision,
    candidate_id,
    canonical_sort_key,
)


def _get_python_command(with_packages: Optional[List[str]] = None) -> List[str]:
    """
    Constructs a platform-appropriate Python invocation command.
    
    The returned command is chosen with this observable precedence: a non-empty PYTHON_BIN environment value, a local Python that already satisfies requested packages, a `mise`+`uv` wrapper, an `uv` wrapper, then the system `python3`. Prefer an existing local environment before `uv --with` so offline audits do not try to fetch packages from PyPI.
    
    Parameters:
        with_packages (Optional[List[str]]): Optional iterable of package names to request via `--with` when using a wrapper that accepts package flags; falsy entries are ignored.
    
    Returns:
        List[str]: Tokenised command suitable for subprocess invocation to run Python.
    """
    configured = os.environ.get("PYTHON_BIN", "").strip()
    if configured:
        return shlex.split(configured)

    packages = [pkg for pkg in (with_packages or []) if pkg]
    if packages:
        preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
        for candidate in ([str(preferred)], ["python3"]):
            if _python_command_supports_packages(candidate, packages):
                return candidate

    if shutil.which("mise") and shutil.which("uv"):
        cmd: List[str] = ["mise", "exec", "--", "uv", "run", "--python", "3.12"]
        for pkg in packages:
            cmd.extend(["--with", pkg])
        cmd.append("python")
        return cmd

    if shutil.which("uv"):
        cmd = ["uv", "run", "--python", "3.12"]
        for pkg in packages:
            cmd.extend(["--with", pkg])
        cmd.append("python")
        return cmd

    return ["python3"]


def _python_command_supports_packages(command: List[str], packages: List[str]) -> bool:
    """Return true when *command* can import every requested package without installation."""
    executable = Path(command[0]).expanduser()
    if os.sep in command[0] and not executable.exists():
        return False
    if os.sep not in command[0] and not shutil.which(command[0]):
        return False
    module_names = ["yaml" if package == "pyyaml" else package for package in packages]
    probe = (
        "import importlib.util, sys; "
        "missing=[name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]; "
        "sys.exit(1 if missing else 0)"
    )
    try:
        completed = subprocess.run(
            [*command, "-c", probe, *module_names],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def extract_family_fail_lines(stdout: str) -> List[str]:
    """Extract normalized FAIL lines from family benchmark stdout."""
    failures: List[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if line.startswith(("- FAIL ", "FAIL ")):
            failures.append(line.lstrip("- "))
    return failures


def _summarize_family_benchmark_failure(stdout: str, stderr: str, limit: int = 3) -> Optional[str]:
    """Return a compact summary of FAIL lines from family benchmark output."""
    fail_lines = extract_family_fail_lines(stdout)

    if fail_lines:
        head = fail_lines[:limit]
        summary = "; ".join(head)
        remainder = len(fail_lines) - len(head)
        if remainder > 0:
            summary += f"; +{remainder} more"
        return summary

    for raw_line in stderr.splitlines():
        line = raw_line.strip()
        if line:
            return line

    return None


@dataclass(frozen=True)
class _RouterSkill:
    name: str
    description: str
    skill_path: str


STARTER_ARCHETYPES = {
    "general": (
        "he-brainstorm",
        "he-spec",
        "he-plan",
        "he-work",
        "he-technical-review",
        "gh-workflow",
        "docs-expert",
        "context7",
    ),
    "delivery": ("he-plan", "he-work", "he-review", "gh-workflow", "coding-harness"),
    "review": ("he-technical-review", "he-review", "security-best-practices"),
    "docs": ("agents-md", "docs-expert", "context7", "openai-docs"),
}


_SKILL_INSTALLER_SCRIPT_CANDIDATES = (
    "Plugins/skill-factory/skills/infrastructure_ops/skill-installer/scripts/install-skill-from-github.py",
)

_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES = (
    "Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts",
    "plugins/skill-factory/skills/code_quality_review/skill-builder/scripts",
)


def _resolve_skill_installer_script(repo_root: Path) -> str:
    for rel in _SKILL_INSTALLER_SCRIPT_CANDIDATES:
        candidate = repo_root / rel
        if candidate.is_file():
            return rel
    # Keep canonical path in the error payload for predictable operator guidance.
    return _SKILL_INSTALLER_SCRIPT_CANDIDATES[0]


def _resolve_skill_builder_script(repo_root: Path, module_name: str) -> str:
    filename = f"{module_name}.py"
    for rel_dir in _SKILL_BUILDER_SCRIPT_DIR_CANDIDATES:
        candidate = repo_root / rel_dir / filename
        if candidate.is_file():
            return f"{rel_dir}/{filename}"
    return f"{_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES[0]}/{filename}"


# Explicitly load builder-specific logic using absolute paths to avoid namespace collisions
def _load_builder_module(repo_root: Path, module_name: str):
    """
    Load a skill-builder script from the repository and return it as an imported module.
    
    Parameters:
        repo_root (Path): Repository root used to locate `<skill-builder>/scripts/<module_name>.py`.
        module_name (str): Script base name (without `.py`) to load.
    
    Returns:
        module (types.ModuleType | None): The imported module object if the script exists and is loaded, `None` otherwise.
    """
    module_rel = _resolve_skill_builder_script(repo_root, module_name)
    module_path = repo_root / module_rel
    if not module_path.exists():
        return None
    scripts_dir = module_path.parent

    internal_name = f"ask_builder_{module_name}"
    if internal_name in sys.modules:
        return sys.modules[internal_name]

    scripts_dir_str = str(scripts_dir)
    inserted = False
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(internal_name, str(module_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[internal_name] = mod  # Register BEFORE exec
            spec.loader.exec_module(mod)
            return mod
    finally:
        if inserted and scripts_dir_str in sys.path:
            sys.path.remove(scripts_dir_str)
    return None

def _canonical_entries(
    repo_root: Path,
    *,
    source: str = "auto",
    visibility: str = "default",
) -> list:
    """
    Filter discovered skill entries to those whose source directory is inside the repository root.
    
    Parameters:
    	repo_root (Path): Repository root used to determine whether an entry's `source_dir` is inside the repository.
    
    Returns:
    	entries (list): Discovered skill entries whose `source_dir` is relative to `repo_root`.
    """
    return [
        entry
        for entry in discover_skill_entries(source=source, visibility=visibility)
        if entry.source_dir.is_relative_to(repo_root)
    ]


def _starter_entries(entries: list, archetype: str, limit: int) -> list:
    """
    Selects a deterministic subset of skill entries for starter mode.
    
    Prefers skills listed in the chosen archetype (in archetype order) and, if needed, appends additional entries from the provided list until a bounded minimum of 1 up to `limit` items is reached. Unknown archetype keys fall back to the "general" archetype.
    
    Parameters:
        entries (list): Iterable of skill entry objects; each must expose a `name` attribute.
        archetype (str): Archetype key whose ordered starter names guide preferred selection.
        limit (int): Maximum number of entries to return; values below 1 are treated as 1.
    
    Returns:
        list: Ordered list of selected entries (length >= 1 and <= `limit`), preferring archetype-specified names first and then remaining entries in input order.
    """
    bounded_limit = max(1, int(limit))
    archetype_key = archetype if archetype in STARTER_ARCHETYPES else "general"
    preferred = list(STARTER_ARCHETYPES[archetype_key])
    by_name = {entry.name: entry for entry in entries}
    selected = [by_name[name] for name in preferred if name in by_name]
    if len(selected) >= bounded_limit:
        return selected[:bounded_limit]

    seen = {item.name for item in selected}
    for entry in entries:
        if entry.name in seen:
            continue
        selected.append(entry)
        if len(selected) >= bounded_limit:
            break
    return selected


def _refresh_catalog_projections(repo_root: Path, dry_run: bool = False) -> list[str]:
    """
    Regenerate root catalog projections from the default catalog surface.

    Parameters:
        repo_root (Path): Repository root containing `README.md` and `SKILL.md`.
        dry_run (bool): When `True`, do not write files and only describe planned changes.

    Returns:
        list[str]: Human-readable log lines describing projection updates.
    """
    entries = [
        entry
        for entry in discover_catalog_entries(source="repo")
        if entry.source_dir.is_relative_to(repo_root)
    ]
    catalog_count = len(entries)
    logs: list[str] = []

    skill_index_path = repo_root / "SKILL.md"
    rendered_index = render_index(entries, source="catalog", visibility="default") + "\n"
    if dry_run:
        logs.append(f"Would refresh catalog index: {skill_index_path}")
    else:
        skill_index_path.write_text(rendered_index, encoding="utf-8")
        logs.append(f"Refreshed catalog index: {skill_index_path}")

    readme_path = repo_root / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        updated_readme, replacements = re.subn(
            r"A governed repository of \*\*\d+(?: canonical)? skills\*\* for AI coding agents",
            f"A governed repository of **{catalog_count} skills** for AI coding agents",
            readme_content,
            count=1,
        )
        if replacements == 0:
            updated_readme, replacements = re.subn(
                r"A governed repository of AI coding skills\.",
                f"A governed repository of **{catalog_count} skills** for AI coding agents.",
                updated_readme,
                count=1,
            )
        updated_readme = re.sub(
            r"currently expects \*\*\d+\*\* skills",
            f"currently expects **{catalog_count}** skills",
            updated_readme,
            count=1,
        )
        if dry_run:
            if updated_readme != readme_content:
                logs.append(f"Would refresh README skill count: {readme_path}")
        elif updated_readme != readme_content:
            readme_path.write_text(updated_readme, encoding="utf-8")
            logs.append(f"Refreshed README skill count: {readme_path}")

    return logs

def list_skills(
    repo_root: Path,
    category: Optional[str] = None,
    *,
    starter: bool = False,
    archetype: str = "general",
    limit: int = 12,
    advanced: bool = False,
) -> CallResult:
    """
    List discovered catalog skills within the repository, optionally filtered by category or reduced to a deterministic starter subset.
    
    Parameters:
    	repo_root (Path): Repository root used to filter discovered catalog entries; entries outside this root are excluded.
    	category (Optional[str]): Case-insensitive substring applied to each entry's category; omit to include all categories.
    	starter (bool): When true, return a deterministic subset selected by `archetype` and limited by `limit`.
    	archetype (str): Archetype key used to pick starter skills; unknown keys fall back to "general".
    	limit (int): Maximum number of skills to return when `starter` is true; coerced to at least 1.
    	advanced (bool): Include advanced/hidden-lane catalog entries when true; otherwise use the default listing.
    
    Returns:
    	CallResult: Result with `status == "success"` and `data` containing:
    		- "skills": list of objects with `name`, `path` (repo-relative when possible), `category`, and `description`
    		- "policy_identity": current policy identity string
    		- "advanced_mode": boolean reflecting the `advanced` parameter
    		- When `starter` is true, also includes:
    			- "starter_mode": true
    			- "starter_archetype": resolved archetype key
    			- "starter_limit": effective integer limit
    """
    result = CallResult()
    entries = [
        entry
        for entry in discover_catalog_entries(advanced=advanced)
        if entry.source_dir.is_relative_to(repo_root)
    ]
    if starter:
        entries = _starter_entries(entries, archetype=archetype, limit=limit)
    skills_data = []
    for entry in entries:
        if category and category.lower() not in entry.category.lower():
            continue
        skills_data.append({
            "name": entry.name,
            "path": str(entry.source_dir.relative_to(repo_root)) if entry.source_dir.is_relative_to(repo_root) else str(entry.source_dir),
            "category": entry.category,
            "description": entry.description
        })
    result.data["skills"] = skills_data
    result.data["policy_identity"] = get_policy_identity()
    result.data["advanced_mode"] = bool(advanced)
    if starter:
        result.data["starter_mode"] = True
        result.data["starter_archetype"] = archetype if archetype in STARTER_ARCHETYPES else "general"
        result.data["starter_limit"] = max(1, int(limit))
    result.status = "success"
    return result


def skills_budget(repo_root: Path, default_max: int = 30) -> CallResult:
    """Run the default skill runtime-budget audit and return its JSON report."""
    result = CallResult()
    script_args = [
        "Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py",
        "--default-max",
        str(default_max),
        "--json",
    ]
    cmd = _get_python_command() + script_args

    def _run_budget(command: List[str]) -> tuple[Optional[subprocess.CompletedProcess[str]], Optional[OSError]]:
        try:
            process = subprocess.run(
                command,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return process, None
        except OSError as exc:
            return None, exc

    process, run_error = _run_budget(cmd)
    wrapper = Path(cmd[0]).name.lower() if cmd else ""
    should_retry_with_sys_python = (
        wrapper in {"uv", "mise"}
        and (
            run_error is not None
            or (process is not None and process.returncode != 0)
        )
    )
    if should_retry_with_sys_python:
        fallback_cmd = [sys.executable] + script_args
        fallback_process, fallback_error = _run_budget(fallback_cmd)
        if fallback_process is not None:
            process = fallback_process
            run_error = None
        elif process is None:
            run_error = fallback_error

    if process is None:
        error_detail = (
            f"Failed to execute runtime budget verifier: {run_error}"
            if run_error is not None
            else "Failed to execute runtime budget verifier."
        )
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message=error_detail,
                fix_suggestion="Ensure Python is available and rerun `ask skills budget`.",
            )
        )
        return result

    try:
        parsed_report = json.loads(process.stdout)
    except json.JSONDecodeError:
        parsed_report = {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
        }
    report = (
        parsed_report
        if isinstance(parsed_report, dict)
        else {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
            "parse_error": "verify_runtime_budget.py did not return a JSON object",
        }
    )

    result.data["runtime_budget"] = report
    result.status = "success" if process.returncode == 0 and report.get("status") == "pass" else "error"
    if result.status == "error":
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill runtime budget failed.",
                fix_suggestion="Reduce default-visible skills, hide bridge aliases under .system, or update the explicit budget with evidence.",
            )
        )
    return result


def skills_handles(
    repo_root: Path,
    check: bool = False,
    include_handles: bool = True,
    write_projection: bool = False,
    write_command_handle_files: bool = False,
    check_command_handle_files: bool = False,
    dry_run: bool = False,
) -> CallResult:
    """Return or validate the rooted command-handle surface."""
    result = CallResult()
    result.metadata["command"] = "skills handles"
    report = handles_report(repo_root_path=repo_root, include_handles=include_handles)
    result.data["command_surface"] = report
    result.data["handles"] = report["handles"]
    result.data["violations"] = report["violations"]
    result.data["policy_identity"] = report["policy_identity"]
    if write_projection:
        result.data["command_surface_projection_write"] = write_command_surface_projection(
            repo_root_path=repo_root,
            dry_run=dry_run,
        )
    if write_command_handle_files:
        result.data["command_handle_write"] = write_command_handles(
            repo_root_path=repo_root,
            dry_run=dry_run,
        )
    if check_command_handle_files:
        result.data["command_handle_check"] = check_command_handles(repo_root_path=repo_root)
    if check and report["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Command-handle validation failed.",
                fix_suggestion="Inspect data.violations, fix command-handle metadata, and rerun `ask skills handles --check --json`.",
            )
        )
    for key, message in (
        ("command_surface_projection_write", "Command-surface projection write failed."),
        ("command_handle_write", "Command-handle generation failed."),
        ("command_handle_check", "Command-handle validation failed."),
    ):
        payload = result.data.get(key)
        if payload and payload.get("status") != "pass":
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=message,
                    fix_suggestion="Inspect data.violations and data.command_handle_write.violations, then fix handle metadata or command-handle budgets.",
                )
            )
    return result


def skills_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one command-visible skill handle to its latent source module."""
    result = CallResult()
    result.metadata["command"] = "skills resolve"
    payload = resolve_skill_handle(handle, repo_root_path=repo_root)
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve skill handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def skills_parse(repo_root: Path, request_text: str) -> CallResult:
    """Parse a prompt for $ skill handles and @ reviewer handles, then resolve them."""
    result = CallResult()
    result.metadata["command"] = "skills parse"
    payload = parse_command_handles(request_text, repo_root_path=repo_root)
    result.data["parse"] = payload
    if payload.get("status") != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="One or more command handles in the prompt could not be resolved.",
                fix_suggestion="Inspect data.parse.unresolved, then rerun with valid $ skill and @ reviewer handles.",
            )
        )
    return result


def skills_proof(repo_root: Path, handle: str) -> CallResult:
    """Prove a command-visible skill handle reaches the workspace and user runtime surfaces."""
    result = CallResult()
    result.metadata["command"] = "skills proof"
    resolution = resolve_skill_handle(handle, repo_root_path=repo_root)
    normalized = resolution.get("handle", handle.lstrip("$"))
    handle_check = check_command_handles(repo_root_path=repo_root)
    workspace_handle = repo_root / str(resolution.get("command_handle_path", ""))
    user_codex_handle = Path.home() / ".codex" / "skills" / str(normalized) / "SKILL.md"
    user_agents_handle = Path.home() / ".agents" / "skills" / str(normalized) / "SKILL.md"
    codex_skills = Path.home() / ".codex" / "skills"
    agents_skills = Path.home() / ".agents" / "skills"
    expected_runtime = repo_root / ".agents" / "skills"

    handle_violations = [
        v for v in handle_check.get("violations", [])
        if v.get("handle") == normalized
    ]
    handle_check_ok = handle_check.get("status") == "pass" or not handle_violations

    def _link_payload(path: Path) -> dict[str, object]:
        payload: dict[str, object] = {
            "path": str(path),
            "exists": path.exists(),
            "is_symlink": path.is_symlink(),
        }
        if path.is_symlink():
            payload["target"] = str(path.resolve())
            payload["points_to_workspace_runtime"] = path.resolve() == expected_runtime.resolve()
        else:
            payload["target"] = None
            payload["points_to_workspace_runtime"] = False
        return payload

    gates = {
        "resolver": resolution.get("status") == "ok",
        "generated_command_handle_check": handle_check_ok,
        "workspace_command_handle_exists": workspace_handle.is_file(),
        "codex_user_link": codex_skills.is_symlink() and codex_skills.resolve() == expected_runtime.resolve(),
        "agents_user_link": agents_skills.is_symlink() and agents_skills.resolve() == expected_runtime.resolve(),
        "codex_user_command_handle_exists": user_codex_handle.is_file(),
        "agents_user_command_handle_exists": user_agents_handle.is_file(),
    }
    core_gates = (
        gates["resolver"],
        gates["generated_command_handle_check"],
        gates["workspace_command_handle_exists"],
    )
    user_runtime_ready = (
        (gates["codex_user_link"] and gates["codex_user_command_handle_exists"])
        or (gates["agents_user_link"] and gates["agents_user_command_handle_exists"])
    )
    proof = {
        "schema_version": "command-handle-proof.v1",
        "handle": normalized,
        "status": "pass" if all(core_gates) and user_runtime_ready else "fail",
        "gates": gates,
        "gate_policy": {
            "required": [
                "resolver",
                "generated_command_handle_check",
                "workspace_command_handle_exists",
            ],
            "user_runtime_any_of": [
                "codex_user_link",
                "agents_user_link",
            ],
        },
        "resolution": resolution,
        "command_handle_check": {
            key: value
            for key, value in handle_check.items()
            if key != "violations" or value
        },
        "workspace_runtime": {
            "path": str(expected_runtime),
            "command_handle_path": str(workspace_handle),
            "command_handle_exists": workspace_handle.is_file(),
        },
        "user_runtime_links": {
            "codex_skills": _link_payload(codex_skills),
            "agents_skills": _link_payload(agents_skills),
        },
        "user_runtime_command_handles": {
            "codex_handle": str(user_codex_handle),
            "codex_handle_exists": user_codex_handle.is_file(),
            "agents_handle": str(user_agents_handle),
            "agents_handle_exists": user_agents_handle.is_file(),
        },
        "live_codex_invocation": {
            "status": "manual_session_gate",
            "operator_action": "Open or reload a Codex session and verify the handle appears in the picker or can be invoked as a $ handle.",
        },
    }
    result.data["proof"] = proof
    if proof["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Command handle proof failed for '{normalized}'.",
                fix_suggestion="Run `./bin/ask skills sync --scope workspace --projection rooted`, then `./bin/ask skills sync --scope user --projection rooted`, and rerun proof.",
            )
        )
    return result


def reviewers_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one reviewer/subagent handle from the reviewer namespace."""
    result = CallResult()
    result.metadata["command"] = "reviewers resolve"
    payload = resolve_reviewer_handle(handle)
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve reviewer handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def init_skill(repo_root: Path, name: str, category: str, description: str) -> CallResult:
    """Initializes a new skill scaffold using the repo template logic."""
    result = CallResult()
    category_token = (category or "").strip()
    if not category_token:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category cannot be empty.",
                fix_suggestion="Use a category such as 'ui' or 'code_quality_review'.",
            )
        )
        return result
    if Path(category_token).is_absolute():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category must be repo-relative.",
                fix_suggestion="Use a category token such as 'ui' (not an absolute path).",
            )
        )
        return result

    if category_token.startswith("Skills/"):
        out_dir = repo_root / category_token
        category_rel = category_token
    else:
        out_dir = repo_root / "Skills" / category_token
        category_rel = f"Skills/{category_token}"
    try:
        out_dir.resolve().relative_to(repo_root.resolve())
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_PATH_TRAVERSAL",
                message=f"Category '{category}' escapes repository root.",
                fix_suggestion="Use a category path under Skills/.",
            )
        )
        return result

    init_skill_script = _resolve_skill_builder_script(repo_root, "init_skill")
    cmd = _get_python_command(["pyyaml"]) + [
        init_skill_script,
        name,
        "--path",
        str(out_dir),
        "--description", description,
        "--owner", "Agent Skills Kit",
        "--review-cadence", "quarterly",
        "--maturity", "experimental",
        "--lifecycle-state", "incubating"
    ]

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized skill '{name}' in '{category_rel}'"
        result.data["canonical_dest"] = category_rel
        result.metadata["next_steps"] = [f"ask skills audit {category_rel}/{name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))
        
    return result

def audit_skill(repo_root: Path, skill_path: str, level: str = "compat") -> CallResult:
    """
    Run structural and (optionally) strict security audits for a skill directory.
    
    Performs path containment validation for `skill_path`, runs structural diagnostics, and when `level` is `"strict"` runs additional validation gates (security gate, family benchmark validation and OpenClaw guard). Populates `result.data` with subprocess outputs under keys `"diagnostics"`, `"security_gate"`, `"family_benchmarks"` and `"openclaw_guard"` as applicable, and appends `ErrorObject`s to `result.errors` when validations fail.
    
    Parameters:
        repo_root (Path): Repository root against which `skill_path` is resolved.
        skill_path (str): Repository-relative path to the skill directory to audit.
        level (str): Validation level; `"compat"` runs structural diagnostics only, `"strict"` also runs security and benchmark guards.
    
    Returns:
        CallResult: Result with `status` set to `"success"` when diagnostics pass (and all strict checks pass if requested), or `"error"` with `errors` containing one or more `ErrorObject`s. Possible error codes include `ERR_PATH_TRAVERSAL` and `ERR_VALIDATION`.
    """
    result = CallResult()

    # Path traversal protection: resolve and verify path is within repo
    try:
        resolved_path = (repo_root / skill_path).resolve()
        resolved_root = repo_root.resolve()
        # Use is_relative_to for proper boundary check (not just string prefix)
        try:
            if not resolved_path.is_relative_to(resolved_root):
                result.status = "error"
                result.errors.append(ErrorObject(
                    code="ERR_PATH_TRAVERSAL",
                    message=f"Path traversal detected: '{skill_path}' resolves outside repository root.",
                    fix_suggestion="Use a relative path within the repository."
                ))
                return result
        except AttributeError:
            # Python <3.9 fallback: check path components
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                result.status = "error"
                result.errors.append(ErrorObject(
                    code="ERR_PATH_TRAVERSAL",
                    message=f"Path traversal detected: '{skill_path}' resolves outside repository root.",
                    fix_suggestion="Use a relative path within the repository."
                ))
                return result
    except Exception as e:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid path: {e}",
            fix_suggestion="Check the path format and try again."
        ))
        return result

    audit_target = Path(skill_path)
    if audit_target.name == "SKILL.md":
        audit_target = audit_target.parent
    audit_target_path = audit_target.as_posix()

    python = _get_python_command(["pyyaml", "jsonschema"])

    diag_cmd = python + ["Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py", skill_path]
    diag_proc = subprocess.run(diag_cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["diagnostics"] = {"exit_code": diag_proc.returncode, "stdout": diag_proc.stdout, "stderr": diag_proc.stderr}

    if level == "strict":
        # Security gate (skill_gate.py)
        gate_script = _resolve_skill_builder_script(repo_root, "skill_gate")
        gate_cmd = python + [gate_script, audit_target_path, "--require-security-evals", "--pi-high-fail", "--require-fail-fast"]
        gate_proc = subprocess.run(gate_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["security_gate"] = {"exit_code": gate_proc.returncode, "stdout": gate_proc.stdout, "stderr": gate_proc.stderr}
        if gate_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Security gate failed."))
            return result

        # Family benchmarks validation
        family_cmd = python + ["Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py", "--skill", audit_target_path]
        family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["family_benchmarks"] = {"exit_code": family_proc.returncode, "stdout": family_proc.stdout, "stderr": family_proc.stderr}
        if family_proc.returncode != 0:
            summary = _summarize_family_benchmark_failure(family_proc.stdout, family_proc.stderr)
            message = "Family benchmarks validation failed."
            if summary:
                message = f"{message} First failures: {summary}"
            quoted_skill_path = shlex.quote(audit_target_path)

            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=(
                    "Inspect data.family_benchmarks for full output, or run: "
                    f"mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py --skill {quoted_skill_path} --format text"
                ),
            ))
            return result

        # OpenClaw skill guard
        openclaw_script = _resolve_skill_builder_script(repo_root, "openclaw_skill_guard")
        openclaw_cmd = python + [openclaw_script, audit_target_path, "--mode", "both", "--format", "text"]
        openclaw_proc = subprocess.run(openclaw_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["openclaw_guard"] = {"exit_code": openclaw_proc.returncode, "stdout": openclaw_proc.stdout, "stderr": openclaw_proc.stderr}
        if openclaw_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="OpenClaw guard validation failed."))
            return result

    if diag_proc.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Structural diagnostics failed. Skill directory not found or invalid.",
            fix_suggestion=f"Ensure '{skill_path}' exists and contains a SKILL.md file."
        ))
        
    return result

def _resolve_canonical_install_dest(repo_root: Path, dest: str) -> tuple[Path, str]:
    """
    Resolve an install destination into an absolute repo path and a canonical repo-relative string.
    
    Parameters:
        repo_root (Path): Repository root directory against which `dest` is resolved.
        dest (str): User-supplied destination token (e.g. "github" or "backend"); empty values default to "github".
    
    Returns:
        tuple[Path, str]: A pair where the first element is the absolute resolved destination path inside `repo_root`
        and the second is the normalized repo-relative destination string.
    
    Raises:
        ValueError: If `dest` is an absolute path, if the resolved destination escapes the repository root,
        or if the repo-relative destination is empty or "." (must include a category directory).
    """
    dest_token = (dest or "Skills/github").strip() or "Skills/github"
    raw_dest = Path(dest_token)
    if raw_dest.is_absolute():
        raise ValueError("Destination must be repo-relative (for example: Skills/github or Skills/backend).")

    resolved_root = repo_root.resolve()
    resolved_dest = (repo_root / raw_dest).resolve()
    try:
        rel_dest = resolved_dest.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Destination escapes repository root.") from exc

    rel_parts = rel_dest.parts
    if len(rel_parts) == 1:
        rel_dest = Path("Skills") / rel_dest
        resolved_dest = (repo_root / rel_dest).resolve()
        rel_parts = rel_dest.parts
    rel_text = rel_dest.as_posix()
    if len(rel_parts) != 2 or rel_parts[0] != "Skills":
        raise ValueError("Destination must be under Skills/<category>.")
    if resolved_dest.exists() and not resolved_dest.is_dir():
        raise ValueError("Destination must resolve to a directory under repository root.")
    return resolved_dest, rel_text


def install_skill(repo_root: Path, url: str, remediate: bool = False, dest: str = "Skills/github", dry_run: bool = False) -> CallResult:
    """
    Install a GitHub-hosted skill into the repository's canonical skill directory.
    
    Dest is validated and normalised to a repo-relative category (for example "github" or "backend"). In dry-run mode no changes are made and a preview of the planned install is returned. If the installer supports `--validation-level` the command will request `compat` validation; if `--remediate` is requested but unsupported the call returns an error result. After a successful install the workspace projection is synchronised.
    
    Parameters:
        repo_root (Path): Root path of the repository used to resolve and validate the install destination.
        url (str): URL or repository path of the skill to install (may end with `.git`).
        remediate (bool): Request installer remediation; fails with `ERR_VALIDATION` if the installer does not support `--remediate`.
        dest (str): Repo-relative category directory for installation under Skills/ (must not be absolute or escape the repo).
        dry_run (bool): If true, return a preview without performing any filesystem or network changes.
    
    Returns:
        CallResult: Result object with `status` set to `"success"` or `"error"`. On success `data` includes at least:
            - `skill_name`: installed skill name,
            - `canonical_dest`: repo-relative destination used,
            - `workspace_sync`: status and logs from the post-install sync.
        On dry-run success `data` includes a preview (`dry_run`, `skill_name`, `target_path`, `url`, `remediate`, `canonical_dest`) and `metadata.next_steps` showing the equivalent install command.
        On error the result contains `errors` with codes such as `ERR_VALIDATION`, `ERR_CONFLICT`, or `ERR_RUNTIME` and a `fix_suggestion`.
    """
    result = CallResult()
    try:
        dest_path, dest_rel = _resolve_canonical_install_dest(repo_root, dest)
    except ValueError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid install destination '{dest}': {exc}",
                fix_suggestion="Use a category under Skills/ such as 'Skills/github' or shorthand 'github'.",
            )
        )
        return result

    # Parse skill name from URL for preview
    skill_name = url.split("/")[-1].replace(".git", "") if "/" in url else url
    target_path = dest_path / skill_name

    # Handle dry-run first (before any side-effect checks)
    if dry_run:
        # Preview mode: show what would happen without making changes
        result.status = "success"
        result.data["dry_run"] = True
        result.data["skill_name"] = skill_name
        # Handle absolute paths gracefully - only relativize if within repo
        try:
            display_path = str(target_path.relative_to(repo_root))
        except ValueError:
            display_path = str(target_path)
        result.data["target_path"] = display_path
        result.data["url"] = url
        result.data["remediate"] = remediate
        result.data["canonical_dest"] = dest_rel
        result.metadata["next_steps"] = [
            f"ask skills install {url} --dest {dest_rel}" + (" --remediate" if remediate else "")
        ]
        return result

    # Check for existing skill conflict (only for actual installation)
    if target_path.exists():
        # Handle absolute paths gracefully - only relativize if within repo
        try:
            display_path = str(target_path.relative_to(repo_root))
        except ValueError:
            display_path = str(target_path)
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_CONFLICT",
            message=f"Skill '{skill_name}' already exists at '{display_path}'.",
            fix_suggestion="Remove the existing skill or choose a different destination with --dest."
        ))
        result.data["skill_name"] = skill_name
        result.data["canonical_dest"] = dest_rel
        result.data["existing_path"] = display_path
        return result

    python_cmd = _get_python_command(["pyyaml"])
    installer_script = _resolve_skill_installer_script(repo_root)
    supported_flags = _install_script_supported_flags(repo_root, python_cmd)
    cmd = python_cmd + [
        installer_script,
        "--url", url,
        "--dest", str(dest_path),
    ]
    if "--validation-level" in supported_flags:
        cmd.extend(["--validation-level", "compat"])
        result.data["validation_level"] = "compat"
    else:
        result.data["validation_level"] = "compat_skipped_unsupported"

    if remediate:
        if "--remediate" in supported_flags:
            cmd.append("--remediate")
        else:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Installed skill installer does not support --remediate.",
                    fix_suggestion=(
                        "Re-run without --remediate, or update the installer to a version "
                        "that supports remediation."
                    ),
                )
            )
            return result

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr
    result.data["canonical_dest"] = dest_rel

    if process.returncode == 0:
        result.status = "success"
        match = re.search(r"Installed (.*?) to", process.stdout)
        installed_name = match.group(1) if match else skill_name
        result.data["skill_name"] = installed_name

        # Keep repo projections current so canonical install and loader symlinks
        # remain in lockstep.
        sync_result = sync_skills(repo_root, scope="workspace", dry_run=False)
        result.data["workspace_sync"] = {
            "status": sync_result.status,
            "logs": sync_result.data.get("logs", []),
        }
        if sync_result.status != "success":
            sync_error = sync_result.errors[0].message if sync_result.errors else "Unknown sync failure."
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Skill installed to '{dest_rel}', but workspace sync failed: {sync_error}",
                    fix_suggestion="Run `ask skills sync --scope workspace` after resolving the sync error.",
                )
            )
            return result
        result.metadata["next_steps"] = [f"ask skills audit {dest_rel}/{installed_name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Installation failed."))

    return result


def _install_script_supported_flags(repo_root: Path, python_cmd: List[str]) -> set[str]:
    """
    Identify which optional flags the installer script advertises in its help text.
    
    Parameters:
        repo_root (Path): Repository root used as the subprocess working directory.
        python_cmd (List[str]): Tokenised Python command to invoke the script (e.g. ["python3"] or a wrapper tool chain).
    
    Returns:
        supported (set[str]): Set containing any of `"--validation-level"` and `"--remediate"` that appear in the script's help output.
    """
    installer_script = _resolve_skill_installer_script(repo_root)
    help_cmd = python_cmd + [
        installer_script,
        "--help",
    ]
    try:
        process = subprocess.run(help_cmd, cwd=str(repo_root), capture_output=True, text=True)
    except OSError:
        return set()

    help_text = "\n".join([process.stdout or "", process.stderr or ""])
    supported = set()
    for flag in ("--validation-level", "--remediate"):
        if flag in help_text:
            supported.add(flag)
    return supported


def fold_skills(repo_root: Path, source: str, target: str, sensitivity: float = 0.2) -> CallResult:
    """
    Determine whether the source skill should be folded into the target skill based on description similarity.
    
    Parameters:
        repo_root (Path): Repository root used to load builder modules and the skill catalog.
        source (str): Name or trailing path segment identifying the source skill to evaluate.
        target (str): Name or trailing path segment identifying the target skill to compare against.
        sensitivity (float): Confidence threshold in the range 0–1 above which overlap is considered high (default 0.2).
    
    Returns:
        CallResult: Result object containing:
            - On success: `status == "success"`, `data["overlap_score"]` (float), and `data["recommendation"]`
              set to either a "KEEP" message or a "KEEP: No significant overlap found." message.
            - On redundancy detection: `status == "error"`, an `ERR_REDUNDANCY` error with a `fix_suggestion`,
              and `data["overlap_score"]`, `data["rationale"]`, and `data["recommendation"]` describing the overlap.
            - On missing dependencies: `status == "error"` with `ERR_DEPENDENCY`.
            - On missing skills: `status == "error"` with `ERR_VALIDATION`.
            - `data["rationale"]`, when present, contains the router's textual rationale for the match.
    """
    result = CallResult()
    
    builder_catalog = _load_builder_module(repo_root, "skill_catalog")
    router_mod = _load_builder_module(repo_root, "skill_router")
    
    if not builder_catalog or not router_mod:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_DEPENDENCY", message="Skill router or builder catalog not available."))
        return result

    catalog = builder_catalog.load_catalog(repo_root)
    source_skill = next((s for s in catalog.skills if s.name == source or str(s.skill_path).endswith(source)), None)
    target_skill = next((s for s in catalog.skills if s.name == target or str(s.skill_path).endswith(target)), None)

    if not source_skill or not target_skill:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Source or target skill not found."))
        return result

    # Run router check
    query = source_skill.description
    candidates, _ = router_mod.route(query, [target_skill], top_k=1)
    
    if candidates:
        match = candidates[0]
        result.data["overlap_score"] = match.confidence
        result.data["rationale"] = match.rationale

        if match.confidence >= sensitivity:
            # High overlap - emit CONFLICT to indicate redundancy issue
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_REDUNDANCY",
                message=f"High overlap ({int(match.confidence * 100)}%) detected between '{source}' and '{target}'.",
                fix_suggestion=f"Consider folding '{source}' into '{target}' to reduce redundancy."
            ))
            result.data["recommendation"] = f"FOLD: High overlap ({int(match.confidence * 100)}%) detected."
        else:
            result.status = "success"
            result.data["recommendation"] = f"KEEP: Low overlap ({int(match.confidence * 100)}%) detected."
    else:
        result.status = "success"
        result.data["overlap_score"] = 0
        result.data["recommendation"] = "KEEP: No significant overlap found."

    return result


def _scope_rank_for_path(skill_path: str) -> int:
    root = skill_path.split("/", 1)[0].strip()
    if root in REPO_SCAN_ROOTS:
        return REPO_SCAN_ROOTS.index(root) + 1
    return len(REPO_SCAN_ROOTS) + 1


def route_skills(
    repo_root: Path,
    request: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Route a textual request to candidate skills and produce a decision payload.
    
    Builds a set of eligible skills from the repository, ranks the best matches for the trimmed request using the skill router, evaluates catalog parity, and returns a CallResult containing the routing decision and related metadata.
    
    Parameters:
        repo_root (Path): Repository root used to discover canonical skill entries.
        request (str): Textual request to route; must be non-empty after trimming.
        top_k (int): Maximum number of top-ranked skills to return; values less than 1 are coerced to 1.
        considered_limit (int): Maximum number of candidate skills to consider when routing; values less than 1 are coerced to 1.
    
    Returns:
        CallResult: Result object whose `data` includes:
            - `decision`: decision payload produced by the routing logic.
            - `catalog_parity`: parity information comparing catalog and routing considerations.
            - `policy_identity`: policy identity used for the decision.
            - `decision_status`: the decision's status string.
        On error the CallResult will have `status == "error"` and `errors` will include one or more ErrorObject entries describing validation, dependency or runtime issues.
    """
    result = CallResult()
    query = request.strip()
    if not query:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Request cannot be empty for skills route.",
                fix_suggestion="Provide request text, for example: ask skills route \"review this PR\"",
            )
        )
        return result

    router_mod = _load_builder_module(repo_root, "skill_router")
    if not router_mod:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_DEPENDENCY",
                message="Skill router module is not available.",
                fix_suggestion=(
                    "Ensure Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/skill_router.py "
                    "exists and rerun."
                ),
            )
        )
        return result

    default_candidates: list[EligibleCandidate] = []
    default_candidate_ids: set[str] = set()
    for entry in discover_catalog_entries():
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = entry.source_dir.relative_to(repo_root).as_posix()
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(rel_path),
        )
        default_candidates.append(candidate)
        default_candidate_ids.add(candidate_id(candidate))

    advanced_only_candidates: list[EligibleCandidate] = []
    for entry in discover_catalog_entries(advanced=True):
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = entry.source_dir.relative_to(repo_root).as_posix()
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(rel_path),
        )
        if candidate_id(candidate) in default_candidate_ids:
            continue
        advanced_only_candidates.append(candidate)

    ordered_default_candidates = sorted(default_candidates, key=canonical_sort_key)
    bounded_limit = max(1, int(considered_limit))
    considered_candidates = ordered_default_candidates[:bounded_limit]
    considered_candidate_ids = {candidate_id(candidate) for candidate in considered_candidates}
    for candidate in sorted(advanced_only_candidates, key=canonical_sort_key):
        cid = candidate_id(candidate)
        if cid in considered_candidate_ids:
            continue
        considered_candidates.append(candidate)
        considered_candidate_ids.add(cid)
    router_skills = [
        _RouterSkill(name=item.name, description=item.description, skill_path=item.path)
        for item in considered_candidates
    ]

    ranked, uncertainty_reasons = router_mod.route(query, router_skills, top_k=max(1, int(top_k)))
    ranked_payload = [
        {
            "skill_name": candidate.skill_name,
            "skill_path": candidate.skill_path,
            "confidence": float(candidate.confidence),
            "rationale": list(candidate.rationale),
            "risk_tier": candidate.risk_tier,
        }
        for candidate in ranked
    ]

    catalog_parity = compute_catalog_parity(
        repo_root,
        strict=False,
    )

    decision = build_decision_payload(
        request=query,
        policy_identity=get_policy_identity(),
        considered_limit=len(considered_candidates),
        top_k=max(1, int(top_k)),
        eligible_candidates=considered_candidates,
        ranked_candidates=ranked_payload,
        uncertainty_reasons=list(uncertainty_reasons),
        catalog_parity_ok=not bool(catalog_parity.get("drift_detected")),
    )

    decision_status = decision["decision_status"]
    result.data["decision"] = decision
    result.data["catalog_parity"] = catalog_parity
    result.data["policy_identity"] = decision["policy_identity"]
    result.data["decision_status"] = decision_status

    if decision_status == "resolved":
        result.status = "success"
        return result

    failure_class = decision.get("failure_class")
    code = "ERR_VALIDATION"
    if failure_class == "AMBIGUITY_UNRESOLVED":
        code = "ERR_CONFLICT"
    elif failure_class == "DISCOVERY_POLICY_DRIFT":
        code = "ERR_DEPENDENCY"
    elif failure_class == "CATALOG_PARITY_DRIFT":
        code = "ERR_VALIDATION"

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code=code,
            message=f"skills route returned {decision_status}",
            fix_suggestion=decision.get("operator_action"),
        )
    )
    return result


def goal_skills(
    repo_root: Path,
    intent_text: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Builds a goal-oriented decision from an intent by routing the intent to skills and converting the resulting route decision into a goal decision.
    
    Parameters:
    	repo_root (Path): Repository root used to discover and route against skills.
    	intent_text (str): Natural-language intent to resolve into a goal decision.
    	top_k (int): Maximum number of top candidate skills to return from routing.
    	considered_limit (int): Number of skills to consider during routing.
    
    Returns:
    	CallResult: Contains:
    		- `data["goal_decision"]` (dict): The constructed goal decision payload.
    		- `data["decision_status"]` (str): Final goal decision status.
    		- `data["policy_identity"]` (dict): Policy identity associated with the decision.
    		- `data["route_decision_status"]` (optional[str]): Status of the underlying route decision.
    		On success (`decision_status == "resolved"`) the result.status is `"success"`. On failure the result.status is `"error"` and result.errors includes an ErrorObject with `code="ERR_VALIDATION"` and a `fix_suggestion` when available. If the routing step did not produce a decision payload the result.error contains an ErrorObject with `code="ERR_RUNTIME"`.
    """
    result = CallResult()
    route_result = route_skills(
        repo_root,
        request=intent_text,
        top_k=max(1, int(top_k)),
        considered_limit=max(1, int(considered_limit)),
    )
    route_decision = route_result.data.get("decision") if isinstance(route_result.data, dict) else None
    if not isinstance(route_decision, dict):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message="Route decision payload missing while building goal decision.",
                fix_suggestion="Retry `ask skills goal` after restoring route command health.",
            )
        )
        return result

    goal_decision = build_goal_decision(route_decision)
    result.data["goal_decision"] = goal_decision
    result.data["decision_status"] = goal_decision["decision_status"]
    result.data["policy_identity"] = goal_decision["policy_identity"]
    result.data["route_decision_status"] = route_decision.get("decision_status")

    if goal_decision["decision_status"] == "resolved":
        result.status = "success"
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=f"skills goal returned {goal_decision['decision_status']}",
            fix_suggestion=goal_decision.get("operator_action"),
        )
    )
    return result

def _create_symlink(source: Path, target: Path, dry_run: bool = False, *, replace_existing: bool = False) -> str:
    """
    Create or update a filesystem symbolic link at `target` that points to `source`.

    Ensures `target.parent` exists before creating the link. Existing non-symlink paths are preserved by default so user-owned directories like `~/plugins` are not deleted during relink.

    Parameters:
        source (Path): Destination path that the symlink should reference.
        target (Path): Filesystem path where the symlink will be created or updated.
        dry_run (bool): If True, do not perform filesystem mutations; only simulate the action.
        replace_existing (bool): If True, replace an existing non-symlink target before creating the symlink.

    Returns:
        action (str): Human-readable summary, e.g. "Created symlink: <target> -> <source>", "Updated symlink: <target> -> <source>", or "Skipped existing non-symlink path: <target>".
    """
    if target.exists() and not target.is_symlink() and not replace_existing:
        return f"Skipped existing non-symlink path: {target}"
    action = "Created" if not target.exists() else "Updated"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source)
    return f"{action} symlink: {target} -> {source}"

def _prune_first_level_symlinks(target_dir: Path, keep_names: set[str], dry_run: bool = False) -> list[str]:
    """
    Remove stale first-level symlinks in target_dir while preserving regular files, directories, hidden names, and any names listed in keep_names.
    
    Parameters:
        target_dir (Path): Directory whose immediate entries will be inspected.
        keep_names (set[str]): Entry names to skip (preserve) even if they are symlinks.
        dry_run (bool): If true, do not modify the filesystem; only report planned removals.
    
    Returns:
        list[str]: Log lines describing each removed (or planned-to-remove when dry_run) symlink in the form "Removed stale symlink: <path> -> <target>".
    """
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        # Preserve hidden control links (for example ".system") and managed links.
        if not item.is_symlink() or item.name in keep_names or item.name.startswith("."):
            continue
        logs.append(f"Removed stale symlink: {item} -> {os.readlink(item)}")
        if not dry_run:
            item.unlink()
    return logs

def _find_symlink_entries(source: Path) -> list[Path]:
    """
    Find symlinked filesystem entries at or below the given source path.
    
    If `source` is a symlink, returns a list containing only `source`. If `source`
    does not exist or is not a directory, returns an empty list. Otherwise walks
    the directory tree (without following symlinks) and returns any symlink paths
    found. Top-level traversal skips the `.git`, `node_modules`, and `__pycache__`
    subdirectories.
    
    Parameters:
        source (Path): Directory or path to inspect for symlink entries.
    
    Returns:
        list[Path]: A list of Path objects pointing to symlink entries; may be empty.
    """
    symlinks: list[Path] = []
    if source.is_symlink():
        symlinks.append(source)
        return symlinks
    if not source.exists() or not source.is_dir():
        return symlinks

    for root, dirs, files in os.walk(source, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in dirs + files:
            candidate = Path(root) / name
            if candidate.is_symlink():
                symlinks.append(candidate)
    return symlinks

def _sync_dir_copy(source: Path, target: Path, dry_run: bool = False) -> str:
    """
    Copy-sync a directory tree into a target directory while disallowing any symlinks in the source.
    
    Skips top-level entries named ".git", "node_modules", and "__pycache__". If any symlink is present anywhere under the source, raises ValueError. When not a dry run, ensures the target directory exists, replaces existing directories at the destination with fresh copies, and copies files preserving file metadata.
    
    Parameters:
        source (Path): Source directory to copy from. Must not contain symlinks.
        target (Path): Destination directory to copy into; will be created if missing.
        dry_run (bool): If True, perform no filesystem changes and only simulate the action.
    
    Returns:
        str: A human-readable message describing the completed sync and the target path.
    """
    symlink_entries = _find_symlink_entries(source)
    if symlink_entries:
        rel = symlink_entries[0]
        rel_text = str(rel.relative_to(source)) if rel != source else "."
        raise ValueError(f"Symlinks are not allowed in sync source: {source} (first: {rel_text})")

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.name in ('.git', 'node_modules', '__pycache__'):
                continue
            dest = target / item.name
            if item.is_symlink():
                raise ValueError(f"Symlink entries are not allowed in sync source: {item}")
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                # Preserve symlink objects defensively if one appears mid-copy.
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest, follow_symlinks=False)
    return f"Synced directory: {target} (copy)"


def _refresh_system_lane_link(
    skills_dir: Path,
    system_skills_dir: Path,
    dry_run: bool = False,
) -> list[str]:
    """
    Preserve or create the reserved `.system` symlink in the skills lane when a managed system store exists.
    
    Parameters:
        skills_dir (Path): Path to the repository skills directory where `.system` should exist.
        system_skills_dir (Path): Path to the managed system skills store; if not a directory, no action is taken.
        dry_run (bool): If true, no filesystem changes are made; actions are returned as planned-log strings.
    
    Returns:
        list[str]: Log lines describing the action taken (created/updated) or skipped; empty list if no managed system store is present.
    """
    if not system_skills_dir.is_dir():
        return []

    target_link = skills_dir / ".system"
    if target_link.exists() and not target_link.is_symlink():
        return [f"Skipped existing non-symlink system lane: {target_link}"]

    return [_create_symlink(Path("../../skills-system"), target_link, dry_run)]


def _is_generated_root_skill_dir(path: Path) -> bool:
    """Return whether a first-level runtime directory was generated by rooted projection."""
    skill_md = path / "SKILL.md"
    if not path.is_dir() or path.is_symlink() or not skill_md.is_file():
        return False
    try:
        head = skill_md.read_text(encoding="utf-8", errors="ignore")[:600]
    except OSError:
        return False
    return "skill-type: root-skill-set" in head and "projection-mode: rooted" in head


def _prune_generated_root_skill_dirs(target_dir: Path, keep_names: set[str], *, dry_run: bool = False) -> list[str]:
    """Remove generated rooted runtime directories that do not belong to the requested projection."""
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        if item.name.startswith(".") or item.name in keep_names:
            continue
        if not _is_generated_root_skill_dir(item):
            continue
        logs.append(f"Removed generated root skill set: {item}")
        if not dry_run:
            shutil.rmtree(item)
    return logs


def _public_root_report(report: dict) -> dict:
    return {
        **report,
        "roots": [
            {key: value for key, value in root.items() if key != "content"}
            for root in report.get("roots", [])
        ],
    }


def _public_manifest_report(report: dict) -> dict:
    return {
        **report,
        "manifests": [
            {key: value for key, value in manifest.items() if key != "rows"}
            for manifest in report.get("manifests", [])
        ],
    }


def _append_user_runtime_relinks(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    skills_dir: Path,
    *,
    dry_run: bool,
) -> None:
    home = Path.home()
    plugins_dir = repo_root / "Plugins"
    targets = [
        (skills_dir, home / ".agents" / "skills", True),
        (skills_dir, home / ".codex" / "skills", True),
        (repo_root, home / ".agents" / "agent-skills", True),
        (plugins_dir, home / ".agents" / "plugins", False),
    ]
    for src, dst, replace_existing in targets:
        plan["symlinks"].append({"from": str(dst), "to": str(src)})
        logs.append(_create_symlink(src, dst, dry_run, replace_existing=replace_existing))
    _refresh_home_plugin_mirrors(plan, logs, repo_root, home / "plugins", dry_run=dry_run)


def _ensure_real_plugin_mirror_root(target: Path, canonical_plugins_dir: Path, dry_run: bool) -> str:
    """Ensure a home plugin mirror root is a real directory, not a repo-backed symlink."""
    canonical_real = canonical_plugins_dir.resolve()
    if target.is_symlink():
        try:
            link_real = target.resolve()
        except OSError:
            link_real = None
        if link_real == canonical_real or (link_real and canonical_real in link_real.parents):
            if not dry_run:
                target.unlink()
                target.mkdir(parents=True, exist_ok=True)
            return f"Replaced repo-backed plugin mirror symlink with directory: {target}"
        return f"Skipped non-repo plugin mirror symlink: {target}"
    if target.exists() and not target.is_dir():
        return f"Skipped non-directory plugin mirror path: {target}"
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    return f"Ensured plugin mirror directory: {target}"


def _refresh_home_plugin_mirrors(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    home_plugins_dir: Path,
    *,
    dry_run: bool,
) -> None:
    """
    Replace managed home plugin mirror copies from canonical Plugins/ sources.

    `~/.agents/plugins` is the live symlink to the canonical source tree. `~/plugins`
    is a materialized runtime mirror so marketplace paths like `./Plugins/<name>`
    remain resolvable without aliasing the repo. Every user sync refreshes listed
    local plugins from `Plugins/marketplace.json`, so plugin edits and updates
    replace stale runtime copies.
    """
    plugins_dir = repo_root / "Plugins"
    mirror_plan = {
        "from": str(plugins_dir),
        "to": str(home_plugins_dir),
        "mode": "copy-replace",
        "trigger": "refresh after canonical Plugins/ or Plugins/marketplace.json changes",
        "plugins": [],
    }
    plan.setdefault("runtime_plugin_mirrors", []).append(mirror_plan)
    root_log = _ensure_real_plugin_mirror_root(home_plugins_dir, plugins_dir, dry_run)
    logs.append(root_log)
    if root_log.startswith("Skipped"):
        return

    try:
        _marketplace_path, entries = _load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        logs.append(f"Skipped home plugin mirror refresh: {exc}")
        return

    marker_name = ".codex-repo-plugin-source"
    keep_names = {entry["name"] for entry in entries}
    for entry in entries:
        plugin_name = entry["name"]
        relative = entry["path"]
        source_dir = repo_root / relative.removeprefix("./")
        target_dir = home_plugins_dir / plugin_name
        mirror_plan["plugins"].append({
            "name": plugin_name,
            "source": str(source_dir),
            "target": str(target_dir),
        })
        if not source_dir.is_dir():
            logs.append(f"Skipped missing home plugin mirror source: {source_dir}")
            continue
        if dry_run:
            logs.append(f"Would replace home plugin mirror: {target_dir} <- {source_dir}")
            continue
        if target_dir.is_symlink() or target_dir.is_file():
            target_dir.unlink()
        elif target_dir.exists():
            shutil.rmtree(target_dir)
        _copy_directory_contents(source_dir, target_dir)
        _materialize_first_level_skill_aliases(target_dir)
        (target_dir / marker_name).write_text(str(source_dir.resolve()) + "\n", encoding="utf-8")
        logs.append(f"Replaced home plugin mirror: {target_dir} <- {source_dir}")

    # Prune stale home plugin mirrors that are no longer declared in the marketplace.
    reserved = {"marketplace.json", "cache"}
    if home_plugins_dir.is_dir():
        for child in home_plugins_dir.iterdir():
            if child.name in keep_names or child.name in reserved:
                continue
            if not child.is_dir():
                continue
            marker_file = child / marker_name
            if not marker_file.is_file():
                continue
            if dry_run:
                logs.append(f"Would remove stale home plugin mirror: {child}")
                continue
            if child.is_symlink():
                child.unlink()
            else:
                shutil.rmtree(child)
            logs.append(f"Removed stale home plugin mirror: {child}")


def _sync_rooted_projection(
    repo_root: Path,
    *,
    dry_run: bool,
    plan: dict,
    logs: list[str],
    skills_dir: Path,
    system_skills_dir: Path,
) -> tuple[bool, list[ErrorObject]]:
    """Generate the rooted runtime projection and latent manifests."""
    root_report = build_roots(skills_dir)
    manifest_report = build_manifest_report(repo_root / ".skillsets")
    command_surface_write = write_command_surface_projection(repo_root_path=repo_root, dry_run=True)
    command_handle_write = write_command_handles(repo_root_path=repo_root, dry_run=True)
    plan["root_skill_sets"] = _public_root_report(root_report)
    plan["skillset_manifests"] = _public_manifest_report(manifest_report)
    plan["command_surface"] = command_surface_write
    plan["command_handles"] = {
        key: value
        for key, value in command_handle_write.items()
        if key != "writes"
    }
    plan["unmapped_entries"] = root_report.get("unmapped", [])

    violations = [
        *root_report.get("violations", []),
        *manifest_report.get("violations", []),
        *command_surface_write.get("violations", []),
        *command_handle_write.get("violations", []),
    ]
    plan["violations"] = violations
    if (
        root_report.get("status") != "pass"
        or manifest_report.get("status") != "pass"
        or command_surface_write.get("status") != "pass"
        or command_handle_write.get("status") != "pass"
    ):
        plan["validation_status"] = "fail"
        plan["warnings"].extend([str(violation.get("code", violation)) for violation in violations])
        return False, [ErrorObject(
            code="ERR_VALIDATION",
            message="Rooted projection validation failed before mutation.",
            fix_suggestion="Inspect plan.violations and rerun `bin/ask skills sync --projection rooted --dry-run --json`.",
        )]

    keep_names = {root["name"] for root in root_report.get("roots", [])}
    keep_names.add("codex-primary-runtime")
    if system_skills_dir.is_dir():
        keep_names.add(".system")

    for root in root_report.get("roots", []):
        plan["writes"].append(root["path"])
    for manifest in manifest_report.get("manifests", []):
        plan["writes"].append(manifest["path"])
    plan["writes"].append(command_surface_write["path"])
    plan["writes"].extend(row["path"] for row in command_handle_write.get("writes", []))

    if dry_run:
        logs.append("Dry-run rooted projection: root skills and manifests validated without mutation.")
        for log in prune_unowned_skillset_files(repo_root / ".skillsets", dry_run=True):
            plan["deletes"].append(log)
            logs.append(f"Dry-run {log}")
    else:
        try:
            pre_prune_logs = _prune_first_level_symlinks(skills_dir, keep_names, dry_run)
            pre_prune_logs.extend(_prune_generated_root_skill_dirs(skills_dir, keep_names, dry_run=dry_run))
            prune_logs = prune_unowned_skillset_files(repo_root / ".skillsets", dry_run)
            root_writes = write_roots(root_report, skills_dir, repo_root_path=repo_root)
            manifest_writes = write_manifests(manifest_report, repo_root / ".skillsets")
            command_surface_write = write_command_surface_projection(repo_root_path=repo_root, dry_run=False)
            command_handle_write = write_command_handles(repo_root_path=repo_root, dry_run=False)
        except (OSError, ValueError) as exc:
            plan["validation_status"] = "fail"
            plan["warnings"].append("ROOTED_PROJECTION_WRITE_FAILED")
            return False, [ErrorObject(
                code="ERR_RUNTIME",
                message=f"Rooted projection write failed: {exc}",
                fix_suggestion="Check filesystem permissions and rerun rooted sync.",
            )]
        for log in pre_prune_logs:
            plan["deletes"].append(log)
            logs.append(log)
        logs.extend(f"Wrote rooted projection file: {item['path']}" for item in root_writes)
        logs.extend(f"Wrote skill-set manifest: {item['path']} ({item['count']} rows)" for item in manifest_writes)
        logs.append(f"Wrote command-surface projection: {command_surface_write['path']}")
        logs.append(
            "Wrote generated command handles: "
            f"{command_handle_write['command_handle_count']} handles ({command_handle_write['write_count']} files)"
        )
        for log in prune_logs:
            plan["deletes"].append(log)
            logs.append(log)

    try:
        for log in _prune_first_level_symlinks(skills_dir, keep_names, dry_run):
            plan["deletes"].append(log)
            logs.append(log)
        for log in _prune_generated_root_skill_dirs(skills_dir, keep_names, dry_run=dry_run):
            plan["deletes"].append(log)
            logs.append(log)
    except OSError as exc:
        plan["validation_status"] = "fail"
        plan["warnings"].append("RUNTIME_PROJECTION_MUTATION_FAILED")
        return False, [ErrorObject(
            code="ERR_RUNTIME",
            message=f"Rooted projection could not update {skills_dir}: {exc}",
            fix_suggestion="Check filesystem permissions on .agents/skills or rerun with --dry-run.",
        )]

    system_lane_logs = _refresh_system_lane_link(skills_dir, system_skills_dir, dry_run)
    if system_lane_logs:
        plan["symlinks"].append({"from": str(skills_dir / ".system"), "to": "../../skills-system"})
        logs.extend(system_lane_logs)
    plan["validation_status"] = "pass"
    return True, []


def sync_skills(
    repo_root: Path,
    scope: str = "workspace",
    dry_run: bool = False,
    projection: Optional[str] = None,
) -> CallResult:
    """
    Synchronizes derived skill views for either the repository workspace or the user environment.
    
    For scope="workspace" this prunes stale first-level symlinks under .agents/skills, recreates symlinks for repository-owned skills, preserves a .system bridge when present, and refreshes catalog projections (SKILL.md and README.md). For scope="user" this creates user-facing symlinks from the repo workspace.
    
    Parameters:
        repo_root (Path): Root path of the repository containing skills directories.
        scope (str): Either "workspace" to sync repository-derived views or "user" to populate user-local locations.
        dry_run (bool): If True, no filesystem mutations are performed; actions are reported only.
        projection (Optional[str]): Explicit runtime projection mode. When omitted,
            SYNC_SKILLS_PROJECTION_MODE is honored before the flat default.
    
    Returns:
        CallResult: Success result contains a `data` object with:
          - plan: dict with lists for "writes", "deletes", and "symlinks" describing intended changes,
          - logs: list of human-readable action logs,
          - policy_identity: identity info from get_policy_identity().
        On error, the result will have status "error" and one or more ErrorObject entries:
          - ERR_INVALID_SCOPE when `scope` is not "workspace" or "user".
          - ERR_VALIDATION when inputs contain disallowed symlinks or other validation failures.
          - Other errors may be returned for copy/sync failures (e.g., when `_sync_dir_copy` detects symlinks).
    """
    result = CallResult()
    try:
        projection_decision = normalize_projection_mode(projection)
    except ProjectionModeError as exc:
        resolved_mode = getattr(exc, "resolved_mode", None)
        fix_suggestions = {
            "ERR_INVALID_PROJECTION_MODE": "Choose a supported projection mode such as --projection flat or --projection rooted.",
            "ERR_DEFERRED_PROJECTION_MODE": "Use --projection flat or --projection rooted until the deferred projection mode is available.",
        }
        result.status = "error"
        result.errors.append(ErrorObject(
            code=exc.code,
            message=exc.message,
            fix_suggestion=fix_suggestions.get(exc.code, "Choose a supported projection mode or rerun with --dry-run."),
        ))
        result.data["projection_mode"] = resolved_mode
        result.data["requested_projection_mode"] = getattr(exc, "requested_mode", projection or "")
        return result

    if scope not in {"workspace", "user"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_INVALID_SCOPE",
            message=f"Invalid scope: '{scope}'. Must be 'workspace' or 'user'.",
            fix_suggestion="Use --scope workspace or --scope user"
        ))
        return result

    plan = {
        "writes": [],
        "deletes": [],
        "symlinks": [],
        "system_bridge_skill_names": sorted(SYSTEM_BRIDGE_SKILL_NAMES),
        "preserved_bridge_lane_entries": [],
        "preserved_system_lane_entries": [],
        "validation_status": "not_run",
        "unmapped_entries": [],
        "violations": [],
        "mutation_counts": {
            "writes": 0,
            "deletes": 0,
            "symlinks": 0,
        },
        "warnings": [],
    }
    logs = []
    skills_dir = repo_root / ".agents" / "skills"
    system_skills_dir = repo_root / "skills-system"

    if system_skills_dir.is_dir():
        plan["preserved_system_lane_entries"] = sorted(
            item.name
            for item in system_skills_dir.iterdir()
            if item.is_dir() and (item / "SKILL.md").exists()
        )

    if projection_decision.projection_mode == "rooted":
        if scope == "user":
            violations = validate_workspace_runtime(skills_dir, repo_root_path=repo_root)
            plan["violations"] = violations
            if violations:
                plan["validation_status"] = "fail"
                plan["warnings"].extend(str(violation.get("code", violation)) for violation in violations)
                result.status = "error"
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message="Rooted workspace validation failed before user relink.",
                    fix_suggestion="Run `bin/ask skills sync --scope workspace --projection rooted` before user relink.",
                ))
                result.data["plan"] = plan
                result.data["logs"] = logs
                result.data["policy_identity"] = get_policy_identity()
                result.data["projection_mode"] = projection_decision.projection_mode
                return result
            _append_user_runtime_relinks(plan, logs, repo_root, skills_dir, dry_run=dry_run)
            plan["validation_status"] = "pass"
            plan["mutation_counts"] = {
                "writes": len(plan["writes"]),
                "deletes": len(plan["deletes"]),
                "symlinks": len(plan["symlinks"]),
            }
            result.data["plan"] = plan
            result.data["logs"] = logs
            result.data["policy_identity"] = get_policy_identity()
            result.data["projection_mode"] = projection_decision.projection_mode
            result.data["projection"] = build_projection_plan_metadata(
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                warnings=plan["warnings"],
            )
            result.status = "success"
            return result
        ok, errors = _sync_rooted_projection(
            repo_root,
            dry_run=dry_run,
            plan=plan,
            logs=logs,
            skills_dir=skills_dir,
            system_skills_dir=system_skills_dir,
        )
        if not ok:
            result.status = "error"
            result.errors.extend(errors)
            result.data["plan"] = plan
            result.data["logs"] = logs
            result.data["policy_identity"] = get_policy_identity()
            result.data["projection_mode"] = projection_decision.projection_mode
            result.data["projection"] = build_projection_plan_metadata(
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                warnings=plan["warnings"],
            )
            return result
        projection_logs = _refresh_catalog_projections(repo_root, dry_run)
        plan["writes"].extend([str(repo_root / "SKILL.md"), str(repo_root / "README.md")])
        logs.extend(projection_logs)
        plan["mutation_counts"] = {
            "writes": len(plan["writes"]),
            "deletes": len(plan["deletes"]),
            "symlinks": len(plan["symlinks"]),
        }
        result.data["plan"] = plan
        result.data["logs"] = logs
        result.data["policy_identity"] = get_policy_identity()
        result.data["projection_mode"] = projection_decision.projection_mode
        result.data["projection"] = build_projection_plan_metadata(
            projection_decision,
            scope=scope,
            dry_run=dry_run,
            warnings=plan["warnings"],
        )
        result.status = "success"
        return result

    entries = discover_skill_entries(source="repo")
    if scope == "workspace":
        plan["preserved_bridge_lane_entries"] = sorted(SYSTEM_BRIDGE_SKILL_NAMES)
        keep_names = {entry.name for entry in entries if entry.source_dir.is_relative_to(repo_root)}
        if system_skills_dir.is_dir():
            keep_names.add(".system")
        for log in _prune_first_level_symlinks(skills_dir, keep_names, dry_run):
            plan["deletes"].append(log)
            logs.append(log)
        for log in _prune_generated_root_skill_dirs(skills_dir, keep_names, dry_run=dry_run):
            plan["deletes"].append(log)
            logs.append(log)
        for entry in entries:
            skill_name = entry.name
            target_link = skills_dir / skill_name
            if not entry.source_dir.is_relative_to(repo_root):
                continue
            rel_to_root = entry.source_dir.relative_to(repo_root)
            source_rel = os.path.join("../..", str(rel_to_root))
            plan["symlinks"].append({"from": str(target_link), "to": source_rel})
            logs.append(_create_symlink(Path(source_rel), target_link, dry_run))
        system_lane_logs = _refresh_system_lane_link(skills_dir, system_skills_dir, dry_run)
        if system_lane_logs:
            plan["symlinks"].append({"from": str(skills_dir / ".system"), "to": "../../skills-system"})
            logs.extend(system_lane_logs)
        projection_logs = _refresh_catalog_projections(repo_root, dry_run)
        plan["writes"].extend([str(repo_root / "SKILL.md"), str(repo_root / "README.md")])
        logs.extend(projection_logs)
    elif scope == "user":
        _append_user_runtime_relinks(plan, logs, repo_root, skills_dir, dry_run=dry_run)
    plan["validation_status"] = "pass"
    plan["mutation_counts"] = {
        "writes": len(plan["writes"]),
        "deletes": len(plan["deletes"]),
        "symlinks": len(plan["symlinks"]),
    }
    result.data["plan"] = plan
    result.data["logs"] = logs
    result.data["policy_identity"] = get_policy_identity()
    result.data["projection_mode"] = projection_decision.projection_mode
    result.data["projection"] = build_projection_plan_metadata(
        projection_decision,
        scope=scope,
        dry_run=dry_run,
        warnings=plan["warnings"],
    )
    result.status = "success"
    return result
