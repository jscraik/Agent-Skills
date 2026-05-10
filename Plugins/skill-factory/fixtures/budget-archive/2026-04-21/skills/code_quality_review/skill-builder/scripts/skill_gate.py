#!/usr/bin/env python3
from pathlib import Path
import runpy

_run_name = "__main__" if __name__ == "__main__" else "skill_gate"
globals().update(runpy.run_path(str(Path(__file__).with_suffix(".pyw")), run_name=_run_name))
