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
from ask.skills_sdk.lenses import (  # noqa: E402
    LENS_SELECTION_SCHEMA_VERSION,
    explain_lens,
    list_lenses,
    select_lenses,
    validate_lens_catalog,
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


class TestSkillsSdkLenses(unittest.TestCase):
    def test_lens_catalog_validates_seed_lenses(self) -> None:
        payload = validate_lens_catalog(REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["schema_version"], "skill-lens-catalog-validation.v1")
        self.assertEqual(payload["summary"]["lens_count"], 3)
        self.assertEqual(payload["findings"], [])

    def test_lens_catalog_lists_trigger_metadata(self) -> None:
        payload = list_lenses(REPO_ROOT)
        lens_ids = {lens["id"] for lens in payload["lenses"]}

        self.assertEqual(payload["status"], "pass")
        self.assertIn("lens.progressive-disclosure", lens_ids)
        progressive = next(lens for lens in payload["lenses"] if lens["id"] == "lens.progressive-disclosure")
        self.assertIn("skill_authoring", progressive["triggers"]["task_intents"])
        self.assertIn("SKILL.md", progressive["triggers"]["file_signals"])

    def test_lens_explain_returns_sections(self) -> None:
        payload = explain_lens(REPO_ROOT, "lens.progressive-disclosure")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["id"], "lens.progressive-disclosure")
        self.assertIn({"level": 2, "title": "Review Questions"}, payload["sections"])
        self.assertIn({"level": 2, "title": "Failure Modes"}, payload["sections"])

    def test_lens_selection_is_deterministic_for_skill_authoring(self) -> None:
        payload = select_lenses(
            REPO_ROOT,
            prompt="Review SKILL.md headings, references, and progressive disclosure for agent usability.",
            task_intent="skill_authoring",
            repo_files=["SKILL.md", "references/routing.md"],
            max_lenses=2,
            skill="sample-skill",
        )

        self.assertEqual(payload["schema_version"], LENS_SELECTION_SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["task_intent"], "skill_authoring")
        self.assertLessEqual(len(payload["selected_lenses"]), 2)
        self.assertEqual(payload["selected_lenses"][0]["id"], "lens.progressive-disclosure")
        self.assertIn("task_intent:skill_authoring", payload["selected_lenses"][0]["reasons"])
        self.assertTrue(any(reason.startswith("keyword:") for reason in payload["selected_lenses"][0]["reasons"]))

    def test_lens_selection_infers_validation_review(self) -> None:
        payload = select_lenses(
            REPO_ROOT,
            prompt="Add a regression test and CI validation gate for this eval fixture.",
            repo_files=["Infrastructure/tests/test_sample.py"],
            max_lenses=1,
        )

        self.assertEqual(payload["task_intent"], "validation_review")
        self.assertEqual(payload["selected_lenses"][0]["id"], "lens.testing-confidence")

    def test_cli_lenses_validate_emits_json_envelope(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lenses",
            "validate",
            "--json",
            "--robot",
        )

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["data"]["lens_catalog_validation"]["status"], "pass")
        self.assertEqual(payload["metadata"]["command"], "sdk lenses validate --json --robot")

    def test_cli_lenses_select_emits_selection_receipt(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lenses",
            "select",
            "--intent",
            "skill_authoring",
            "--prompt",
            "Review SKILL.md headings and references for progressive disclosure",
            "--repo-file",
            "SKILL.md",
            "--json",
            "--robot",
        )

        selection = payload["data"]["lens_selection"]
        self.assertEqual(payload["status"], "success")
        self.assertEqual(selection["schema_version"], LENS_SELECTION_SCHEMA_VERSION)
        self.assertEqual(selection["selected_lenses"][0]["id"], "lens.progressive-disclosure")
        self.assertTrue(selection["selected_lenses"][0]["reasons"])

    def test_cli_lenses_explain_emits_lens_details(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "lenses",
            "explain",
            "lens.operator-evidence",
            "--json",
            "--robot",
        )

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["data"]["lens"]["id"], "lens.operator-evidence")
        self.assertEqual(payload["data"]["lens"]["lens_type"], "expert_lens")

    def test_command_metadata_registers_lens_route(self) -> None:
        self.assertIn("lenses", VALID_ACTIONS["sdk"])
        self.assertIn("ask sdk lenses validate --json --robot", COMMAND_EXAMPLES[("sdk", "lenses")])
        self.assertTrue(
            any(command.startswith("ask sdk lenses select ") for command in COMMAND_EXAMPLES[("sdk", "lenses")])
        )


if __name__ == "__main__":
    unittest.main()
