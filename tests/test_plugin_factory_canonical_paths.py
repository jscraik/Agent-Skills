import importlib.util
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_CREATOR_SCRIPT = (
    REPO_ROOT / "plugins" / "plugin-factory" / "skills" / "plugin-creator" / "scripts" / "create_basic_plugin.py"
)
PLUGIN_BUILDER_SCRIPT = (
    REPO_ROOT / "plugins" / "plugin-factory" / "skills" / "plugin-builder" / "scripts" / "plugin_builder.py"
)
PLUGIN_CREATOR_SKILL = REPO_ROOT / "plugins" / "plugin-factory" / "skills" / "plugin-creator" / "SKILL.md"


def _load_module(module_name: str, script_path: Path):
    """
    Load a Python module from a given file path under a specific module name.
    
    Parameters:
        module_name (str): The name to assign to the loaded module.
        script_path (Path): Filesystem path to the Python source file to import.
    
    Returns:
        module: The loaded module object.
    
    Raises:
        RuntimeError: If an import spec or loader cannot be created for the given script_path.
    """
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def _chdir(path: Path):
    """
    Context manager that temporarily changes the process working directory to the given path.
    
    On exit — including when an exception is raised inside the context — the original working directory is restored.
    
    Parameters:
        path (Path): Directory to switch to for the duration of the context.
    """
    original_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_cwd)


class TestPluginFactoryCanonicalPaths(unittest.TestCase):
    def _assert_defaults_anchor_to_repo_root(
        self, *, script_path: Path, module_name: str, temp_prefix: str
    ) -> None:
        """
        Assert that a plugin script's path constants remain anchored to the repository root rather than the current working directory.
        
        Verifies that the loaded module's `REPO_ROOT`, `DEFAULT_PLUGIN_PARENT` and `DEFAULT_MARKETPLACE_PATH` resolve to the repository-level locations and that `DEFAULT_PLUGIN_PARENT` is not derived from a temporary CWD created for the test.
        
        Parameters:
        	script_path (Path): Filesystem path to the plugin script to import.
        	module_name (str): Module name to use when loading the script.
        	temp_prefix (str): Prefix for the temporary directory created for the test.
        """
        with tempfile.TemporaryDirectory(prefix=temp_prefix) as temp_dir:
            temp_path = Path(temp_dir)
            with _chdir(temp_path):
                module = _load_module(module_name, script_path)
        self.assertEqual(module.REPO_ROOT, REPO_ROOT)
        self.assertEqual(module.DEFAULT_PLUGIN_PARENT, REPO_ROOT / "plugins")
        self.assertEqual(
            module.DEFAULT_MARKETPLACE_PATH,
            REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        )
        self.assertNotEqual(module.DEFAULT_PLUGIN_PARENT, temp_path / "plugins")

    def test_plugin_creator_defaults_anchor_to_repo_root(self) -> None:
        self._assert_defaults_anchor_to_repo_root(
            script_path=PLUGIN_CREATOR_SCRIPT,
            module_name="plugin_creator_defaults_test",
            temp_prefix="plugin-creator-cwd-",
        )

    def test_plugin_builder_defaults_anchor_to_repo_root(self) -> None:
        """
        Verify the plugin builder's default path constants are anchored to the repository root.
        
        Loads the plugin builder script from its file path while the process CWD is a temporary directory and asserts that the module's `REPO_ROOT`, `DEFAULT_PLUGIN_PARENT` and `DEFAULT_MARKETPLACE_PATH` resolve to repository-local paths (not to paths under the temporary CWD).
        """
        self._assert_defaults_anchor_to_repo_root(
            script_path=PLUGIN_BUILDER_SCRIPT,
            module_name="plugin_builder_defaults_test",
            temp_prefix="plugin-builder-cwd-",
        )

    def test_plugin_creator_skill_uses_repo_local_script_path(self) -> None:
        skill_doc = PLUGIN_CREATOR_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "plugins/plugin-factory/skills/plugin-creator/scripts/create_basic_plugin.py",
            skill_doc,
        )


if __name__ == "__main__":
    unittest.main()
