from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.security_adapter_discovery import (  # noqa: E402
    SecurityAdapterDiscoveryError,
    build_security_adapter_discovery_receipt,
)


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


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkSecurityAdapterDiscovery(unittest.TestCase):
    def test_builder_discovers_local_configured_security_adapters_without_execution(self) -> None:
        receipt = build_security_adapter_discovery_receipt(REPO_ROOT)
        adapter_ids = {candidate["adapter_id"] for candidate in receipt["adapter_candidates"]}

        self.assertEqual(receipt["status"], "preview")
        self.assertIn("semgrep", adapter_ids)
        self.assertIn("trivy", adapter_ids)
        self.assertIn("gitleaks", adapter_ids)
        self.assertIn("codeql", adapter_ids)
        self.assertIn("dependency-review", adapter_ids)
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])
        for candidate in receipt["adapter_candidates"]:
            self.assertTrue(candidate["configured"])
            self.assertTrue(candidate["evidence_refs"])
            self.assertFalse(candidate["scanner_execution_performed"])
            self.assertFalse(candidate["network_accessed"])
            self.assertFalse(candidate["credentials_accessed"])

    def test_command_emits_preview_receipt(self) -> None:
        process = _run_ask("sdk", "security", "adapters", "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_security_adapter_discovery"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertGreaterEqual(payload["adapter_count"], 5)
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_public_wrapper_preserves_security_adapter_command(self) -> None:
        process = subprocess.run(
            [sys.executable, "bin/skills-sdk", "security", "adapters", "--preview", "--json", "--robot"],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["data"]["skills_sdk_security_adapter_discovery"]["status"], "preview")

    def test_security_adapter_discovery_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "security", "adapters", "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_builder_blocks_when_no_local_sources_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SecurityAdapterDiscoveryError) as context:
                build_security_adapter_discovery_receipt(Path(temp_dir))

        receipt = context.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["adapter_candidates"], [])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
