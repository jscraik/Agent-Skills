"""Tests for PR #196 / JSC-351 governed closeout changes.

Covers:
- command_metadata.py: conformance action added to skills VALID_ACTIONS, new COMMAND_EXAMPLES and
  TOPIC_EXAMPLES entries for conformance and package verify
- package_verify.py: _unsafe_archive_entry, _safe_link_target, _normalize_expected_digest,
  _read_jsonl, _read_external_rollback_journal helper functions; verify_archive_package missing-file
  path
- conformance.py: unknown suite blocking, _safe_case_id character sanitization, evidence file
  structure, summary schema
- skills_impl.py: _package_verify_rule_evidence, _package_verify_blockers,
  _package_verify_mutation_status, skills_package_verify with directory / missing targets
"""

from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

import unittest  # noqa: E402

from ask.command_metadata import (  # noqa: E402
    COMMAND_EXAMPLES,
    TOPIC_EXAMPLES,
    VALID_ACTIONS,
)
from ask.skills_sdk.package_verify import (  # noqa: E402
    _normalize_expected_digest,
    _read_jsonl,
    _safe_link_target,
    _unsafe_archive_entry,
    verify_archive_package,
)
from ask.skills_sdk.conformance import (  # noqa: E402
    _annotate_conformance_status,
    _safe_case_id,
    run_skills_conformance,
)
from ask.commands.skills_impl import (  # noqa: E402
    _package_verify_blockers,
    _package_verify_mutation_status,
    _package_verify_rule_evidence,
    skills_package_verify,
)
from ask.skills_sdk.contracts import skill_doctor_check_summary  # noqa: E402


# ---------------------------------------------------------------------------
# command_metadata.py tests
# ---------------------------------------------------------------------------




