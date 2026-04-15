"""ContractValidityEvidence for install/plugin handoff gates (SA9-SA10)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .envelope import ErrorCode
from .state import ReadinessState, SkillState


@dataclass
class IterationEvidence:
    """Evidence from one iteration round."""
    round_id: str
    baseline_type: str  # no_skill, prior_snapshot, neutral_repo
    comparison_result: str  # improved, regressed, neutral, inconclusive
    timing_ms: Optional[int] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    qualitative_notes: str = ""
    quantitative_score: Optional[float] = None

    VALID_BASELINE_TYPES = {"no_skill", "prior_snapshot", "neutral_repo"}
    VALID_RESULTS = {"improved", "regressed", "neutral", "inconclusive"}

    def __post_init__(self):
        """Validate baseline_type and comparison_result values."""
        if self.baseline_type not in self.VALID_BASELINE_TYPES:
            raise ValueError(
                f"Invalid baseline_type: {self.baseline_type}. "
                f"Must be one of: {self.VALID_BASELINE_TYPES}"
            )
        if self.comparison_result not in self.VALID_RESULTS:
            raise ValueError(
                f"Invalid comparison_result: {self.comparison_result}. "
                f"Must be one of: {self.VALID_RESULTS}"
            )


@dataclass
class ContractValidityEvidence:
    """
    Evidence bundle required for downstream handoff (SA9-SA10).
    Proves skill has passed lifecycle hardening.
    """
    skill_name: str
    schema_version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Source of validity
    handoff_package_path: str = ""
    iteration_rounds: List[IterationEvidence] = field(default_factory=list)
    
    # Final assessment
    final_state: str = ""  # downstream_ready
    skill_gate_passed: bool = False
    security_evals_passed: bool = False
    contract_checks_passed: bool = False
    
    # Qualitative review
    qualitative_review_completed: bool = False
    description_assessment: str = ""  # adequate, needs_work, improved
    routing_assessment: str = ""  # clear, ambiguous, improved
    
    # Quantitative metrics
    eval_coverage_percent: float = 0.0
    smoke_tests_passed: int = 0
    smoke_tests_total: int = 0
    release_tests_passed: int = 0
    release_tests_total: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "skill_name": self.skill_name,
            "created_at": self.created_at,
            "handoff_package_path": self.handoff_package_path,
            "iteration_rounds": [
                {
                    "round_id": r.round_id,
                    "baseline_type": r.baseline_type,
                    "comparison_result": r.comparison_result,
                    "timing_ms": r.timing_ms,
                    "tokens_in": r.tokens_in,
                    "tokens_out": r.tokens_out,
                    "qualitative_notes": r.qualitative_notes,
                    "quantitative_score": r.quantitative_score,
                }
                for r in self.iteration_rounds
            ],
            "final_state": self.final_state,
            "skill_gate_passed": self.skill_gate_passed,
            "security_evals_passed": self.security_evals_passed,
            "contract_checks_passed": self.contract_checks_passed,
            "qualitative_review_completed": self.qualitative_review_completed,
            "description_assessment": self.description_assessment,
            "routing_assessment": self.routing_assessment,
            "eval_coverage_percent": self.eval_coverage_percent,
            "smoke_tests_passed": self.smoke_tests_passed,
            "smoke_tests_total": self.smoke_tests_total,
            "release_tests_passed": self.release_tests_passed,
            "release_tests_total": self.release_tests_total,
        }

    def write(self, repo_root: Path) -> Path:
        """Write validity evidence to .agent/validity/ directory."""
        validity_dir = repo_root / ".agent" / "validity"
        validity_dir.mkdir(parents=True, exist_ok=True)
        path = validity_dir / f"{self.skill_name}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        path.chmod(0o600)  # Owner read/write only
        return path

    @classmethod
    def load(cls, repo_root: Path, skill_name: str) -> Optional[ContractValidityEvidence]:
        """Load validity evidence from file."""
        path = repo_root / ".agent" / "validity" / f"{skill_name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        evidence = cls(
            skill_name=data.get("skill_name", skill_name),
            schema_version=data.get("schema_version", "1.0"),
            created_at=data.get("created_at", ""),
            handoff_package_path=data.get("handoff_package_path", ""),
            final_state=data.get("final_state", ""),
            skill_gate_passed=data.get("skill_gate_passed", False),
            security_evals_passed=data.get("security_evals_passed", False),
            contract_checks_passed=data.get("contract_checks_passed", False),
            qualitative_review_completed=data.get("qualitative_review_completed", False),
            description_assessment=data.get("description_assessment", ""),
            routing_assessment=data.get("routing_assessment", ""),
            eval_coverage_percent=data.get("eval_coverage_percent", 0.0),
            smoke_tests_passed=data.get("smoke_tests_passed", 0),
            smoke_tests_total=data.get("smoke_tests_total", 0),
            release_tests_passed=data.get("release_tests_passed", 0),
            release_tests_total=data.get("release_tests_total", 0),
        )
        evidence.iteration_rounds = [
            IterationEvidence(
                round_id=r["round_id"],
                baseline_type=r["baseline_type"],
                comparison_result=r["comparison_result"],
                timing_ms=r.get("timing_ms"),
                tokens_in=r.get("tokens_in"),
                tokens_out=r.get("tokens_out"),
                qualitative_notes=r.get("qualitative_notes", ""),
                quantitative_score=r.get("quantitative_score"),
            )
            for r in data.get("iteration_rounds", [])
        ]
        return evidence

    def is_valid_for_install(self) -> tuple[bool, Optional[str]]:
        """Check if evidence is sufficient for install handoff (SA9)."""
        if self.final_state != ReadinessState.DOWNSTREAM_READY.value:
            return False, f"final_state is '{self.final_state}', expected 'downstream_ready' (SA9)"
        if not self.skill_gate_passed:
            return False, "skill_gate_passed is false (SA9)"
        if not self.security_evals_passed:
            return False, "security_evals_passed is false (SA9)"
        if not self.qualitative_review_completed:
            return False, "qualitative_review_completed is false (SA6/SA9)"
        if len(self.iteration_rounds) == 0:
            return False, "no iteration rounds recorded (SA4)"
        return True, None


def check_install_validity(repo_root: Path, skill_name: str, force: bool = False) -> tuple[bool, Optional[str]]:
    """
    Check if skill can be installed per SA9/SA10.
    Returns (can_install, error_message).
    """
    if force:
        return True, None

    # Check state exists and is downstream_ready
    state = SkillState.load(repo_root, skill_name)
    if not state:
        return False, f"No state record found for '{skill_name}'"

    if state.current_state != ReadinessState.DOWNSTREAM_READY:
        return False, (
            f"Skill '{skill_name}' is not downstream_ready (current: {state.current_state.value}). "
            f"Required: downstream_ready (SA9/SA10). "
            f"Block reason: {state.block_reason or 'N/A'}"
        )

    # Check ContractValidityEvidence exists
    evidence = ContractValidityEvidence.load(repo_root, skill_name)
    if not evidence:
        return False, (
            f"No ContractValidityEvidence found for '{skill_name}' (SA9/SA10). "
            f"Skill must pass skill-builder hardening before install. "
            f"Use --force to override (not recommended)."
        )

    # Validate evidence content
    valid, err = evidence.is_valid_for_install()
    if not valid:
        return False, f"ContractValidityEvidence invalid for '{skill_name}': {err}"

    return True, None
