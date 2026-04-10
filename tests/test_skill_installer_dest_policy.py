import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = (
    REPO_ROOT
    / "skills-system"
    / "skill-installer"
    / "scripts"
    / "install-skill-from-github.py"
)
INSTALLER_DIR = INSTALLER_PATH.parent


def _load_installer():
    if str(INSTALLER_DIR) not in sys.path:
        sys.path.insert(0, str(INSTALLER_DIR))
    module_name = "skill_installer_dest_policy"
    spec = importlib.util.spec_from_file_location(module_name, INSTALLER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


installer = _load_installer()


class SkillInstallerDestPolicyTests(unittest.TestCase):
    def test_resolve_dest_root_requires_canonical_repo(self) -> None:
        with patch.object(installer, "_canonical_repo_dest", return_value=None):
            with self.assertRaises(installer.InstallError):
                installer._resolve_dest_root(None)

    def test_resolve_dest_root_defaults_to_canonical_dest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            canonical = Path(tmpdir) / "agent-skills" / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                resolved = installer._resolve_dest_root(None)
        self.assertEqual(Path(resolved), canonical.resolve())

    def test_resolve_dest_root_allows_repo_relative_category(self) -> None:
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            repo_root = Path(tmpdir) / "agent-skills"
            canonical = repo_root / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                resolved = installer._resolve_dest_root("utilities")
        self.assertEqual(Path(resolved), (repo_root / "utilities").resolve())

    def test_resolve_dest_root_rejects_destination_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            canonical = Path(tmpdir) / "agent-skills" / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                with self.assertRaises(installer.InstallError):
                    installer._resolve_dest_root("/tmp/not-canonical")


if __name__ == "__main__":
    unittest.main()
