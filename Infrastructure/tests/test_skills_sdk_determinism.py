import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from ask.skills_sdk.determinism import (  # noqa: E402
    DETERMINISM_AUDIT_SCHEMA_VERSION,
    audit_skill_determinism,
)


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_json_command(*args: str) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _write_skill(path: Path, *, description: str, body: str) -> Path:
    skill_dir = path
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        f"---\nname: sample-skill\ndescription: >\n  {description}\n---\n{body}\n",
        encoding="utf-8",
    )
    return skill_path


class TestSkillsSdkDeterminism(unittest.TestCase):
    def test_audit_finds_prompt_only_determinism_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_path = _write_skill(
                temp_root / "Skills" / "sample",
                description="Reviews things with a very broad routing description.",
                body=(
                    "Return schema_version when structured output is requested.\n"
                    "Run validation after edits.\n"
                    "Use Infrastructure/references/software-literature-expert-lens-pack.md.\n"
                    "Read [missing reference](references/missing.md).\n"
                ),
            )

            payload = audit_skill_determinism(temp_root, paths=[str(skill_path)])

        areas = {candidate["area"] for candidate in payload["candidates"]}
        self.assertEqual(payload["schema_version"], DETERMINISM_AUDIT_SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["summary"]["skills_scanned"], 1)
        self.assertIn("description_trigger_contract", areas)
        self.assertIn("description_boundary_contract", areas)
        self.assertIn("lens_migration_contract", areas)
        self.assertIn("output_schema_contract", areas)
        self.assertIn("validation_command_contract", areas)
        self.assertIn("reference_integrity_contract", areas)

    def test_audit_accepts_explicit_description_boundary_and_validation_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            command = "\x60python3 -m py_compile sample.py\x60"
            skill_path = _write_skill(
                temp_root / "Skills" / "sample",
                description=(
                    "Reviews sample skills. Use this skill when checking sample skill routing. "
                    "Do not use for runtime plugin packaging."
                ),
                body=f"Run validation with {command}.\n",
            )

            payload = audit_skill_determinism(temp_root, paths=[str(skill_path)])

        areas = {candidate["area"] for candidate in payload["candidates"]}
        self.assertNotIn("description_trigger_contract", areas)
        self.assertNotIn("description_boundary_contract", areas)
        self.assertNotIn("validation_command_contract", areas)

    def test_audit_limit_is_applied_after_priority_sort(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_path = _write_skill(
                temp_root / "Skills" / "sample",
                description="Vague.",
                body="Return schema_version.\nRun validation.\n",
            )

            payload = audit_skill_determinism(temp_root, paths=[str(skill_path)], limit=1)

        self.assertEqual(payload["summary"]["candidate_count"], 1)
        self.assertEqual(len(payload["candidates"]), 1)
        self.assertEqual(payload["candidates"][0]["priority"], "high")

    def test_cli_determinism_audit_emits_json_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_path = _write_skill(
                Path(temp_dir) / "Skills" / "sample",
                description="Vague.",
                body="Return schema_version.\n",
            )

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "determinism",
                "audit",
                "--path",
                str(skill_path),
                "--json",
                "--robot",
            )

        audit = payload["data"]["determinism_audit"]
        self.assertEqual(payload["status"], "success")
        self.assertEqual(audit["schema_version"], DETERMINISM_AUDIT_SCHEMA_VERSION)
        self.assertEqual(audit["summary"]["skills_scanned"], 1)
        self.assertTrue(audit["candidates"])

    def test_command_metadata_registers_determinism_route(self) -> None:
        self.assertIn("determinism", VALID_ACTIONS["sdk"])
        self.assertIn("ask sdk determinism audit --scope skills --json --robot", COMMAND_EXAMPLES[("sdk", "determinism")])


if __name__ == "__main__":
    unittest.main()
