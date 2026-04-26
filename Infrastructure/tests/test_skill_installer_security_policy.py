import importlib.util
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


if __name__ == "__main__":
    unittest.main()
