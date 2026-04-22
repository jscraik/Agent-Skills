#!/usr/bin/env python3
"""Shared wrapper test helpers for deferred-store plugin fixtures."""

from pathlib import Path


def find_repo_root(current: Path) -> Path:
    for parent in current.parents:
        if (parent / "AGENTS.md").exists() and (parent / "Plugins").exists():
            return parent
    raise AssertionError("could not locate repo root")
