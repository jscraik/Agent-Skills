#!/usr/bin/env python3
"""Unit tests for projection integrity helpers and mirror policy."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "projection_integrity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("projection_integrity", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load projection_integrity module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[misc]
    return module


class ProjectionIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_markdown_frontmatter_header_round_trip(self) -> None:
        source = "---\ntitle: demo\n---\n\n# Hello\n"
        stamped = self.mod.apply_projection_header(source, "plugins/demo/README.md", ".md")
        stripped, had_header = self.mod.strip_projection_header(stamped, ".md")
        self.assertTrue(had_header)
        self.assertEqual(stripped, source)

    def test_shell_shebang_header_round_trip(self) -> None:
        source = "#!/usr/bin/env bash\necho hi\n"
        stamped = self.mod.apply_projection_header(source, "plugins/demo/script.sh", ".sh")
        stripped, had_header = self.mod.strip_projection_header(stamped, ".sh")
        self.assertTrue(had_header)
        self.assertEqual(stripped, source)

    def test_verify_mirror_requires_generated_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "plugins" / "demo"
            projection = repo_root / "plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            (projection / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="plugins/demo",
                projection_path="plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(result["status"], "drift")
            self.assertIn("README.md", result["unstamped_files"])
            self.assertFalse(result["manifest_mismatch"])

    def test_sync_mirror_removes_stale_files_and_stamps_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "plugins" / "demo"
            projection = repo_root / "plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            (source / "script.sh").write_text("#!/usr/bin/env bash\necho hi\n", encoding="utf-8")
            (projection / "stale.txt").write_text("stale\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="plugins/demo",
                projection_path="plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            sync_result = self.mod.sync_mirror(repo_root, spec)
            self.assertEqual(sync_result["status"], "synced")
            self.assertFalse((projection / "stale.txt").exists())
            readme_text = (projection / "README.md").read_text(encoding="utf-8")
            self.assertIn(self.mod.HEADER_TOKEN, readme_text)

            verify_result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(verify_result["status"], "pass")

    def test_verify_symlink_reports_missing_canonical_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            alias = repo_root / "utilities" / "plugin-builder"
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to("../plugins/plugin-factory/skills/plugin-builder", target_is_directory=True)

            spec = self.mod.SymlinkProjection(
                name="plugin-builder",
                alias_path="utilities/plugin-builder",
                canonical_path="plugins/plugin-factory/skills/plugin-builder",
                tags=("plugin-factory",),
            )
            result = self.mod.verify_symlink(repo_root, spec)
            self.assertEqual(result["status"], "drift")
            self.assertEqual(result["reason"], "canonical_missing")

    def test_ensure_symlink_refuses_directory_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            canonical = repo_root / "plugins" / "plugin-factory" / "skills" / "plugin-builder"
            canonical.mkdir(parents=True, exist_ok=True)
            alias = repo_root / "utilities" / "plugin-builder"
            alias.mkdir(parents=True, exist_ok=True)
            (alias / "local-note.txt").write_text("keep me\n", encoding="utf-8")

            spec = self.mod.SymlinkProjection(
                name="plugin-builder",
                alias_path="utilities/plugin-builder",
                canonical_path="plugins/plugin-factory/skills/plugin-builder",
                tags=("plugin-factory",),
            )
            result = self.mod.ensure_symlink(repo_root, spec)
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["reason"], "alias_requires_manual_migration")
            self.assertTrue(alias.is_dir())
            self.assertTrue((alias / "local-note.txt").exists())


if __name__ == "__main__":
    unittest.main()
