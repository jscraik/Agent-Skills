#!/usr/bin/env python3
"""Entry-point stub that loads the implementation from the sibling .pyw file."""
from pathlib import Path
import runpy

globals().update(runpy.run_path(str(Path(__file__).with_suffix(".pyw")), run_name=__name__))
