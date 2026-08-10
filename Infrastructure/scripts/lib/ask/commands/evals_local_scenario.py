from __future__ import annotations

from dataclasses import dataclass

from .evals_live_preflight import *  # noqa: F403


@dataclass(frozen=True)
class TesslLocalProofRequest:
    """Named options for one staged Tessl lint, pack, install, and review proof."""

    path: str
    workspace: str
    execute: bool
    include_review: bool
    review_threshold: int
    timeout_seconds: int


@dataclass(frozen=True)
class TesslScenarioGenerationRequest:
    """Named options for one isolated Tessl scenario-generation workspace."""

    path: str
    workspace: str | None
    dry_run: bool


def run_tessl_local_proof(repo_root: Path, request: TesslLocalProofRequest) -> dict[str, object]:
    """Stage a Tessl package and optionally run local lint, pack, file install, and review checks."""
    proof_path = _tessl_proof_path(request.path)
    try:
        normalized_workspace = _validate_tessl_workspace(request.workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(repo_root, proof_path, normalized_workspace)
    except (OSError, ValueError) as e:
        return _tessl_local_proof_staging_blocker(request, proof_path, e)

    plan = _tessl_local_proof_plan(repo_root, proof_path, staged_source, normalized_workspace, request)
    receipt = _tessl_local_proof_receipt(request, proof_path, staged_source, copied_files, normalized_workspace, plan)
    if not request.execute:
        return receipt
    return _execute_tessl_local_proof(receipt, request, plan)


def _tessl_proof_path(path: str) -> str:
    source_path = Path(path)
    return str(source_path.parent) if source_path.name == "SKILL.md" else path


def _tessl_local_proof_staging_blocker(
    request: TesslLocalProofRequest,
    proof_path: str,
    error: OSError | ValueError,
) -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.tessl-local-proof.v1",
        "status": "blocked",
        "source_path": request.path,
        "proof_path": proof_path,
        "workspace": request.workspace,
        "execute": request.execute,
        "blocker": f"Failed to stage Tessl local proof source: {error}",
        "blocker_class": "blocked_validation" if isinstance(error, ValueError) else "blocked_runtime",
        "policy": _tessl_local_proof_policy(request.workspace),
    }


def _tessl_local_proof_plan(
    repo_root: Path,
    proof_path: str,
    staged_source: Path,
    workspace: str,
    request: TesslLocalProofRequest,
) -> dict[str, object]:
    tessl_path = shutil.which("tessl") or "tessl"
    source_root_name = (repo_root.resolve() / proof_path).resolve().name
    dist_dir = staged_source / "dist"
    dist_path = dist_dir / f"{source_root_name}.tgz"
    review_path = staged_source / "skills" / source_root_name
    commands = {
        "plugin_lint": [tessl_path, "plugin", "lint", str(staged_source)],
        "plugin_pack": [tessl_path, "plugin", "pack", "--output", str(dist_path), str(staged_source)],
        "install_file": [tessl_path, "install", f"file:{staged_source}", "--agent", "codex", "--yes", "--strict"],
        "review_run": [tessl_path, "review", "run", str(review_path), "--workspace", workspace, "--json", "--threshold", str(request.review_threshold)],
    }
    return {
        "commands": commands,
        "dist_dir": dist_dir,
        "dist_path": dist_path,
        "install_workspace": _stable_tessl_local_install_workspace(proof_path),
    }


