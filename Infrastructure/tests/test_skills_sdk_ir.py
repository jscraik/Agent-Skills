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

from ask.skills_sdk.ir import build_skill_ir  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_robot_envelope, validate_skill_ir  # noqa: E402


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


class TestSkillsSdkIr(unittest.TestCase):
    def test_builder_emits_strict_read_only_ir_for_skill_source(self) -> None:
        payload = build_skill_ir(REPO_ROOT, source_path=FIXTURE_SKILL / "SKILL.md", query=FIXTURE_SKILL.as_posix())
        model = validate_skill_ir(payload)

        self.assertEqual(model.schema_version, "skills-sdk.skill-ir.v0")
        self.assertEqual(model.identity.id, "skills-sdk-valid-fixture")
        self.assertEqual(model.risk.tier, "local")
        self.assertEqual(model.risk.source_kind, "docs_only")
        self.assertFalse(model.mutation_performed)

    def test_builder_preserves_declared_restricted_network_need(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_root = Path(tmpdir) / "network-skill"
            skill_root.mkdir()
            skill_md = skill_root / "SKILL.md"
            skill_md.write_text(
                "\n".join(
                    [
                        "---",
                        "name: network-skill",
                        "description: Uses a restricted network adapter.",
                        "runtime_needs:",
                        "  - network:restricted",
                        "---",
                        "",
                        "# Network Skill",
                        "",
                        "Use the network adapter only through the declared restricted profile.",
                    ]
                ),
                encoding="utf-8",
            )

            payload = build_skill_ir(REPO_ROOT, source_path=skill_md, query=skill_root.as_posix())
            model = validate_skill_ir(payload)

        self.assertEqual(model.permissions.network, "restricted")
        self.assertIn("network:restricted", model.permissions.tools)

    def test_builder_can_emit_no_filesystem_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_root = Path(tmpdir) / "no-filesystem-skill"
            skill_root.mkdir()
            skill_md = skill_root / "SKILL.md"
            skill_md.write_text(
                "\n".join(
                    [
                        "---",
                        "name: no-filesystem-skill",
                        "description: Answers from in-memory prompt context.",
                        "---",
                        "",
                        "# No Filesystem Skill",
                        "",
                        "Answer from the prompt context without reading or writing files.",
                    ]
                ),
                encoding="utf-8",
            )

            payload = build_skill_ir(REPO_ROOT, source_path=skill_md, query=skill_root.as_posix())
            model = validate_skill_ir(payload)

        self.assertEqual(model.permissions.filesystem, "none")

    def test_public_cli_builds_skill_ir(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "ir",
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
        payload = envelope.data["skills_sdk_ir"]
        self.assertIsInstance(payload, dict)
        ir = validate_skill_ir(payload["ir"])

        self.assertEqual(payload["status"], "built")
        self.assertEqual(ir.source.root, "Infrastructure/tests/fixtures/skills_sdk/valid_skill")
        self.assertIn("./bin/ask sdk ir build", payload["validation_commands"][0])

    def test_public_cli_blocks_missing_skill_source(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "ir",
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
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing", payload["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
