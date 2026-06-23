from __future__ import annotations

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

from ask.skills_sdk.risk_modes import build_risk_mode_taxonomy_receipt  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/risk-mode-taxonomy-receipt.v0.schema.json"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"


def _schema() -> dict:
    """
    Load the risk-mode taxonomy receipt JSON schema.
    
    Returns:
        dict: The parsed schema.
    """
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _command_env() -> dict[str, str]:
    """
    Create an environment dictionary with isolated cache and state directories for subprocess execution.
    
    Returns:
        A dictionary containing environment variables with isolated cache and state directories under a temporary base path, plus the trusted configuration path.
    """
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
    """
    Execute the ask CLI command with the given arguments.
    
    Returns:
    	A CompletedProcess object with the command's return code, stdout, and stderr.
    """
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _write_skill(root: Path, body: str, frontmatter: str | None = None) -> Path:
    """
    Create a skill markdown file in a sample-risk-mode directory.
    
    Parameters:
        root (Path): The base directory where the skill structure is created.
        body (str): The skill content.
        frontmatter (str | None): YAML frontmatter. Defaults to standard name and description fields.
    
    Returns:
        Path: The path to the created SKILL.md file.
    """
    skill_dir = root / "sample-risk-mode"
    skill_dir.mkdir()
    frontmatter_text = frontmatter or "name: sample-risk-mode\ndescription: sample risk mode skill"
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"---\n{frontmatter_text}\n---\n\n{body}\n", encoding="utf-8")
    return skill_md


class TestSkillsSdkRiskModeTaxonomy(unittest.TestCase):
    def assert_schema_valid(self, payload: dict) -> None:
        """
        Assert that the payload conforms to the risk-mode-taxonomy-receipt schema.
        
        Parameters:
        	payload (dict): The receipt payload to validate
        """
        _validate_schema_subset(_schema(), payload, {"risk-mode-taxonomy-receipt": _schema()})

    def test_builder_detects_negligent_instruction_without_safety_language(self) -> None:
        """
        Verify that the risk mode builder identifies negligent instruction risk when a skill contains impactful write operations without safety language, and confirm execution, scanner execution, network access, and mutation flags remain false.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = _write_skill(
                Path(temp_dir),
                "# Sample\n\nDelete stale tickets and publish the summary.",
                "name: sample-risk-mode\ndescription: sample risk mode skill\nprovenance: test",
            )
            receipt = build_risk_mode_taxonomy_receipt(
                REPO_ROOT,
                source_path=skill_md,
                query=str(skill_md),
            )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["primary_mode"], "negligent_instruction")
        self.assertIn("negligent_instruction", receipt["detected_modes"])
        negligent = next(row for row in receipt["mode_results"] if row["mode"] == "negligent_instruction")
        indicator_ids = {indicator["id"] for indicator in negligent["indicators"]}
        self.assertIn("impactful_write_without_review", indicator_ids)
        self.assertIn("no_boundary_language", indicator_ids)
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_builder_detects_vulnerable_operation_for_secret_logging_without_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = _write_skill(
                Path(temp_dir),
                "# Sample\n\nRead the API token and include it in stdout logs for debugging.",
                "name: sample-risk-mode\ndescription: sample risk mode skill\nprovenance: test",
            )
            receipt = build_risk_mode_taxonomy_receipt(
                REPO_ROOT,
                source_path=skill_md,
                query=str(skill_md),
            )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["primary_mode"], "vulnerable_operation")
        vulnerable = next(row for row in receipt["mode_results"] if row["mode"] == "vulnerable_operation")
        indicator_ids = {indicator["id"] for indicator in vulnerable["indicators"]}
        self.assertIn("secret_handling", indicator_ids)
        self.assertIn("log_exposure", indicator_ids)
        self.assertIn("secret_without_redaction", indicator_ids)

    def test_builder_detects_unknown_when_provenance_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = _write_skill(Path(temp_dir), "# Sample\n\nPlain authoring guidance.")
            receipt = build_risk_mode_taxonomy_receipt(
                REPO_ROOT,
                source_path=skill_md,
                query=str(skill_md),
            )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["primary_mode"], "unknown_insufficient_evidence")
        self.assertEqual(receipt["detected_modes"], ["unknown_insufficient_evidence"])

    def test_command_emits_preview_receipt_for_fixture_skill(self) -> None:
        process = _run_ask(
            "sdk",
            "security",
            "risk-modes",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--preview",
            "--json",
            "--robot",
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_risk_mode_taxonomy"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["package_id"], "skills-sdk-valid-fixture")
        self.assert_schema_valid(receipt)
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_command_requires_preview_flag(self) -> None:
        """
        Verify that the risk-modes command requires the --preview flag.
        
        Asserts that invoking the command without --preview results in a non-zero return code and an error message containing "requires --preview".
        """
        process = _run_ask(
            "sdk",
            "security",
            "risk-modes",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--json",
            "--robot",
        )

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_schema_fixture_preserves_non_execution_boundary(self) -> None:
        payload = json.loads((FIXTURE_DIR / "valid" / "risk-mode-taxonomy-receipt.json").read_text(encoding="utf-8"))

        self.assert_schema_valid(payload)
        self.assertEqual(payload["primary_mode"], "vulnerable_operation")
        self.assertIn("vulnerable_operation", payload["detected_modes"])
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_schema_rejects_execution_claims(self) -> None:
        payload = json.loads((FIXTURE_DIR / "invalid" / "risk-mode-taxonomy-executes.json").read_text(encoding="utf-8"))

        with self.assertRaises(AssertionError):
            self.assert_schema_valid(payload)


if __name__ == "__main__":
    unittest.main()
