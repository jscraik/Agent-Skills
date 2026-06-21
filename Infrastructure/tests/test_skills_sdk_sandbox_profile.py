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

from ask.skills_sdk.sandbox_profile import build_sandbox_profile_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_robot_envelope, validate_sandbox_profile_receipt  # noqa: E402


VALID_PROFILE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/sandbox-profile.json"
UNSAFE_PROFILE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/invalid/sandbox-profile-allow-default.json"
BAD_ENUM_PROFILE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/invalid/sandbox-profile-bad-enums.json"
ROOT_READ_PROFILE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/invalid/sandbox-profile-root-read.json"
RECEIPT_SCHEMA = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sandbox-profile-receipt.v0.schema.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    tmp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(tmp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(tmp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(tmp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(tmp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(tmp_base / "uv-cache"))
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


class TestSkillsSdkSandboxProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt_schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))

    def assert_receipt_schema_valid(self, receipt: dict) -> None:
        _validate_schema_subset(self.receipt_schema, receipt, {"sandbox-profile-receipt": self.receipt_schema})

    def test_valid_deny_by_default_profile_passes_without_execution(self) -> None:
        receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=VALID_PROFILE)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["profile_id"], "skills-sdk-deny-default-local")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])
        self.assertFalse(receipt["mutation_performed"])
        self.assertEqual(receipt["blockers"], [])
        self.assert_receipt_schema_valid(receipt)
        validate_sandbox_profile_receipt(receipt)

    def test_unsafe_profile_blocks_without_selecting_execution_provider(self) -> None:
        receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=UNSAFE_PROFILE)
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("deny_by_default", blocker_ids)
        self.assertIn("filesystem_read_scope", blocker_ids)
        self.assertIn("filesystem_write_scope", blocker_ids)
        self.assertIn("network_egress_denied", blocker_ids)
        self.assertIn("execution_provider_not_selected", blocker_ids)
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])
        self.assertFalse(receipt["mutation_performed"])
        self.assert_receipt_schema_valid(receipt)

    def test_schema_invalid_profile_still_emits_schema_valid_blocked_receipt(self) -> None:
        receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=BAD_ENUM_PROFILE)
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("profile_schema", blocker_ids)
        self.assertIsNone(receipt["risk_tier"])
        self.assertIsNone(receipt["default_policy"])
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])
        self.assert_receipt_schema_valid(receipt)
        validate_sandbox_profile_receipt(receipt)

    def test_repo_root_read_alias_blocks_as_broad_filesystem_scope(self) -> None:
        receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=ROOT_READ_PROFILE)
        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        read_blocker = next(blocker for blocker in receipt["blockers"] if blocker["id"] == "filesystem_read_scope")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("filesystem_read_scope", blocker_ids)
        self.assertIn(".", read_blocker["evidence"])
        self.assertIn("~/.ssh", read_blocker["evidence"])
        self.assertIn("Secrets/*", read_blocker["evidence"])
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])
        self.assert_receipt_schema_valid(receipt)

    def test_shell_program_allowlist_blocks_when_shell_execution_disabled(self) -> None:
        profile = json.loads((REPO_ROOT / VALID_PROFILE).read_text(encoding="utf-8"))
        profile["commands"]["allow"] = ["bash"]

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / "sandbox-profile.json"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=profile_path.as_posix())

        blocker_ids = {blocker["id"] for blocker in receipt["blockers"]}
        allowlist_blocker = next(
            blocker for blocker in receipt["blockers"] if blocker["id"] == "command_allowlist_present"
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("command_allowlist_present", blocker_ids)
        self.assertIn("bash", allowlist_blocker["evidence"])
        self.assertFalse(receipt["execution_performed"])
        self.assert_receipt_schema_valid(receipt)

    def test_wildcard_environment_allowlist_blocks_when_inherit_disabled(self) -> None:
        profile = json.loads((REPO_ROOT / VALID_PROFILE).read_text(encoding="utf-8"))
        profile["environment"]["allowed"] = ["*"]

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / "sandbox-profile.json"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            receipt = build_sandbox_profile_receipt(REPO_ROOT, profile_path=profile_path.as_posix())

        blocker = next(blocker for blocker in receipt["blockers"] if blocker["id"] == "environment_inheritance_denied")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("*", blocker["evidence"])
        self.assertFalse(receipt["execution_performed"])
        self.assert_receipt_schema_valid(receipt)

    def test_directory_profile_path_returns_blocked_receipt(self) -> None:
        with self.assertRaisesRegex(Exception, "could not be read") as raised:
            build_sandbox_profile_receipt(REPO_ROOT, profile_path="Infrastructure/tests/fixtures/skills_sdk/schema_spine")

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["blockers"][0]["id"], "profile_load")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])
        self.assert_receipt_schema_valid(receipt)

    def test_sdk_sandbox_validate_cli_emits_robot_envelope(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "sandbox",
            "validate",
            "--profile",
            VALID_PROFILE,
            "--json",
            "--robot",
        )
        envelope = validate_robot_envelope(payload)
        sdk_payload = envelope.data["skills_sdk_sandbox_validate"]
        self.assertIsInstance(sdk_payload, dict)
        receipt = sdk_payload["receipt"]

        self.assertEqual(payload["status"], "success")
        self.assertEqual(sdk_payload["status"], "pass")
        self.assertFalse(sdk_payload["execution_performed"])
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])

    def test_sdk_sandbox_validate_cli_blocks_high_risk_profile(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "sandbox",
            "validate",
            "--profile",
            UNSAFE_PROFILE,
            "--json",
            "--robot",
            expected_code=2,
        )
        sdk_payload = payload["data"]["skills_sdk_sandbox_validate"]
        receipt = sdk_payload["receipt"]

        self.assertEqual(payload["status"], "error")
        self.assertEqual(receipt["status"], "blocked")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["adapter_selected"])

    def test_public_wrapper_preserves_sandbox_validate_contract(self) -> None:
        ask_payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "sandbox",
            "validate",
            "--profile",
            VALID_PROFILE,
            "--json",
            "--robot",
        )
        wrapper_payload = _run_json_command(
            sys.executable,
            "bin/skills-sdk",
            "sandbox",
            "validate",
            "--profile",
            VALID_PROFILE,
            "--json",
            "--robot",
        )

        self.assertEqual(
            wrapper_payload["data"]["skills_sdk_sandbox_validate"],
            ask_payload["data"]["skills_sdk_sandbox_validate"],
        )
        self.assertEqual(
            wrapper_payload["metadata"]["command"],
            f"sdk sandbox validate --profile {VALID_PROFILE} --json --robot",
        )


if __name__ == "__main__":
    unittest.main()
