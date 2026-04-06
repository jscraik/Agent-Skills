"""HandoffPackage implementation for skill-authoring family contract (SA2-SA3)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .envelope import ErrorCode, CallResult, ErrorObject


@dataclass
class ResourceItem:
    type: str  # skill_md, reference, script, schema, other
    path: str
    description: str


@dataclass
class ValidationFinding:
    level: str  # info, warn, fail
    code: str
    message: str


@dataclass
class ValidationState:
    quick_validate_passed: bool
    timestamp: str
    validator_version: str = ""
    findings: List[ValidationFinding] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quick_validate_passed": self.quick_validate_passed,
            "timestamp": self.timestamp,
            "validator_version": self.validator_version,
            "findings": [{"level": f.level, "code": f.code, "message": f.message} for f in self.findings],
        }


@dataclass
class AuthoringState:
    is_trivial: bool = False
    ready_for_builder: bool = False
    interview_rounds: int = 0
    assumptions_made: List[str] = field(default_factory=list)


@dataclass
class HandoffPackage:
    """Creator-to-builder handoff artifact per SA2-SA3 spec."""
    schema_version: str = "1.0"
    skill_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    goal: str = ""
    boundary_summary: str = ""
    trigger_contexts: List[str] = field(default_factory=list)
    resource_inventory: List[ResourceItem] = field(default_factory=list)
    starter_prompts: List[str] = field(default_factory=list)
    known_risks: List[str] = field(default_factory=list)
    validation_state: ValidationState = field(default_factory=lambda: ValidationState(False, ""))
    authoring_state: AuthoringState = field(default_factory=AuthoringState)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "skill_name": self.skill_name,
            "created_at": self.created_at,
            "goal": self.goal,
            "boundary_summary": self.boundary_summary,
            "trigger_contexts": self.trigger_contexts,
            "resource_inventory": [
                {"type": r.type, "path": r.path, "description": r.description}
                for r in self.resource_inventory
            ],
            "starter_prompts": self.starter_prompts,
            "known_risks": self.known_risks,
            "validation_state": self.validation_state.to_dict(),
            "authoring_state": {
                "is_trivial": self.authoring_state.is_trivial,
                "ready_for_builder": self.authoring_state.ready_for_builder,
                "interview_rounds": self.authoring_state.interview_rounds,
                "assumptions_made": self.authoring_state.assumptions_made,
            },
        }

    def to_yaml(self) -> str:
        """Serialize to YAML format."""
        import yaml
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    def to_json(self) -> str:
        """Serialize to JSON format."""
        return json.dumps(self.to_dict(), indent=2)

    def write(self, repo_root: Path) -> Path:
        """Write handoff package to .agent/handoff/ directory."""
        handoff_dir = repo_root / ".agent" / "handoff"
        handoff_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        path = handoff_dir / f"{self.skill_name}-{timestamp}.yaml"
        path.write_text(self.to_yaml())
        path.chmod(0o600)  # Owner read/write only
        return path

    @classmethod
    def load(cls, path: Path) -> HandoffPackage:
        """Load handoff package from file."""
        import yaml
        data = yaml.safe_load(path.read_text())
        pkg = cls()
        pkg.schema_version = data.get("schema_version", "1.0")
        pkg.skill_name = data.get("skill_name", "")
        pkg.created_at = data.get("created_at", "")
        pkg.goal = data.get("goal", "")
        pkg.boundary_summary = data.get("boundary_summary", "")
        pkg.trigger_contexts = data.get("trigger_contexts", [])
        pkg.resource_inventory = [
            ResourceItem(r["type"], r["path"], r["description"])
            for r in data.get("resource_inventory", [])
        ]
        pkg.starter_prompts = data.get("starter_prompts", [])
        pkg.known_risks = data.get("known_risks", [])
        vs = data.get("validation_state", {})
        pkg.validation_state = ValidationState(
            vs.get("quick_validate_passed", False),
            vs.get("timestamp", ""),
            vs.get("validator_version", ""),
            [
                ValidationFinding(f["level"], f["code"], f["message"])
                for f in vs.get("findings", [])
            ],
        )
        ast = data.get("authoring_state", {})
        pkg.authoring_state = AuthoringState(
            ast.get("is_trivial", False),
            ast.get("ready_for_builder", False),
            ast.get("interview_rounds", 0),
            ast.get("assumptions_made", []),
        )
        return pkg

    def validate(self) -> List[str]:
        """Validate package completeness per SA3. Returns list of missing fields."""
        errors = []
        if not self.goal:
            errors.append("goal is required (SA3)")
        if not self.boundary_summary:
            errors.append("boundary_summary is required (SA3)")
        if len(self.trigger_contexts) < 1:
            errors.append("at least 1 trigger_context is required (SA3)")
        if len(self.starter_prompts) < 1:
            errors.append("at least 1 starter_prompt is required (SA3)")
        if not self.validation_state.quick_validate_passed:
            errors.append("validation_state.quick_validate_passed must be true (SA3)")
        return errors


def find_latest_handoff(repo_root: Path, skill_name: str) -> Optional[Path]:
    """Find the most recent handoff package for a skill."""
    handoff_dir = repo_root / ".agent" / "handoff"
    if not handoff_dir.exists():
        return None
    matching = sorted(
        [p for p in handoff_dir.glob(f"{skill_name}-*.yaml")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matching[0] if matching else None


def require_handoff(repo_root: Path, skill_name: str) -> CallResult:
    """Check if handoff package exists and is valid. Returns CallResult."""
    handoff_path = find_latest_handoff(repo_root, skill_name)
    if not handoff_path:
        return CallResult(
            status="error",
            errors=[ErrorObject(
                code=ErrorCode.ERR_INVALID_HANDOFF,
                message=f"No HandoffPackage found for '{skill_name}' (SA2)",
                fix_suggestion=f"Run skill-creator for '{skill_name}' to generate handoff package",
            )],
        )
    try:
        pkg = HandoffPackage.load(handoff_path)
        validation_errors = pkg.validate()
        if validation_errors:
            return CallResult(
                status="error",
                errors=[ErrorObject(
                    code=ErrorCode.ERR_INVALID_HANDOFF,
                    message=f"HandoffPackage for '{skill_name}' is incomplete: {', '.join(validation_errors)}",
                    fix_suggestion="Complete the handoff package before proceeding to hardening",
                )],
            )
        return CallResult(
            status="success",
            data={"handoff_package": pkg.to_dict(), "path": str(handoff_path)},
        )
    except Exception as e:
        return CallResult(
            status="error",
            errors=[ErrorObject(
                code=ErrorCode.ERR_SCHEMA_INVALID,
                message=f"Failed to parse HandoffPackage for '{skill_name}': {e}",
            )],
        )
