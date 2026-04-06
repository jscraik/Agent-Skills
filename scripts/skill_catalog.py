#!/usr/bin/env python3
"""Compatibility shim for skill_catalog.py → skill_discovery.py

Deprecated: Use scripts/skill_discovery.py directly.
This shim preserves backward compatibility for existing callers.
"""
import sys
from pathlib import Path

# Delegate to skill_discovery
skill_discovery_path = Path(__file__).resolve().parent / "skill_discovery.py"
sys.path.insert(0, str(skill_discovery_path.parent))

from skill_discovery import main, parse_args

if __name__ == "__main__":
    raise SystemExit(main())
