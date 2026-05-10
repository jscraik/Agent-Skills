#!/usr/bin/env python3
"""Validate Harness Engineering subagent routing against runtime roles."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = ROOT / "Plugins/harness-engineering"
ROUTING_MAP = PLUGIN_ROOT / "references/routing-map.json"
SUBAGENT_ROUTING = PLUGIN_ROOT / "references/subagent-routing.md"
SUBAGENT_CALL_CONTRACT = PLUGIN_ROOT / "references/subagent-call-contract.md"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
DEFAULT_MANIFEST = Path("~/.codex/agents/manifest.json").expanduser()


@dataclass(frozen=True)
class ValidationError:
    path: Path
    message: str

    def format(self) -> str:
        try:
            display_path = self.path.relative_to(ROOT)
        except ValueError:
            display_path = self.path
        return f"{display_path}: {self.message}"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: {exc}") from exc


def manifest_roles(path: Path) -> set[str]:
    data = load_json(path)
    records: Any
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("agents"), list):
        records = data["agents"]
    else:
        raise RuntimeError(
            f"{path} must be a top-level array or an object with an agents array"
        )

    roles: set[str] = set()
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("role"), str):
            roles.add(record["role"])
    return roles


def mapped_stage_roles(routing_map: dict[str, Any]) -> dict[str, set[str]]:
    stage_map = routing_map.get("subagent_stage_map")
    if not isinstance(stage_map, dict):
        raise RuntimeError(f"{ROUTING_MAP} missing subagent_stage_map object")

    mapped: dict[str, set[str]] = {}
    for stage, policy in stage_map.items():
        if not isinstance(policy, dict):
            raise RuntimeError(f"{stage} policy must be an object")
        roles: set[str] = set()
        for key in ("baseline_roles", "conditional_roles"):
            value = policy.get(key, [])
            if not isinstance(value, list) or not all(isinstance(role, str) for role in value):
                raise RuntimeError(f"{stage}.{key} must be a list of strings")
            roles.update(value)
        mapped[stage] = roles
    return mapped


def validate_roles(
    routing_map: dict[str, Any],
    mapped_roles_by_stage: dict[str, set[str]],
    available_roles: set[str],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    mapped_roles = set().union(*mapped_roles_by_stage.values()) if mapped_roles_by_stage else set()

    for stage, roles in sorted(mapped_roles_by_stage.items()):
        missing = sorted(roles - available_roles)
        if missing:
            errors.append(
                ValidationError(
                    ROUTING_MAP,
                    f"{stage} maps roles missing from manifest: {', '.join(missing)}",
                )
            )

    inventory_policy = routing_map.get("subagent_inventory_policy")
    if not isinstance(inventory_policy, dict):
        errors.append(
            ValidationError(
                ROUTING_MAP,
                "missing subagent_inventory_policy object for HE-relevant role governance",
            )
        )
        return errors

    he_relevant_roles = inventory_policy.get("he_relevant_roles", [])
    if not isinstance(he_relevant_roles, list) or not all(
        isinstance(role, str) for role in he_relevant_roles
    ):
        errors.append(
            ValidationError(ROUTING_MAP, "subagent_inventory_policy.he_relevant_roles must be strings")
        )
    else:
        unmapped_relevant = sorted((set(he_relevant_roles) & available_roles) - mapped_roles)
        if unmapped_relevant:
            errors.append(
                ValidationError(
                    ROUTING_MAP,
                    "HE-relevant manifest roles are not mapped to any stage: "
                    + ", ".join(unmapped_relevant),
                )
            )

    retired_roles = inventory_policy.get("retired_roles", [])
    if not isinstance(retired_roles, list) or not all(
        isinstance(role, str) for role in retired_roles
    ):
        errors.append(
            ValidationError(ROUTING_MAP, "subagent_inventory_policy.retired_roles must be strings")
        )
    else:
        present_retired = sorted(set(retired_roles) & available_roles)
        if present_retired:
            errors.append(
                ValidationError(
                    ROUTING_MAP,
                    "retired roles are still present in manifest: "
                    + ", ".join(present_retired),
                )
            )

    return errors


def validate_reference_docs() -> list[ValidationError]:
    errors: list[ValidationError] = []
    routing_text = SUBAGENT_ROUTING.read_text(encoding="utf-8")
    contract_text = SUBAGENT_CALL_CONTRACT.read_text(encoding="utf-8")

    required_routing_phrases = (
        "Use [routing-map.json](routing-map.json) as the machine-readable source of truth",
        "Do not invent or prefer `he-*` role aliases",
        "Route missing role creation or installation to `[[codex-agent-creator]]`",
    )
    for phrase in required_routing_phrases:
        if phrase not in routing_text:
            errors.append(ValidationError(SUBAGENT_ROUTING, f"missing phrase: {phrase}"))

    stale_phrases = (
        "Prefer `he-*` roles",
        "preferring `he-*` roles",
        "he-agent-native-reviewer",
        "he-testing-reviewer",
        "he-repo-research-analyst",
        "he-learnings-researcher",
    )
    for phrase in stale_phrases:
        if phrase in routing_text:
            errors.append(ValidationError(SUBAGENT_ROUTING, f"stale alias phrase: {phrase}"))

    required_contract_phrases = (
        "Use the exact role names from `routing-map.json`",
        "Call `spawn_agent(agent_type=<role>)` only for roles present in the manifest",
        "`roles_missing`",
    )
    for phrase in required_contract_phrases:
        if phrase not in contract_text:
            errors.append(ValidationError(SUBAGENT_CALL_CONTRACT, f"missing phrase: {phrase}"))

    return errors


def validate_stage_entrypoints(changed_files: set[Path] | None = None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for skill_path in sorted(SKILLS_ROOT.glob("**/SKILL.md")):
        relative_skill_path = skill_path.relative_to(ROOT)
        if changed_files is not None and relative_skill_path not in changed_files:
            continue
        text = skill_path.read_text(encoding="utf-8")
        if "subagent-call-contract.md" not in text:
            errors.append(
                ValidationError(
                    skill_path,
                    "must link the shared subagent-call-contract.md reference",
                )
            )
    return errors


def validate_router_fragments() -> list[ValidationError]:
    errors: list[ValidationError] = []
    for path in sorted((SKILLS_ROOT / "he-router/references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "preferring `he-*` roles" in text or "has no `he-*` mapping" in text:
            errors.append(
                ValidationError(
                    path,
                    "stale he-* role-alias preference must use canonical manifest roles",
                )
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Harness Engineering subagent role routing."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to codex agents manifest; defaults to ~/.codex/agents/manifest.json.",
    )
    parser.add_argument(
        "--routing-map",
        type=Path,
        default=ROUTING_MAP,
        help="Path to Harness Engineering routing map; defaults to plugin routing-map.json.",
    )
    parser.add_argument(
        "--changed-files",
        nargs="*",
        default=None,
        help="Optional repo-relative file list used to scope stage entrypoint checks.",
    )
    args = parser.parse_args()

    try:
        changed_files = (
            {Path(path.lstrip("./")) for path in args.changed_files}
            if args.changed_files is not None
            else None
        )
        routing_map = load_json(args.routing_map)
        mapped_roles = mapped_stage_roles(routing_map)
        available_roles = manifest_roles(args.manifest.expanduser())
        errors = [
            *validate_roles(routing_map, mapped_roles, available_roles),
            *validate_reference_docs(),
            *validate_stage_entrypoints(changed_files),
            *validate_router_fragments(),
        ]
    except RuntimeError as exc:
        print(f"[he-subagent-routing] ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("[he-subagent-routing] ERROR: routing contract violations:", file=sys.stderr)
        for error in errors:
            print(f"  - {error.format()}", file=sys.stderr)
        return 1

    print(
        "[he-subagent-routing] ok: "
        f"{len(mapped_roles)} stages, {len(available_roles)} manifest roles"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
