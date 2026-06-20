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

from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from ask.skills_sdk.capability_status import (  # noqa: E402
    ALLOWED_STATUSES,
    MUTATING_CAPABILITY_IDS,
    REQUIRED_CAPABILITY_IDS,
    CapabilityStatusError,
    build_capability_status,
    load_capability_matrix,
    validate_capability_matrix,
)


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json"
MATRIX_PATH = REPO_ROOT / "Infrastructure/config/skills-sdk/capability-matrix.v1.json"


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


class TestSkillsSdkCapabilityStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_matrix_contains_every_required_capability_once(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        capability_ids = [row["id"] for row in matrix["capabilities"]]

        self.assertEqual(capability_ids, list(REQUIRED_CAPABILITY_IDS))
        self.assertEqual(len(capability_ids), len(set(capability_ids)))

    def test_status_payload_is_schema_valid(self) -> None:
        payload = build_capability_status(REPO_ROOT)

        _validate_schema_subset(self.schema, payload, {"capability-status": self.schema})
        self.assertEqual(payload["summary"]["total"], len(REQUIRED_CAPABILITY_IDS))
        self.assertEqual(payload["summary"]["mutation_performed_count"], len(MUTATING_CAPABILITY_IDS))
        self.assertEqual(set(payload["summary"]["by_status"]), ALLOWED_STATUSES)

    def test_matrix_rejects_implemented_without_execution(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        bad_matrix["capabilities"][0]["feature_executed"] = False

        with self.assertRaisesRegex(CapabilityStatusError, "cannot be implemented"):
            validate_capability_matrix(bad_matrix)

    def test_matrix_allows_only_approved_mutating_capabilities(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        mutating_ids = {
            row["id"]
            for row in matrix["capabilities"]
            if row["mutation_performed"]
        }

        self.assertEqual(mutating_ids, MUTATING_CAPABILITY_IDS)

    def test_lenses_review_plan_handoff_and_determinism_are_read_only_advisory_capabilities(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        by_id = {row["id"]: row for row in matrix["capabilities"]}

        for capability_id in ("sdk_lenses", "review_plan", "review_handoff", "review_verification", "determinism_audit"):
            with self.subTest(capability=capability_id):
                capability = by_id[capability_id]
                self.assertEqual(capability["status"], "implemented")
                self.assertTrue(capability["feature_executed"])
                self.assertFalse(capability["mutation_performed"])
                self.assertTrue(any("./bin/ask sdk" in ref for ref in capability["evidence_refs"]))

    def test_matrix_rejects_preview_mutation_claims(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        install_preview = next(row for row in bad_matrix["capabilities"] if row["id"] == "install_preview")
        install_preview["mutation_performed"] = True

        with self.assertRaisesRegex(CapabilityStatusError, "cannot report mutation_performed"):
            validate_capability_matrix(bad_matrix)

    def test_matrix_rejects_deferred_mutating_real_install(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        real_install = next(row for row in bad_matrix["capabilities"] if row["id"] == "real_install")
        real_install["status"] = "deferred"

        with self.assertRaisesRegex(CapabilityStatusError, "cannot mutate unless implemented"):
            validate_capability_matrix(bad_matrix)

    def test_matrix_rejects_unknown_status(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        bad_matrix["capabilities"][0]["status"] = "claimed_ready"

        with self.assertRaisesRegex(CapabilityStatusError, "unknown status"):
            validate_capability_matrix(bad_matrix)

    def test_matrix_rejects_malformed_top_level_status(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        bad_matrix["status"] = "success"

        with self.assertRaisesRegex(CapabilityStatusError, "status must be truth_surface"):
            validate_capability_matrix(bad_matrix)

    def test_matrix_rejects_unexpected_capability_row_fields(self) -> None:
        matrix = load_capability_matrix(REPO_ROOT)
        bad_matrix = json.loads(json.dumps(matrix))
        bad_matrix["capabilities"][0]["schema_invalid_extra"] = True

        with self.assertRaisesRegex(CapabilityStatusError, "unexpected keys"):
            validate_capability_matrix(bad_matrix)

    def test_ask_sdk_status_emits_schema_valid_payload(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "status",
            "--json",
            "--robot",
        )
        status = payload["data"]["skills_sdk_status"]

        _validate_schema_subset(self.schema, status, {"capability-status": self.schema})
        self.assertEqual(payload["status"], "success")
        self.assertEqual(status["summary"]["total"], len(REQUIRED_CAPABILITY_IDS))
        self.assertEqual(status["summary"]["mutation_performed_count"], len(MUTATING_CAPABILITY_IDS))

    def test_public_wrapper_preserves_status_contract(self) -> None:
        ask_payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "status",
            "--json",
            "--robot",
        )
        wrapper_payload = _run_json_command(
            sys.executable,
            "bin/skills-sdk",
            "status",
            "--json",
            "--robot",
        )

        self.assertEqual(wrapper_payload["data"]["skills_sdk_status"], ask_payload["data"]["skills_sdk_status"])
        self.assertEqual(wrapper_payload["metadata"]["command"], "sdk status --json --robot")

    def test_command_metadata_registers_sdk_lifecycle_routes(self) -> None:
        expected_actions = {
            "rollback",
            "uninstall",
            "ir",
            "docs",
            "eval",
            "package",
            "sandbox",
            "trust",
            "observability",
            "emitter",
            "ci",
            "explorer",
            "status",
            "project",
        }

        self.assertTrue(expected_actions.issubset(set(VALID_ACTIONS["sdk"])))

    def test_command_metadata_registers_sdk_lifecycle_examples(self) -> None:
        self.assertIn("ask sdk ir build Skills/agent-ops/autofix --json --robot", COMMAND_EXAMPLES[("sdk", "ir")])
        self.assertIn("ask sdk docs verify --json --robot", COMMAND_EXAMPLES[("sdk", "docs")])
        self.assertIn(
            "ask sdk eval run Skills/agent-ops/testing --runner internal --mode smoke --json --robot",
            COMMAND_EXAMPLES[("sdk", "eval")],
        )
        self.assertIn("ask sdk package build Skills/agent-ops/autofix --json --robot", COMMAND_EXAMPLES[("sdk", "package")])
        self.assertIn(
            "ask sdk sandbox validate --profile Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/sandbox-profile.json --json --robot",
            COMMAND_EXAMPLES[("sdk", "sandbox")],
        )
        self.assertIn(
            "ask sdk observability feedback --skill Infrastructure/tests/fixtures/skills_sdk/valid_skill --events Infrastructure/tests/fixtures/skills_sdk/observability/redacted-events.fixture --preview --json --robot",
            COMMAND_EXAMPLES[("sdk", "observability")],
        )
        self.assertIn(
            "ask sdk emitter preview --skill Infrastructure/tests/fixtures/skills_sdk/valid_skill --preview --json --robot",
            COMMAND_EXAMPLES[("sdk", "emitter")],
        )
        self.assertIn(
            "ask sdk ci policy --risk-tier high --preview --json --robot",
            COMMAND_EXAMPLES[("sdk", "ci")],
        )
        self.assertIn(
            "ask sdk explorer static --preview --json --robot",
            COMMAND_EXAMPLES[("sdk", "explorer")],
        )
        self.assertIn(
            "ask sdk trust decide Infrastructure/tests/fixtures/skills_sdk/valid_skill --decision trust --reason 'fixture passed local checks' --owner skills-sdk-tests --preview --json --robot",
            COMMAND_EXAMPLES[("sdk", "trust")],
        )
        self.assertTrue(any(command.startswith("ask sdk rollback ") for command in COMMAND_EXAMPLES[("sdk", "rollback")]))
        self.assertTrue(any(command.startswith("ask sdk uninstall ") for command in COMMAND_EXAMPLES[("sdk", "uninstall")]))
        self.assertIn("ask sdk status --json --robot", COMMAND_EXAMPLES[("sdk", "status")])
        self.assertIn("skills-sdk status --json --robot", COMMAND_EXAMPLES[("sdk", "status")])
        self.assertIn(
            "ask sdk project status --project-root /tmp/sample-project --json --robot",
            COMMAND_EXAMPLES[("sdk", "project")],
        )

    def test_status_robot_guidance_stays_registered(self) -> None:
        """
        Verifies that invoking `ask sdk status` with an unrecognized argument returns an error and preserves the robot guidance metadata.
        
        Asserts that the process exits with a non-zero code, the JSON payload has `"status" == "error"`, the first error message mentions the unrecognized argument, the reported `metadata.command` reflects the original invocation, and `data["candidate_commands"]` includes the suggested `ask sdk status --json --robot` command.
        """
        process = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "status",
                "bogus",
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

        self.assertNotEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("unrecognized arguments: bogus", payload["errors"][0]["message"])
        self.assertEqual(payload["metadata"]["command"], "sdk status bogus --json --robot")
        self.assertIn("ask sdk status --json --robot", payload["data"]["candidate_commands"])

    def test_help_surfaces_expose_status_route(self) -> None:
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
                self.assertIn("status", process.stdout)

    def test_matrix_file_is_deterministic_json(self) -> None:
        loaded = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))

        self.assertEqual(loaded, load_capability_matrix(REPO_ROOT))

    def test_v1_spec_and_plan_encode_closeout_status(self) -> None:
        spec_text = (REPO_ROOT / ".harness/specs/2026-06-03-skills-sdk-v1-product-spec.md").read_text(encoding="utf-8")
        plan_text = (REPO_ROOT / ".harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md").read_text(encoding="utf-8")

        self.assertIn("## Appendix D. V1.0 Implementation Status", spec_text)
        self.assertIn("Infrastructure/config/skills-sdk/capability-matrix.v1.json", spec_text)
        self.assertIn("registry, marketplace, publish", spec_text)
        self.assertIn("## Appendix D. V1.0 Final Closeout Status", plan_text)
        self.assertIn("PU-001 through PU-007 are completed historical implementation slices", plan_text)
        self.assertIn("PR, CI, review-thread, tracker, merge readiness", plan_text)



if __name__ == "__main__":
    unittest.main()
