#!/usr/bin/env python3
"""Canonical selection/discovery policy shared by route, discovery, and sync."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from typing import Any, Iterable

POLICY_VERSION = "2026-04-25.v20"

PROJECTION_MODE_CHOICES: tuple[str, ...] = ("flat", "rooted", "hybrid")

ROOT_SKILL_SET_NAMES: tuple[str, ...] = (
    "agent-ops",
    "frontend-ui",
    "backend-platform",
    "product-strategy",
    "security-ops",
    "content-publishing",
    "mobile-native",
    "skill-factory",
    "plugin-factory",
    "harness-engineering",
)

# Canonical roots for repo-owned skills.
REPO_SCAN_ROOTS: tuple[str, ...] = (
    "Skills",
)

# Plugin-bundled skill roots scanned by sync scripts.
PLUGIN_SKILL_ROOT_GLOB = "./Plugins/*/skills"

# Ignore implementation/support subtrees that are not runtime-selectable skills.
EXCLUDED_SCAN_SEGMENTS: tuple[str, ...] = (
    "_archive",
    "agents",
    "assets",
    "examples",
    "fixtures",
    "references",
    "rules",
    "scripts",
    "templates",
)

# Internal skills intentionally hidden from flat runtime discovery.
HIDDEN_FLAT_SKILL_NAMES: tuple[str, ...] = (
    "browser",
    "circleci",
    "linear",
    "skillgrade-graders",
    "skillgrade-setup",
)

# Default flat-runtime surface to keep skill-context pressure bounded.
# Skills outside this list remain available in repository scan modes but are
# excluded from the default always-loaded flat skill view.
DEFAULT_VISIBLE_FLAT_SKILL_NAMES: tuple[str, ...] = (
    "agents-md",
    "keep-codex-fast",
    "autofix",
    "autoresearch",
    "bootstrap",
    "codex-agent-creator",
    "codex-automation-architect",
    "codex-hooks-builder",
    "codex-review",
    "code-fixes-triage",
    "coding-harness",
    "context7",
    "docs-expert",
    "fix-mise",
    "improve-codebase-architecture",
    "npm-release",
    "pnpm-manager",
    "project-brain",
    "simplify",
    "skill-pr-delivery",
    "triage",
    "ubiquitous-language",
    "unslopify",
    "verification-before-completion",
)

# Plugin-owned skills stay on their plugin first-level picker surface. Do not
# promote them into flat runtime discovery, or Codex can render duplicate rows.
PLUGIN_VISIBLE_ROUTER_SKILL_NAMES: tuple[str, ...] = ()

# Plugin lane skills hidden from default flat discovery.
PLUGIN_HIDDEN_LANE_SKILL_NAMES: tuple[str, ...] = (
    "he-goal-governor-archive",
    "he-phase-heartbeat",
)

# Skills intentionally routed through the hidden `.system` lane. OpenAI-owned
# skills stay as preserved system sources; local factory packages may attach
# references/evals beside them, but must not fork their `SKILL.md` bodies.
SYSTEM_BRIDGE_SKILL_NAMES: tuple[str, ...] = (
    "imagegen",
    "openai-docs",
    "plugin-creator",
    "plugin-installer",
    "skill-creator",
    "skill-installer",
)

# System bridge skills that are intentionally visible on the default catalog
# surface. Other bridge skills remain available through explicit routing.
DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILL_NAMES: tuple[str, ...] = (
    "imagegen",
    "openai-docs",
)

# Runtime projection modes. These are intentionally outside the selection
# policy identity: mode support is command behavior, not a change to which
# flat skills are selected by default.
DEFAULT_PROJECTION_MODE = "flat"
SUPPORTED_PROJECTION_MODES: tuple[str, ...] = (
    "flat",
    "rooted",
)
PROJECTION_MODE_ALIASES: dict[str, str] = {
    "skill-tree": "rooted",
}
DEFERRED_PROJECTION_MODES: tuple[str, ...] = (
    "hybrid",
)

def repo_scan_roots_with_prefix() -> tuple[str, ...]:
    """
    Builds repository scan roots prefixed with "./".
    
    Each entry from REPO_SCAN_ROOTS is returned with a "./" prefix to ensure relative-path scanning.
    
    Returns:
    	tuple[str, ...]: Tuple of scan-root strings, each prefixed with "./".
    """
    return tuple(f"./{root}" for root in REPO_SCAN_ROOTS)


def payload() -> dict[str, Any]:
    """
    Produce a stable dictionary of all inputs that define the selection policy identity.
    
    Tuples are converted to lists to ensure deterministic JSON serialization for hashing and storage.
    
    Returns:
        payload (dict[str, Any]): Mapping with the following keys:
            - "policy_version": str
            - "root_skill_set_names": list[str]
            - "repo_scan_roots": list[str]
            - "plugin_skill_root_glob": str
            - "excluded_scan_segments": list[str]
            - "hidden_flat_skill_names": list[str]
            - "default_visible_flat_skill_names": list[str]
            - "plugin_visible_router_skill_names": list[str]
            - "plugin_hidden_lane_skill_names": list[str]
            - "system_bridge_skill_names": list[str]
            - "default_visible_system_bridge_skill_names": list[str]
    """
    return {
        "policy_version": POLICY_VERSION,
        "root_skill_set_names": list(ROOT_SKILL_SET_NAMES),
        "repo_scan_roots": list(REPO_SCAN_ROOTS),
        "plugin_skill_root_glob": PLUGIN_SKILL_ROOT_GLOB,
        "excluded_scan_segments": list(EXCLUDED_SCAN_SEGMENTS),
        "hidden_flat_skill_names": list(HIDDEN_FLAT_SKILL_NAMES),
        "default_visible_flat_skill_names": list(DEFAULT_VISIBLE_FLAT_SKILL_NAMES),
        "plugin_visible_router_skill_names": list(PLUGIN_VISIBLE_ROUTER_SKILL_NAMES),
        "plugin_hidden_lane_skill_names": list(PLUGIN_HIDDEN_LANE_SKILL_NAMES),
        "system_bridge_skill_names": list(SYSTEM_BRIDGE_SKILL_NAMES),
        "default_visible_system_bridge_skill_names": list(
            DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILL_NAMES
        ),
    }


def policy_identity() -> str:
    canonical = json.dumps(payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _shell_array(name: str, values: Iterable[str]) -> str:
    encoded = " ".join(shlex.quote(value) for value in values)
    return f"{name}=({encoded})"


def render_shell() -> str:
    """
    Produce a newline-delimited shell fragment defining selection policy variables.
    
    The fragment contains a quoted `SELECTION_POLICY_IDENTITY`, shell-array assignments for repo scan roots, excluded segments, hidden flat skills, plugin-visible router skills and plugin-hidden lane skills, and a quoted `SELECTION_POLICY_PLUGIN_SKILL_ROOT_GLOB`.
    
    Returns:
        shell_fragment (str): Lines joined by newlines representing shell assignments.
    """
    lines = [
        f"SELECTION_POLICY_IDENTITY={shlex.quote(policy_identity())}",
        _shell_array("SELECTION_POLICY_PROJECTION_MODES", PROJECTION_MODE_CHOICES),
        _shell_array("SELECTION_POLICY_ROOT_SKILL_SETS", ROOT_SKILL_SET_NAMES),
        _shell_array("SELECTION_POLICY_REPO_SCAN_ROOTS", repo_scan_roots_with_prefix()),
        _shell_array("SELECTION_POLICY_EXCLUDED_SEGMENTS", EXCLUDED_SCAN_SEGMENTS),
        _shell_array("SELECTION_POLICY_HIDDEN_FLAT_SKILLS", HIDDEN_FLAT_SKILL_NAMES),
        _shell_array("SELECTION_POLICY_DEFAULT_VISIBLE_FLAT_SKILLS", DEFAULT_VISIBLE_FLAT_SKILL_NAMES),
        _shell_array(
            "SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS",
            PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
        ),
        _shell_array(
            "SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS",
            PLUGIN_HIDDEN_LANE_SKILL_NAMES,
        ),
        _shell_array(
            "SELECTION_POLICY_SYSTEM_BRIDGE_SKILLS",
            SYSTEM_BRIDGE_SKILL_NAMES,
        ),
        _shell_array(
            "SELECTION_POLICY_DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILLS",
            DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILL_NAMES,
        ),
        f"SELECTION_POLICY_PLUGIN_SKILL_ROOT_GLOB={shlex.quote(PLUGIN_SKILL_ROOT_GLOB)}",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit canonical selection policy values.")
    parser.add_argument(
        "--format",
        choices=("json", "shell", "identity"),
        default="json",
        help="Output format.",
    )
    parser.add_argument("--compact", action="store_true", help="Compact JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.format == "identity":
        print(policy_identity())
        return 0
    if args.format == "shell":
        print(render_shell())
        return 0

    if args.compact:
        print(json.dumps({**payload(), "policy_identity": policy_identity()}, separators=(",", ":")))
    else:
        print(json.dumps({**payload(), "policy_identity": policy_identity()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
