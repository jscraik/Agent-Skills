from __future__ import annotations

from dataclasses import dataclass
import tempfile

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


def _coerce_tessl_local_proof_request(
    request_or_path: TesslLocalProofRequest | str | None,
    legacy_options: dict[str, object],
) -> TesslLocalProofRequest:
    """Accept the request object while retaining the former path-and-keyword form."""
    path, workspace, execute, include_review, review_threshold, timeout_seconds = _legacy_tessl_local_proof_values(
        legacy_options
    )
    if isinstance(request_or_path, TesslLocalProofRequest):
        if any(value is not None for value in (path, workspace, execute, include_review, review_threshold, timeout_seconds)):
            raise TypeError("TesslLocalProofRequest cannot be combined with legacy proof options")
        return request_or_path
    if request_or_path is None:
        request_or_path = path
    elif path is not None:
        raise TypeError("run_tessl_local_proof received both a positional path and path keyword")
    if not isinstance(request_or_path, str):
        raise TypeError("run_tessl_local_proof expects a TesslLocalProofRequest or skill path string")
    if workspace is None:
        raise TypeError("run_tessl_local_proof requires workspace when called with a skill path")
    return TesslLocalProofRequest(
        path=request_or_path,
        workspace=workspace,
        execute=False if execute is None else execute,
        include_review=False if include_review is None else include_review,
        review_threshold=TESSL_LOCAL_REVIEW_MIN_SCORE if review_threshold is None else review_threshold,
        timeout_seconds=180 if timeout_seconds is None else timeout_seconds,
    )


def _legacy_tessl_local_proof_values(legacy_options: dict[str, object]) -> tuple[object | None, ...]:
    """Validate and consume the legacy local-proof keyword options."""
    allowed = {
        "path",
        "workspace",
        "execute",
        "include_review",
        "review_threshold",
        "timeout_seconds",
    }
    unexpected = sorted(set(legacy_options) - allowed)
    if unexpected:
        raise TypeError(f"run_tessl_local_proof received unexpected option(s): {', '.join(unexpected)}")
    return (
        legacy_options.pop("path", None),
        legacy_options.pop("workspace", None),
        legacy_options.pop("execute", None),
        legacy_options.pop("include_review", None),
        legacy_options.pop("review_threshold", None),
        legacy_options.pop("timeout_seconds", None),
    )


def run_tessl_local_proof(
    repo_root: Path,
    request_or_path: TesslLocalProofRequest | str | None = None,
    **legacy_options: object,
) -> dict[str, object]:
    """Stage a Tessl package and optionally run local lint, pack, file install, and review checks."""
    request = _coerce_tessl_local_proof_request(
        request_or_path,
        legacy_options,
    )
    proof_path = _tessl_proof_path(request.path)
    try:
        normalized_workspace = _validate_tessl_workspace(request.workspace)
        staged_source, copied_files = _stage_tessl_live_private_source(
            repo_root, proof_path, normalized_workspace,
            temp_root=Path(tempfile.gettempdir()) / "ask-tessl-local-proof",
        )
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
        f"staged package is left under {tempfile.gettempdir()}/ask-tessl-local-proof and "
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


def _coerce_tessl_scenario_generation_request(
    request: TesslScenarioGenerationRequest | None,
    *,
    path: str | None,
    workspace: str | None,
    dry_run: bool | None,
) -> TesslScenarioGenerationRequest:
    if request is not None:
        if path is not None or workspace is not None or dry_run is not None:
            raise TypeError("scenario generation received both a request and legacy options")
        return request
    if path is None or dry_run is None:
        raise TypeError("scenario generation requires path and dry_run when no request is supplied")
    return TesslScenarioGenerationRequest(path=path, workspace=workspace, dry_run=dry_run)


@dataclass(frozen=True)
class _TesslScenarioStaging:
    workspace: str
    staged_root: Path
    target_tile: Path
    tool_project: Path
    target_files: list[str]
    tool_files: list[str]
    live_source: Path | None
    live_files: list[str]


def _scenario_generation_error(
    command: str, source_path: str, policy: dict[str, object], blocker: str,
    blocker_class: str, *, raw_error: str = "", raw_output: str = "", common: dict[str, object] | None = None,
) -> CallResult:
    data = {"status": "blocked", "source_path": source_path, "policy": policy, **(common or {})}
    data.update(command=command, raw_output=raw_output, raw_error=raw_error, blocker=blocker, blocker_class=blocker_class)
    code = "ERR_RUNTIME" if blocker_class == "blocked_runtime" else "ERR_VALIDATION"
    return CallResult(status="error", data=data, errors=[ErrorObject(code=code, message=blocker)])