def _tessl_local_proof_receipt(
    request: TesslLocalProofRequest,
    proof_path: str,
    staged_source: Path,
    copied_files: list[str],
    workspace: str,
    plan: dict[str, object],
) -> dict[str, object]:
    commands = plan["commands"]
    assert isinstance(commands, dict)
    return {
        "schema_version": "skills-sdk.tessl-local-proof.v1",
        "status": "preview" if not request.execute else "pass",
        "source_path": request.path,
        "proof_path": proof_path,
        "workspace": workspace,
        "execute": request.execute,
        "include_review": request.include_review,
        "review_threshold": request.review_threshold,
        "staged_source": str(staged_source),
        "staged_files": copied_files,
        "staged_file_count": len(copied_files),
        "install_workspace": str(plan["install_workspace"]),
        "dist_dir": str(plan["dist_dir"]),
        "dist_path": str(plan["dist_path"]),
        "planned_commands": {key: " ".join(shlex.quote(part) for part in command) for key, command in commands.items()},
        "commands": {},
        "policy": _tessl_local_proof_policy(workspace),
        "evidence_retention": _tessl_local_proof_evidence_retention(),
    }


def _tessl_local_proof_evidence_retention() -> str:
    return (
        f"staged package is left under {tempfile.gettempdir()}/ask-tessl-evals-live and "
        f"install evidence under {tempfile.gettempdir()}/ask-tessl-local-install for inspection"
    )


def _execute_tessl_local_proof(
    receipt: dict[str, object], request: TesslLocalProofRequest, plan: dict[str, object]
) -> dict[str, object]:
    if not shutil.which("tessl"):
        receipt.update({"status": "blocked", "blocker": "Installed native tessl CLI was not found on PATH.", "blocker_class": "blocked_runtime"})
        return receipt
    install_workspace = plan["install_workspace"]
    dist_dir = plan["dist_dir"]
    commands = plan["commands"]
    assert isinstance(install_workspace, Path) and isinstance(dist_dir, Path) and isinstance(commands, dict)
    _clear_directory(install_workspace)
    dist_dir.mkdir(parents=True, exist_ok=True)
    return _run_tessl_local_proof_commands(receipt, request, commands, install_workspace)


def _run_tessl_local_proof_commands(
    receipt: dict[str, object],
    request: TesslLocalProofRequest,
    planned_commands: dict[str, list[str]],
    install_workspace: Path,
) -> dict[str, object]:
    env = {**os.environ, "TESSL_AUTO_UPDATE_INTERVAL_MINUTES": "0"}
    commands: dict[str, object] = {}
    required = (("plugin_lint", None), ("plugin_pack", None), ("install_file", install_workspace))
    for key, install_cwd in required:
        payload = _run_tessl_local_command(planned_commands[key], cwd=install_cwd or Path(str(receipt["staged_source"])), env=env, timeout_seconds=request.timeout_seconds)
        commands[key] = payload
        if payload.get("status") != "success":
            return _tessl_local_proof_command_failure(receipt, commands, key, payload)
    if request.include_review:
        payload = _run_tessl_local_command(planned_commands["review_run"], cwd=Path(str(receipt["staged_source"])), env=env, timeout_seconds=request.timeout_seconds)
        commands["review_run"] = payload
        if payload.get("status") != "success":
            return _tessl_local_proof_command_failure(receipt, commands, "review_run", payload)
    receipt["commands"] = commands
    receipt["installed_project_manifest"] = str(install_workspace / "tessl.json")
    return receipt


