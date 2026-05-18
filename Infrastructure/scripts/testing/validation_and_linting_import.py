from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_docs_validator() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_ask_bootstrap_docs.py"
    spec = importlib.util.spec_from_file_location("verify_ask_bootstrap_docs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
