import unittest
import subprocess
import json
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts" / "lib"))

from ask.cli_errors import build_helpful_error, build_unknown_action_result
from ask.command_metadata import VALID_ACTIONS

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(cmd: list[str], **kwargs):
    kwargs.setdefault("cwd", REPO_ROOT)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, **kwargs)


def _assert_readiness_overview_ready(
    testcase: unittest.TestCase,
    overview: dict,
    expected_sections: list[str],
) -> None:
    testcase.assertEqual(overview["contract_status"], "ready")
    testcase.assertTrue(overview["contract_ready"])
    testcase.assertEqual(overview["contract_gap_count"], 0)
    testcase.assertFalse(overview["has_contract_gaps"])
    testcase.assertEqual(overview["contract_section_count"], len(expected_sections))
    testcase.assertEqual(
        overview["contract_status_by_section"],
        {section: "ready" for section in expected_sections},
    )
    testcase.assertEqual(
        overview["contract_gap_count_by_section"],
        {section: 0 for section in expected_sections},
    )
    testcase.assertEqual(overview["ready_contract_sections"], expected_sections)
    testcase.assertEqual(overview["blocked_contract_sections"], [])


def _assert_contract_ready(testcase: unittest.TestCase, payload: dict) -> None:
    testcase.assertEqual(payload["contract_gap_count"], 0)
    testcase.assertFalse(payload["has_contract_gaps"])
    testcase.assertEqual(payload["contract_status"], "ready")
    testcase.assertTrue(payload["contract_ready"])


def _write_pass_closeout(tmp: str) -> Path:
    case_dir = Path(tmp) / "01-edge-case"
    case_dir.mkdir()
    (case_dir / "result.json").write_text('{"id":"edge-case","status":"pass"}\n', encoding="utf-8")
    closeout_path = Path(tmp) / "workflow-closeout.json"
    closeout_path.write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.eval-closeout.v1",
                "status": "pass",
                "skill_path": "Skills/example-skill",
                "mode": "smoke",
                "runner": "codex",
                "blocker_class": None,
                "report_dir": str(Path(tmp)),
                "cases": [{"id": "edge-case", "status": "pass", "result_path": str(case_dir)}],
                "mutation_allowed": False,
                "registry_update_allowed": False,
                "next_reproduce_command": "./bin/ask evals run Skills/example-skill --mode smoke --json --robot",
            }
        ),
        encoding="utf-8",
    )
    return closeout_path


