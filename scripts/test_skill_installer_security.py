#!/usr/bin/env python3
"""Security-focused regression tests for skill-installer GitHub import script."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills-system" / "skill-installer" / "scripts" / "install-skill-from-github.py"
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
    references = skill_dir / "references"
    references.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: sample-skill\ndescription: valid sample skill.\n---\n\n# Sample\n",
        encoding="utf-8",
    )
    (references / "contract.yaml").write_text("purpose: test\n", encoding="utf-8")
    (references / "evals.yaml").write_text("cases: []\n", encoding="utf-8")


class SkillInstallerSecurityTests(unittest.TestCase):
    def test_validate_relative_path_rejects_option_like_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path("--dangerous")

    def test_validate_ref_token_rejects_option_like_ref(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("--orphan")

    def test_validate_relative_path_rejects_dot_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path(".")

    def test_validate_ref_token_rejects_empty(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("   ")

    def test_validate_skill_rejects_symlink_payloads(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not supported on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "sample-skill"
            _write_min_skill(skill_dir)
            os.symlink("/etc/hosts", skill_dir / "leak.txt")

            with self.assertRaises(installer.InstallError):
                installer._validate_skill(str(skill_dir))

    def test_validate_skill_rejects_symlink_root(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not supported on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            real_skill_dir = Path(tmpdir) / "real-skill"
            _write_min_skill(real_skill_dir)
            linked_path = Path(tmpdir) / "linked-skill"
            os.symlink(real_skill_dir, linked_path)

            with self.assertRaises(installer.InstallError):
                installer._validate_skill(str(linked_path))

    def test_validate_skill_rejects_nested_symlink_directory(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not supported on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "sample-skill"
            _write_min_skill(skill_dir)
            linked_dir = skill_dir / "references" / "linked-dir"
            os.symlink("/tmp", linked_dir)

            with self.assertRaises(installer.InstallError):
                installer._validate_skill(str(skill_dir))

    def test_assert_path_within_repo_rejects_escape(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._assert_path_within_repo("/tmp/repo", "/tmp/other/skill")

    def test_sparse_checkout_uses_option_separator(self) -> None:
        commands: list[list[str]] = []

        def fake_run_git(args: list[str]) -> str:
            commands.append(args)
            if args[-2:] == ["rev-parse", "HEAD"]:
                return "a" * 40
            return ""

        with patch.object(installer, "_run_git", side_effect=fake_run_git):
            repo_dir, resolved = installer._git_sparse_checkout(
                "https://github.com/example/repo.git",
                "main",
                ["skills/my-skill"],
                "/tmp/codex-test",
            )

        self.assertTrue(repo_dir.endswith("/repo"))
        self.assertEqual(resolved, "a" * 40)
        sparse_set = [cmd for cmd in commands if "sparse-checkout" in cmd]
        self.assertTrue(sparse_set, "expected sparse-checkout command")
        self.assertIn("--", sparse_set[0], "expected sparse-checkout option separator")

    def test_prepare_repo_requires_explicit_ssh_fallback(self) -> None:
        source = installer.Source(owner="octocat", repo="skills", ref="main", paths=["skills/demo"])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(installer, "_git_sparse_checkout", side_effect=installer.InstallError("https failed")) as mock_sparse:
                with self.assertRaises(installer.InstallError) as ctx:
                    installer._prepare_repo(source, "git", tmpdir, allow_ssh_fallback=False)
                self.assertIn("SSH fallback is disabled", str(ctx.exception))
                self.assertIn("HTTPS error: https failed", str(ctx.exception))
                self.assertEqual(mock_sparse.call_count, 1)

    def test_prepare_repo_uses_ssh_when_override_enabled(self) -> None:
        source = installer.Source(owner="octocat", repo="skills", ref="main", paths=["skills/demo"])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(
                installer,
                "_git_sparse_checkout",
                side_effect=[installer.InstallError("HTTP 403"), ("/tmp/repo", "b" * 40)],
            ) as mock_sparse:
                prepared = installer._prepare_repo(source, "git", tmpdir, allow_ssh_fallback=True)

        self.assertEqual(prepared.source_method, "git+ssh")
        self.assertEqual(prepared.resolved_commit, "b" * 40)
        self.assertEqual(mock_sparse.call_count, 2)

    def test_prepare_repo_refuses_ssh_fallback_for_non_transport_error(self) -> None:
        source = installer.Source(owner="octocat", repo="skills", ref="main", paths=["skills/demo"])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(installer, "_git_sparse_checkout", side_effect=installer.InstallError("pathspec not found")):
                with self.assertRaises(installer.InstallError) as ctx:
                    installer._prepare_repo(source, "git", tmpdir, allow_ssh_fallback=True)
                self.assertIn("Refusing SSH fallback", str(ctx.exception))

    def test_main_rolls_back_if_manifest_write_fails(self) -> None:
        pinned_ref = "a" * 40
        source = installer.Source(owner="octocat", repo="skills", ref=pinned_ref, paths=["skills/demo"])

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_path = repo_root / "skills" / "demo"
            _write_min_skill(skill_path)
            dest = Path(tmpdir) / "dest"

            args = [
                "--repo",
                "octocat/skills",
                "--path",
                "skills/demo",
                "--ref",
                pinned_ref,
                "--dest",
                str(dest),
                "--validation-level",
                "compat",
                "--allow-untrusted-source",
            ]

            with patch.object(installer, "_resolve_source", return_value=source):
                with patch.object(
                    installer,
                    "_prepare_repo",
                    return_value=installer.PreparedRepo(
                        repo_root=str(repo_root),
                        resolved_commit=pinned_ref,
                        source_method="download",
                    ),
                ):
                    with patch.object(installer, "_write_json_atomic", side_effect=OSError("disk full")):
                        exit_code = installer.main(args)

            self.assertEqual(exit_code, 1)
            self.assertFalse((dest / "demo").exists(), "promotion should roll back when manifest write fails")

    def test_main_rejects_ssh_fallback_without_git_method(self) -> None:
        pinned_ref = "a" * 40
        args = [
            "--repo",
            "octocat/skills",
            "--path",
            "skills/demo",
            "--ref",
            pinned_ref,
            "--allow-ssh-fallback",
        ]
        exit_code = installer.main(args)
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
