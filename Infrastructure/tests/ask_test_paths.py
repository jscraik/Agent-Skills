"""Shared import-path setup for ask helper tests."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"
SCRIPTS_DIR = REPO_ROOT / "Infrastructure" / "scripts"
LIFECYCLE_DIR = SCRIPTS_DIR / "lifecycle-and-sync"
UTILITIES_DIR = REPO_ROOT / "Infrastructure" / "utilities" / "skill-builder" / "scripts"


def ensure_ask_lib_path() -> None:
    ask_lib_path = str(ASK_LIB_DIR)
    if ask_lib_path not in sys.path:
        sys.path.insert(0, ask_lib_path)


def ensure_ask_support_paths() -> None:
    for path in (ASK_LIB_DIR, SCRIPTS_DIR, LIFECYCLE_DIR, UTILITIES_DIR):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
