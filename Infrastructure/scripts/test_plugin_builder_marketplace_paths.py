#!/usr/bin/env python3
"""Regression tests for Codex plugin-builder marketplace path handling."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from unittest import mock
from unittest import TestCase, main
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "utilities" / "plugin-builder" / "scripts" / "plugin_builder.py"
SPEC = importlib.util.spec_from_file_location("plugin_builder", MODULE_PATH)
assert SPEC and SPEC.loader
plugin_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin_builder)


def _write_valid_plugin(plugin_root: Path, plugin_name: str) -> None:
    (plugin_root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    manifest = plugin_builder.build_plugin_json(
        plugin_name,
        {
            "skills": False,
            "hooks": False,
            "mcp": False,
            "apps": False,
            "agents": False,
            "assets": False,
        },
    )
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_provenance_manifest(
    path: Path,
    *,
    plugin_name: str,
    verified: bool,
    reason: str,
    emails: list[str] | None = None,
    logins: list[str] | None = None,
) -> None:
    payload = {
        "schema_version": "1.0",
        "plugin_name": plugin_name,
        "source": {
            "owner": "openai",
            "repo": "plugins",
            "ref_requested": "a" * 40,
            "resolved_commit": "a" * 40,
            "path": "Plugins/example-plugin",
        },
        "commit_verification": {
            "verified": verified,
            "reason": reason,
        },
        "signer_identity": {
            "emails": emails if emails is not None else ["release@openai.com"],
            "logins": logins if logins is not None else ["release-bot"],
            "attested_emails": emails if emails is not None else ["release@openai.com"],
            "attested_logins": [],
            "metadata_emails": emails if emails is not None else ["release@openai.com"],
            "metadata_logins": logins if logins is not None else ["release-bot"],
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_validate(
    *,
    plugin_root: Path,
    marketplace_path: Path,
    extra_marketplace_path: list[str] | None = None,
    require_marketplace: bool = False,
    provenance_manifest: str | None = None,
    require_signed_provenance: bool = False,
    allow_signer_email: list[str] | None = None,
    allow_signer_domain: list[str] | None = None,
    allow_signer_login: list[str] | None = None,
) -> int:
    args = argparse.Namespace(
        plugin_path=str(plugin_root),
        marketplace_path=str(marketplace_path),
        extra_marketplace_path=extra_marketplace_path or [],
        require_marketplace=require_marketplace,
        show_terminology_map=False,
        allow_legacy_marketplace_path=False,
        provenance_manifest=provenance_manifest,
        require_signed_provenance=require_signed_provenance,
        allow_signer_email=allow_signer_email or [],
        allow_signer_domain=allow_signer_domain or [],
        allow_signer_login=allow_signer_login or [],
    )
    return plugin_builder._run_validate(args)


class PluginBuilderMarketplacePathTests(TestCase):
    def test_uv_python_command_requires_uv_binary(self) -> None:
        with mock.patch.object(plugin_builder.shutil, "which", return_value=None):
            with self.assertRaises(RuntimeError) as context:
                plugin_builder._uv_python_command()

        self.assertIn("uv is required", str(context.exception))

    def test_repo_root_relative_path_for_plugins_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            marketplace_path = repo_root / "plugins" / "marketplace.json"

            path = plugin_builder._relative_repo_source_path(plugin_root, marketplace_path)

            self.assertEqual(path, "./Plugins/example-plugin")

    def test_repo_root_relative_path_for_agents_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            agents_plugins = repo_root / ".agents" / "plugins"
            agents_plugins.mkdir(parents=True)
            marketplace_path = agents_plugins / "marketplace.json"

            path = plugin_builder._relative_repo_source_path(plugin_root, marketplace_path)

            self.assertEqual(path, "./Plugins/example-plugin")

    def test_marketplace_root_rejects_nested_plugins_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            nested_marketplace = repo_root / "custom" / "plugins" / "marketplace.json"
            nested_marketplace.parent.mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "Marketplace file must live at"):
                plugin_builder._marketplace_repo_root(nested_marketplace)

    def test_relative_repo_source_path_strict_mode_rejects_legacy_marketplace_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            legacy_marketplace = repo_root / "plugins" / "marketplace.json"
            legacy_marketplace.parent.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(ValueError, "OpenAI/Codex marketplace mode"):
                plugin_builder._relative_repo_source_path(
                    plugin_root,
                    legacy_marketplace,
                    strict_openai_layout=True,
                )

    def test_relative_repo_source_path_strict_mode_accepts_agents_symlink_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            legacy_plugins = repo_root / "plugins"
            agents_dir = repo_root / ".agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / "plugins").symlink_to(legacy_plugins, target_is_directory=True)
            marketplace_path = agents_dir / "plugins" / "marketplace.json"
            marketplace_path.write_text('{"name":"test","plugins":[]}\n', encoding="utf-8")

            path = plugin_builder._relative_repo_source_path(
                plugin_root,
                marketplace_path,
                strict_openai_layout=True,
            )

            self.assertEqual(path, "./Plugins/example-plugin")

    def test_relative_plugin_path_validator_rejects_parent_segments(self) -> None:
        self.assertFalse(plugin_builder._is_relative_plugin_path("./Plugins/example/../escape"))

    def test_marketplace_entry_rejects_plugins_dir_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            marketplace_path = repo_root / "plugins" / "marketplace.json"
            payload = {
                "name": "local-marketplace",
                "interface": {"displayName": "Local Marketplace"},
                "plugins": [
                    {
                        "name": "example-plugin",
                        "source": {
                            "source": "local",
                            "path": "./example-plugin",
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                            "products": ["CODEX"],
                        },
                        "category": "Productivity",
                    }
                ],
            }

            failures = plugin_builder._check_marketplace_entry(
                payload,
                "example-plugin",
                plugin_root,
                marketplace_path,
            )

            self.assertTrue(
                any("./Plugins/example-plugin" in failure for failure in failures),
                failures,
            )

    def test_marketplace_entry_requires_policy_products(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()
            plugin_root = repo_root / "plugins" / "example-plugin"
            plugin_root.mkdir(parents=True)
            agents_plugins = repo_root / ".agents" / "plugins"
            agents_plugins.mkdir(parents=True)
            marketplace_path = agents_plugins / "marketplace.json"
            payload = {
                "name": "local-marketplace",
                "interface": {"displayName": "Local Marketplace"},
                "plugins": [
                    {
                        "name": "example-plugin",
                        "source": {
                            "source": "local",
                            "path": "./Plugins/example-plugin",
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                        "category": "Productivity",
                    }
                ],
            }

            failures = plugin_builder._check_marketplace_entry(
                payload,
                "example-plugin",
                plugin_root,
                marketplace_path,
                strict_openai_layout=True,
            )

            self.assertTrue(
                any("policy.products must include at least one product" in failure for failure in failures),
                failures,
            )

    def test_validate_accepts_partial_marketplace_failures_when_one_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")

            good_marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
            good_marketplace.parent.mkdir(parents=True, exist_ok=True)
            good_marketplace.write_text(
                json.dumps(
                    {
                        "name": "local-marketplace",
                        "interface": {"displayName": "Local Marketplace"},
                        "plugins": [
                            {
                                "name": "example-plugin",
                                "source": {"source": "local", "path": "./Plugins/example-plugin"},
                                "policy": {
                                    "installation": "AVAILABLE",
                                    "authentication": "ON_INSTALL",
                                    "products": ["CODEX"],
                                },
                                "category": "Productivity",
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            bad_marketplace = repo_root / ".agents" / "plugins" / "bad-marketplace.json"
            bad_marketplace.write_text("{not json}\n", encoding="utf-8")

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=good_marketplace,
                extra_marketplace_path=[str(bad_marketplace)],
                require_marketplace=True,
            )
            self.assertEqual(code, 0)

    def test_validate_fails_unsigned_provenance_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=False,
                reason="unsigned",
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
            )
            self.assertEqual(code, 2)

    def test_validate_accepts_signed_provenance_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
            )
            self.assertEqual(code, 0)

    def test_validate_fails_when_signer_allowlist_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
                emails=["unknown@example.org"],
                logins=["unknown-user"],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
                allow_signer_email=["trusted@example.com"],
                allow_signer_domain=["openai.com"],
                allow_signer_login=["trusted-bot"],
            )
            self.assertEqual(code, 2)

    def test_validate_accepts_matching_signer_domain_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
                emails=["release@openai.com"],
                logins=["release-bot"],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
                allow_signer_domain=["openai.com"],
            )
            self.assertEqual(code, 0)

    def test_validate_accepts_matching_signer_login_allowlist_with_metadata_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
                emails=["release@openai.com"],
                logins=["release-bot"],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
                allow_signer_login=["release-bot"],
            )
            self.assertEqual(code, 0)

    def test_validate_fails_signer_login_allowlist_when_no_login_identity_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
                emails=["release@openai.com"],
                logins=[],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
                allow_signer_login=["release-bot"],
            )
            self.assertEqual(code, 2)

    def test_validate_fails_allowlist_when_reason_is_not_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="unknown_signature_type",
                emails=["release@openai.com"],
                logins=["release-bot"],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                allow_signer_domain=["openai.com"],
            )
            self.assertEqual(code, 2)

    def test_validate_requires_all_configured_allowlist_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".git").mkdir()

            plugin_root = repo_root / "plugins" / "example-plugin"
            _write_valid_plugin(plugin_root, "example-plugin")
            provenance_path = repo_root / "tmp-provenance.json"
            _write_provenance_manifest(
                provenance_path,
                plugin_name="example-plugin",
                verified=True,
                reason="valid",
                emails=["trusted@example.com"],
                logins=["release-bot"],
            )

            code = _run_validate(
                plugin_root=plugin_root,
                marketplace_path=repo_root / ".agents" / "plugins" / "marketplace.json",
                provenance_manifest=str(provenance_path),
                require_signed_provenance=True,
                allow_signer_email=["trusted@example.com"],
                allow_signer_domain=["openai.com"],
            )
            self.assertEqual(code, 2)


if __name__ == "__main__":
    main()
