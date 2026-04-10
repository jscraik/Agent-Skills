#!/usr/bin/env python3
"""Regression test: plugin-factory packaged skills must match canonical sources."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAIRINGS: tuple[tuple[str, str], ...] = (
    ("utilities/plugin-builder", "plugins/plugin-factory/skills/plugin-builder"),
    ("skills-system/plugin-creator", "plugins/plugin-factory/skills/plugin-creator"),
    ("skills-system/plugin-installer", "plugins/plugin-factory/skills/plugin-installer"),
)
IGNORED_FILE_NAMES = {".DS_Store"}
IGNORED_DIR_NAMES = {"__pycache__"}


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _collect_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if path.name in IGNORED_FILE_NAMES:
            continue
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        files[rel] = _file_digest(path)
    return files


class PluginFactoryFamilyParityTests(unittest.TestCase):
    def test_packaged_skill_families_match_source_of_truth(self) -> None:
        for source_rel, packaged_rel in PAIRINGS:
            with self.subTest(source=source_rel, packaged=packaged_rel):
                source_root = REPO_ROOT / source_rel
                packaged_root = REPO_ROOT / packaged_rel
                self.assertTrue(source_root.is_dir(), f"missing source directory: {source_root}")
                self.assertTrue(packaged_root.is_dir(), f"missing packaged directory: {packaged_root}")

                source_files = _collect_files(source_root)
                packaged_files = _collect_files(packaged_root)
                self.assertEqual(
                    source_files,
                    packaged_files,
                    (
                        f"source and packaged trees differ for {source_rel} -> {packaged_rel}. "
                        "Run `bash scripts/sync_plugin_factory_family.sh`."
                    ),
                )


if __name__ == "__main__":
    unittest.main()
