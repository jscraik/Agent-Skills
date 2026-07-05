import argparse
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

from ask.commands.sdk_intake import dispatch_sdk_intake  # noqa: E402
from ask.skills_sdk.skill_intake_review import build_skill_intake_review_receipt  # noqa: E402


VALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/skill-intake-review-receipt.v0.schema.json"
INTAKE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/skill-intake-receipt.v0.schema.json"
RISK_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/risk-mode-taxonomy-receipt.v0.schema.json"
PACKAGE_SECURITY_SCHEMA_PATH = (
    REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/package-security-signature-receipt.v0.schema.json"
)
FIXTURE_DIR = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine"


def _command_env() -> dict[str, str]:
    """
    Create an environment dictionary for test subprocess execution with isolated cache and state directories.
    
    Configures XDG, mise, and uv cache/state variables to use deterministic temporary directories,
    preventing test execution from polluting the system's actual cache and state locations.
    MISE_TRUSTED_CONFIG_PATHS is set to the repository's .mise.toml file.
    
    Returns:
    	dict[str, str]: Environment variables configured with isolated cache/state paths.
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
    Executes a command and returns its JSON output.
    
    Parameters:
        *args (str): Command and arguments to execute.
        check (bool): If True, raise AssertionError on non-zero exit code.
    
    Returns:
        dict: Parsed JSON from the command's standard output.
    
    Raises:
        AssertionError: If check is True and the command fails (non-zero exit code).
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
    Create a minimal skill directory fixture.
    
    Creates the directory at source and writes a SKILL.md file containing YAML 
    frontmatter (with name and description fields) followed by optional additional 
    frontmatter and body content.
    
    Parameters:
        source (Path): Directory path where the skill fixture will be created.
        body (str): Markdown body content to append after the frontmatter.
        frontmatter (str): Optional additional YAML frontmatter lines (default: "").
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
        cls.package_security_schema = json.loads(PACKAGE_SECURITY_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schema_store = {
            "skill-intake-review-receipt.v0.schema.json": cls.schema,
            "skill-intake-receipt.v0.schema.json": cls.intake_schema,
            "package-security-signature-receipt.v0.schema.json": cls.package_security_schema,
            "risk-mode-taxonomy-receipt.v0.schema.json": cls.risk_schema,
            "skill-intake-review-receipt": cls.schema,
            "skill-intake-receipt": cls.intake_schema,
            "package-security-signature-receipt": cls.package_security_schema,
            "risk-mode-taxonomy-receipt": cls.risk_schema,
        }

    def assert_schema_valid(self, payload: dict) -> None:
        """
        Assert that a receipt payload conforms to the skill intake review receipt schema.
        """
        _validate_schema_subset(self.schema, payload, self.schema_store)

    def test_builder_consumes_intake_and_risk_mode_receipts(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "review")
        self.assertEqual(receipt["review_decision"], "needs_human_review")
        self.assertEqual(receipt["intake_receipt"]["schema_version"], "skills-sdk.skill-intake-receipt.v0")
        self.assertEqual(receipt["risk_mode_receipt"]["schema_version"], "skills-sdk.risk-mode-taxonomy-receipt.v0")

    def test_schema_rejects_inconsistent_status_conditionals(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        pass_receipt = json.loads(json.dumps(receipt))
        for item in pass_receipt["review_items"]:
            item["status"] = "pass"
        pass_receipt["status"] = "pass"
        pass_receipt["review_decision"] = "ready_for_adoption_decision"
        pass_receipt["skill_id"] = None
        with self.assertRaises(AssertionError):
            self.assert_schema_valid(pass_receipt)

        blocked_receipt = json.loads(json.dumps(receipt))
        blocked_receipt["status"] = "blocked"
        blocked_receipt["review_decision"] = "blocked"
        blocked_receipt["risk_mode_receipt"] = None
        blocked_receipt["risk_mode_receipt_digest"] = None
        blocked_receipt["package_id"] = "unexpected-package"
        blocked_receipt["package_digest"] = "sha256:" + "a" * 64
        blocked_receipt["review_items"][0]["status"] = "block"
        with self.assertRaises(AssertionError):
            self.assert_schema_valid(blocked_receipt)
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
            {
                "skills-sdk.skill-intake-receipt.v0",
                "skills-sdk.package-security-signature-receipt.v0",
                "skills-sdk.risk-mode-taxonomy-receipt.v0",
            },
        )
        self.assertEqual(
            payload["package_security_signature_receipt"]["schema_version"],
            "skills-sdk.package-security-signature-receipt.v0",
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

    def test_review_items_cover_all_eight_review_dimensions(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        item_ids = {item["id"] for item in receipt["review_items"]}
        expected_ids = {
            "provenance",
            "permissions",
            "data_exposure",
            "action_surface",
            "isolation",
            "semantic_behavior",
            "approval_friction",
            "risk_modes",
        }
        self.assertEqual(item_ids, expected_ids)

    def test_provenance_via_owner_field_passes_provenance_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="owner: my-team\n",
                body="Summarize provided documents.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        provenance_item = next(i for i in receipt["review_items"] if i["id"] == "provenance")
        self.assertEqual(provenance_item["status"], "pass")
        self.assertEqual(provenance_item["verdict"], "declared")

    def test_skill_with_data_exposure_terms_flags_data_exposure_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Read the API token and include in transcript output.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        data_item = next(i for i in receipt["review_items"] if i["id"] == "data_exposure")
        self.assertEqual(data_item["status"], "review")

    def test_skill_with_action_surface_and_approval_language_passes_approval_friction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Commit changes only after explicit approval and preview.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        approval_item = next(i for i in receipt["review_items"] if i["id"] == "approval_friction")
        self.assertEqual(approval_item["status"], "pass")

    def test_skill_with_action_surface_without_approval_language_flags_approval_friction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Commit the changes to the repository immediately.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        approval_item = next(i for i in receipt["review_items"] if i["id"] == "approval_friction")
        self.assertEqual(approval_item["status"], "review")

    def test_blocked_receipt_has_null_risk_mode_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            source.mkdir()
            (source / "README.md").write_text("not a skill", encoding="utf-8")

            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        self.assertIsNone(receipt["risk_mode_receipt"])
        self.assertIsNone(receipt["risk_mode_receipt_digest"])
        self.assertIsNone(receipt["package_id"])
        self.assertIsNone(receipt["package_digest"])
        self.assertEqual(receipt["review_decision"], "blocked")

    def test_residual_risk_contains_risk_mode_and_review_item_entries(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        risk_mode_entries = [r for r in receipt["residual_risk"] if r.startswith("risk_mode:")]
        review_item_entries = [r for r in receipt["residual_risk"] if r.startswith("review_item:")]
        self.assertTrue(len(risk_mode_entries) > 0 or len(review_item_entries) > 0)
        for entry in receipt["residual_risk"]:
            self.assertTrue(
                entry.startswith("risk_mode:") or entry.startswith("review_item:"),
                f"Unexpected residual_risk entry format: {entry}",
            )

    def test_receipt_records_non_mutation_boundary(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["scanner_execution_performed"])
        self.assertFalse(receipt["install_performed"])
        self.assertFalse(receipt["projection_mutation_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["credentials_accessed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_agent_summary_contains_skill_id(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assertIn("skills-sdk-valid-fixture", receipt["agent_summary"])

    def test_receipt_includes_required_acceptance_trace_items(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assertIn("PU-034", receipt["acceptance_trace"])
        self.assertIn("FR-008", receipt["acceptance_trace"])
        self.assertIn("SEC-001", receipt["acceptance_trace"])

    def test_isolation_review_item_always_passes_when_intake_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Read documents.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        isolation_item = next(i for i in receipt["review_items"] if i["id"] == "isolation")
        self.assertEqual(isolation_item["status"], "pass")
        self.assertEqual(isolation_item["verdict"], "quarantined")

    def test_review_status_matches_review_decision(self) -> None:
        receipt = build_skill_intake_review_receipt(REPO_ROOT, source=VALID_SKILL)

        if receipt["status"] == "pass":
            self.assertEqual(receipt["review_decision"], "ready_for_adoption_decision")
        elif receipt["status"] == "review":
            self.assertEqual(receipt["review_decision"], "needs_human_review")
        elif receipt["status"] == "blocked":
            self.assertEqual(receipt["review_decision"], "blocked")
        else:
            self.fail(f"Unexpected review status: {receipt['status']}")

    def test_scripted_package_requires_permission_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Summarize provided documents.",
            )
            scripts = source / "scripts"
            scripts.mkdir()
            (scripts / "run.sh").write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        permissions_item = next(i for i in receipt["review_items"] if i["id"] == "permissions")
        self.assertEqual(receipt["risk_mode_receipt"]["source_kind"], "scripted")
        self.assertEqual(permissions_item["status"], "review")
        self.assertIn("source_kind:scripted", permissions_item["evidence"])

    def test_review_contract_rejects_archive_source_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external.zip"
            source.write_bytes(b"not a real archive")
            with self.assertRaisesRegex(ValueError, "directory source_kind only"):
                build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix(), source_kind="archive")

    def test_required_receipts_always_lists_all_schema_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            _write_skill(
                source,
                frontmatter="provenance: test\n",
                body="Safe docs.",
            )
            receipt = build_skill_intake_review_receipt(REPO_ROOT, source=source.as_posix())

        self.assertIn("skills-sdk.skill-intake-receipt.v0", receipt["required_receipts"])
        self.assertIn("skills-sdk.package-security-signature-receipt.v0", receipt["required_receipts"])
        self.assertIn("skills-sdk.risk-mode-taxonomy-receipt.v0", receipt["required_receipts"])
        self.assertEqual(
            receipt["package_security_signature_receipt"]["schema_version"],
            "skills-sdk.package-security-signature-receipt.v0",
        )


class TestDispatchSdkIntakeRouting(unittest.TestCase):
    def _make_args(self, **kwargs) -> argparse.Namespace:
        """
        Build an argument namespace for dispatcher testing.
        
        Parameters:
            **kwargs: Configuration overrides. Defaults are json=True, robot=True, verbose=False.
        
        Returns:
            argparse.Namespace: Argument namespace with defaults and overrides applied.
        """
        defaults = {
            "json": True,
            "robot": True,
            "verbose": False,
        }
        defaults.update(kwargs)
        return argparse.Namespace(**defaults)

    def test_dispatch_returns_error_for_unknown_intake_action(self) -> None:
        args = self._make_args(intake_action="nonexistent_action")
        result = dispatch_sdk_intake(REPO_ROOT, args)

        self.assertEqual(result.status, "error")
        self.assertTrue(len(result.errors) > 0)
        self.assertIn("nonexistent_action", result.errors[0].message)

    def test_dispatch_returns_error_for_review_without_preview(self) -> None:
        args = self._make_args(
            intake_action="review",
            source=VALID_SKILL,
            source_kind="directory",
            preview=False,
        )
        result = dispatch_sdk_intake(REPO_ROOT, args)

        self.assertEqual(result.status, "error")
        self.assertTrue(len(result.errors) > 0)
        self.assertIn("--preview", result.errors[0].fix_suggestion)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_dispatch_returns_error_for_inspect_without_preview(self) -> None:
        args = self._make_args(
            intake_action="inspect",
            source=VALID_SKILL,
            source_kind="directory",
            preview=False,
        )
        result = dispatch_sdk_intake(REPO_ROOT, args)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_dispatch_routes_review_with_preview_to_implementation(self) -> None:
        args = self._make_args(
            intake_action="review",
            source=VALID_SKILL,
            source_kind="directory",
            preview=True,
        )
        result = dispatch_sdk_intake(REPO_ROOT, args)

        self.assertIn("skills_sdk_intake_review", result.data)
        payload = result.data["skills_sdk_intake_review"]
        self.assertIn(payload["status"], ("pass", "review", "blocked"))


if __name__ == "__main__":
    unittest.main()
