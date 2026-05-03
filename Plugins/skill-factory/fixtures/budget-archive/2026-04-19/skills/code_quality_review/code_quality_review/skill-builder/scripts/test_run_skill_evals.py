#!/usr/bin/env python3
from pathlib import Path
import runpy

wrapper_path = Path(__file__)
namespace = runpy.run_path(str(wrapper_path.with_suffix(".pyw")), run_name=__name__)
namespace["__file__"] = str(wrapper_path)
globals().update(namespace)
