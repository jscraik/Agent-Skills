"""Facade module for ask CLI tests."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def _load_impl() -> ModuleType:
    module_name = "test_ask_cli_impl_runtime"
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).with_name("test_ask_cli_impl.py"),
    )
    if not spec or spec.loader is None:
        raise RuntimeError("Failed to locate test_ask_cli implementation")
    impl = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = impl
    spec.loader.exec_module(impl)
    return impl


_impl = _load_impl()
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("_")})


if __name__ == "__main__":
    raise SystemExit(0)
