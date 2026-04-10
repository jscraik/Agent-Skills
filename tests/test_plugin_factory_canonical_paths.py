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
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def _chdir(path: Path):
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
        self._assert_defaults_anchor_to_repo_root(
            script_path=PLUGIN_BUILDER_SCRIPT,
            module_name="plugin_builder_defaults_test",
            temp_prefix="plugin-builder-cwd-",
        )

    def test_plugin_creator_skill_uses_repo_local_script_path(self) -> None:
        skill_doc = PLUGIN_CREATOR_SKILL.read_text(encoding="utf-8")
        self.assertIn("skills-system/plugin-creator/scripts/create_basic_plugin.py", skill_doc)
        self.assertNotIn(
            ".agents/skills/plugin-creator/scripts/create_basic_plugin.py",
            skill_doc,
        )


if __name__ == "__main__":
    unittest.main()
