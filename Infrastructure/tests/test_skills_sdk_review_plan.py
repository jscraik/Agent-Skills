import json
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from ask.commands.sdk import _dispatch_sdk_review  # noqa: E402
from ask.skills_sdk.lenses import KNOWN_TASK_INTENTS, LensCatalogError  # noqa: E402
from ask.skills_sdk.review_plan import (  # noqa: E402
    REVIEW_PLAN_SCHEMA_VERSION,
    build_review_plan,
)


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_json_command(*args: str, expect_success: bool = True) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expect_success and process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    if not expect_success and process.returncode == 0:
        raise AssertionError(f"{' '.join(args)} unexpectedly passed\nSTDOUT:\n{process.stdout}")
    return json.loads(process.stdout)


class TestSkillsSdkReviewPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_review_plan_receipt_is_schema_valid_for_skill_target(self) -> None:
        receipt = build_review_plan(
            REPO_ROOT,
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
            max_lenses=2,
        )

        _validate_schema_subset(self.schema, receipt, {"sdk-review-plan": self.schema})
        self.assertEqual(receipt["schema_version"], REVIEW_PLAN_SCHEMA_VERSION)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["target_kind"], "skill_source")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["receipt_written"])
        self.assertIsNone(receipt["receipt_path"])
        self.assertGreaterEqual(len(receipt["selected_lenses"]), 1)

    def test_review_plan_selection_and_next_commands_are_deterministic(self) -> None:
        first = build_review_plan(
            REPO_ROOT,
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
            prompt="Review validation confidence and evidence for simplify.",
            max_lenses=2,
        )
        second = build_review_plan(
            REPO_ROOT,
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
            prompt="Review validation confidence and evidence for simplify.",
            max_lenses=2,
        )

        self.assertEqual(
            [lens["id"] for lens in first["selected_lenses"]],
            [lens["id"] for lens in second["selected_lenses"]],
        )
        self.assertEqual(first["next_commands"], second["next_commands"])

    def test_all_known_intents_fit_public_receipt_schema(self) -> None:
        for task_intent in KNOWN_TASK_INTENTS:
            with self.subTest(task_intent=task_intent):
                receipt = build_review_plan(
                    REPO_ROOT,
                    target="Skills/agent-ops/simplify",
                    task_intent=task_intent,
                    max_lenses=1,
                )

                _validate_schema_subset(self.schema, receipt, {"sdk-review-plan": self.schema})
                self.assertEqual(receipt["task_intent"], task_intent)

    def test_cli_review_plan_emits_robot_envelope(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--json",
            "--robot",
        )
        receipt = payload["data"]["review_plan"]

        _validate_schema_subset(self.schema, receipt, {"sdk-review-plan": self.schema})
        self.assertEqual(payload["status"], "success")
        self.assertIn("sdk review plan", payload["metadata"]["command"])
        self.assertIn("--target Skills/agent-ops/simplify", payload["metadata"]["command"])
        self.assertIn("review_plan", payload["data"])
        self.assertEqual(receipt["target"], "Skills/agent-ops/simplify")
        self.assertFalse(receipt["mutation_performed"])

    def test_repo_file_signals_are_propagated_to_lens_selection(self) -> None:
        captured: dict[str, list[str]] = {}

        def fake_select_lenses(*_args: object, **kwargs: object) -> dict[str, object]:
            captured["repo_files"] = list(kwargs["repo_files"])  # type: ignore[arg-type]
            return {
                "status": "pass",
                "task_intent": "validation_review",
                "selected_lenses": [
                    {
                        "id": "lens.testing-confidence",
                        "path": "Infrastructure/references/lenses/lenses/testing-confidence.md",
                        "score": 1,
                        "reasons": ["task_intent:validation_review"],
                    }
                ],
            }

        with mock.patch("ask.skills_sdk.review_plan.select_lenses", side_effect=fake_select_lenses):
            build_review_plan(
                REPO_ROOT,
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
                repo_files=["Infrastructure/tests/test_skills_sdk_review_plan.py", "artifacts/recommended-skills-sdk-pipeline.html"],
            )

        self.assertEqual(
            captured["repo_files"],
            [
                "Skills/agent-ops/simplify",
                "Infrastructure/tests/test_skills_sdk_review_plan.py",
                "artifacts/recommended-skills-sdk-pipeline.html",
            ],
        )

    def test_review_plan_builder_uses_local_inputs_only(self) -> None:
        with (
            mock.patch("socket.create_connection", side_effect=AssertionError("network call attempted")),
            mock.patch("subprocess.run", side_effect=AssertionError("subprocess call attempted")),
        ):
            receipt = build_review_plan(
                REPO_ROOT,
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
                max_lenses=1,
            )

        self.assertEqual(receipt["status"], "pass")

    def test_receipt_out_writes_only_when_explicit(self) -> None:
        receipt_path = REPO_ROOT / ".harness/artifacts/sdk-review-plan/test-review-plan.json"
        if receipt_path.exists():
            receipt_path.unlink()
        try:
            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "review",
                "plan",
                "--target",
                "Skills/agent-ops/simplify",
                "--intent",
                "validation_review",
                "--receipt-out",
                ".harness/artifacts/sdk-review-plan/test-review-plan.json",
                "--json",
                "--robot",
            )
            receipt = payload["data"]["review_plan"]

            self.assertTrue(receipt["receipt_written"])
            self.assertEqual(receipt["receipt_path"], ".harness/artifacts/sdk-review-plan/test-review-plan.json")
            self.assertTrue(receipt_path.exists())
            written = json.loads(receipt_path.read_text(encoding="utf-8"))
            _validate_schema_subset(self.schema, written, {"sdk-review-plan": self.schema})
        finally:
            if receipt_path.exists():
                receipt_path.unlink()

    def test_handle_like_target_is_classified_without_file_claim(self) -> None:
        receipt = build_review_plan(
            REPO_ROOT,
            target="simplify",
            task_intent="validation_review",
            max_lenses=1,
        )

        self.assertEqual(receipt["target_kind"], "unresolved_handle")
        self.assertIn("target_not_resolved_to_repo_path", receipt["risk_flags"])

    def test_typoed_repo_relative_path_fails_instead_of_becoming_handle(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            "Skills/agent-ops/simplifie",
            "--intent",
            "validation_review",
            "--json",
            "--robot",
            expect_success=False,
        )

        self.assertEqual(payload["status"], "error")
        self.assertIn("target path does not exist", payload["errors"][0]["message"])

    def test_invalid_max_lenses_fails(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--max-lenses",
            "0",
            "--json",
            "--robot",
            expect_success=False,
        )

        self.assertEqual(payload["status"], "error")
        self.assertIn("max_lenses must be at least 1", payload["errors"][0]["message"])

    def test_unsafe_receipt_out_fails_without_write(self) -> None:
        outside_path = REPO_ROOT.parent / "unsafe-review-plan.json"
        if outside_path.exists():
            outside_path.unlink()
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--receipt-out",
            "../unsafe-review-plan.json",
            "--json",
            "--robot",
            expect_success=False,
        )

        self.assertEqual(payload["status"], "error")
        self.assertIn("receipt_out must resolve inside the repository root", payload["errors"][0]["message"])
        self.assertFalse(outside_path.exists())

    def test_catalog_failure_returns_robot_error_without_receipt_write(self) -> None:
        args = SimpleNamespace(
            review_action="plan",
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
            prompt=None,
            repo_file=[],
            max_lenses=1,
            receipt_out=None,
        )

        with mock.patch(
            "ask.skills_sdk.review_plan.select_lenses",
            side_effect=LensCatalogError("forced catalog failure"),
        ):
            result = _dispatch_sdk_review(REPO_ROOT, args)

        self.assertEqual(result.status, "error")
        self.assertNotIn("review_plan", result.data)
        self.assertIn("forced catalog failure", result.errors[0].message)

    def test_command_metadata_registers_review_route(self) -> None:
        self.assertIn("review", VALID_ACTIONS["sdk"])
        self.assertIn(
            "ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --json --robot",
            COMMAND_EXAMPLES[("sdk", "review")],
        )


if __name__ == "__main__":
    unittest.main()
