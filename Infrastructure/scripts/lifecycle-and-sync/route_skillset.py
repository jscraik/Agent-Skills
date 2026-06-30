#!/usr/bin/env python3
"""Route a task to a bounded latent module inside one rooted skill set."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import rel, repo_root

DEFAULT_SKILLSETS_DIR = repo_root() / ".skillsets"
MAX_TOP_K = 3
LOW_CONFIDENCE_THRESHOLD = 0.18
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "but",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "should",
    "so",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
}
# TOKEN_RE captures alphanumeric tokens with optional hyphens.
# Minimum token length is 1 character to include single-letter terms like "i".
# The second character group is optional to allow single-character tokens.
TOKEN_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
TOKEN_ALIASES = {
    "verification": "verify",
}

# Harness Engineering keeps folded stage bodies as preserved context while
# routing active calls through parent stages.
HE_FOLDED_STAGE_ALIASES = {
    "he-compound": "he-reinforce",
    "he-compound-refresh": "he-reinforce",
    "he-deepen-plan": "he-plan",
    "he-deepen-spec": "he-spec",
    "he-ideate": "he-brainstorm",
    "he-phase-heartbeat": "he-phase-work",
    "he-prune-branches": "he-reconcile",
    "he-refactor": "he-reframe",
    "he-refine": "he-improve",
    "he-reliability-review": "he-code-review",
    "he-tdd": "he-work",
    "he-technical-review": "he-code-review",
}


def tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        cleaned = token.strip("-")
        if not cleaned:
            continue
        if cleaned in STOPWORDS:
            continue
        tokens.add(cleaned)
        if cleaned in TOKEN_ALIASES:
            tokens.add(TOKEN_ALIASES[cleaned])
        tokens.update(part for part in cleaned.split("-") if part and part not in STOPWORDS)
        tokens.update(TOKEN_ALIASES[part] for part in cleaned.split("-") if part in TOKEN_ALIASES)
    return tokens


def normalize_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def read_manifest(skill_set: str, skillsets_dir: Path = DEFAULT_SKILLSETS_DIR) -> tuple[list[dict[str, Any]], str | None]:
    if skill_set not in ROOT_SKILL_SET_NAMES:
        return [], "invalid_skill_set"
    manifest_path = skillsets_dir / skill_set / "manifest.jsonl"
    if not manifest_path.is_file():
        return [], "manifest_missing"
    source_roots = [skillsets_dir.parent, repo_root()]
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid manifest JSON at {rel(manifest_path)}:{line_no}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Invalid manifest row at {rel(manifest_path)}:{line_no}: expected JSON object")
        for field in ("id", "description", "level", "source_path"):
            if not isinstance(row.get(field), str) or not row.get(field):
                raise ValueError(
                    f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field {field!r} must be a non-empty string"
                )
        source_path = Path(str(row["source_path"]))
        if source_path.is_absolute() or ".." in source_path.parts:
            raise ValueError(
                f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field 'source_path' must be a repo-relative path"
            )
        if not any(_source_path_exists_within_root(source_root, source_path) for source_root in source_roots):
            raise ValueError(
                f"Invalid manifest row at {rel(manifest_path)}:{line_no}: source_path {row['source_path']!r} does not exist"
            )
        triggers = row.get("triggers", [])
        if not isinstance(triggers, list) or any(not isinstance(item, str) for item in triggers):
            raise ValueError(
                f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field 'triggers' must be a list of strings"
            )
        rows.append(row)
    return rows, None


def _source_path_exists_within_root(source_root: Path, source_path: Path) -> bool:
    candidate = source_root / source_path
    if not candidate.is_file():
        return False
    try:
        candidate.resolve().relative_to(source_root.resolve())
    except (OSError, ValueError):
        return False
    return True


def score_row(row: dict[str, Any], task: str) -> tuple[float, list[str]]:
    task_phrase = normalize_phrase(task)
    phrase_candidates = [
        normalize_phrase(str(row.get("id", "")).replace("-", " ")),
        *[
            normalize_phrase(str(item))
            for item in row.get("triggers", [])
            if isinstance(item, str)
        ],
    ]
    for phrase in phrase_candidates:
        if len(phrase.split()) >= 2 and phrase in task_phrase:
            return 1.0, [f"matched phrase '{phrase}'"]

    task_tokens = tokenize(task)
    haystack_parts = [
        str(row.get("id", "")),
        str(row.get("description", "")),
        " ".join(str(item) for item in row.get("triggers", []) if isinstance(item, str)),
    ]
    row_tokens = tokenize(" ".join(haystack_parts))
    if not task_tokens or not row_tokens:
        return 0.0, []
    overlap = task_tokens & row_tokens
    confidence = len(overlap) / max(len(task_tokens), 1)
    reasons = [f"matched term '{term}'" for term in sorted(overlap)[:3]]
    return round(min(confidence, 1.0), 4), reasons


def signal_matches(task_text: str, task_tokens: set[str], signal: str) -> bool:
    signal_text = signal.lower().strip()
    if not signal_text:
        return False
    if signal_text in task_text:
        return True
    signal_tokens = tokenize(signal_text)
    if not signal_tokens:
        return False
    return signal_tokens <= task_tokens


def row_by_id(rows: list[dict[str, Any]], stage_id: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("id") == stage_id:
            return row
    return None


FACTORY_ORDINARY_WORK_TOKENS = {
    "app",
    "application",
    "code",
    "debug",
    "debugging",
    "feature",
    "implementation",
    "product",
    "test",
    "tests",
    "unit",
}

SKILL_FACTORY_NO_CHANGE_PHRASES = (
    "no skill changes",
    "no skill change",
    "without skill changes",
    "without changing skills",
    "do not change skills",
    "don't change skills",
)

PLUGIN_FACTORY_NO_CHANGE_PHRASES = (
    "no plugin changes",
    "no plugin change",
    "without plugin changes",
    "without changing plugins",
    "do not change plugins",
    "don't change plugins",
)


def factory_scope_excluded(skill_set: str, task: str) -> bool:
    task_text = task.lower()
    task_tokens = tokenize(task)
    if skill_set == "skill-factory":
        no_factory_change = any(phrase in task_text for phrase in SKILL_FACTORY_NO_CHANGE_PHRASES)
        ordinary_work = bool(task_tokens & FACTORY_ORDINARY_WORK_TOKENS)
        return no_factory_change and ordinary_work
    if skill_set == "plugin-factory":
        no_factory_change = any(phrase in task_text for phrase in PLUGIN_FACTORY_NO_CHANGE_PHRASES)
        ordinary_work = bool(task_tokens & FACTORY_ORDINARY_WORK_TOKENS)
        return no_factory_change and ordinary_work
    return False


def resolve_he_stage_alias(stage_id: str) -> str:
    return HE_FOLDED_STAGE_ALIASES.get(stage_id, stage_id)


def he_row_for_stage(rows: list[dict[str, Any]], stage_id: str) -> tuple[dict[str, Any] | None, str]:
    resolved_stage_id = resolve_he_stage_alias(stage_id)
    return row_by_id(rows, resolved_stage_id), resolved_stage_id


def is_he_phase_heartbeat_request(task_text: str, task_tokens: set[str]) -> bool:
    recurring_tokens = {"heartbeat", "monitor", "wake", "wakeup", "recurring", "continue"}
    phase_tokens = {"phase", "phases", "plan", "slice", "slices", "unit", "units"}
    gate_tokens = {"commit", "review", "reviewed", "gate", "gates", "simplify", "validation"}
    return bool(task_tokens & recurring_tokens) and bool(task_tokens & phase_tokens) and bool(
        task_tokens & gate_tokens or "he-work" in task_text
    )


def selected_payload(row: dict[str, Any], confidence: float) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "level": row.get("level"),
        "source_path": row.get("source_path"),
        "confidence": round(confidence, 4),
    }


def is_stage_correctness_question(task_text: str, task_tokens: set[str]) -> bool:
    return (
        re.search(r"\bis\s+he-[a-z0-9-]+\s+(correct|right)\b", task_text) is not None
        or re.search(r"\bwhether\s+(to\s+use\s+)?he-[a-z0-9-]+\s+(is\s+)?(correct|right)\b", task_text) is not None
        or re.search(r"\bwhether\b.*\b(right|correct|best)\s+stage\b", task_text) is not None
        or "right stage" in task_text
        or "correct stage" in task_text
        or "best stage" in task_text
        or "which stage" in task_text
        or "what stage" in task_text
        or "should we use" in task_text
        or "should i use" in task_text
        or "should codex use" in task_text
    )


def harness_engineering_override(
    task: str,
    rows: list[dict[str, Any]],
    *,
    routing_map_path: Path | None = None,
) -> dict[str, Any] | None:
    """
    Apply harness-engineering deterministic routing to the given task and manifest rows.
    
    Evaluates deterministic HE policies (explicit HE stage mentions, stage-correctness questions, and rules from Plugins/harness-engineering/references/routing-map.json) and returns a single routing decision when a deterministic override applies.
    
    Parameters:
        task (str): The user task text to evaluate.
        rows (list[dict[str, Any]]): Parsed manifest rows (each row is a dict from the manifest).
    
    Returns:
        dict[str, Any] | None: A routing decision dict with keys:
            - "row" (dict): The selected manifest row.
            - "confidence" (float): Confidence score for the decision (e.g., 1.0, 0.95, 0.9).
            - "reason" (str): Short explanation of which deterministic rule matched.
        Returns None if no deterministic HE rule applies. Direct HE stage
        mentions still route when the optional routing map is missing.
    """
    routing_map_path = routing_map_path or repo_root() / "Plugins/harness-engineering/references/routing-map.json"
    routing_map: dict[str, Any] = {}
    try:
        if routing_map_path.is_file():
            routing_map = json.loads(routing_map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid Harness Engineering routing map at {routing_map_path}: {exc}") from exc

    task_text = task.lower()
    task_tokens = tokenize(task)
    stage_ids = {str(row.get("id")) for row in rows}

    mentioned_stages = [
        stage
        for stage in re.findall(r"\bhe-[a-z0-9-]+\b", task_text)
        if stage in stage_ids or resolve_he_stage_alias(stage) in stage_ids
    ]
    distinct_mentioned_stages = sorted(set(mentioned_stages))
    resolved_mentioned_stages = sorted({resolve_he_stage_alias(stage) for stage in distinct_mentioned_stages})
    router_row = row_by_id(rows, "he-reconcile")
    if len(resolved_mentioned_stages) > 1 and router_row:
        return {
            "row": router_row,
            "confidence": 0.9,
            "reason": "matched multi-stage HE rule 'named-stage-ambiguity'",
        }
    if distinct_mentioned_stages and is_stage_correctness_question(task_text, task_tokens) and router_row:
        return {
            "row": router_row,
            "confidence": 0.9,
            "reason": "matched multi-stage HE rule 'stage-correctness-question'",
        }
    phase_work_row = row_by_id(rows, "he-phase-work")
    if phase_work_row and is_he_phase_heartbeat_request(task_text, task_tokens):
        return {
            "row": phase_work_row,
            "confidence": 0.97,
            "reason": "matched deterministic HE rule 'phase-work-control-loop'",
        }
    if distinct_mentioned_stages:
        stage_id = distinct_mentioned_stages[0]
        row, resolved_stage_id = he_row_for_stage(rows, stage_id)
        if row:
            reason = "matched deterministic HE rule 'direct-stage-invocation'"
            if resolved_stage_id != stage_id:
                reason += f" via folded stage alias '{stage_id}'"
            return {
                "row": row,
                "confidence": 1.0,
                "reason": reason,
            }

    for rule in sorted(routing_map.get("deterministic_decision_order", []), key=lambda item: item.get("priority", 999)):
        route = str(rule.get("route", ""))
        signals = [str(signal) for signal in rule.get("signals", []) if isinstance(signal, str)]
        if not signals:
            continue
        if not any(signal_matches(task_text, task_tokens, signal) for signal in signals):
            continue
        resolved_route = resolve_he_stage_alias(route)
        if resolved_route in stage_ids:
            row = row_by_id(rows, resolved_route)
            if row:
                reason = f"matched deterministic HE rule '{rule.get('rule')}'"
                if resolved_route != route:
                    reason += f" via folded stage alias '{route}'"
                elif rule.get("folded_from"):
                    reason += f" via folded stage alias '{rule.get('folded_from')}'"
                return {
                    "row": row,
                    "confidence": 0.95,
                    "reason": reason,
                }
        if " or " in route or " -> " in route:
            row = row_by_id(rows, "he-reconcile")
            if row:
                return {
                    "row": row,
                    "confidence": 0.9,
                    "reason": f"matched multi-stage HE rule '{rule.get('rule')}'",
                }
    return None


def factory_override(skill_set: str, task: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Route tasks deterministically for the `plugin-factory` and `skill-factory` skill sets before falling back to generic scoring.
    
    Parameters:
        skill_set (str): Root skill set name, e.g., "plugin-factory" or "skill-factory".
        task (str): The user task text to evaluate for deterministic routing signals.
        rows (list[dict[str, Any]]): Manifest rows for the skill set.
    
    Returns:
        dict[str, Any] | None: A routing decision dict with keys:
            - "row": the selected manifest row (dict),
            - "confidence": confidence score as a float,
            - "reason": short string describing the matched deterministic rule;
        or `None` if no deterministic rule applies.
    """
    if skill_set == "skill-factory":
        rows = [*rows, *_skill_factory_system_bridge_rows(rows)]
    task_text = task.lower()
    row_ids = {str(row.get("id")) for row in rows}

    if skill_set == "plugin-factory":
        internal_plugin_lanes = {"plugin-factory-router", "plugin-router"}
        if task_tokens := tokenize(task):
            if internal_plugin_lanes & task_tokens:
                router_row = row_by_id(rows, "plugin-factory-router")
                if router_row:
                    return {
                        "row": router_row,
                        "confidence": 0.9,
                        "reason": "matched deterministic plugin-factory rule 'internal-lane-mention'",
                    }

    direct_mentions = [row_id for row_id in sorted(row_ids, key=len, reverse=True) if row_id in task_text]
    if len(direct_mentions) == 1:
        row = row_by_id(rows, direct_mentions[0])
        if row:
            return {
                "row": row,
                "confidence": 1.0,
                "reason": f"matched deterministic {skill_set} rule 'direct-lane-invocation'",
            }
    if len(direct_mentions) > 1:
        router_id = "plugin-factory-router" if skill_set == "plugin-factory" else "skill-factory-router"
        row = row_by_id(rows, router_id)
        if row:
            return {
                "row": row,
                "confidence": 0.9,
                "reason": f"matched deterministic {skill_set} rule 'multi-lane-ambiguity'",
            }

    task_tokens = tokenize(task)

    if skill_set == "skill-factory":
        feedback_source_tokens = {"feedback", "coderabbit", "codex"}
        recurrence_tokens = {"again", "across", "recurring", "repeat", "repeated", "same"}
        context_package_tokens = {"skill", "skills", "context", "package", "packages", "eval", "evals"}
        if (
            task_tokens & feedback_source_tokens
            and task_tokens & recurrence_tokens
            and task_tokens & context_package_tokens
        ):
            row = row_by_id(rows, "skill-refactor")
            if row:
                return {
                    "row": row,
                    "confidence": 0.95,
                    "reason": "matched deterministic skill-factory rule 'context-feedback-analysis'",
                }

    rules = {
        "plugin-factory": [
            (
                "plugin-creator",
                "create-plugin",
                {"create", "new", "scaffold", "generate", "make", "starter", "template"},
                {"plugin", "plugins"},
            ),
            (
                "plugin-installer",
                "install-plugin",
                {"install", "add", "sync", "marketplace", "repair", "visibility", "visible", "import", "discover", "discovery"},
                {"plugin", "plugins"},
            ),
            (
                "plugin-factory-router",
                "harden-plugin",
                {"harden", "validate", "audit", "release", "package", "convert", "build"},
                {"plugin", "plugins"},
            ),
        ],
        "skill-factory": [
            (
                "skillify",
                "skillify-workflow",
                {"skillify", "operationalize", "operationalise", "capture", "turn", "convert"},
                {"workflow", "process", "session", "repeatable", "skill", "skills"},
            ),
            (
                "skill-creator",
                "create-skill",
                {"create", "new", "scaffold", "generate", "make", "draft"},
                {"skill", "skills"},
            ),
            (
                "skill-installer",
                "install-skill",
                {"install", "add", "sync", "github", "curated"},
                {"skill", "skills"},
            ),
            (
                "skill-builder",
                "improve-skill-sdk-pipeline",
                {"improve", "harden", "fix", "repair", "review", "score", "eval", "evals", "tessl", "sdk"},
                {"skill", "skills"},
            ),
            (
                "skill-refactor",
                "refactor-skill",
                {"refactor", "simplify", "merge", "fold", "prune", "coverage", "session"},
                {"skill", "skills"},
            ),
            (
                "skill-factory-router",
                "harden-skill",
                {"harden", "validate", "audit", "release", "package", "eval", "benchmark"},
                {"skill", "skills"},
            ),
        ],
    }

    matched = []
    for route_id, rule_name, action_tokens, noun_tokens in rules.get(skill_set, []):
        if route_id not in row_ids:
            continue
        if task_tokens & action_tokens and task_tokens & noun_tokens:
            matched.append((route_id, rule_name))

    if len(matched) == 1:
        route_id, rule_name = matched[0]
        row = row_by_id(rows, route_id)
        if row:
            return {
                "row": row,
                "confidence": 0.95,
                "reason": f"matched deterministic {skill_set} rule '{rule_name}'",
            }
    if len(matched) > 1:
        preferred = _preferred_factory_match(skill_set, matched)
        if preferred is not None:
            route_id, rule_name = preferred
            row = row_by_id(rows, route_id)
            if row:
                return {
                    "row": row,
                    "confidence": 0.95,
                    "reason": f"matched deterministic {skill_set} rule '{rule_name}' with explicit precedence",
                }
        router_id = "plugin-factory-router" if skill_set == "plugin-factory" else "skill-factory-router"
        row = row_by_id(rows, router_id)
        if row:
            return {
                "row": row,
                "confidence": 0.9,
                "reason": f"matched deterministic {skill_set} rule 'multi-intent-factory-task'",
            }
    return None


