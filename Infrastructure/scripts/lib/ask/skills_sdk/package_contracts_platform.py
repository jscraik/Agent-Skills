from .package_contracts_core import *  # noqa: F403
from .package_contracts_rubric import *  # noqa: F403
from .package_contracts_support import *  # noqa: F403
from .package_contracts_optimization import *  # noqa: F403
from .package_contracts_writing_core import *  # noqa: F403
from .package_contracts_writing_checks import *  # noqa: F403

def _platform_check(
    name: str,
    status: str,
    *,
    dimension: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility check record."""
    return {
        "name": name,
        "dimension": dimension,
        "status": status,
        "evidence": evidence or {},
    }


def _platform_blocker(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility blocker record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "blocked",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _platform_advisory(
    rule_id: str,
    message: str,
    *,
    dimension: str,
    path: str | None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a stable OpenAI platform compatibility advisory record."""
    return {
        "rule_id": rule_id,
        "dimension": dimension,
        "severity": "advisory",
        "path": path,
        "message": message,
        "evidence": evidence or {},
    }


def _plugin_root_for_source(repo_root: Path | None, source_path: Path | None) -> Path | None:
    """Return the owning plugin root for a plugin-owned skill source."""
    if not repo_root or not source_path:
        return None
    relative = repo_relative_path(repo_root, source_path)
    if not relative:
        return None
    parts = relative.split("/")
    if len(parts) >= 4 and parts[0] == "Plugins" and parts[2] == "skills":
        return repo_root / parts[0] / parts[1]
    return None


def _plugin_manifest_path(plugin_root: Path | None) -> Path | None:
    """Return the supported plugin manifest path for a plugin root."""
    if not plugin_root:
        return None
    for relative in (".codex-plugin/plugin.json", "plugin.json"):
        candidate = plugin_root / relative
        if candidate.is_file():
            return candidate
    return None


def _read_json_object(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    """Read a JSON object without treating malformed data as instructions."""
    if path is None:
        return None, "missing"
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, exc.__class__.__name__
    if not isinstance(loaded, dict):
        return None, "json root must be an object"
    return loaded, None


def _rel_path_or_none(repo_root: Path | None, path: Path | None) -> str | None:
    if repo_root and path:
        return repo_relative_path(repo_root, path) or path.as_posix()
    return path.as_posix() if path else None


def _plugin_hook_commands_are_portable(command: str) -> bool:
    """Return whether a command avoids local absolute plugin-owned paths."""
    tokens = command.split()
    return not any(token.startswith(("/", "~/")) for token in tokens)


def _hook_timeout_shape(hook: dict[str, Any]) -> str:
    if "timeoutSec" in hook:
        return "timeoutSec"
    if "timeout" not in hook:
        return "missing"
    return "seconds" if type(hook.get("timeout")) is int else "invalid"


def _plugin_hooks_contract(
    repo_root: Path | None,
    plugin_root: Path | None,
    manifest: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic checks for Codex-supported plugin bundled hooks."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    if not plugin_root:
        checks.append(
            _platform_check(
                "plugin_hook_contract",
                "not_applicable",
                dimension="plugin_hooks",
                evidence={"reason": "skill is not plugin-owned"},
            )
        )
        return checks, blockers, advisories

    hook_decl = manifest.get("hooks") if isinstance(manifest, dict) else None
    hooks_path = plugin_root / "hooks" / "hooks.json"
    hooks_rel = _rel_path_or_none(repo_root, hooks_path)
    if hook_decl is None and not hooks_path.is_file():
        checks.append(
            _platform_check(
                "plugin_hooks_manifest_declared",
                "not_applicable",
                dimension="plugin_hooks",
                evidence={
                    "declared_hooks": hook_decl,
                    "expected": "./hooks/hooks.json",
                    "reason": "plugin does not declare bundled hooks",
                },
            )
        )
        return checks, blockers, advisories
    if hooks_path.is_file() and hook_decl != "./hooks/hooks.json":
        blockers.append(
            _platform_blocker(
                "plugin_hooks_manifest_path_invalid",
                "Plugin manifests must declare bundled hooks as ./hooks/hooks.json.",
                dimension="plugin_hooks",
                path=_rel_path_or_none(repo_root, _plugin_manifest_path(plugin_root)),
                evidence={"declared_hooks": hook_decl},
            )
        )
    checks.append(
        _platform_check(
            "plugin_hooks_manifest_declared",
            "pass" if hook_decl == "./hooks/hooks.json" else "blocked_validation",
            dimension="plugin_hooks",
            evidence={"declared_hooks": hook_decl, "expected": "./hooks/hooks.json"},
        )
    )
    loaded, error = _read_json_object(hooks_path)
    if error is not None:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_file_unreadable",
                "Bundled plugin hooks must be readable JSON.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"error": error},
            )
        )
        checks.append(
            _platform_check(
                "plugin_hooks_json_parse",
                "blocked_validation",
                dimension="plugin_hooks",
                evidence={"path": hooks_rel, "error": error},
            )
        )
        return checks, blockers, advisories

    hooks_root = loaded.get("hooks") if isinstance(loaded, dict) else None
    hooks_root_ok = isinstance(hooks_root, dict)
    checks.append(
        _platform_check(
            "plugin_hooks_top_level_object",
            "pass" if hooks_root_ok else "blocked_validation",
            dimension="plugin_hooks",
            evidence={"path": hooks_rel},
        )
    )
    if not hooks_root_ok:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_top_level_missing",
                "Codex plugin hook config must use a top-level hooks object.",
                dimension="plugin_hooks",
                path=hooks_rel,
            )
        )
        return checks, blockers, advisories

    hook_count = 0
    unsupported_types: list[str] = []
    timeoutsec_hooks: list[str] = []
    missing_timeout_hooks: list[str] = []
    nonportable_commands: list[str] = []
    invalid_groups: list[str] = []
    for matcher_name, matcher_groups in hooks_root.items():
        if not isinstance(matcher_groups, list):
            invalid_groups.append(str(matcher_name))
            continue
        for group_index, group in enumerate(matcher_groups):
            group_label = f"{matcher_name}[{group_index}]"
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                invalid_groups.append(group_label)
                continue
            for hook_index, hook in enumerate(group["hooks"]):
                hook_label = f"{group_label}.hooks[{hook_index}]"
                if not isinstance(hook, dict):
                    invalid_groups.append(hook_label)
                    continue
                hook_count += 1
                hook_type = str(hook.get("type") or "")
                if hook_type != "command":
                    unsupported_types.append(f"{hook_label}:{hook_type or '<missing>'}")
                timeout_shape = _hook_timeout_shape(hook)
                if timeout_shape == "timeoutSec":
                    timeoutsec_hooks.append(hook_label)
                elif timeout_shape != "seconds":
                    missing_timeout_hooks.append(hook_label)
                command = str(hook.get("command") or "")
                if hook_type == "command" and command and not _plugin_hook_commands_are_portable(command):
                    nonportable_commands.append(hook_label)

    if invalid_groups:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_group_shape_invalid",
                "Each hook matcher group must contain a hooks array.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"invalid_groups": invalid_groups},
            )
        )
    if unsupported_types:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_unsupported_type",
                "Plugin hooks currently support command hooks only.",
                dimension="runtime_support",
                path=hooks_rel,
                evidence={"unsupported_types": unsupported_types},
            )
        )
    if timeoutsec_hooks:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_timeoutsec_unsupported",
                "Command hooks must use timeout in seconds; timeoutSec is unsupported.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"hooks": timeoutsec_hooks},
            )
        )
    if missing_timeout_hooks:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_timeout_missing",
                "Command hooks must declare timeout as an integer number of seconds.",
                dimension="plugin_hooks",
                path=hooks_rel,
                evidence={"hooks": missing_timeout_hooks},
            )
        )
    if nonportable_commands:
        blockers.append(
            _platform_blocker(
                "plugin_hooks_command_not_portable",
                "Plugin-owned hook commands must reference ${PLUGIN_ROOT} or ${PLUGIN_DATA}.",
                dimension="path_portability",
                path=hooks_rel,
                evidence={"hooks": nonportable_commands},
            )
        )
    checks.append(
        _platform_check(
            "plugin_hooks_runtime_supported_shape",
            "blocked_validation"
            if invalid_groups or unsupported_types or timeoutsec_hooks or missing_timeout_hooks
            else "pass",
            dimension="plugin_hooks",
            evidence={
                "hook_count": hook_count,
                "invalid_groups": invalid_groups,
                "unsupported_types": unsupported_types,
                "timeoutSec_hooks": timeoutsec_hooks,
                "missing_timeout_hooks": missing_timeout_hooks,
            },
        )
    )
    checks.append(
        _platform_check(
            "plugin_hooks_command_portability",
            "pass" if not nonportable_commands else "blocked_validation",
            dimension="path_portability",
            evidence={"nonportable_commands": nonportable_commands},
        )
    )
    if hook_count == 0:
        advisories.append(
            _platform_advisory(
                "plugin_hooks_empty",
                "Bundled hook files should contain at least one supported command hook when declared.",
                dimension="plugin_hooks",
                path=hooks_rel,
            )
        )
    return checks, blockers, advisories


