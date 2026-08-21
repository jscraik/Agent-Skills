from __future__ import annotations

from .repo_impl_core import *  # noqa: F403
from .repo_impl_doctor import *  # noqa: F403
from .repo_impl_closeout import *  # noqa: F403

def provider_audit(repo_root: Path) -> CallResult:
    """Run the OpenAI provider policy audit and return its JSON report."""
    result = CallResult()
    result.data["validation_commands"] = [_repo_validation_command("provider-audit")]
    cmd = [
        sys.executable,
        "Infrastructure/scripts/validation-and-linting/verify_provider_policy.py",
        "--json",
    ]
    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=SCRIPT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result.data["provider_policy"] = {
            "status": "fail",
            "raw_stdout": exc.stdout or "",
            "raw_stderr": exc.stderr or "",
        }
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit timed out.",
                fix_suggestion="Run the provider policy script directly, inspect for hangs, and retry.",
            )
        )
        return result
    except OSError as exc:
        result.data["provider_policy"] = {
            "status": "fail",
            "raw_stdout": "",
            "raw_stderr": str(exc),
        }
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit could not start.",
                fix_suggestion="Verify the Python interpreter and provider policy script path, then retry.",
            )
        )
        return result
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
        }

    result.data["provider_policy"] = report
    result.status = "success" if process.returncode == 0 and report.get("status") == "pass" else "error"
    if result.status == "error":
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit failed.",
                fix_suggestion="Remove or archive active legacy provider paths, then rerun ask repo provider-audit.",
            )
        )
    return result


def repo_surface(repo_root: Path, strict: bool = False) -> CallResult:
    """
    Produce a surface-inventory report for the repository.

    Parameters:
        repo_root (Path): Path to the repository root where the inventory check will run.
        strict (bool): When true, require strict inventory validation.

    Returns:
        CallResult: Result containing:
            - data["repo_surface"]: parsed inventory report dictionary (or a fallback error report on parse failure).
            - data["strict"]: the provided `strict` value.
            - status: "success" when the inventory indicates no blocking failures, otherwise "error".
            - errors: on failure, one or more ErrorObject entries describing the problem and suggested fixes.
              Inventory failures use "ERR_VALIDATION"; inventory command timeouts use "ERR_TIMEOUT".
    """
    result = CallResult()
    result.data["validation_commands"] = [_repo_validation_command("surface", strict=strict)]
    cmd = [
        sys.executable,
        "Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py",
        "--json",
    ]
    if strict:
        cmd.append("--strict")

    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        result.status = "error"
        result.data["repo_surface"] = {
            "status": "error",
            "raw_stdout": exc.stdout or "",
            "raw_stderr": exc.stderr or "",
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }
        result.data["strict"] = strict
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_TIMEOUT,
                message=(
                    "Repo surface inventory timed out after "
                    f"{SCRIPT_TIMEOUT_SECONDS} seconds."
                ),
                fix_suggestion=(
                    "Run the underlying inventory script directly to identify "
                    "the slow path, then retry repo surface."
                ),
            )
        )
        return result
    except OSError as exc:
        result.status = "error"
        result.data["repo_surface"] = {
            "status": "error",
            "raw_stdout": "",
            "raw_stderr": str(exc),
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }
        result.data["strict"] = strict
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Repo surface inventory could not start.",
                fix_suggestion="Verify the Python interpreter and inventory script path, then retry repo surface.",
            )
        )
        return result
    parse_ok = True
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        parse_ok = False
        report = {
            "status": "error",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }

    result.data["repo_surface"] = report
    result.data["strict"] = strict
    report_status = report.get("status")
    result.status = (
        "success"
        if process.returncode == 0 and parse_ok and report_status in {"success", "warning"}
        else "error"
    )
    if result.status == "error":
        blocking = report.get("summary", {}).get("blocking_findings", "unknown")
        message = f"Repo surface inventory found {blocking} blocking finding(s)."
        suggestion = (
            "Review data.repo_surface.findings and classify or clean up the owning "
            "tracked surfaces before relying on strict mode."
        )
        if not parse_ok:
            message = "Repo surface inventory emitted invalid JSON."
            suggestion = "Run the underlying inventory script directly and fix stdout JSON integrity."
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=suggestion,
            )
        )
    return result


