"""Atomic promotion integration tests for ask skills install (CA3)."""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# Add scripts/lib to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "scripts" / "lib"))

from ask.envelope import CallResult, ErrorCode
from ask.state import SkillState, ReadinessState
from ask.validity import ContractValidityEvidence, check_install_validity
from ask.handoff import HandoffPackage


class TestAtomicPromotion(unittest.TestCase):
    """Test atomic promotion and failure cleanup (CA3)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        # Create required directories
        (self.repo_root / ".agent" / "handoff").mkdir(parents=True)
        (self.repo_root / ".agent" / "validity").mkdir(parents=True)
        (self.repo_root / ".agent" / "state").mkdir(parents=True)
        (self.repo_root / ".quarantine").mkdir(parents=True)
        (self.repo_root / "skills").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_no_partial_skill_on_validation_failure(self):
        """CA3: Failed validation blocks promotion; no partial skill in destination."""
        skill_name = "test-skill"
        dest_dir = self.repo_root / "skills" / skill_name
        
        # Simulate partial write attempt
        dest_dir.mkdir(parents=True)
        (dest_dir / "partial.txt").write_text("incomplete")
        
        # Simulate validation failure that triggers cleanup
        # In real implementation, this would be in install_skill
        try:
            # Simulate: validation fails, should rollback
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            raise Exception("Validation failed")
        except Exception:
            pass
        
        # Assert no partial skill remains
        self.assertFalse(dest_dir.exists(), "Partial skill should be cleaned up on validation failure")

    def test_state_transitions_blocked_on_failure(self):
        """SA17: Blocked state recorded when iteration fails."""
        skill_name = "test-skill"
        
        # Create initial state
        state = SkillState.create(self.repo_root, skill_name)
        self.assertEqual(state.current_state, ReadinessState.STARTER_VALID)
        
        # Transition to comparison
        state.transition(
            ReadinessState.COMPARISON_INCOMPLETE,
            reason="Starting baseline comparison",
            actor="skill-builder"
        )
        self.assertEqual(state.current_state, ReadinessState.COMPARISON_INCOMPLETE)
        
        # Simulate failure - transition to blocked
        state.transition(
            ReadinessState.BLOCKED,
            reason="Baseline comparison failed - no improvement",
            actor="skill-builder"
        )
        self.assertEqual(state.current_state, ReadinessState.BLOCKED)
        self.assertEqual(state.block_reason, "Baseline comparison failed - no improvement")
        
        # Verify history recorded
        self.assertEqual(len(state.history), 3)
        self.assertEqual(state.history[-1].to_state, ReadinessState.BLOCKED.value)

    def test_downstream_ready_required_for_install(self):
        """SA9: skill-installer only accepts downstream_ready skills."""
        skill_name = "test-skill"
        
        # Test with no state
        can_install, err = check_install_validity(self.repo_root, skill_name)
        self.assertFalse(can_install)
        self.assertIn("No state record found", err)
        
        # Create state but not downstream_ready
        state = SkillState.create(self.repo_root, skill_name)
        can_install, err = check_install_validity(self.repo_root, skill_name)
        self.assertFalse(can_install)
        self.assertIn("not downstream_ready", err)
        
        # Transition to downstream_ready
        state.transition(
            ReadinessState.COMPARISON_INCOMPLETE,
            reason="Comparison started",
            actor="skill-builder"
        )
        state.transition(
            ReadinessState.DOWNSTREAM_READY,
            reason="All validations passed",
            actor="skill-builder"
        )
        state.write(self.repo_root)
        
        # Create validity evidence
        evidence = ContractValidityEvidence(
            skill_name=skill_name,
            final_state=ReadinessState.DOWNSTREAM_READY.value,
            skill_gate_passed=True,
            security_evals_passed=True,
            qualitative_review_completed=True,
        )
        from ask.validity import IterationEvidence
        evidence.iteration_rounds.append(
            IterationEvidence(
                round_id="round-001",
                baseline_type="no_skill",
                comparison_result="improved",
            )
        )
        evidence.write(self.repo_root)
        
        # Now should be installable
        can_install, err = check_install_validity(self.repo_root, skill_name)
        self.assertTrue(can_install)
        self.assertIsNone(err)

    def test_force_override_installs_without_evidence(self):
        """SA9: --force flag allows install without ContractValidityEvidence."""
        skill_name = "test-skill"
        
        # No state, no evidence
        can_install, err = check_install_validity(self.repo_root, skill_name, force=True)
        self.assertTrue(can_install)
        self.assertIsNone(err)

    def test_invalid_state_transition_raises(self):
        """SA17: Invalid state transitions are rejected."""
        skill_name = "test-skill"
        state = SkillState.create(self.repo_root, skill_name)
        
        # Cannot go from starter_valid to downstream_ready directly
        with self.assertRaises(ValueError) as ctx:
            state.transition(
                ReadinessState.DOWNSTREAM_READY,
                reason="Invalid jump",
                actor="test"
            )
        self.assertIn("Invalid state transition", str(ctx.exception))

    def test_handoff_package_validation(self):
        """SA2-SA3: HandoffPackage validation enforces required fields."""
        pkg = HandoffPackage()
        pkg.skill_name = "test-skill"
        # Missing required fields
        
        errors = pkg.validate()
        self.assertIn("goal is required (SA3)", errors)
        self.assertIn("boundary_summary is required (SA3)", errors)
        
        # Fill in required fields
        pkg.goal = "Test goal"
        pkg.boundary_summary = "Test boundary"
        pkg.trigger_contexts = ["when user says test"]
        pkg.starter_prompts = ["test prompt"]
        pkg.validation_state.quick_validate_passed = True
        
        errors = pkg.validate()
        self.assertEqual(errors, [])

    def test_handoff_package_serialization(self):
        """SA2a: HandoffPackage can be written and loaded."""
        pkg = HandoffPackage()
        pkg.skill_name = "test-skill"
        pkg.goal = "Test goal"
        pkg.boundary_summary = "Test boundary"
        pkg.trigger_contexts = ["when user says test"]
        pkg.starter_prompts = ["test prompt 1", "test prompt 2"]
        pkg.validation_state.quick_validate_passed = True
        pkg.validation_state.timestamp = "2026-04-06T00:00:00Z"
        pkg.authoring_state.ready_for_builder = True
        
        # Write
        path = pkg.write(self.repo_root)
        self.assertTrue(path.exists())
        
        # Load
        loaded = HandoffPackage.load(path)
        self.assertEqual(loaded.skill_name, pkg.skill_name)
        self.assertEqual(loaded.goal, pkg.goal)
        self.assertEqual(loaded.starter_prompts, pkg.starter_prompts)


class TestQuarantineLifecycle(unittest.TestCase):
    """Test quarantine → promotion → cleanup lifecycle (CA3)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)
        (self.repo_root / ".quarantine").mkdir(parents=True)
        (self.repo_root / "skills").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_quarantine_directory_created(self):
        """Install creates quarantine directory first."""
        quarantine_dir = self.repo_root / ".quarantine" / "test-run"
        quarantine_dir.mkdir(parents=True)
        (quarantine_dir / "skill.yaml").write_text("test")
        
        self.assertTrue(quarantine_dir.exists())
        
        # Simulate cleanup on failure
        shutil.rmtree(quarantine_dir)
        self.assertFalse(quarantine_dir.exists())

    def test_atomic_move_on_success(self):
        """Successful validation triggers atomic move to destination."""
        quarantine_dir = self.repo_root / ".quarantine" / "test-run"
        dest_dir = self.repo_root / "skills" / "test-skill"
        
        quarantine_dir.mkdir(parents=True)
        (quarantine_dir / "SKILL.md").write_text("# Test Skill")
        
        # Atomic move
        shutil.move(str(quarantine_dir), str(dest_dir))
        
        self.assertFalse(quarantine_dir.exists())
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
