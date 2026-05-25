import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "runtime-separation"
    / "validate_runtime_separation_profile_home.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_runtime_separation_profile_home", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestValidateRuntimeSeparationProfileHome(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def _write_current(self, path: Path, *, command_checks_digest: str | None) -> None:
        command_checks = {
            "repo_status": {
                "returncode": 0,
                "drift_class": None,
                "blocker_id": None,
                "normalized_fields": {"status": "success"},
            }
        }
        summary = {
            "policy_identity": "policy",
            "discovery_identity": "discovery",
            "canonical_root_digest": "root",
            "command_checks": command_checks,
            "plugin_package_root_parity": [],
        }
        if command_checks_digest is not None:
            summary["command_checks_digest"] = command_checks_digest
        path.write_text(json.dumps({"summary": summary}), encoding="utf-8")

    def test_accepts_matching_command_checks_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            current = root / "current.json"
            output = root / "profile-home.json"
            digest = self.module._json_digest(
                {
                    "repo_status": {
                        "returncode": 0,
                        "drift_class": None,
                        "blocker_id": None,
                        "normalized_fields": {"status": "success"},
                    }
                }
            )
            self._write_current(current, command_checks_digest=digest)

            with unittest.mock.patch(
                "sys.argv",
                [
                    "validate_runtime_separation_profile_home.py",
                    "--repo-root",
                    str(REPO_ROOT),
                    "--repo-current",
                    str(current),
                    "--output",
                    str(output),
                ],
            ):
                self.assertEqual(self.module.main(), 0)

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["command_checks_digest"], digest)

    def test_rejects_mismatched_command_checks_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            current = root / "current.json"
            output = root / "profile-home.json"
            self._write_current(current, command_checks_digest="stale")

            with unittest.mock.patch(
                "sys.argv",
                [
                    "validate_runtime_separation_profile_home.py",
                    "--repo-root",
                    str(REPO_ROOT),
                    "--repo-current",
                    str(current),
                    "--output",
                    str(output),
                ],
            ):
                with self.assertRaises(SystemExit) as raised:
                    self.module.main()

            self.assertIn("command_checks_digest does not match command_checks", str(raised.exception))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
