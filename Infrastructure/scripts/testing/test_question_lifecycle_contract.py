#!/usr/bin/env python3
"""Tests for question lifecycle contract validation."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "verify_question_lifecycle_contract.py"
)


def load_validator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "verify_question_lifecycle_contract_test_runtime",
        VALIDATOR,
    )
    if not spec or spec.loader is None:
        raise RuntimeError("Failed to load question lifecycle validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class QuestionLifecycleContractTests(unittest.TestCase):
    def test_stale_reference_scan_ignores_generated_cache_broken_symlinks(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            canonical_doc = repo_root / "Docs" / "example.md"
            canonical_doc.parent.mkdir(parents=True)
            canonical_doc.write_text(
                "See Infrastructure/references/skill-knowledge-graph.md\n",
                encoding="utf-8",
            )

            generated_doc = (
                repo_root
                / ".agents"
                / "plugins-runtime"
                / "cache"
                / "agent-skills-local"
                / "plugin-factory"
                / "README.md"
            )
            generated_doc.parent.mkdir(parents=True)
            generated_doc.symlink_to("missing/README.md")

            module.REPO_ROOT = repo_root
            module.EXCLUDED_SCAN_ROOTS = (
                repo_root / ".agents",
                repo_root / ".skillsets",
                repo_root / "Plugins" / "cache",
                repo_root / "plugins" / "cache",
            )

            findings = module.find_stale_graph_references()

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path.name, "example.md")
        self.assertIn("stale skill knowledge graph reference", findings[0].message)


if __name__ == "__main__":
    unittest.main()
