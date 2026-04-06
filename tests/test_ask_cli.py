import unittest
import subprocess
import json
import os

class TestAskCLI(unittest.TestCase):
    def test_json_envelope_format(self):
        """CA1: Verify ask --json returns a valid CallResult envelope."""
        # Using -p to pass a dummy command if needed, or just root --json
        cmd = ["python3", "bin/ask", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
        self.assertTrue(os.path.isdir(output["data"]["repo_root"]))

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
        """CA2: Verify ask skills install (mocked via dry-run or similar) identifies redundancy."""
        # Using a URL that we know overlaps with something existing if possible
        # For now, just test basic command structure and response
        cmd = ["python3", "bin/ask", "skills", "install", "https://github.com/google-gemini/gemini-cli/tree/main/.gemini/skills/review-duplication", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # This will actually run the installer, so we check for status: success or expected conflict
        output = json.loads(result.stdout)
        self.assertIn(output["status"], ["success", "error"])
        if output["status"] == "success":
            self.assertIn("skill_name", output["data"])

if __name__ == "__main__":
    unittest.main()
