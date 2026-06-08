import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.command_metadata import COMMAND_EXAMPLES  # noqa: E402
from ask.skills_sdk.review_handoff import build_review_handoff  # noqa: E402
from ask.skills_sdk.review_plan import TRACE_DIR, canonical_receipt_digest  # noqa: E402


HANDOFF_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-handoff-receipt.v1.schema.json"


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


class TestSkillsSdkReviewHandoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(HANDOFF_SCHEMA_PATH.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.plan_path = REPO_ROOT / ".harness/artifacts/sdk-review-plan/test-handoff-plan.json"
        self.handoff_path = REPO_ROOT / ".harness/artifacts/sdk-review-handoff/test-handoff.json"
        self._cleanup_paths()

    def tearDown(self) -> None:
        self._cleanup_paths()

    def _cleanup_paths(self) -> None:
        for path in (self.plan_path, self.handoff_path):
            if path.exists():
                path.unlink()
        trace_dir = REPO_ROOT / TRACE_DIR
        if trace_dir.exists():
            for trace_path in trace_dir.glob("*.trace.json"):
                trace_path.unlink()

    def _write_plan(self, *, target: str = "Skills/agent-ops/simplify", intent: str = "validation_review") -> dict:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "plan",
            "--target",
            target,
            "--intent",
            intent,
            "--receipt-out",
            ".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            "--json",
            "--robot",
        )
        return payload["data"]["review_plan"]

    def test_handoff_receipt_is_schema_valid_and_does_not_claim_review_completion(self) -> None:
        plan = self._write_plan()

        receipt = build_review_handoff(
            REPO_ROOT,
            plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
        )

        _validate_schema_subset(
            self.schema,
            receipt,
            {
                "sdk-review-handoff": self.schema,
                "sdk-review-plan-receipt.v1.schema.json": json.loads(
                    (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json").read_text(
                        encoding="utf-8"
                    )
                ),
            },
        )
        self.assertEqual(receipt["source_review_plan"]["receipt_sha256"], canonical_receipt_digest(plan))
        self.assertEqual(receipt["target_kind"], "skill_source")
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["receipt_written"])
        self.assertIn("reviewers_completed", receipt["not_proven"])
        self.assertIn("ci_passed", receipt["not_proven"])

    def test_cli_handoff_emits_robot_envelope_and_writes_only_when_requested(self) -> None:
        self._write_plan()

        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "review",
            "handoff",
            "--plan",
            ".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            "--target",
            "Skills/agent-ops/simplify",
            "--intent",
            "validation_review",
            "--receipt-out",
            ".harness/artifacts/sdk-review-handoff/test-handoff.json",
            "--json",
            "--robot",
        )

        receipt = payload["data"]["review_handoff"]
        _validate_schema_subset(
            self.schema,
            receipt,
            {
                "sdk-review-handoff": self.schema,
                "sdk-review-plan-receipt.v1.schema.json": json.loads(
                    (REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json").read_text(
                        encoding="utf-8"
                    )
                ),
            },
        )
        self.assertTrue(receipt["receipt_written"])
        self.assertEqual(receipt["receipt_path"], ".harness/artifacts/sdk-review-handoff/test-handoff.json")
        self.assertTrue(self.handoff_path.exists())

    def test_handoff_refuses_missing_trace_sidecar(self) -> None:
        self._write_plan()
        for trace_path in (REPO_ROOT / TRACE_DIR).glob("*.trace.json"):
            trace_path.unlink()

        with self.assertRaisesRegex(ValueError, "required JSON file does not exist"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
            )

    def test_handoff_refuses_unwritten_review_plan_receipt(self) -> None:
        from ask.skills_sdk.review_plan import build_review_plan

        plan = build_review_plan(
            REPO_ROOT,
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
        )
        self.plan_path.parent.mkdir(parents=True, exist_ok=True)
        self.plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "must be written with --receipt-out"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
            )

    def test_handoff_accepts_diagnostic_branch_label_drift_on_same_head(self) -> None:
        plan = self._write_plan()
        plan["source_context"]["branch"] = "diagnostic-renamed-branch"
        self.plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt_sha256 = canonical_receipt_digest(plan)
        for old_trace in (REPO_ROOT / TRACE_DIR).glob("*.trace.json"):
            old_trace.unlink()
        trace_path = REPO_ROOT / TRACE_DIR / f"{receipt_sha256}.trace.json"
        trace = {
            "schema_version": "skills-sdk.review-plan-trace.v1",
            "schema_uri": "https://jscraik.local/agent-skills/schemas/skills-sdk/sdk-review-plan-trace.v1.schema.json",
            "receipt_path": ".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            "receipt_instance_id": plan["source_context"]["receipt_instance_id"],
            "receipt_sha256": receipt_sha256,
            "repo_root": plan["source_context"]["repo_root"],
            "head_sha": plan["source_context"]["head_sha"],
            "branch": plan["source_context"]["branch"],
            "branch_policy": plan["source_context"]["branch_policy"],
            "target_input": plan["source_context"]["target_input"],
            "target_identity": plan["source_context"]["target_identity"],
            "target_resolved_path": plan["source_context"]["target_resolved_path"],
            "target_content_digest": plan["source_context"]["target_content_digest"],
            "target_digest_status": plan["source_context"]["target_digest_status"],
            "created_by_command": "./bin/ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --receipt-out .harness/artifacts/sdk-review-plan/test-handoff-plan.json --json --robot",
        }
        trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        receipt = build_review_handoff(
            REPO_ROOT,
            plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            target="Skills/agent-ops/simplify",
            task_intent="validation_review",
        )

        self.assertEqual(receipt["status"], "pass")

    def test_handoff_accepts_equivalent_target_path_spelling_when_identity_matches(self) -> None:
        plan = self._write_plan(target="Skills/agent-ops/simplify")

        receipt = build_review_handoff(
            REPO_ROOT,
            plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
            target="./Skills/agent-ops/simplify",
            task_intent="validation_review",
        )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["target"], "./Skills/agent-ops/simplify")
        self.assertEqual(receipt["source_context"]["target_input"], plan["source_context"]["target_input"])
        self.assertEqual(receipt["source_context"]["target_identity"], plan["source_context"]["target_identity"])

    def test_handoff_refuses_edited_receipt_digest(self) -> None:
        plan = self._write_plan()
        plan["prompt"] = "tampered"
        self.plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "required JSON file does not exist"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
            )

    def test_handoff_refuses_copied_receipt_path_mismatch(self) -> None:
        self._write_plan()
        copy_path = REPO_ROOT / ".harness/artifacts/sdk-review-plan/copied-plan.json"
        try:
            shutil.copyfile(self.plan_path, copy_path)

            with self.assertRaisesRegex(ValueError, "receipt_path does not match"):
                build_review_handoff(
                    REPO_ROOT,
                    plan_path=".harness/artifacts/sdk-review-plan/copied-plan.json",
                    target="Skills/agent-ops/simplify",
                    task_intent="validation_review",
                )
        finally:
            if copy_path.exists():
                copy_path.unlink()

    def test_handoff_refuses_target_and_intent_mismatch(self) -> None:
        self._write_plan()

        with self.assertRaisesRegex(ValueError, "source_context target_.* is stale or mismatched"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Infrastructure/tests/test_skills_sdk_review_plan.py",
                task_intent="validation_review",
            )
        with self.assertRaisesRegex(ValueError, "intent must match"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Skills/agent-ops/simplify",
                task_intent="architecture_review",
            )

    def test_handoff_refuses_unresolved_handle_plan(self) -> None:
        self._write_plan(target="simplify")

        with self.assertRaisesRegex(ValueError, "unresolved handles fail closed"):
            build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="simplify",
                task_intent="validation_review",
            )

    def test_handoff_rejects_symlink_output_escape(self) -> None:
        self._write_plan()
        escape_dir = REPO_ROOT / ".harness/artifacts/sdk-review-handoff/escape"
        outside_dir = REPO_ROOT.parent / "handoff-outside"
        if escape_dir.exists() or escape_dir.is_symlink():
            escape_dir.unlink()
        outside_dir.mkdir(exist_ok=True)
        escape_dir.symlink_to(outside_dir, target_is_directory=True)
        try:
            with self.assertRaisesRegex(ValueError, "receipt_out must resolve inside the repository root"):
                build_review_handoff(
                    REPO_ROOT,
                    plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                    target="Skills/agent-ops/simplify",
                    task_intent="validation_review",
                    receipt_out=".harness/artifacts/sdk-review-handoff/escape/out.json",
                )
        finally:
            if escape_dir.exists() or escape_dir.is_symlink():
                escape_dir.unlink()
            outside_output = outside_dir / "out.json"
            if outside_output.exists():
                outside_output.unlink()
            outside_dir.rmdir()

    def test_handoff_builder_uses_local_inputs_only(self) -> None:
        self._write_plan()
        with (
            mock.patch("socket.create_connection", side_effect=AssertionError("network call attempted")),
            mock.patch("subprocess.run", side_effect=AssertionError("subprocess call attempted")),
        ):
            receipt = build_review_handoff(
                REPO_ROOT,
                plan_path=".harness/artifacts/sdk-review-plan/test-handoff-plan.json",
                target="Skills/agent-ops/simplify",
                task_intent="validation_review",
            )

        self.assertEqual(receipt["status"], "pass")

    def test_command_metadata_registers_handoff_route(self) -> None:
        self.assertIn(
            "ask sdk review handoff --plan .harness/artifacts/sdk-review-plan/simplify.json --target Skills/agent-ops/simplify --intent validation_review --json --robot",
            COMMAND_EXAMPLES[("sdk", "review")],
        )


if __name__ == "__main__":
    unittest.main()
