"""Disposable-home acceptance and adversarial proof for temporary installs."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/lib"))

from ask.skills_sdk import runtime_adapters, transitional_installs  # noqa: E402


class TestTransitionalInstalls(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.home = self.root / "home"
        self.package = self.home / ".agents/skills/testing"
        self.package.mkdir(parents=True)
        (self.package / "SKILL.md").write_text("# Testing\n", encoding="utf-8")
        (self.package / "references").mkdir()
        (self.package / "references/guide.md").write_text("Complete resource\n", encoding="utf-8")
        descriptor = os.open(self.package, transitional_installs.DIRECTORY_FLAGS)
        try:
            identity, count = transitional_installs.package_identity(descriptor)
        finally:
            os.close(descriptor)
        self.record = self.repo / transitional_installs.IDENTITY_RECORD
        self.record.parent.mkdir(parents=True)
        self.manifest = {"schema_version": transitional_installs.SCHEMA, "packages": {
            "testing": {"approval": "jamie-temporary-sdk-exemption", "sha256": identity,
                        "file_count": count, "source_ref": "independently-approved-test-source"},
        }}
        self.write_record()

    def write_record(self) -> None:
        self.record.write_text(json.dumps(self.manifest), encoding="utf-8")

    def verify(self, handle: str = "testing") -> dict:
        return transitional_installs.verify_transitional_install(
            repo_root=self.repo, home=self.home, handle=handle,
        )

    def test_approved_complete_copy_passes_without_sdk_or_invocation_claim(self) -> None:
        result = self.verify()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["classification"], "verified_transitional_copy")
        self.assertFalse(result["sdk_clearance"])
        self.assertFalse(result["live_invocation_verified"])
        self.assertEqual(result["file_count"], 2)

    def test_missing_tampered_extra_and_mode_changed_resources_fail(self) -> None:
        resource = self.package / "references/guide.md"
        original = resource.read_bytes()
        for mutation in ("missing", "tampered", "extra", "executable"):
            with self.subTest(mutation=mutation):
                resource.write_bytes(original)
                resource.chmod(0o644)
                if mutation == "missing":
                    resource.unlink()
                elif mutation == "tampered":
                    resource.write_text("Tampered\n", encoding="utf-8")
                elif mutation == "extra":
                    (self.package / "extra").write_text("unapproved", encoding="utf-8")
                else:
                    resource.chmod(0o755)
                self.assertEqual(self.verify()["status"], "fail")
                (self.package / "extra").unlink(missing_ok=True)

    def test_unapproved_and_traversal_handles_fail(self) -> None:
        for handle in ("unselected", "../testing", "/testing", "testing/../testing", ""):
            with self.subTest(handle=handle):
                self.assertEqual(self.verify(handle)["status"], "fail")

    def test_package_and_resource_symlinks_fail(self) -> None:
        resource = self.package / "references/guide.md"
        outside = self.root / "outside.md"
        outside.write_bytes(resource.read_bytes())
        resource.unlink()
        resource.symlink_to(outside)
        self.assertEqual(self.verify()["status"], "fail")
        resource.unlink()
        resource.write_bytes(outside.read_bytes())
        moved = self.package.with_name("preserved")
        self.package.rename(moved)
        self.package.symlink_to(moved, target_is_directory=True)
        self.assertEqual(self.verify()["status"], "fail")

    def test_parent_alias_and_nested_directory_links_fail(self) -> None:
        references = self.package / "references"
        preserved = self.root / "references"
        references.rename(preserved)
        references.symlink_to(preserved, target_is_directory=True)
        self.assertEqual(self.verify()["status"], "fail")
        references.unlink()
        preserved.rename(references)
        skills = self.package.parent
        preserved_root = self.root / "skills"
        skills.rename(preserved_root)
        skills.symlink_to(preserved_root, target_is_directory=True)
        self.assertEqual(self.verify()["status"], "fail")

    def test_special_resource_fails_without_opening_fifo(self) -> None:
        os.mkfifo(self.package / "unexpected-fifo")
        self.assertEqual(self.verify()["status"], "fail")

    def test_empty_directories_and_depth_consume_the_verifier_budget(self) -> None:
        for index in range(5):
            (self.package / f"empty-{index}").mkdir()
        with patch.object(transitional_installs, "MAX_FILES", 4):
            self.assertEqual(self.verify()["status"], "fail")
        nested = self.package / "empty-0/a/b/c"
        nested.mkdir(parents=True)
        with patch.object(transitional_installs, "MAX_DEPTH", 2):
            self.assertEqual(self.verify()["status"], "fail")

    def test_same_size_replacement_after_hash_is_rejected(self) -> None:
        hash_resource = transitional_installs._hash_resource
        skill = self.package / "SKILL.md"

        def replace_after_hash(digest: object, directory: int, relative: str, expected: tuple) -> None:
            hash_resource(digest, directory, relative, expected)
            if relative == "SKILL.md":
                replacement = self.root / "replacement"
                replacement.write_bytes(b"X" * skill.stat().st_size)
                replacement.replace(skill)

        with patch.object(transitional_installs, "_hash_resource", side_effect=replace_after_hash):
            self.assertEqual(self.verify()["status"], "fail")

    def test_runtime_local_manifest_cannot_grant_identity(self) -> None:
        (self.package / "approval.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        self.record.unlink()
        self.assertEqual(self.verify()["status"], "fail")

    def test_malformed_record_missing_provenance_and_wrong_approval_fail(self) -> None:
        for field, value in (("source_ref", ""), ("sha256", "bad"), ("file_count", 99),
                             ("approval", "runtime-local")):
            with self.subTest(field=field):
                expected = self.manifest["packages"]["testing"]
                original = expected[field]
                expected[field] = value
                self.write_record()
                self.assertEqual(self.verify()["status"], "fail")
                expected[field] = original
        self.record.write_text("[]", encoding="utf-8")
        self.assertEqual(self.verify()["status"], "fail")

    def test_all_runtime_targets_preserve_identity_without_granting_readiness(self) -> None:
        def absent_source(handle: str, **_kwargs: object) -> dict:
            return {"status": "not_found", "handle": handle, "runtime_visibility": "flat"}

        for target in ("any", "agents", "codex"):
            with self.subTest(target=target):
                proof = runtime_adapters.build_sdk_skill_proof(
                    repo_root=self.repo, home_path=self.home, handle="testing",
                    runtime_target=target, resolve_skill_handle_fn=absent_source,
                )
                self.assertEqual(proof["status"], "fail")
                self.assertEqual(proof["installation_proof"]["status"], "pass")
                self.assertFalse(proof["gates"]["user_runtime_ready"])
                self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
                self.assertFalse(proof["gates"]["agents_user_runtime_ready"])
                self.assertEqual(proof["available_runtimes"], [])
                self.assertIsNone(proof["runtime_satisfied_by"])
                self.assertFalse(proof["sdk_clearance"])
                self.assertFalse(proof["gates"]["canonical_source_exists"])
                self.assertNotIn("live_runtime_invocation", proof)
                self.assertEqual(proof["runtime_diagnostics"]["recovery_commands"], [])
                self.assertEqual(proof["runtime_diagnostics"]["runtime_aliases"]["status"],
                                 "single_selected_physical_collection")
                context = {"runtime_status": "implemented_enforced", "claim_status": "pass"}
                runtime_adapters._apply_transitional_evidence_boundary(context, proof)
                self.assertEqual(context["claim_status"], "partial")
                self.assertEqual(context["failed_check_id"], "transitional_identity_only")

    def test_emitted_evidence_cannot_promote_copy_identity_to_invocation(self) -> None:
        proof = runtime_adapters.build_sdk_skill_proof(
            repo_root=self.repo, home_path=self.home, handle="testing", runtime_target="codex",
            resolve_skill_handle_fn=lambda handle, **kwargs: {"status": "not_found", "handle": handle},
        )
        observation = {"thread_runs": [], "turn_events": [], "session": None,
                       "observability": {"overall_status": "healthy", "skill_invocation_event_count": 1}}
        with patch.object(runtime_adapters, "_runtime_observation", return_value=observation):
            result = runtime_adapters.emit_sdk_skill_runtime_evidence(repo_root=self.repo, proof=proof)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["failed_check_id"], "transitional_identity_only")
        probe = json.loads((self.repo / result["probe_artifact_path"]).read_text(encoding="utf-8"))
        self.assertEqual(probe["proof"]["status"], "partial")
        self.assertEqual(probe["proof"]["structural_status"], "fail")
        self.assertFalse(probe["proof"]["sdk_clearance"])

    def test_verification_preserves_contents_and_has_no_runtime_writes(self) -> None:
        before = {path.relative_to(self.home): path.read_bytes()
                  for path in self.home.rglob("*") if path.is_file()}
        self.assertEqual(self.verify()["status"], "pass")
        after = {path.relative_to(self.home): path.read_bytes()
                 for path in self.home.rglob("*") if path.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
