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

from ask.skills_sdk.emitter_contracts import validate_emitter_preview_receipt  # noqa: E402
from ask.skills_sdk.emitter_preview import build_emitter_preview_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkEmitterPreview(unittest.TestCase):
    def test_emitter_preview_command_builds_non_mutating_write_plan(self) -> None:
        process = _run_ask(
            "sdk",
            "emitter",
            "preview",
            "--skill",
            FIXTURE_SKILL,
            "--preview",
            "--json",
            "--robot",
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_emitter_preview"]
        receipt = payload["receipt"]

        self.assertEqual(envelope["status"], "success")
        self.assertEqual(payload["status"], "preview")
        self.assertEqual(payload["facade_command"], "skills-sdk emitter preview")
        self.assertEqual(receipt["projection"], "runtime-skill")
        self.assertEqual(receipt["target_root"], ".agents/skills")
        self.assertEqual(
            receipt["write_plan"][0]["target_path"],
            ".agents/skills/skills-sdk-valid-fixture/SKILL.md",
        )
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["artifact_emitted"])
        self.assertFalse(receipt["remote_publish_requested"])

    def test_emitter_preview_requires_explicit_preview_flag(self) -> None:
        process = _run_ask(
            "sdk",
            "emitter",
            "preview",
            "--skill",
            FIXTURE_SKILL,
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_emitter_preview_keeps_skill_instructions_first_when_manifest_is_reversed(self) -> None:
        package_receipt = build_package_digest_receipt(
            REPO_ROOT,
            source_path=REPO_ROOT / FIXTURE_SKILL / "SKILL.md",
            query=FIXTURE_SKILL,
        )
        package_receipt["manifest"]["files"] = list(reversed(package_receipt["manifest"]["files"]))
        hardening_receipt = build_package_hardening_receipt(package_receipt)

        receipt = build_emitter_preview_receipt(
            REPO_ROOT,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
        )

        self.assertTrue(receipt["write_plan"][0]["source_path"].endswith("/SKILL.md"))
        self.assertFalse(receipt["mutation_performed"])

    def test_emitter_preview_blocks_non_local_projection_roots(self) -> None:
        process = _run_ask(
            "sdk",
            "emitter",
            "preview",
            "--skill",
            FIXTURE_SKILL,
            "--target-root",
            "https://registry.example/skills",
            "--preview",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_emitter_preview"]
        receipt = payload["receipt"]

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["target_root"], ".agents/skills")
        self.assertEqual(receipt["write_plan"], [])
        self.assertTrue(
            any(check["id"] == "target_root_local_projection" for check in receipt["blockers"])
        )
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["artifact_emitted"])
        validate_emitter_preview_receipt(receipt)

    def test_emitter_preview_blocks_absolute_projection_roots(self) -> None:
        process = _run_ask(
            "sdk",
            "emitter",
            "preview",
            "--skill",
            FIXTURE_SKILL,
            "--target-root",
            "/.agents/skills",
            "--preview",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        receipt = envelope["data"]["skills_sdk_emitter_preview"]["receipt"]

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["target_root"], ".agents/skills")
        self.assertEqual(receipt["write_plan"], [])
        self.assertEqual(receipt["blockers"][0]["id"], "target_root_local_projection")
        validate_emitter_preview_receipt(receipt)

    def test_emitter_preview_normalizes_trailing_slash_projection_root(self) -> None:
        process = _run_ask(
            "sdk",
            "emitter",
            "preview",
            "--skill",
            FIXTURE_SKILL,
            "--target-root",
            ".agents/skills/",
            "--preview",
            "--json",
            "--robot",
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        receipt = envelope["data"]["skills_sdk_emitter_preview"]["receipt"]

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["target_root"], ".agents/skills")
        self.assertTrue(receipt["write_plan"][0]["target_path"].startswith(".agents/skills/"))

    def test_emitter_preview_builder_blocks_failed_hardening_receipt(self) -> None:
        package_receipt = json.loads(
            (REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/package-digest-receipt.json").read_text(
                encoding="utf-8"
            )
        )
        hardening_receipt = build_package_hardening_receipt(package_receipt)
        hardening_receipt["status"] = "blocked"

        with self.assertRaisesRegex(ValueError, "blocked"):
            build_emitter_preview_receipt(
                REPO_ROOT,
                package_receipt=package_receipt,
                hardening_receipt=hardening_receipt,
            )


if __name__ == "__main__":
    unittest.main()
