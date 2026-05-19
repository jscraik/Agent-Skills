from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "check_skill_factory_system_overlays.py"
)
SPEC = importlib.util.spec_from_file_location("check_skill_factory_system_overlays", SCRIPT_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["check_skill_factory_system_overlays"] = MODULE
SPEC.loader.exec_module(MODULE)


def test_current_skill_factory_system_overlay_contract_passes() -> None:
    assert MODULE.main() == 0
