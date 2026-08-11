from __future__ import annotations

from .skills_impl_project_conformance import *  # noqa: F403


def _run_audit_subprocess(
    result: CallResult,
    repo_root: Path,
    command: list[str],
    data_key: str,
    failure_message: str,
) -> bool:
    """Record one bounded audit subprocess and copy structured failures into the audit result."""
    command_result = _run_validation_command(
        repo_root,
        command,
        data_key,
        failure_message,
    )
    result.data[data_key] = command_result.data[data_key]
    if command_result.status == "success":
        return True
    result.status = "error"
    result.errors.extend(command_result.errors)
    return False


def _audit_external_children(
    result: CallResult, repo_root: Path, skill_path: str, children: list[Path],
    level: str, validation_scope: Literal["runtime", "source"],
) -> CallResult:
    """Audit each child under an external skill root."""
    result.data["target"] = Path(skill_path).expanduser().as_posix()
    result.data["audit_scope"] = {
        "classification": "external_project_skill_root",
        "repo_coupled_gates": False,
        "child_count": len(children),
    }
    child_results = [
        audit_skill(repo_root, child.as_posix(), level=level, validation_scope=validation_scope)
        for child in children
    ]
    result.data["children"] = [
        {
            "target": child.as_posix(), "status": child_result.status,
            "audit_scope": child_result.data.get("audit_scope"),
            "errors": [getattr(error, "__dict__", error) for error in child_result.errors],
        }
        for child, child_result in zip(children, child_results)
    ]
    failed = [child.as_posix() for child, row in zip(children, child_results) if row.status != "success"]
    result.status = "error" if failed else "success"
    if failed:
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"External skill root audit failed for {len(failed)} of {len(children)} child skills.",
            fix_suggestion="Inspect data.children for failing child skill audits.",
        ))
    return result


def _resolve_audit_target(
    repo_root: Path, skill_path: str,
) -> tuple[str, bool, CallResult | None]:
    """Resolve one audit target and its ownership classification."""
    resolved, external, path_error = _resolve_audit_skill_path(repo_root, skill_path)
    if path_error:
        return "", external, path_error
    if not external and (resolved is None or _resolve_existing_skill_path(resolved) is None):
        target_info, resolved_target = _resolve_doctor_target(repo_root, skill_path)
        if target_info.get("target_kind") == "command_handle" and target_info.get("source_exists") and resolved_target:
            resolved = (repo_root / resolved_target).resolve()
    target_input = skill_path
    if resolved is not None:
        target_input = (
            resolved.as_posix()
            if external
            else resolved.relative_to(repo_root.resolve()).as_posix()
        )
    _, target_path = _normalize_skill_target_path(target_input)
    return target_path, external, None


def _run_audit_diagnostics(
    result: CallResult, repo_root: Path, skill_path: str, target_path: str,
    python: list[str], validation_scope: Literal["runtime", "source"],
) -> bool:
    """Run structural diagnostics before any strict gate."""
    command = python + ["Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py", target_path]
    if validation_scope == "source":
        command.append("--source-only")
    passed = _run_audit_subprocess(
        result, repo_root, command, "diagnostics",
        "Structural diagnostics failed. Skill directory not found or invalid.",
    )
    if not passed:
        result.errors[-1].fix_suggestion = f"Ensure '{skill_path}' exists and contains a SKILL.md file."
    return passed


def _run_family_benchmark(
    result: CallResult, repo_root: Path, target_path: str, python: list[str], *, detailed: bool,
) -> bool:
    """Run family benchmarks and enrich non-timeout failures."""
    command = python + [
        "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py",
        "--skill", target_path,
    ]
    if _run_audit_subprocess(
        result, repo_root, command, "family_benchmarks", "Family benchmarks validation failed."
    ):
        return True
    data = result.data["family_benchmarks"]
    summary = _summarize_family_benchmark_failure(data["stdout"], data["stderr"])
    if result.errors[-1].code != "ERR_TIMEOUT":
        result.errors[-1].message += f" First failures: {summary}" if summary else ""
        if detailed:
            quoted = shlex.quote(target_path)
            result.errors[-1].fix_suggestion = (
                "Inspect data.family_benchmarks for full output, or run: "
                "mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python "
                "Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py "
                f"--skill {quoted} --format text"
            )
    return False


