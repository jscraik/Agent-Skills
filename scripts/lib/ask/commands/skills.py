import os
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

from ask.envelope import CallResult, ErrorObject
from skill_discovery import discover_skill_entries, get_policy_identity
from selection_policy import REPO_SCAN_ROOTS
from ask.catalog_parity import compute_catalog_parity
from ask.selection_contract import (
    EligibleCandidate,
    build_decision_payload,
    build_goal_decision,
    canonical_sort_key,
)


def _get_python_command(with_packages: Optional[List[str]] = None) -> List[str]:
    """
    Constructs a platform-appropriate Python invocation command prioritising uv/mise wrappers when available.
    
    The returned command is chosen with this observable precedence: a non-empty PYTHON_BIN environment value, a `mise`+`uv` wrapper, an `uv` wrapper, a user virtualenv at `~/.venvs/pyyaml/bin/python`, then the system `python3`.
    
    Parameters:
        with_packages (Optional[List[str]]): Optional iterable of package names to request via `--with` when using a wrapper that accepts package flags; falsy entries are ignored.
    
    Returns:
        List[str]: Tokenised command suitable for subprocess invocation to run Python.
    """
    configured = os.environ.get("PYTHON_BIN", "").strip()
    if configured:
        return shlex.split(configured)

    packages = [pkg for pkg in (with_packages or []) if pkg]

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

    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if preferred.exists():
        return [str(preferred)]
    return ["python3"]


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
        "ce-brainstorm",
        "ce-spec",
        "ce-plan",
        "ce-work",
        "ce-technical-review",
        "gh-workflow",
        "docs-expert",
        "context7",
    ),
    "delivery": ("ce-plan", "ce-work", "ce-review", "gh-workflow", "coding-harness"),
    "review": ("ce-technical-review", "ce-review", "agent-native-audit", "security-best-practices"),
    "docs": ("agents-md", "docs-expert", "context7", "openai-docs"),
}

