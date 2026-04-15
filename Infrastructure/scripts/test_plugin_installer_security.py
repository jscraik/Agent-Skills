#!/usr/bin/env python3
"""Security-focused regression tests for plugin-installer GitHub import script."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from unittest import mock
from unittest import TestCase, main
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "skills-system" / "plugin-installer" / "scripts" / "install-plugin-from-github.py"
SCRIPT_DIR = SCRIPT_PATH.parent


def _load_installer_module():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("plugin_installer_github", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


installer = _load_installer_module()


def _write_min_plugin(plugin_dir: Path) -> None:
    manifest_dir = plugin_dir / ".codex-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "plugin.json").write_text(
        '{"name":"sample-plugin","version":"0.1.0","description":"sample"}\n',
        encoding="utf-8",
    )


class PluginInstallerSecurityTests(TestCase):
    def test_uv_python_command_requires_uv_binary(self) -> None:
        with mock.patch.object(installer.shutil, "which", return_value=None):
            with self.assertRaises(installer.InstallError) as context:
                installer._uv_python_command()

        self.assertIn("uv is required", str(context.exception))

    def test_validate_relative_path_rejects_option_like_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path("--dangerous")

    def test_validate_ref_token_rejects_option_like_ref(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("--orphan")

    def test_validate_relative_path_rejects_dot_path(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path(".")

    def test_validate_relative_path_rejects_parent_component(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_relative_path("Plugins/example/../escape")

    def test_validate_ref_token_rejects_empty(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_ref_token("   ")

    def test_dependency_identifier_rejects_invalid_plugin_name(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_dependency_identifier(
                "Bad Name",
                allow_cross_marketplace_dependencies=False,
            )

    def test_dependency_identifier_rejects_cross_marketplace_without_flag(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._validate_dependency_identifier(
                "alpha-plugin@codex",
                allow_cross_marketplace_dependencies=False,
            )

    def test_dependency_identifier_accepts_cross_marketplace_with_flag(self) -> None:
        installer._validate_dependency_identifier(
            "alpha-plugin@codex",
            allow_cross_marketplace_dependencies=True,
        )

    def test_enforce_signed_commit_provenance_accepts_verified_commit(self) -> None:
        installer._enforce_signed_commit_provenance(
            owner="openai",
            repo="plugins",
            resolved_commit="a" * 40,
            commit_verification={
                "verified": True,
                "reason": "valid",
            },
            signer_identity={"emails": ["trusted@example.com"], "logins": ["trusted-bot"]},
            allow_unsigned_provenance=False,
            allowed_signer_emails=set(),
            allowed_signer_domains=set(),
            allowed_signer_logins=set(),
        )

    def test_enforce_signed_commit_provenance_rejects_unverified_commit(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._enforce_signed_commit_provenance(
                owner="openai",
                repo="plugins",
                resolved_commit="b" * 40,
                commit_verification={
                    "verified": False,
                    "reason": "unsigned",
                },
                signer_identity={"emails": ["trusted@example.com"], "logins": ["trusted-bot"]},
                allow_unsigned_provenance=False,
                allowed_signer_emails=set(),
                allowed_signer_domains=set(),
                allowed_signer_logins=set(),
            )

    def test_enforce_signed_commit_provenance_allows_override_for_unverified_commit(self) -> None:
        installer._enforce_signed_commit_provenance(
            owner="openai",
            repo="plugins",
            resolved_commit="c" * 40,
            commit_verification={
                "verified": False,
                "reason": "unsigned",
            },
            signer_identity={"emails": ["trusted@example.com"], "logins": ["trusted-bot"]},
            allow_unsigned_provenance=True,
            allowed_signer_emails=set(),
            allowed_signer_domains=set(),
            allowed_signer_logins=set(),
        )

    def test_enforce_signed_commit_provenance_enforces_signer_allowlist(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._enforce_signed_commit_provenance(
                owner="openai",
                repo="plugins",
                resolved_commit="d" * 40,
                commit_verification={
                    "verified": True,
                    "reason": "valid",
                },
                signer_identity={"emails": ["unknown@example.org"], "logins": ["unknown"]},
                allow_unsigned_provenance=False,
                allowed_signer_emails={"trusted@example.com"},
                allowed_signer_domains={"openai.com"},
                allowed_signer_logins={"trusted-bot"},
            )

    def test_enforce_signed_commit_provenance_accepts_matching_signer_domain(self) -> None:
        installer._enforce_signed_commit_provenance(
            owner="openai",
            repo="plugins",
            resolved_commit="e" * 40,
            commit_verification={
                "verified": True,
                "reason": "valid",
            },
            signer_identity={"emails": ["release@openai.com"], "logins": ["release-bot"]},
            allow_unsigned_provenance=False,
            allowed_signer_emails=set(),
            allowed_signer_domains={"openai.com"},
            allowed_signer_logins=set(),
        )

    def test_enforce_signed_commit_provenance_accepts_metadata_login_fallback(self) -> None:
        installer._enforce_signed_commit_provenance(
            owner="openai",
            repo="plugins",
            resolved_commit="f" * 40,
            commit_verification={
                "verified": True,
                "reason": "valid",
            },
            signer_identity={
                "attested_emails": ["release@openai.com"],
                "attested_logins": [],
                "metadata_emails": ["release@openai.com"],
                "metadata_logins": ["release-bot"],
            },
            allow_unsigned_provenance=False,
            allowed_signer_emails=set(),
            allowed_signer_domains={"openai.com"},
            allowed_signer_logins={"release-bot"},
        )

    def test_enforce_signed_commit_provenance_rejects_login_allowlist_when_no_logins_present(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._enforce_signed_commit_provenance(
                owner="openai",
                repo="plugins",
                resolved_commit="1" * 40,
                commit_verification={
                    "verified": True,
                    "reason": "valid",
                },
                signer_identity={
                    "attested_emails": ["release@openai.com"],
                    "attested_logins": [],
                    "metadata_emails": ["release@openai.com"],
                    "metadata_logins": [],
                },
                allow_unsigned_provenance=False,
                allowed_signer_emails=set(),
                allowed_signer_domains={"openai.com"},
                allowed_signer_logins={"release-bot"},
            )

    def test_enforce_signed_commit_provenance_requires_valid_reason_for_allowlist(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._enforce_signed_commit_provenance(
                owner="openai",
                repo="plugins",
                resolved_commit="2" * 40,
                commit_verification={
                    "verified": True,
                    "reason": "unknown_signature_type",
                },
                signer_identity={"emails": ["release@openai.com"], "logins": []},
                allow_unsigned_provenance=True,
                allowed_signer_emails=set(),
                allowed_signer_domains={"openai.com"},
                allowed_signer_logins=set(),
            )

    def test_enforce_signed_commit_provenance_requires_all_configured_allowlist_dimensions(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._enforce_signed_commit_provenance(
                owner="openai",
                repo="plugins",
                resolved_commit="0" * 40,
                commit_verification={
                    "verified": True,
                    "reason": "valid",
                },
                signer_identity={"emails": ["trusted@example.com"], "logins": []},
                allow_unsigned_provenance=False,
                allowed_signer_emails={"trusted@example.com"},
                allowed_signer_domains={"openai.com"},
                allowed_signer_logins=set(),
            )

    def test_validate_plugin_root_rejects_symlink_payloads(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not supported on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "sample-plugin"
            _write_min_plugin(plugin_dir)
            leak_target = Path(tmpdir) / "leak.txt"
            leak_target.write_text("secret\n", encoding="utf-8")
            try:
                os.symlink(leak_target, plugin_dir / "leak.txt")
            except OSError as exc:
                self.skipTest(f"symlink creation not permitted on this platform: {exc}")

            with self.assertRaises(installer.InstallError):
                installer._validate_plugin_root(str(plugin_dir))

    def test_validate_plugin_root_rejects_missing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir) / "sample-plugin"
            plugin_dir.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(installer.InstallError):
                installer._validate_plugin_root(str(plugin_dir))

    def test_resolve_install_plugin_name_requires_manifest_match_by_default(self) -> None:
        with self.assertRaises(installer.InstallError):
            installer._resolve_install_plugin_name(
                detected_name="manifest-plugin",
                override_name="custom-name",
                allow_manifest_name_mismatch=False,
            )

    def test_fetch_repo_with_fallback_uses_git_on_zip_failure(self) -> None:
        with mock.patch.object(
            installer,
            "_download_repo_zip",
            side_effect=installer.InstallError("zip failed"),
        ) as zip_mock, mock.patch.object(
            installer,
            "_download_repo_git_sparse",
            return_value="/tmp/repo-git",
        ) as git_mock:
            repo_root, transport = installer._fetch_repo_with_fallback(
                "openai",
                "plugins",
                "1234" * 10,
                "/tmp/plugin-installer",
                "Plugins/sample-plugin",
            )

        self.assertEqual(repo_root, "/tmp/repo-git")
        self.assertEqual(transport, "git_sparse_fallback")
        zip_mock.assert_called_once()
        git_mock.assert_called_once()


if __name__ == "__main__":
    main()
