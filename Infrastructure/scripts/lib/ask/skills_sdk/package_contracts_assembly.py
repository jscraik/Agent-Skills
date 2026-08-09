from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403
from .package_contracts_workflow import *  # noqa: F403
from .package_contracts_optimization import *  # noqa: F403
from .package_contracts_reference_quality import *  # noqa: F403
from .package_contracts_writing_support import *  # noqa: F403
from .package_contracts_writing_quality import *  # noqa: F403
from .package_contracts_platform import *  # noqa: F403

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


def sdk_contract_field_present(field: str, value: Any) -> bool:
    """Return whether an SDK package contract field has real declared evidence."""
    if field == "evals" and isinstance(value, dict):
        return bool(value.get("declared"))
    if field in {"agent_metadata", "reference_contract", "task_profile"} and isinstance(value, dict):
        return bool(value.get("declared"))
    if field == "portability_profile" and isinstance(value, dict):
        return any(bool(item) for item in value.values())
    return bool(value)


def skill_package_contract(
    repo_root: Path,
    source_path: Path | None,
    frontmatter: dict[str, Any],
) -> dict[str, Any]:
    """Return the Codex-native package contract for SKILL.md plus agents/openai.yaml."""
    openai_fields = read_agents_openai_yaml_fields(source_path)
    interface = frontmatter.get("interface")
    if not isinstance(interface, dict):
        interface = {}
    openai_interface = openai_fields.get("interface")
    if isinstance(openai_interface, dict):
        interface = {**interface, **openai_interface}

    dependencies = frontmatter.get("dependencies")
    if not isinstance(dependencies, dict):
        dependencies = {}
    openai_dependencies = openai_fields.get("dependencies")
    if isinstance(openai_dependencies, dict):
        dependencies = {**dependencies, **openai_dependencies}
    policy = frontmatter.get("policy")
    if not isinstance(policy, dict):
        policy = {}
    openai_policy = openai_fields.get("policy")
    if isinstance(openai_policy, dict):
        policy = {**policy, **openai_policy}

    codex_metadata = {
        "name": frontmatter.get("name"),
        "description": frontmatter.get("description"),
        "short_description": frontmatter.get("short_description")
        or interface.get("short_description"),
        "interface": interface or None,
        "dependencies": dependencies or None,
        "policy": policy or None,
        "scope": frontmatter.get("scope"),
        "plugin_id": frontmatter.get("plugin_id"),
    }
    required_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if codex_metadata.get(field)
    )
    required_missing = sorted(
        field for field in CODEX_SKILL_PACKAGE_REQUIRED_FIELDS if not codex_metadata.get(field)
    )
    optional_present = sorted(
        field for field in CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS if codex_metadata.get(field)
    )
    source_rel = repo_relative_path(repo_root, source_path) if source_path else None
    openai_rel = None
    if source_path:
        openai_path = source_path.parent / "agents" / "openai.yaml"
        if openai_path.is_file():
            openai_rel = repo_relative_path(repo_root, openai_path)
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": source_rel,
            "agents_openai_yaml": openai_rel,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": codex_metadata,
        "required_fields": {
            "present": required_present,
            "missing": required_missing,
        },
        "optional_fields": {
            "present": optional_present,
        },
        "compatibility_status": "blocked_validation" if required_missing else "compatible",
    }


def empty_skill_package_contract() -> dict[str, Any]:
    """Return a package contract for unresolved or missing source paths."""
    return {
        "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
        "source_files": {
            "skill_md": None,
            "agents_openai_yaml": None,
        },
        "codex_abi_source": codex_skill_package_abi_source(),
        "metadata": {
            "name": None,
            "description": None,
            "short_description": None,
            "interface": None,
            "dependencies": None,
            "policy": None,
            "scope": None,
            "plugin_id": None,
        },
        "required_fields": {
            "present": [],
            "missing": list(CODEX_SKILL_PACKAGE_REQUIRED_FIELDS),
        },
        "optional_fields": {
            "present": [],
        },
        "compatibility_status": "blocked_missing_source",
    }

__all__ = [name for name in globals() if not name.startswith("__")]
