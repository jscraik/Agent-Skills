from __future__ import annotations

from .skills_impl_project_conformance import *  # noqa: F403

def audit_skill(
    repo_root: Path,
    skill_path: str,
    level: str = "compat",
    validation_scope: Literal["runtime", "source"] = "runtime",
) -> CallResult:
    """
    Run structural and (optionally) strict security audits for a skill directory.

    Performs path containment validation for `skill_path`, runs structural diagnostics, and when `level` is `"strict"` runs additional validation gates (security gate, family benchmark validation and OpenClaw guard). Populates `result.data` with subprocess outputs under keys `"diagnostics"`, `"security_gate"`, `"family_benchmarks"` and `"openclaw_guard"` as applicable, and appends `ErrorObject`s to `result.errors` when validations fail.

    Parameters:
        repo_root (Path): Repository root against which `skill_path` is resolved.
        skill_path (str): Repository-relative path to the skill directory to audit.
        level (str): Validation level; `"compat"` runs structural diagnostics only, `"strict"` also runs security and benchmark guards.
        validation_scope (Literal["runtime", "source"]): Diagnostics scope. `"source"` adds `--source-only` to the structural diagnostics command; `"runtime"` runs the default runtime-aware diagnostics.

    Returns:
        CallResult: Result with `status` set to `"success"` when diagnostics pass (and all strict checks pass if requested), or `"error"` with `errors` containing one or more `ErrorObject`s. Possible error codes include `ERR_PATH_TRAVERSAL` and `ERR_VALIDATION`.
    """ 
    result = CallResult()
    validation_args = [skill_path]
    if level != "compat":
        validation_args.extend(["--level", level])
    result.data["validation_commands"] = [_skills_validation_command("audit", *validation_args)]

    external_skill_children = _external_skill_root_children(repo_root, skill_path)
    if external_skill_children:
        result.data["target"] = Path(skill_path).expanduser().as_posix()
        result.data["audit_scope"] = {
            "classification": "external_project_skill_root",
            "repo_coupled_gates": False,
            "child_count": len(external_skill_children),
        }
        child_results: list[dict[str, Any]] = []
        failed_children: list[str] = []
        for child in external_skill_children:
            child_result = audit_skill(
                repo_root,
                child.as_posix(),
                level=level,
                validation_scope=validation_scope,
            )
            child_errors = [getattr(error, "__dict__", error) for error in child_result.errors]
            child_results.append({
                "target": child.as_posix(),
                "status": child_result.status,
                "audit_scope": child_result.data.get("audit_scope"),
                "errors": child_errors,
            })
            if child_result.status != "success":
                failed_children.append(child.as_posix())
        result.data["children"] = child_results
        if failed_children:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=(
                    f"External skill root audit failed for {len(failed_children)} "
                    f"of {len(external_skill_children)} child skills."
                ),
                fix_suggestion="Inspect data.children for failing child skill audits.",
            ))
        else:
            result.status = "success"
        return result

    resolved_skill_path, external_project_skill, path_error = _resolve_audit_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    if not external_project_skill and (
        resolved_skill_path is None or _resolve_existing_skill_path(resolved_skill_path) is None
    ):
        target_info, resolved_audit_target = _resolve_doctor_target(repo_root, skill_path)
        if target_info.get("target_kind") == "command_handle" and target_info.get("source_exists") and resolved_audit_target:
            resolved_skill_path = (repo_root / resolved_audit_target).resolve()

    target_input = skill_path
    if resolved_skill_path is not None:
        if external_project_skill:
            target_input = resolved_skill_path.as_posix()
        else:
            target_input = resolved_skill_path.relative_to(repo_root.resolve()).as_posix()
    audit_target, audit_target_path = _normalize_skill_target_path(
        target_input
    )
    result.data["target"] = audit_target_path
    result.data["audit_scope"] = {
        "classification": "external_project_skill" if external_project_skill else "foundry_repo_skill",
        "repo_coupled_gates": not external_project_skill,
    }

    python = _get_python_command(["pyyaml", "jsonschema"])

    diag_cmd = python + ["Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py", audit_target_path]
    if validation_scope == "source":
        diag_cmd.append("--source-only")
    audit_env = _subprocess_env_with_uv_cache()

    diag_proc = subprocess.run(diag_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
    result.data["diagnostics"] = {"exit_code": diag_proc.returncode, "stdout": diag_proc.stdout, "stderr": diag_proc.stderr}

    is_skill_factory_system_overlay = not external_project_skill and audit_target_path in {
        "skills-system/skill-creator",
        "skills-system/skill-installer",
    }

    if level == "strict" and is_skill_factory_system_overlay:
        overlay_cmd = python + ["Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py"]
        overlay_proc = subprocess.run(overlay_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["system_overlay"] = {"exit_code": overlay_proc.returncode, "stdout": overlay_proc.stdout, "stderr": overlay_proc.stderr}
        if overlay_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Skill Factory system overlay validation failed."))
            return result

        family_cmd = python + ["Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py", "--skill", audit_target_path]
        family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["family_benchmarks"] = {"exit_code": family_proc.returncode, "stdout": family_proc.stdout, "stderr": family_proc.stderr}
        if family_proc.returncode != 0:
            summary = _summarize_family_benchmark_failure(family_proc.stdout, family_proc.stderr)
            message = "Family benchmarks validation failed."
            if summary:
                message = f"{message} First failures: {summary}"
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message))
            return result

        result.data["security_gate"] = {
            "status": "skipped_skill_factory_system_overlay",
            "reason": (
                "Preserved Codex .system SKILL.md body; the local strict contract is enforced through "
                "attached Skill Factory references and system overlay validators."
            ),
        }
        result.data["openclaw_guard"] = {
            "status": "skipped_skill_factory_system_overlay",
            "reason": (
                "Preserved Codex .system SKILL.md body; run the overlay and family validators for "
                "local Skill Factory additions."
            ),
        }
    elif level == "strict":
        # Security gate (skill_gate.py)
        gate_script = _resolve_skill_builder_script(repo_root, "skill_gate")
        gate_cmd = python + [gate_script, audit_target_path, "--require-security-evals", "--pi-high-fail", "--require-fail-fast"]
        gate_proc = subprocess.run(gate_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["security_gate"] = {"exit_code": gate_proc.returncode, "stdout": gate_proc.stdout, "stderr": gate_proc.stderr}
        if gate_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Security gate failed."))
            return result

        if external_project_skill:
            result.data["family_benchmarks"] = {
                "status": "skipped_external_project_skill",
                "reason": "Family benchmark validation is foundry-repo-relative; owner repo receipts must prove external release readiness.",
            }
        else:
            # Family benchmarks validation
            family_cmd = python + ["Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py", "--skill", audit_target_path]
            family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
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
        openclaw_proc = subprocess.run(openclaw_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
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
