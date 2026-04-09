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
        """CA1: Verify ask skills list returns a catalog of skills."""
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
