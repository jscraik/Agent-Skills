"""Readiness state machine for skill lifecycle (SA17)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .envelope import ErrorCode


class ReadinessState(str, Enum):
    """Skill readiness states per SA17."""
    STARTER_VALID = "starter_valid"
    COMPARISON_INCOMPLETE = "comparison_incomplete"
    BLOCKED = "blocked"
    DOWNSTREAM_READY = "downstream_ready"


class StateTransition:
    """Valid state transitions."""
    VALID = {
        ReadinessState.STARTER_VALID: [ReadinessState.COMPARISON_INCOMPLETE, ReadinessState.BLOCKED],
        ReadinessState.COMPARISON_INCOMPLETE: [ReadinessState.BLOCKED, ReadinessState.DOWNSTREAM_READY],
        ReadinessState.BLOCKED: [ReadinessState.COMPARISON_INCOMPLETE],  # Retry from blocked
        ReadinessState.DOWNSTREAM_READY: [],  # Terminal state
    }

    @classmethod
    def is_valid(cls, from_state: ReadinessState, to_state: ReadinessState) -> bool:
        return to_state in cls.VALID.get(from_state, [])


@dataclass
class StateRecord:
    """A state transition record."""
    timestamp: str
    from_state: Optional[str]
    to_state: str
    reason: str
    actor: str  # skill-creator, skill-builder, manual


@dataclass
class SkillState:
    """Complete state for a skill including history."""
    skill_name: str
    current_state: ReadinessState = ReadinessState.STARTER_VALID
    block_reason: Optional[str] = None
    history: List[StateRecord] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "current_state": self.current_state.value,
            "block_reason": self.block_reason,
            "updated_at": self.updated_at,
            "history": [
                {
                    "timestamp": h.timestamp,
                    "from_state": h.from_state,
                    "to_state": h.to_state,
                    "reason": h.reason,
                    "actor": h.actor,
                }
                for h in self.history
            ],
        }

    def transition(self, new_state: ReadinessState, reason: str, actor: str) -> None:
        """Attempt state transition. Raises ValueError if invalid."""
        if not StateTransition.is_valid(self.current_state, new_state):
            raise ValueError(
                f"Invalid state transition: {self.current_state.value} -> {new_state.value}. "
                f"Valid transitions from {self.current_state.value}: "
                f"{[s.value for s in StateTransition.VALID.get(self.current_state, [])]}"
            )
        
        record = StateRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            from_state=self.current_state.value,
            to_state=new_state.value,
            reason=reason,
            actor=actor,
        )
        self.history.append(record)
        self.current_state = new_state
        self.updated_at = record.timestamp
        
        if new_state == ReadinessState.BLOCKED:
            self.block_reason = reason
        elif new_state == ReadinessState.DOWNSTREAM_READY:
            self.block_reason = None

    def write(self, repo_root: Path) -> Path:
        """Write state to .agent/state/ directory."""
        state_dir = repo_root / ".agent" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        path = state_dir / f"{self.skill_name}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        path.chmod(0o600)  # Owner read/write only
        return path

    @classmethod
    def load(cls, repo_root: Path, skill_name: str) -> Optional[SkillState]:
        """Load state from file or return None."""
        path = repo_root / ".agent" / "state" / f"{skill_name}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        state = cls(
            skill_name=data["skill_name"],
            current_state=ReadinessState(data["current_state"]),
            block_reason=data.get("block_reason"),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )
        state.history = [
            StateRecord(
                h["timestamp"],
                h.get("from_state"),
                h["to_state"],
                h["reason"],
                h["actor"],
            )
            for h in data.get("history", [])
        ]
        return state

    @classmethod
    def create(cls, repo_root: Path, skill_name: str, actor: str = "skill-creator") -> SkillState:
        """Create initial state for a new skill."""
        state = cls(skill_name=skill_name)
        state.history.append(StateRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            from_state=None,
            to_state=ReadinessState.STARTER_VALID.value,
            reason="Initial creation via quick_validate",
            actor=actor,
        ))
        state.write(repo_root)
        return state


def require_downstream_ready(repo_root: Path, skill_name: str) -> tuple[bool, Optional[str]]:
    """Check if skill is downstream_ready. Returns (is_ready, error_message)."""
    state = SkillState.load(repo_root, skill_name)
    if not state:
        return False, f"No state record found for '{skill_name}'"
    if state.current_state != ReadinessState.DOWNSTREAM_READY:
        return False, (
            f"Skill '{skill_name}' is not downstream_ready (current: {state.current_state.value}). "
            f"Required: downstream_ready (SA9/SA10). "
            f"Block reason: {state.block_reason or 'N/A'}"
        )
    return True, None