def openai_platform_compat_contract(
    repo_root: Path | None,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic OpenAI-facing skill and plugin compatibility checks."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    source_rel = repo_relative_path(repo_root, source_path) if repo_root and source_path else None
    openai_fields = read_agents_openai_yaml_fields(source_path)
    interface = openai_fields.get("interface")
    short_description = ""
    if isinstance(interface, dict):
        short_description = str(interface.get("short_description") or "").strip()
    skill_description = str(frontmatter.get("description") or "").strip()
    checks.append(
        _platform_check(
            "skill_metadata_projection",
            "pass" if frontmatter.get("name") and skill_description else "blocked_validation",
            dimension="metadata_projection",
            evidence={
                "name_present": bool(frontmatter.get("name")),
                "description_present": bool(skill_description),
                "short_description_present": bool(short_description),
            },
        )
    )
    if not frontmatter.get("name") or not skill_description:
        blockers.append(
            _platform_blocker(
                "openai_skill_metadata_incomplete",
                "OpenAI-facing skill projection requires name and description metadata.",
                dimension="metadata_projection",
                path=source_rel,
            )
        )
    if not short_description:
        advisories.append(
            _platform_advisory(
                "openai_short_description_missing",
                "agents/openai.yaml should expose interface.short_description for browseable surfaces.",
                dimension="metadata_projection",
                path=source_rel,
            )
        )

    plugin_root = _plugin_root_for_source(repo_root, source_path)
    plugin_manifest_path = _plugin_manifest_path(plugin_root)
    plugin_manifest, manifest_error = _read_json_object(plugin_manifest_path)
    if plugin_root:
        checks.append(
            _platform_check(
                "plugin_manifest_parse",
                "pass" if manifest_error is None else "blocked_validation",
                dimension="plugin_manifest",
                evidence={
                    "path": _rel_path_or_none(repo_root, plugin_manifest_path),
                    "error": manifest_error,
                },
            )
        )
        if manifest_error is not None:
            blockers.append(
                _platform_blocker(
                    "plugin_manifest_unreadable",
                    "Plugin-owned skills must have a readable plugin.json manifest.",
                    dimension="plugin_manifest",
                    path=_rel_path_or_none(repo_root, plugin_manifest_path),
                    evidence={"error": manifest_error},
                )
            )
    hook_checks, hook_blockers, hook_advisories = _plugin_hooks_contract(
        repo_root,
        plugin_root,
        plugin_manifest,
    )
    checks.extend(hook_checks)
    blockers.extend(hook_blockers)
    advisories.extend(hook_advisories)

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": OPENAI_PLATFORM_COMPAT_SCHEMA_VERSION,
        "policy": "deterministic_openai_skill_and_plugin_projection",
        "required_for_package_readiness": True,
        "status": status,
        "target_kind": "plugin_skill" if plugin_root else "skill",
        "rubric": {
            "source": "openai-platform-and-codex-plugin-hook-contract",
            "dimensions": [
                "metadata_projection",
                "plugin_manifest",
                "plugin_hooks",
                "path_portability",
                "runtime_support",
            ],
        },
        "checks": checks,
        "blockers": blockers,
        "advisories": advisories,
        "what_this_proves": [
            "openai_facing_metadata_shape_checked",
            "plugin_manifest_hook_pointer_checked",
            "bundled_command_hook_shape_checked",
            "plugin_command_path_portability_checked",
        ] if status == "pass" else [],
        "what_this_does_not_prove": [
            "hosted_openai_acceptance",
            "runtime_plugin_hook_execution",
            "behavioral_eval_pass",
            "marketplace_publication",
        ],
    }


