import hashlib
import json
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills_impl import (  # noqa: E402
    skills_conformance_run,
    skills_package_verify,
)
from ask.skills_sdk.package_verify import verify_skill_directory  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_rollback_journal(path: Path) -> None:
    path.write_text(
        json.dumps({"action": "verify", "decision": "rollback-ready", "status": "pass"}) + "\n",
        encoding="utf-8",
    )


def _write_package_archive(
    path: Path,
    *,
    provenance_source: str = "agent-skills",
    provenance_trusted: bool | None = None,
    rollback_path: str = "rollback.jsonl",
    skill_digest: str | None = None,
) -> str:
    skill_text = "---\nname: sample-skill\ndescription: Use when verifying sample packages.\n---\n"
    skill_bytes = skill_text.encode("utf-8")
    provenance = {"source": provenance_source}
    if provenance_trusted is not None:
        provenance["trusted"] = provenance_trusted
    manifest = {
        "provenance": provenance,
        "files": [{"path": "SKILL.md", "sha256": skill_digest or hashlib.sha256(skill_bytes).hexdigest()}],
        "rollback_journal": rollback_path,
    }
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("SKILL.md", skill_text)
        archive.writestr(rollback_path, '{"action":"verify","decision":"rollback-ready","status":"pass"}\n')
        archive.writestr("skill-package-manifest.json", json.dumps(manifest))
    return _sha256(path)