class TestAskCLI(unittest.TestCase):
    def test_json_envelope_format(self):
        """CA1: Verify ask --json returns a valid CallResult envelope."""
        # Using -p to pass a dummy command if needed, or just root --json
        cmd = [sys.executable, "Infrastructure/bin/ask", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"CLI failed with stderr: {result.stderr}")

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("CLI output was not valid JSON")

        # Verify mandatory envelope fields
        self.assertIn("status", output)
        self.assertIn("trace_id", output)
        self.assertIn("metadata", output)
        self.assertEqual(output["status"], "success")
        self.assertIn("version", output["metadata"])

    def test_repo_status_discovery(self):
        """CA1: Verify ask repo status correctly identifies the repo root."""
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("repo_root", output["data"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask repo status --json --robot"],
        )
        # Verify it found the actual current directory or a parent
        # Handle redacted paths by substituting back the home directory
        repo_root = output["data"]["repo_root"]
        if "<USER_HOME>" in repo_root:
            repo_root = repo_root.replace("<USER_HOME>", os.path.expanduser("~"))
        self.assertTrue(os.path.isdir(repo_root), f"repo_root is not a directory: {repo_root}")

    def test_repo_status_human_output_exposes_validation(self):
        """Verify repo status human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Success:", result.stdout)
        self.assertIn("Validation: ./bin/ask repo status --json --robot", result.stdout)

    def test_repo_yaml_inspect_cli_uses_managed_pyyaml(self):
        """Verify YAML inspection works through ask instead of bare system python."""
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp_dir:
            yaml_path = Path(tmp_dir) / "fixture.yaml"
            yaml_path.write_text("cases:\n  - id: package-fixture\n", encoding="utf-8")
            cmd = [
                "python3",
                "Infrastructure/bin/ask",
                "repo",
                "yaml-inspect",
                str(yaml_path.relative_to(REPO_ROOT)),
                "--query",
                "cases.0.id",
                "--json",
                "--robot",
            ]
            result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"yaml-inspect output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["yaml"]["query_value"], "package-fixture")
        self.assertTrue(output["data"]["python_command"].endswith(" -"))
        self.assertNotIn("mise exec", output["data"]["python_command"])
        self.assertNotIn("mise", output["data"]["python_command"])

    def test_repo_yaml_inspect_serializes_yaml_dates(self):
        """Verify YAML inspection emits JSON-safe values for YAML scalar types."""
        repo_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmp_dir:
            yaml_path = Path(tmp_dir) / "dates.yaml"
            yaml_path.write_text("released_on: 2026-06-16\n", encoding="utf-8")
            relative_path = yaml_path.relative_to(repo_root)
            cmd = [
                "python3",
                "Infrastructure/bin/ask",
                "repo",
                "yaml-inspect",
                str(relative_path),
                "--query",
                "released_on",
                "--json",
                "--robot",
            ]

            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])

        self.assertEqual(result.returncode, 0, f"yaml-inspect output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["yaml"]["query_type"], "date")
        self.assertEqual(output["data"]["yaml"]["query_value"], "2026-06-16")

    def test_repo_yaml_inspect_human_output_renders_result(self):
        """Verify YAML inspection has a visible non-JSON success output."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "repo",
            "yaml-inspect",
            "Skills/agent-ops/improve-agent-native/references/evals.yaml",
            "--query",
            "cases.0.id",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"yaml-inspect output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("YAML inspect: Skills/agent-ops/improve-agent-native/references/evals.yaml", result.stdout)
        self.assertIn("query=cases.0.id", result.stdout)
        self.assertIn("value='smoke-discovery-target'", result.stdout)

    def test_repo_yaml_inspect_human_output_renders_summary_without_query(self):
        """Verify root YAML inspection renders summary metadata without a query."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "repo",
            "yaml-inspect",
            "Skills/agent-ops/improve-agent-native/references/evals.yaml",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"yaml-inspect output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("root_type=dict", result.stdout)
        self.assertIn("top_level_keys=", result.stdout)
        self.assertNotIn("item_count=None", result.stdout)

    def test_repo_missing_action_exposes_validation(self):
        """Verify incomplete repo commands expose the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"repo output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask repo status --json --robot"])

    def test_repo_missing_action_human_output_exposes_validation(self):
        """Verify incomplete repo commands render the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"repo output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'repo'", result.stdout)
        self.assertIn("Validation: ./bin/ask repo status --json --robot", result.stdout)

    def test_skills_list(self):
        """
        Validate that `ask skills list --json` returns a skills catalogue with required envelope, mode settings, and skill fields.
        
        Checks:
        - Exit code 0 and `status` equals "success".
        - `data.skills` is present as a list.
        - `advanced_mode` is true and `inventory_mode` equals "repo".
        - `validation_commands` contains the expected replay command.
        - If non-empty, first skill contains `name` and `path`.
        """
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("skills", output["data"])
        self.assertIsInstance(output["data"]["skills"], list)
        self.assertTrue(output["data"].get("advanced_mode"))
        self.assertEqual(output["data"].get("inventory_mode"), "repo")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills list --json --robot"],
        )
        if len(output["data"]["skills"]) > 0:
            skill = output["data"]["skills"][0]
            self.assertIn("name", skill)
            self.assertIn("path", skill)

    def test_skills_list_human_output_exposes_validation(self):
        """
        Verify that the human-readable skills list output includes discovery confirmation and a validation replay command.
        """
        cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / "bin" / "ask"), "skills", "list", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Discovered", result.stdout)
        self.assertIn("Validation: ./bin/ask skills list --json --robot", result.stdout)

    def test_skills_list_advanced_flag(self):
        """CA1: Verify ask skills list --advanced remains a full-inventory compatibility alias."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--advanced", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))
        self.assertEqual(output["data"].get("inventory_mode"), "repo")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills list --advanced --json --robot"],
        )

    def test_skills_list_visible_only_flag(self):
        """Verify ask skills list --visible-only exposes the narrower visible inventory."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--visible-only", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertFalse(output["data"].get("advanced_mode"))
        self.assertEqual(output["data"].get("inventory_mode"), "visible")
        self.assertTrue(output["data"].get("visible_only"))
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills list --visible-only --json --robot"],
        )

    def test_skills_list_visible_only_wins_over_advanced_alias(self):
        """Verify mixed compatibility flags report one coherent visible inventory."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "list",
            "--advanced",
            "--visible-only",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertFalse(output["data"].get("advanced_mode"))
        self.assertEqual(output["data"].get("inventory_mode"), "visible")
        self.assertTrue(output["data"].get("visible_only"))
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills list --visible-only --json --robot"],
        )

    def test_skills_budget_json_contract(self):
        """Verify ask skills budget exposes the runtime-budget validation command."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "budget", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        budget = output["data"]["runtime_budget"]
        self.assertEqual(budget["status"], "pass")
        self.assertEqual(
            budget["validation_commands"],
            ["./bin/ask skills budget --json --robot"],
        )

    def test_skills_budget_human_output_exposes_validation(self):
        """Verify ask skills budget renders its validation command."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "budget", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Runtime budget:", result.stdout)
        self.assertIn("Validation: ./bin/ask skills budget --json --robot", result.stdout)

    def test_skills_route_json_contract(self):
        """CA1: Verify ask skills route exposes selection-decision fields."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "route", "create-auth", "--json"]
        result = _run_cli(cmd)

        # Route may exit non-zero for unresolved ambiguity/no-candidate, but should emit envelope JSON.
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("data", output)
        self.assertIn("decision", output["data"])
        decision = output["data"]["decision"]
        self.assertIn("decision_status", decision)
        self.assertIn("policy_identity", decision)
        self.assertIn("considered_limit", decision)
        self.assertIn("selected_candidates", decision)
        self.assertEqual(
            decision.get("validation_commands"),
            ["./bin/ask skills route create-auth --json --robot"],
        )

    def test_skills_route_human_output_exposes_validation(self):
        """Verify ambiguous route output renders the route validation command."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "route",
            "help me",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("🧭 Route decision:", result.stdout)
        self.assertIn("Validation: ./bin/ask skills route", result.stdout)
        self.assertIn("--json --robot", result.stdout)

    def test_skills_list_json_contract(self):
        """Verify ask skills list exposes the SDK target inventory contract."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "list", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        skills = output["data"]["skills"]
        self.assertGreater(len(skills), 0)
        self.assertIn("name", skills[0])
        self.assertIn("path", skills[0])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills list --json --robot"],
        )

    def test_skills_list_human_output_includes_inventory_entries(self):
        """Verify ask skills list renders inventory entries."""
        cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / "bin" / "ask"), "skills", "list", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Discovered", result.stdout)
        self.assertIn("autofix", result.stdout)

    def test_skills_removed_projection_flags_fail_closed(self):
        """Verify removed projection flags direct callers to current skill sync/list surfaces."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "handles",
            "--write-projection",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_INVALID_PROJECTION_MODE")
        self.assertIn("skills sync --scope workspace --projection flat", output["errors"][0]["fix_suggestion"])
        self.assertIn("skills list --json --robot", output["errors"][0]["fix_suggestion"])

    def test_skills_resolve_json_contract(self):
        """Verify ask skills resolve returns the canonical source for a source-path target."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "resolve", "Skills/agent-ops/autofix", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["handle"], "autofix")
        self.assertEqual(resolution["source_path"], "Skills/agent-ops/autofix/SKILL.md")
        self.assertEqual(resolution["requested_handle"], "Skills/agent-ops/autofix")
        self.assertEqual(resolution["alias_resolution"], "autofix")
        self.assertEqual(
            resolution["validation_commands"],
            ["./bin/ask skills resolve autofix --json --robot"],
        )

    def test_skills_resolve_human_output_exposes_validation(self):
        """Verify ask skills resolve renders its validation command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "resolve", "Skills/agent-ops/autofix", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill target: autofix", result.stdout)
        self.assertIn("Validation: ./bin/ask skills resolve autofix --json --robot", result.stdout)

    def test_skills_parse_json_contract(self):
        """Verify ask skills parse reports resolved mentions and its validation command."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "parse",
            "use $simplify and $autofix",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        parsed = output["data"]["parse"]
        self.assertEqual(parsed["status"], "pass")
        self.assertEqual(parsed["mention_counts"]["skills"], 2)
        self.assertEqual(
            parsed["validation_commands"],
            ["./bin/ask skills parse 'use $simplify and $autofix' --json --robot"],
        )

    def test_skills_parse_human_output_exposes_validation(self):
        """Verify ask skills parse renders its validation command."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "parse",
            "use $simplify and $autofix",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Parse succeeded: pass", result.stdout)
        self.assertIn("Skill mentions: 2", result.stdout)
        self.assertIn("Validation: ./bin/ask skills parse", result.stdout)
        self.assertIn("--json --robot", result.stdout)

    def test_skills_proof_json_contract(self):
        """Verify ask skills proof separates resolver, canonical source, and runtime-link gates."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "Skills/agent-ops/autofix", "--json"]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        proof = output["data"]["proof"]
        self.assertEqual(proof["schema_version"], "sdk-skill-proof.v1")
        self.assertEqual(proof["handle"], "autofix")
        self.assertIn("resolver", proof["gates"])
        self.assertIn("canonical_source_exists", proof["gates"])
        self.assertIn("codex_user_link", proof["gates"])
        self.assertIn("user_runtime_ready", proof["gates"])
        self.assertIn("user_runtime_ready", proof["gate_policy"]["required"])
        self.assertIn("either supported user runtime link", proof["gate_policy"]["required_semantics"])
        self.assertIn("codex_user_link", proof["gate_policy"]["supporting_runtime_diagnostics"])
        self.assertIn("agents_user_link", proof["gate_policy"]["supporting_runtime_diagnostics"])
        self.assertEqual(
            proof["validation_commands"],
            ["./bin/ask skills proof autofix --json --robot"],
        )
        if proof.get("status") == "pass":
            self.assertEqual(proof["live_runtime_invocation"]["status"], "manual_session_gate")
        else:
            self.assertNotIn("live_runtime_invocation", proof)

    def test_skills_proof_human_output(self):
        """Verify ask skills proof has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "Skills/agent-ops/autofix"]
        result = _run_cli(cmd)

        if result.returncode == 0:
            self.assertIn("Skill target proof: autofix", result.stdout)
            self.assertIn(
                "required gates: resolver, canonical_source_exists, direct_runtime_projection, user_runtime_ready",
                result.stdout,
            )
            self.assertIn("Validation: ./bin/ask skills proof autofix --json --robot", result.stdout)
            if "runtime satisfied by:" in result.stdout:
                self.assertRegex(result.stdout, r"runtime satisfied by: (codex_user_runtime|agents_user_runtime)")
            if "live invocation:" in result.stdout:
                self.assertIn("live invocation: manual_session_gate", result.stdout)
        elif result.returncode == 2:
            self.assertRegex(result.stdout, r"SDK skill proof failed for 'autofix'")
        else:
            self.fail(f"Unexpected return code {result.returncode}, stderr: {result.stderr}")

    def test_skills_prove_json_contract(self):
        """Verify ask skills prove keeps its three user-facing truths compact."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "Skills/agent-ops/autofix", "--json"]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        self.assertLess(len(result.stdout.encode("utf-8")), 10 * 1024)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["handle"], "autofix")
        self.assertIn("runtime_reachability", skill_proof)
        self.assertIn("structural_quality", skill_proof)
        self.assertIn("outcome_proof", skill_proof)
        self.assertIn("claims_boundary", skill_proof)
        self.assertNotIn("sdk_skill_proof", output["data"])

    def test_skills_prove_reachability_blocker_names_a_non_repeating_preview(self):
        """Verify a blocked proof points to the prerequisite instead of itself."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "simplify", "--json", "--robot"]
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["HOME"] = temp_dir
            result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["proof_status"], "blocked_reachability")
        self.assertEqual(
            skill_proof["next_command"],
            "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
        )

    def test_skills_prove_human_output(self):
        """Verify ask skills prove renders the scorecard in non-JSON mode."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "Skills/agent-ops/autofix", "--robot"]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, result.stderr)
        if result.returncode == 0:
            self.assertIn("Skill proof scorecard: $autofix", result.stdout)
            self.assertRegex(result.stdout, r"reachability: (pass|fail)")
            self.assertIn("structural_quality: pass", result.stdout)
            self.assertIn("analytics: unavailable_or_legacy", result.stdout)
            self.assertIn("outcome_proof: missing", result.stdout)
            self.assertIn("Next:", result.stdout)
        else:
            self.assertIn("SDK skill proof failed for 'autofix'.", result.stdout)
            self.assertIn("skills sync --scope user --projection flat --dry-run", result.stdout)

    def test_skills_prove_maps_golden_path_taxonomy_for_current_target(self):
        """Verify prove exposes the stable proof taxonomy without adding schemas."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "Skills/agent-ops/autofix", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["handle"], "autofix")
        self.assertIn(skill_proof["runtime_reachability"]["status"], {"pass", "fail"})
        self.assertEqual(skill_proof["structural_quality"]["status"], "pass")
        self.assertEqual(skill_proof["outcome_proof"]["evidence_class"], "outcome_proof")
        self.assertIn(
            skill_proof["proof_status"],
            {"blocked_reachability", "reachable_without_outcome_proof", "pass"},
        )
        self.assertNotIn("sdk_skill_proof", output["data"])

    def test_skills_prove_keeps_compact_invocation_summary(self):
        """Verify compact prove output keeps the bounded analytics summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "skill_id": "autofix",
                            "plugin_id": "harness-engineering",
                            "turn_id_hash": "turn_123",
                            "thread_id_hash": "thread_123",
                            "invoke_type": "skill",
                            "scope": "workspace",
                            "model_slug": "gpt-5.3-codex",
                            "product_client_id_hash": "client_123",
                            "repository_hash": "repo_123",
                            "timestamp": "2026-05-07T10:00:00Z",
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )

            env = os.environ.copy()
            env["SKILL_TELEMETRY_DIR"] = telemetry_dir
            cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "autofix", "--json"]
            result = _run_cli(cmd, env=env)

        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        analytics = output["data"]["skill_proof"]["analytics"]
        self.assertEqual(analytics["status"], "available")
        self.assertEqual(analytics["matching_invocation_count"], 1)

    def test_skills_prove_reports_projection_parse_warning(self):
        """Verify ask skills prove preserves valid projection rows with parse warnings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write("{not-json\n")
                handle.write(json.dumps({"skill_id": "other-skill", "timestamp": "2026-05-07T10:00:00Z"}) + "\n")

            with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": telemetry_dir}):
                lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
                sys.path.insert(0, lib_path)
                try:
                    from ask.skill_analytics import skill_invocation_analytics

                    analytics = skill_invocation_analytics(Path.cwd(), "autofix")
                finally:
                    sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "parse_warning")
        self.assertEqual(analytics["invocation_count"], 1)
        self.assertEqual(analytics["matching_invocation_count"], 0)
        self.assertEqual(analytics["parse_error_count"], 1)

    def test_skills_prove_keeps_compact_parse_warning_summary(self):
        """Verify compact prove output preserves the parse-warning classification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            telemetry_dir = os.path.join(temp_dir, "telemetry")
            os.makedirs(telemetry_dir, exist_ok=True)
            with open(os.path.join(telemetry_dir, "skill-invocations.jsonl"), "w", encoding="utf-8") as handle:
                handle.write("{not-json\n")
                handle.write(json.dumps({"skill_id": "autofix", "timestamp": "2026-05-07T10:00:00Z"}) + "\n")

            env = os.environ.copy()
            env["SKILL_TELEMETRY_DIR"] = telemetry_dir
            cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "prove", "autofix", "--json"]
            result = _run_cli(cmd, env=env)

        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        analytics = output["data"]["skill_proof"]["analytics"]
        self.assertEqual(analytics["status"], "parse_warning")
        self.assertEqual(analytics["parse_error_count"], 1)

    def test_skill_invocation_analytics_relative_override_uses_repo_root(self):
        """Verify relative telemetry overrides are anchored to the repository root."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics

            repo_root = Path("/tmp/agent-skills-repo")
            with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": "generated/telemetry"}):
                telemetry_dir = skill_analytics.skill_telemetry_dir(repo_root)
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(telemetry_dir, repo_root / "generated" / "telemetry")

    def test_skill_invocation_analytics_handles_projection_read_errors(self):
        """Verify projection read errors return an unavailable summary."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask import skill_analytics

            with tempfile.TemporaryDirectory() as temp_dir:
                telemetry_dir = Path(temp_dir) / "telemetry"
                telemetry_dir.mkdir(parents=True)
                projection = telemetry_dir / "skill-invocations.jsonl"
                projection.write_text("", encoding="utf-8")
                original_open = Path.open

                def selective_open(path_self, *args, **kwargs):
                    if path_self == projection:
                        raise PermissionError("permission denied")
                    return original_open(path_self, *args, **kwargs)

                with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": str(telemetry_dir)}), mock.patch.object(
                    Path,
                    "open",
                    selective_open,
                ):
                    analytics = skill_analytics.skill_invocation_analytics(Path.cwd(), "autofix")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "unavailable_or_legacy")
        self.assertEqual(analytics["parse_error_count"], 1)
        self.assertIn("permission denied", analytics["parse_errors"][0]["message"])

    def test_skills_prove_goal_fallback_json_contract(self):
        """Verify ask skills prove routes or clearly blocks a goal query."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "prove",
            "fix",
            "PR",
            "review",
            "comments",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        skill_proof = output["data"]["skill_proof"]
        self.assertEqual(skill_proof["schema_version"], "skill-proof-scorecard.v1")
        self.assertEqual(skill_proof["query"], "fix PR review comments")
        self.assertIn(
            skill_proof["proof_status"],
            ("blocked_goal_resolution", "blocked_reachability", "reachable_without_outcome_proof"),
        )
        self.assertIn("goal_resolution", skill_proof)
        self.assertIn("recommended_capability", skill_proof["goal_resolution"])
        self.assertEqual(skill_proof["validation_commands"], [skill_proof["next_command"]])

    def test_skills_prove_single_token_goal_uses_improve_fallback(self):
        """Verify one-word goals use the same improvement route as phrase goals."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            failed_reachability = CallResult(status="error")
            goal_result = CallResult()
            goal_result.data["improvement"] = {
                "recommended_capability": {"handle": "security-reviewer"},
                "next_command": "./bin/ask skills proof security-reviewer --json --robot",
            }
            reachable_result = CallResult()
            reachable_result.data["proof"] = {
                "status": "pass",
                "handle": "security-reviewer",
                "resolution": {
                    "handle": "security-reviewer",
                    "source_path": "Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md",
                },
            }

            with mock.patch.object(
                skills_commands,
                "skills_proof",
                side_effect=[failed_reachability, reachable_result],
            ), mock.patch.object(
                skills_commands,
                "improve_skills",
                return_value=goal_result,
            ) as improve_mock, mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ):
                result = skills_commands.skills_prove(Path.cwd(), "security")
        finally:
            sys.path.remove(lib_path)

        improve_mock.assert_called_once()
        self.assertEqual(result.data["skill_proof"]["handle"], "security-reviewer")
        self.assertIn("goal_resolution", result.data["skill_proof"])
        self.assertEqual(
            result.data["skill_proof"]["validation_commands"],
            [result.data["skill_proof"]["next_command"]],
        )

    def test_skills_prove_goal_resolution_without_candidate_uses_improve_command(self):
        """Verify unresolved goals point back to the improve command."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            failed_reachability = CallResult(status="error")
            goal_result = CallResult()
            goal_result.data["improvement"] = {"recommended_capability": {}}

            with mock.patch.object(
                skills_commands,
                "skills_proof",
                return_value=failed_reachability,
            ), mock.patch.object(
                skills_commands,
                "improve_skills",
                return_value=goal_result,
            ):
                result = skills_commands.skills_prove(Path.cwd(), "unknown goal")
        finally:
            sys.path.remove(lib_path)

        skill_proof = result.data["skill_proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(skill_proof["proof_status"], "blocked_goal_resolution")
        self.assertEqual(skill_proof["next_command"], "./bin/ask skills improve 'unknown goal' --json --robot")
        self.assertEqual(skill_proof["validation_commands"], [skill_proof["next_command"]])

    def test_skills_prove_resolved_handle_failure_does_not_use_goal_fallback(self):
        """Verify a resolved handle with broken reachability stays on the requested handle."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult, ErrorObject

            failed_reachability = CallResult(status="error")
            failed_reachability.data["proof"] = {
                "status": "fail",
                "handle": "autofix",
                "resolution": {
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md",
                },
            }
            failed_reachability.errors.append(
                ErrorObject(code="ERR_VALIDATION", message="reachability failed")
            )

            with mock.patch.object(
                skills_commands,
                "skills_proof",
                return_value=failed_reachability,
            ), mock.patch.object(
                skills_commands,
                "improve_skills",
            ) as improve_mock, mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ), mock.patch.object(
                skills_commands,
                "skill_invocation_analytics",
                return_value={"status": "unavailable_or_legacy"},
            ):
                result = skills_commands.skills_prove(Path.cwd(), "autofix")
        finally:
            sys.path.remove(lib_path)

        improve_mock.assert_not_called()
        self.assertEqual(result.status, "error")
        self.assertEqual(result.data["skill_proof"]["handle"], "autofix")
        self.assertEqual(result.data["skill_proof"]["proof_status"], "blocked_reachability")
        self.assertEqual(
            result.data["skill_proof"]["validation_commands"],
            [result.data["skill_proof"]["next_command"]],
        )

    def test_skills_prove_human_output_exposes_validation(self):
        """Verify ask skills prove renders its scorecard validation command."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "prove",
            "autofix",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills prove output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("SDK skill proof failed for 'autofix'.", result.stdout)
        self.assertIn("skills sync --scope user --projection flat --dry-run", result.stdout)

    def test_skills_prove_workout_candidates_require_explicit_metadata_match(self):
        """Verify workout outcome candidates are not inferred from directory names."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills import _skill_workout_candidates

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                false_positive = repo_root / ".workouts" / "autofix-but-not-referenced"
                false_positive.mkdir(parents=True)
                false_positive.joinpath("workout.yaml").write_text(
                    "id: unrelated\nskills:\n  - other-skill\n",
                    encoding="utf-8",
                )
                explicit_match = repo_root / ".workouts" / "explicit-outcome"
                explicit_match.mkdir(parents=True)
                explicit_match.joinpath("workout.yaml").write_text(
                    "id: outcome\nskills:\n  - autofix\n",
                    encoding="utf-8",
                )
                target_module_match = repo_root / ".workouts" / "target-module-outcome"
                target_module_match.mkdir(parents=True)
                target_module_match.joinpath("workout.yaml").write_text(
                    "id: outcome-target\ntarget_module: autofix\n",
                    encoding="utf-8",
                )

                candidates = _skill_workout_candidates(repo_root, "autofix")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(candidates, ["explicit-outcome", "target-module-outcome"])

    def test_skills_prove_workout_next_command_uses_ask_helper(self):
        """Verify workout proof replay commands use the shared ask command builder."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_source = repo_root / "Skills" / "agent-ops" / "demo" / "SKILL.md"
                skill_source.parent.mkdir(parents=True)
                skill_source.write_text("---\nname: demo\n---\n", encoding="utf-8")

                reachable_result = CallResult()
                reachable_result.data["proof"] = {
                    "status": "pass",
                    "handle": "demo",
                    "resolution": {
                        "status": "ok",
                        "handle": "demo",
                        "source_path": skill_source.relative_to(repo_root).as_posix(),
                    },
                }

                with mock.patch.object(
                    skills_commands,
                    "skills_proof",
                    return_value=reachable_result,
                ), mock.patch.object(
                    skills_commands,
                    "audit_skill",
                    return_value=CallResult(),
                ), mock.patch.object(
                    skills_commands,
                    "skill_invocation_analytics",
                    return_value={"status": "unavailable_or_legacy"},
                ), mock.patch.object(
                    skills_commands,
                    "_skill_workout_candidates",
                    return_value=["outcome proof"],
                ):
                    result = skills_commands.skills_prove(repo_root, "demo")
        finally:
            sys.path.remove(lib_path)

        skill_proof = result.data["skill_proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(skill_proof["proof_status"], "reachable_without_outcome_proof")
        self.assertEqual(skill_proof["next_command"], "./bin/ask workouts run 'outcome proof' --json --robot")
        self.assertEqual(skill_proof["validation_commands"], [skill_proof["next_command"]])

    def test_skills_prove_accepts_current_identity_bound_shard_aggregate(self):
        """A current local aggregate is outcome proof rather than a legacy workout."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / "Skills" / "agent-ops" / "demo" / "SKILL.md"
                source.parent.mkdir(parents=True)
                source.write_text("---\nname: demo\n---\n", encoding="utf-8")
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                rubric_digest = "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                aggregate_path = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo" / "proof" / "aggregate.json"
                aggregate_path.parent.mkdir(parents=True)
                aggregate_path.write_text(
                    json.dumps(
                        {
                            "status": "success",
                            "data": {
                                "skills_sdk_eval_shard_aggregate": {
                                    "status": "pass",
                                    "receipt": {
                                        "status": "pass",
                                        "lane": "oss-local",
                                        "profile": "oss-local",
                                        "codex_profile": "oss-local",
                                        "package_id": "demo",
                                        "package_digest": "sha256:current",
                                        "rubric_digest": rubric_digest,
                                        "scenario_set_id": "demo-release-8-v1",
                                        "case_count": 8,
                                        "checks": [
                                            {"id": "shards_match_current_package", "status": "pass"},
                                            {"id": "all_case_results_pass", "status": "pass"},
                                        ],
                                    },
                                },
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                reachable = CallResult()
                reachable.data["proof"] = {
                    "status": "pass",
                    "handle": "demo",
                    "resolution": {"status": "ok", "handle": "demo", "source_path": source.relative_to(repo_root).as_posix()},
                }
                with mock.patch.object(skills_commands, "skills_proof", return_value=reachable), mock.patch.object(
                    skills_commands, "audit_skill", return_value=CallResult()
                ), mock.patch.object(
                    skills_commands, "skill_invocation_analytics", return_value={"status": "unavailable_or_legacy"}
                ), mock.patch.object(
                    skills_commands, "_skill_workout_candidates", return_value=[]
                ), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    result = skills_commands.skills_prove(repo_root, "demo")
        finally:
            sys.path.remove(lib_path)

        proof = result.data["skill_proof"]
        self.assertEqual(proof["proof_status"], "proved_local")
        self.assertEqual(proof["outcome_proof"]["status"], "pass")
        self.assertEqual(proof["outcome_proof"]["evidence_ref"], "Infrastructure/artifacts/skills/demo/proof/aggregate.json")
        self.assertEqual(proof["next_command"], None)
        self.assertEqual(proof["validation_commands"], [])

    def test_skills_prove_keeps_outcome_proof_when_runtime_is_blocked(self):
        """Runtime reachability must not hide current local outcome evidence."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / "Skills" / "agent-ops" / "demo" / "SKILL.md"
                source.parent.mkdir(parents=True)
                source.write_text("---\nname: demo\n---\n", encoding="utf-8")
                blocked = CallResult(status="error")
                blocked.data["proof"] = {
                    "status": "fail",
                    "handle": "demo",
                    "resolution": {"status": "ok", "handle": "demo", "source_path": source.relative_to(repo_root).as_posix()},
                    "runtime_diagnostics": {
                        "recovery_commands": [
                            {"kind": "preview_user_runtime_sync", "command": "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot"}
                        ]
                    },
                }
                outcome_proof = {
                    "status": "pass",
                    "evidence_class": "oss_local_release_aggregate",
                    "evidence_ref": "Infrastructure/artifacts/skills/demo/proof/aggregate.json",
                    "evidence_digest": "sha256:current",
                    "scenario_set": "demo-release-8-v1",
                    "case_count": 8,
                }
                with mock.patch.object(skills_commands, "skills_proof", return_value=blocked), mock.patch.object(
                    skills_commands, "audit_skill", return_value=CallResult()
                ) as audit_mock, mock.patch.object(
                    skills_commands, "skill_invocation_analytics", return_value={"status": "unavailable_or_legacy"}
                ), mock.patch.object(
                    skills_commands, "_skill_workout_candidates", return_value=[]
                ), mock.patch.object(skills_commands._impl, "_eval_shard_outcome_proof", return_value=outcome_proof):
                    result = skills_commands.skills_prove(repo_root, "demo")
        finally:
            sys.path.remove(lib_path)

        proof = result.data["skill_proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["proof_status"], "blocked_reachability")
        self.assertEqual(proof["outcome_proof"]["status"], "pass")
        self.assertEqual(proof["outcome_proof"]["workout_candidates"], [])
        for key, value in outcome_proof.items():
            self.assertEqual(proof["outcome_proof"][key], value)
        self.assertEqual(
            proof["next_command"],
            "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
        )
        audit_mock.assert_called_once_with(
            repo_root,
            "Skills/agent-ops/demo",
            level="compat",
            validation_scope="source",
        )

    def test_skills_prove_rejects_stale_shard_aggregate_package_digest(self):
        """A passing aggregate for an earlier package must not prove the current source."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                source = repo_root / "Skills" / "agent-ops" / "demo" / "SKILL.md"
                source.parent.mkdir(parents=True)
                source.write_text("---\nname: demo\n---\n", encoding="utf-8")
                aggregate_path = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo" / "proof" / "aggregate.json"
                aggregate_path.parent.mkdir(parents=True)
                aggregate_path.write_text(
                    json.dumps(
                        {"status": "success", "data": {"skills_sdk_eval_shard_aggregate": {"status": "pass", "receipt": {
                            "status": "pass", "package_id": "demo", "package_digest": "sha256:stale",
                            "checks": [{"id": "shards_match_current_package", "status": "pass"}, {"id": "all_case_results_pass", "status": "pass"}],
                        }}}}
                    ),
                    encoding="utf-8",
                )
                reachable = CallResult()
                reachable.data["proof"] = {
                    "status": "pass",
                    "handle": "demo",
                    "resolution": {"status": "ok", "handle": "demo", "source_path": source.relative_to(repo_root).as_posix()},
                }
                with mock.patch.object(skills_commands, "skills_proof", return_value=reachable), mock.patch.object(
                    skills_commands, "audit_skill", return_value=CallResult()
                ), mock.patch.object(
                    skills_commands, "skill_invocation_analytics", return_value={"status": "unavailable_or_legacy"}
                ), mock.patch.object(
                    skills_commands, "_skill_workout_candidates", return_value=[]
                ), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    result = skills_commands.skills_prove(repo_root, "demo")
        finally:
            sys.path.remove(lib_path)

        proof = result.data["skill_proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["proof_status"], "reachable_without_outcome_proof")
        self.assertEqual(proof["outcome_proof"]["status"], "missing")

    def test_skills_prove_names_first_bounded_release_shard_when_outcome_is_missing(self):
        """A missing aggregate must advance through a bounded declared release shard."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands
            from ask.envelope import CallResult

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                skill_dir.mkdir(parents=True)
                skill_dir.joinpath("SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir()
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-8-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                reachable = CallResult()
                reachable.data["proof"] = {
                    "status": "pass",
                    "handle": "demo",
                    "resolution": {"status": "ok", "handle": "demo", "source_path": "Skills/agent-ops/demo/SKILL.md"},
                }
                with mock.patch.object(skills_commands, "skills_proof", return_value=reachable), mock.patch.object(
                    skills_commands, "audit_skill", return_value=CallResult()
                ), mock.patch.object(
                    skills_commands, "skill_invocation_analytics", return_value={"status": "unavailable_or_legacy"}
                ), mock.patch.object(
                    skills_commands, "_skill_workout_candidates", return_value=[]
                ), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    result = skills_commands.skills_prove(repo_root, "demo")
        finally:
            sys.path.remove(lib_path)

        proof = result.data["skill_proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["proof_status"], "reachable_without_outcome_proof")
        self.assertEqual(
            proof["next_command"],
            "./bin/ask sdk eval run Skills/agent-ops/demo --runner internal --mode release "
            "--codex-profile oss-local --scenario-set demo-release-8-v1 --case case-one --case case-two --json --robot",
        )

    def test_outcome_proof_next_command_rejects_undersized_release_set(self):
        """An invalid release set must not replace the existing safe repair action."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-invalid-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two]
""",
                    encoding="utf-8",
                )
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"):
                    command = skills_commands._impl._outcome_proof_next_command(
                        repo_root,
                        "demo",
                        "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot",
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(command, "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot")

    def test_outcome_proof_next_command_skips_current_passing_shard_cases(self):
        """A current shard receipt advances the next action to missing release cases."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-8-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                rubric_digest = "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipt_path = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo" / "run" / "sdk-eval-run-receipt.json"
                receipt_path.parent.mkdir(parents=True)
                receipt_path.write_text(
                    json.dumps(
                        {
                            "status": "pass",
                            "lane": "oss-local",
                            "lane_type": "release-shard",
                            "profile": "oss-local",
                            "codex_profile": "oss-local",
                            "rubric_digest": rubric_digest,
                            "scenario_set_id": "demo-release-8-v1",
                            "package_id": "demo",
                            "package_digest": "sha256:current",
                            "selected_case_ids": ["case-one", "case-two"],
                            "case_count": 2,
                            "passed_count": 2,
                            "failed_count": 0,
                        }
                    ),
                    encoding="utf-8",
                )
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    command = skills_commands._impl._outcome_proof_next_command(
                        repo_root,
                        "demo",
                        "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot",
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertIn("--case case-three --case case-four", command)

    def test_outcome_proof_next_command_aggregates_complete_current_release_shards(self):
        """Complete current shards advance to the existing aggregate command."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-5-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                rubric_digest = "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipts_root = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo"
                for index, selected_case_ids in enumerate((['case-one', 'case-two'], ['case-three', 'case-four'], ['case-five'])):
                    receipt_path = receipts_root / f"run-{index}" / "sdk-eval-run-receipt.json"
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(
                        json.dumps(
                            {
                                "status": "pass",
                                "lane": "oss-local",
                                "lane_type": "release-shard",
                                "profile": "oss-local",
                                "codex_profile": "oss-local",
                                "rubric_digest": rubric_digest,
                                "scenario_set_id": "demo-release-5-v1",
                                "package_id": "demo",
                                "package_digest": "sha256:current",
                                "selected_case_ids": selected_case_ids,
                                "case_count": len(selected_case_ids),
                                "passed_count": len(selected_case_ids),
                                "failed_count": 0,
                            }
                        ),
                        encoding="utf-8",
                    )
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    command = skills_commands._impl._outcome_proof_next_command(
                        repo_root,
                        "demo",
                        "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot",
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(
            command,
            "./bin/ask sdk eval aggregate-shards Skills/agent-ops/demo --scenario-set demo-release-5-v1 "
            "--codex-profile oss-local --receipt Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json "
            "--receipt Infrastructure/artifacts/skills/demo/run-1/sdk-eval-run-receipt.json "
            "--receipt Infrastructure/artifacts/skills/demo/run-2/sdk-eval-run-receipt.json --json --robot",
        )

    def test_outcome_proof_next_command_ignores_stale_and_non_shard_receipts(self):
        """Only current release-shard receipts may advance an OSS-local release set."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-5-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                receipts_root = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo"
                for run_name, lane_type, rubric_digest in (
                    ("full-release", "release", "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest()),
                    ("stale-shard", "release-shard", "sha256:stale"),
                ):
                    receipt_path = receipts_root / run_name / "sdk-eval-run-receipt.json"
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(
                        json.dumps(
                            {
                                "status": "pass",
                                "lane": "oss-local",
                                "lane_type": lane_type,
                                "profile": "oss-local",
                                "codex_profile": "oss-local",
                                "rubric_digest": rubric_digest,
                                "scenario_set_id": "demo-release-5-v1",
                                "package_id": "demo",
                                "package_digest": "sha256:current",
                                "selected_case_ids": ["case-one", "case-two"],
                                "case_count": 2,
                                "passed_count": 2,
                                "failed_count": 0,
                            }
                        ),
                        encoding="utf-8",
                    )
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    command = skills_commands._impl._outcome_proof_next_command(
                        repo_root,
                        "demo",
                        "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot",
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertIn("--case case-one --case case-two", command)
        self.assertNotIn("aggregate-shards", command)

    def test_outcome_proof_next_command_uses_latest_disjoint_release_shards(self):
        """A rerun replaces its earlier shard instead of duplicating aggregate cases."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-5-v1
    default: true
    minimum_scenarios: 5
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                rubric_digest = "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest()
                receipts_root = repo_root / "Infrastructure" / "artifacts" / "skills" / "demo"
                for index, (run_name, selected_case_ids) in enumerate(
                    (
                        ("rerun-old", ["case-one", "case-two"]),
                        ("rerun-new", ["case-one", "case-two"]),
                        ("run-one", ["case-three", "case-four"]),
                        ("run-two", ["case-five"]),
                    )
                ):
                    receipt_path = receipts_root / run_name / "sdk-eval-run-receipt.json"
                    receipt_path.parent.mkdir(parents=True)
                    receipt_path.write_text(
                        json.dumps(
                            {
                                "status": "pass",
                                "lane": "oss-local",
                                "lane_type": "release-shard",
                                "profile": "oss-local",
                                "codex_profile": "oss-local",
                                "rubric_digest": rubric_digest,
                                "scenario_set_id": "demo-release-5-v1",
                                "package_id": "demo",
                                "package_digest": "sha256:current",
                                "selected_case_ids": selected_case_ids,
                                "case_count": len(selected_case_ids),
                                "passed_count": len(selected_case_ids),
                                "failed_count": 0,
                            }
                        ),
                        encoding="utf-8",
                    )
                    os.utime(receipt_path, ns=(1_000_000_000 + index, 1_000_000_000 + index))
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"), mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ):
                    command = skills_commands._impl._outcome_proof_next_command(
                        repo_root,
                        "demo",
                        "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot",
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertIn("rerun-new", command)
        self.assertIn("run-one", command)
        self.assertIn("run-two", command)
        self.assertNotIn("rerun-old", command)

    def test_outcome_proof_next_command_falls_back_for_non_numeric_minimum(self):
        """Malformed release-set thresholds cannot escape the compact proof facade."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                skill_dir = repo_root / "Skills" / "agent-ops" / "demo"
                evals_path = skill_dir / "references" / "evals.yaml"
                evals_path.parent.mkdir(parents=True)
                evals_path.write_text(
                    """release_scenario_sets:
  - id: demo-release-invalid-v1
    default: true
    minimum_scenarios: not-a-number
    groups:
      core: [case-one, case-two, case-three, case-four, case-five]
""",
                    encoding="utf-8",
                )
                fallback = "./bin/ask skills audit Skills/agent-ops/demo --level strict --json --robot"
                with mock.patch.object(skills_commands._impl, "_skills_sdk_eval_source_path", return_value=skill_dir / "SKILL.md"):
                    command = skills_commands._impl._outcome_proof_next_command(repo_root, "demo", fallback)
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(command, fallback)

    def test_current_release_shard_receipts_reject_path_traversal_package_id(self):
        """Receipt discovery remains contained in the package artifact lane."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                rubric_path = repo_root / "Infrastructure" / "config" / "skills-sdk" / "gold-standard-rubric.v1.json"
                rubric_path.parent.mkdir(parents=True)
                rubric_path.write_text('{"rubric":"current"}\n', encoding="utf-8")
                escaped_receipt = repo_root / "Infrastructure" / "artifacts" / "outside" / "run" / "sdk-eval-run-receipt.json"
                escaped_receipt.parent.mkdir(parents=True)
                escaped_receipt.write_text(
                    json.dumps(
                        {
                            "status": "pass",
                            "lane": "oss-local",
                            "lane_type": "release-shard",
                            "profile": "oss-local",
                            "codex_profile": "oss-local",
                            "rubric_digest": "sha256:" + hashlib.sha256(rubric_path.read_bytes()).hexdigest(),
                            "scenario_set_id": "demo-release-5-v1",
                            "package_id": "../outside",
                            "package_digest": "sha256:current",
                            "selected_case_ids": ["case-one"],
                            "case_count": 1,
                            "passed_count": 1,
                            "failed_count": 0,
                        }
                    ),
                    encoding="utf-8",
                )
                receipts = skills_commands._impl._current_release_shard_receipts(
                    repo_root,
                    package_id="../outside",
                    package_digest="sha256:current",
                    scenario_set_id="demo-release-5-v1",
                )
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(receipts, [])

    def test_persist_eval_shard_aggregate_does_not_claim_failed_write(self):
        """A failed aggregate write cannot leave persisted-evidence fields on the payload."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                payload = {"mutation_performed": False}
                with mock.patch.object(Path, "write_text", side_effect=OSError("disk full")):
                    artifact_ref = skills_commands._impl._skills_sdk_persist_eval_shard_aggregate(
                        Path(temp_dir),
                        "demo",
                        payload,
                    )
        finally:
            sys.path.remove(lib_path)

        self.assertIsNone(artifact_ref)
        self.assertNotIn("artifact_path", payload)
        self.assertFalse(payload["mutation_performed"])

    def test_persist_eval_shard_aggregate_rejects_dot_package_ids(self):
        """Aggregate evidence never escapes its per-package artifact lane."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                for package_id in (".", ".."):
                    with self.subTest(package_id=package_id):
                        payload = {"mutation_performed": False}
                        artifact_ref = skills_commands._impl._skills_sdk_persist_eval_shard_aggregate(
                            repo_root,
                            package_id,
                            payload,
                        )
                        self.assertIsNone(artifact_ref)
                        self.assertEqual(payload, {"mutation_performed": False})
                        self.assertFalse((repo_root / "Infrastructure" / "artifacts").exists())
        finally:
            sys.path.remove(lib_path)

    def test_shard_aggregate_writes_evidence_only_outside_preview(self):
        """The normal aggregate route persists evidence while preview remains non-mutating."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                receipt = {"status": "pass", "agent_summary": "All bounded release shards passed."}
                with mock.patch.object(
                    skills_commands._impl,
                    "_skills_sdk_eval_package_identity",
                    return_value={"package_id": "demo", "package_digest": "sha256:current"},
                ), mock.patch(
                    "ask.skills_sdk.eval_shard_aggregate.build_eval_shard_aggregate_receipt",
                    return_value=receipt,
                ):
                    written = skills_commands.skills_sdk_eval_shard_aggregate(
                        repo_root,
                        target="Skills/agent-ops/demo",
                        scenario_set="demo-release-5-v1",
                        receipts=["Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json"],
                    )
                    preview = skills_commands.skills_sdk_eval_shard_aggregate_preview(
                        repo_root,
                        target="Skills/agent-ops/demo",
                        scenario_set="demo-release-5-v1",
                        receipts=["Infrastructure/artifacts/skills/demo/run-0/sdk-eval-run-receipt.json"],
                    )
                    written_payload = written.data["skills_sdk_eval_shard_aggregate"]
                    artifact_path = repo_root / written_payload["artifact_path"]
                    self.assertTrue(written_payload["mutation_performed"])
                    self.assertTrue(artifact_path.is_file())
                    self.assertEqual(
                        json.loads(artifact_path.read_text(encoding="utf-8"))["data"]["skills_sdk_eval_shard_aggregate"]["receipt"],
                        receipt,
                    )
                    preview_payload = preview.data["skills_sdk_eval_shard_aggregate"]
                    self.assertFalse(preview_payload["mutation_performed"])
                    self.assertNotIn("artifact_path", preview_payload)
        finally:
            sys.path.remove(lib_path)

    def test_compact_skill_prove_payload_keeps_local_outcome_evidence(self):
        """The compact proof facade retains the identity-bound outcome reference."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.cli_output import compact_skill_prove_payload
        finally:
            sys.path.remove(lib_path)

        payload = {
            "skill_proof": {
                "schema_version": "skill-proof-scorecard.v1",
                "query": "demo",
                "handle": "demo",
                "proof_status": "proved_local",
                "agent_summary": "demo has current local outcome proof.",
                "reachability": {"status": "pass", "command": "./bin/ask skills proof demo --json --robot"},
                "structural_quality": {"status": "pass", "audit_level": "compat", "audit_command": "audit demo"},
                "outcome_proof": {
                    "status": "pass",
                    "evidence_class": "oss_local_release_aggregate",
                    "evidence_ref": "Infrastructure/artifacts/skills/demo/proof/aggregate.json",
                    "evidence_digest": "sha256:current",
                    "scenario_set": "demo-release-8-v1",
                    "case_count": 8,
                },
                "next_command": None,
                "validation_commands": [],
            }
        }

        compact_skill_prove_payload(payload)

        self.assertEqual(
            payload["skill_proof"]["outcome_proof"],
            {
                "status": "pass",
                "evidence_class": "oss_local_release_aggregate",
                "evidence_ref": "Infrastructure/artifacts/skills/demo/proof/aggregate.json",
                "evidence_digest": "sha256:current",
                "scenario_set": "demo-release-8-v1",
                "case_count": 8,
            },
        )

    def test_skill_invocation_analytics_resolves_relative_telemetry_dir_from_repo_root(self):
        """Verify relative SKILL_TELEMETRY_DIR overrides are repo-root relative."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.skill_analytics import skill_invocation_analytics

            with tempfile.TemporaryDirectory() as temp_dir:
                repo_root = Path(temp_dir)
                telemetry_dir = repo_root / "telemetry"
                telemetry_dir.mkdir(parents=True)
                telemetry_dir.joinpath("skill-invocations.jsonl").write_text(
                    json.dumps({"skill_id": "autofix", "timestamp": "2026-05-07T10:00:00Z"}) + "\n",
                    encoding="utf-8",
                )
                with mock.patch.dict(os.environ, {"SKILL_TELEMETRY_DIR": "telemetry"}):
                    analytics = skill_invocation_analytics(repo_root, "autofix")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(analytics["status"], "available")
        self.assertEqual(analytics["matching_invocation_count"], 1)

    def test_skills_explain_json_contract(self):
        """Verify ask skills explain returns concise agent-facing skill guidance."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "explain", "autofix", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        skills_explain = output["data"]["skills_explain"]
        self.assertEqual(skills_explain["schema_version"], "skills-explain.v1")
        self.assertEqual(skills_explain["query"], "autofix")
        self.assertEqual(skills_explain["canonical_source"], "Skills/agent-ops/autofix/SKILL.md")
        self.assertEqual(skills_explain["skill_handle"], "autofix")
        self.assertEqual(skills_explain["handle_source"], "sdk_flat_registry")
        self.assertIn("validation", skills_explain)
        self.assertIn("when_not_to_use", skills_explain)

        explanation = output["data"]["explanation"]
        self.assertEqual(explanation["schema_version"], "skill-explanation.v1")
        self.assertEqual(explanation["handle"], "autofix")
        self.assertEqual(explanation["status"], "resolved")
        for field in (
            "agent_summary",
            "canonical_source_path",
            "runtime_projection_path",
            "skill_handles",
            "required_validation",
            "validation_commands",
            "known_limitations",
            "reachability",
            "next_command",
        ):
            self.assertIn(field, explanation)
        self.assertIsInstance(explanation["reachability"], dict)

    def test_skills_explain_human_output_exposes_validation(self):
        """Verify ask skills explain renders its primary validation command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "explain", "Skills/agent-ops/autofix", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills explain output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("ℹ️  Skill: $autofix (resolved)", result.stdout)
        self.assertIn("Source: Skills/agent-ops/autofix/SKILL.md", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills audit Skills/agent-ops/autofix --level strict --json --robot",
            result.stdout,
        )
        self.assertIn("Next: ./bin/ask skills proof autofix --json --robot", result.stdout)

    def test_skills_explain_golden_path_fields_for_flat_handles(self):
        """Verify explain exposes source, runtime, validation, and proof handoff."""
        for handle, canonical_source, owner in (
            ("agents-md", "Skills/agent-ops/agents-md/SKILL.md", "agent-ops"),
            ("simplify", "Skills/agent-ops/simplify/SKILL.md", "Agent Skills Team"),
        ):
            with self.subTest(handle=handle):
                cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "explain", handle, "--json", "--robot"]
                result = _run_cli(cmd)

                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                skills_explain = output["data"]["skills_explain"]
                self.assertEqual(skills_explain["query"], handle)
                self.assertEqual(skills_explain["canonical_source"], canonical_source)
                self.assertEqual(skills_explain["skill_handle"], handle)
                self.assertEqual(skills_explain["handle_source"], "sdk_flat_registry")
                self.assertIn(skills_explain["runtime_projection"], {"flat", "source"})
                self.assertIn(skills_explain["runtime_visibility"], {"flat", "source"})
                self.assertEqual(skills_explain["owner"], owner)
                self.assertIn("validation", skills_explain)
                self.assertIn("ambiguity_notes", skills_explain)

                explanation = output["data"]["explanation"]
                self.assertEqual(explanation["canonical_source_path"], canonical_source)
                if skills_explain["runtime_projection"] == "flat":
                    self.assertEqual(explanation["runtime_projection_path"], f".agents/skills/{handle}/SKILL.md")
                else:
                    self.assertIsNone(explanation["runtime_projection_path"])
                self.assertEqual(
                    explanation["skill_handles"],
                    [{
                        "handle": handle,
                        "path": explanation["runtime_projection_path"],
                        "projection_note": None if explanation["runtime_projection_path"] else "projection_not_file_backed",
                        "handle_source": "sdk_flat_registry",
                    }],
                )
                self.assertTrue(explanation["validation_commands"])
                self.assertIn("known_limitations", explanation)
                self.assertIn(explanation["reachability"]["status"], {"pass", "fail"})
                self.assertEqual(
                    explanation["reachability"]["proof_command"],
                    f"./bin/ask skills proof {handle} --json --robot",
                )
                self.assertEqual(explanation["next_command"], f"./bin/ask skills proof {handle} --json --robot")

    def test_skills_explain_rejects_out_of_repo_source_path(self):
        """Verify explain validates resolved skill paths before reading skill files."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "escaped",
                    "source_path": "../outside/SKILL.md",
                    "description": "outside repo",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "escaped")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_PATH_TRAVERSAL")

    def test_skills_explain_rejects_missing_source_path(self):
        """Verify explain rejects resolved handles that omit the source path."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "missing-source",
                    "description": "missing source",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "missing-source")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("without a canonical source path", result.errors[0].message)

    def test_skills_explain_rejects_nonexistent_source_file(self):
        """Verify explain rejects stale handles before reading source sections."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "stale-source",
                    "source_path": "Skills/agent-ops/nope/SKILL.md",
                    "description": "stale source",
                },
            ):
                result = skills_commands.explain_skill(Path.cwd(), "stale-source")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("is missing", result.errors[0].message)

    def test_skills_explain_rejects_unreadable_source_file(self):
        """Verify explain rejects source files that cannot be read."""
        lib_path = str(REPO_ROOT / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands import skills as skills_commands

            with mock.patch.object(
                skills_commands,
                "resolve_skill_handle",
                return_value={
                    "status": "ok",
                    "handle": "autofix",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                    "description": "autofix",
                },
            ), mock.patch.object(
                skills_commands,
                "_skill_sections",
                side_effect=PermissionError("permission denied"),
            ):
                result = skills_commands.explain_skill(REPO_ROOT, "autofix")
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("could not be read", result.errors[0].message)

    def test_reviewers_resolve_json_contract(self):
        """Verify ask reviewers resolve exposes the reviewer handle namespace."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector", "--json"]
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "agents.json"
            manifest.write_text(
                json.dumps([{"role": "skill-inspector", "source": "test", "output": "agents/skill-inspector.toml"}]),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["CODEX_AGENTS_MANIFEST"] = str(manifest)
            result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["kind"], "reviewer")
        self.assertEqual(resolution["command_visibility"], "reviewer")
        self.assertEqual(resolution["canonical_handle"], "skill-inspector")
        self.assertEqual(
            resolution["validation_commands"],
            ["./bin/ask reviewers resolve skill-inspector --json --robot"],
        )

    def test_reviewers_resolve_human_output(self):
        """Verify ask reviewers resolve has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector"]
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "agents.json"
            manifest.write_text(
                json.dumps([{"role": "skill-inspector", "source": "test", "output": "agents/skill-inspector.toml"}]),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["CODEX_AGENTS_MANIFEST"] = str(manifest)
            result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Reviewer handle: @skill-inspector", result.stdout)
        self.assertIn("Source: test", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask reviewers resolve skill-inspector --json --robot",
            result.stdout,
        )

    def test_reviewers_missing_action_exposes_validation(self):
        """Verify ask reviewers missing action returns a concrete recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask reviewers resolve skill-inspector --json --robot"],
        )

    def test_reviewers_missing_action_human_output_exposes_validation(self):
        """Verify ask reviewers missing action prints the recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("missing action for topic 'reviewers'", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask reviewers resolve skill-inspector --json --robot",
            result.stdout,
        )

    def test_skills_invalid_action_mentions_prove(self):
        """Verify invalid skill-action guidance includes the public prove command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "nonsense", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        suggestion = output["errors"][0]["fix_suggestion"]
        self.assertIn("prove", suggestion)

    def test_unknown_action_helpers_share_valid_actions_fix_suggestion(self):
        """Verify unknown-action helpers format valid actions from one source."""
        unknown_result = build_unknown_action_result("repo", "nonsense")
        helpful_result = build_helpful_error("repo", "nonsense", ["repo", "nonsense"])

        expected_suggestion = f"Valid actions: {', '.join(VALID_ACTIONS['repo'])}"
        self.assertEqual(unknown_result.errors[0].fix_suggestion, expected_suggestion)
        self.assertEqual(helpful_result.errors[0].fix_suggestion, expected_suggestion)
        self.assertEqual(
            unknown_result.data["validation_commands"],
            ["./bin/ask repo status --json --robot"],
        )
        self.assertEqual(
            unknown_result.data["candidate_commands"],
            [
                "ask repo doctor --json --robot",
                "ask repo closeout --changed --json --robot",
                "ask repo validate --ephemeral",
            ],
        )

    def test_skills_unknown_action_exposes_parser_recovery_validation(self):
        """Verify parser-level unknown skill actions expose the recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "nonsense", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("Unknown action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask sdk start <skill> --json --robot"])
        self.assertEqual(
            output["data"]["candidate_commands"],
            [
                "ask skills package verify Skills/agent-ops/simplify --strict --json --robot",
                "ask skills prove Skills/agent-ops/simplify --json --robot",
            ],
        )

    def test_skills_unknown_action_human_output_exposes_parser_recovery_validation(self):
        """Verify parser-level unknown skill actions render the recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "nonsense", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Unknown action", result.stdout)
        self.assertIn("Validation: ./bin/ask sdk start <skill> --json --robot", result.stdout)

    def test_skills_default_help_hides_expert_routes_but_sync_remains_callable(self):
        help_result = _run_cli([sys.executable, "Infrastructure/bin/ask", "skills", "--help"])
        sync_result = _run_cli([sys.executable, "Infrastructure/bin/ask", "skills", "sync", "--help"])

        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("{package,prove}", help_result.stdout)
        self.assertNotIn("Synchronize skill symlinks", help_result.stdout)
        self.assertEqual(sync_result.returncode, 0, sync_result.stderr)
        self.assertIn("--user-sync-mode {full,links-only}", sync_result.stdout)

    def test_sdk_unknown_action_keeps_expert_routes_out_of_default_recovery(self):
        cmd = [sys.executable, "Infrastructure/bin/ask", "sdk", "unsupported-action", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        error = output["errors"][0]
        self.assertEqual(error["fix_suggestion"], "Valid actions: start, check")
        self.assertIn("choose from start, check", error["message"])
        self.assertNotIn("score", error["message"])
        self.assertNotIn("lifecycle", error["message"])
        self.assertEqual(
            output["data"]["candidate_commands"],
            [
                "ask sdk start Skills/agent-ops/simplify --json --robot",
                "ask sdk check Skills/agent-ops/simplify --json --robot",
            ],
        )

    def test_ambiguous_action_first_error_exposes_candidate_commands(self):
        """Verify ambiguous action-first parser errors expose machine-readable candidates."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "list", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("ambiguous", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["candidate_commands"],
            ["ask skills list", "ask plugins list", "ask graph list"],
        )
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask sdk start <skill> --json --robot",
                "./bin/ask plugins list --json --robot",
                "./bin/ask graph list --json --robot",
            ],
        )

    def test_argument_error_exposes_candidate_commands(self):
        """
        Verify that missing required arguments in known commands expose candidate command examples.
        
        Tests that when a required argument is omitted (e.g., `skills resolve --json --robot` without a skill identifier), the error response includes candidate commands matching the expected argument pattern.
        """
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "resolve", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("argument syntax is invalid", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask skills resolve --help"])
        self.assertEqual(len(output["data"]["candidate_commands"]), 1)
        self.assertRegex(
            output["data"]["candidate_commands"][0],
            r"^ask skills resolve Skills/agent-ops/[a-z0-9-]+ --json$",
        )

    def test_skills_missing_action_exposes_validation(self):
        """Verify incomplete skills commands expose the read-only recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask sdk start <skill> --json --robot"])

    def test_skills_missing_action_human_output_exposes_validation(self):
        """Verify incomplete skills commands render the read-only recovery command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("missing action for topic 'skills'", result.stdout)
        self.assertIn("Validation: ./bin/ask sdk start <skill> --json --robot", result.stdout)

    def test_skills_goal_json_contract(self):
        """
        Ensure the `ask skills goal create` CLI returns a JSON envelope containing a `goal_decision` with required fields.

        Asserts the top-level `status` and `data` keys exist and that `data.goal_decision` includes `schema_version`, `decision_status`, `policy_identity`, `recommended_candidate`, and `alternative_candidates`.
        """
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "goal", "create auth integration", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("data", output)
        self.assertIn("goal_decision", output["data"])
        goal = output["data"]["goal_decision"]
        self.assertEqual(goal.get("schema_version"), "goal-decision.v1")
        self.assertIn("decision_status", goal)
        self.assertIn("policy_identity", goal)
        self.assertIn("recommended_candidate", goal)
        self.assertIn("alternative_candidates", goal)
        self.assertEqual(
            goal.get("validation_commands"),
            ["./bin/ask skills goal 'create auth integration' --json --robot"],
        )

    def test_skills_goal_human_output_exposes_validation(self):
        """Verify ambiguous goal output renders the goal validation command."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "goal",
            "help me",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("🎯 Goal decision:", result.stdout)
        self.assertIn("Validation: ./bin/ask skills goal", result.stdout)
        self.assertIn("--json --robot", result.stdout)

    def test_skills_improve_json_contract(self):
        """Verify `ask skills improve` returns an agent-facing recommendation envelope."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "skills",
            "improve",
            "autofix",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        improvement = output.get("data", {}).get("improvement", {})
        self.assertEqual(improvement.get("schema_version"), "skill-improvement-recommendation.v1")
        self.assertIn(improvement.get("route_state"), {"blocked_reachability", "resolved", "resolved_with_fallback"})
        self.assertIn("route_state_reason", improvement)
        self.assertIn("goal_decision_status", improvement)
        self.assertIn("agent_summary", improvement)
        self.assertIn("recommended_capability", improvement)
        self.assertIn("why", improvement)
        self.assertIn("reachability", improvement)
        self.assertIn("proof", improvement)
        self.assertIn("why", improvement)
        self.assertIn("next_command", improvement)
        self.assertEqual(improvement["validation_commands"], [improvement["next_command"]])

    def test_skills_improve_human_output_exposes_validation(self):
        """Verify ask skills improve renders the recommendation validation command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "skills",
            "improve",
            "autofix",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"skills improve output: {result.stdout}\nstderr: {result.stderr}")
        if result.returncode == 0:
            self.assertIn("🎯 Skill improvement:", result.stdout)
            self.assertIn("Recommended:", result.stdout)
            self.assertIn("Reachability: pass", result.stdout)
            self.assertIn("Validation: ./bin/ask skills proof", result.stdout)
            self.assertIn("Next: ./bin/ask skills proof", result.stdout)
        else:
            self.assertIn("SDK skill proof failed for 'autofix'", result.stdout)
            self.assertIn("skills sync --scope user --projection flat --dry-run", result.stdout)

    def test_repo_doctor_catalog_json_contract(self):
        """
        Verify `ask repo doctor-catalog --json` returns a catalog parity payload with required fields.

        Asserts the CLI emits non-empty JSON and that `data.catalog_parity` contains `schema_version`, `drift_detected` and `surfaces`.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor-catalog", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("catalog_parity", output.get("data", {}))
        report = output["data"]["catalog_parity"]
        self.assertEqual(report.get("schema_version"), "catalog-parity.v1")
        self.assertIn("drift_detected", report)
        self.assertIn("surfaces", report)

    def test_repo_doctor_json_contract(self):
        """Verify `ask repo doctor --json` exposes the golden-path payload."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "doctor",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        doctor = output.get("data", {}).get("doctor", {})
        self.assertIn("agent_summary", doctor)
        self.assertIn("blocking", doctor)
        self.assertIn("blockers", doctor)
        self.assertIn("next_command", doctor)
        self.assertIn("signals", doctor)
        self.assertIn("diagnostic_debt", doctor)
        capability = doctor["signals"].get("capability_readiness", {})
        projection = doctor["signals"].get("projection_sync", {})
        if projection.get("state") == "warn":
            self.assertEqual(capability.get("state"), "skipped")
            self.assertEqual(capability.get("source"), "repo_status")
            self.assertIn("intentionally has no runtime projection", capability.get("summary", ""))
        else:
            self.assertEqual(capability.get("state"), "pass")
            self.assertEqual(capability.get("source"), "skills_profiles+skills_events")
        memory = doctor["signals"].get("memory_readiness", {})
        self.assertEqual(memory.get("state"), "skipped" if projection.get("state") == "warn" else "pass")
        package = doctor["signals"].get("package_readiness", {})
        self.assertEqual(package.get("state"), "skipped" if projection.get("state") == "warn" else "pass")

    def test_repo_doctor_human_output_includes_readiness_signals(self):
        """Verify repo doctor --robot prints capability-readiness signals."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "doctor",
            "--robot",
        ]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Repo doctor:", result.stdout)
        self.assertIn("Usable with diagnostic debt", result.stdout)
        if "Capability readiness:" not in result.stdout:
            self.assertIn("intentionally unmaterialized", result.stdout)
        self.assertIn("Next:", result.stdout)

    def test_repo_doctor_help_mentions_agent_health_entrypoint(self):
        """Verify `ask repo doctor --help` exposes the agent health wording."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor", "--help"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Agent-facing repository health entrypoint", result.stdout)

    def test_repo_provider_audit_json_contract_exposes_validation(self):
        """Verify provider audit exposes its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "provider-audit",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"provider audit output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("provider_policy", output["data"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask repo provider-audit --json --robot"],
        )

    def test_repo_provider_audit_human_output_exposes_validation(self):
        """Verify provider audit human output names its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "provider-audit",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"provider audit output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Provider policy:", result.stdout)
        self.assertIn("Validation: ./bin/ask repo provider-audit --json --robot", result.stdout)

    def test_repo_check_stability_json_contract_exposes_validation(self):
        """Verify check-stability exposes its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "check-stability",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"check-stability output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("stable_skills", output["data"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask repo check-stability --json --robot"],
        )

    def test_repo_check_stability_human_output_exposes_validation(self):
        """Verify check-stability human output names its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "check-stability",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"check-stability output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Stability check passed", result.stdout)
        self.assertIn("Validation: ./bin/ask repo check-stability --json --robot", result.stdout)

    def test_repo_closeout_json_contract(self):
        """Verify `ask repo closeout --changed --json` exposes readiness fields."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "closeout",
            "--changed",
            "--robot",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        closeout = output.get("data", {}).get("repo_closeout", {})
        self.assertIn("changed_files", closeout)
        self.assertIn("sync", closeout)
        self.assertIn("runtime_budget", closeout)
        self.assertIn("capability_readiness", closeout)
        self.assertIn("memory_readiness", closeout)
        self.assertIn("package_readiness", closeout)
        self.assertIn("surface_policy", closeout)
        self.assertIn("runtime_evidence", closeout)
        self.assertIn("focused_validation", closeout)
        self.assertIn("commit_readiness", closeout)
        self.assertIn("next_command", closeout)
        capability = closeout["capability_readiness"]
        if capability["status"] == "skipped":
            self.assertIn("intentionally has no runtime projection", capability["summary"])
        else:
            self.assertEqual(capability["status"], "pass")
            self.assertIn(capability["profile_contract_status"], {"ready", None})
            self.assertEqual(capability["profile_contract_gap_count"], 0)
            self.assertIn(capability["event_contract_status"], {"ready", None})
            self.assertEqual(capability["event_contract_gap_count"], 0)
            self.assertIsInstance(capability["eval_blocker_classes"], list)
            self.assertEqual(capability["eval_blocker_class_count"], len(capability["eval_blocker_classes"]))
            self.assertEqual(capability["contract_gap_count"], 0)
        memory = closeout["memory_readiness"]
        if memory["status"] == "skipped":
            self.assertIn("intentionally has no runtime projection", memory["summary"])
        else:
            self.assertEqual(memory["status"], "pass")
            self.assertIn(memory["provider_model"], {"extension-like-read-only", None})
            self.assertGreaterEqual(memory["entry_count"], 0)
            self.assertIn("available_sources", memory)
            self.assertIsInstance(memory["by_freshness"], dict)
        package = closeout["package_readiness"]
        if package["status"] == "skipped":
            self.assertIn("intentionally has no runtime projection", package["summary"])
        else:
            self.assertEqual(package["status"], "pass")
            self.assertIsInstance(package["target"], str)
        runtime_evidence = closeout["runtime_evidence"]
        self.assertIn(runtime_evidence["status"], {"not_applicable", "missing", "present", "invalid", "deleted"})
        self.assertEqual(runtime_evidence["evidence_root"], ".harness/evidence/runtime-proof")
        self.assertIn("changed_scope", runtime_evidence)
        self.assertIn("workspace_scope", runtime_evidence)
        self.assertEqual(
            runtime_evidence["truth_boundaries"]["command_proof"],
            "workspace_runtime_evidence",
        )
        if runtime_evidence["status"] == "not_applicable":
            self.assertEqual(runtime_evidence["schema_validation"]["status"], "not_run")
            self.assertEqual(
                runtime_evidence["truth_boundaries"]["schema_proof"],
                "not_run_by_closeout_use_schema_validation_command",
            )
        else:
            self.assertEqual(runtime_evidence["schema_validation"]["status"], "pass")
            self.assertEqual(runtime_evidence["truth_boundaries"]["schema_proof"], "checked_by_repo_closeout")
        self.assertEqual(runtime_evidence["truth_boundaries"]["pr_truth"], "not_checked_by_repo_closeout")
        self.assertEqual(runtime_evidence["truth_boundaries"]["tracker_truth"], "not_checked_by_repo_closeout")
        self.assertEqual(runtime_evidence["truth_boundaries"]["docs_truth"], "not_checked_by_repo_closeout")
        validation_ids = [command["id"] for command in closeout["focused_validation"]]
        self.assertIn("skill_profiles_readiness", validation_ids)
        self.assertIn("skill_events_readiness", validation_ids)
        self.assertIn("skill_memory_readiness", validation_ids)
        self.assertIn("skill_package_readiness", validation_ids)
        package_validation = next(
            command for command in closeout["focused_validation"] if command["id"] == "skill_package_readiness"
        )
        self.assertIn("--checkout-test", package_validation["command"])

    def test_repo_closeout_help_mentions_completion_readiness(self):
        """Verify `ask repo closeout --help` exposes completion-readiness wording."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "closeout", "--help"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("commit readiness", result.stdout)

    def test_repo_closeout_human_output_mentions_capability_readiness(self):
        """Verify non-JSON repo closeout output exposes readiness and validation cues."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "closeout",
            "--changed",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"repo closeout output: {result.stdout}\nstderr: {result.stderr}")
        if result.returncode == 0:
            self.assertIn("Repo closeout: Ready: no closeout blockers detected.", result.stdout)
            self.assertIn("Commit ready: True", result.stdout)
        else:
            self.assertIn("Blocked: closeout has", result.stdout)
            self.assertIn("💡 ./bin/ask ", result.stdout)
            return
        self.assertIn("Capability readiness:", result.stdout)
        self.assertIn("Memory readiness:", result.stdout)
        self.assertIn("Package readiness:", result.stdout)
        self.assertIn("Runtime evidence:", result.stdout)
        self.assertIn("command=workspace_runtime_evidence", result.stdout)
        self.assertTrue(
            "schema=checked_by_repo_closeout" in result.stdout
            or "schema=not_run_by_closeout_use_schema_validation_command" in result.stdout
        )
        self.assertIn("PR=not_checked_by_repo_closeout", result.stdout)
        self.assertIn("skill_profiles_readiness", result.stdout)
        self.assertIn("skill_events_readiness", result.stdout)
        self.assertIn("skill_memory_readiness", result.stdout)
        self.assertIn("skill_package_readiness", result.stdout)

    def test_goal_alias_normalization(self):
        """
        Ensure the `goal create` CLI alias returns a skills-style goal decision in the JSON envelope.

        Runs `bin/ask goal create auth integration --json`, asserts stdout contains JSON and that `data.goal_decision` exists.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "goal", "create auth integration", "--json"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_goal_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json goal alias maps to ask skills goal."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "--json", "goal", "create auth integration"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_doctor_catalog_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json doctor catalog alias maps to repo doctor-catalog."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "--json", "doctor", "catalog"]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("catalog_parity", output.get("data", {}))

    def test_skills_starter_mode(self):
        """
        Verify the CLI `skills starter` command returns starter-mode catalogue metadata for the chosen archetype.

        Runs `bin/ask skills starter --archetype delivery --limit 5 --json` and asserts the process exits with code 0, the JSON envelope `status` is `"success"`, `data.starter_mode` is truthy, `data.starter_archetype` equals `"delivery"`, and `data.skills` is a list.
        """
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "skills", "starter", "--archetype", "delivery", "--limit", "5", "--json"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, f"skills starter failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("starter_mode"))
        self.assertEqual(output["data"].get("starter_archetype"), "delivery")
        self.assertIsInstance(output["data"].get("skills"), list)
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills starter --archetype delivery --limit 5 --json --robot"],
        )

    def test_skills_starter_human_output_exposes_validation(self):
        """Verify ask skills starter renders its validation command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "skills",
            "starter",
            "--archetype",
            "delivery",
            "--limit",
            "5",
            "--robot",
        ]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Starter skills (5) [delivery]", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills starter --archetype delivery --limit 5 --json --robot",
            result.stdout,
        )

    def test_skills_package_command(self):
        """Verify ask skills package exposes package readiness metadata."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        package = output["data"]["skill_package"]
        self.assertEqual(package["schema_version"], "skill-package-readiness.v1")
        self.assertIsNone(package["target_summary"]["handle"])
        self.assertEqual(
            package["target_summary"]["canonical_source_path"],
            "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        )
        self.assertEqual(package["target_summary"]["target_kind"], package["target_kind"])
        self.assertIn("version", package["package_contract"]["required_fields"]["present"])
        self.assertEqual(package["readiness_summary"]["readiness_level"], package["package_contract"]["readiness_level"])
        self.assertIn("version", package["readiness_summary"]["present_fields"])
        self.assertEqual(
            package["readiness_summary"]["missing_field_count"],
            len(package["package_contract"]["required_fields"]["missing"]),
        )
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        self.assertTrue(package["package_contract"]["install_gate"]["install_ready"])
        self.assertEqual(package["package_contract"]["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(package["package_contract"]["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(package["package_contract"]["promotion_gate"]["promotion_ready"])
        self.assertEqual(package["package_contract"]["required_fields"]["missing"], [])
        self.assertEqual(package["package_contract"]["install_gate"]["blocked_reasons"], [])
        self.assertEqual(package["package_contract"]["promotion_gate"]["blocked_reasons"], [])
        self.assertEqual(package["contract_schemas"]["package"], "skill-package-readiness.v1")
        self.assertEqual(package["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(package["operation_context"]["primary_profile"], "package-review")
        self.assertEqual(package["operation_context"]["promotion_profile"], "plugin-share")
        self.assertIn("metadata contract", package["operation_context"]["profiles"]["package-review"]["required_evidence"])
        self.assertIn(
            "./bin/ask skills package <handle-or-path> --json --robot",
            package["operation_context"]["events"]["package_readiness_checked"]["producer_commands"],
        )
        self.assertIn(
            "./bin/ask skills events package_readiness_checked --json --robot",
            package["operation_context"]["validation_commands"],
        )
        self.assertEqual(package["lifecycle_events"][1]["details"]["gate_summary"], package["gate_summary"])
        self.assertEqual(package["lifecycle_event"], package["lifecycle_events"][1])
        self.assertEqual(package["lifecycle_events"][1]["event_identity"]["event_type"], "package_readiness_checked")
        self.assertEqual(
            package["lifecycle_events"][1]["event_identity"]["subject_key"],
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
        )
        self.assertEqual(
            package["lifecycle_events"][1]["contract_schemas"]["lifecycle_event"],
            "capability-lifecycle-event.v1",
        )
        self.assertEqual(
            package["lifecycle_events"][1]["producer_command"],
            "./bin/ask skills package <handle-or-path> --json --robot",
        )
        self.assertEqual(
            package["lifecycle_events"][1]["observer_command"],
            "./bin/ask skills events package_readiness_checked --json --robot",
        )
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])

    def test_skills_package_rejects_missing_target(self):
        """Verify ask skills package preserves the required target contract."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "package", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIn("the following arguments are required: target", output["errors"][0]["message"])

    def test_skills_package_rejects_extra_non_verify_target(self):
        """Verify ask skills package does not ignore unexpected positional input."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "extra",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIn("unexpected verify-only arguments", output["errors"][0]["message"])

    def test_skills_package_rejects_verify_flags_without_verify_mode(self):
        """Verify verify-only flags cannot silently alter package readiness."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--expected-sha256",
            "0" * 64,
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIn("unexpected verify-only arguments", output["errors"][0]["message"])

    def test_skills_package_verify_strict_enforces_target_readiness_with_compact_json(self):
        """Verify strict verification uses the requested target's readiness gate."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "verify",
            "simplify",
            "--strict",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(len(result.stdout.encode("utf-8")), 10 * 1024)
        output = json.loads(result.stdout)
        verification = output["data"]["skill_package_verification"]
        self.assertTrue(verification["strict"])
        self.assertEqual(verification["status"], "pass")
        self.assertEqual(
            verification["next_command"],
            "./bin/ask skills prove simplify --json --robot",
        )
        self.assertEqual(
            verification["strict_package_readiness"]["missing_fields"],
            [],
        )
        self.assertEqual(output["errors"], [])

    def test_skills_package_human_output(self):
        """Verify ask skills package has a useful non-JSON readiness render."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill package: Plugins/skill-factory/skills/code_quality_review/skill-builder", result.stdout)
        self.assertIn("Event: package_readiness_checked", result.stdout)
        self.assertIn("Readiness level: share_ready", result.stdout)
        self.assertIn("Compatible roles: default, worker, skill-inspector", result.stdout)
        self.assertIn("Runtime needs: 3 declared", result.stdout)
        self.assertIn("Provenance: frontmatter:Agent Skills Team:2026-05-15:canonical-source", result.stdout)
        self.assertIn("Install ready:", result.stdout)
        self.assertIn("Checkout test:", result.stdout)
        self.assertIn("Promotion:", result.stdout)
        self.assertIn("Validation: ./bin/ask skills package <handle-or-path> --json --robot", result.stdout)
        self.assertIn("Next:", result.stdout)

    def test_skills_package_checkout_test_command_records_evidence(self):
        """Verify ask skills package --checkout-test records local install-gate evidence."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--checkout-test",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package checkout output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        package = output["data"]["skill_package"]
        checkout = package["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertEqual(package["gate_summary"]["checkout_test_status"], "pass")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready")
        self.assertTrue(package["gate_summary"]["promotion_ready"])
        self.assertIn("source_readable:true", checkout["evidence"])
        self.assertIn("package_metadata_complete:true", checkout["evidence"])

    def test_skills_package_strict_command_accepts_complete_metadata(self):
        """Verify ask skills package --strict accepts complete package metadata."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--strict",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills package strict output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        package = output["data"]["skill_package"]
        self.assertTrue(package["strict"])
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["blockers"], [])
        self.assertEqual(package["package_contract"]["required_fields"]["missing"], [])
        self.assertEqual(package["package_contract"]["install_gate"]["blocked_reasons"], [])
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])

    def test_skills_package_verify_strict_reaches_directory_verification(self):
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "package",
            "verify",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--strict",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        output = json.loads(result.stdout)
        self.assertIn("skill_package_verification", output["data"])
        self.assertTrue(output["data"]["skill_package_verification"]["strict"])

    def test_skills_doctor_command_exposes_lifecycle_and_readiness(self):
        """Verify ask skills doctor exposes lifecycle and readiness contracts."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "doctor", "Skills/agent-ops/autofix", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills doctor failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        doctor = output["data"]["skill_doctor"]
        self.assertEqual(doctor["schema_version"], "skill-doctor.v1")
        self.assertEqual(doctor["target_kind"], "canonical_source_path")
        self.assertEqual(doctor["target_summary"]["query"], "Skills/agent-ops/autofix")
        self.assertEqual(doctor["target_summary"]["canonical_source_path"], doctor["canonical_source_path"])
        self.assertIn("canonical_source", doctor["check_summary"]["check_names"])
        self.assertEqual(doctor["check_summary"]["check_count"], len(doctor["checks"]))
        self.assertIn("missing", doctor["check_summary"]["status_counts"])
        self.assertEqual(doctor["lifecycle_event"]["schema_version"], "capability-lifecycle-event.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_type"], "skill_doctor_completed")
        self.assertEqual(doctor["lifecycle_event"]["contract_schemas"]["events"], "skill-events.v1")
        self.assertEqual(doctor["lifecycle_event"]["event_identity"]["target_kind"], "canonical_source_path")
        self.assertEqual(doctor["lifecycle_event"]["event_identity"]["subject_key"], "Skills/agent-ops/autofix")
        self.assertEqual(
            doctor["lifecycle_event"]["producer_command"],
            "./bin/ask skills doctor <handle-or-path> --json --robot",
        )
        self.assertEqual(
            doctor["lifecycle_event"]["observer_command"],
            "./bin/ask skills events skill_doctor_completed --json --robot",
        )
        self.assertIn("blocked_user_input", doctor["readiness_taxonomy"]["blockers"])
        self.assertEqual(doctor["contract_schemas"]["doctor"]["version"], "skill-doctor.v1")
        self.assertEqual(doctor["contract_schemas"]["doctor"]["owner"], "Agent Skills Kit")
        self.assertTrue(
            doctor["contract_schemas"]["doctor"].get("path")
            or doctor["contract_schemas"]["doctor"].get("missing_schema_reason")
        )
        self.assertEqual(doctor["contract_schemas"]["events"]["version"], "skill-events.v1")
        self.assertEqual(doctor["contract_schema_versions"]["doctor"], "skill-doctor.v1")
        self.assertEqual(doctor["contract_schema_versions"]["events"], "skill-events.v1")
        self.assertEqual(doctor["operation_context"]["primary_profile"], "authoring")
        self.assertIn("package-review", doctor["operation_context"]["next_profiles"])
        self.assertIn("skill audit", doctor["operation_context"]["profiles"]["authoring"]["required_evidence"])
        self.assertIn(
            "./bin/ask skills doctor <handle-or-path> --json --robot",
            doctor["operation_context"]["events"]["skill_doctor_completed"]["producer_commands"],
        )
        self.assertIn(
            "./bin/ask skills events skill_doctor_completed --json --robot",
            doctor["operation_context"]["validation_commands"],
        )
        self.assertIn("eval_blocked", doctor["lifecycle_event_types"])
        self.assertIn("Packaging", doctor["sdk_layers"])
        projection_ownership = doctor["checks"]["projection_ownership"]
        self.assertEqual(projection_ownership["sdk_layer"], "Runtime Adapters")
        self.assertEqual(projection_ownership["source"]["classification"], "canonical_project_source")
        self.assertTrue(projection_ownership["source"]["editable_source"])
        self.assertFalse(projection_ownership["projection_editable"])
        self.assertEqual(
            projection_ownership["owner_manifest_schema"],
            "Infrastructure/config/schemas/skills-sdk.project.v1.schema.json",
        )
        self.assertEqual(doctor["checks"]["package_readiness"]["sdk_layer"], "Packaging")
        package_readiness = doctor["checks"]["capability_metadata"]["package_readiness"]
        self.assertIn("version", package_readiness["required_fields"]["present"])
        self.assertFalse(package_readiness["promotion_gate"]["share_ready"])
        package_contract = doctor["checks"]["capability_metadata"]["package_contract"]
        self.assertEqual(package_contract["role_compatibility"], package_readiness["role_compatibility"])
        self.assertEqual(package_contract["runtime_contract"], package_readiness["runtime_contract"])
        self.assertEqual(package_contract["install_gate"], package_readiness["install_gate"])
        self.assertEqual(package_contract["promotion_gate"], package_readiness["promotion_gate"])

    def test_skills_doctor_blocks_generated_projection_path_as_source(self):
        """Verify doctor refuses to treat generated .agents skill projections as source."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "doctor",
            ".agents/skills/1password",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills doctor output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        doctor = output["data"]["skill_doctor"]
        self.assertEqual(doctor["checks"]["projection_ownership"]["status"], "fail")
        self.assertEqual(
            doctor["checks"]["projection_ownership"]["source"]["classification"],
            "generated_runtime_projection",
        )
        self.assertFalse(doctor["checks"]["projection_ownership"]["source"]["editable_source"])
        self.assertIn("blocked_validation", [blocker["class"] for blocker in doctor["blockers"]])

    def test_skills_doctor_blocks_runtime_symlink_target_path(self):
        """Verify path-mode doctor classifies the queried path before dereferencing symlinks."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            source = repo_root / "Skills" / "agent-ops" / "autofix" / "SKILL.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "---\n"
                "name: autofix\n"
                "description: Fix a known issue\n"
                "version: 0.1.0\n"
                "---\n"
                "# Autofix\n",
                encoding="utf-8",
            )
            projection = repo_root / ".agents" / "skills" / "autofix"
            projection.parent.mkdir(parents=True)
            try:
                projection.symlink_to(source.parent)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ), mock.patch.object(
                skills_commands,
                "_skill_workout_candidates",
                return_value=["autofix proof"],
            ):
                result = skills_commands.skills_doctor(repo_root, ".agents/skills/autofix")

        doctor = result.data["skill_doctor"]
        projection_ownership = doctor["checks"]["projection_ownership"]
        self.assertEqual(result.status, "error")
        self.assertEqual(projection_ownership["status"], "fail")
        self.assertEqual(
            projection_ownership["source"]["classification"],
            "generated_runtime_projection",
        )
        self.assertEqual(
            projection_ownership["projection"]["classification"],
            "generated_runtime_projection",
        )
        self.assertFalse(projection_ownership["projection_editable"])
        self.assertIn("blocked_validation", [blocker["class"] for blocker in doctor["blockers"]])

    def test_skill_root_ownership_classifies_generated_roots_case_insensitively(self):
        """Verify generated-root guards survive mixed-case paths on case-insensitive filesystems."""
        from ask.commands import skills_impl as skills_commands

        agents_ownership = skills_commands._skill_root_ownership_for_path(".Agents/skills/1password")
        codex_ownership = skills_commands._skill_root_ownership_for_path(".CoDeX/skills/1password")

        self.assertEqual(agents_ownership["classification"], "generated_runtime_projection")
        self.assertFalse(agents_ownership["editable_source"])
        self.assertTrue(agents_ownership["owner_manifest_required_for_edit"])
        self.assertEqual(codex_ownership["classification"], "client_runtime_config")
        self.assertFalse(codex_ownership["editable_source"])
        self.assertTrue(codex_ownership["owner_manifest_required_for_edit"])

    def test_skills_doctor_allows_manifest_declared_project_skill_source(self):
        """Verify owner repo manifests can declare .agents/skills as canonical project source."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / ".agents" / "skills" / "local-demo" / "SKILL.md"
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text(
                "---\n"
                "name: local-demo\n"
                "description: Local owner skill\n"
                "version: 0.1.0\n"
                "---\n"
                "# Local Demo\n",
                encoding="utf-8",
            )
            (repo_root / "skills-sdk.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.project.v1",
                        "project_id": "owner-repo",
                        "skill_roots": [
                            {
                                "path": ".agents/skills",
                                "classification": "canonical_project_source",
                                "default_for_create": True,
                                "default_for_install": True,
                                "default_for_update": True,
                            }
                        ],
                        "eval_suite": {"path": ".harness/evals/skills"},
                        "evidence": {"output_path": ".harness/session-evidence/skills"},
                        "trust_policy": "local_owner",
                        "precedence_policy": "project_over_user_after_trust",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ), mock.patch.object(
                skills_commands,
                "_skill_workout_candidates",
                return_value=["local-demo proof"],
            ):
                result = skills_commands.skills_doctor(repo_root, ".agents/skills/local-demo")

        doctor = result.data["skill_doctor"]
        source = doctor["checks"]["projection_ownership"]["source"]
        self.assertNotEqual(result.status, "error")
        self.assertEqual(doctor["checks"]["projection_ownership"]["status"], "pass")
        self.assertEqual(source["classification"], "canonical_project_source")
        self.assertTrue(source["editable_source"])
        self.assertTrue(source["manifest_declared"])
        self.assertEqual(source["owner_manifest_path"], "skills-sdk.json")
        self.assertNotIn("blocked_validation", [blocker["class"] for blocker in doctor["blockers"]])

    def test_skill_root_ownership_prefers_most_specific_manifest_root(self):
        """Verify nested generated roots are not masked by broader manifest roots."""
        from ask.commands import skills_impl as skills_commands

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "skills-sdk.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.project.v1",
                        "project_id": "owner-repo",
                        "skill_roots": [
                            {
                                "path": ".agents/skills",
                                "classification": "canonical_project_source",
                                "default_for_create": True,
                                "default_for_install": True,
                                "default_for_update": True,
                            },
                            {
                                "path": ".agents/skills/generated",
                                "classification": "generated_runtime_projection",
                                "default_for_create": False,
                                "default_for_install": False,
                                "default_for_update": False,
                            },
                        ],
                        "eval_suite": {"path": ".harness/evals/skills"},
                        "evidence": {"output_path": ".harness/session-evidence/skills"},
                        "trust_policy": "local_owner",
                        "precedence_policy": "project_over_user_after_trust",
                    }
                ),
                encoding="utf-8",
            )

            ownership = skills_commands._skill_root_ownership_for_path(
                ".agents/skills/generated/demo",
                repo_root=repo_root,
            )

        self.assertEqual(ownership["root"], ".agents/skills/generated")
        self.assertEqual(ownership["classification"], "generated_runtime_projection")
        self.assertFalse(ownership["editable_source"])
        self.assertTrue(ownership["owner_manifest_required_for_edit"])

    def test_skills_doctor_rejects_duplicate_manifest_root_paths(self):
        """Verify duplicate manifest paths cannot grant canonical edit authority."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / ".agents" / "skills" / "local-demo" / "SKILL.md"
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text(
                "---\n"
                "name: local-demo\n"
                "description: Local owner skill\n"
                "version: 0.1.0\n"
                "---\n"
                "# Local Demo\n",
                encoding="utf-8",
            )
            (repo_root / "skills-sdk.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.project.v1",
                        "project_id": "owner-repo",
                        "skill_roots": [
                            {
                                "path": ".agents/skills",
                                "classification": "canonical_project_source",
                                "default_for_create": True,
                                "default_for_install": True,
                                "default_for_update": True,
                            },
                            {
                                "path": "/.agents/skills/",
                                "classification": "canonical_project_source",
                                "default_for_create": False,
                                "default_for_install": False,
                                "default_for_update": False,
                            },
                        ],
                        "eval_suite": {"path": ".harness/evals/skills"},
                        "evidence": {"output_path": ".harness/session-evidence/skills"},
                        "trust_policy": "local_owner",
                        "precedence_policy": "project_over_user_after_trust",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                skills_commands,
                "audit_skill",
                return_value=CallResult(),
            ), mock.patch.object(
                skills_commands,
                "_skill_workout_candidates",
                return_value=["local-demo proof"],
            ):
                result = skills_commands.skills_doctor(repo_root, ".agents/skills/local-demo")

        doctor = result.data["skill_doctor"]
        source = doctor["checks"]["projection_ownership"]["source"]
        self.assertEqual(result.status, "error")
        self.assertEqual(source["classification"], "generated_runtime_projection")
        self.assertFalse(source["manifest_declared"])
        self.assertIn("blocked_validation", [blocker["class"] for blocker in doctor["blockers"]])

    def test_skills_doctor_exposes_valid_manifest_state(self):
        """Verify doctor projection_ownership surfaces a valid owner-manifest state."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / ".agents" / "skills" / "local-demo" / "SKILL.md"
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text(
                "---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n",
                encoding="utf-8",
            )
            (repo_root / "skills-sdk.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.project.v1",
                        "project_id": "owner-repo",
                        "skill_roots": [
                            {
                                "path": ".agents/skills",
                                "classification": "canonical_project_source",
                                "default_for_create": True,
                                "default_for_install": True,
                                "default_for_update": True,
                            }
                        ],
                        "eval_suite": {"path": ".harness/evals/skills"},
                        "evidence": {"output_path": ".harness/session-evidence/skills"},
                        "trust_policy": "local_owner",
                        "precedence_policy": "project_over_user_after_trust",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                skills_commands, "audit_skill", return_value=CallResult()
            ), mock.patch.object(
                skills_commands, "_skill_workout_candidates", return_value=["local-demo proof"]
            ):
                result = skills_commands.skills_doctor(repo_root, ".agents/skills/local-demo")

        doctor = result.data["skill_doctor"]
        manifest_state = doctor["checks"]["projection_ownership"]["owner_manifest_state"]
        self.assertEqual(manifest_state["state"], "valid")
        self.assertFalse(manifest_state["legacy_compat"])
        self.assertEqual(manifest_state["blockers"], [])

    def test_skills_doctor_blocks_invalid_manifest_and_exposes_state(self):
        """Verify an invalid owner manifest is blocked, not silently treated as absent."""
        from ask.commands import skills_impl as skills_commands
        from ask.envelope import CallResult

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_source = repo_root / ".agents" / "skills" / "local-demo" / "SKILL.md"
            skill_source.parent.mkdir(parents=True)
            skill_source.write_text(
                "---\nname: local-demo\ndescription: Local owner skill\nversion: 0.1.0\n---\n# Local Demo\n",
                encoding="utf-8",
            )
            # Wrong schema version is a deterministic manifest blocker.
            (repo_root / "skills-sdk.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.project.v2",
                        "project_id": "owner-repo",
                        "skill_roots": [
                            {
                                "path": ".agents/skills",
                                "classification": "canonical_project_source",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                skills_commands, "audit_skill", return_value=CallResult()
            ), mock.patch.object(
                skills_commands, "_skill_workout_candidates", return_value=["local-demo proof"]
            ):
                result = skills_commands.skills_doctor(repo_root, ".agents/skills/local-demo")

        doctor = result.data["skill_doctor"]
        manifest_state = doctor["checks"]["projection_ownership"]["owner_manifest_state"]
        self.assertEqual(result.status, "error")
        self.assertEqual(manifest_state["state"], "invalid")
        self.assertIn(
            "manifest_schema_version_unsupported",
            [blocker["class"] for blocker in manifest_state["blockers"]],
        )
        self.assertIn("blocked_validation", [blocker["class"] for blocker in doctor["blockers"]])

    def test_skills_doctor_human_output_exposes_lifecycle_event(self):
        """Verify ask skills doctor exposes the primary lifecycle event in human output."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "doctor",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills doctor output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill doctor: Plugins/skill-factory/skills/code_quality_review/skill-builder", result.stdout)
        self.assertIn("Event: skill_doctor_completed", result.stdout)
        self.assertNotIn("Warning classes:", result.stdout)
        self.assertIn("Checks: available_not_run=1, pass=6, skipped=1", result.stdout)
        self.assertIn("Validation: ./bin/ask skills doctor <handle-or-path> --json --robot", result.stdout)
        self.assertIn("Next:", result.stdout)

    def test_skills_profiles_command_returns_selected_profile(self):
        """Verify ask skills profiles exposes one operation-mode contract."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "eval", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills profiles failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        profiles = output["data"]["skill_profiles"]
        self.assertEqual(profiles["schema_version"], "skill-operation-profiles.v1")
        self.assertEqual(profiles["selected_profile"], "eval")
        self.assertEqual(profiles["profile_names"], ["eval"])
        self.assertIn("package-review", profiles["available_profiles"])
        self.assertEqual(profiles["profile_summary"]["profile_count"], 1)
        self.assertEqual(profiles["profile_summary"]["profile_names"], ["eval"])
        self.assertTrue(profiles["profile_summary"]["has_profiles"])
        _assert_readiness_overview_ready(
            self,
            profiles["readiness_overview"],
            ["lifecycle_event_coverage", "profile_contracts"],
        )
        self.assertEqual(
            profiles["readiness_overview"]["contract_sections"],
            {
                "lifecycle_event_coverage": {"gap_count": 0, "ready": True, "status": "ready"},
                "profile_contracts": {"gap_count": 0, "ready": True, "status": "ready"},
            },
        )
        self.assertEqual(
            profiles["profile_summary"]["contract_dimensions"],
            ["allowed_roots", "permissions", "required_evidence", "stop_conditions", "write_policy"],
        )
        self.assertEqual(profiles["profile_summary"]["contract_dimension_count"], 5)
        self.assertEqual(
            profiles["profile_summary"]["contract_dimension_status"],
            {
                "allowed_roots": "ready",
                "permissions": "ready",
                "required_evidence": "ready",
                "stop_conditions": "ready",
                "write_policy": "ready",
            },
        )
        self.assertEqual(
            profiles["profile_summary"]["missing_profiles_by_contract_dimension"],
            {
                "allowed_roots": [],
                "permissions": [],
                "required_evidence": [],
                "stop_conditions": [],
                "write_policy": [],
            },
        )
        self.assertEqual(
            profiles["profile_summary"]["missing_profile_count_by_contract_dimension"],
            {
                "allowed_roots": 0,
                "permissions": 0,
                "required_evidence": 0,
                "stop_conditions": 0,
                "write_policy": 0,
            },
        )
        self.assertEqual(
            profiles["profile_summary"]["required_evidence_count"],
            len(profiles["profiles"]["eval"]["required_evidence"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["required_evidence_by_profile"]["eval"],
            sorted(profiles["profiles"]["eval"]["required_evidence"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["required_evidence_count_by_profile"]["eval"],
            len(profiles["profiles"]["eval"]["required_evidence"]),
        )
        self.assertTrue(profiles["profile_summary"]["has_required_evidence"])
        self.assertTrue(profiles["profile_summary"]["has_stop_conditions"])
        self.assertEqual(
            profiles["profile_summary"]["stop_conditions_by_profile"]["eval"],
            sorted(profiles["profiles"]["eval"]["stop_conditions"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["stop_condition_count_by_profile"]["eval"],
            len(profiles["profiles"]["eval"]["stop_conditions"]),
        )
        self.assertEqual(profiles["profile_summary"]["profiles_missing_allowed_roots"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_allowed_root_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_allowed_roots"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_allowed_roots"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_permissions"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_permission_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_permissions"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_permissions"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_required_evidence"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_required_evidence_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_required_evidence"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_required_evidence"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_stop_conditions"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_stop_condition_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_stop_conditions"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_stop_conditions"])
        self.assertEqual(profiles["profile_summary"]["profiles_without_taxonomy_stop_conditions"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_with_taxonomy_stop_conditions"], ["eval"])
        self.assertEqual(profiles["profile_summary"]["profiles_with_taxonomy_stop_condition_count"], 1)
        self.assertEqual(profiles["profile_summary"]["profiles_without_taxonomy_stop_condition_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_without_taxonomy_stop_conditions"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_taxonomy_stop_conditions"])
        self.assertTrue(profiles["profile_summary"]["has_taxonomy_stop_conditions"])
        self.assertIn("blocked_runtime", profiles["profile_summary"]["taxonomy_stop_conditions_by_profile"]["eval"])
        self.assertIn("timeout_no_output", profiles["profile_summary"]["taxonomy_stop_conditions_by_profile"]["eval"])
        self.assertEqual(
            profiles["profile_summary"]["taxonomy_stop_condition_count"],
            len(profiles["profile_summary"]["taxonomy_stop_conditions_by_profile"]["eval"]),
        )
        self.assertEqual(profiles["profile_summary"]["profiles_missing_write_policy"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_write_policy_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_write_policy"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_write_policy"])
        self.assertEqual(profiles["profile_summary"]["profiles_with_contract_gaps"], [])
        _assert_contract_ready(self, profiles["profile_summary"])
        self.assertIn("artifact_write_only", profiles["profile_summary"]["by_write_policy"])
        self.assertEqual(profiles["profile_summary"]["write_policy_count"], 1)
        self.assertEqual(
            profiles["profile_summary"]["write_policy_by_profile"]["eval"],
            profiles["profiles"]["eval"]["write_policy"],
        )
        self.assertIn("repo_read", profiles["profile_summary"]["by_permission"])
        self.assertEqual(
            profiles["profile_summary"]["permission_count"],
            len(profiles["profile_summary"]["by_permission"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["permissions_by_profile"]["eval"],
            sorted(profiles["profiles"]["eval"]["permissions"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["permission_count_by_profile"]["eval"],
            len(profiles["profiles"]["eval"]["permissions"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["allowed_roots_by_profile"]["eval"],
            sorted(profiles["profiles"]["eval"]["allowed_roots"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["allowed_root_count_by_profile"]["eval"],
            len(profiles["profiles"]["eval"]["allowed_roots"]),
        )
        self.assertEqual(list(profiles["profiles"]), ["eval"])
        eval_contract = profiles["profiles"]["eval"]["eval_profile_contract"]
        self.assertEqual(eval_contract["codex_profile"], "fast")
        self.assertEqual(eval_contract["codex_profile_config"], "[profiles.fast]")
        self.assertEqual(eval_contract["tessl_project_marker"], "tessl.json")
        self.assertIn(
            os.path.join(tempfile.gettempdir(), "ask-tessl-evals"),
            eval_contract["tessl_eval_staging_root"],
        )
        self.assertEqual(profiles["operation_context"]["profile_model"], "profile-v2-inspired")
        self.assertEqual(profiles["operation_context"]["contract_schemas"]["doctor"], "skill-doctor.v1")
        self.assertEqual(profiles["operation_context"]["contract_schemas"]["memory"], "skill-memory-provider.v1")
        self.assertIn("eval", profiles["operation_context"]["routing_contracts"]["events"])
        self.assertEqual(profiles["event_coverage"]["profile_count"], 1)
        self.assertEqual(profiles["event_coverage"]["profile_names"], ["eval"])
        self.assertIn("eval_blocked", profiles["event_coverage"]["events_by_profile"]["eval"])
        self.assertIn("eval_completed", profiles["event_coverage"]["events_by_profile"]["eval"])
        self.assertEqual(
            profiles["event_coverage"]["event_count_by_profile"]["eval"],
            len(profiles["event_coverage"]["events_by_profile"]["eval"]),
        )
        self.assertEqual(
            profiles["event_coverage"]["event_reference_count"],
            profiles["event_coverage"]["event_count_by_profile"]["eval"],
        )
        self.assertEqual(profiles["event_coverage"]["profiles_with_events"], ["eval"])
        self.assertEqual(profiles["event_coverage"]["profiles_with_event_count"], 1)
        self.assertEqual(profiles["event_coverage"]["profiles_missing_events"], [])
        self.assertEqual(profiles["event_coverage"]["profiles_missing_event_count"], 0)
        self.assertFalse(profiles["event_coverage"]["has_profiles_missing_events"])
        self.assertTrue(profiles["event_coverage"]["all_profiles_have_events"])
        self.assertEqual(profiles["event_coverage"]["profiles_with_event_gaps"], [])
        self.assertEqual(profiles["event_coverage"]["profiles_with_event_gap_count"], 0)
        _assert_contract_ready(self, profiles["event_coverage"])
        self.assertEqual(
            profiles["operation_context"]["consumer_commands"]["events"],
            "./bin/ask skills events --json --robot",
        )
        self.assertIn("Skills", profiles["workspace_roots"]["canonical_skill_roots"])
        self.assertIn(".agents/skills", profiles["workspace_roots"]["runtime_projection_roots"])
        self.assertIn("blocked_runtime", profiles["eval_blocker_classes"])
        self.assertEqual(
            profiles["blocker_taxonomy"]["blocked_runtime"],
            profiles["eval_blocker_classes"]["blocked_runtime"],
        )
        self.assertIn("strict_audit_not_run", profiles["warning_taxonomy"])
        self.assertIn("blocked_runtime", profiles["profiles"]["eval"]["stop_conditions"])
        self.assertIn("timeout_no_output", profiles["profiles"]["eval"]["stop_conditions"])
        self.assertIn("blocked_runtime", profiles["profiles"]["eval"]["stop_condition_definitions"])
        self.assertIn("timeout_no_output", profiles["profiles"]["eval"]["stop_condition_definitions"])
        self.assertIn("blocked_user_input", profiles["profiles"]["eval"]["eval_blocker_classes"])
        self.assertEqual(
            profiles["profiles"]["eval"]["effective_roots"],
            ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        )

    def test_skills_profiles_command_returns_aggregate_contract_readiness(self):
        """Verify ask skills profiles summarizes all operation-mode contracts."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills profiles failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        profiles = output["data"]["skill_profiles"]
        self.assertEqual(profiles["selected_profile"], None)
        _assert_readiness_overview_ready(
            self,
            profiles["readiness_overview"],
            ["lifecycle_event_coverage", "profile_contracts"],
        )
        self.assertEqual(
            profiles["readiness_overview"]["contract_sections"]["profile_contracts"]["status"],
            profiles["profile_summary"]["contract_status"],
        )
        self.assertEqual(
            profiles["readiness_overview"]["contract_sections"]["lifecycle_event_coverage"]["status"],
            profiles["event_coverage"]["contract_status"],
        )
        self.assertEqual(profiles["profile_summary"]["profile_count"], len(profiles["profiles"]))
        self.assertEqual(profiles["profile_summary"]["profile_names"], sorted(profiles["profiles"]))
        self.assertEqual(
            profiles["profile_summary"]["contract_dimensions"],
            ["allowed_roots", "permissions", "required_evidence", "stop_conditions", "write_policy"],
        )
        self.assertEqual(profiles["profile_summary"]["contract_dimension_count"], 5)
        self.assertEqual(
            set(profiles["profile_summary"]["contract_dimension_status"]),
            set(profiles["profile_summary"]["contract_dimensions"]),
        )
        self.assertTrue(
            all(
                status == "ready"
                for status in profiles["profile_summary"]["contract_dimension_status"].values()
            )
        )
        self.assertTrue(
            all(
                count == 0
                for count in profiles["profile_summary"]["missing_profile_count_by_contract_dimension"].values()
            )
        )
        self.assertEqual(
            set(profiles["profile_summary"]["missing_profiles_by_contract_dimension"]),
            set(profiles["profile_summary"]["contract_dimensions"]),
        )
        self.assertEqual(profiles["profile_summary"]["profiles_with_contract_gaps"], [])
        _assert_contract_ready(self, profiles["profile_summary"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_allowed_roots"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_allowed_root_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_allowed_roots"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_allowed_roots"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_permissions"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_permission_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_permissions"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_permissions"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_required_evidence"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_required_evidence_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_required_evidence"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_required_evidence"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_stop_conditions"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_stop_condition_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_stop_conditions"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_stop_conditions"])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_write_policy"], [])
        self.assertEqual(profiles["profile_summary"]["profiles_missing_write_policy_count"], 0)
        self.assertFalse(profiles["profile_summary"]["has_profiles_missing_write_policy"])
        self.assertTrue(profiles["profile_summary"]["all_profiles_have_write_policy"])
        self.assertEqual(
            profiles["profile_summary"]["required_evidence_count"],
            sum(profiles["profile_summary"]["required_evidence_count_by_profile"].values()),
        )
        self.assertEqual(
            sorted(profiles["profile_summary"]["write_policy_by_profile"]),
            sorted(profiles["profiles"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["write_policy_by_profile"]["live-mutation"],
            "explicit_request_required",
        )
        self.assertEqual(
            sorted(profiles["profile_summary"]["stop_conditions_by_profile"]),
            sorted(profiles["profiles"]),
        )
        self.assertEqual(
            sum(profiles["profile_summary"]["stop_condition_count_by_profile"].values()),
            profiles["profile_summary"]["stop_condition_count"],
        )
        self.assertIn(
            "unrelated dirty worktree",
            profiles["profile_summary"]["stop_conditions_by_profile"]["live-mutation"],
        )
        self.assertEqual(
            sorted(profiles["profile_summary"]["required_evidence_by_profile"]),
            sorted(profiles["profiles"]),
        )
        self.assertIn(
            "post-mutation validation",
            profiles["profile_summary"]["required_evidence_by_profile"]["live-mutation"],
        )
        self.assertTrue(profiles["profile_summary"]["has_taxonomy_stop_conditions"])
        self.assertIn("eval", profiles["profile_summary"]["profiles_with_taxonomy_stop_conditions"])
        self.assertIn("package-review", profiles["profile_summary"]["profiles_with_taxonomy_stop_conditions"])
        self.assertIn("authoring", profiles["profile_summary"]["profiles_without_taxonomy_stop_conditions"])
        self.assertEqual(
            profiles["profile_summary"]["profiles_with_taxonomy_stop_condition_count"],
            len(profiles["profile_summary"]["profiles_with_taxonomy_stop_conditions"]),
        )
        self.assertEqual(
            profiles["profile_summary"]["profiles_without_taxonomy_stop_condition_count"],
            len(profiles["profile_summary"]["profiles_without_taxonomy_stop_conditions"]),
        )
        self.assertTrue(profiles["profile_summary"]["has_profiles_without_taxonomy_stop_conditions"])
        self.assertFalse(profiles["profile_summary"]["all_profiles_have_taxonomy_stop_conditions"])
        self.assertIn(
            "blocked_user_input",
            profiles["profile_summary"]["taxonomy_stop_conditions_by_profile"]["eval"],
        )
        self.assertIn("live-mutation", profiles["profile_names"])
        self.assertIn("external_write_after_confirmation", profiles["profile_summary"]["by_permission"])
        self.assertEqual(
            sorted(profiles["profile_summary"]["permissions_by_profile"]),
            sorted(profiles["profiles"]),
        )
        self.assertEqual(
            sum(profiles["profile_summary"]["permission_count_by_profile"].values()),
            sum(len(profile["permissions"]) for profile in profiles["profiles"].values()),
        )
        self.assertIn(
            "external_write_after_confirmation",
            profiles["profile_summary"]["permissions_by_profile"]["live-mutation"],
        )
        self.assertEqual(
            sorted(profiles["profile_summary"]["allowed_roots_by_profile"]),
            sorted(profiles["profiles"]),
        )
        self.assertEqual(
            sum(profiles["profile_summary"]["allowed_root_count_by_profile"].values()),
            profiles["profile_summary"]["allowed_root_count"],
        )
        self.assertIn(
            "Infrastructure/artifacts/skill-reviews/**",
            profiles["profile_summary"]["allowed_roots_by_profile"]["package-review"],
        )
        self.assertEqual(sorted(profiles["event_coverage"]["events_by_profile"]), sorted(profiles["profiles"]))
        self.assertEqual(profiles["event_coverage"]["profile_count"], len(profiles["profiles"]))
        self.assertEqual(profiles["event_coverage"]["profile_names"], sorted(profiles["profiles"]))
        self.assertFalse(profiles["event_coverage"]["has_profiles_missing_events"])
        self.assertEqual(profiles["event_coverage"]["profiles_missing_events"], [])
        self.assertEqual(profiles["event_coverage"]["profiles_missing_event_count"], 0)
        self.assertTrue(profiles["event_coverage"]["all_profiles_have_events"])
        self.assertEqual(
            profiles["event_coverage"]["event_reference_count"],
            sum(profiles["event_coverage"]["event_count_by_profile"].values()),
        )
        self.assertEqual(
            profiles["event_coverage"]["profiles_with_events"],
            sorted(profiles["profiles"]),
        )
        self.assertEqual(
            profiles["event_coverage"]["profiles_with_event_count"],
            len(profiles["profiles"]),
        )
        self.assertGreaterEqual(profiles["event_coverage"]["event_count_by_profile"]["authoring"], 1)
        self.assertIn("projection_synced", profiles["event_coverage"]["events_by_profile"]["live-mutation"])
        self.assertEqual(profiles["event_coverage"]["profiles_with_event_gaps"], [])
        self.assertEqual(profiles["event_coverage"]["profiles_with_event_gap_count"], 0)
        _assert_contract_ready(self, profiles["event_coverage"])

    def test_skills_profiles_human_output(self):
        """Verify ask skills profiles has a useful non-JSON selected-profile render."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "package-review", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills profiles output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill profiles: pass", result.stdout)
        self.assertIn("Readiness: ready (0 gaps)", result.stdout)
        self.assertIn("Ready sections: lifecycle_event_coverage, profile_contracts", result.stdout)
        self.assertIn("Validation: ./bin/ask skills list --json --robot", result.stdout)
        self.assertIn("Profile: package-review", result.stdout)
        self.assertIn("Intent: Check a skill or plugin package before promotion.", result.stdout)
        self.assertIn("Write policy: reports_only_unless_fix_requested", result.stdout)

    def test_skills_profiles_command_blocks_unknown_profile(self):
        """Verify ask skills profiles fails closed for unknown operation modes."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "profiles", "unsafe-live-linear", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills profiles output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        profiles = output["data"]["skill_profiles"]
        self.assertEqual(profiles["status"], "blocked")
        self.assertEqual(profiles["requested_profile"], "unsafe-live-linear")
        self.assertIn("live-mutation", profiles["available_profiles"])

    def test_skills_events_command_returns_lifecycle_contract(self):
        """Verify ask skills events exposes the lifecycle event contract."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        events = output["data"]["skill_events"]
        self.assertEqual(events["schema_version"], "skill-events.v1")
        self.assertEqual(events["event_schema"], "capability-lifecycle-event.v1")
        self.assertEqual(events["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(events["contract_schemas"]["package"], "skill-package-readiness.v1")
        self.assertGreaterEqual(events["event_count"], 8)
        self.assertIn("eval_blocked", events["event_names"])
        self.assertIn("skill_loaded", events["available_event_types"])
        _assert_readiness_overview_ready(
            self,
            events["readiness_overview"],
            ["lifecycle_event_contract"],
        )
        self.assertEqual(
            events["readiness_overview"]["contract_sections"],
            {"lifecycle_event_contract": {"gap_count": 0, "ready": True, "status": "ready"}},
        )
        self.assertEqual(events["event_summary"]["event_count"], events["event_count"])
        self.assertEqual(
            events["event_summary"]["contract_dimensions"],
            ["known_profiles", "observer_commands", "producer_commands", "profiles"],
        )
        self.assertEqual(events["event_summary"]["contract_dimension_count"], 4)
        self.assertEqual(
            events["event_summary"]["contract_dimension_status"],
            {
                "known_profiles": "ready",
                "observer_commands": "ready",
                "producer_commands": "ready",
                "profiles": "ready",
            },
        )
        self.assertEqual(
            events["event_summary"]["missing_events_by_contract_dimension"],
            {
                "known_profiles": [],
                "observer_commands": [],
                "producer_commands": [],
                "profiles": [],
            },
        )
        self.assertEqual(
            events["event_summary"]["missing_event_count_by_contract_dimension"],
            {
                "known_profiles": 0,
                "observer_commands": 0,
                "producer_commands": 0,
                "profiles": 0,
            },
        )
        self.assertGreaterEqual(events["event_summary"]["producer_command_count"], events["event_count"])
        self.assertGreaterEqual(events["event_summary"]["observer_command_count"], events["event_count"])
        self.assertEqual(
            sorted(events["event_summary"]["producer_command_count_by_event"]),
            sorted(events["event_consumers"]),
        )
        self.assertEqual(
            events["event_summary"]["producer_command_count_by_event"]["eval_completed"],
            len(events["event_consumers"]["eval_completed"]["producer_commands"]),
        )
        self.assertEqual(
            events["event_summary"]["observer_command_count_by_event"]["projection_synced"],
            len(events["event_consumers"]["projection_synced"]["observer_commands"]),
        )
        self.assertGreaterEqual(events["event_summary"]["by_profile"]["eval"], 1)
        self.assertIn("eval_blocked", events["event_summary"]["events_by_profile"]["eval"])
        self.assertIn("projection_synced", events["event_summary"]["events_by_profile"]["live-mutation"])
        self.assertEqual(
            events["event_summary"]["event_count_by_profile"]["eval"],
            len(events["event_summary"]["events_by_profile"]["eval"]),
        )
        self.assertEqual(
            events["event_summary"]["profiles_by_event"]["eval_blocked"],
            events["event_consumers"]["eval_blocked"]["profiles"],
        )
        self.assertEqual(
            events["event_summary"]["profile_count_by_event"]["manifest_changed"],
            len(events["event_consumers"]["manifest_changed"]["profiles"]),
        )
        self.assertEqual(events["event_summary"]["profile_count"], len(events["event_summary"]["by_profile"]))
        self.assertEqual(events["event_summary"]["profile_names"], sorted(events["event_summary"]["by_profile"]))
        self.assertIn("eval", events["event_summary"]["profile_names"])
        self.assertTrue(events["event_summary"]["has_profiles"])
        self.assertFalse(events["event_summary"]["has_missing_producers"])
        self.assertFalse(events["event_summary"]["has_missing_observers"])
        self.assertFalse(events["event_summary"]["has_missing_profiles"])
        self.assertFalse(events["event_summary"]["has_unknown_profiles"])
        self.assertEqual(events["event_summary"]["events_missing_producers"], [])
        self.assertEqual(events["event_summary"]["events_missing_observers"], [])
        self.assertEqual(events["event_summary"]["events_missing_profiles"], [])
        self.assertEqual(events["event_summary"]["events_missing_profile_count"], 0)
        self.assertEqual(events["event_summary"]["events_with_unknown_profile_count"], 0)
        self.assertEqual(events["event_summary"]["unknown_profile_reference_count"], 0)
        self.assertEqual(events["event_summary"]["events_with_unknown_profiles"], {})
        self.assertEqual(events["event_summary"]["profiles_unknown_to_registry"], [])
        self.assertEqual(events["event_summary"]["known_profile_count"], len(events["event_summary"]["known_profile_names"]))
        self.assertEqual(events["event_summary"]["referenced_profile_count"], len(events["event_summary"]["referenced_profile_names"]))
        self.assertEqual(
            sorted(events["event_summary"]["known_events_by_profile"]),
            events["event_summary"]["known_profile_names"],
        )
        self.assertEqual(
            events["event_summary"]["known_event_count_by_profile"]["eval"],
            len(events["event_summary"]["known_events_by_profile"]["eval"]),
        )
        self.assertEqual(events["event_summary"]["known_profiles_with_events"], events["event_summary"]["known_profile_names"])
        self.assertEqual(
            events["event_summary"]["known_profile_event_coverage_count"],
            events["event_summary"]["known_profile_count"],
        )
        self.assertTrue(events["event_summary"]["all_known_profiles_have_events"])
        self.assertEqual(events["event_summary"]["known_profiles_without_events"], [])
        self.assertFalse(events["event_summary"]["has_known_profiles_without_events"])
        self.assertIn("live-mutation", events["event_summary"]["known_profile_names"])
        self.assertIn("live-mutation", events["event_summary"]["referenced_profile_names"])
        self.assertEqual(events["event_summary"]["events_with_contract_gaps"], [])
        _assert_contract_ready(self, events["event_summary"])
        self.assertIn("./bin/ask skills events --json --robot", events["validation_commands"])
        self.assertIn("eval_blocked", events["event_types"])
        self.assertIn("eval", events["event_consumers"]["eval_blocked"]["profiles"])
        self.assertIn("./bin/ask skills prove <handle> --json --robot", events["event_consumers"]["eval_completed"]["producer_commands"])
        self.assertEqual(
            events["event_consumers"]["projection_synced"]["producer_commands"],
            ["./bin/ask skills sync --json --robot"],
        )
        self.assertEqual(
            events["event_consumers"]["manifest_changed"]["producer_commands"],
            ["./bin/ask skills sync --scope workspace --projection flat --json --robot"],
        )
        self.assertEqual(
            events["event_consumers"]["projection_synced"]["observer_commands"],
            ["./bin/ask skills list --json --robot"],
        )
        self.assertIn("blocked_user_input", events["eval_blocker_classes"])
        self.assertIn("blocked_runtime", events["eval_blocker_classes"])
        self.assertIn("timeout_partial_output", events["eval_blocker_classes"])
        self.assertEqual(events["blocker_taxonomy"]["blocked_auth"], events["eval_blocker_classes"]["blocked_auth"])
        self.assertIn("strict_audit_not_run", events["warning_taxonomy"])
        self.assertIn("skill_doctor_completed", events["event_order"])
        self.assertEqual(events["selected_event_type"], None)

    def test_skills_events_command_returns_selected_event(self):
        """Verify ask skills events can narrow to a single event type."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "eval_blocked", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events failed: {result.stderr}")
        output = json.loads(result.stdout)
        events = output["data"]["skill_events"]
        self.assertEqual(events["selected_event_type"], "eval_blocked")
        self.assertEqual(events["event_names"], ["eval_blocked"])
        self.assertIn("eval_completed", events["available_event_types"])
        _assert_readiness_overview_ready(
            self,
            events["readiness_overview"],
            ["lifecycle_event_contract"],
        )
        self.assertEqual(
            events["readiness_overview"]["contract_sections"]["lifecycle_event_contract"]["status"],
            events["event_summary"]["contract_status"],
        )
        self.assertEqual(events["event_summary"]["event_count"], 1)
        self.assertEqual(
            events["event_summary"]["contract_dimensions"],
            ["known_profiles", "observer_commands", "producer_commands", "profiles"],
        )
        self.assertEqual(events["event_summary"]["contract_dimension_count"], 4)
        self.assertEqual(
            events["event_summary"]["contract_dimension_status"],
            {
                "known_profiles": "ready",
                "observer_commands": "ready",
                "producer_commands": "ready",
                "profiles": "ready",
            },
        )
        self.assertEqual(
            events["event_summary"]["missing_events_by_contract_dimension"],
            {
                "known_profiles": [],
                "observer_commands": [],
                "producer_commands": [],
                "profiles": [],
            },
        )
        self.assertEqual(
            events["event_summary"]["missing_event_count_by_contract_dimension"],
            {
                "known_profiles": 0,
                "observer_commands": 0,
                "producer_commands": 0,
                "profiles": 0,
            },
        )
        self.assertEqual(events["event_summary"]["producer_command_count"], 1)
        self.assertEqual(events["event_summary"]["observer_command_count"], 1)
        self.assertEqual(events["event_summary"]["producer_command_count_by_event"], {"eval_blocked": 1})
        self.assertEqual(events["event_summary"]["observer_command_count_by_event"], {"eval_blocked": 1})
        self.assertEqual(events["event_summary"]["profile_names"], ["eval"])
        self.assertEqual(events["event_summary"]["profile_count"], 1)
        self.assertEqual(events["event_summary"]["events_by_profile"], {"eval": ["eval_blocked"]})
        self.assertEqual(events["event_summary"]["event_count_by_profile"], {"eval": 1})
        self.assertEqual(events["event_summary"]["profiles_by_event"], {"eval_blocked": ["eval"]})
        self.assertEqual(events["event_summary"]["profile_count_by_event"], {"eval_blocked": 1})
        self.assertFalse(events["event_summary"]["has_missing_producers"])
        self.assertFalse(events["event_summary"]["has_missing_observers"])
        self.assertFalse(events["event_summary"]["has_missing_profiles"])
        self.assertFalse(events["event_summary"]["has_unknown_profiles"])
        self.assertEqual(events["event_summary"]["events_missing_profile_count"], 0)
        self.assertEqual(events["event_summary"]["events_with_unknown_profile_count"], 0)
        self.assertEqual(events["event_summary"]["unknown_profile_reference_count"], 0)
        self.assertEqual(events["event_summary"]["events_with_unknown_profiles"], {})
        self.assertEqual(events["event_summary"]["profiles_unknown_to_registry"], [])
        self.assertEqual(events["event_summary"]["known_profile_count"], 5)
        self.assertIn("live-mutation", events["event_summary"]["known_profile_names"])
        self.assertEqual(events["event_summary"]["known_events_by_profile"]["eval"], ["eval_blocked"])
        self.assertEqual(events["event_summary"]["known_events_by_profile"]["live-mutation"], [])
        self.assertEqual(events["event_summary"]["known_event_count_by_profile"]["live-mutation"], 0)
        self.assertEqual(events["event_summary"]["known_profiles_with_events"], ["eval"])
        self.assertEqual(events["event_summary"]["known_profile_event_coverage_count"], 1)
        self.assertFalse(events["event_summary"]["all_known_profiles_have_events"])
        self.assertEqual(events["event_summary"]["referenced_profile_names"], ["eval"])
        self.assertIn("live-mutation", events["event_summary"]["known_profiles_without_events"])
        self.assertTrue(events["event_summary"]["has_known_profiles_without_events"])
        self.assertEqual(events["event_summary"]["events_with_contract_gaps"], [])
        _assert_contract_ready(self, events["event_summary"])
        self.assertEqual(list(events["event_types"]), ["eval_blocked"])
        self.assertEqual(list(events["event_consumers"]), ["eval_blocked"])
        self.assertEqual(events["contract_schemas"]["events"], "skill-events.v1")
        self.assertIn("blocker", events["event_types"]["eval_blocked"])
        self.assertIn("eval", events["event_consumers"]["eval_blocked"]["profiles"])
        self.assertIn("blocked_auth", events["eval_blocker_classes"])

    def test_skills_events_summary_flags_unknown_profiles(self):
        """Verify event summaries fail closed on undeclared profile references."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills_impl import _skill_event_summary

            summary = _skill_event_summary(
                {
                    "unsafe_event": {
                        "profiles": ["ghost-profile"],
                        "producer_commands": ["ask unsafe"],
                        "observer_commands": ["ask events unsafe_event"],
                    }
                },
                {"eval": {"intent": "Run evidence."}},
            )
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(summary["events_with_unknown_profiles"], {"unsafe_event": ["ghost-profile"]})
        self.assertEqual(
            summary["contract_dimensions"],
            ["known_profiles", "observer_commands", "producer_commands", "profiles"],
        )
        self.assertEqual(summary["contract_dimension_count"], 4)
        self.assertEqual(
            summary["contract_dimension_status"],
            {
                "known_profiles": "has_gaps",
                "observer_commands": "ready",
                "producer_commands": "ready",
                "profiles": "ready",
            },
        )
        self.assertEqual(
            summary["missing_events_by_contract_dimension"],
            {
                "known_profiles": ["unsafe_event"],
                "observer_commands": [],
                "producer_commands": [],
                "profiles": [],
            },
        )
        self.assertEqual(
            summary["missing_event_count_by_contract_dimension"],
            {
                "known_profiles": 1,
                "observer_commands": 0,
                "producer_commands": 0,
                "profiles": 0,
            },
        )
        self.assertEqual(summary["profiles_unknown_to_registry"], ["ghost-profile"])
        self.assertTrue(summary["has_unknown_profiles"])
        self.assertEqual(summary["events_missing_profile_count"], 0)
        self.assertEqual(summary["events_with_unknown_profile_count"], 1)
        self.assertEqual(summary["unknown_profile_reference_count"], 1)
        self.assertEqual(summary["known_profile_names"], ["eval"])
        self.assertEqual(summary["referenced_profile_names"], ["ghost-profile"])
        self.assertEqual(summary["known_events_by_profile"], {"eval": []})
        self.assertEqual(summary["known_event_count_by_profile"], {"eval": 0})
        self.assertEqual(summary["known_profiles_with_events"], [])
        self.assertEqual(summary["known_profile_event_coverage_count"], 0)
        self.assertFalse(summary["all_known_profiles_have_events"])
        self.assertEqual(summary["producer_command_count_by_event"], {"unsafe_event": 1})
        self.assertEqual(summary["observer_command_count_by_event"], {"unsafe_event": 1})
        self.assertEqual(summary["events_by_profile"], {"ghost-profile": ["unsafe_event"]})
        self.assertEqual(summary["event_count_by_profile"], {"ghost-profile": 1})
        self.assertEqual(summary["profiles_by_event"], {"unsafe_event": ["ghost-profile"]})
        self.assertEqual(summary["profile_count_by_event"], {"unsafe_event": 1})
        self.assertEqual(summary["known_profiles_without_events"], ["eval"])
        self.assertTrue(summary["has_known_profiles_without_events"])
        self.assertEqual(summary["events_with_contract_gaps"], ["unsafe_event"])
        self.assertEqual(summary["contract_gap_count"], 1)
        self.assertTrue(summary["has_contract_gaps"])
        self.assertEqual(summary["contract_status"], "has_gaps")
        self.assertFalse(summary["contract_ready"])

    def test_skills_readiness_overviews_flag_blocked_sections(self):
        """Verify readiness overview helpers expose blocked sections directly."""
        lib_path = str(Path.cwd() / "Infrastructure" / "scripts" / "lib")
        sys.path.insert(0, lib_path)
        try:
            from ask.commands.skills_impl import (
                _skill_events_readiness_overview,
                _skill_profiles_readiness_overview,
            )

            profile_overview = _skill_profiles_readiness_overview(
                {
                    "contract_status": "ready",
                    "contract_ready": True,
                    "contract_gap_count": 0,
                },
                {
                    "contract_status": "has_gaps",
                    "contract_ready": False,
                    "contract_gap_count": 2,
                },
            )
            event_overview = _skill_events_readiness_overview(
                {
                    "contract_status": "has_gaps",
                    "contract_ready": False,
                    "contract_gap_count": 1,
                    "has_contract_gaps": True,
                }
            )
            empty_event_overview = _skill_events_readiness_overview(
                {
                    "contract_status": "empty",
                    "contract_ready": False,
                    "contract_gap_count": 0,
                    "has_contract_gaps": False,
                }
            )
        finally:
            sys.path.remove(lib_path)

        self.assertEqual(profile_overview["contract_status"], "has_gaps")
        self.assertFalse(profile_overview["contract_ready"])
        self.assertTrue(profile_overview["has_contract_gaps"])
        self.assertEqual(profile_overview["contract_gap_count"], 2)
        self.assertEqual(profile_overview["ready_contract_sections"], ["profile_contracts"])
        self.assertEqual(profile_overview["blocked_contract_sections"], ["lifecycle_event_coverage"])
        self.assertEqual(
            profile_overview["contract_status_by_section"],
            {"lifecycle_event_coverage": "has_gaps", "profile_contracts": "ready"},
        )
        self.assertEqual(
            profile_overview["contract_gap_count_by_section"],
            {"lifecycle_event_coverage": 2, "profile_contracts": 0},
        )
        self.assertEqual(event_overview["contract_status"], "has_gaps")
        self.assertFalse(event_overview["contract_ready"])
        self.assertTrue(event_overview["has_contract_gaps"])
        self.assertEqual(event_overview["contract_gap_count"], 1)
        self.assertEqual(event_overview["ready_contract_sections"], [])
        self.assertEqual(event_overview["blocked_contract_sections"], ["lifecycle_event_contract"])
        self.assertEqual(
            event_overview["contract_status_by_section"],
            {"lifecycle_event_contract": "has_gaps"},
        )
        self.assertEqual(
            event_overview["contract_gap_count_by_section"],
            {"lifecycle_event_contract": 1},
        )
        self.assertEqual(empty_event_overview["contract_status"], "empty")
        self.assertFalse(empty_event_overview["contract_ready"])
        self.assertFalse(empty_event_overview["has_contract_gaps"])
        self.assertEqual(empty_event_overview["contract_gap_count"], 0)
        self.assertEqual(empty_event_overview["ready_contract_sections"], [])
        self.assertEqual(empty_event_overview["blocked_contract_sections"], ["lifecycle_event_contract"])

    def test_skills_events_human_output(self):
        """Verify ask skills events has a useful non-JSON selected-event render."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "eval_blocked", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills events output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill events: pass", result.stdout)
        self.assertIn("Readiness: ready (0 gaps)", result.stdout)
        self.assertIn("Ready sections: lifecycle_event_contract", result.stdout)
        self.assertIn("Validation: ./bin/ask skills events --json --robot", result.stdout)
        self.assertIn("Event: eval_blocked", result.stdout)
        self.assertIn("Definition:", result.stdout)

    def test_skills_events_command_blocks_unknown_event(self):
        """Verify ask skills events fails closed for unknown event types."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "events", "made_up_event", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills events output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        events = output["data"]["skill_events"]
        self.assertEqual(events["status"], "blocked")
        self.assertEqual(events["requested_event_type"], "made_up_event")
        self.assertIn("eval_blocked", events["available_event_types"])

    def test_skills_memory_search_command_returns_provider_entries(self):
        """Verify ask skills memory search exposes provenance-bearing entries."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "search", "projection", "--limit", "3", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory search failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["schema_version"], "skill-memory-provider.v1")
        self.assertEqual(memory["provider_model"], "extension-like-read-only")
        self.assertEqual(memory["contract_schemas"]["memory"], "skill-memory-provider.v1")
        self.assertEqual(memory["contract_schemas"]["profiles"], "skill-operation-profiles.v1")
        self.assertEqual(memory["operation_context"]["provider_model"], "extension-like-read-only")
        self.assertEqual(memory["operation_context"]["provider_contract"]["mutation_policy"], "read_only")
        self.assertIn("provenance", memory["operation_context"]["provider_contract"]["required_entry_fields"])
        self.assertIn("eval", memory["operation_context"]["consumer_profiles"])
        self.assertIn("./bin/ask memory search projection --json --robot", memory["operation_context"]["validation_commands"])
        self.assertGreaterEqual(memory["source_summary"]["source_count"], 1)
        self.assertEqual(memory["mode"], "search")
        self.assertGreaterEqual(memory["entry_count"], 1)
        self.assertEqual(memory["entry_summary"]["returned_count"], memory["entry_count"])
        self.assertGreaterEqual(memory["entry_summary"]["total_count"], memory["entry_count"])
        self.assertIn("provenance", memory["entries"][0])
        self.assertIn("freshness", memory["entries"][0])

    def test_skills_memory_human_output_exposes_provider_contract(self):
        """Verify ask skills memory human output names the provider model and sources."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "search",
            "projection",
            "--limit",
            "3",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skill memory: search (pass)", result.stdout)
        self.assertIn("Provider: extension-like-read-only", result.stdout)
        self.assertIn("Validation: ./bin/ask skills memory search projection --json --robot", result.stdout)
        self.assertIn("Sources:", result.stdout)
        self.assertIn("docs-agent-guidance", result.stdout)

    def test_skills_memory_search_command_blocks_missing_query(self):
        """Verify ask skills memory search requires a query from the CLI path."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "search", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "search")
        self.assertIn("requires a non-empty query", memory["agent_summary"])

    def test_skills_memory_search_command_blocks_negative_limit(self):
        """Verify ask skills memory search rejects negative limits."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "search",
            "projection",
            "--limit",
            "-1",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "search")
        self.assertIn("limit must be non-negative", memory["agent_summary"])

    def test_skills_memory_list_source_filter_limits_entries(self):
        """Verify ask skills memory list preserves provider source filtering."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "list",
            "--source",
            "harness-solutions",
            "--limit",
            "2",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["entry_count"], 2)
        self.assertGreaterEqual(memory["total_count"], 2)
        self.assertIn("./bin/ask skills memory search <query> --json --robot", memory["operation_context"]["follow_up_commands"])
        self.assertTrue(all(entry["source_id"] == "harness-solutions" for entry in memory["entries"]))

    def test_skills_memory_read_command_returns_content_and_provenance(self):
        """Verify ask skills memory read exposes durable content with provenance."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "memory",
            "read",
            ".harness/memory/LEARNINGS.md",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"skills memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["mode"], "read")
        entry = memory["entry"]
        self.assertEqual(entry["path"], ".harness/memory/LEARNINGS.md")
        self.assertEqual(entry["provenance"]["provider"], "harness-memory")
        self.assertIn("# Learnings", entry["content"])

    def test_skills_memory_read_command_blocks_missing_identifier(self):
        """Verify ask skills memory read fails closed without an entry id."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "memory", "read", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"skills memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["skill_memory"]
        self.assertEqual(memory["status"], "blocked")
        self.assertEqual(memory["mode"], "read")
        self.assertIn("requires an entry id", memory["agent_summary"])

    def test_evals_missing_action_exposes_validation(self):
        """Verify incomplete eval commands expose the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "evals", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"evals output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask evals dashboard --json --robot"])

    def test_evals_missing_action_human_output_exposes_validation(self):
        """Verify incomplete eval commands render the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "evals", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"evals output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'evals'", result.stdout)
        self.assertIn("Validation: ./bin/ask evals dashboard --json --robot", result.stdout)

    def test_evals_closeout_doctor_human_output_renders_result(self):
        """Verify evals closeout doctor prints its non-JSON result."""
        with tempfile.TemporaryDirectory() as tmp:
            closeout_path = _write_pass_closeout(tmp)
            cmd = [
                "python3",
                "Infrastructure/bin/ask",
                "evals",
                "closeout",
                "doctor",
                str(closeout_path),
                "--robot",
            ]
            result = _run_cli(cmd, cwd=REPO_ROOT)

        self.assertEqual(result.returncode, 0, f"closeout doctor output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Eval closeout doctor: pass", result.stdout)
        self.assertIn("Validation: pass", result.stdout)
        self.assertIn("Validation: ./bin/ask evals closeout doctor", result.stdout)

    def test_mcp_sync_dry_run_json_contract_exposes_validation(self):
        """Verify MCP sync dry-run exposes its replay command without writing config."""
        cmd = ["python3", "Infrastructure/bin/ask", "mcp", "sync", "--dry-run", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"mcp sync output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"]["dry_run"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask mcp sync --dry-run --json --robot"],
        )

    def test_mcp_sync_dry_run_human_output_exposes_validation(self):
        """Verify MCP sync dry-run human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "mcp", "sync", "--dry-run", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"mcp sync output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Dry run - would sync", result.stdout)
        self.assertIn("Validation: ./bin/ask mcp sync --dry-run --json --robot", result.stdout)

    def test_mcp_missing_action_exposes_validation(self):
        """Verify incomplete MCP commands expose the safe dry-run recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "mcp", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"mcp output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask mcp sync --dry-run --json --robot"],
        )

    def test_mcp_missing_action_human_output_exposes_validation(self):
        """Verify incomplete MCP commands render the safe recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "mcp", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"mcp output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'mcp'", result.stdout)
        self.assertIn("Validation: ./bin/ask mcp sync --dry-run --json --robot", result.stdout)

    def test_wiki_lint_json_contract_exposes_validation(self):
        """Verify wiki lint exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "lint", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki lint output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask wiki lint --wiki-root Wiki/wiki --max-age-days 60 --json --robot"],
        )

    def test_wiki_lint_human_output_exposes_validation(self):
        """Verify wiki lint human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "lint", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki lint output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Wiki lint passed.", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask wiki lint --wiki-root Wiki/wiki --max-age-days 60 --json --robot",
            result.stdout,
        )

    def test_wiki_query_json_contract_exposes_validation(self):
        """Verify wiki query exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "query", "skill", "--limit", "1", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki query output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["query"], "skill")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask wiki query skill --wiki-root Wiki/wiki --limit 1 --json --robot"],
        )

    def test_wiki_query_human_output_exposes_validation(self):
        """Verify wiki query human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "query", "skill", "--limit", "1", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki query output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Found 1 matching wiki page(s).", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask wiki query skill --wiki-root Wiki/wiki --limit 1 --json --robot",
            result.stdout,
        )

    def test_wiki_ingest_dry_run_json_contract_exposes_validation(self):
        """Verify wiki ingest dry-run exposes its replay command without writing."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "ingest",
            "Capability Readiness Note",
            "--source",
            "heartbeat:test",
            "--summary",
            "Dry-run readiness evidence for wiki ingest.",
            "--tag",
            "readiness",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki ingest output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"]["dry_run"])
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask wiki ingest 'Capability Readiness Note' --source heartbeat:test "
                "--summary 'Dry-run readiness evidence for wiki ingest.' --tag readiness --dry-run --json --robot"
            ],
        )

    def test_wiki_ingest_dry_run_human_output_exposes_validation(self):
        """Verify wiki ingest dry-run human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "ingest",
            "Capability Readiness Note",
            "--source",
            "heartbeat:test",
            "--summary",
            "Dry-run readiness evidence for wiki ingest.",
            "--tag",
            "readiness",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"wiki ingest output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Dry run - would ingest:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask wiki ingest 'Capability Readiness Note' --source heartbeat:test "
            "--summary 'Dry-run readiness evidence for wiki ingest.' --tag readiness --dry-run --json --robot",
            result.stdout,
        )

    def test_wiki_add_json_contract_exposes_validation(self):
        """Verify wiki add exposes its replay command even when dependencies block."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "add",
            "Capability Readiness Finding",
            "--summary",
            "Dry-run readiness evidence for wiki add.",
            "--source",
            "heartbeat:test",
            "--intent",
            "finding",
            "--status",
            "needs-verification",
            "--destination",
            "failures",
            "--tag",
            "readiness",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"wiki add output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask wiki add 'Capability Readiness Finding' "
                "--summary 'Dry-run readiness evidence for wiki add.' --source heartbeat:test "
                "--intent finding --status needs-verification --destination failures "
                "--tag readiness --dry-run --json --robot"
            ],
        )

    def test_wiki_add_human_output_exposes_validation(self):
        """Verify wiki add human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "add",
            "Capability Readiness Finding",
            "--summary",
            "Dry-run readiness evidence for wiki add.",
            "--source",
            "heartbeat:test",
            "--intent",
            "finding",
            "--status",
            "needs-verification",
            "--destination",
            "failures",
            "--tag",
            "readiness",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"wiki add output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn(
            "Validation: ./bin/ask wiki add 'Capability Readiness Finding' "
            "--summary 'Dry-run readiness evidence for wiki add.' --source heartbeat:test "
            "--intent finding --status needs-verification --destination failures "
            "--tag readiness --dry-run --json --robot",
            result.stdout,
        )

    def test_wiki_add_asset_json_contract_exposes_validation(self):
        """Verify wiki add-asset exposes its replay command even when dependencies block."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "add-asset",
            "Wiki/wiki/playbooks/code-scanning-remediation.md",
            "--title",
            "Capability Readiness Asset",
            "--summary",
            "Dry-run readiness evidence for wiki asset add.",
            "--source",
            "heartbeat:test",
            "--status",
            "verified",
            "--destination",
            "assets/ui",
            "--tag",
            "readiness",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"wiki add-asset output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask wiki add-asset Wiki/wiki/playbooks/code-scanning-remediation.md "
                "--title 'Capability Readiness Asset' "
                "--summary 'Dry-run readiness evidence for wiki asset add.' --source heartbeat:test "
                "--status verified --destination assets/ui --tag readiness --dry-run --json --robot"
            ],
        )

    def test_wiki_add_asset_human_output_exposes_validation(self):
        """Verify wiki add-asset human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "wiki",
            "add-asset",
            "Wiki/wiki/playbooks/code-scanning-remediation.md",
            "--title",
            "Capability Readiness Asset",
            "--summary",
            "Dry-run readiness evidence for wiki asset add.",
            "--source",
            "heartbeat:test",
            "--status",
            "verified",
            "--destination",
            "assets/ui",
            "--tag",
            "readiness",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"wiki add-asset output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn(
            "Validation: ./bin/ask wiki add-asset Wiki/wiki/playbooks/code-scanning-remediation.md "
            "--title 'Capability Readiness Asset' "
            "--summary 'Dry-run readiness evidence for wiki asset add.' --source heartbeat:test "
            "--status verified --destination assets/ui --tag readiness --dry-run --json --robot",
            result.stdout,
        )

    def test_wiki_add_missing_fields_json_contract_exposes_validation(self):
        """Verify wiki add missing-field errors expose their replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "add", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki add output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIn("Missing required fields for wiki add", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask wiki add --json --robot"])

    def test_wiki_add_missing_fields_human_output_exposes_validation(self):
        """Verify wiki add missing-field human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "add", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki add output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Missing required fields for wiki add", result.stdout)
        self.assertIn("Validation: ./bin/ask wiki add --json --robot", result.stdout)

    def test_wiki_add_asset_missing_fields_json_contract_exposes_validation(self):
        """Verify wiki add-asset missing-field errors expose their replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "add-asset", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki add-asset output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIn("Missing required fields for wiki add-asset", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask wiki add-asset --status verified --destination assets/ui --json --robot"],
        )

    def test_wiki_add_asset_missing_fields_human_output_exposes_validation(self):
        """Verify wiki add-asset missing-field human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "add-asset", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki add-asset output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Missing required fields for wiki add-asset", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask wiki add-asset --status verified --destination assets/ui --json --robot",
            result.stdout,
        )

    def test_wiki_missing_action_exposes_validation(self):
        """Verify incomplete wiki commands expose the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask wiki lint --json --robot"])

    def test_wiki_missing_action_human_output_exposes_validation(self):
        """Verify incomplete wiki commands render the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "wiki", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"wiki output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'wiki'", result.stdout)
        self.assertIn("Validation: ./bin/ask wiki lint --json --robot", result.stdout)

    def test_memory_search_command_returns_provider_entries(self):
        """Verify ask memory search exposes the same provenance-bearing provider entries."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "search", "projection", "--limit", "1", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory search failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        memory = output["data"]["memory"]
        self.assertEqual(memory["schema_version"], "memory-provider.v1")
        self.assertEqual(memory["count"], 1)
        entry = memory["results"][0]
        self.assertEqual(entry["provenance"]["provider"], entry["source_id"])
        self.assertEqual(entry["provenance"]["repo_relative_path"], entry["path"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask memory search projection --limit 1 --json --robot"],
        )

    def test_memory_search_human_output_lists_entry_paths(self):
        """Verify ask memory search has a useful non-JSON provider render."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "search", "projection", "--limit", "1", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Found 1 memory entry.", result.stdout)
        self.assertIn("docs-agent-guidance:docs-agents-04-validation-md", result.stdout)
        self.assertIn("Docs/agents/04-validation.md", result.stdout)
        self.assertIn("Validation: ./bin/ask memory search projection --limit 1 --json --robot", result.stdout)

    def test_memory_list_source_filter_limits_entries(self):
        """Verify ask memory list honors source filtering from the CLI path."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "memory",
            "list",
            "--source",
            "harness-solutions",
            "--limit",
            "2",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["memory"]
        self.assertEqual(memory["count"], 2)
        self.assertGreaterEqual(memory["total_count"], 2)
        self.assertTrue(all(entry["source_id"] == "harness-solutions" for entry in memory["entries"]))
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask memory list --source harness-solutions --limit 2 --json --robot"],
        )

    def test_memory_list_command_blocks_negative_limit(self):
        """Verify ask memory list rejects negative limits."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "list", "--limit", "-1", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("limit must be non-negative", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask memory list --limit -1 --json --robot"])

    def test_memory_read_command_returns_content_and_provenance(self):
        """Verify ask memory read exposes durable content with provenance."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "memory",
            "read",
            ".harness/memory/LEARNINGS.md",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        memory = output["data"]["memory"]
        entry = memory["entry"]
        self.assertEqual(entry["path"], ".harness/memory/LEARNINGS.md")
        self.assertEqual(entry["provenance"]["provider"], "harness-memory")
        self.assertIn("# Learnings", entry["content"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask memory read .harness/memory/LEARNINGS.md --json --robot"],
        )

    def test_memory_read_command_blocks_missing_identifier(self):
        """Verify ask memory read parser reports the missing identifier clearly."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "read", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory read output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("arguments are required: identifier", output["errors"][0]["message"])
        self.assertIn("ask memory read .harness/memory/LEARNINGS.md --json", output["errors"][0]["message"])

    def test_memory_command_blocks_missing_action(self):
        """Verify ask memory fails closed when no provider mode is selected."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask memory list --json --robot"])

    def test_memory_missing_action_human_output_exposes_validation(self):
        """Verify incomplete memory commands render the recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "memory", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"memory output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'memory'", result.stdout)
        self.assertIn("Validation: ./bin/ask memory list --json --robot", result.stdout)

    def test_plugins_list_state(self):
        """CA1: Verify ask plugins list returns lifecycle state groups."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "list", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins list failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("installed_state", output["data"])
        self.assertIn("activation_state", output["data"])
        self.assertIn("health_state", output["data"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask plugins list --json --robot"])

    def test_plugins_list_human_output_exposes_validation(self):
        """Verify plugins list human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "list", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins list failed: {result.stderr}")
        self.assertIn("Plugins installed:", result.stdout)
        self.assertIn("Validation: ./bin/ask plugins list --json --robot", result.stdout)

    def test_plugins_missing_action_exposes_validation(self):
        """Verify incomplete plugin commands expose the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"plugins output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask plugins list --json --robot"])

    def test_plugins_missing_action_human_output_exposes_validation(self):
        """Verify incomplete plugin commands render the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"plugins output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'plugins'", result.stdout)
        self.assertIn("Validation: ./bin/ask plugins list --json --robot", result.stdout)

    def test_plugins_status_json_contract_exposes_validation(self):
        """Verify plugin status exposes its scoped replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "status",
            "harness-engineering",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins status failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask plugins status harness-engineering --json --robot"],
        )

    def test_plugins_doctor_json_contract_exposes_validation(self):
        """Verify plugin doctor exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "doctor", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertIn(result.returncode, {0, 2}, f"plugins doctor failed: {result.stderr}")
        output = json.loads(result.stdout)
        if result.returncode == 0:
            self.assertEqual(output["status"], "success")
            self.assertEqual(output["data"]["validation_commands"], ["./bin/ask plugins doctor --json --robot"])
        else:
            self.assertEqual(output["status"], "error")

    def test_plugins_sync_local_runtime_dry_run_exposes_validation(self):
        """Verify plugin runtime sync dry-run exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "sync-local-runtime",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins sync-local-runtime failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"]["dry_run"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask plugins sync-local-runtime --dry-run --json --robot"],
        )

    def test_plugins_sync_local_runtime_human_output_exposes_validation(self):
        """Verify plugin runtime sync dry-run human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "sync-local-runtime",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins sync-local-runtime failed: {result.stderr}")
        self.assertIn("Dry run - would replace local-plugin runtime mirrors", result.stdout)
        self.assertIn("Validation: ./bin/ask plugins sync-local-runtime --dry-run --json --robot", result.stdout)

    def test_plugins_harden_success_human_output_exposes_validation(self):
        """Verify plugin harden success output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "harden",
            "Plugins/harness-engineering",
            "--skip-compat",
            "--skip-marketplace-audit",
            "--no-require-marketplace",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins harden failed: {result.stderr}")
        self.assertIn("Hardened plugin 'harness-engineering'", result.stdout)
        self.assertIn("Checks run:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins harden Plugins/harness-engineering --skip-compat "
            "--skip-marketplace-audit --no-require-marketplace --json --robot",
            result.stdout,
        )

    def test_plugins_install_dry_run_human_output_exposes_validation(self):
        """Verify plugin install dry-run human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "install",
            "https://github.com/example/repo",
            "--path",
            "Plugins/demo-plugin",
            "--name",
            "demo-plugin",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins install dry-run failed: {result.stderr}")
        self.assertIn("Dry run - would install plugin", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins install https://github.com/example/repo "
            "--path Plugins/demo-plugin --name demo-plugin --dry-run --json --robot",
            result.stdout,
        )

    def test_plugins_install_validation_error_exposes_validation(self):
        """Verify plugin install validation errors expose a replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "install",
            "https://github.com/example/repo",
            "--path",
            "Plugins/demo-plugin",
            "--dest",
            "/tmp/not-a-plugin-dest",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask plugins install https://github.com/example/repo "
                "--path Plugins/demo-plugin --dest /tmp/not-a-plugin-dest --json --robot"
            ],
        )

    def test_plugins_install_validation_error_human_output_exposes_validation(self):
        """Verify plugin install validation errors render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "install",
            "https://github.com/example/repo",
            "--path",
            "Plugins/demo-plugin",
            "--dest",
            "/tmp/not-a-plugin-dest",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid plugin destination", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins install https://github.com/example/repo "
            "--path Plugins/demo-plugin --dest /tmp/not-a-plugin-dest --json --robot",
            result.stdout,
        )

    def test_plugins_uninstall_dry_run_json_contract_exposes_validation(self):
        """Verify plugin uninstall dry-run exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "uninstall",
            "harness-engineering",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins uninstall dry-run failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"]["dry_run"])
        self.assertEqual(output["data"]["plugin_name"], "harness-engineering")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask plugins uninstall harness-engineering --dry-run --json --robot"],
        )

    def test_plugins_uninstall_dry_run_human_output_exposes_validation(self):
        """Verify plugin uninstall dry-run human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "uninstall",
            "harness-engineering",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins uninstall dry-run failed: {result.stderr}")
        self.assertIn("Dry run - would uninstall plugin", result.stdout)
        self.assertIn("Name: harness-engineering", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins uninstall harness-engineering --dry-run --json --robot",
            result.stdout,
        )

    def test_plugins_uninstall_missing_plugin_exposes_validation(self):
        """Verify plugin uninstall missing-plugin errors expose a replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "uninstall",
            "not-a-real-plugin",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask plugins uninstall not-a-real-plugin --dry-run --json --robot"],
        )

    def test_plugins_uninstall_missing_plugin_human_output_exposes_validation(self):
        """Verify plugin uninstall missing-plugin errors render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "uninstall",
            "not-a-real-plugin",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Plugin 'not-a-real-plugin' not found under Plugins/.", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins uninstall not-a-real-plugin --dry-run --json --robot",
            result.stdout,
        )

    def test_skills_sync_dry_run(self):
        """CA2: Verify ask skills sync --dry-run returns a plan without changes."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "sync", "--dry-run", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("plan", output["data"])
        self.assertIn("symlinks", output["data"]["plan"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills sync --dry-run --json --robot"],
        )

    def test_skills_user_sync_defaults_to_links_only(self):
        """User sync must not refresh plugin mirrors without an explicit full mode."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "user",
            "--dry-run",
            "--json",
            "--robot",
        ]
        with tempfile.TemporaryDirectory() as home:
            result = _run_cli(cmd, env={**os.environ, "HOME": home})
            self.assertFalse((Path(home) / ".agents").exists())
            self.assertFalse((Path(home) / ".codex").exists())

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        plan = output["data"]["plan"]
        self.assertEqual(plan["user_sync_mode"], "links-only")
        self.assertNotIn("runtime_plugin_mirrors", plan)
        self.assertEqual(plan["mutation_counts"]["writes"], 0)
        self.assertEqual(plan["mutation_counts"]["deletes"], 0)
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills sync --scope user --dry-run --user-sync-mode links-only --json --robot"],
        )

    def test_skills_user_sync_full_mode_keeps_plugin_mirror_route_explicit(self):
        """The legacy plugin-mirror route remains available only with explicit full mode."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "user",
            "--user-sync-mode",
            "full",
            "--dry-run",
            "--json",
            "--robot",
        ]
        with tempfile.TemporaryDirectory() as home:
            result = _run_cli(cmd, env={**os.environ, "HOME": home})

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        plan = output["data"]["plan"]
        self.assertEqual(plan["user_sync_mode"], "full")
        self.assertIn("runtime_plugin_mirrors", plan)
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills sync --scope user --dry-run --user-sync-mode full --json --robot"],
        )

    def test_skills_workspace_sync_preserves_full_sync_contract(self):
        """Workspace sync must not inherit the user-only links-only default."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["data"]["plan"]["user_sync_mode"], "full")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills sync --dry-run --json --robot"],
        )

    def test_skills_workspace_sync_rejects_user_only_links_mode(self):
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--user-sync-mode",
            "links-only",
            "--dry-run",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["errors"][0]["code"], "ERR_INVALID_SCOPE")
        self.assertIn("only with --scope user", output["errors"][0]["message"])

    def test_skills_sync_human_output_exposes_validation(self):
        """Verify ask skills sync renders its validation command in dry-run mode."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "sync", "--dry-run", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Planned sync:", result.stdout)
        self.assertIn("Validation: ./bin/ask skills sync --dry-run --json --robot", result.stdout)

    def test_runtime_surface_json_contract(self):
        """Verify ask runtime surface exposes the runtime report under an obvious topic."""
        # Pin projection mode so assertions remain deterministic regardless of ambient runtime.
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "surface", "--json"]
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "success")
            report = output["data"]["runtime_surface"]
            self.assertIn(report["projection_mode"], {"flat", "rooted"})
            self.assertIn("first_level_default_entries", report)
            self.assertIn("hidden_system_entries", report)
            self.assertIn("estimated_description_tokens", report)
            self.assertEqual(
                output["data"]["validation_commands"],
                ["./bin/ask runtime surface --json --robot"],
            )
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_runtime_surface_human_output_exposes_validation(self):
        """Verify ask runtime surface renders its runtime replay command."""
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "surface", "--robot"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Runtime surface:", result.stdout)
            self.assertIn("Validation: ./bin/ask runtime surface --json --robot", result.stdout)
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_runtime_missing_action_human_output_exposes_validation(self):
        """Verify incomplete runtime commands render the recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "runtime", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"runtime output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'runtime'", result.stdout)
        self.assertIn("Validation: ./bin/ask runtime surface --json --robot", result.stdout)

    def test_runtime_missing_action_json_contract_exposes_validation(self):
        """Verify incomplete runtime commands expose the surface recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "runtime", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"runtime output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask runtime surface --json --robot"],
        )

    def test_repo_surface_json_contract_exposes_validation(self):
        """Verify repo surface exposes its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "surface",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"repo surface output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("repo_surface", output["data"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask repo surface --json --robot"],
        )

    def test_repo_surface_human_output_exposes_validation(self):
        """Verify repo surface human output names its replay command."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "repo",
            "surface",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"repo surface output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Repo surface:", result.stdout)
        self.assertIn("Validation: ./bin/ask repo surface --json --robot", result.stdout)

    def test_runtime_budget_json_contract(self):
        """Verify ask runtime budget remains a first-class budget gate command."""
        # Pin SYNC_SKILLS_PROJECTION_MODE to ensure deterministic test behavior.
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "budget", "--json"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "success")
            self.assertEqual(output["data"]["runtime_budget"]["status"], "pass")
            self.assertEqual(output["data"]["runtime_surface"]["status"], "pass")
            self.assertEqual(
                output["data"]["validation_commands"],
                ["./bin/ask runtime budget --json --robot"],
            )
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_runtime_budget_human_output_exposes_validation(self):
        """Verify ask runtime budget renders its runtime replay command."""
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "budget", "--robot"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Runtime budget:", result.stdout)
            self.assertIn("Validation: ./bin/ask runtime budget --json --robot", result.stdout)
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_graph_list_json_contract_exposes_validation(self):
        """Verify graph list exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "list",
            "--topic-filter",
            "agent-ops",
            "--tier",
            "experimental",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph list output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph list --topic-filter agent-ops --tier experimental --json --robot"],
        )

    def test_graph_list_human_output_exposes_validation(self):
        """Verify graph list human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "list",
            "--topic-filter",
            "agent-ops",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph list output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Skills [topic=agent-ops]", result.stdout)
        self.assertIn("Validation: ./bin/ask graph list --topic-filter agent-ops --json --robot", result.stdout)

    def test_graph_topics_json_contract_exposes_validation(self):
        """Verify graph topics exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "topics", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph topics output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph topics --json --robot"],
        )

    def test_graph_topics_human_output_exposes_validation(self):
        """Verify graph topics human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "topics", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph topics output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Topic Clusters", result.stdout)
        self.assertIn("Validation: ./bin/ask graph topics --json --robot", result.stdout)

    def test_graph_missing_action_exposes_validation(self):
        """Verify incomplete graph commands expose the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"graph output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(output["data"]["validation_commands"], ["./bin/ask graph list --json --robot"])

    def test_graph_missing_action_human_output_exposes_validation(self):
        """Verify incomplete graph commands render the read-only recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"graph output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'graph'", result.stdout)
        self.assertIn("Validation: ./bin/ask graph list --json --robot", result.stdout)

    def test_graph_related_json_contract_exposes_validation(self):
        """Verify graph related exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "related",
            "agents-md",
            "--depth",
            "2",
            "--reverse",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph related output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph related agents-md --depth 2 --reverse --json --robot"],
        )

    def test_graph_related_human_output_exposes_validation(self):
        """Verify graph related human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "related",
            "agents-md",
            "--depth",
            "2",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph related output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("agents-md [out-links, depth=2]", result.stdout)
        self.assertIn("Validation: ./bin/ask graph related agents-md --depth 2 --json --robot", result.stdout)

    def test_graph_find_json_contract_exposes_validation(self):
        """Verify graph find exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "find",
            "agent",
            "--topic-filter",
            "agent-ops",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph find output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph find agent --topic-filter agent-ops --json --robot"],
        )

    def test_graph_find_human_output_exposes_validation(self):
        """Verify graph find human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "find", "agent", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph find output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Search: 'agent'", result.stdout)
        self.assertIn("Validation: ./bin/ask graph find agent --json --robot", result.stdout)

    def test_graph_info_json_contract_exposes_validation(self):
        """Verify graph info exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "info", "agents-md", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph info output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph info agents-md --json --robot"],
        )

    def test_graph_info_unknown_skill_exposes_recovery_commands(self):
        """Verify an unknown graph skill points agents to inspect valid ids."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "info",
            "definitely-missing",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(
            result.returncode,
            2,
            f"graph info output: {result.stdout}\nstderr: {result.stderr}",
        )
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["errors"][0]["fix_suggestion"],
            "Search available skill ids with: ./bin/ask graph find definitely-missing --json --robot; "
            "if no matches are returned, run ./bin/ask graph list --json --robot",
        )

    def test_graph_info_human_output_exposes_validation(self):
        """Verify graph info human output names its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "graph", "info", "agents-md", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph info output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("agents-md", result.stdout)
        self.assertIn("Validation: ./bin/ask graph info agents-md --json --robot", result.stdout)

    def test_graph_chain_json_contract_exposes_validation(self):
        """Verify graph chain exposes its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "chain",
            "agents-md",
            "verification-before-completion",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph chain output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"]["reachable"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask graph chain agents-md verification-before-completion --json --robot"],
        )

    def test_graph_chain_human_output_exposes_validation(self):
        """Verify graph chain human output names its replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "graph",
            "chain",
            "agents-md",
            "verification-before-completion",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"graph chain output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("Chain (", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask graph chain agents-md verification-before-completion --json --robot",
            result.stdout,
        )

    def test_skills_sync_projection_reaches_engine(self):
        """Verify --projection is dispatched and cannot be silently ignored."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "flat",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["projection_mode"], "flat")
        self.assertEqual(output["data"]["projection"]["engine"], "projection_engine.py")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills sync --dry-run --projection flat --json --robot"],
        )

    def test_skills_sync_rejects_removed_rooted_projection(self):
        """Rooted mode is removed from the SDK-flat sync contract."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "rooted",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIsNone(output["data"]["projection_mode"])
        self.assertEqual(output["data"]["requested_projection_mode"], "rooted")
        self.assertEqual(output["errors"][0]["code"], "ERR_INVALID_PROJECTION_MODE")

    def test_skills_sync_rejects_removed_skill_tree_alias(self):
        """Rooted aliases are removed with rooted mode."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "skill-tree",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIsNone(output["data"]["projection_mode"])
        self.assertEqual(output["data"]["requested_projection_mode"], "skill-tree")
        self.assertEqual(output["errors"][0]["code"], "ERR_INVALID_PROJECTION_MODE")

    def test_skills_sync_rejects_deferred_hybrid_projection(self):
        """Hybrid remains out of mutating scope until a named consumer exists."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "sync",
            "--scope",
            "workspace",
            "--projection",
            "hybrid",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertIsNone(output["data"]["projection_mode"])
        self.assertEqual(output["data"]["requested_projection_mode"], "hybrid")
        self.assertEqual(output["errors"][0]["code"], "ERR_DEFERRED_PROJECTION_MODE")

    def test_skills_install_dry_run(self):
        """CA2: Verify ask skills install --dry-run returns a plan without making changes."""
        # Using --dry-run to avoid actual network calls and mutations
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "install", "https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication", "--dry-run", "--json"]
        result = _run_cli(cmd)

        # Dry run should succeed and return installation plan
        output = json.loads(result.stdout)
        self.assertIn(output["status"], ["success", "error"])
        if output["status"] == "success":
            self.assertIn("skill_name", output["data"])
            self.assertTrue(output["data"].get("dry_run", False), "Expected dry_run to be True")
            intake = output["data"].get("intake_decision")
            self.assertIsInstance(intake, dict)
            self.assertEqual(intake.get("schema_version"), "skill-install-intake.v1")
            self.assertIn(intake.get("outcome"), intake.get("allowed_outcomes", []))
            self.assertIn("post_install_gates", intake)
            readiness = output["data"].get("readiness_policy")
            self.assertTrue(readiness.get("full_evals_required_before_promotion"))
            self.assertTrue(readiness.get("external_skill_install_is_intake_not_copy"))
            self.assertEqual(
                output["data"]["validation_commands"],
                [
                    "./bin/ask skills install "
                    "https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication "
                    "--dest Skills/github --dry-run --json --robot"
                ],
            )

    def test_skills_install_dry_run_human_output_exposes_validation(self):
        """Verify ask skills install --dry-run renders its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "install",
            "https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication",
            "--dry-run",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run - would install:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills install "
            "https://github.com/google-openai/openai-cli/tree/main/.openai/skills/review-duplication "
            "--dest Skills/github --dry-run --json --robot",
            result.stdout,
        )

    def test_skills_external_review_skip_tools_json_contract(self):
        """Verify ask skills external-review exposes a replayable local-only contract."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "external-review",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--skip-plugin-eval",
            "--skip-tessl",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["plugin_eval"]["status"], "skipped")
        self.assertEqual(output["data"]["tessl_lint"]["status"], "skipped")
        self.assertEqual(output["data"]["policy"]["plugin_eval_min_acceptable_grade"], "B+")
        self.assertEqual(output["data"]["policy"]["tessl_review_min_score"], 95)
        self.assertEqual(output["data"]["policy"]["tessl_review_target_score"], 95)
        self.assertEqual(output["data"]["policy"]["tessl_project_marker"], "tessl.json")
        self.assertIn("/tmp/ask-tessl-reviews", output["data"]["policy"]["tessl_staging_root"])
        self.assertEqual(output["data"]["review_mode_details"]["tessl_review"]["minimum_score"], 95)
        self.assertEqual(output["data"]["review_mode_details"]["tessl_review"]["target_score"], 95)
        self.assertIn("--threshold 95", output["data"]["review_mode_details"]["tessl_review"]["command"])
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask skills external-review "
                "Plugins/skill-factory/skills/code_quality_review/skill-builder "
                "--skip-plugin-eval --skip-tessl --json --robot"
            ],
        )

    def test_skills_external_review_skip_tools_human_output_exposes_validation(self):
        """Verify ask skills external-review renders local-only status and validation."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "external-review",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--skip-plugin-eval",
            "--skip-tessl",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("External review:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills external-review "
            "Plugins/skill-factory/skills/code_quality_review/skill-builder "
            "--skip-plugin-eval --skip-tessl --json --robot",
            result.stdout,
        )

    def test_skills_fold_dependency_error_exposes_validation(self):
        """Verify ask skills fold dependency blockers remain replayable."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "fold",
            "simplify",
            "imagegen",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_DEPENDENCY")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills fold simplify imagegen --json --robot"],
        )
        self.assertIn(output["data"]["dependency_status"]["skill_catalog"], {"load_failed", "missing"})

    def test_skills_fold_dependency_error_human_output_exposes_validation(self):
        """Verify ask skills fold dependency blockers render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "fold",
            "simplify",
            "imagegen",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Skill router or builder catalog not available.", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills fold simplify imagegen --json --robot",
            result.stdout,
        )

    def test_trace_id_from_env(self):
        """CA2: ASK_TRACE_ID environment variable propagates to output."""
        env = os.environ.copy()
        env["ASK_TRACE_ID"] = "test-trace-123"
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json"]
        result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "test-trace-123")

    def test_trace_id_flag_overrides_env(self):
        """CA2: --trace-id flag overrides ASK_TRACE_ID environment variable."""
        env = os.environ.copy()
        env["ASK_TRACE_ID"] = "env-trace-456"
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json", "--trace-id", "flag-trace-789"]
        result = _run_cli(cmd, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "flag-trace-789")  # Flag wins

    def test_robot_mode_recovers_swapped_topic_action(self):
        """Robot mode should recover clear intent when topic/action are swapped."""
        cmd = ["python3", "Infrastructure/bin/ask", "list", "skills", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"Expected success, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("skills", output.get("data", {}))
        self.assertIn("correction_note", output.get("metadata", {}))

    def test_robot_mode_recovers_action_after_flags(self):
        """Robot mode should recover when action token is after option flags."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "--advanced", "ls", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"Expected success, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))
        self.assertIn("correction_note", output.get("metadata", {}))

    def test_robot_mode_returns_detailed_error_for_ambiguous_intent(self):
        """Robot mode should return rich guidance when intent cannot be resolved."""
        cmd = ["python3", "Infrastructure/bin/ask", "status", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        message = output["errors"][0]["message"]
        self.assertIn("Guidance", message)
        self.assertIn("Try one of these", message)
        self.assertIn("repo status", message)

    def test_robot_mode_returns_argument_guidance_when_intent_clear(self):
        """Robot mode should explain missing arguments with command-specific examples."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "audit", "--robot", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        message = output["errors"][0]["message"]
        self.assertIn("Command intent was understood", message)
        self.assertIn("ask skills audit --help", message)
        self.assertIn("Valid examples", message)
        self.assertIn("skills audit", message)

    def test_skills_audit_json_contract(self):
        """Verify ask skills audit exposes its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "audit",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["diagnostics"]["exit_code"], 0)
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask skills audit "
                "Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot"
            ],
        )

    def test_skills_audit_accepts_explicit_external_project_skill(self):
        """Verify Skill Factory audit can inspect project-local skills outside the foundry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "x-writer" / ".codex" / "skills" / "draft-helper"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: draft-helper\n"
                "description: Use when improving a project-local writing workflow.\n"
                "---\n\n"
                "# Draft Helper\n",
                encoding="utf-8",
            )
            cmd = [
                sys.executable,
                str(Path(__file__).resolve().parents[1] / "bin" / "ask"),
                "skills",
                "audit",
                str(skill_dir),
                "--json",
                "--robot",
            ]
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["audit_scope"]["classification"], "external_project_skill")
        self.assertFalse(output["data"]["audit_scope"]["repo_coupled_gates"])
        diagnostics = output["data"]["diagnostics"]
        self.assertEqual(diagnostics["exit_code"], 0)
        self.assertIn("external project skill", diagnostics["stdout"])

    def test_skills_audit_accepts_explicit_external_project_skill_root(self):
        """Verify Skill Factory audit can inspect a project-local .codex/skills root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "x-writer" / ".codex" / "skills"
            for name in ("draft-helper", "style-check"):
                skill_dir = skills_root / name
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(
                    "---\n"
                    f"name: {name}\n"
                    "description: Use when improving a project-local writing workflow.\n"
                    "---\n\n"
                    f"# {name}\n",
                    encoding="utf-8",
                )
            cmd = [
                sys.executable,
                str(Path(__file__).resolve().parents[1] / "bin" / "ask"),
                "skills",
                "audit",
                str(skills_root),
                "--json",
                "--robot",
            ]
            result = _run_cli(cmd, cwd=Path(__file__).resolve().parents[2])

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["audit_scope"]["classification"], "external_project_skill_root")
        self.assertEqual(output["data"]["audit_scope"]["child_count"], 2)
        self.assertEqual([child["status"] for child in output["data"]["children"]], ["success", "success"])

    def test_skills_audit_human_output_exposes_validation(self):
        """Verify ask skills audit renders its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "audit",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Audit passed:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills audit "
            "Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot",
            result.stdout,
        )

    def test_skills_validate_openai_format_json_contract(self):
        """Verify ask exposes OpenAI skill format as a first-class validation surface."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-openai-format",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        gate = output["data"]["openai_skill_format"]
        self.assertEqual(gate["exit_code"], 0)
        self.assertIn("lint_openai_skill_format.sh", " ".join(gate["command"]))
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask skills validate-openai-format "
                "Plugins/skill-factory/skills/code_quality_review/skill-builder --mode strict --json --robot"
            ],
        )

    def test_skills_validate_openai_format_human_output_exposes_validation(self):
        """Verify ask skills validate-openai-format renders its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-openai-format",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OpenAI skill format passed:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills validate-openai-format "
            "Plugins/skill-factory/skills/code_quality_review/skill-builder --mode strict --json --robot",
            result.stdout,
        )

    def test_skills_validate_skill_gate_json_contract(self):
        """Verify ask exposes skill gate as a first-class validation surface."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-skill-gate",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        gate = output["data"]["skill_gate"]
        self.assertEqual(gate["exit_code"], 0)
        self.assertTrue(any("skill_gate.py" in part for part in gate["command"]))
        self.assertNotIn("SEC_CANONICAL_HEADER_ORDER", gate["stdout"])
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask skills validate-skill-gate "
                "Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot"
            ],
        )

    def test_skills_validate_skill_gate_human_output_exposes_validation(self):
        """Verify ask skills validate-skill-gate renders its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-skill-gate",
            "Plugins/skill-factory/skills/code_quality_review/skill-builder",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill gate passed:", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills validate-skill-gate "
            "Plugins/skill-factory/skills/code_quality_review/skill-builder --json --robot",
            result.stdout,
        )

    def test_skills_validate_boundaries_json_contract(self):
        """Verify ask exposes canonical-versus-projection ownership as a first-class check."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-boundaries",
            "Skills/agent-ops/autofix",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        boundary = output["data"]["boundary_check"]
        self.assertEqual(boundary["status"], "pass")
        self.assertEqual(boundary["handle"], "autofix")
        self.assertEqual(boundary["canonical_skill_path"], "Skills/agent-ops/autofix/SKILL.md")
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask skills validate-boundaries Skills/agent-ops/autofix --json --robot"],
        )

    def test_skills_validate_boundaries_human_output_exposes_validation(self):
        """Verify ask skills validate-boundaries renders its validation command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "validate-boundaries",
            "Skills/agent-ops/autofix",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill boundaries passed: $autofix", result.stdout)
        self.assertIn("Canonical source:", result.stdout)
        self.assertIn("Note: Edit the canonical source path", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills validate-boundaries Skills/agent-ops/autofix --json --robot",
            result.stdout,
        )

    def test_skills_init_validation_error_exposes_validation(self):
        """Verify ask skills init validation errors remain replayable without writing files."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "init",
            "example-skill",
            "--category",
            "/tmp/not-repo-relative",
            "--description",
            "Example description",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask skills init example-skill --category /tmp/not-repo-relative "
                "--description 'Example description' --json --robot"
            ],
        )

    def test_skills_init_validation_error_human_output_exposes_validation(self):
        """Verify ask skills init validation errors render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "skills",
            "init",
            "example-skill",
            "--category",
            "/tmp/not-repo-relative",
            "--description",
            "Example description",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Skill category must be repo-relative.", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask skills init example-skill --category /tmp/not-repo-relative "
            "--description 'Example description' --json --robot",
            result.stdout,
        )

    def test_workouts_list_json_contract_exposes_validation(self):
        """Verify ask workouts list exposes its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "workouts", "list", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("workouts", output["data"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask workouts list --json --robot"],
        )

    def test_workouts_list_human_output_exposes_validation(self):
        """Verify ask workouts list renders its replay command."""
        cmd = ["python3", "Infrastructure/bin/ask", "workouts", "list", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Workout list: success", result.stdout)
        self.assertIn("Validation: ./bin/ask workouts list --json --robot", result.stdout)

    def test_workouts_missing_action_exposes_validation(self):
        """Verify incomplete workout commands expose the list recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "workouts", "--json", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"workouts output: {result.stdout}\nstderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("missing action", output["errors"][0]["message"])
        self.assertEqual(
            output["data"]["validation_commands"],
            ["./bin/ask workouts list --json --robot"],
        )

    def test_workouts_missing_action_human_output_exposes_validation(self):
        """Verify incomplete workout commands render the list recovery command."""
        cmd = ["python3", "Infrastructure/bin/ask", "workouts", "--robot"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 2, f"workouts output: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn("missing action for topic 'workouts'", result.stdout)
        self.assertIn("Validation: ./bin/ask workouts list --json --robot", result.stdout)

    def test_workouts_score_error_json_contract_exposes_validation(self):
        """Verify ask workouts score validation errors remain replayable."""
        workout_id = "agent-ops/not-a-real-workout"
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "workouts",
            "score",
            workout_id,
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(
            output["data"]["validation_commands"],
            [f"./bin/ask workouts score {workout_id} --json --robot"],
        )

    def test_workouts_score_error_human_output_exposes_validation(self):
        """Verify ask workouts score validation errors render their replay command."""
        workout_id = "agent-ops/not-a-real-workout"
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "workouts",
            "score",
            workout_id,
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"No scorecard found for workout {workout_id}.", result.stdout)
        self.assertIn(
            f"Validation: ./bin/ask workouts score {workout_id} --json --robot",
            result.stdout,
        )

    def test_plugins_init_validation_error_exposes_validation(self):
        """Verify plugins init validation errors expose a replay command without writing."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "init",
            "example-plugin",
            "--category",
            "/tmp/not-a-plugin-category",
            "--with-marketplace",
            "--with-scripts",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask plugins init example-plugin --category /tmp/not-a-plugin-category "
                "--with-marketplace --with-scripts --json --robot"
            ],
        )

    def test_plugins_init_validation_error_human_output_exposes_validation(self):
        """Verify plugins init validation errors render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "init",
            "example-plugin",
            "--category",
            "/tmp/not-a-plugin-category",
            "--with-marketplace",
            "--with-scripts",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid plugin category", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins init example-plugin --category /tmp/not-a-plugin-category "
            "--with-marketplace --with-scripts --json --robot",
            result.stdout,
        )

    def test_plugins_harden_validation_error_exposes_validation(self):
        """Verify plugin harden validation errors expose a replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "harden",
            "/tmp/not-a-plugin",
            "--skip-compat",
            "--skip-marketplace-audit",
            "--no-require-marketplace",
            "--strict-marketplace-path",
            "--json",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "ERR_VALIDATION")
        self.assertEqual(
            output["data"]["validation_commands"],
            [
                "./bin/ask plugins harden /tmp/not-a-plugin --skip-compat "
                "--skip-marketplace-audit --no-require-marketplace "
                "--strict-marketplace-path --json --robot"
            ],
        )

    def test_plugins_harden_validation_error_human_output_exposes_validation(self):
        """Verify plugin harden validation errors render their replay command."""
        cmd = [
            "python3",
            "Infrastructure/bin/ask",
            "plugins",
            "harden",
            "/tmp/not-a-plugin",
            "--skip-compat",
            "--skip-marketplace-audit",
            "--no-require-marketplace",
            "--strict-marketplace-path",
            "--robot",
        ]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Plugin path", result.stdout)
        self.assertIn(
            "Validation: ./bin/ask plugins harden /tmp/not-a-plugin --skip-compat "
            "--skip-marketplace-audit --no-require-marketplace "
            "--strict-marketplace-path --json --robot",
            result.stdout,
        )

if __name__ == "__main__":
    unittest.main()