def skill_agent_toml_paths(repo_root: Path | None, skill_md: Path | None) -> list[str]:
    """Return optional per-skill agent TOML runtime profiles."""
    if not skill_md:
        return []
    agents_dir = skill_md.parent / "agents"
    if not agents_dir.is_dir():
        return []
    paths: list[str] = []
    for candidate in sorted(agents_dir.glob("*.toml")):
        if repo_root:
            paths.append(repo_relative_path(repo_root, candidate) or candidate.as_posix())
        else:
            paths.append(candidate.as_posix())
    return paths


def skill_command_candidates(text: str) -> list[str]:
    """Extract a conservative command list from skill prose."""
    commands: list[str] = []
    for line in text.splitlines():
        stripped = normalized_command_candidate(line)
        if not stripped:
            continue
        if stripped and stripped not in commands:
            commands.append(stripped)
    return commands[:8]


def normalized_command_candidate(line: str) -> str | None:
    """Return a command only when the line itself is shaped like a command."""
    stripped = line.strip().strip(chr(96))
    while stripped.startswith(("-", "*")):
        stripped = stripped[1:].strip()
    if len(stripped) >= 3 and stripped[0].isdigit() and stripped[1] == ".":
        stripped = stripped[2:].strip()
    stripped = stripped.strip(chr(96))
    if stripped.lower().startswith("command:"):
        stripped = stripped.split(":", 1)[1].strip().strip(chr(96))
    for prefix in ("./bin/ask ", "python3 ", "bash "):
        if stripped.startswith(prefix):
            return stripped
    return None


