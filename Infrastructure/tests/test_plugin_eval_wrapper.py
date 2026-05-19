import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "Infrastructure" / "bin" / "plugin-eval"


class TestPluginEvalWrapper(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        wrapper_dest = self.root / "Infrastructure" / "bin" / "plugin-eval"
        wrapper_dest.parent.mkdir(parents=True)
        shutil.copy2(WRAPPER, wrapper_dest)
        self.wrapper = wrapper_dest

        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        fake_node = fake_bin / "node"
        fake_node.write_text("#!/usr/bin/env bash\necho NODE_ARG:$1\n", encoding="utf-8")
        fake_node.chmod(fake_node.stat().st_mode | stat.S_IXUSR)
        self.env = {
            **os.environ,
            "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _add_cached_cli(self, version: str) -> Path:
        cli = (
            self.root
            / "Plugins"
            / "cache"
            / "openai-curated"
            / "plugin-eval"
            / version
            / "scripts"
            / "plugin-eval.js"
        )
        cli.parent.mkdir(parents=True)
        cli.write_text("console.log('plugin eval')\n", encoding="utf-8")
        return cli.resolve()

    def _run(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.wrapper), *args],
            capture_output=True,
            text=True,
            env=env or self.env,
            timeout=10,
        )

    def test_uses_single_cached_cli_without_sorting(self):
        cli = self._add_cached_cli("dc902811")

        result = self._run("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"NODE_ARG:{cli}", result.stdout)

    def test_uses_explicit_cache_version(self):
        cli = self._add_cached_cli("dc902811")
        self._add_cached_cli("newer")
        env = {**self.env, "PLUGIN_EVAL_CACHE_VERSION": "dc902811"}

        result = self._run("analyze", env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"NODE_ARG:{cli}", result.stdout)

    def test_missing_explicit_cache_version_is_actionable(self):
        (self.root / "Plugins" / "cache" / "openai-curated" / "plugin-eval").mkdir(parents=True)
        env = {**self.env, "PLUGIN_EVAL_CACHE_VERSION": "missing"}

        result = self._run("--help", env=env)

        self.assertEqual(result.returncode, 1)
        self.assertIn("plugin-eval CLI not found for PLUGIN_EVAL_CACHE_VERSION=missing", result.stderr)
        self.assertIn("Expected:", result.stderr)

    def test_multiple_cached_versions_require_explicit_selection(self):
        first = self._add_cached_cli("dc902811")
        second = self._add_cached_cli("ffff0000")

        result = self._run("--help")

        self.assertEqual(result.returncode, 1)
        self.assertIn("multiple plugin-eval CLI candidates found", result.stderr)
        self.assertIn("Set PLUGIN_EVAL_CACHE_VERSION", result.stderr)
        self.assertIn(str(first), result.stderr)
        self.assertIn(str(second), result.stderr)


if __name__ == "__main__":
    unittest.main()
