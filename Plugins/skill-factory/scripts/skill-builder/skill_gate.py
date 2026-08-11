#!/usr/bin/env python3
"""Compatibility facade for the modular skill gate implementation."""

import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from skill_gate_core import *  # noqa: E402,F403
from skill_gate_output import *  # noqa: E402,F403
from skill_gate_research_checks import *  # noqa: E402,F403
from skill_gate_security_checks import *  # noqa: E402,F403


if __name__ == "__main__" and os.environ.get("SKILL_GATE_DISABLE_CLI") != "1":
    raise SystemExit(globals()["main"]())
