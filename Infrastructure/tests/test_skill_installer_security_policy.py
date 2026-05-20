import importlib.util
import json
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_PATH = (
    REPO_ROOT
    / "Plugins"
    / "skill-factory"
    / "skills"
    / "infrastructure_ops"
    / "skill-installer"
    / "scripts"
    / "install-skill-from-github.pyw"
)
INSTALLER_DIR = INSTALLER_PATH.parent
SYSTEM_INSTALLER = (
    REPO_ROOT
    / "skills-system"
    / "skill-installer"
    / "scripts"
    / "install-skill-from-github.py"
)


def _load_installer():
    """
    Dynamically load the installer script from INSTALLER_PATH and return it as a module.

    If INSTALLER_DIR is not already on sys.path, it is inserted. The loaded module is registered in
    sys.modules under the name "skill_installer_security_policy".

    Returns:
        module: The imported installer module object.
    """
    if str(INSTALLER_DIR) not in sys.path:
        sys.path.insert(0, str(INSTALLER_DIR))
    module_name = "skill_installer_security_policy"
    loader = SourceFileLoader(module_name, str(INSTALLER_PATH))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


installer = _load_installer()
system_installer = installer._MODULE


class SkillInstallerSecurityPolicyTests(unittest.TestCase):
    def test_extract_commit_signer_identity_prefers_attested_payload(self) -> None:
        payload = {
            "commit": {
                "verification": {
                    "payload": "tree deadbeef\nauthor Dev One <attested@example.com> 1710000000 +0000\ncommitter Dev One <attested@example.com> 1710000000 +0000\n",
                },
                "author": {"email": "meta@example.com"},
                "committer": {"email": "meta@example.com"},
            },
            "author": {"login": "meta-login"},
            "committer": {"login": "meta-login"},
        }
        identity = installer._extract_commit_signer_identity(payload)
        self.assertEqual(identity["attested_emails"], ["attested@example.com"])
        self.assertEqual(identity["metadata_emails"], ["meta@example.com"])
        self.assertEqual(identity["metadata_logins"], ["meta-login"])

    def test_rejects_untrusted_source_by_default(self) -> None:
        args = [
            "--repo",
            "unknown-owner/unknown-repo",
            "--path",
            "Skills/.curated/example",
            "--ref",
            "0" * 40,
        ]
        code = installer.main(args)
        self.assertEqual(code, 1)

    def test_rejects_unpinned_ref_without_override(self) -> None:
        args = [
            "--repo",
            "openai/skills",
            "--path",
            "Skills/.curated/example",
            "--ref",
            "main",
        ]
        code = installer.main(args)
        self.assertEqual(code, 1)

    def test_compatibility_installer_trusts_canonical_agent_skills_repo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "jscraik/agent-skills",
                                "--path",
                                "skills/sample",
                                "--ref",
                                "a" * 40,
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())

    def test_canonical_installer_rejects_unpinned_ref_without_override(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            code = system_installer.main(
                [
                    "--repo",
                    "openai/skills",
                    "--path",
                    "Skills/.curated/example",
                    "--ref",
                    "main",
                    "--dest",
                    tmpdir,
                ]
            )
        self.assertEqual(code, 1)

    def test_canonical_resolves_verified_commit_provenance(self) -> None:
        payload = {
            "sha": "A" * 40,
            "commit": {
                "verification": {
                    "verified": True,
                    "reason": "valid",
                    "payload": "tree deadbeef\nauthor Dev <Dev@Example.com> 1710000000 +0000\ncommitter Dev <Dev@Example.com> 1710000000 +0000\n",
                    "signature": "signature",
                },
            },
            "author": {"login": "DevUser"},
        }
        with patch.object(system_installer, "_request", return_value=json.dumps(payload).encode("utf-8")):
            sha, verification, identity = system_installer._resolve_commit_provenance("openai", "skills", "A" * 40)

        self.assertEqual(sha, "a" * 40)
        self.assertTrue(verification["verified"])
        self.assertEqual(verification["reason"], "valid")
        self.assertEqual(identity["attested_emails"], ["dev@example.com"])
        self.assertEqual(identity["metadata_logins"], ["devuser"])

    def test_compatibility_resolver_delegates_to_canonical_provenance(self) -> None:
        expected = ("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]})
        with patch.object(system_installer, "_resolve_commit_provenance", return_value=expected) as resolve:
            actual = installer._resolve_commit_provenance("openai", "skills", "a" * 40)

        self.assertEqual(actual, expected)
        resolve.assert_called_once_with("openai", "skills", "a" * 40)

    def test_allows_untrusted_with_override(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "unknown-owner/unknown-repo",
                                "--path",
                                "Skills/sample",
                                "--ref",
                                "a" * 40,
                                "--allow-untrusted-source",
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())

    def test_rejects_symlinked_files_before_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")
            outside = Path(tmpdir) / "outside.txt"
            outside.write_text("secret\n", encoding="utf-8")
            (skill_dir / "leak.txt").symlink_to(outside)

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "openai/skills",
                                "--path",
                                "skills/sample",
                                "--ref",
                                "a" * 40,
                            ]
                        )

            self.assertEqual(code, 1)
            self.assertFalse((dest_root / "sample").exists())

    def test_legacy_url_installs_without_repo_path_flags(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--url",
                                f"https://github.com/openai/skills/tree/{'a' * 40}/skills/sample",
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())

    def test_accepts_uppercase_pinned_commit_sha(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "openai/skills",
                                "--path",
                                "skills/sample",
                                "--ref",
                                "A" * 40,
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())

    def test_rejects_signer_allowlist_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "openai/skills",
                                "--path",
                                "Skills/sample",
                                "--ref",
                                "a" * 40,
                                "--allowed-signer-domain",
                                "other.example",
                            ]
                        )

            self.assertEqual(code, 1)

    def test_allows_signer_allowlist_match(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=("a" * 40, {"verified": True, "reason": "valid"}, {"emails": ["dev@example.com"], "logins": ["dev"]}),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "openai/skills",
                                "--path",
                                "Skills/sample",
                                "--ref",
                                "a" * 40,
                                "--allowed-signer-domain",
                                "example.com",
                                "--allowed-signer-login",
                                "dev",
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())

    def test_allows_signer_allowlist_match_case_insensitively(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-installer-policy-") as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            skill_dir = repo_root / "skills" / "sample"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Sample\n", encoding="utf-8")

            dest_root = Path(tmpdir) / "dest"
            dest_root.mkdir(parents=True)

            with patch.object(installer, "_resolve_dest_root", return_value=str(dest_root)):
                with patch.object(
                    installer,
                    "_resolve_commit_provenance",
                    return_value=(
                        "a" * 40,
                        {"verified": True, "reason": "valid"},
                        {"emails": ["Dev@Example.COM"], "logins": ["DevUser"]},
                    ),
                ):
                    with patch.object(installer, "_prepare_repo", return_value=(str(repo_root), "zipball")):
                        code = installer.main(
                            [
                                "--repo",
                                "openai/skills",
                                "--path",
                                "Skills/sample",
                                "--ref",
                                "a" * 40,
                                "--allowed-signer-email",
                                "dev@example.com",
                                "--allowed-signer-login",
                                "devuser",
                            ]
                        )

            self.assertEqual(code, 0)
            self.assertTrue((dest_root / "sample" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