def _stage_tessl_scenario_generation(
    repo_root: Path, request: TesslScenarioGenerationRequest, command: str, policy: dict[str, object],
) -> _TesslScenarioStaging | CallResult:
    try:
        workspace = _validate_tessl_workspace(request.workspace)
        staged_root = _stable_tessl_scenario_generation_parent(request.path)
        staged_root.mkdir(parents=True, exist_ok=True)
        target_tile, target_files = _stage_tessl_scenario_target_tile(repo_root, request.path, workspace, staged_root / "target-tile")
        tool_project = staged_root / "tool-project"
        tool_files = _write_tessl_scenario_tool_project(tool_project)
        live_source, live_files = (None, []) if request.dry_run else _stage_tessl_live_private_source(repo_root, request.path, workspace)
        return _TesslScenarioStaging(workspace, staged_root, target_tile, tool_project, target_files, tool_files, live_source, live_files)
    except (OSError, ValueError) as exc:
        return _scenario_generation_error(command, request.path, policy, f"Failed to prepare Tessl scenario-generation staging: {exc}", "blocked_validation", raw_error=str(exc))


def _scenario_generation_common(
    repo_root: Path, request: TesslScenarioGenerationRequest, staging: _TesslScenarioStaging,
) -> dict[str, object]:
    return {
        "source_path": request.path, "staged_root": str(staging.staged_root), "target_tile": str(staging.target_tile),
        "tool_project": str(staging.tool_project), "target_plugin_manifest": str(staging.target_tile / ".tessl-plugin" / "plugin.json"),
        "target_tessl_project_marker": str(staging.target_tile / "tessl.json"), "target_staged_files": staging.target_files,
        "tool_project_files": staging.tool_files, "live_staged_source": str(staging.live_source) if staging.live_source else None,
        "live_staged_files": staging.live_files, "workspace": staging.workspace,
        "project_identity": _tessl_project_identity((repo_root / request.path).resolve(), staging.workspace), "dry_run": request.dry_run,
        "scenario_tool_tile": TESSL_SCENARIO_TOOL_TILE, "scenario_tool_version": TESSL_SCENARIO_TOOL_VERSION,
        "staging_policy": "stable_tmp_scenario_generation_evidence",
        "evidence_retention": f"staged directory is left under {tempfile.gettempdir()}/ask-tessl-scenario-generation for inspection",
        "policy": _tessl_scenario_generation_policy(staging.workspace),
    }


def _scenario_generation_dry_run(
    request: TesslScenarioGenerationRequest, staging: _TesslScenarioStaging, common: dict[str, object], command: str,
) -> CallResult:
    brief = _write_tessl_scenario_generation_brief(staging.staged_root, source_path=request.path, workspace=staging.workspace, target_tile=staging.target_tile, tool_project=staging.tool_project)
    return CallResult(status="success", data={"status": "pass", **common, "command": command, "scenario_generation_brief": str(brief), "raw_output": "", "raw_error": "", "exit_code": 0, "blocker": None, "blocker_class": None})


def _link_tessl_scenario_project(
    repo_root: Path, request: TesslScenarioGenerationRequest, staging: _TesslScenarioStaging,
    common: dict[str, object], command: str, tessl_path: str,
) -> CallResult | None:
    link = _ensure_tessl_project_link(tessl_path, staging.live_source or staging.target_tile, common["project_identity"])
    common["project_link"] = link
    if link.get("status") == "blocked":
        return _scenario_generation_error(command, request.path, common["policy"], str(link.get("blocker") or "Tessl project link check failed."), str(link.get("blocker_class") or "blocked_validation"), common=common)
    receipt = _write_tessl_project_link_receipt(repo_root, request.path, workspace=staging.workspace, identity=common["project_identity"], project_link=link)
    if receipt is None:
        return _scenario_generation_error(command, request.path, common["policy"], "Tessl project link completed but a current project-link receipt could not be written.", "blocked_validation", common=common)
    common["project_link_receipt"] = receipt
    return None


