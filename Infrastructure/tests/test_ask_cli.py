import unittest
import subprocess
import json
import os
import sys


def _run_cli(cmd: list[str], **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, **kwargs)


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
        cmd = ["python3", "Infrastructure/bin/ask", "repo", "status", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)

        self.assertEqual(output["status"], "success")
        self.assertIn("repo_root", output["data"])
        # Verify it found the actual current directory or a parent
        # Handle redacted paths by substituting back the home directory
        repo_root = output["data"]["repo_root"]
        if "<USER_HOME>" in repo_root:
            repo_root = repo_root.replace("<USER_HOME>", os.path.expanduser("~"))
        self.assertTrue(os.path.isdir(repo_root), f"repo_root is not a directory: {repo_root}")

    def test_skills_list(self):
        """
        Validate that the CLI `ask skills list --json` exposes a skills catalogue with the expected envelope and fields.
        
        Checks:
        - the process exits successfully (return code 0),
        - top-level `status` equals "success",
        - `data.skills` is present and is a list,
        - if the list is non-empty, the first skill contains `name` and `path`.
        """
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--json"]
        result = _run_cli(cmd)
        
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        
        self.assertEqual(output["status"], "success")
        self.assertIn("skills", output["data"])
        self.assertIsInstance(output["data"]["skills"], list)
        if len(output["data"]["skills"]) > 0:
            skill = output["data"]["skills"][0]
            self.assertIn("name", skill)
            self.assertIn("path", skill)

    def test_skills_list_advanced_flag(self):
        """CA1: Verify ask skills list --advanced toggles advanced_mode in JSON output."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "list", "--advanced", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))

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

    def test_skills_handles_json_contract(self):
        """Verify ask skills handles exposes the command-surface contract."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "handles", "--check", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        surface = output["data"]["command_surface"]
        self.assertEqual(surface["schema_version"], "command-surface.v1")
        self.assertEqual(surface["status"], "pass")
        self.assertGreater(surface["handle_count"], 0)

    def test_skills_handles_projection_dry_run_contract(self):
        """Verify ask can preview the generated command-surface projection."""
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

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        write = output["data"]["command_surface_projection_write"]
        self.assertEqual(write["status"], "pass")
        self.assertTrue(write["dry_run"])
        self.assertEqual(write["path"], ".skillsets/command-surface.json")

    def test_skills_handles_command_handle_dry_run_contract(self):
        """Verify ask can preview generated runtime command handles."""
        cmd = [
            sys.executable,
            "Infrastructure/bin/ask",
            "skills",
            "handles",
            "--write-command-handles",
            "--dry-run",
            "--json",
        ]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        write = output["data"]["command_handle_write"]
        self.assertEqual(write["status"], "pass")
        self.assertTrue(write["dry_run"])
        self.assertGreater(write["command_handle_count"], 0)
        paths = {row["path"] for row in write["writes"] if row["handle"] == "he-heartbeat"}
        self.assertEqual(
            paths,
            {
                ".agents/skills/he-heartbeat/SKILL.md",
                ".agents/skills/he-heartbeat/agents/openai.yaml",
            },
        )

    def test_skills_resolve_json_contract(self):
        """Verify ask skills resolve returns a latent source path for a command handle."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "resolve", "he-heartbeat", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["handle"], "he-heartbeat")
        self.assertEqual(resolution["command_visibility"], "target")
        self.assertEqual(resolution["invoke_via"], "harness-engineering")

    def test_skills_proof_json_contract(self):
        """Verify ask skills proof separates resolver, command handle, and runtime-link gates."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "he-heartbeat", "--json"]
        result = _run_cli(cmd)

        self.assertTrue(result.stdout.strip(), result.stderr)
        output = json.loads(result.stdout)
        proof = output["data"]["proof"]
        self.assertEqual(proof["schema_version"], "command-handle-proof.v1")
        self.assertEqual(proof["handle"], "he-heartbeat")
        self.assertIn("resolver", proof["gates"])
        self.assertIn("generated_command_handle_check", proof["gates"])
        self.assertIn("workspace_command_handle_exists", proof["gates"])
        self.assertIn("codex_user_link", proof["gates"])
        self.assertIn("agents_user_link", proof["gate_policy"]["user_runtime_any_of"])
        self.assertEqual(proof["live_codex_invocation"]["status"], "manual_session_gate")

    def test_skills_proof_human_output(self):
        """Verify ask skills proof has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "proof", "he-heartbeat"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill handle proof: $he-heartbeat", result.stdout)
        self.assertIn("live invocation: manual_session_gate", result.stdout)

    def test_reviewers_resolve_json_contract(self):
        """Verify ask reviewers resolve exposes the reviewer handle namespace."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        resolution = output["data"]["resolution"]
        self.assertEqual(resolution["status"], "ok")
        self.assertEqual(resolution["kind"], "reviewer")
        self.assertEqual(resolution["command_visibility"], "reviewer")
        self.assertEqual(resolution["canonical_handle"], "skill-inspector")

    def test_reviewers_resolve_human_output(self):
        """Verify ask reviewers resolve has a useful non-JSON success render."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "reviewers", "resolve", "skillinspector"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Reviewer handle: @skill-inspector", result.stdout)
        self.assertIn("codex/agents/skill-inspector/skill-inspector.toml", result.stdout)

    def test_skills_invalid_action_mentions_proof(self):
        """Verify invalid skill-action guidance includes the public proof command."""
        cmd = [sys.executable, "Infrastructure/bin/ask", "skills", "nonsense", "--json"]
        result = _run_cli(cmd)

        self.assertNotEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        suggestion = output["errors"][0]["fix_suggestion"]
        self.assertIn("proof", suggestion)

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

    def test_skills_improve_json_contract(self):
        """Verify `ask skills improve` returns an agent-facing recommendation envelope."""
        cmd = [
            __import__("sys").executable,
            "Infrastructure/bin/ask",
            "skills",
            "improve",
            "autofix",
            "--json",
        ]
        result = _run_cli(cmd)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        improvement = output.get("data", {}).get("improvement", {})
        self.assertEqual(improvement.get("schema_version"), "skill-improvement-recommendation.v1")
        self.assertIn("agent_summary", improvement)
        self.assertIn("recommended_capability", improvement)
        self.assertIn("reachability", improvement)
        self.assertIn("proof", improvement)
        self.assertIn("next_command", improvement)

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
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor", "--json"]
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

    def test_repo_doctor_help_mentions_agent_health_entrypoint(self):
        """Verify `ask repo doctor --help` exposes the agent health wording."""
        cmd = [__import__("sys").executable, "Infrastructure/bin/ask", "repo", "doctor", "--help"]
        result = _run_cli(cmd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Agent-facing repository health entrypoint", result.stdout)

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

    def test_plugins_list_state(self):
        """CA1: Verify ask plugins list returns lifecycle state groups."""
        cmd = ["python3", "Infrastructure/bin/ask", "plugins", "list", "--json"]
        result = _run_cli(cmd)

        self.assertEqual(result.returncode, 0, f"plugins list failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("installed_state", output["data"])
        self.assertIn("activation_state", output["data"])
        self.assertIn("health_state", output["data"])

    def test_skills_sync_dry_run(self):
        """CA2: Verify ask skills sync --dry-run returns a plan without changes."""
        cmd = ["python3", "Infrastructure/bin/ask", "skills", "sync", "--dry-run", "--json"]
        result = _run_cli(cmd)
        
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        
        self.assertEqual(output["status"], "success")
        self.assertIn("plan", output["data"])
        self.assertIn("symlinks", output["data"]["plan"])

    def test_runtime_surface_json_contract(self):
        """Verify ask runtime surface exposes the runtime report under an obvious topic."""
        # Pin projection mode so assertions remain deterministic regardless of ambient runtime.
        saved_projection_mode = os.environ.get("SYNC_SKILLS_PROJECTION_MODE")
        try:
            os.environ["SYNC_SKILLS_PROJECTION_MODE"] = "flat"
            cmd = ["python3", "Infrastructure/bin/ask", "runtime", "surface", "--json"]
            result = _run_cli(cmd)

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "success")
            report = output["data"]["runtime_surface"]
            self.assertIn(report["projection_mode"], {"flat", "rooted"})
            self.assertIn("first_level_default_entries", report)
            self.assertIn("hidden_system_entries", report)
            self.assertIn("estimated_description_tokens", report)
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

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
        finally:
            if saved_projection_mode is None:
                os.environ.pop("SYNC_SKILLS_PROJECTION_MODE", None)
            else:
                os.environ["SYNC_SKILLS_PROJECTION_MODE"] = saved_projection_mode

    def test_skills_sync_projection_reaches_engine(self):
        """Verify --projection is dispatched and cannot be silently ignored."""
        for mode in ("flat", "rooted"):
            with self.subTest(mode=mode):
                cmd = [
                    "python3",
                    "Infrastructure/bin/ask",
                    "skills",
                    "sync",
                    "--scope",
                    "workspace",
                    "--projection",
                    mode,
                    "--dry-run",
                    "--json",
                ]
                result = _run_cli(cmd)

                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                self.assertEqual(output["status"], "success")
                self.assertEqual(output["data"]["projection_mode"], mode)
                self.assertEqual(output["data"]["projection"]["engine"], "projection_engine.py")

    def test_skills_sync_rooted_alias_dry_run_reports_canonical_mode(self):
        """Rooted aliases must report the canonical projection mode in dry-run plans."""
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

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertEqual(output["data"]["projection_mode"], "rooted")
        self.assertEqual(output["data"]["projection"]["requested_mode"], "skill-tree")
        self.assertEqual(output["data"]["plan"]["validation_status"], "pass")

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

if __name__ == "__main__":
    unittest.main()