def _tessl_local_proof_command_failure(
    receipt: dict[str, object], commands: dict[str, object], key: str, payload: dict[str, object]
) -> dict[str, object]:
    receipt["status"] = "blocked" if payload.get("status") == "blocked" else "fail"
    receipt["blocker"] = payload.get("blocker") or f"Tessl local proof step failed: {key}"
    receipt["blocker_class"] = payload.get("blocker_class") or "blocked_validation"
    receipt["commands"] = commands
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
    repo_root: Path, request: TesslScenarioGenerationRequest
) -> CallResult:
    """Prepare a temp Tessl scenario-generation workspace for a skill.

    Staging-only is the safe default. Callers must explicitly opt into the
    Tessl tile install because that command can alter the staged project state.
    """
    policy = _tessl_scenario_generation_policy(request.workspace)
    tool_spec = f"{TESSL_SCENARIO_TOOL_TILE}@{TESSL_SCENARIO_TOOL_VERSION}"
    command_display = f"tessl install {tool_spec} --agent codex --yes"
    if not request.dry_run and os.environ.get("ASK_EXTERNAL_EFFECTS") == "deny":
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                "command": command_display,
                "source_path": request.path,
                "raw_output": "",
                "raw_error": "",
                "blocker": "Tessl project setup is blocked by the hermetic test effect policy; use --dry-run in test lanes.",
                "blocker_class": "blocked_validation",
                "policy": policy,
            },
            errors=[ErrorObject(code="ERR_VALIDATION", message="Tessl project setup is blocked by the hermetic test effect policy.")],
        )
    try:
        normalized_workspace = _validate_tessl_workspace(request.workspace)
        staged_root = _stable_tessl_scenario_generation_parent(request.path)
        staged_root.mkdir(parents=True, exist_ok=True)
        target_tile = staged_root / "target-tile"
        tool_project = staged_root / "tool-project"
        target_tile, target_files = _stage_tessl_scenario_target_tile(
            repo_root,
            request.path,
            normalized_workspace,
            target_tile,
        )
        tool_files = _write_tessl_scenario_tool_project(tool_project)
        live_staged_source: Path | None = None
        live_staged_files: list[str] = []
        if not request.dry_run:
            # Tessl binds a project to the concrete directory path. The live
            # evaluator later stages the private plugin under
            # /tmp/ask-tessl-evals-live, so setup must link that exact stable path
            # rather than the scenario-generation target tile.
            live_staged_source, live_staged_files = _stage_tessl_live_private_source(
                repo_root,
                request.path,
                normalized_workspace,
            )
    except (OSError, ValueError) as e:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                "command": command_display,
                "source_path": request.path,
                "raw_output": "",
                "raw_error": str(e),
                "blocker": f"Failed to prepare Tessl scenario-generation staging: {e}",
                "blocker_class": "blocked_validation",
                "policy": policy,
            },
            errors=[ErrorObject(code="ERR_VALIDATION", message=str(e))],
        )

    common = {
        "source_path": request.path,
        "staged_root": str(staged_root),
        "target_tile": str(target_tile),
        "tool_project": str(tool_project),
        "target_plugin_manifest": str(target_tile / ".tessl-plugin" / "plugin.json"),
        "target_tessl_project_marker": str(target_tile / "tessl.json"),
        "target_staged_files": target_files,
        "tool_project_files": tool_files,
        "live_staged_source": str(live_staged_source) if live_staged_source else None,
        "live_staged_files": live_staged_files,
        "workspace": normalized_workspace,
        "project_identity": _tessl_project_identity((repo_root / request.path).resolve(), normalized_workspace),
        "dry_run": request.dry_run,
        "scenario_tool_tile": TESSL_SCENARIO_TOOL_TILE,
        "scenario_tool_version": TESSL_SCENARIO_TOOL_VERSION,
        "staging_policy": "stable_tmp_scenario_generation_evidence",
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-scenario-generation for inspection",
        "policy": _tessl_scenario_generation_policy(normalized_workspace),
    }

    if request.dry_run:
        brief_path = _write_tessl_scenario_generation_brief(
            staged_root,
            source_path=request.path,
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
        live_staged_source or target_tile,
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

    project_link_receipt = _write_tessl_project_link_receipt(
        repo_root,
        request.path,
        workspace=normalized_workspace,
        identity=common["project_identity"],
        project_link=project_link,
    )
    if project_link_receipt is None:
        return CallResult(
            status="error",
            data={
                "status": "blocked",
                **common,
                "command": command_display,
                "raw_output": "",
                "raw_error": "",
                "blocker": "Tessl project link completed but a current project-link receipt could not be written.",
                "blocker_class": "blocked_validation",
            },
            errors=[ErrorObject(code="ERR_VALIDATION", message="Tessl project link receipt could not be written.")],
        )
    common["project_link_receipt"] = project_link_receipt

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
        source_path=request.path,
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

__all__ = [name for name in globals() if not name.startswith("__")]
