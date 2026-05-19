import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import skills_package  # noqa: E402


class TestAskSkillsPackage(unittest.TestCase):
    def test_package_reports_versioned_role_ready_contract(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-builder")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["schema_version"], "skill-package-readiness.v1")
        self.assertEqual(package["gate_summary"]["promotion_status"], "blocked_validation")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        contract = package["package_contract"]
        self.assertEqual(contract["values"]["version"], "1.0.0")
        self.assertEqual(contract["values"]["maturity"], "canonical")
        self.assertIn("compatible_roles", contract["required_fields"]["missing"])
        self.assertFalse(contract["install_gate"]["install_ready"])
        self.assertIn("compatible_roles", contract["install_gate"]["blocked_reasons"])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "blocked_validation")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(contract["promotion_gate"]["share_ready"])
        self.assertIn("compatible_roles", contract["promotion_gate"]["blocked_reasons"])
        self.assertIn("compatible_roles", contract["promotion_gate"]["recommended_next_fields"])
        self.assertEqual(package["lifecycle_event"]["event_type"], "skill_loaded")
        self.assertEqual(
            [event["event_type"] for event in package["lifecycle_events"]],
            ["skill_loaded", "package_readiness_checked"],
        )
        self.assertNotIn("details", package["lifecycle_events"][0])
        self.assertEqual(
            package["lifecycle_events"][1]["details"]["gate_summary"],
            package["gate_summary"],
        )
        self.assertIn("package_readiness_checked", package["lifecycle_event_types"])

    def test_package_strict_fails_on_metadata_gaps(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-builder", strict=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["blockers"][0]["class"], "blocked_validation")
        self.assertIn("package_readiness_checked", package["lifecycle_event_types"])
        self.assertIn("missing package metadata", package["blockers"][0]["message"])
        self.assertTrue(result.errors)
        self.assertIn("Strict package readiness failed", result.errors[0].message)

    def test_package_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill")

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["blockers"][0]["class"], "blocked_missing_source")
        self.assertFalse(package["package_contract"]["install_gate"]["install_ready"])
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "not_run",
        )
        self.assertEqual(
            package["package_contract"]["promotion_gate"]["status"],
            "blocked_missing_source",
        )

    def test_package_checkout_test_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill", checkout_test=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "blocked_missing_source",
        )

    def test_package_reads_nested_block_list_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Test package readiness metadata parsing.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
    - reviewer
  runtime_needs:
    - network
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        self.assertEqual(package["gate_summary"]["checkout_test_status"], "not_run")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["network", "filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])
        self.assertEqual(contract["install_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertEqual(contract["promotion_gate"]["checkout_test_status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["blocked_reasons"], [])
        self.assertTrue(contract["promotion_gate"]["share_ready"])

    def test_package_reads_top_level_package_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Test package readiness metadata parsing.
version: "2.0.0"
compatible_roles: [worker, reviewer]
runtime_needs: [filesystem]
maturity: beta
provenance: internal
share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        contract = result.data["skill_package"]["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])

    def test_package_blocks_declared_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Test package readiness metadata parsing.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: draft
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "warning")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertFalse(contract["install_gate"]["install_ready"])
        self.assertIn("share_readiness_not_ready", contract["install_gate"]["blocked_reasons"])
        self.assertEqual(contract["promotion_gate"]["status"], "blocked_validation")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(contract["promotion_gate"]["share_ready"])
        self.assertEqual(contract["promotion_gate"]["recommended_next_fields"], ["share_readiness"])

    def test_package_checkout_test_records_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Test package readiness metadata parsing.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertIn("source_path:Skills/agent-ops/packaged-skill/SKILL.md", checkout["evidence"])
        self.assertIn("package_metadata_complete:true", checkout["evidence"])
        self.assertEqual(
            result.data["skill_package"]["gate_summary"],
            {
                "install_ready": True,
                "checkout_test_status": "pass",
                "promotion_status": "ready",
                "promotion_ready": True,
                "blocked_reasons": [],
            },
        )
        self.assertEqual(
            result.data["skill_package"]["lifecycle_events"][1]["details"]["gate_summary"],
            result.data["skill_package"]["gate_summary"],
        )
        promotion = result.data["skill_package"]["package_contract"]["promotion_gate"]
        self.assertEqual(promotion["status"], "ready")
        self.assertTrue(promotion["promotion_ready"])
        self.assertEqual(promotion["checkout_test_status"], "pass")

    def test_package_checkout_test_blocks_metadata_gaps(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-builder",
            "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-builder", checkout_test=True)

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "warning")
        checkout = package["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "blocked_validation")
        self.assertTrue(any(item.startswith("missing_package_metadata:") for item in checkout["evidence"]))

    def test_package_checkout_test_blocks_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Test package readiness metadata parsing.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: draft
---

# Packaged Skill
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "blocked_validation")
        self.assertIn("promotion_gate_blocked:share_readiness_not_ready", checkout["evidence"])


if __name__ == "__main__":
    unittest.main()