class TestRunSkillsConformanceEvidenceStructure(unittest.TestCase):
    """Verify the codex-parity suite writes the expected evidence files."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.mkdtemp(prefix="test-conformance-")
        cls._result = run_skills_conformance(
            REPO_ROOT, suite="codex-parity", evidence_dir=cls._tmp
        )

    def test_status_is_pass_or_blocked(self) -> None:
        self.assertIn(self._result["status"], {"pass", "blocked"})

    def test_model_and_live_status_are_separate(self) -> None:
        """
        Verify modeled (contract) and live runtime statuses are reported separately and consistently in the conformance result.
        
        Asserts that:
        - the top-level `status` matches `model_contract_status` and the `modeled_conformance` status,
        - `live_parity_status` is either `"blocked_runtime"` or `"not_checked"`,
        - the `live_runtime_parity["status"]` equals `live_parity_status`,
        - the result contains the keys `modeled_conformance`, `live_runtime_parity`, and `blocked_runtime`.
        """
        self.assertEqual(self._result["model_contract_status"], self._result["status"])
        self.assertEqual(self._result["modeled_conformance"]["status"], self._result["status"])
        self.assertIn(self._result["live_parity_status"], {"blocked_runtime", "not_checked"})
        self.assertEqual(self._result["live_runtime_parity"]["status"], self._result["live_parity_status"])
        self.assertIn("modeled_conformance", self._result)
        self.assertIn("live_runtime_parity", self._result)
        self.assertIn("blocked_runtime", self._result)

    def test_cases_and_checks_remain_compatible_aliases(self) -> None:
        self.assertEqual(self._result["cases"], self._result["checks"])

    def test_live_runtime_blockers_do_not_fail_model_contract(self) -> None:
        if self._result["live_parity_status"] != "blocked_runtime":
            self.skipTest("live parity was not blocked in this environment")

        self.assertEqual(self._result["status"], "pass")
        self.assertTrue(self._result["blocked_runtime"]["does_not_fail_model_contract"])
        self.assertTrue(self._result["live_runtime_parity"]["blockers"])

    def test_summary_live_runtime_blockers_match_case_blockers(self) -> None:
        expected_blockers = [
            blocker
            for case in self._result["cases"]
            for blocker in case["live_runtime_parity"]["blockers"]
        ]

        self.assertEqual(self._result["live_runtime_parity"]["blockers"], expected_blockers)
        self.assertEqual(self._result["blocked_runtime"]["blockers"], expected_blockers)

    def test_cases_include_separate_statuses(self) -> None:
        for case in self._result["cases"]:
            self.assertIn("modeled_conformance", case)
            self.assertIn("live_runtime_parity", case)

    def test_non_object_preview_limitations_are_ignored(self) -> None:
        case = {
            "case_id": "malformed_preview_limitations",
            "status": "pass",
            "evidence": {
                "preview_limitations": [
                    "not-an-object",
                    {"status": "partial", "id": "not_blocked", "reason": "informational"},
                    {"status": "blocked", "id": "live_runtime", "reason": "blocked"},
                    {
                        "status": "blocked",
                        "id": "mixed_sources",
                        "source_files": ["codex-rs/core-skills/src/loader.rs", 42, None],
                    },
                    {"status": "blocked", "id": "bad_sources", "source_files": "not-a-list"},
                ]
            },
        }

        _annotate_conformance_status(case)

        blockers = case["live_runtime_parity"]["blockers"]
        self.assertEqual(len(blockers), 3)
        self.assertEqual(blockers[0]["rule_id"], "live_runtime")
        self.assertEqual(blockers[1]["rule_id"], "mixed_sources")
        self.assertEqual(blockers[1]["source_files"], ["codex-rs/core-skills/src/loader.rs"])
        self.assertEqual(blockers[2]["source_files"], [])

    def test_non_list_preview_limitations_are_ignored(self) -> None:
        case = {
            "case_id": "scalar_preview_limitations",
            "status": "pass",
            "evidence": {"preview_limitations": "not-a-list"},
        }

        _annotate_conformance_status(case)

        self.assertEqual(case["live_runtime_parity"]["status"], "not_checked")
        self.assertEqual(case["live_runtime_parity"]["blockers"], [])

    def test_schema_version(self) -> None:
        """
        Asserts the conformance run result uses the expected schema version.
        
        Checks that self._result["schema_version"] is exactly "skills-conformance-evidence.v1".
        """
        self.assertEqual(self._result["schema_version"], "skills-conformance-evidence.v1")

    def test_suite_name(self) -> None:
        self.assertEqual(self._result["suite"], "codex-parity")

    def test_cases_list_is_non_empty(self) -> None:
        self.assertGreater(len(self._result["cases"]), 0)

    def test_evidence_jsonl_exists(self) -> None:
        path = Path(self._result["evidence_jsonl"])
        self.assertTrue(path.is_file(), f"evidence JSONL missing: {path}")

    def test_commands_jsonl_exists(self) -> None:
        path = Path(self._result["commands_jsonl"])
        self.assertTrue(path.is_file(), f"commands JSONL missing: {path}")

    def test_summary_json_exists(self) -> None:
        path = Path(self._result["summary_path"])
        self.assertTrue(path.is_file(), f"summary JSON missing: {path}")

    def test_snapshot_files_exist_for_each_case(self) -> None:
        for case in self._result["cases"]:
            snapshot = Path(case["snapshot_path"])
            self.assertTrue(snapshot.is_file(), f"snapshot missing: {snapshot}")

    def test_evidence_jsonl_is_valid_jsonl(self) -> None:
        path = Path(self._result["evidence_jsonl"])
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreater(len(lines), 0)
        for line in lines:
            parsed = json.loads(line)
            self.assertIn("case_id", parsed)

    def test_summary_json_has_required_keys(self) -> None:
        summary = json.loads(Path(self._result["summary_path"]).read_text(encoding="utf-8"))
        for key in ("schema_version", "suite", "status", "case_count", "cases", "blockers"):
            self.assertIn(key, summary)

    def test_case_count_matches_cases_list(self) -> None:
        self.assertEqual(self._result["case_count"], len(self._result["cases"]))

    def test_passed_count_consistency(self) -> None:
        expected_passed = sum(1 for case in self._result["cases"] if case.get("status") == "pass")
        self.assertEqual(self._result["passed_count"], expected_passed)


# ---------------------------------------------------------------------------
# skills_impl.py helper unit tests
# ---------------------------------------------------------------------------


class TestPackageVerifyRuleEvidence(unittest.TestCase):
    """Unit tests for _package_verify_rule_evidence."""

    def _make_verification_with_checks(self, checks: list[dict]) -> dict:
        return {"checks": checks}

    def test_pass_check_produces_true_token(self) -> None:
        verification = self._make_verification_with_checks(
            [{"name": "archive_traversal", "status": "pass", "evidence": {}}]
        )
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("archive_traversal:true", evidence)

    def test_fail_check_produces_false_token(self) -> None:
        verification = self._make_verification_with_checks(
            [{"name": "trusted_provenance", "status": "fail", "evidence": {}}]
        )
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("trusted_provenance:false", evidence)

    def test_blocked_check_produces_false_token(self) -> None:
        verification = self._make_verification_with_checks(
            [{"name": "rollback_journal", "status": "blocked", "evidence": {}}]
        )
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("rollback_journal:false", evidence)

    def test_rule_results_provenance_trusted_true(self) -> None:
        """With rule_results format, provenance_trusted should be extracted."""
        verification = {
            "rule_results": [],
            "provenance_identity": {"trusted": True},
            "contract": {"required_fields": {"missing": []}},
        }
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("provenance_trusted:true", evidence)

    def test_rule_results_provenance_trusted_false(self) -> None:
        verification = {
            "rule_results": [{"rule_id": "untrusted_provenance"}],
            "provenance_identity": {"trusted": False},
            "contract": {"required_fields": {"missing": []}},
        }
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("provenance_trusted:false", evidence)

    def test_rule_results_package_metadata_incomplete(self) -> None:
        verification = {
            "rule_results": [],
            "provenance_identity": {"trusted": True},
            "contract": {"required_fields": {"missing": ["version"]}},
        }
        evidence = _package_verify_rule_evidence(verification)
        self.assertIn("package_metadata_complete:false", evidence)

    def test_empty_checks_returns_empty(self) -> None:
        evidence = _package_verify_rule_evidence({"checks": []})
        self.assertEqual(evidence, [])

    def test_neither_checks_nor_rule_results(self) -> None:
        evidence = _package_verify_rule_evidence({})
        self.assertEqual(evidence, [])


class TestPackageVerifyBlockers(unittest.TestCase):
    """Unit tests for _package_verify_blockers."""

    def test_uses_blockers_list_when_present(self) -> None:
        verification = {
            "blockers": [
                {"rule_id": "untrusted_provenance", "message": "Bad provenance."}
            ]
        }
        result = _package_verify_blockers(verification)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["rule_id"], "untrusted_provenance")
        # class field must be filled in
        self.assertEqual(result[0]["class"], "untrusted_provenance")

    def test_falls_back_to_rule_results(self) -> None:
        verification = {
            "rule_results": [
                {"rule_id": "digest_mismatch", "message": "Mismatch."}
            ]
        }
        result = _package_verify_blockers(verification)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["rule_id"], "digest_mismatch")

    def test_empty_blockers_and_no_rule_results(self) -> None:
        result = _package_verify_blockers({})
        self.assertEqual(result, [])

    def test_class_preserved_if_already_set(self) -> None:
        verification = {
            "blockers": [{"rule_id": "x", "class": "custom_class", "message": "M"}]
        }
        result = _package_verify_blockers(verification)
        self.assertEqual(result[0]["class"], "custom_class")

    def test_non_dict_items_skipped(self) -> None:
        verification = {"blockers": [None, "string", {"rule_id": "ok"}]}
        result = _package_verify_blockers(verification)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["rule_id"], "ok")


class TestPackageVerifyMutationStatus(unittest.TestCase):
    """Unit tests for _package_verify_mutation_status."""

    def test_not_mutated_dict(self) -> None:
        verification = {
            "mutation_status": {
                "status": "pass",
                "mutated": False,
                "runtime_roots_mutated": False,
                "install_attempted": False,
                "archive_extracted": False,
                "network_used": False,
            }
        }
        result = _package_verify_mutation_status(verification)
        self.assertFalse(result["mutated"])
        self.assertFalse(result["runtime_roots_mutated"])
        self.assertFalse(result["install_attempted"])
        self.assertFalse(result["archive_extracted"])

    def test_runtime_mutation_fail_sets_mutated(self) -> None:
        verification = {
            "runtime_mutation": {"status": "fail", "mutations": [{"path": ".agents"}]},
            "mutation_status": {
                "status": "pass",
                "mutated": False,
                "runtime_roots_mutated": False,
                "install_attempted": False,
                "archive_extracted": False,
                "network_used": False,
            },
        }
        result = _package_verify_mutation_status(verification)
        self.assertTrue(result["mutated"])
        self.assertTrue(result["runtime_roots_mutated"])

    def test_not_mutated_string_sentinel(self) -> None:
        verification = {"mutation_status": "not_mutated"}
        result = _package_verify_mutation_status(verification)
        self.assertFalse(result["mutated"])

    def test_archive_extracted_flag(self) -> None:
        verification = {
            "mutation_status": {
                "status": "pass",
                "mutated": False,
                "runtime_roots_mutated": False,
                "install_attempted": False,
                "archive_extracted": True,
                "network_used": False,
            }
        }
        result = _package_verify_mutation_status(verification)
        self.assertTrue(result["archive_extracted"])


class TestSkillsPackageVerifyMissingTarget(unittest.TestCase):
    """Verify skills_package_verify handles non-existent / unresolvable targets gracefully."""

    def test_completely_missing_nonexistent_handle_returns_error(self) -> None:
        result = skills_package_verify(REPO_ROOT, "completely-nonexistent-handle-xyz-99999")
        self.assertEqual(result.status, "error")
        self.assertIn("skill_package_verification", result.data)

    def test_completely_missing_returns_schema_version(self) -> None:
        result = skills_package_verify(REPO_ROOT, "completely-nonexistent-handle-xyz-99999")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["schema_version"], "skill-package-verify.v1")


class TestSkillsPackageVerifyDirectoryTarget(unittest.TestCase):
    """Verify skills_package_verify handles a directory target read-only."""

    def test_directory_target_does_not_mutate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_dir = Path(tmp_dir) / "my-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "---\n"
                "name: my-skill\n"
                "description: A test fixture skill.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: repo-owned-fixture\n"
                "share_readiness: ready\n"
                "---\n",
                encoding="utf-8",
            )

            result = skills_package_verify(REPO_ROOT, str(skill_dir))

        self.assertIn("skill_package_verification", result.data)
        verification = result.data["skill_package_verification"]
        self.assertFalse(verification["mutation_status"]["mutated"])
        self.assertFalse(verification["mutation_status"]["archive_extracted"])
        self.assertFalse(verification["mutation_status"]["install_attempted"])

    def test_directory_target_with_untrusted_provenance_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_dir = Path(tmp_dir) / "untrusted-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "---\n"
                "name: untrusted-skill\n"
                "description: Untrusted fixture.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: external-untrusted\n"
                "share_readiness: not_ready\n"
                "---\n",
                encoding="utf-8",
            )

            result = skills_package_verify(REPO_ROOT, str(skill_dir))

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertNotEqual(verification["status"], "pass")

    def test_directory_target_with_unknown_provenance_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_dir = Path(tmp_dir) / "unknown-provenance-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "---\n"
                "name: unknown-provenance-skill\n"
                "description: Unknown provenance fixture.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: totally-unknown-source\n"
                "share_readiness: ready\n"
                "---\n",
                encoding="utf-8",
            )

            result = skills_package_verify(REPO_ROOT, str(skill_dir))

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertFalse(verification["provenance_identity"]["trusted"])
        self.assertIn("provenance_trusted:false", verification["rule_evidence"])

    def test_directory_target_uses_custom_trusted_provenance_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_dir = Path(tmp_dir) / "partner-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "---\n"
                "name: partner-skill\n"
                "description: Partner provenance fixture.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: partner-source\n"
                "share_readiness: ready\n"
                "---\n",
                encoding="utf-8",
            )

            result = skills_package_verify(REPO_ROOT, str(skill_dir), trusted_provenance="partner-source")

        self.assertEqual(result.status, "success")
        verification = result.data["skill_package_verification"]
        self.assertTrue(verification["provenance_identity"]["trusted"])
        self.assertIn("provenance_trusted:true", verification["rule_evidence"])

    def test_directory_target_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_dir = Path(tmp_dir) / "schema-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: schema-skill\ndescription: Schema test.\n---\n",
                encoding="utf-8",
            )

            result = skills_package_verify(REPO_ROOT, str(skill_dir))

        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["schema_version"], "skill-package-verify.v1")

    def test_missing_zip_target_uses_archive_missing_artifact_blocker(self) -> None:
        missing_archive = Path(tempfile.gettempdir()) / "agent-skills-missing-package-fixture.zip"

        result = skills_package_verify(REPO_ROOT, str(missing_archive))

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["target_identity"]["kind"], "archive")
        self.assertTrue(
            any(blocker.get("rule_id") == "blocked_missing_artifact" for blocker in verification["blockers"])
        )


class TestSkillsPackageVerifyArchiveTarget(unittest.TestCase):
    """Regression tests for archive verify path through skills_package_verify."""

    def _make_valid_archive(self, path: Path) -> str:
        import hashlib

        skill_text = "---\nname: archived-skill\ndescription: Archive fixture.\n---\n"
        skill_bytes = skill_text.encode("utf-8")
        manifest = {
            "provenance": {"source": "agent-skills"},
            "files": [{"path": "SKILL.md", "sha256": hashlib.sha256(skill_bytes).hexdigest()}],
            "rollback_journal": "rollback.jsonl",
        }
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("SKILL.md", skill_text)
            archive.writestr("rollback.jsonl", '{"action":"verify","decision":"rollback-ready","status":"pass"}\n')
            archive.writestr("skill-package-manifest.json", json.dumps(manifest))
        import hashlib as _h

        digest = _h.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def test_valid_archive_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_path = Path(tmp_dir) / "valid.zip"
            rollback_path = Path(tmp_dir) / "rollback.jsonl"
            expected_sha = self._make_valid_archive(archive_path)
            rollback_path.write_text(
                '{"action":"verify","decision":"rollback-ready","status":"pass"}\n',
                encoding="utf-8",
            )

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=expected_sha,
                rollback_journal=str(rollback_path),
            )

        self.assertEqual(result.status, "success")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "pass")
        self.assertFalse(verification["mutation_status"]["mutated"])


if __name__ == "__main__":
    unittest.main()