def _run_overlay_audit(
    result: CallResult, repo_root: Path, target_path: str, python: list[str],
) -> bool:
    """Run strict validation for Skill Factory system overlays."""
    overlay = python + ["Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py"]
    if not _run_audit_subprocess(
        result, repo_root, overlay, "system_overlay", "Skill Factory system overlay validation failed."
    ) or not _run_family_benchmark(result, repo_root, target_path, python, detailed=False):
        return False
    result.data["security_gate"] = {
        "status": "skipped_skill_factory_system_overlay",
        "reason": "System overlay and family validators enforce this preserved Codex .system skill.",
    }
    result.data["openclaw_guard"] = {
        "status": "skipped_skill_factory_system_overlay",
        "reason": "System overlay and family validators enforce local Skill Factory additions.",
    }
    return True


def _run_strict_audit(
    result: CallResult, repo_root: Path, target_path: str, external: bool, python: list[str],
) -> bool:
    """Run strict security, family, and OpenClaw gates."""
    security = python + [
        _resolve_skill_builder_script(repo_root, "skill_gate"), target_path,
        "--require-security-evals", "--pi-high-fail", "--require-fail-fast",
    ]
    if not _run_audit_subprocess(result, repo_root, security, "security_gate", "Security gate failed."):
        return False
    if external:
        result.data["family_benchmarks"] = {
            "status": "skipped_external_project_skill",
            "reason": "Family benchmarks are repo-relative; the owner repo must prove readiness.",
        }
    elif not _run_family_benchmark(result, repo_root, target_path, python, detailed=True):
        return False
    openclaw = python + [
        _resolve_skill_builder_script(repo_root, "openclaw_skill_guard"),
        target_path, "--mode", "both", "--format", "text",
    ]
    return _run_audit_subprocess(
        result, repo_root, openclaw, "openclaw_guard", "OpenClaw guard validation failed."
    )


def audit_skill(
    repo_root: Path, skill_path: str, level: str = "compat",
    validation_scope: Literal["runtime", "source"] = "runtime",
) -> CallResult:
    """Run runtime gates for runtime scope, or source-only diagnostics for source scope."""
    result = CallResult()
    args = [skill_path, *(["--level", level] if level != "compat" else [])]
    result.data["validation_commands"] = [_skills_validation_command("audit", *args)]
    children = _external_skill_root_children(repo_root, skill_path)
    if children:
        return _audit_external_children(result, repo_root, skill_path, children, level, validation_scope)
    target_path, external, path_error = _resolve_audit_target(repo_root, skill_path)
    if path_error:
        return path_error
    result.data["target"] = target_path
    result.data["audit_scope"] = {
        "classification": "external_project_skill" if external else "foundry_repo_skill",
        "repo_coupled_gates": not external,
    }
    python = _get_python_command(["pyyaml", "jsonschema"])
    if not _run_audit_diagnostics(result, repo_root, skill_path, target_path, python, validation_scope):
        return result
    overlay = not external and target_path in {"skills-system/skill-creator", "skills-system/skill-installer"}
    if level == "strict" and not (
        _run_overlay_audit(result, repo_root, target_path, python)
        if overlay else _run_strict_audit(result, repo_root, target_path, external, python)
    ):
        return result
    result.status = "success"
    return result


def validate_skill_gate(repo_root: Path, skill_path: str) -> CallResult:
    """Run the canonical skill gate as a first-class validation command."""
    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    audit_target, audit_target_path = _normalize_skill_target_path(skill_path)
    python = _get_python_command(["pyyaml", "jsonschema"])
    gate_script = _resolve_skill_builder_script(repo_root, "skill_gate")
    gate_cmd = python + [
        gate_script,
        audit_target_path,
        "--require-security-evals",
        "--pi-high-fail",
        "--require-fail-fast",
    ]
    result = _run_validation_command(
        repo_root,
        gate_cmd,
        "skill_gate",
        "Skill gate validation failed.",
        fix_suggestion=(
            "Inspect data.skill_gate for full output, or rerun the command shown there "
            f"against {shlex.quote(audit_target_path)}."
        ),
    )
    result.data["validation_commands"] = [_skills_validation_command("validate-skill-gate", skill_path)]
    return result


def validate_openai_skill_format(repo_root: Path, skill_path: str, mode: str = "strict") -> CallResult:
    """Run the canonical OpenAI skill format wrapper as a first-class validation command."""
    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    _, audit_target_path = _normalize_skill_target_path(skill_path)
    command = [
        "bash",
        "Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh",
        "--mode",
        mode,
        audit_target_path,
    ]
    result = _run_validation_command(
        repo_root,
        command,
        "openai_skill_format",
        "OpenAI skill format validation failed.",
        fix_suggestion=(
            "Inspect data.openai_skill_format for full output, or rerun the command shown there "
            f"against {shlex.quote(audit_target_path)}."
        ),
    )
    result.data["validation_commands"] = [
        _skills_validation_command("validate-openai-format", skill_path, "--mode", mode)
    ]
    return result

__all__ = [name for name in globals() if not name.startswith("__")]
