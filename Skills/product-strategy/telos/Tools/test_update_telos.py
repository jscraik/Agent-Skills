import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("UpdateTelos.ts")


class UpdateTelosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="telos-update-")
        self.root = Path(self.temp.name)
        (self.root / "TOOLS").mkdir(parents=True)
        (self.root / "USER" / "TELOS").mkdir(parents=True)
        (self.root / "TOOLS" / "LifeosConfig.ts").write_text(
            f'export function loadLifeosConfig() {{ return {{ principal: {{ timezone: "Europe/London" }}, paths: {{ userDir: "{self.root / "USER"}" }} }}; }}\n',
            encoding="utf-8",
        )
        (self.root / "USER" / "TELOS" / "STRATEGIES.md").write_text(
            "# Strategies\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_update(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["LIFEOS_DIR"] = str(self.root)
        return subprocess.run(
            ["bun", str(SCRIPT), *args],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_updates_backs_up_and_records_change(self) -> None:
        result = self.run_update(
            "STRATEGIES.md", "- Prefer inspectable delivery", "Added career strategy"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "- Prefer inspectable delivery",
            (self.root / "USER" / "TELOS" / "STRATEGIES.md").read_text(),
        )
        self.assertIn(
            "Added career strategy",
            (self.root / "USER" / "TELOS" / "updates.md").read_text(),
        )
        self.assertEqual(
            len(list((self.root / "USER" / "TELOS" / "Backups").glob("STRATEGIES-*.md"))),
            1,
        )

    def test_rejects_unsupported_file_without_writing(self) -> None:
        result = self.run_update("PRIVATE.md", "secret", "invalid")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Invalid file", result.stderr)
        self.assertFalse((self.root / "USER" / "TELOS" / "PRIVATE.md").exists())


if __name__ == "__main__":
    unittest.main()
