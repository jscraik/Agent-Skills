#!/usr/bin/env python3
from pathlib import Path
import runpy

_here = Path(__file__).resolve()
_root = next(parent for parent in [_here, *_here.parents] if parent.name == "skill-factory")
_archive = (
    _root
    / "fixtures/budget-archive/2026-04-19/skills/scaffolding_templates/skill-creator/scripts/"
    "check_handoff_package_template_drift.py"
)

runpy.run_path(str(_archive), run_name=__name__)
