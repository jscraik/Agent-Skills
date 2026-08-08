"""Deterministic policy overrides for skill-set routing."""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import MappingProxyType
from typing import Any

from route_skillset_support import row_by_id, signal_matches, tokenize
from skillset_model import repo_root

# Harness Engineering keeps folded stage bodies as preserved context while
# routing active calls through parent stages.
HE_FOLDED_STAGE_ALIASES = MappingProxyType(
    {
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
)
FACTORY_ORDINARY_WORK_TOKENS = frozenset(
    {
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
)
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
_HE_RECURRING_TOKENS = frozenset({"heartbeat", "monitor", "wake", "wakeup", "recurring", "continue"})
_HE_PHASE_TOKENS = frozenset({"phase", "phases", "plan", "slice", "slices", "unit", "units"})
_HE_GATE_TOKENS = frozenset({"commit", "review", "reviewed", "gate", "gates", "simplify", "validation"})
_PLUGIN_INTERNAL_LANES = frozenset({"plugin-factory-router", "plugin-router"})
_FACTORY_RULES = MappingProxyType({
    "plugin-factory": (
        (
            "plugin-creator",
            "create-plugin",
            frozenset({"create", "new", "scaffold", "generate", "make", "starter", "template"}),
            frozenset({"plugin", "plugins"}),
        ),
        (
            "plugin-installer",
            "install-plugin",
            frozenset({"install", "add", "sync", "marketplace", "repair", "visibility", "visible", "import", "discover", "discovery"}),
            frozenset({"plugin", "plugins"}),
        ),
        (
            "plugin-factory-router",
            "harden-plugin",
            frozenset({"harden", "validate", "audit", "release", "package", "convert", "build"}),
            frozenset({"plugin", "plugins"}),
        ),
    ),
    "skill-factory": (
        (
            "skillify",
            "skillify-workflow",
            frozenset({"skillify", "operationalize", "operationalise", "capture", "turn", "convert"}),
            frozenset({"workflow", "process", "session", "repeatable", "skill", "skills"}),
        ),
        (
            "skill-creator",
            "create-skill",
            frozenset({"create", "new", "scaffold", "generate", "make", "draft"}),
            frozenset({"skill", "skills"}),
        ),
        (
            "skill-installer",
            "install-skill",
            frozenset({"install", "add", "sync", "github", "curated"}),
            frozenset({"skill", "skills"}),
        ),
        (
            "skill-builder",
            "improve-skill-sdk-pipeline",
            frozenset({"improve", "harden", "fix", "repair", "review", "score", "eval", "evals", "tessl", "sdk"}),
            frozenset({"skill", "skills"}),
        ),
        (
            "skill-refactor",
            "refactor-skill",
            frozenset({"refactor", "simplify", "merge", "fold", "prune", "coverage", "session"}),
            frozenset({"skill", "skills"}),
        ),
        (
            "skill-factory-router",
            "harden-skill",
            frozenset({"harden", "validate", "audit", "release", "package", "eval", "benchmark"}),
            frozenset({"skill", "skills"}),
        ),
    ),
})


def factory_scope_excluded(skill_set: str, task: str) -> bool:
    task_text = task.lower()
    phrases = {
        "skill-factory": SKILL_FACTORY_NO_CHANGE_PHRASES,
        "plugin-factory": PLUGIN_FACTORY_NO_CHANGE_PHRASES,
    }.get(skill_set)
    if phrases is None:
        return False
    no_factory_change = any(phrase in task_text for phrase in phrases)
    return no_factory_change and bool(tokenize(task) & FACTORY_ORDINARY_WORK_TOKENS)


def resolve_he_stage_alias(stage_id: str) -> str:
    return HE_FOLDED_STAGE_ALIASES.get(stage_id, stage_id)


def he_row_for_stage(rows: list[dict[str, Any]], stage_id: str) -> tuple[dict[str, Any] | None, str]:
    resolved_stage_id = resolve_he_stage_alias(stage_id)
    return row_by_id(rows, resolved_stage_id), resolved_stage_id


def is_he_phase_heartbeat_request(task_text: str, task_tokens: set[str]) -> bool:
    recurring = bool(task_tokens & _HE_RECURRING_TOKENS)
    phase = bool(task_tokens & _HE_PHASE_TOKENS)
    gate = bool(task_tokens & _HE_GATE_TOKENS or "he-work" in task_text)
    return recurring and phase and gate


def selected_payload(row: dict[str, Any], confidence: float) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "level": row.get("level"),
        "source_path": row.get("source_path"),
        "confidence": round(confidence, 4),
    }


def is_stage_correctness_question(task_text: str, _task_tokens: set[str]) -> bool:
    patterns = (
        r"\bis\s+he-[a-z0-9-]+\s+(correct|right)\b",
        r"\bwhether\s+(to\s+use\s+)?he-[a-z0-9-]+\s+(is\s+)?(correct|right)\b",
        r"\bwhether\b.*\b(right|correct|best)\s+stage\b",
    )
    return any(re.search(pattern, task_text) for pattern in patterns) or any(
        phrase in task_text
        for phrase in ("right stage", "correct stage", "best stage", "which stage", "what stage", "should we use", "should i use", "should codex use")
    )


def _load_routing_map(routing_map_path: Path) -> dict[str, Any]:
    if not routing_map_path.is_file():
        return {}
    try:
        payload = json.loads(routing_map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid Harness Engineering routing map at {routing_map_path}: {exc}") from exc
    return payload


def _mentioned_he_stages(task_text: str, rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    stage_ids = {str(row.get("id")) for row in rows}
    mentioned = [
        stage
        for stage in re.findall(r"\bhe-[a-z0-9-]+\b", task_text)
        if stage in stage_ids or resolve_he_stage_alias(stage) in stage_ids
    ]
    distinct = sorted(set(mentioned))
    resolved = sorted({resolve_he_stage_alias(stage) for stage in distinct})
    return distinct, resolved


def _he_named_stage_override(
    task_text: str,
    task_tokens: set[str],
    rows: list[dict[str, Any]],
    mentioned: list[str],
    resolved: list[str],
) -> dict[str, Any] | None:
    router_row = row_by_id(rows, "he-reconcile")
    if len(resolved) > 1 and router_row:
        return {"row": router_row, "confidence": 0.9, "reason": "matched multi-stage HE rule 'named-stage-ambiguity'"}
    if mentioned and is_stage_correctness_question(task_text, task_tokens) and router_row:
        return {"row": router_row, "confidence": 0.9, "reason": "matched multi-stage HE rule 'stage-correctness-question'"}
    phase_work_row = row_by_id(rows, "he-phase-work")
    if phase_work_row and is_he_phase_heartbeat_request(task_text, task_tokens):
        return {"row": phase_work_row, "confidence": 0.97, "reason": "matched deterministic HE rule 'phase-work-control-loop'"}
    if mentioned:
        row, resolved_stage_id = he_row_for_stage(rows, mentioned[0])
        if row:
            reason = "matched deterministic HE rule 'direct-stage-invocation'"
            if resolved_stage_id != mentioned[0]:
                reason += f" via folded stage alias '{mentioned[0]}'"
            return {"row": row, "confidence": 1.0, "reason": reason}
    return None


def _he_rule_override(
    task_text: str,
    task_tokens: set[str],
    rows: list[dict[str, Any]],
    routing_map: dict[str, Any],
) -> dict[str, Any] | None:
    stage_ids = {str(row.get("id")) for row in rows}
    rules = sorted(routing_map.get("deterministic_decision_order", []), key=lambda item: item.get("priority", 999))
    for rule in rules:
        result = _he_rule_match(task_text, task_tokens, rows, stage_ids, rule)
        if result:
            return result
    return None


def _he_rule_match(
    task_text: str,
    task_tokens: set[str],
    rows: list[dict[str, Any]],
    stage_ids: set[str],
    rule: dict[str, Any],
) -> dict[str, Any] | None:
    route = str(rule.get("route", ""))
    signals = [str(signal) for signal in rule.get("signals", []) if isinstance(signal, str)]
    if not signals or not any(signal_matches(task_text, task_tokens, signal) for signal in signals):
        return None
    resolved_route = resolve_he_stage_alias(route)
    row = row_by_id(rows, resolved_route)
    if resolved_route in stage_ids and row:
        reason = f"matched deterministic HE rule '{rule.get('rule')}'"
        if resolved_route != route:
            reason += f" via folded stage alias '{route}'"
        elif rule.get("folded_from"):
            reason += f" via folded stage alias '{rule.get('folded_from')}'"
        return {"row": row, "confidence": 0.95, "reason": reason}
    if " or " in route or " -> " in route:
        row = row_by_id(rows, "he-reconcile")
        if row:
            return {"row": row, "confidence": 0.9, "reason": f"matched multi-stage HE rule '{rule.get('rule')}'"}
    return None


def harness_engineering_override(
    task: str,
    rows: list[dict[str, Any]],
    *,
    routing_map_path: Path | None = None,
) -> dict[str, Any] | None:
    routing_path = routing_map_path or repo_root() / "Plugins/harness-engineering/references/routing-map.json"
    routing_map = _load_routing_map(routing_path)
    task_text = task.lower()
    task_tokens = tokenize(task)
    mentioned, resolved = _mentioned_he_stages(task_text, rows)
    named_override = _he_named_stage_override(task_text, task_tokens, rows, mentioned, resolved)
    return named_override or _he_rule_override(task_text, task_tokens, rows, routing_map)


def _factory_internal_override(skill_set: str, task_tokens: set[str], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if skill_set == "plugin-factory" and task_tokens & _PLUGIN_INTERNAL_LANES:
        row = row_by_id(rows, "plugin-factory-router")
        if row:
            return {"row": row, "confidence": 0.9, "reason": "matched deterministic plugin-factory rule 'internal-lane-mention'"}
    if skill_set != "skill-factory":
        return None
    if task_tokens & frozenset({"plugin", "plugins", "hook", "hooks", "mcp"}):
        row = row_by_id(rows, "skill-factory-router")
        if row:
            return {"row": row, "confidence": 0.9, "reason": "matched deterministic skill-factory rule 'plugin-boundary-handoff'"}
    if (
        task_tokens & frozenset({"feedback", "coderabbit", "codex"})
        and task_tokens & frozenset({"again", "across", "recurring", "repeat", "repeated", "same"})
        and task_tokens & frozenset({"skill", "skills", "context", "package", "packages", "eval", "evals"})
    ):
        row = row_by_id(rows, "skill-refactor")
        if row:
            return {"row": row, "confidence": 0.95, "reason": "matched deterministic skill-factory rule 'context-feedback-analysis'"}
    return None


def _factory_direct_override(skill_set: str, task: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    row_ids = {str(row.get("id")) for row in rows}
    mentions = [row_id for row_id in sorted(row_ids, key=len, reverse=True) if row_id in task.lower()]
    if len(mentions) == 1:
        row = row_by_id(rows, mentions[0])
        if row:
            return {"row": row, "confidence": 1.0, "reason": f"matched deterministic {skill_set} rule 'direct-lane-invocation'"}
    if len(mentions) > 1:
        router_id = "plugin-factory-router" if skill_set == "plugin-factory" else "skill-factory-router"
        row = row_by_id(rows, router_id)
        if row:
            return {"row": row, "confidence": 0.9, "reason": f"matched deterministic {skill_set} rule 'multi-lane-ambiguity'"}
    return None


def _preferred_factory_match(skill_set: str, matched: list[tuple[str, str]]) -> tuple[str, str] | None:
    if skill_set == "skill-factory" and ("skill-builder", "improve-skill-sdk-pipeline") in matched:
        return ("skill-builder", "improve-skill-sdk-pipeline")
    if skill_set == "skill-factory" and ("skill-refactor", "refactor-skill") in matched:
        return ("skill-refactor", "refactor-skill")
    return None


def _factory_rule_override(skill_set: str, task_tokens: set[str], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    row_ids = {str(row.get("id")) for row in rows}
    matched = [
        (route_id, rule_name)
        for route_id, rule_name, action_tokens, noun_tokens in _FACTORY_RULES.get(skill_set, ())
        if route_id in row_ids and task_tokens & action_tokens and task_tokens & noun_tokens
    ]
    if len(matched) == 1:
        route_id, rule_name = matched[0]
        row = row_by_id(rows, route_id)
        if row:
            return {"row": row, "confidence": 0.95, "reason": f"matched deterministic {skill_set} rule '{rule_name}'"}
    if len(matched) > 1:
        preferred = _preferred_factory_match(skill_set, matched)
        if preferred is not None:
            route_id, rule_name = preferred
            row = row_by_id(rows, route_id)
            if row:
                return {"row": row, "confidence": 0.95, "reason": f"matched deterministic {skill_set} rule '{rule_name}' with explicit precedence"}
        router_id = "plugin-factory-router" if skill_set == "plugin-factory" else "skill-factory-router"
        row = row_by_id(rows, router_id)
        if row:
            return {"row": row, "confidence": 0.9, "reason": f"matched deterministic {skill_set} rule 'multi-intent-factory-task'"}
    return None


def factory_override(skill_set: str, task: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    task_tokens = tokenize(task)
    internal = _factory_internal_override(skill_set, task_tokens, rows)
    if internal:
        return internal
    direct = _factory_direct_override(skill_set, task, rows)
    if direct:
        return direct
    return _factory_rule_override(skill_set, task_tokens, rows)
