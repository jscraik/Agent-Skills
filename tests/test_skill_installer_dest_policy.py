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
    """
    Load the installer script as a module named 'skill_installer_dest_policy'.
    
    Adds INSTALLER_DIR to sys.path if it is not present, loads the module from INSTALLER_PATH and registers it in sys.modules under the name 'skill_installer_dest_policy'.
    
    Returns:
        module: The loaded module object.
    """
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
        """
        Verify that passing None defaults the destination root to the installer's canonical repository path.
        
        Creates a temporary repository layout, mocks `_canonical_repo_dest` to return that canonical path, calls `_resolve_dest_root(None)`, and asserts the returned path equals the canonical directory's resolved absolute path.
        """
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            canonical = Path(tmpdir) / "agent-skills" / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                resolved = installer._resolve_dest_root(None)
        self.assertEqual(Path(resolved), canonical.resolve())

    def test_resolve_dest_root_allows_repo_relative_category(self) -> None:
        """
        Verifies that a repo-relative category name resolves to a directory under the repository root.
        
        Patches the installer's canonical repository destination to a path ending with `agent-skills/github`
        and asserts that passing `"utilities"` to `_resolve_dest_root` yields the resolved path
        `agent-skills/utilities`.
        """
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            repo_root = Path(tmpdir) / "agent-skills"
            canonical = repo_root / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                resolved = installer._resolve_dest_root("utilities")
        self.assertEqual(Path(resolved), (repo_root / "utilities").resolve())

    def test_resolve_dest_root_rejects_destination_outside_repo(self) -> None:
        """
        Verifies that providing a destination path outside the canonical repository raises InstallError.
        
        Sets the canonical repository location to a temporary agent-skills/github directory and asserts that calling _resolve_dest_root with an absolute path that lies outside that repository raises installer.InstallError.
        """
        with tempfile.TemporaryDirectory(prefix="installer-canonical-") as tmpdir:
            canonical = Path(tmpdir) / "agent-skills" / "github"
            canonical.mkdir(parents=True, exist_ok=True)
            with patch.object(installer, "_canonical_repo_dest", return_value=str(canonical)):
                with self.assertRaises(installer.InstallError):
                    installer._resolve_dest_root("/tmp/not-canonical")


if __name__ == "__main__":
    unittest.main()
