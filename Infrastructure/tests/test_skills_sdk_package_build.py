from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_package_digest_receipt, validate_robot_envelope  # noqa: E402


FIXTURE_SKILL = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkPackageBuild(unittest.TestCase):
    def test_builder_emits_non_mutating_package_digest_receipt(self) -> None:
        payload = build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )
        model = validate_package_digest_receipt(payload)

        self.assertEqual(model.schema_version, "skills-sdk.package-digest-receipt.v0")
        self.assertEqual(model.package_id, "skills-sdk-valid-fixture")
        self.assertEqual(model.manifest.skill_ir_schema_version, "skills-sdk.skill-ir.v0")
        self.assertFalse(model.mutation_performed)
        self.assertEqual(model.included_files, ["Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"])
        self.assertTrue(model.package_digest.startswith("sha256:"))

    def test_public_cli_builds_package_identity_receipt(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "build",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_build"]
        self.assertIsInstance(payload, dict)
        receipt = validate_package_digest_receipt(payload["receipt"])

        self.assertEqual(payload["status"], "built")
        self.assertEqual(payload["package_digest"], receipt.package_digest)
        self.assertEqual(payload["included_files"], ["Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"])
        self.assertFalse(payload["mutation_performed"])
        self.assertIn("./bin/ask sdk package build", payload["validation_commands"][0])

    def test_public_cli_blocks_missing_skill_source(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "build",
                "Infrastructure/tests/fixtures/skills_sdk/missing",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_package_build"]

        self.assertEqual(envelope.status, "error")
        self.assertEqual(envelope.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
