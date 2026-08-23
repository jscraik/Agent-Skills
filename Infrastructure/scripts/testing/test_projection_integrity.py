#!/usr/bin/env python3
"""Unit tests for projection integrity helpers and mirror policy."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "lifecycle-and-sync" / "projection_integrity.py"


def _load_module():
    """
    Load and return the projection_integrity module from the SCRIPT path.
    
    Raises a RuntimeError if the module spec or loader cannot be obtained.
    
    Returns:
        module: The imported projection_integrity module object.
    """
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
        """
        Set up a class-level fixture by loading the target projection_integrity module and assigning it to `cls.mod`.
        
        This loads the module once for the test class so individual tests reuse the same module instance.
        """
        cls.mod = _load_module()

    def test_markdown_frontmatter_header_round_trip(self) -> None:
        source = "---\ntitle: demo\n---\n\n# Hello\n"
        stamped = self.mod.apply_projection_header(source, "Plugins/demo/README.md", ".md")
        stripped, had_header = self.mod.strip_projection_header(stamped, ".md")
        self.assertTrue(had_header)
        self.assertEqual(stripped, source)

    def test_shell_shebang_header_round_trip(self) -> None:
        """
        Verify that applying then removing a projection header preserves a shell script starting with a shebang.
        
        This test ensures a shell script with an initial shebang line is stamped with a projection header by apply_projection_header and that strip_projection_header detects and removes that header, returning the original script content and indicating a header was present.
        """
        source = "#!/usr/bin/env bash\necho hi\n"
        stamped = self.mod.apply_projection_header(source, "Plugins/demo/script.sh", ".sh")
        stripped, had_header = self.mod.strip_projection_header(stamped, ".sh")
        self.assertTrue(had_header)
        self.assertEqual(stripped, source)

    def test_verify_mirror_requires_generated_headers(self) -> None:
        """
        Verifies that verify_mirror reports drift when projection files exist but lack projection headers.
        
        Creates a source and a projection README.md with identical content, constructs a MirrorProjection pointing at those paths, and calls verify_mirror. Asserts the result reports status "drift", includes "README.md" in `unstamped_files`, and indicates `manifest_mismatch` is False.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            (projection / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(result["status"], "drift")
            self.assertIn("README.md", result["unstamped_files"])
            self.assertFalse(result["manifest_mismatch"])

    def test_verify_mirror_allows_optional_missing_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            source.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo-optional",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
                optional_when_missing=True,
            )
            result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["reason"], "projection_missing_optional")

            projection_file = repo_root / "Plugins" / "cache" / "demo" / "local"
            projection_file.parent.mkdir(parents=True, exist_ok=True)
            projection_file.write_text("not-a-directory\n", encoding="utf-8")
            result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(result["status"], "drift")
            self.assertEqual(result["reason"], "projection_not_directory")

    def test_sync_mirror_removes_stale_files_and_stamps_headers(self) -> None:
        """
        Verify syncing a mirror removes stale files, stamps projection headers on copied files, preserves executable mode, and yields a passing verification.
        
        Sets up a source tree with README.md and an executable shell script, places a stale file in the projection, runs sync_mirror(...), and asserts that the stale file is deleted, the projected README contains HEADER_TOKEN, the script retains executable bits, and a subsequent verify_mirror(...) returns "pass".
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            source_script = source / "script.sh"
            source_script.write_text("#!/usr/bin/env bash\necho hi\n", encoding="utf-8")
            source_script.chmod(0o755)
            (projection / "stale.txt").write_text("stale\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            sync_result = self.mod.sync_mirror(repo_root, spec)
            self.assertEqual(sync_result["status"], "synced")
            self.assertFalse((projection / "stale.txt").exists())
            readme_text = (projection / "README.md").read_text(encoding="utf-8")
            self.assertIn(self.mod.HEADER_TOKEN, readme_text)
            script_mode = os.stat(projection / "script.sh").st_mode & 0o777
            self.assertEqual(script_mode & 0o111, 0o111)

            verify_result = self.mod.verify_mirror(repo_root, spec)
            self.assertEqual(verify_result["status"], "pass")

    def test_sync_mirror_falls_back_when_rsync_hits_permission_error(self) -> None:
        """
        Ensure sync_mirror falls back to the Python sync engine when rsync fails with a mkstemp permission error.
        
        Simulates rsync being available but raising subprocess.CalledProcessError (return code 23) with stderr containing a mkstemp "Operation not permitted" message, and asserts the function reports a successful sync using the "python" engine and that the projected README.md is created.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            rsync_error = subprocess.CalledProcessError(
                returncode=23,
                cmd=["rsync"],
                stderr="rsync: mkstemp \"/tmp/foo\" failed: Operation not permitted (1)\n",
            )
            with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/rsync"):
                with mock.patch.object(self.mod.subprocess, "run", side_effect=rsync_error):
                    result = self.mod.sync_mirror(repo_root, spec)
            self.assertEqual(result["status"], "synced")
            self.assertEqual(result["sync_engine"], "python")
            self.assertTrue((projection / "README.md").exists())

    def test_sync_mirror_raises_non_permission_rsync_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            rsync_error = subprocess.CalledProcessError(
                returncode=2,
                cmd=["rsync"],
                stderr="rsync error: syntax or usage error\n",
            )
            with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/rsync"):
                with mock.patch.object(self.mod.subprocess, "run", side_effect=rsync_error):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.mod.sync_mirror(repo_root, spec)

    def test_sync_mirror_raises_when_mkstemp_lacks_permission_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)
            (source / "README.md").write_text("# Demo\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            rsync_error = subprocess.CalledProcessError(
                returncode=23,
                cmd=["rsync"],
                stderr="rsync: mkstemp \"/tmp/foo\" failed: Read-only file system (30)\n",
            )
            with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/rsync"):
                with mock.patch.object(self.mod.subprocess, "run", side_effect=rsync_error):
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.mod.sync_mirror(repo_root, spec)

    def test_sync_mirror_replaces_projection_directory_with_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)

            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            stale_dir = projection / "README.md"
            stale_dir.mkdir(parents=True, exist_ok=True)
            (stale_dir / "stale.txt").write_text("stale\n", encoding="utf-8")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            result = self.mod.sync_mirror(repo_root, spec)
            self.assertEqual(result["status"], "synced")
            self.assertTrue((projection / "README.md").is_file())

    def test_sync_mirror_replaces_projection_symlink_with_file(self) -> None:
        """
        Verify sync_mirror replaces a stray symlink projection with a real file.

        This regression test ensures symlinks don't pass the fast-path equality check
        and instead fall through to the Python fallback that clears symlink_kind_mismatch states.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "Plugins" / "demo"
            projection = repo_root / "Plugins" / "cache" / "demo" / "local"
            source.mkdir(parents=True, exist_ok=True)
            projection.mkdir(parents=True, exist_ok=True)

            (source / "README.md").write_text("# Demo\n", encoding="utf-8")
            stale_symlink = projection / "README.md"
            stale_symlink.symlink_to("/dev/null")

            spec = self.mod.MirrorProjection(
                name="demo",
                source_path="Plugins/demo",
                projection_path="Plugins/cache/demo/local",
                tags=("plugin-caches",),
            )
            result = self.mod.sync_mirror(repo_root, spec)
            self.assertEqual(result["status"], "synced")
            self.assertTrue((projection / "README.md").is_file())
            self.assertFalse((projection / "README.md").is_symlink())

    def test_verify_symlink_reports_missing_canonical_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            alias = repo_root / "Skills" / "plugin-builder"
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to("../Plugins/plugin-factory/skills/code_quality_review/plugin-builder", target_is_directory=True)

            spec = self.mod.SymlinkProjection(
                name="plugin-builder",
                alias_path="Skills/plugin-builder",
                canonical_path="Plugins/plugin-factory/skills/code_quality_review/plugin-builder",
                tags=("plugin-factory",),
            )
            result = self.mod.verify_symlink(repo_root, spec)
            self.assertEqual(result["status"], "drift")
            self.assertEqual(result["reason"], "canonical_missing")

    def test_ensure_symlink_refuses_directory_replacement(self) -> None:
        """
        Verifies that ensure_symlink does not replace an existing directory alias and requests manual migration.
        
        Sets up a canonical directory and an alias path that is already a directory containing a file, then calls ensure_symlink and asserts the result has status "error" with reason "alias_requires_manual_migration", and that the alias directory and its contents are unchanged.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            canonical = (
                repo_root
                / "Plugins"
                / "plugin-factory"
                / "skills"
                / "code_quality_review"
                / "plugin-builder"
            )
            canonical.mkdir(parents=True, exist_ok=True)
            alias = repo_root / "Skills" / "plugin-builder"
            alias.mkdir(parents=True, exist_ok=True)
            (alias / "local-note.txt").write_text("keep me\n", encoding="utf-8")

            spec = self.mod.SymlinkProjection(
                name="plugin-builder",
                alias_path="Skills/plugin-builder",
                canonical_path="Plugins/plugin-factory/skills/code_quality_review/plugin-builder",
                tags=("plugin-factory",),
            )
            result = self.mod.ensure_symlink(repo_root, spec)
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["reason"], "alias_requires_manual_migration")
            self.assertTrue(alias.is_dir())
            self.assertTrue((alias / "local-note.txt").exists())

    def test_ensure_symlink_replaces_managed_skills_system_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            canonical = (
                repo_root
                / "Plugins"
                / "skill-factory"
                / "skills"
                / "scaffolding_templates"
                / "skill-creator"
            )
            canonical.mkdir(parents=True, exist_ok=True)
            (canonical / "SKILL.md").write_text("# Skill Creator\n", encoding="utf-8")

            alias = repo_root / "skills-system" / "skill-creator"
            alias.mkdir(parents=True, exist_ok=True)
            (alias / "stale.txt").write_text("stale\n", encoding="utf-8")

            spec = self.mod.SymlinkProjection(
                name="skill-factory-skill-creator-alias",
                alias_path="skills-system/skill-creator",
                canonical_path="Plugins/skill-factory/skills/scaffolding_templates/skill-creator",
                tags=("skill-factory",),
            )
            result = self.mod.ensure_symlink(repo_root, spec)
            self.assertIn(result["status"], {"replaced", "synced"})
            self.assertTrue(alias.is_symlink())
            self.assertEqual((alias.parent / os.readlink(alias)).resolve(), canonical.resolve())

    def test_validation_wrapper_defaults_to_ignored_artifact_root(self) -> None:
        wrapper = SCRIPT.parent / "validate_projection_integrity.sh"
        content = wrapper.read_text(encoding="utf-8")

        self.assertIn(
            'manifest_out="${PROJECTION_INTEGRITY_MANIFEST:-'
            '.tmp/agent-skills-artifacts/validation/projection-integrity/latest.json}"',
            content,
        )

if __name__ == "__main__":
    unittest.main()