# Explicitly load builder-specific logic using absolute paths to avoid namespace collisions
def _load_builder_module(repo_root: Path, module_name: str):
    """
    Load a skill-builder script from the repository and return it as an imported module.
    
    Parameters:
        repo_root (Path): Repository root used to locate `utilities/skill-builder/scripts/<module_name>.py`.
        module_name (str): Script base name (without `.py`) to load.
    
    Returns:
        module (types.ModuleType | None): The imported module object if the script exists and is loaded, `None` otherwise.
    """
    module_path = repo_root / "utilities" / "skill-builder" / "scripts" / f"{module_name}.py"
    if not module_path.exists():
        return None

    internal_name = f"ask_builder_{module_name}"
    if internal_name in sys.modules:
        return sys.modules[internal_name]

    spec = importlib.util.spec_from_file_location(internal_name, str(module_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[internal_name] = mod # Register BEFORE exec
        spec.loader.exec_module(mod)
        return mod
    return None

def _canonical_entries(repo_root: Path) -> list:
    """
    Return skill entries whose source directory is inside the repository root.
    
    Parameters:
    	repo_root (Path): Repository root used to filter discovered skill entries.
    
    Returns:
    	entries (list): List of discovered skill entries whose `source_dir` is relative to `repo_root`.
    """
    return [
        entry
        for entry in discover_skill_entries(source="repo")
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


def list_skills(
    repo_root: Path,
    category: Optional[str] = None,
    *,
    starter: bool = False,
    archetype: str = "general",
    limit: int = 12,
) -> CallResult:
    """
    Return a listing of skills in the repository, optionally filtered or reduced to a deterministic "starter" subset.
    
    Parameters:
    	repo_root (Path): Root path of the repository to discover skills from; entries outside this root are excluded.
    	category (Optional[str]): Case-insensitive substring filter applied to each skill's category; omit to include all.
    	starter (bool): When true, return a deterministic, archetype-ordered subset of skills instead of the full set.
    	archetype (str): Archetype key to select starter skills from; falls back to "general" when unknown.
    	limit (int): Maximum number of skills to return when `starter` is true; coerced to at least 1.
    
    Returns:
    	CallResult: Result with `status == "success"` and `data` containing:
    		- "skills": list of objects with keys `name`, `path` (repository-relative when possible), `category`, `description`
    		- "policy_identity": current policy identity string
    		- When `starter` is true, also includes:
    			- "starter_mode": true
    			- "starter_archetype": resolved archetype key
    			- "starter_limit": effective integer limit
    """
    result = CallResult()
    entries = _canonical_entries(repo_root)
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
    if starter:
        result.data["starter_mode"] = True
        result.data["starter_archetype"] = archetype if archetype in STARTER_ARCHETYPES else "general"
        result.data["starter_limit"] = max(1, int(limit))
    result.status = "success"
    return result

def init_skill(repo_root: Path, name: str, category: str, description: str) -> CallResult:
    """Initializes a new skill scaffold using the repo template logic."""
    result = CallResult()

    cmd = _get_python_command(["pyyaml"]) + [
        "utilities/skill-builder/scripts/init_skill.py",
        name,
        "--category", category,
        "--description", description,
        "--owner", "Agent Skills Kit",
        "--review-cadence", "quarterly",
        "--maturity", "experimental",
        "--lifecycle-state", "incubating"
    ]

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized skill '{name}' in '{category}'"
        result.metadata["next_steps"] = [f"ask skills audit {category}/{name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))
        
    return result

def audit_skill(repo_root: Path, skill_path: str, level: str = "compat") -> CallResult:
    """Runs structural and security audits on a skill."""
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

    python = _get_python_command(["pyyaml", "jsonschema"])

    diag_cmd = python + ["scripts/diagnose_skill.py", skill_path]
    diag_proc = subprocess.run(diag_cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["diagnostics"] = {"exit_code": diag_proc.returncode, "stdout": diag_proc.stdout, "stderr": diag_proc.stderr}

    if level == "strict":
        # Security gate (skill_gate.py)
        gate_cmd = python + ["utilities/skill-builder/scripts/skill_gate.py", skill_path, "--require-security-evals", "--pi-high-fail", "--require-fail-fast"]
        gate_proc = subprocess.run(gate_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["security_gate"] = {"exit_code": gate_proc.returncode, "stdout": gate_proc.stdout, "stderr": gate_proc.stderr}
        if gate_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Security gate failed."))
            return result

        # Family benchmarks validation
        family_cmd = python + ["scripts/validate_skill_authoring_family_benchmarks.py", "--skill", skill_path]
        family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["family_benchmarks"] = {"exit_code": family_proc.returncode, "stdout": family_proc.stdout, "stderr": family_proc.stderr}
        if family_proc.returncode != 0:
            summary = _summarize_family_benchmark_failure(family_proc.stdout, family_proc.stderr)
            message = "Family benchmarks validation failed."
            if summary:
                message = f"{message} First failures: {summary}"
            quoted_skill_path = shlex.quote(skill_path)

            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=(
                    "Inspect data.family_benchmarks for full output, or run: "
                    f"mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python scripts/validate_skill_authoring_family_benchmarks.py --skill {quoted_skill_path} --format text"
                ),
            ))
            return result

        # OpenClaw skill guard
        openclaw_cmd = python + ["utilities/skill-builder/scripts/openclaw_skill_guard.py", skill_path, "--mode", "both", "--format", "text"]
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

def install_skill(repo_root: Path, url: str, remediate: bool = False, dest: str = "github", dry_run: bool = False) -> CallResult:
    """Installs a skill from GitHub, wrapping the hardened installer script."""
    result = CallResult()
    dest_path = repo_root / dest

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
        result.metadata["next_steps"] = [
            f"ask skills install {url} --dest {dest}" + (" --remediate" if remediate else "")
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
        result.data["existing_path"] = display_path
        return result

    cmd = _get_python_command(["pyyaml"]) + [
        "skills-system/skill-installer/scripts/install-skill-from-github.py",
        "--url", url,
        "--dest", str(dest_path),
        "--validation-level", "compat"
    ]

    if remediate:
        cmd.append("--remediate")

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr

    if process.returncode == 0:
        result.status = "success"
        match = re.search(r"Installed (.*?) to", process.stdout)
        if match:
            result.data["skill_name"] = match.group(1)
            result.metadata["next_steps"] = [f"ask skills audit {dest}/{match.group(1)} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Installation failed."))

    return result

def fold_skills(repo_root: Path, source: str, target: str, sensitivity: float = 0.2) -> CallResult:
    """Calculates functional similarity and suggests folding source into target."""
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
    Route a textual request to ranked skill candidates and build a decision payload.
    
    Parameters:
        repo_root (Path): Repository root used to discover canonical skill entries.
        request (str): Textual request to route; must be non-empty after trimming.
        top_k (int): Number of top-ranked skills to return (bounded to at least 1).
        considered_limit (int): Maximum number of candidate skills to consider when routing (bounded to at least 1).
    
    Returns:
        CallResult: Result object whose `data` contains:
            - `decision`: the decision payload produced by the routing logic.
            - `catalog_parity`: parity information comparing catalog and routing considerations.
            - `policy_identity`: policy identity used for the decision.
            - `decision_status`: the decision's status string.
        On error, `status` will be "error" and `errors` will include one or more `ErrorObject` entries describing validation, dependency or runtime issues.
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
                fix_suggestion="Ensure utilities/skill-builder/scripts/skill_router.py exists and rerun.",
            )
        )
        return result

    eligible_candidates: list[EligibleCandidate] = []
    for entry in _canonical_entries(repo_root):
        rel_path = entry.source_dir.relative_to(repo_root).as_posix()
        eligible_candidates.append(
            EligibleCandidate(
                name=entry.name,
                path=rel_path,
                description=entry.description,
                scope_rank=_scope_rank_for_path(rel_path),
            )
        )

    ordered_candidates = sorted(eligible_candidates, key=canonical_sort_key)
    bounded_limit = max(1, int(considered_limit))
    considered_candidates = ordered_candidates[:bounded_limit]
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
        skills_list_count=len(_canonical_entries(repo_root)),
        route_considered_total=len(ordered_candidates),
    )

    decision = build_decision_payload(
        request=query,
        policy_identity=get_policy_identity(),
        considered_limit=bounded_limit,
        top_k=max(1, int(top_k)),
        eligible_candidates=ordered_candidates,
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

def _create_symlink(source: Path, target: Path, dry_run: bool = False) -> str:
    """
    Create or update a symbolic link at `target` that points to `source`.
    
    Ensures `target.parent` exists. If `target` already exists and is a directory (and not a symlink) it is removed; otherwise the existing file or symlink is unlinked before creating the new link. When `dry_run` is True no filesystem mutations are performed.
    
    Parameters:
        source (Path): Path the new symlink should point to.
        target (Path): Path at which to create or update the symlink.
        dry_run (bool): If True, do not modify the filesystem; only simulate the action.
    
    Returns:
        str: Human-readable action summary, e.g. "Created symlink: <target> -> <source>" or "Updated symlink: <target> -> <source>".
    """
    action = "Created" if not target.exists() else "Updated"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source)
    return f"{action} symlink: {target} -> {source}"

def _find_symlink_entries(source: Path) -> list[Path]:
    """Return symlink entries under source (including source itself)."""
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
    """Sync directory via copy (rsync-like)."""
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

def sync_skills(repo_root: Path, scope: str = "workspace", dry_run: bool = False) -> CallResult:
    result = CallResult()
    plan = {"writes": [], "deletes": [], "symlinks": []}
    logs = []
    skills_dir = repo_root / ".agents" / "skills"
    antigravity_skills_dir = repo_root / "skills-antigravity"
    entries = discover_skill_entries(source="repo")
    if scope == "workspace":
        for entry in entries:
            skill_name = entry.name
            target_link = skills_dir / skill_name
            if not entry.source_dir.is_relative_to(repo_root):
                continue
            rel_to_root = entry.source_dir.relative_to(repo_root)
            source_rel = os.path.join("../..", str(rel_to_root))
            plan["symlinks"].append({"from": str(target_link), "to": source_rel})
            logs.append(_create_symlink(Path(source_rel), target_link, dry_run))
    elif scope == "user":
        home = Path.home()
        # Guard: antigravity source directory must exist before any mutations
        if not antigravity_skills_dir.exists():
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message=f"Antigravity skills directory not found: {antigravity_skills_dir}",
                fix_suggestion="Ensure the skills-antigravity directory exists or use --scope workspace"
            ))
            return result
        if antigravity_skills_dir.is_symlink():
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=f"Refusing to sync from symlinked antigravity directory: {antigravity_skills_dir}",
                fix_suggestion="Replace skills-antigravity symlink with a real directory before running user scope sync."
            ))
            return result
        symlink_entries = _find_symlink_entries(antigravity_skills_dir)
        if symlink_entries:
            rel = str(symlink_entries[0].relative_to(antigravity_skills_dir))
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=(
                    f"Refusing to sync skills-antigravity with symlink entries "
                    f"(first: {rel})."
                ),
                fix_suggestion="Remove symlinks from skills-antigravity and rerun ask skills sync --scope user."
            ))
            return result
        targets = [(skills_dir, repo_root / "skills"), (skills_dir, home / ".claude" / "skills"), (skills_dir, home / ".agents" / "skills"), (skills_dir, home / ".codex" / "skills"), (antigravity_skills_dir, home / ".antigravity" / "skills")]
        for src, dst in targets:
            plan["symlinks"].append({"from": str(dst), "to": str(src)})
            logs.append(_create_symlink(src, dst, dry_run))
        antigravity_dest = home / ".gemini" / "antigravity" / "skills"
        plan["writes"].append(str(antigravity_dest))
        try:
            logs.append(_sync_dir_copy(antigravity_skills_dir, antigravity_dest, dry_run))
        except ValueError as exc:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=str(exc),
                fix_suggestion="Remove symlinks from sync source and retry."
            ))
            return result
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_INVALID_SCOPE",
            message=f"Invalid scope: '{scope}'. Must be 'workspace' or 'user'.",
            fix_suggestion="Use --scope workspace or --scope user"
        ))
        return result
    result.data["plan"] = plan
    result.data["logs"] = logs
    result.data["policy_identity"] = get_policy_identity()
    result.status = "success"
    return result
