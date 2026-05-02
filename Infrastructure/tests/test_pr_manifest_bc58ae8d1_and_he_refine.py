"""Regression checks for rooted manifests and command-surface projection."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLSET_DIR = REPO_ROOT / ".skillsets"
COMMAND_SURFACE_PATH = SKILLSET_DIR / "command-surface.json"

_REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,}", re.IGNORECASE)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise AssertionError(
                    f"Invalid JSON on line {lineno} of {path}: {exc}"
                ) from exc
    return records


def _load_command_surface() -> dict[str, Any]:
    return json.loads(COMMAND_SURFACE_PATH.read_text(encoding="utf-8"))


class TestManifestSourceRevisions(unittest.TestCase):
    """Generated manifests should carry valid rooted source revisions."""

    def test_all_revisions_are_valid_git_hash_format(self) -> None:
        for path in sorted(SKILLSET_DIR.glob("*/manifest.jsonl")):
            for rec in _load_jsonl(path):
                rev = rec.get("provenance", {}).get("source_revision", "")
                with self.subTest(path=path.relative_to(REPO_ROOT), skill_id=rec.get("id", "?")):
                    self.assertRegex(rev, _REVISION_PATTERN)


class TestManifestRequiredFields(unittest.TestCase):
    """Each manifest.jsonl entry must carry all required fields."""

    REQUIRED_FIELDS = (
        "description",
        "id",
        "level",
        "provenance",
        "risk",
        "runtime_visibility",
        "scope",
        "skill_set",
        "source_path",
        "triggers",
    )
    PROVENANCE_FIELDS = ("source_revision", "source_sha256", "generator")

    def test_all_manifests_have_required_fields(self) -> None:
        for path in sorted(SKILLSET_DIR.glob("*/manifest.jsonl")):
            records = _load_jsonl(path)
            self.assertGreater(len(records), 0, f"{path.name} must be non-empty")
            for rec in records:
                with self.subTest(path=path.relative_to(REPO_ROOT), skill_id=rec.get("id", "?")):
                    for field in self.REQUIRED_FIELDS:
                        self.assertIn(field, rec, f"Missing required field '{field}'")
                    for field in self.PROVENANCE_FIELDS:
                        self.assertIn(field, rec["provenance"], f"Missing provenance field '{field}'")
                    self.assertIsInstance(rec["triggers"], list)
                    self.assertGreater(len(rec["triggers"]), 0, "triggers list must be non-empty")


class TestCommandSurfaceProjection(unittest.TestCase):
    def setUp(self) -> None:
        self._data = _load_command_surface()

    def test_file_is_valid_json_with_handles_list(self) -> None:
        self.assertIsInstance(self._data, dict)
        self.assertIn("handles", self._data)
        self.assertIsInstance(self._data["handles"], list)

    def test_all_handle_revisions_are_valid_git_hashes(self) -> None:
        for entry in self._data.get("handles", []):
            rev = entry.get("provenance", {}).get("source_revision", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertRegex(rev, _REVISION_PATTERN)

    def test_all_handles_have_required_fields(self) -> None:
        required = ("handle", "description", "kind", "provenance", "source_path")
        for entry in self._data.get("handles", []):
            for field in required:
                with self.subTest(handle=entry.get("handle", "?"), field=field):
                    self.assertIn(field, entry)

    def test_harness_engineering_handles_use_active_plugin_paths(self) -> None:
        he_handles = [
            entry
            for entry in self._data.get("handles", [])
            if entry.get("owner") == "harness-engineering"
        ]
        self.assertGreater(len(he_handles), 0, "No Harness Engineering handles found")
        for entry in he_handles:
            source_path = entry.get("source_path", "")
            with self.subTest(handle=entry.get("handle", "?")):
                self.assertTrue(source_path.startswith("Plugins/harness-engineering/skills/"))
                self.assertNotIn("team_automation/", source_path)

    def test_he_refine_handle_is_not_exposed(self) -> None:
        handles = {entry.get("handle") for entry in self._data.get("handles", [])}
        self.assertNotIn("he-refine", handles)


class TestAllManifestsParseable(unittest.TestCase):
    """Regression: every manifest.jsonl in the repo must be valid JSONL."""

    def test_all_manifest_jsonl_files_parse_without_error(self) -> None:
        manifest_paths = sorted(SKILLSET_DIR.glob("*/manifest.jsonl"))
        self.assertGreater(len(manifest_paths), 0, "No manifest.jsonl files found")
        for path in manifest_paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                records = _load_jsonl(path)
                self.assertGreater(len(records), 0, f"{path.name} must be non-empty")


if __name__ == "__main__":
    unittest.main()
