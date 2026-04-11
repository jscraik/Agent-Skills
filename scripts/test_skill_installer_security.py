#!/usr/bin/env python3
"""Security-focused regression tests for the skill-installer script."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "plugins"
    / "skill-factory"
    / "skills"
    / "skill-installer"
    / "scripts"
    / "install-skill-from-github.py"
)
SCRIPT_DIR = SCRIPT_PATH.parent


def _load_installer_module():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("skill_installer_github", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


installer = _load_installer_module()


def _write_min_skill(skill_dir: Path) -> None:
    (skill_dir / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: valid sample skill.\n---\n\n# Sample\n",
        encoding="utf-8",
    )


class SkillInstallerSecurityTests(unittest.TestCase):
    def test_canonical_repo_dest_prefers_env_override(self) -> None:
        with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": "/tmp/canonical-skills-dest"}, clear=False):
            self.assertEqual(installer._canonical_repo_dest(), "/tmp/canonical-skills-dest")

    def test_resolve_dest_root_uses_canonical_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            canonical = Path(tmpdir) / "repo" / "github"
            canonical.mkdir(parents=True)
            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                resolved = Path(installer._resolve_dest_root(None)).resolve()
                self.assertEqual(resolved, canonical.resolve())

    def test_resolve_dest_root_rejects_repo_root_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            canonical = repo_root / "github"
            canonical.mkdir(parents=True)
            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                with self.assertRaises(installer.InstallError):
                    installer._resolve_dest_root(".")

    def test_resolve_dest_root_rejects_nested_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            canonical = repo_root / "github"
            canonical.mkdir(parents=True)
            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                with self.assertRaises(installer.InstallError):
                    installer._resolve_dest_root("plugins/coderabbit/skills")

    def test_resolve_dest_root_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            canonical = repo_root / "github"
            canonical.mkdir(parents=True)
            outside = Path(tmpdir) / "outside"
            outside.mkdir(parents=True)
            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                with self.assertRaises(installer.InstallError):
                    installer._resolve_dest_root(str(outside))

    def test_validate_relative_path_rejects_parent_escape(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path("../bad")

    def test_safe_extract_zip_rejects_path_traversal(self) -> None:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("../escape.txt", "bad")

        zip_buffer.seek(0)
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_buffer, "r") as zip_file:
                with self.assertRaises(installer.InstallError):
                    installer._safe_extract_zip(zip_file, tmpdir)

    def test_main_rejects_nested_dest_category(self) -> None:
        pinned_ref = "a" * 40
        args = [
            "--repo",
            "octocat/skills",
            "--path",
            "skills/demo",
            "--ref",
            pinned_ref,
            "--dest",
            "plugins/coderabbit/skills",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            canonical = Path(tmpdir) / "repo" / "github"
            canonical.mkdir(parents=True)
            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                exit_code = installer.main(args)
                self.assertEqual(exit_code, 1)

    def test_main_installs_skill_into_top_level_category(self) -> None:
        pinned_ref = "a" * 40
        source = installer.Source(owner="openai", repo="skills", ref=pinned_ref, paths=["skills/demo"])

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_path = repo_root / "skills" / "demo"
            skill_path.mkdir(parents=True, exist_ok=True)
            _write_min_skill(skill_path)

            canonical = repo_root / "github"
            canonical.mkdir(parents=True, exist_ok=True)

            args = [
                "--repo",
                "openai/skills",
                "--path",
                "skills/demo",
                "--ref",
                pinned_ref,
                "--dest",
                "github",
            ]

            with patch.dict(os.environ, {"ASK_SKILLS_CANONICAL_DEST": str(canonical)}, clear=False):
                with patch.object(installer, "_resolve_source", return_value=source):
                    with patch.object(
                        installer,
                        "_resolve_commit_provenance",
                        return_value=(
                            pinned_ref,
                            {"verified": True, "reason": "valid"},
                            {
                                "emails": [],
                                "logins": [],
                                "attested_emails": [],
                                "attested_logins": [],
                                "metadata_emails": [],
                                "metadata_logins": [],
                            },
                        ),
                    ):
                        with patch.object(installer, "_prepare_repo", return_value=str(repo_root)):
                            stderr_buffer = io.StringIO()
                            with contextlib.redirect_stderr(stderr_buffer):
                                exit_code = installer.main(args)

            self.assertEqual(exit_code, 0)
            self.assertTrue((canonical / "demo" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