def _install_tessl_scenario_tool(
    tessl_path: str, tool_project: Path, tool_spec: str, request: TesslScenarioGenerationRequest,
    common: dict[str, object], command: str,
) -> subprocess.CompletedProcess | CallResult:
    try:
        return subprocess.run([tessl_path, "install", tool_spec, "--agent", "codex", "--yes"], cwd=str(tool_project), capture_output=True, text=True, timeout=600, env={**os.environ, "TESSL_AUTO_UPDATE_INTERVAL_MINUTES": "0"})
    except subprocess.TimeoutExpired as exc:
        return _scenario_generation_error(command, request.path, common["policy"], "Tessl scenario tool install timed out after 600 seconds.", "blocked_runtime", raw_output=_as_text(exc.stdout), raw_error=_as_text(exc.stderr), common=common)
    except OSError as exc:
        return _scenario_generation_error(command, request.path, common["policy"], f"Failed to run Tessl scenario tool install: {exc}", "blocked_runtime", raw_error=str(exc), common=common)


def _scenario_generation_install_result(
    process: subprocess.CompletedProcess, request: TesslScenarioGenerationRequest, staging: _TesslScenarioStaging,
    common: dict[str, object], command: str,
) -> CallResult:
    raw_output, raw_error = process.stdout, process.stderr
    auth_required = process.returncode != 0 and "authenticate with tessl" in f"{raw_output}\n{raw_error}".lower()
    status, blocker, blocker_class = ("blocked", "Tessl CLI is installed locally, but authentication is required before scenario tool install can run.", "blocked_auth") if auth_required else ("pass" if process.returncode == 0 else "fail", None, None)
    scenario_skill, scenario_reference = _tessl_scenario_tool_paths(staging.tool_project)
    brief = _write_tessl_scenario_generation_brief(staging.staged_root, source_path=request.path, workspace=staging.workspace, target_tile=staging.target_tile, tool_project=staging.tool_project)
    data = {"status": status, **common, "command": command, "exit_code": process.returncode, "raw_output": raw_output, "raw_error": raw_error, "blocker": blocker, "blocker_class": blocker_class, "scenario_skill": str(scenario_skill) if scenario_skill.exists() else None, "scenario_reference": str(scenario_reference) if scenario_reference.exists() else None, "scenario_generation_brief": str(brief), "generated_output": str(staging.target_tile / "evals"), "prepared_only": True}
    if status == "pass":
        return CallResult(status="success", data=data)
    return CallResult(status="error", data=data, errors=[ErrorObject(code="ERR_VALIDATION", message=blocker or "Tessl scenario tool install failed.")])


def prepare_tessl_scenario_generation(
    repo_root: Path, request: TesslScenarioGenerationRequest | None = None, *, path: str | None = None,
    workspace: str | None = None, dry_run: bool | None = None,
) -> CallResult:
    """Prepare a disposable Tessl scenario-generation workspace for one skill."""
    request = _coerce_tessl_scenario_generation_request(request, path=path, workspace=workspace, dry_run=dry_run)
    policy = _tessl_scenario_generation_policy(request.workspace)
    tool_spec = f"{TESSL_SCENARIO_TOOL_TILE}@{TESSL_SCENARIO_TOOL_VERSION}"
    command = f"tessl install {tool_spec} --agent codex --yes"
    if not request.dry_run and os.environ.get("ASK_EXTERNAL_EFFECTS") == "deny":
        return _scenario_generation_error(command, request.path, policy, "Tessl project setup is blocked by the hermetic test effect policy; use --dry-run in test lanes.", "blocked_validation")
    staging = _stage_tessl_scenario_generation(repo_root, request, command, policy)
    if isinstance(staging, CallResult):
        return staging
    common = _scenario_generation_common(repo_root, request, staging)
    if request.dry_run:
        return _scenario_generation_dry_run(request, staging, common, command)
    tessl_path = shutil.which("tessl")
    if not tessl_path:
        return _scenario_generation_error(command, request.path, common["policy"], "Installed native tessl CLI was not found on PATH.", "blocked_runtime", common=common)
    if linked := _link_tessl_scenario_project(repo_root, request, staging, common, command, tessl_path):
        return linked
    process = _install_tessl_scenario_tool(tessl_path, staging.tool_project, tool_spec, request, common, command)
    if isinstance(process, CallResult):
        return process
    return _scenario_generation_install_result(process, request, staging, common, command)

__all__ = [name for name in globals() if not name.startswith("__")]
