"""Compatibility test facade for modularized test cases."""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_all_runtime_separation_tests_core import *  # noqa: F403
from validate_all_runtime_separation_tests_01 import *  # noqa: F403
