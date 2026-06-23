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

from ask.skills_sdk.skill_intake_review import build_skill_intake_review_receipt  # noqa: E402


VALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/skill-intake-review-receipt.v0.schema.json"
INTAKE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/skill-intake-receipt.v0.schema.json"
RISK_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/risk-mode-taxonomy-receipt.v0.schema.json"
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"


def _command_env() -> dict[str, str]:
    """
    Create a process environment with isolated cache and state directories.
    
    Sets default values for cache, state, and configuration directories to a temporary location,
    allowing controlled subprocess execution without interfering with system or user environments.
    Existing environment variable values are preserved.
    
    Returns:
        A dictionary of environment variables with paths redirected to a temporary test location.
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


def _run_json_command(*args: str, check: bool = True) -> dict:
    """
    Execute a command and return its JSON output.
    
    Parameters:
        check (bool): If True, raises an error on non-zero exit code.
    
    Returns:
        dict: Parsed JSON from standard output.
    
    Raises:
        AssertionError: If check is True and the subprocess exits with a non-zero code.
    """
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _write_skill(source: Path, *, body: str, frontmatter: str = "") -> None:
    """
    Create a skill fixture file with YAML frontmatter in the specified directory.
    
    Parameters:
        source (Path): Directory where the SKILL.md file will be created.
        body (str): Body content of the skill file, appended after the frontmatter.
        frontmatter (str): Optional additional YAML frontmatter fields to include before the body separator.
    """
    source.mkdir()
    (source / "SKILL.md").write_text(
        f"---\nname: external-review\n"
        f"description: External review fixture\n"
        f"{frontmatter}"
        f"---\n\n{body}\n",
        encoding="utf-8",
    )


class TestSkillsSdkSkillIntakeReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.intake_schema = json.loads(INTAKE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.risk_schema = json.loads(RISK_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schema_store = {
            "skill-intake-review-receipt.v0.schema.json": cls.schema,
            "skill-intake-receipt.v0.schema.json": cls.intake_schema,
            "risk-mode-taxonomy-receipt.v0.schema.json": cls.risk_schema,
            "skill-intake-review-receipt": cls.schema,
            "skill-intake-receipt": cls.intake_schema,
            "risk-mode-taxonomy-receipt": cls.risk_schema,
        }

    def assert_schema_valid(self, payload: dict) -> None:
        """
        Validates a payload against the skill intake review receipt schema.
        
        Parameters:
        	payload (dict): The receipt payload to validate
        """
        _validate_schema_subset(self.schema, payload, self.schema_store)

    def test_builder_consumes_intake_and_risk_mode_receipts(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "review")
        self.assertEqual(receipt["review_decision"], "needs_human_review")
        self.assertEqual(receipt["intake_receipt"]["schema_version"], "skills-sdk.skill-intake-receipt.v0")
        self.assertEqual(receipt["risk_mode_receipt"]["schema_version"], "skills-sdk.risk-mode-taxonomy-receipt.v0")
        self.assertIn("skills-sdk.risk-mode-taxonomy-receipt.v0", receipt["required_receipts"])
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_public_cli_emits_schema_valid_review_receipt(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "intake",
            "review",
            VALID_SKILL,
            "--preview",
            "--json",
            "--robot",
        )

        receipt = payload["data"]["skills_sdk_intake_review"]["receipt"]
        self.assert_schema_valid(receipt)
        self.assertEqual(payload["data"]["skills_sdk_intake_review"]["status"], "review")

    def test_cli_requires_preview(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "intake",
            "review",
            VALID_SKILL,
            "--json",
            "--robot",
            check=False,
        )

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("--preview", payload["errors"][0]["fix_suggestion"])

    def test_clean_skill_can_pass_into_adoption_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: local-fixture\n",
                body="Use this skill to summarize provided project documentation.",
            )

            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["review_decision"], "ready_for_adoption_decision")
        self.assertTrue(all(item["status"] == "pass" for item in receipt["review_items"]))

    def test_blocked_intake_skips_risk_mode_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            source.mkdir()
            (source / "README.md").write_text("not a skill", encoding="utf-8")

            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertIsNone(receipt["risk_mode_receipt"])
        self.assertIsNone(receipt["risk_mode_receipt_digest"])
        self.assertEqual(receipt["review_decision"], "blocked")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_schema_fixture_consumes_risk_mode_receipt(self) -> None:
        payload = json.loads((FIXTURE_DIR / "valid" / "skill-intake-review-receipt.json").read_text(encoding="utf-8"))

        self.assert_schema_valid(payload)
        self.assertEqual(payload["status"], "review")
        self.assertEqual(payload["review_decision"], "needs_human_review")
        self.assertEqual(payload["risk_mode_receipt"]["schema_version"], "skills-sdk.risk-mode-taxonomy-receipt.v0")
        self.assertEqual(
            set(payload["required_receipts"]),
            {"skills-sdk.skill-intake-receipt.v0", "skills-sdk.risk-mode-taxonomy-receipt.v0"},
        )
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["scanner_execution_performed"])
        self.assertFalse(payload["install_performed"])
        self.assertFalse(payload["network_accessed"])
        self.assertFalse(payload["credentials_accessed"])
        self.assertFalse(payload["mutation_performed"])

    def test_schema_rejects_execution_claims(self) -> None:
        payload = json.loads((FIXTURE_DIR / "invalid" / "skill-intake-review-executes.json").read_text(encoding="utf-8"))

        with self.assertRaises(AssertionError):
            self.assert_schema_valid(payload)


if __name__ == "__main__":
    unittest.main()