def local_evidence_provider_status() -> dict[str, Any]:
    """Return optional ~/.agents observability providers for package evidence enrichment."""
    agents_root = Path.home() / ".agents"
    providers: list[dict[str, Any]] = []
    provider_specs = [
        {
            "name": "otel_collector",
            "root": agents_root / "otel-collector",
            "signals": ["otlp_raw", "processed_stats"],
            "stats": agents_root / "otel-collector" / "data" / "processed" / "stats.json",
        },
        {
            "name": "session_collector",
            "root": agents_root / "session-collector",
            "signals": ["normalized_sessions", "session_evidence"],
            "stats": None,
        },
        {
            "name": "observability_stack",
            "root": agents_root / "observability-stack",
            "signals": ["jaeger", "prometheus", "loki", "grafana"],
            "stats": None,
        },
    ]
    available_count = 0
    for spec in provider_specs:
        root = spec["root"]
        available = root.is_dir()
        available_count += int(available)
        stats_path = spec["stats"]
        stats_freshness = "not_applicable"
        if stats_path is not None:
            stats_freshness = "present" if stats_path.is_file() else "missing"
        providers.append(
            {
                "name": spec["name"],
                "optional": True,
                "authority": "enrichment_only",
                "status": "available" if available else "missing",
                "root": root.as_posix(),
                "signals": spec["signals"],
                "stats_freshness": stats_freshness,
            }
        )
    if available_count >= 2:
        telemetry_confidence = "enriched"
    elif available_count == 1:
        telemetry_confidence = "partial"
    else:
        telemetry_confidence = "not_available"
    return {
        "schema_version": "skill-evidence-providers.v1",
        "authority": "artifacts_decide_telemetry_explains",
        "telemetry_confidence": telemetry_confidence,
        "providers": providers,
        "required_for_package_readiness": False,
    }


