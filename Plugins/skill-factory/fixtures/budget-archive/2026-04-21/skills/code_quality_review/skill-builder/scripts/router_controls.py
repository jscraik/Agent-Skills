#!/usr/bin/env python3
from pathlib import Path
import runpy

_here = Path(__file__).resolve()
_root = next(parent for parent in [_here, *_here.parents] if parent.name == "skill-factory")
_archive = (
    _root
    / "fixtures/budget-archive/2026-04-19/skills/code_quality_review/skill-builder/scripts/"
    "router_controls.py"
)

_loaded_namespace = runpy.run_path(str(_archive), run_name="__archived_router_controls__")
_reserved_names = {
    "__name__",
    "__file__",
    "__package__",
    "__spec__",
    "__loader__",
    "__cached__",
    "__builtins__",
    "_here",
    "_root",
    "_archive",
}
for _name, _value in _loaded_namespace.items():
    if _name in _reserved_names or (_name.startswith("__") and _name.endswith("__")):
        continue
    globals()[_name] = _value
