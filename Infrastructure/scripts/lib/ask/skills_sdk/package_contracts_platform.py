from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403

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

__all__ = [name for name in globals() if not name.startswith("__")]
