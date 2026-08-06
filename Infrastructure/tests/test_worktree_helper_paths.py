from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestWorktreeHelperPaths(unittest.TestCase):
    def test_physical_infrastructure_helpers_resolve_checkout_root(self) -> None:
        expected = 'REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"'
        for relative_path in (
            "Infrastructure/scripts/new-task.sh",
            "Infrastructure/scripts/check-git-common-config.sh",
        ):
            with self.subTest(script=relative_path):
                script = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected, script)

    def test_plugin_factory_sync_runs_from_checkout_root(self) -> None:
        script = (
            REPO_ROOT
            / "Infrastructure/scripts/lifecycle-and-sync/sync_plugin_factory_family.sh"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp_path = Path(temporary_directory)
            capture_path = temp_path / "working-directory.txt"
            python_shim = temp_path / "python3"
            python_shim.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$PWD" > "$CAPTURE_PATH"\n',
                encoding="utf-8",
            )
            python_shim.chmod(0o755)
            environment = os.environ.copy()
            environment["CAPTURE_PATH"] = str(capture_path)
            environment["PATH"] = f"{temp_path}:{environment['PATH']}"

            subprocess.run(
                ["/bin/bash", str(script)],
                cwd=temp_path,
                env=environment,
                check=True,
            )

            observed_root = capture_path.read_text(encoding="utf-8").strip()
            self.assertEqual(observed_root, str(REPO_ROOT))


if __name__ == "__main__":
    unittest.main()
