from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from types import MappingProxyType
from typing import Any

from ask.skills_sdk.contracts import (
    CODEX_SKILL_PACKAGE_FIELDS,
    CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS,
    PACKAGE_CONTRACT_FIELDS,
    parse_frontmatter_scalar,
)
from ask.skills_sdk.skill_authoring_contract import authoring_contract

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


SKILL_PACKAGE_SCHEMA_VERSION = "skill-package.v1"
SKILL_PACKAGE_READINESS_SCHEMA_VERSION = "skill-package-readiness.v1"
SKILL_PACKAGE_COMPATIBILITY_SNAPSHOT_ID = "skill-package-readiness.v1.public-output.2026-05-23"
SKILL_PACKAGE_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package.v1.schema.json"
SKILL_PACKAGE_READINESS_SCHEMA_PATH = "Infrastructure/config/schemas/skill-package-readiness.v1.schema.json"
SKILLFLOW_SCHEMA_VERSION = "skillflow.v1"
SKILLFLOW_SCHEMA_PATH = "Infrastructure/config/schemas/skillflow.v1.schema.json"
SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION = "skill-optimization-contract.v1"
SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH = (
    "Infrastructure/config/schemas/skill-optimization-contract.v1.schema.json"
)
SKILL_PACKAGE_SNAPSHOT_PATH = (
    "Infrastructure/tests/fixtures/skill_package_snapshots/"
    "skill-package-readiness-public-output.v1.json"
)
CODEX_SKILL_PACKAGE_ABI_SOURCE_PATH = "codex-rs/core-skills/src/model.rs"
CODEX_SKILL_PACKAGE_ABI_EVIDENCE_FIELDS: tuple[str, ...] = CODEX_SKILL_PACKAGE_FRONTMATTER_FIELDS
CODEX_SKILL_PACKAGE_REQUIRED_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if required
)
CODEX_SKILL_PACKAGE_OPTIONAL_FIELDS: tuple[str, ...] = tuple(
    field for field, required in CODEX_SKILL_PACKAGE_FIELDS if not required
)
SDK_PACKAGE_CONTRACT_SCHEMA_VERSION = "skill-sdk-contract.v1"
SDK_PACKAGE_CONTRACT_FIELDS: tuple[str, ...] = (
    "agent_metadata",
    "reference_contract",
    "reference_quality",
    "writing_quality",
    "authoring_contract",
    "openai_platform_compat",
    "purpose",
    "inputs",
    "outputs",
    "commands",
    "permission_profile",
    "portability_profile",
    "evals",
    "task_profile",
    "evidence_policy",
    "optimization_contract",
)
SDK_PACKAGE_ADVISORY_CONTRACT_FIELDS: tuple[str, ...] = (
    "budget_classification",
)
OPERATING_MODEL_FORMAT_DOCS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("MISSION.md", ("MISSION.md",), "references/mission-format.md"),
    ("RESOURCES.md", ("RESOURCES.md",), "references/resources-format.md"),
    ("GLOSSARY.md", ("GLOSSARY.md",), "references/glossary-format.md"),
    (
        "learning-records/",
        ("learning-records/", "learning-records/*.md"),
        "references/learning-record-format.md",
    ),
)
SOURCE_OPERATING_MODEL_KINDS = frozenset({
    "source_operating_model",
    "operating_model_source",
    "operating_model_reference",
    "operating_model_format",
})
PACKAGE_IGNORED_FILE_NAMES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})
CENTRAL_RUBRIC_PROFILES = MappingProxyType({
    "skills-sdk.gold-standard.v1": "Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json",
})
OPENAI_PLATFORM_COMPAT_SCHEMA_VERSION = "skills-sdk.openai-platform-compat.v1"
SKILLFLOW_NODE_TYPES = frozenset({
    "command",
    "llm",
    "router",
    "validator",
    "human_gate",
    "subflow",
})
SKILLFLOW_EXECUTION_MODES = frozenset({
    "prose",
    "deterministic_flow",
    "hybrid",
})
OPTIMIZATION_MODES = frozenset({"bounded_patch", "reviewed_rewrite"})
OPTIMIZATION_EDIT_MODES = frozenset({"patch", "reviewed_rewrite"})
OPTIMIZATION_EDIT_OPERATIONS = frozenset({"add", "delete", "replace"})
OPTIMIZATION_ACCEPTANCE_RULES = frozenset({"strict_improvement", "min_delta"})
OPTIMIZATION_TIE_POLICIES = frozenset({"reject", "allow_with_review"})
OPTIMIZATION_GUARD_FAILURE_POLICIES = frozenset({"discard", "block"})
OPTIMIZATION_METRIC_DIRECTIONS = frozenset({"maximize", "minimize"})
OPTIMIZATION_SPLIT_ROLES = MappingProxyType({
    "train": "proposal_generation",
    "selection": "candidate_acceptance",
    "test": "final_report_only",
})
PACKAGE_FILE_STEM_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_DESCRIPTION_HANDLE_RE = re.compile(r"\$[A-Za-z][A-Za-z0-9_-]*")
GENERIC_PACKAGE_FILE_STEMS = frozenset({"details", "misc", "notes", "scratch", "todo", "tmp"})
GENERIC_REFERENCE_HEADING_TERMS = frozenset({
    "details",
    "misc",
    "notes",
    "overview",
    "reference",
    "scratch",
    "todo",
    "tmp",
})
DESCRIPTION_ACTION_TERMS = frozenset({
    "audit",
    "build",
    "check",
    "create",
    "debug",
    "diagnose",
    "evaluate",
    "fix",
    "generate",
    "harden",
    "install",
    "plan",
    "prepare",
    "review",
    "run",
    "sync",
    "update",
    "use",
    "validate",
})
CONSTRUCTION_OBLIGATION_TERMS = DESCRIPTION_ACTION_TERMS | {
    "accept",
    "ask",
    "block",
    "choose",
    "classify",
    "collect",
    "compare",
    "decide",
    "decline",
    "fail",
    "gather",
    "link",
    "load",
    "map",
    "open",
    "produce",
    "read",
    "refuse",
    "route",
    "select",
    "stop",
}
CONSTRUCTION_TRIGGER_BOUNDARY_TERMS = frozenset({
    "avoid",
    "boundary",
    "delegate",
    "except",
    "handoff",
    "instead",
    "never",
    "not",
    "only",
    "outside",
    "refuse",
    "unless",
    "when",
})
CONSTRUCTION_PHASE_TERMS = frozenset({
    "after",
    "before",
    "block",
    "blocked",
    "gate",
    "gated",
    "phase",
    "step",
    "stop",
    "validate",
})
CONSTRUCTION_GENERIC_TRIGGER_TERMS = frozenset({
    "anything",
    "everything",
    "general",
    "misc",
    "stuff",
    "things",
})
CONSTRUCTION_SEDIMENT_WORD_LIMIT = 55
CONSTRUCTION_DUPLICATE_LINE_WORD_LIMIT = 8
CANONICAL_SKILL_H2_HEADERS: tuple[str, ...] = (
    "When To Use",
    "Inputs",
    "Outputs",
    "Workflow",
    "Failure Mode",
    "Validation",
    "References",
)
OPTIONAL_SKILL_H2_HEADERS: tuple[str, ...] = (
    "Gotchas",
    "Execution Boundaries",
)

__all__ = [name for name in globals() if not name.startswith("__")]
