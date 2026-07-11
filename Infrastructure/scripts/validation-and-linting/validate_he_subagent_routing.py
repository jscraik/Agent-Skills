#!/usr/bin/env python3
"""Validate Harness Engineering capability routing for generic Desktop collaborators."""

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
ACTIVE_CONTRACTS = (
    PLUGIN_ROOT / "skills/he-strategy/references/strategy-output-contract.md",
    PLUGIN_ROOT / "references/skills/he-linear-plan/linear-plan-output-contract.md",
    PLUGIN_ROOT / "skills/he-improve/references/contract.yaml",
)


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


def mapped_stage_capabilities(routing_map: dict[str, Any]) -> dict[str, set[str]]:
    stage_map = routing_map.get("subagent_stage_map")
    if not isinstance(stage_map, dict):
        raise RuntimeError(f"{ROUTING_MAP} missing subagent_stage_map object")

    mapped: dict[str, set[str]] = {}
    for stage, policy in stage_map.items():
        if not isinstance(policy, dict):
            raise RuntimeError(f"{stage} policy must be an object")
        capabilities: set[str] = set()
        for key in ("baseline_capabilities", "conditional_capabilities"):
            value = policy.get(key, [])
            if not isinstance(value, list) or not all(isinstance(capability, str) and capability.strip() for capability in value):
                raise RuntimeError(f"{stage}.{key} must be a list of strings")
            capabilities.update(value)
        if not capabilities:
            raise RuntimeError(f"{stage} must declare at least one task capability")
        mapped[stage] = capabilities
    return mapped


def validate_capability_contract(routing_map: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    contract = routing_map.get("desktop_collaboration_contract")
    if not isinstance(contract, dict):
        errors.append(
            ValidationError(
                ROUTING_MAP,
                "missing desktop_collaboration_contract object",
            )
        )
        return errors
    if contract.get("selection") != "task_capability":
        errors.append(ValidationError(ROUTING_MAP, "desktop_collaboration_contract.selection must be task_capability"))
    if contract.get("named_role_selection") != "unsupported":
        errors.append(ValidationError(ROUTING_MAP, "desktop_collaboration_contract.named_role_selection must be unsupported"))
    packet_fields = contract.get("required_packet_fields")
    required_fields = {"task_capability", "authority", "evidence_requirements", "stop_condition"}
    if not isinstance(packet_fields, list) or not required_fields.issubset(set(packet_fields)):
        errors.append(ValidationError(ROUTING_MAP, "desktop_collaboration_contract.required_packet_fields must include task_capability, authority, evidence_requirements, and stop_condition"))

    return errors


def validate_reference_docs() -> list[ValidationError]:
    errors: list[ValidationError] = []
    routing_text = SUBAGENT_ROUTING.read_text(encoding="utf-8")
    contract_text = SUBAGENT_CALL_CONTRACT.read_text(encoding="utf-8")

    required_routing_phrases = (
        "Use [routing-map.json](routing-map.json) as the machine-readable source of truth",
        "Route by task capability, authority, evidence requirements, and stop condition",
        "Do not use `~/.codex/agents/manifest.json` as a runtime availability source",
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
        "Use the capability packet declared by `routing-map.json`",
        "Do not pass `agent_type`",
        "`capabilities_not_covered`",
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
    for path in sorted((SKILLS_ROOT / "he-reconcile/references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "preferring `he-*` roles" in text or "has no `he-*` mapping" in text:
            errors.append(
                ValidationError(
                    path,
                    "stale he-* role-alias preference must use canonical manifest roles",
                )
            )
    return errors


def validate_active_contracts() -> list[ValidationError]:
    """Reject retired named-role fields in active HE contracts."""
    errors: list[ValidationError] = []
    stale_phrases = (
        "roles_used",
        "roles_recommended",
        "roles_missing",
        "manifest checks",
        "codex-agent-creator fallback",
        "when roles exist",
        "helper-role availability",
    )
    for path in ACTIVE_CONTRACTS:
        text = path.read_text(encoding="utf-8")
        for phrase in stale_phrases:
            if phrase in text:
                errors.append(
                    ValidationError(
                        path,
                        f"stale named-role contract phrase: {phrase}",
                    )
                )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Harness Engineering generic Desktop collaborator routing."
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
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> tuple[dict[str, set[str]], list[ValidationError]]:
    changed_files = (
        {Path(path.lstrip("./")) for path in args.changed_files}
        if args.changed_files is not None
        else None
    )
    routing_map = load_json(args.routing_map)
    mapped_capabilities = mapped_stage_capabilities(routing_map)
    errors = [
        *validate_capability_contract(routing_map),
        *validate_reference_docs(),
        *validate_stage_entrypoints(changed_files),
        *validate_router_fragments(),
        *validate_active_contracts(),
    ]
    return mapped_capabilities, errors


def main() -> int:
    args = parse_args()

    try:
        mapped_capabilities, errors = validate_inputs(args)
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
        f"{len(mapped_capabilities)} stages, generic Desktop capability routing"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
