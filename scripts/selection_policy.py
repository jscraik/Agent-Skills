#!/usr/bin/env python3
"""Canonical selection/discovery policy shared by route, discovery, and sync."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from typing import Any, Iterable

POLICY_VERSION = "2026-04-10.v2"

# Canonical roots for repo-owned skills.
REPO_SCAN_ROOTS: tuple[str, ...] = (
    "auth",
    "backend",
    "design",
    "frontend",
    "github",
    "interview",
    "ops",
    "personas",
    "product",
    "skills-system",
    "utilities",
)

# Plugin-bundled skill roots scanned by sync scripts.
PLUGIN_SKILL_ROOT_GLOB = "./plugins/*/skills"

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
    "linear",
    "plugin-builder",
    "plugin-creator",
    "plugin-installer",
    "skillgrade-graders",
    "skillgrade-setup",
)

# Plugin router skills that should be visible in default flat discovery.
PLUGIN_VISIBLE_ROUTER_SKILL_NAMES: tuple[str, ...] = (
    "coderabbit",
)

# Plugin lane skills that stay hidden by default unless advanced mode is used.
PLUGIN_HIDDEN_LANE_SKILL_NAMES: tuple[str, ...] = (
    "autofix",
    "code-review",
    "simplify",
)


def repo_scan_roots_with_prefix() -> tuple[str, ...]:
    return tuple(f"./{root}" for root in REPO_SCAN_ROOTS)


def payload() -> dict[str, Any]:
    """Stable serialization input used to compute policy identity."""
    return {
        "policy_version": POLICY_VERSION,
        "repo_scan_roots": list(REPO_SCAN_ROOTS),
        "plugin_skill_root_glob": PLUGIN_SKILL_ROOT_GLOB,
        "excluded_scan_segments": list(EXCLUDED_SCAN_SEGMENTS),
        "hidden_flat_skill_names": list(HIDDEN_FLAT_SKILL_NAMES),
        "plugin_visible_router_skill_names": list(PLUGIN_VISIBLE_ROUTER_SKILL_NAMES),
        "plugin_hidden_lane_skill_names": list(PLUGIN_HIDDEN_LANE_SKILL_NAMES),
    }


def policy_identity() -> str:
    canonical = json.dumps(payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _shell_array(name: str, values: Iterable[str]) -> str:
    encoded = " ".join(shlex.quote(value) for value in values)
    return f"{name}=({encoded})"


def render_shell() -> str:
    lines = [
        f"SELECTION_POLICY_IDENTITY={shlex.quote(policy_identity())}",
        _shell_array("SELECTION_POLICY_REPO_SCAN_ROOTS", repo_scan_roots_with_prefix()),
        _shell_array("SELECTION_POLICY_EXCLUDED_SEGMENTS", EXCLUDED_SCAN_SEGMENTS),
        _shell_array("SELECTION_POLICY_HIDDEN_FLAT_SKILLS", HIDDEN_FLAT_SKILL_NAMES),
        _shell_array(
            "SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS",
            PLUGIN_VISIBLE_ROUTER_SKILL_NAMES,
        ),
        _shell_array(
            "SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS",
            PLUGIN_HIDDEN_LANE_SKILL_NAMES,
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
