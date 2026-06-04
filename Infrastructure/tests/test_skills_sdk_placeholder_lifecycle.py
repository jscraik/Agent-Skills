import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.placeholder_lifecycle import build_placeholder_lifecycle_receipts  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/placeholder-lifecycle.v1.schema.json"
SURFACES = {"refs", "evals", "signing", "sandbox", "security_adapter", "explorer"}
FORBIDDEN_STATUSES = {"pass", "success"}


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    tmp_base = tempfile.gettempdir()
    env.setdefault("XDG_CACHE_HOME", os.path.join(tmp_base, "agent-skills-xdg-cache"))
    env.setdefault("XDG_STATE_HOME", os.path.join(tmp_base, "agent-skills-xdg-state"))
    env.setdefault("MISE_CACHE_DIR", os.path.join(tmp_base, "agent-skills-mise-cache"))
    env.setdefault("UV_CACHE_DIR", os.path.join(tmp_base, "agent-skills-uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_json_command(*args: str, expected_code: int = 0) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != expected_code:
        raise AssertionError(
            f"{' '.join(args)} returned {process.returncode}, expected {expected_code}\n"
            f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


class TestSkillsSdkPlaceholderLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {"placeholder-lifecycle": cls.schema}

    def assert_receipt_schema_valid(self, receipt: dict) -> None:
        _validate_schema_subset(self.schema, receipt, self.schemas)

    def test_sdk_lifecycle_emits_schema_valid_honest_placeholders(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lifecycle",
            "--json",
            "--robot",
        )
        lifecycle = payload["data"]["skills_sdk_placeholder_lifecycle"]

        self.assertEqual(lifecycle["status"], "placeholder")
        self.assertEqual(set(lifecycle["surfaces"]), SURFACES)
        self.assertFalse(lifecycle["feature_executed"])
        self.assertFalse(lifecycle["mutation_performed"])
        for receipt in lifecycle["receipts"]:
            with self.subTest(surface=receipt["surface"]):
                self.assert_receipt_schema_valid(receipt)
                self.assertNotIn(receipt["status"], FORBIDDEN_STATUSES)
                self.assertFalse(receipt["feature_executed"])
                self.assertFalse(receipt["required_for_risk_tier"])

    def test_public_wrapper_preserves_lifecycle_placeholder_contract(self) -> None:
        ask_payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lifecycle",
            "--surface",
            "sandbox",
            "--json",
            "--robot",
        )
        wrapper_payload = _run_json_command(
            sys.executable,
            "bin/skills-sdk",
            "lifecycle",
            "--surface",
            "sandbox",
            "--json",
            "--robot",
        )

        self.assertEqual(
            wrapper_payload["data"]["skills_sdk_placeholder_lifecycle"],
            ask_payload["data"]["skills_sdk_placeholder_lifecycle"],
        )
        self.assertEqual(
            wrapper_payload["metadata"]["command"],
            "sdk lifecycle --surface sandbox --json --robot",
        )

    def test_missing_required_adapters_block_for_high_risk_without_credentials(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lifecycle",
            "--risk-tier",
            "high",
            "--json",
            "--robot",
            expected_code=2,
        )
        lifecycle = payload["data"]["skills_sdk_placeholder_lifecycle"]
        receipts = {receipt["surface"]: receipt for receipt in lifecycle["receipts"]}

        self.assertEqual(lifecycle["status"], "blocked")
        self.assertEqual(lifecycle["blocked_surfaces"], ["sandbox", "security_adapter"])
        self.assertEqual(receipts["sandbox"]["status"], "blocked")
        self.assertEqual(receipts["sandbox"]["adapter_state"], "missing")
        self.assertTrue(receipts["sandbox"]["required_for_risk_tier"])
        self.assertEqual(receipts["security_adapter"]["status"], "blocked")
        self.assertEqual(receipts["security_adapter"]["adapter_state"], "missing")
        self.assertTrue(receipts["security_adapter"]["required_for_risk_tier"])
        for receipt in lifecycle["receipts"]:
            self.assertFalse(receipt["feature_executed"])

    def test_placeholder_builder_does_not_write_receipts_or_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            watched_paths = [
                repo_root / ".harness" / "receipts" / "skills-sdk" / "placeholders" / "refs.json",
                repo_root / ".harness" / "receipts" / "skills-sdk" / "placeholders" / "sandbox.json",
                repo_root / ".agents" / "skills",
                repo_root / ".codex" / "skills",
                repo_root / "skills.lock.json",
            ]

            lifecycle = build_placeholder_lifecycle_receipts(risk_tier="published")

            self.assertEqual(lifecycle["status"], "blocked")
            self.assertFalse(lifecycle["feature_executed"])
            self.assertFalse(lifecycle["mutation_performed"])
            for path in watched_paths:
                self.assertFalse(path.exists(), f"placeholder lifecycle unexpectedly wrote {path}")


if __name__ == "__main__":
    unittest.main()
