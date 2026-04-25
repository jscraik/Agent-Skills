import importlib.util
import os
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_CREATOR_SCRIPT = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "scaffolding_templates"
    / "plugin-creator"
    / "scripts"
    / "create_basic_plugin.pyw"
)
PLUGIN_BUILDER_SCRIPT = (
    REPO_ROOT
    / "Plugins"
    / "plugin-factory"
    / "skills"
    / "code_quality_review"
    / "plugin-builder"
    / "scripts"
    / "plugin_builder.pyw"
)
PLUGIN_CREATOR_SKILL = (
    REPO_ROOT / "Plugins" / "plugin-factory" / "skills" / "scaffolding_templates" / "plugin-creator" / "SKILL.md"
)
PLUGIN_CREATOR_WORKFLOW = PLUGIN_CREATOR_SKILL.parent / "references" / "workflow.md"


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
    loader = SourceFileLoader(module_name, str(script_path))
    spec = importlib.util.spec_from_file_location(module_name, script_path, loader=loader)
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
        self.assertEqual(module.DEFAULT_PLUGIN_PARENT, REPO_ROOT / "Plugins" / "third-party")
        self.assertEqual(
            module.DEFAULT_MARKETPLACE_PATH,
            REPO_ROOT / ".agents" / "Plugins" / "marketplace.json",
        )
        self.assertNotEqual(module.DEFAULT_PLUGIN_PARENT, temp_path / "Plugins" / "third-party")

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
        """
        Verify that the plugin-creator skill document references the workflow and that the workflow contains the repository-local `.pyw` script path for create_basic_plugin.
        
        The test reads the skill and workflow documentation files and asserts that:
        - "references/workflow.md" appears in the skill document.
        - The workflow document includes the repository-local path "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw".
        """
        skill_doc = PLUGIN_CREATOR_SKILL.read_text(encoding="utf-8")
        workflow_doc = PLUGIN_CREATOR_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("references/workflow.md", skill_doc)
        self.assertIn(
            "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw",
            workflow_doc,
        )

    def test_plugin_builder_accepts_required_codex_manifest_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="plugin-builder-validate-") as temp_dir:
            plugin_root = Path(temp_dir) / "sample-plugin"
            manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
            skills_dir = plugin_root / "skills"
            manifest_path.parent.mkdir(parents=True)
            (skills_dir / "sample-skill").mkdir(parents=True)
            (skills_dir / "sample-skill" / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Sample plugin skill.\n---\n\n# Sample Skill\n",
                encoding="utf-8",
            )
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "sample-plugin",
                        "version": "0.1.0",
                        "description": "Sample plugin for validator coverage.",
                        "author": {"name": "Agent Skills Team"},
                        "skills": "./skills/",
                        "interface": {
                            "displayName": "Sample Plugin",
                            "shortDescription": "Sample plugin",
                            "longDescription": "Sample plugin for validator coverage.",
                            "developerName": "Agent Skills Team",
                            "category": "Coding",
                            "capabilities": ["Read"],
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(PLUGIN_BUILDER_SCRIPT.with_suffix(".py")), "validate", str(plugin_root)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
