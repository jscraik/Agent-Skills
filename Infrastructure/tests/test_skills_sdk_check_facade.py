import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/check-receipt.v1.schema.json"
PUBLIC_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-check.v1.schema.json"
TARGET = "Skills/agent-ops/simplify"
UNMATERIALIZED_TARGET = "Skills/agent-ops/improve-agent-native"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("XDG_CACHE_HOME", "/private/tmp/agent-skills-xdg-cache")
    env.setdefault("XDG_STATE_HOME", "/private/tmp/agent-skills-xdg-state")
    env.setdefault("MISE_CACHE_DIR", "/private/tmp/agent-skills-mise-cache")
    env.setdefault("UV_CACHE_DIR", "/private/tmp/agent-skills-uv-cache")
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


class TestSkillsSdkCheckFacade(unittest.TestCase):
    def test_ask_sdk_check_emits_schema_valid_receipt(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "check",
            TARGET,
            "--json",
            "--robot",
        )
        check = payload["data"]["skills_sdk_check"]

        self.assertEqual(check["schema_version"], "skills-sdk-check.v1")
        self.assertEqual(check["facade_command"], "skills-sdk check")
        self.assertEqual(check["receipt"]["command"], "skills-sdk check")
        self.assertEqual(check["receipt"]["failure_class"], "none")
        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["doctor_status"], "warning")
        self.assertEqual(check["canonical_source_path"], "Skills/agent-ops/simplify/SKILL.md")
        self.assertEqual(
            check["claims_boundary"],
            "This checks local source readiness; it does not prove package readiness, runtime reachability, task outcome, publication, or release readiness.",
        )
        self.assertEqual(
            check["next_command"],
            "./bin/ask skills package verify Skills/agent-ops/simplify --strict --json --robot",
        )
        self.assertNotIn("skill_doctor", check)
        self.assertLess(len(json.dumps(payload)), 10_240)
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, check["receipt"], {"check-receipt": schema})
        public_schema = json.loads(PUBLIC_SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema_subset(
            public_schema,
            check,
            {"check-receipt": schema, SCHEMA_PATH.name: schema},
        )

    def test_check_validates_source_without_requiring_workspace_projection(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "check",
            UNMATERIALIZED_TARGET,
            "--json",
            "--robot",
        )

        check = payload["data"]["skills_sdk_check"]
        self.assertEqual(check["status"], "pass")
        self.assertEqual(check["failure_class"], "none")
        self.assertEqual(check["doctor_status"], "warning")
        self.assertEqual(
            check["next_command"],
            "./bin/ask skills package verify Skills/agent-ops/improve-agent-native --strict --json --robot",
        )

    def test_public_wrapper_preserves_ask_sdk_contract(self) -> None:
        ask_payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "check",
            TARGET,
            "--json",
            "--robot",
        )
        wrapper_payload = _run_json_command(
            sys.executable,
            "bin/skills-sdk",
            "check",
            TARGET,
            "--json",
            "--robot",
        )

        ask_check = ask_payload["data"]["skills_sdk_check"]
        wrapper_check = wrapper_payload["data"]["skills_sdk_check"]
        self.assertEqual(wrapper_check["schema_version"], ask_check["schema_version"])
        self.assertEqual(wrapper_check["status"], ask_check["status"])
        self.assertEqual(wrapper_check["receipt"], ask_check["receipt"])
        self.assertEqual(wrapper_payload["metadata"]["command"], f"sdk check {TARGET} --json --robot")

    def test_default_help_exposes_only_the_local_sdk_entrypoints(self) -> None:
        for command in (
            [sys.executable, "Infrastructure/bin/ask", "sdk", "--help"],
            [sys.executable, "bin/skills-sdk", "--help"],
        ):
            with self.subTest(command=command):
                process = subprocess.run(
                    command,
                    cwd=REPO_ROOT,
                    env=_command_env(),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )

                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn("check", process.stdout)
                self.assertIn("start", process.stdout)
                self.assertNotIn("\n    lifecycle", process.stdout)
                self.assertNotIn("\n    status", process.stdout)
                self.assertNotIn("\n    observability", process.stdout)
                expert_help = subprocess.run(
                    [command[0], *command[1:-1], "eval", "--help"],
                    cwd=REPO_ROOT,
                    env=_command_env(),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(expert_help.returncode, 0, expert_help.stderr)


if __name__ == "__main__":
    unittest.main()
