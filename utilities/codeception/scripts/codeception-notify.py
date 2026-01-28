#!/usr/bin/env python3
"""Codex notify hook for Codeception.

Compatibility wrapper that forwards to the original claudeception notifier.
"""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> None:
    target = Path(__file__).with_name("claudeception-notify.py")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