def sdk_package_contract(
    repo_root: Path | None,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the portable Skills SDK package contract view for agents."""
    text = skill_markdown_text(source_path)
    reference_contract = read_reference_contract(source_path)
    reference_quality = reference_quality_contract(repo_root, source_path)
    progressive_disclosure = progressive_disclosure_contract(repo_root, source_path, text)
    writing_quality = writing_quality_contract(
        repo_root,
        source_path,
        frontmatter,
        text,
        progressive_disclosure,
    )
    authoring = authoring_contract(
        repo_root,
        source_path,
        frontmatter,
        reference_contract,
        text,
    )
    openai_platform_compat = openai_platform_compat_contract(repo_root, source_path, frontmatter)
    identity_and_assets = identity_and_assets_contract(repo_root, source_path, frontmatter)
    knowledge_capsules = knowledge_capsule_first_party_contract(repo_root, source_path, text)
    workflow_contract = skillflow_contract(repo_root, source_path, reference_contract)
    optimization_readiness = optimization_contract(repo_root, source_path, reference_contract)
    eval_paths = skill_eval_paths(repo_root, source_path)
    agents_openai_path = skill_package_file_path(repo_root, source_path, "agents/openai.yaml")
    references_contract_path = skill_package_file_path(
        repo_root,
        source_path,
        "references/contract.yaml",
    )
    task_profile_path = skill_package_file_path(
        repo_root,
        source_path,
        "references/task-profile.json",
    )
    agent_toml_paths = skill_agent_toml_paths(repo_root, source_path)
    package_values = package_field_values(frontmatter)
    commands = skill_command_candidates(text)
    if not commands:
        commands = _string_list(reference_contract.get("commands"))
    policy = frontmatter.get("policy")
    permission_profile = reference_contract.get("permission_profile")
    if not permission_profile and isinstance(policy, dict) and policy:
        permission_profile = policy
    evidence_policy = (
        reference_contract.get("evidence_policy")
        or reference_contract.get("observability")
        or ("Validation section declared" if markdown_heading_declared(text, "Validation") else None)
    )
    values = {
        "agent_metadata": {
            "declared": bool(agents_openai_path),
            "path": agents_openai_path,
            "format": "agents/openai.yaml",
            "authority": "skill_interface_and_dependency_metadata",
        },
        "reference_contract": {
            "declared": bool(references_contract_path),
            "path": references_contract_path,
            "format": "references/contract.yaml",
            "authority": "sdk_package_contract",
        },
        "reference_quality": reference_quality,
        "writing_quality": writing_quality,
        "authoring_contract": authoring,
        "openai_platform_compat": openai_platform_compat,
        "purpose": reference_contract.get("purpose") or frontmatter.get("description"),
        "inputs": reference_contract.get("inputs")
        or ("declared_in_skill_md" if markdown_heading_declared(text, "Inputs") else None),
        "outputs": reference_contract.get("outputs")
        or ("declared_in_skill_md" if markdown_heading_declared(text, "Outputs") else None),
        "commands": commands,
        "permission_profile": permission_profile,
        "portability_profile": {
            "compatible_roles": package_values["compatible_roles"],
            "runtime_needs": package_values["runtime_needs"],
            "provenance": package_values["provenance"],
            "share_readiness": package_values["share_readiness"],
        },
        "evals": {
            "declared": bool(eval_paths),
            "paths": eval_paths,
        },
        "task_profile": {
            "declared": bool(task_profile_path),
            "path": task_profile_path,
        },
        "evidence_policy": evidence_policy,
        "budget_classification": reference_contract.get("budget_classification"),
        "workflow_contract": workflow_contract,
        "optimization_contract": optimization_readiness,
        "knowledge_capsules": knowledge_capsules,
    }
    present = sorted(
        field for field, value in values.items() if sdk_contract_field_present(field, value)
    )
    missing = sorted(field for field in SDK_PACKAGE_CONTRACT_FIELDS if field not in present)
    source_rel = repo_relative_path(repo_root, source_path) if repo_root and source_path else None
    skill_dir = source_path.parent if source_path else None
    editable_paths = [
        repo_relative_path(repo_root, skill_dir) or skill_dir.as_posix()
    ] if repo_root and skill_dir else []
    return {
        "schema_version": SDK_PACKAGE_CONTRACT_SCHEMA_VERSION,
        "required_fields": {
            "present": present,
            "missing": missing,
        },
        "values": values,
        "progressive_disclosure": {
            "skill_md_declared": bool(source_path and source_path.is_file()),
            **progressive_disclosure,
            "agent_metadata_declared": bool(agents_openai_path),
            "references_contract_declared": bool(reference_contract),
            "references_quality_status": reference_quality["status"],
            "writing_quality_status": writing_quality["status"],
            "authoring_contract_status": authoring["status"],
            "openai_platform_compat_status": openai_platform_compat["status"],
            "evals_declared": bool(eval_paths),
            "task_profile_declared": bool(task_profile_path),
            "agent_tomls_declared": bool(agent_toml_paths),
            "agent_tomls": agent_toml_paths,
            "workflow_declared": bool(workflow_contract["declared"]),
            "workflow_status": workflow_contract["status"],
            "execution_mode": workflow_contract["execution_mode"],
            "optimization_declared": bool(optimization_readiness["enabled"]),
            "optimization_status": optimization_readiness["status"],
            "optimization_mode": optimization_readiness["optimizer_mode"],
            "knowledge_capsules_declared": bool(knowledge_capsules["manifest_declared"]),
            "knowledge_capsules_first_party_ready": bool(knowledge_capsules["ready"]),
        },
        "identity_and_assets": identity_and_assets,
        "knowledge_capsules": knowledge_capsules,
        "agent_contract": {
            "source_of_truth": source_rel,
            "editable_paths": editable_paths,
            "generated_paths": [".agents/skills/**"],
            "forbidden_actions": [
                "edit_generated_runtime_projection",
                "claim_eval_pass_as_runtime_proof",
            ],
            "next_safe_command": "./bin/ask skills package <handle-or-path> --checkout-test --json --robot",
            "what_this_proves": ["package_shape", "declared_metadata", "local_file_presence"],
            "what_this_does_not_prove": ["runtime_behavior", "security_posture", "human_approval"],
            "workflow_policy": (
                "SKILL.md remains the judgment layer; workflows/skillflow.json is optional "
                "deterministic mechanics. Runtime adaptation inside declared graph bounds may be "
                "autonomous; durable graph amendments require review."
            ),
            "optimization_policy": (
                "Skill optimization may produce bounded candidate artifacts and rejected-edit "
                "evidence. Canonical SKILL.md promotion requires declared gates, anti-cheat "
                "checks, and review."
            ),
            "agent_toml_policy": (
                "optional_per_skill_runtime_profiles; required only when the skill contract "
                "declares a dedicated subagent or persona runtime"
            ),
        },
        "evidence_providers": local_evidence_provider_status(),
    }
__all__ = [name for name in globals() if not name.startswith("__")]
