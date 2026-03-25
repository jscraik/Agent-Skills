#!/usr/bin/env python3
"""Compatibility wrapper for the canonical skill-builder initializer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


CANONICAL_INIT = (
    Path(__file__).resolve().parents[3]
    / "utilities"
    / "skill-builder"
    / "scripts"
    / "init_skill.py"
)


def _load_canonical_main():
    spec = importlib.util.spec_from_file_location("canonical_skill_builder_init", CANONICAL_INIT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load canonical init script: {CANONICAL_INIT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


def main() -> int:
    canonical_main = _load_canonical_main()
    return canonical_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
