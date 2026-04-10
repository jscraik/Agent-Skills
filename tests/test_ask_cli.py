import unittest
import subprocess
import json
import os
import sys

class TestAskCLI(unittest.TestCase):
    def test_json_envelope_format(self):
        """CA1: Verify ask --json returns a valid CallResult envelope."""
        # Using -p to pass a dummy command if needed, or just root --json
        cmd = [sys.executable, "bin/ask", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
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
        cmd = ["python3", "bin/ask", "repo", "status", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

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
        cmd = ["python3", "bin/ask", "skills", "list", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        cmd = ["python3", "bin/ask", "skills", "list", "--advanced", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("advanced_mode"))

    def test_skills_route_json_contract(self):
        """CA1: Verify ask skills route exposes selection-decision fields."""
        cmd = ["python3", "bin/ask", "skills", "route", "create-auth", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

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

    def test_skills_goal_json_contract(self):
        """
        Ensure the `ask skills goal create` CLI returns a JSON envelope containing a `goal_decision` with required fields.
        
        Asserts the top-level `status` and `data` keys exist and that `data.goal_decision` includes `schema_version`, `decision_status`, `policy_identity`, `recommended_candidate`, and `alternative_candidates`.
        """
        cmd = ["python3", "bin/ask", "skills", "goal", "create auth integration", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
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

    def test_repo_doctor_catalog_json_contract(self):
        """
        Verify `ask repo doctor-catalog --json` returns a catalog parity payload with required fields.
        
        Asserts the CLI emits non-empty JSON and that `data.catalog_parity` contains `schema_version`, `drift_detected` and `surfaces`.
        """
        cmd = [__import__("sys").executable, "bin/ask", "repo", "doctor-catalog", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("status", output)
        self.assertIn("catalog_parity", output.get("data", {}))
        report = output["data"]["catalog_parity"]
        self.assertEqual(report.get("schema_version"), "catalog-parity.v1")
        self.assertIn("drift_detected", report)
        self.assertIn("surfaces", report)

    def test_goal_alias_normalization(self):
        """
        Ensure the `goal create` CLI alias returns a skills-style goal decision in the JSON envelope.
        
        Runs `bin/ask goal create auth integration --json`, asserts stdout contains JSON and that `data.goal_decision` exists.
        """
        cmd = [__import__("sys").executable, "bin/ask", "goal", "create auth integration", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_goal_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json goal alias maps to ask skills goal."""
        cmd = [__import__("sys").executable, "bin/ask", "--json", "goal", "create auth integration"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("goal_decision", output.get("data", {}))

    def test_doctor_catalog_alias_normalization_with_prefix_global_flag(self):
        """CA1: Verify ask --json doctor catalog alias maps to repo doctor-catalog."""
        cmd = [__import__("sys").executable, "bin/ask", "--json", "doctor", "catalog"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertTrue(result.stdout.strip(), f"Expected JSON output, stderr: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertIn("catalog_parity", output.get("data", {}))

    def test_skills_starter_mode(self):
        """
        Verify the CLI `skills starter` command returns starter-mode catalogue metadata for the chosen archetype.
        
        Runs `bin/ask skills starter --archetype delivery --limit 5 --json` and asserts the process exits with code 0, the JSON envelope `status` is `"success"`, `data.starter_mode` is truthy, `data.starter_archetype` equals `"delivery"`, and `data.skills` is a list.
        """
        cmd = [__import__("sys").executable, "bin/ask", "skills", "starter", "--archetype", "delivery", "--limit", "5", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, f"skills starter failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(output["data"].get("starter_mode"))
        self.assertEqual(output["data"].get("starter_archetype"), "delivery")
        self.assertIsInstance(output["data"].get("skills"), list)

    def test_plugins_list_state(self):
        """CA1: Verify ask plugins list returns lifecycle state groups."""
        cmd = ["python3", "bin/ask", "plugins", "list", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, f"plugins list failed: {result.stderr}")
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("installed_state", output["data"])
        self.assertIn("activation_state", output["data"])
        self.assertIn("health_state", output["data"])

    def test_skills_sync_dry_run(self):
        """CA2: Verify ask skills sync --dry-run returns a plan without changes."""
        cmd = ["python3", "bin/ask", "skills", "sync", "--dry-run", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        
        self.assertEqual(output["status"], "success")
        self.assertIn("plan", output["data"])
        self.assertIn("symlinks", output["data"]["plan"])

    def test_skills_install_dry_run(self):
        """CA2: Verify ask skills install --dry-run returns a plan without making changes."""
        # Using --dry-run to avoid actual network calls and mutations
        cmd = ["python3", "bin/ask", "skills", "install", "https://github.com/google-gemini/gemini-cli/tree/main/.gemini/skills/review-duplication", "--dry-run", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

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
        cmd = ["python3", "bin/ask", "repo", "status", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "test-trace-123")

    def test_trace_id_flag_overrides_env(self):
        """CA2: --trace-id flag overrides ASK_TRACE_ID environment variable."""
        env = os.environ.copy()
        env["ASK_TRACE_ID"] = "env-trace-456"
        cmd = ["python3", "bin/ask", "repo", "status", "--json", "--trace-id", "flag-trace-789"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["trace_id"], "flag-trace-789")  # Flag wins

if __name__ == "__main__":
    unittest.main()