class TestAskSkillsConformance(unittest.TestCase):
    def test_package_verify_accepts_staged_archive_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            expected_digest = _write_package_archive(archive_path)
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=expected_digest,
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "success")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["schema_version"], "skill-package-verify.v1")
        self.assertEqual(verification["status"], "pass")
        self.assertFalse(verification["mutation_status"]["mutated"])
        self.assertFalse(verification["mutation_status"]["install_attempted"])
        self.assertFalse(verification["mutation_status"]["archive_extracted"])
        check_names = {check["name"]: check["status"] for check in verification["checks"]}
        self.assertEqual(check_names["archive_traversal"], "pass")
        self.assertEqual(check_names["symlink_escape"], "pass")
        self.assertEqual(check_names["archive_digest_match"], "pass")
        self.assertEqual(check_names["trusted_provenance"], "pass")
        self.assertEqual(check_names["rollback_journal"], "pass")
        self.assertEqual(check_names["no_runtime_mutation"], "pass")

    def test_package_verify_blocks_untrusted_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            expected_digest = _write_package_archive(archive_path, provenance_source="untrusted")
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=expected_digest,
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "blocked")
        self.assertTrue(any(item["rule_id"] == "untrusted_provenance" for item in verification["blockers"]))
        self.assertIn("trusted_provenance:false", verification["rule_evidence"])

    def test_package_verify_blocks_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            _write_package_archive(archive_path)
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256="0" * 64,
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "digest_mismatch" for item in verification["blockers"]))
        self.assertFalse(verification["mutation_status"]["archive_extracted"])

    def test_package_verify_blocks_unsafe_archive_member(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape/SKILL.md", "---\nname: escape\n---\n")
                archive.writestr("rollback.jsonl", '{"action":"verify","decision":"blocked"}\n')
                archive.writestr("skill-package-manifest.json", json.dumps({"provenance": {"source": "agent-skills"}, "files": [], "rollback_journal": "rollback.jsonl"}))
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=_sha256(archive_path),
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "archive_path_traversal" for item in verification["blockers"]))

    def test_package_verify_blocks_unsafe_archive_directory_member(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            directory_info = zipfile.ZipInfo("../escape/")
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(directory_info, "")
                archive.writestr("rollback.jsonl", '{"action":"verify","decision":"blocked"}\n')
                archive.writestr(
                    "skill-package-manifest.json",
                    json.dumps({"provenance": {"source": "agent-skills"}, "files": [], "rollback_journal": "rollback.jsonl"}),
                )
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=_sha256(archive_path),
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "archive_path_traversal" for item in verification["blockers"]))

    def test_package_verify_blocks_absolute_root_archive_member(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            root_info = zipfile.ZipInfo("/")
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(root_info, "")
                archive.writestr("rollback.jsonl", '{"action":"verify","decision":"blocked"}\n')
                archive.writestr(
                    "skill-package-manifest.json",
                    json.dumps({"provenance": {"source": "agent-skills"}, "files": [], "rollback_journal": "rollback.jsonl"}),
                )
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=_sha256(archive_path),
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "absolute_archive_path" for item in verification["blockers"]))

    def test_package_verify_rejects_manifest_self_attested_trust(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            expected_digest = _write_package_archive(
                archive_path,
                provenance_source="external-untrusted",
                provenance_trusted=True,
            )
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=expected_digest,
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "untrusted_provenance" for item in verification["blockers"]))

    def test_package_verify_blocks_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            symlink_info = zipfile.ZipInfo("sample-skill/link")
            symlink_info.create_system = 3
            symlink_info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(symlink_info, "../../outside")
                archive.writestr("rollback.jsonl", '{"action":"verify","decision":"blocked"}\n')
                archive.writestr("skill-package-manifest.json", json.dumps({"provenance": {"source": "agent-skills"}, "files": [], "rollback_journal": "rollback.jsonl"}))
            _write_rollback_journal(rollback_journal)

            result = skills_package_verify(
                REPO_ROOT,
                str(archive_path),
                expected_sha256=_sha256(archive_path),
                rollback_journal=str(rollback_journal),
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "archive_symlink_escape" for item in verification["blockers"]))

    def test_package_verify_blocks_missing_rollback_journal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("SKILL.md", "---\nname: sample-skill\ndescription: Fixture.\n---\n")
                archive.writestr(
                    "skill-package-manifest.json",
                    json.dumps({"provenance": {"source": "agent-skills"}, "files": []}),
                )
            expected_digest = _sha256(archive_path)

            result = skills_package_verify(REPO_ROOT, str(archive_path), expected_sha256=expected_digest)

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertTrue(any(item["rule_id"] == "rollback_journal_missing" for item in verification["blockers"]))

    def test_directory_verify_requires_trusted_provenance_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = Path(temp_dir) / "sample" / "SKILL.md"
            skill_md.parent.mkdir()
            skill_md.write_text(
                "---\n"
                "name: sample-skill\n"
                "description: Use when verifying sample packages.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: external-untrusted\n"
                "share_readiness: ready\n"
                "---\n",
                encoding="utf-8",
            )

            verification = verify_skill_directory(REPO_ROOT, skill_md, str(skill_md.parent))

        self.assertEqual(verification["status"], "blocked")
        self.assertFalse(verification["provenance_identity"]["trusted"])
        self.assertTrue(any(item["rule_id"] == "untrusted_provenance" for item in verification["blockers"]))

    def test_directory_verify_blocks_empty_reference_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_md = Path(temp_dir) / "sample" / "SKILL.md"
            references_dir = skill_md.parent / "references"
            references_dir.mkdir(parents=True)
            skill_md.write_text(
                "---\n"
                "name: sample-skill\n"
                "description: Use when verifying sample packages.\n"
                "version: 1.0.0\n"
                "compatible_roles: default\n"
                "runtime_needs: local files\n"
                "maturity: fixture\n"
                "provenance: agent-skills\n"
                "share_readiness: ready\n"
                "---\n",
                encoding="utf-8",
            )
            (references_dir / "context.md").write_text("\n", encoding="utf-8")

            verification = verify_skill_directory(REPO_ROOT, skill_md, str(skill_md.parent))

        self.assertEqual(verification["status"], "blocked")
        self.assertEqual(
            verification["sdk_contract"]["values"]["reference_quality"]["status"],
            "blocked_validation",
        )
        self.assertTrue(
            any(item["rule_id"] == "reference_quality_blocked" for item in verification["blockers"])
        )
        self.assertEqual(
            {check["name"]: check["status"] for check in verification["checks"]}["reference_quality"],
            "fail",
        )

    def test_handle_verify_preserves_branch_rule_evidence(self) -> None:
        result = skills_package_verify(REPO_ROOT, "skill-builder")

        self.assertEqual(result.status, "success")
        verification = result.data["skill_package_verification"]
        rule_evidence = verification["rule_evidence"]
        self.assertIn("skill_md_present:true", rule_evidence)
        self.assertIn("frontmatter_read:true", rule_evidence)
        self.assertIn("package_metadata_complete:true", rule_evidence)
        self.assertIn("reference_quality:true", rule_evidence)
        self.assertIn("provenance_trusted:true", rule_evidence)

    def test_conformance_run_writes_replayable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = skills_conformance_run(
                REPO_ROOT,
                suite="codex-parity",
                evidence_dir=temp_dir,
            )
            conformance = result.data["skills_conformance"]
            evidence_dir = Path(conformance["evidence_dir"])

            self.assertIn(result.status, {"success", "error"})
            self.assertEqual(conformance["schema_version"], "skills-conformance-evidence.v1")
            self.assertIn(conformance["status"], {"pass", "blocked"})
            self.assertGreaterEqual(len(conformance["cases"]), 6)
            self.assertTrue(Path(conformance["evidence_jsonl"]).is_file())
            for case in conformance["cases"]:
                self.assertTrue(Path(case["snapshot_path"]).is_file())
            if conformance["status"] == "blocked":
                self.assertTrue(conformance["blockers"])

    def test_cli_exposes_package_verify_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "skill.zip"
            rollback_journal = Path(temp_dir) / "rollback.jsonl"
            expected_digest = _write_package_archive(archive_path)
            _write_rollback_journal(rollback_journal)
            cmd = [
                "python3",
                "Infrastructure/bin/ask",
                "skills",
                "package",
                "verify",
                str(archive_path),
                "--expected-sha256",
                expected_digest,
                "--rollback-journal",
                str(rollback_journal),
                "--json",
                "--robot",
            ]
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["status"], "success")
        self.assertIn("trace_id", output)
        self.assertIsInstance(output["metadata"], dict)
        self.assertTrue(output["metadata"]["command"].startswith("skills package verify "))
        self.assertIn("--expected-sha256", output["metadata"]["command"])
        self.assertIn("--rollback-journal", output["metadata"]["command"])
        self.assertIn("skill_package_verification", output["data"])
        self.assertEqual(output["errors"], [])
        verification = output["data"]["skill_package_verification"]
        self.assertEqual(verification["schema_version"], "skill-package-verify.v1")
        self.assertIn("next_command", verification)
        self.assertIn("checks", verification)
        self.assertEqual(verification["status"], "pass")
        self.assertFalse(verification["mutation_status"]["runtime_roots_mutated"])

    def test_cli_exposes_conformance_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = [
                "python3",
                "Infrastructure/bin/ask",
                "skills",
                "conformance",
                "run",
                "--suite",
                "codex-parity",
                "--evidence-dir",
                temp_dir,
                "--json",
                "--robot",
            ]
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)

        self.assertIn(result.returncode, {0, 2}, result.stderr)
        output = json.loads(result.stdout)
        self.assertIn(output["status"], {"success", "error"})
        self.assertIn("trace_id", output)
        self.assertIsInstance(output["metadata"], dict)
        self.assertTrue(output["metadata"]["command"].startswith("skills conformance run "))
        self.assertIn("--suite codex-parity", output["metadata"]["command"])
        self.assertIn("--evidence-dir", output["metadata"]["command"])
        self.assertIn("skills_conformance", output["data"])
        conformance = output["data"]["skills_conformance"]
        self.assertEqual(conformance["schema_version"], "skills-conformance-evidence.v1")
        self.assertIn("cases", conformance)
        self.assertIn("checks", conformance)
        self.assertIn(conformance["status"], {"pass", "blocked"})


if __name__ == "__main__":
    unittest.main()
