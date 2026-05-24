#!/usr/bin/env python3
"""Skill-local wrapper for the Goal Governor board validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def _impl_paths():
    yield SCRIPT_DIR / "check_goal_board_impl.py"
    for parent in SCRIPT_DIR.parents:
        yield parent / "Infrastructure" / "scripts" / "goal-governor" / "check_goal_board_impl.py"


def _load_impl():
    searched = []
    for impl_path in _impl_paths():
        searched.append(str(impl_path))
        if not impl_path.is_file():
            continue

        spec = importlib.util.spec_from_file_location(
            "goal_governor_check_goal_board_impl",
            impl_path,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load Goal Governor board validator: {impl_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    searched_text = "\n- ".join(searched)
    raise ImportError(
        "cannot find Goal Governor board validator implementation. Searched:\n"
        f"- {searched_text}"
    )


_impl = _load_impl()

for _name in dir(_impl):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_impl, _name)


if __name__ == "__main__":
    raise SystemExit(_impl.main(sys.argv))