def check_hub_stability(repo_root: Path, changed_files: List[str] | None = None) -> CallResult:
    """
    Validate stability-related changes to SKILL.md files and enforce rules for skills marked `stability: stable`.

    Checks the repository for SKILL.md frontmatter that declares a skill as stable and, when a list of changed files is provided, verifies that:
    - stable SKILL.md files include `name:` and `description:` fields in their frontmatter, and
    - deletion of a stable skill is not performed without an existing deprecation notice.

    Parameters:
        repo_root (Path): Repository root directory against which paths and SKILL.md files are resolved.
        changed_files (List[str], optional): Iterable of file paths (typically relative to `repo_root`) to inspect; if omitted, only a global scan is performed.

    Returns:
        CallResult: Contains:
          - `status`: `"success"` if no stability violations were found, `"error"` otherwise.
          - `data.stable_skills` (List[str]): Sorted list of discovered stable skill identifiers.
          - `data.stable_count` (int): Number of discovered stable skills.
          - `data.checked_files` (int): Number of `changed_files` inspected (0 if `changed_files` was not provided).
          - `data.errors` (List[str], optional): When `status` is `"error"`, a list of human-readable error messages describing each violation.
          - `errors` (List[ErrorObject]): For each string in `data.errors`, an `ErrorObject` with `code="ERR_VALIDATION"` is appended to the result's `errors` list.
    """
    result = CallResult()
    validation_args = ["--changed-files", *changed_files] if changed_files else []
    result.data["validation_commands"] = [_repo_validation_command("check-stability", *validation_args)]

    # Build list of all SKILL.md files
    stable_skills = []
    errors = []

    FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
    STABLE_RE = re.compile(r"^stability\s*:\s*stable\s*$", re.MULTILINE)

    for md in sorted(repo_root.rglob("SKILL.md")):
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
            fm = FRONTMATTER_RE.search(content)
            if fm and STABLE_RE.search(fm.group(1)):
                skill = md.parts[-2]
                stable_skills.append(skill)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Warning: Failed to read or parse {md}: {exc}", file=sys.stderr)
            continue
        except re.error as exc:
            print(f"Warning: Regex error processing {md}: {exc}", file=sys.stderr)
            continue

    # If checking specific changed files
    if changed_files:
        for f in changed_files:
            p = repo_root / f
            if p.name != "SKILL.md":
                continue
            skill = p.parts[-2] if len(p.parts) >= 2 else str(p)

            if not p.exists():
                # File was deleted - check against stable skills list or edges file
                edges_file = repo_root / "ops" / "metrics" / "graph" / "skill-edges.json"
                if edges_file.exists():
                    try:
                        data = json.loads(edges_file.read_text())
                        stable_ids = {n["id"] for n in data.get("nodes", []) if n.get("stability") == "stable"}
                        if skill in stable_ids:
                            previous = subprocess.run(
                                ["git", "show", f"HEAD:{f}"],
                                cwd=str(repo_root),
                                capture_output=True,
                                text=True,
                                check=False,
                                timeout=SCRIPT_TIMEOUT_SECONDS,
                            )
                            if previous.returncode == 0 and re.search(r"^## Deprecation\b", previous.stdout, re.MULTILINE):
                                continue
                            errors.append(
                                f"STABLE SKILL DELETED: '{skill}' is marked stable and was deleted "
                                f"without a deprecation notice. Add a ## Deprecation section to the "
                                f"last committed version before removal."
                            )
                    except (OSError, json.JSONDecodeError, KeyError, TypeError, subprocess.SubprocessError) as e:
                        errors.append(
                            f"Unable to validate stable skill deletion for '{skill}' due to error reading "
                            f"or parsing skill-edges.json: {e}"
                        )
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                fm = FRONTMATTER_RE.search(content)
                if not (fm and STABLE_RE.search(fm.group(1))):
                    continue

                # Stable skill exists - check required fields
                if not re.search(r"^name\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'name': {skill}")
                if not re.search(r"^description\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'description': {skill}")
            except (OSError, UnicodeDecodeError) as exc:
                print(f"Warning: Failed to read or parse {p}: {exc}", file=sys.stderr)
                continue
            except re.error as exc:
                print(f"Warning: Regex error processing {p}: {exc}", file=sys.stderr)
                continue

    result.data["stable_skills"] = sorted(stable_skills)
    result.data["stable_count"] = len(stable_skills)
    result.data["checked_files"] = len(changed_files) if changed_files else 0

    if errors:
        result.status = "error"
        result.data["errors"] = errors
        for e in errors:
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=e))
    else:
        result.status = "success"

    return result
__all__ = [name for name in globals() if not name.startswith("__")]
