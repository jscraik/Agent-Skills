from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_package_hardening_receipt, validate_robot_envelope  # noqa: E402


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


class TestSkillsSdkPackageHardening(unittest.TestCase):
    def _package_receipt(self) -> dict:
        return build_package_digest_receipt(
            REPO_ROOT,
            source_path=FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL.as_posix(),
        )

    def test_builder_emits_non_mutating_hardening_receipt(self) -> None:
        payload = build_package_hardening_receipt(self._package_receipt())
        model = validate_package_hardening_receipt(payload)

        self.assertEqual(model.schema_version, "skills-sdk.package-hardening-receipt.v0")
        self.assertEqual(model.status, "pass")
        self.assertFalse(model.mutation_performed)
        self.assertEqual(model.package_id, "skills-sdk-valid-fixture")
        self.assertEqual(model.blockers, [])
        self.assertEqual(model.included_files, ["Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"])

    def test_builder_blocks_forbidden_package_paths(self) -> None:
        package_receipt = deepcopy(self._package_receipt())
        package_receipt["manifest"]["files"].append(
            {
                "path": "Skills/sample/.ENV.production",
                "sha256": "0" * 64,
                "size_bytes": 0,
                "role": "reference",
            }
        )

        payload = build_package_hardening_receipt(package_receipt)
        model = validate_package_hardening_receipt(payload)

        self.assertEqual(model.status, "blocked")
        self.assertEqual(model.blockers[0].id, "forbidden_package_paths")
        self.assertIn("Skills/sample/.ENV.production:forbidden_env_family", model.blockers[0].evidence)

    def test_builder_blocks_root_escaping_package_paths(self) -> None:
        package_receipt = deepcopy(self._package_receipt())
        package_receipt["manifest"]["files"].extend(
            [
                {
                    "path": "/tmp/secret.txt",
                    "sha256": "0" * 64,
                    "size_bytes": 0,
                    "role": "reference",
                },
                {
                    "path": "Skills/sample/../secret.txt",
                    "sha256": "0" * 64,
                    "size_bytes": 0,
                    "role": "reference",
                },
            ]
        )

        payload = build_package_hardening_receipt(package_receipt)
        model = validate_package_hardening_receipt(payload)

        self.assertEqual(model.status, "blocked")
        self.assertEqual(model.blockers[0].id, "forbidden_package_paths")
        self.assertIn("/tmp/secret.txt:forbidden_absolute_path", model.blockers[0].evidence)
        self.assertIn("Skills/sample/../secret.txt:forbidden_parent_relative_path", model.blockers[0].evidence)

    def test_public_cli_hardens_package_identity_receipt(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "harden",
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
        payload = envelope.data["skills_sdk_package_harden"]
        self.assertIsInstance(payload, dict)
        receipt = validate_package_hardening_receipt(payload["receipt"])

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(receipt.status, "pass")
        self.assertFalse(payload["mutation_performed"])
        self.assertIn("./bin/ask sdk package harden", payload["validation_commands"][0])

    def test_public_cli_blocks_missing_skill_source(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "package",
                "harden",
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
        payload = envelope.data["skills_sdk_package_harden"]

        self.assertEqual(envelope.status, "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