def _preferred_factory_match(skill_set: str, matched: list[tuple[str, str]]) -> tuple[str, str] | None:
    if skill_set == "skill-factory" and ("skill-builder", "improve-skill-sdk-pipeline") in matched:
        return ("skill-builder", "improve-skill-sdk-pipeline")
    if skill_set == "skill-factory" and ("skill-refactor", "refactor-skill") in matched:
        return ("skill-refactor", "refactor-skill")
    return None


def _skill_factory_system_bridge_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return system skill rows that are intentionally routed by Skill Factory."""
    existing_ids = {str(row.get("id")) for row in rows}
    bridge_specs = {
        "skill-creator": (
            "Create or scaffold Codex skills through the system skill-creator with Skill Factory references.",
            "skills-system/skill-creator/SKILL.md",
            ["skill creator", "create skill", "scaffold skill"],
        ),
        "skill-installer": (
            "Install, list, and validate Codex skills through the system skill-installer with Skill Factory references.",
            "skills-system/skill-installer/SKILL.md",
            ["skill installer", "install skill", "list skills"],
        ),
    }
    bridges: list[dict[str, Any]] = []
    for bridge_id, (description, source_path, triggers) in bridge_specs.items():
        if bridge_id in existing_ids or not (repo_root() / source_path).is_file():
            continue
        bridges.append(
            {
                "id": bridge_id,
                "description": description,
                "level": "system-bridge",
                "source_path": source_path,
                "triggers": triggers,
            }
        )
    return bridges


def route(skill_set: str, task: str, *, top_k: int = MAX_TOP_K, skillsets_dir: Path = DEFAULT_SKILLSETS_DIR) -> dict[str, Any]:
    """
    Route a task to the best-matching stage within a root skill set.
    
    Parameters:
    	skill_set (str): Root skill set name to route within.
    	task (str): The user task text to route.
    	top_k (int): Maximum number of candidate stages to return (bounded to 1..MAX_TOP_K).
    	skillsets_dir (Path): Directory containing skill-set subfolders.
    
    Returns:
    	payload (dict): A structured routing result with these keys:
    		- schema_version (int): Payload schema version.
    		- status (str): One of "selected", "low_confidence", "no_match", or an error status (e.g., "manifest_missing", "manifest_invalid").
    		- policy_identity (dict): Identifying metadata for the routing policy.
    		- skill_set (str): Echoed input skill set.
    		- top_k (int): The bounded top_k used for this routing.
    		- selected (dict|None): When status is "selected", the chosen stage summary with `id`, `level`, `source_path`, and `confidence`; otherwise None.
    		- candidates (list[dict]): Ordered list of candidate summaries (each with `id`, `level`, `confidence`, `reason`).
    		- operator_action (str|None): Suggested next action for an operator when manual intervention or repair is required.
    """
    bounded_top_k = max(1, min(int(top_k), MAX_TOP_K))
    try:
        rows, error_status = read_manifest(skill_set, skillsets_dir)
    except ValueError as exc:
        return {
            "schema_version": 1,
            "status": "manifest_invalid",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "error": str(exc),
            "operator_action": "Repair the skill-set manifest and rerun routing.",
        }
    if error_status:
        return {
            "schema_version": 1,
            "status": error_status,
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "operator_action": "Generate manifests before routing." if error_status == "manifest_missing" else "Choose a valid root skill set.",
        }
    if skill_set in {"plugin-factory", "skill-factory"} and factory_scope_excluded(skill_set, task):
        return {
            "schema_version": 1,
            "status": "no_match",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "operator_action": "Handle as ordinary product work; factory routing is excluded by the task text.",
        }
    override = None
    try:
        if skill_set == "harness-engineering":
            routing_map_path = skillsets_dir.parent / "Plugins/harness-engineering/references/routing-map.json"
            if not routing_map_path.is_file():
                routing_map_path = None
            override = harness_engineering_override(task, rows, routing_map_path=routing_map_path)
        elif skill_set in {"plugin-factory", "skill-factory"}:
            override = factory_override(skill_set, task, rows)
    except ValueError as exc:
        return {
            "schema_version": 1,
            "status": "routing_policy_invalid",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "error": str(exc),
            "operator_action": "Repair the routing policy and rerun routing.",
        }
    if override:
        selected_row = override["row"]
        selected_confidence = float(override["confidence"])
        candidates = [
            {
                "id": selected_row.get("id"),
                "level": selected_row.get("level"),
                "confidence": round(selected_confidence, 4),
                "reason": override["reason"],
            }
        ]
        return {
            "schema_version": 1,
            "status": "selected",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": selected_payload(selected_row, selected_confidence),
            "candidates": candidates,
            "operator_action": None,
        }
    scored = []
    for row in rows:
        confidence, reasons = score_row(row, task)
        if confidence <= 0:
            continue
        scored.append((confidence, row, reasons))
    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    candidates = [
        {
            "id": row.get("id"),
            "level": row.get("level"),
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "matched manifest metadata",
        }
        for confidence, row, reasons in scored[:bounded_top_k]
    ]
    if not candidates:
        return {
            "schema_version": 1,
            "status": "no_match",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "operator_action": "Ask a clarifying question or choose a documented fallback root skill set.",
        }
    selected_confidence, selected_row, _reasons = scored[0]
    if skill_set == "harness-engineering":
        selected_id = str(selected_row.get("id", ""))
        resolved_selected_id = resolve_he_stage_alias(selected_id)
        if resolved_selected_id != selected_id:
            selected_row = row_by_id(rows, resolved_selected_id) or selected_row
    status = "selected" if selected_confidence >= LOW_CONFIDENCE_THRESHOLD else "low_confidence"
    selected = None
    if status == "selected":
        selected = selected_payload(selected_row, selected_confidence)
    return {
        "schema_version": 1,
        "status": status,
        "policy_identity": policy_identity(),
        "skill_set": skill_set,
        "top_k": bounded_top_k,
        "selected": selected,
        "candidates": candidates,
        "operator_action": None if selected else "Clarify before loading a latent module.",
    }


def read_task(args: argparse.Namespace) -> str:
    sources = [bool(args.task), bool(args.task_stdin), bool(args.task_file)]
    if sum(sources) != 1:
        raise SystemExit("Specify exactly one of --task, --task-stdin, or --task-file.")
    if args.task:
        return args.task
    if args.task_stdin:
        import sys

        return sys.stdin.read().strip()
    task_path = Path(args.task_file)
    if not task_path.is_file():
        raise SystemExit(f"Task file not found: {args.task_file}")
    return task_path.read_text(encoding="utf-8").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-set", required=True)
    parser.add_argument("--task", help="Task text; use --task-stdin or --task-file for sensitive tasks")
    parser.add_argument("--task-stdin", action="store_true")
    parser.add_argument("--task-file")
    parser.add_argument("--top-k", type=int, default=MAX_TOP_K)
    parser.add_argument("--skillsets-dir", type=Path, default=DEFAULT_SKILLSETS_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = route(args.skill_set, read_task(args), top_k=args.top_k, skillsets_dir=args.skillsets_dir)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"route status: {payload['status']}")
        selected = payload.get("selected")
        if selected:
            print(f"selected: {selected['id']} ({selected['source_path']})")
    return 0 if payload["status"] in {"selected", "low_confidence", "no_match"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
