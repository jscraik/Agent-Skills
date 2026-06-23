from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import read_skill_frontmatter_fields
from ask.skills_sdk.risk_modes import (
    RISK_MODE_TAXONOMY_SCHEMA_VERSION,
    build_risk_mode_taxonomy_receipt,
)
from ask.skills_sdk.skill_intake import build_skill_intake_receipt


SKILL_INTAKE_REVIEW_SCHEMA_VERSION = "skills-sdk.skill-intake-review-receipt.v0"
SKILL_INTAKE_REVIEW_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/skill-intake-review-receipt.v0.schema.json"
)
SKILL_INTAKE_REVIEW_ACCEPTANCE_TRACE = ["PU-034", "FR-008", "FR-010", "SA-004", "SEC-001", "VP-034"]
REVIEW_ITEM_IDS = (
    "provenance",
    "permissions",
    "data_exposure",
    "action_surface",
    "isolation",
    "semantic_behavior",
    "approval_friction",
    "risk_modes",
)
DATA_EXPOSURE_PATTERN = re.compile(r"\b(secret|credential|token|api key|password|log|stdout|stderr|transcript|trace)\b", re.IGNORECASE)
ACTION_SURFACE_PATTERN = re.compile(r"\b(write|modify|delete|publish|install|commit|push|deploy|message|ticket|browser|api)\b", re.IGNORECASE)
APPROVAL_PATTERN = re.compile(r"\b(approval|ask|confirm|preview|dry-run|non-mutating|block|rollback|sandbox)\b", re.IGNORECASE)


def _body_without_frontmatter(text: str) -> str:
    """
    Remove YAML frontmatter from text bounded by --- delimiters.
    
    Parameters:
    	text (str): The text to process, potentially containing YAML frontmatter
    
    Returns:
    	str: Text content following the frontmatter block if present, otherwise the original text, with leading and trailing whitespace removed
    """
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def _digest_json(value: object) -> str:
    """
    Computes a deterministic SHA-256 digest of an object.
    
    Returns:
    	A string in the format `sha256:<hexdigest>`, where `<hexdigest>` is the SHA-256 hash of the object's JSON representation.
    """
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _source_root(repo_root: Path, source: str) -> Path:
    """
    Resolve a source path relative to a repository root if the source is not absolute.
    
    Parameters:
        repo_root (Path): Base directory used if source is relative
        source (str): Source path string, which may include ~ for home directory
    
    Returns:
        Path: Resolved path without filesystem validation
    """
    source_path = Path(source).expanduser()
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    return source_path


def _review_item(
    item_id: str,
    status: str,
    question: str,
    evidence: list[str],
    verdict: str,
    reason: str,
) -> dict[str, Any]:
    """
    Constructs a standardized review-item object.
    
    Parameters:
        item_id (str): Identifier for the review item
        status (str): Review status ('pass', 'review', or 'block')
        question (str): The review question
        evidence (list[str]): Evidence supporting the determination
        verdict (str): The verdict or finding
        reason (str): The reason or explanation for the verdict
    
    Returns:
        dict[str, Any]: A dictionary with id, status, question, evidence, verdict, and reason keys
    """
    return {
        "id": item_id,
        "status": status,
        "question": question,
        "evidence": evidence,
        "verdict": verdict,
        "reason": reason,
    }


def _frontmatter_value(frontmatter: dict[str, Any], key: str) -> Any:
    """
    Extract a value from frontmatter, checking a metadata fallback if the primary value is empty.
    
    Returns:
    	Any: The value from frontmatter[key] if it is not None, empty string, empty list, or empty dict. Falls back to frontmatter["metadata"][key] if metadata is a dict. Returns None if no usable value is found.
    """
    value = frontmatter.get(key)
    if value not in (None, "", [], {}):
        return value
    metadata = frontmatter.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    return None


def _has_provenance(frontmatter: dict[str, Any]) -> bool:
    """
    Determines if a skill has documented provenance information.
    
    Returns:
    	`true` if the frontmatter contains meaningful provenance or owner information, `false` otherwise.
    """
    return bool(_frontmatter_value(frontmatter, "provenance") or _frontmatter_value(frontmatter, "owner"))


def _risk_mode_evidence(risk_mode_receipt: dict[str, Any]) -> list[str]:
    """
    Build evidence strings from detected risk modes and their indicators.
    
    Parameters:
        risk_mode_receipt (dict[str, Any]): Receipt containing mode_results with risk modes and their indicators.
    
    Returns:
        list[str]: Evidence strings formatted as `mode:indicator_ids` for modes with indicators, or the mode name alone.
    """
    evidence: list[str] = []
    for mode_result in risk_mode_receipt["mode_results"]:
        if mode_result["status"] != "detected":
            continue
        indicators = ", ".join(indicator["id"] for indicator in mode_result["indicators"])
        evidence.append(f"{mode_result['mode']}:{indicators}" if indicators else str(mode_result["mode"]))
    return evidence


def _review_items(
    *,
    frontmatter: dict[str, Any],
    body: str,
    intake_receipt: dict[str, Any],
    risk_mode_receipt: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Generate review items analyzing a skill's content and risk exposure.
    
    Returns:
        list[dict[str, Any]]: A list of eight review items, each containing id, status, question, evidence, verdict, and reason fields.
    """
    text = json.dumps(frontmatter, sort_keys=True, separators=(",", ":")) + "\n" + body
    context = {
        "detected_modes": set(risk_mode_receipt["detected_modes"]),
        "has_action_surface": bool(ACTION_SURFACE_PATTERN.search(text)),
        "has_data_exposure": bool(DATA_EXPOSURE_PATTERN.search(text)),
        "has_approval_language": bool(APPROVAL_PATTERN.search(text)),
        "has_provenance": _has_provenance(frontmatter),
        "risk_evidence": _risk_mode_evidence(risk_mode_receipt),
    }
    return [
        _provenance_item(context),
        _permissions_item(context),
        _data_exposure_item(context),
        _action_surface_item(context),
        _isolation_item(intake_receipt),
        _semantic_behavior_item(context),
        _approval_friction_item(context),
        _risk_modes_item(context),
    ]


def _provenance_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Build a review item assessing whether the skill declares provenance or ownership.
    
    Returns:
        dict[str, Any]: A review item with status "pass" if provenance is present, "review" otherwise.
    """
    has_provenance = bool(context["has_provenance"])
    return _review_item(
        "provenance",
        "pass" if has_provenance else "review",
        "Does the skill declare an owner or provenance before adoption?",
        ["frontmatter.provenance"] if has_provenance else ["missing provenance or owner field"],
        "declared" if has_provenance else "needs_human_review",
        "Structured owner/provenance evidence is present." if has_provenance else "External intake should not treat source identity as known.",
    )


def _permissions_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Creates a review item assessing whether declared or inferred permissions require human review based on detected risk modes.
    """
    risky_modes = context["detected_modes"] & {"malicious_supply_chain", "negligent_instruction", "vulnerable_operation"}
    return _review_item(
        "permissions",
        "review" if risky_modes else "pass",
        "Do declared or inferred permissions need a reviewer before activation?",
        context["risk_evidence"] or ["risk-mode receipt has no permission-affecting modes"],
        "needs_human_review" if risky_modes else "bounded",
        "Risk modes indicate permission-bearing behavior." if risky_modes else "No permission-bearing risk mode was detected.",
    )


def _data_exposure_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Create a review item assessing whether the skill text contains data-exposure language.
    
    Parameters:
    	context (dict[str, Any]): Context dictionary with "has_data_exposure" flag indicating whether data-exposure patterns were detected.
    
    Returns:
    	dict[str, Any]: Review item evaluating potential secrets, logs, or transcripts exposure.
    """
    has_data_exposure = bool(context["has_data_exposure"])
    return _review_item(
        "data_exposure",
        "review" if has_data_exposure else "pass",
        "Could the skill expose secrets, logs, transcripts, or tool output?",
        ["matched data-exposure language"] if has_data_exposure else ["no deterministic data-exposure terms detected"],
        "needs_human_review" if has_data_exposure else "bounded",
        "The skill text references data that needs exposure boundaries." if has_data_exposure else "No deterministic data-exposure trigger was found.",
    )


def _action_surface_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Generates a review item assessing whether the skill contains action-surface language.
    
    Evaluates whether the skill's text includes deterministic terms indicating external actions
    such as writes, deploys, publishes, or other mutating operations.
    
    Parameters:
        context (dict): A dictionary containing has_action_surface (bool), indicating whether
            action-surface language was detected in the skill.
    
    Returns:
        dict: A review item with status "review" if action-surface language is detected,
            "pass" otherwise.
    """
    has_action_surface = bool(context["has_action_surface"])
    return _review_item(
        "action_surface",
        "review" if has_action_surface else "pass",
        "Could the skill cause writes, external actions, installs, publishes, messages, tickets, or deploys?",
        ["matched action-surface language"] if has_action_surface else ["no deterministic action-surface terms detected"],
        "needs_human_review" if has_action_surface else "bounded",
        "The skill text includes action terms that need adoption constraints." if has_action_surface else "No deterministic action-surface trigger was found.",
    )


def _isolation_item(intake_receipt: dict[str, Any]) -> dict[str, Any]:
    """
    Creates an isolation review item confirming the intake stayed quarantined.
    
    Parameters:
    	intake_receipt (dict[str, Any]): The intake receipt containing the schema version and execution flags
    
    Returns:
    	dict[str, Any]: A review item with "pass" status indicating the intake maintained a non-mutating quarantine boundary
    """
    return _review_item(
        "isolation",
        "pass",
        "Did intake stay inside quarantine without execution, install, network, or projection mutation?",
        [intake_receipt["schema_version"], "execution_performed=false", "install_performed=false", "mutation_performed=false"],
        "quarantined",
        "Directory intake already proved a non-mutating quarantine boundary.",
    )


def _semantic_behavior_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Constructs a review item assessing semantic behavior risks.
    
    Returns:
        A review item dictionary containing the semantic behavior assessment based on detected risk modes.
    """
    semantic_modes = context["detected_modes"] & {"malicious_supply_chain", "negligent_instruction", "unknown_insufficient_evidence"}
    return _review_item(
        "semantic_behavior",
        "review" if semantic_modes else "pass",
        "Does the skill's semantic instruction behavior need human review?",
        context["risk_evidence"] or ["risk-mode receipt detected no semantic risk modes"],
        "needs_human_review" if semantic_modes else "bounded",
        "Risk-mode taxonomy found semantic or evidence gaps." if semantic_modes else "No semantic risk mode was detected.",
    )


def _approval_friction_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Build a review item assessing approval friction for impactful actions.
    
    Returns:
        dict[str, Any]: A review item with "review" status if impactful actions lack approval friction, otherwise "pass" status.
    """
    needs_review = bool(context["has_action_surface"]) and not bool(context["has_approval_language"])
    return _review_item(
        "approval_friction",
        "review" if needs_review else "pass",
        "Does the skill describe meaningful human approval or preview friction for impactful actions?",
        ["action terms without approval language"] if needs_review else ["approval or preview boundary present, or no impactful action found"],
        "needs_human_review" if needs_review else "bounded",
        "Impactful actions are present without explicit approval friction." if needs_review else "Approval friction is either present or not required by detected action surface.",
    )


def _risk_modes_item(context: dict[str, Any]) -> dict[str, Any]:
    """
    Builds a review item for detected risk modes.
    
    Returns:
    	A review item dict with status "review" if any risk modes were detected, "pass" otherwise.
    """
    detected_modes = context["detected_modes"]
    return _review_item(
        "risk_modes",
        "review" if detected_modes else "pass",
        "What Tal/Podjarny risk modes did the consumed risk-mode receipt detect?",
        context["risk_evidence"] or ["none_detected"],
        "needs_human_review" if detected_modes else "bounded",
        "Detected risk modes must feed the adoption decision." if detected_modes else "Risk-mode taxonomy found no current modes.",
    )


def _decision(review_items: list[dict[str, Any]]) -> str:
    """
    Determine the overall review decision based on aggregated review item statuses.
    
    Returns:
        'blocked' if any item blocks review, 'needs_human_review' if any item requires review, 'ready_for_adoption_decision' otherwise.
    """
    if any(item["status"] == "block" for item in review_items):
        return "blocked"
    if any(item["status"] == "review" for item in review_items):
        return "needs_human_review"
    return "ready_for_adoption_decision"


def _status(review_items: list[dict[str, Any]]) -> str:
    """
    Derive a status code from review items.
    
    Returns:
        str: 'blocked' if the review is blocked, 'review' if human review is needed, 'pass' otherwise.
    """
    decision = _decision(review_items)
    if decision == "blocked":
        return "blocked"
    if decision == "needs_human_review":
        return "review"
    return "pass"


def _residual_risk(review_items: list[dict[str, Any]], risk_mode_receipt: dict[str, Any]) -> list[str]:
    """
    Identify residual risks from detected modes and review items requiring review.
    
    Parameters:
        review_items: List of review item objects, each containing an 'id' and 'status'.
        risk_mode_receipt: Receipt containing 'detected_modes' list of risk mode names.
    
    Returns:
        List of risk identifiers as strings in the format 'risk_mode:<mode>' for each detected mode and 'review_item:<item_id>' for each review item with status 'review'.
    """
    risks = [f"risk_mode:{mode}" for mode in risk_mode_receipt["detected_modes"]]
    risks.extend(f"review_item:{item['id']}" for item in review_items if item["status"] == "review")
    return risks


def _blocked_receipt(repo_root: Path, source: str, intake_receipt: dict[str, Any]) -> dict[str, Any]:
    """
    Construct a blocked skill intake review receipt for skills with intake quarantine blockers.
    
    Returns:
    	dict[str, Any]: A receipt with status 'blocked', containing an isolation review item
    		that lists the intake's blockers as evidence, and indicating no code execution or
    		mutation occurred. Requires intake blockers to be cleared before risk-mode review can proceed.
    """
    source_path = _source_root(repo_root, source)
    review_items = [
        _review_item(
            "isolation",
            "block",
            "Did quarantine inspection complete before review?",
            [blocker["id"] for blocker in intake_receipt.get("blockers", [])],
            "blocked",
            "Risk-mode review is skipped until intake quarantine blockers are cleared.",
        )
    ]
    return {
        "schema_version": SKILL_INTAKE_REVIEW_SCHEMA_VERSION,
        "schema_uri": SKILL_INTAKE_REVIEW_SCHEMA_URI,
        "status": "blocked",
        "operation": "skill_intake_review_preview",
        "source_kind": intake_receipt["source_kind"],
        "source_path": intake_receipt["source_path"],
        "source_digest": intake_receipt["source_digest"],
        "skill_id": intake_receipt["skill_id"],
        "package_id": None,
        "package_digest": None,
        "intake_receipt": intake_receipt,
        "risk_mode_receipt": None,
        "risk_mode_receipt_digest": None,
        "required_receipts": [intake_receipt["schema_version"], RISK_MODE_TAXONOMY_SCHEMA_VERSION],
        "review_decision": "blocked",
        "review_items": review_items,
        "residual_risk": ["intake_blocked"],
        "execution_performed": False,
        "scanner_execution_performed": False,
        "install_performed": False,
        "projection_mutation_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SKILL_INTAKE_REVIEW_ACCEPTANCE_TRACE,
        "agent_summary": f"External skill intake review blocked {source_path.name}; clear quarantine blockers before risk-mode review.",
    }


def build_skill_intake_review_receipt(
    repo_root: Path,
    *,
    source: str,
    source_kind: str = "directory",
) -> dict[str, Any]:
    """Build a non-mutating external skill review receipt from intake and risk-mode receipts."""
    intake_receipt = build_skill_intake_receipt(repo_root, source=source, source_kind=source_kind)
    if intake_receipt["status"] == "blocked":
        return _blocked_receipt(repo_root, source, intake_receipt)

    source_root = _source_root(repo_root, source).resolve(strict=True)
    skill_file = source_root / "SKILL.md"
    frontmatter = read_skill_frontmatter_fields(skill_file)
    body = _body_without_frontmatter(skill_file.read_text(encoding="utf-8"))
    risk_mode_receipt = build_risk_mode_taxonomy_receipt(repo_root, source_path=skill_file, query=intake_receipt["skill_id"])
    review_items = _review_items(
        frontmatter=frontmatter,
        body=body,
        intake_receipt=intake_receipt,
        risk_mode_receipt=risk_mode_receipt,
    )
    decision = _decision(review_items)
    return _review_receipt(
        intake_receipt=intake_receipt,
        risk_mode_receipt=risk_mode_receipt,
        review_items=review_items,
        decision=decision,
    )


def _review_receipt(
    *,
    intake_receipt: dict[str, Any],
    risk_mode_receipt: dict[str, Any],
    review_items: list[dict[str, Any]],
    decision: str,
) -> dict[str, Any]:
    """
    Construct a skill intake review receipt from intake, risk-mode, and review assessments.
    
    Parameters:
        decision (str): The overall review decision ("blocked", "needs_human_review", or "ready_for_adoption_decision").
    
    Returns:
        dict[str, Any]: A receipt dictionary with schema information, source/package identity, embedded receipts, and review items.
    """
    return {
        "schema_version": SKILL_INTAKE_REVIEW_SCHEMA_VERSION,
        "schema_uri": SKILL_INTAKE_REVIEW_SCHEMA_URI,
        "status": _status(review_items),
        "operation": "skill_intake_review_preview",
        "source_kind": intake_receipt["source_kind"],
        "source_path": intake_receipt["source_path"],
        "source_digest": intake_receipt["source_digest"],
        "skill_id": intake_receipt["skill_id"],
        "package_id": risk_mode_receipt["package_id"],
        "package_digest": risk_mode_receipt["package_digest"],
        "intake_receipt": intake_receipt,
        "risk_mode_receipt": risk_mode_receipt,
        "risk_mode_receipt_digest": _digest_json(risk_mode_receipt),
        "required_receipts": [intake_receipt["schema_version"], risk_mode_receipt["schema_version"]],
        "review_decision": decision,
        "review_items": review_items,
        "residual_risk": _residual_risk(review_items, risk_mode_receipt),
        "execution_performed": False,
        "scanner_execution_performed": False,
        "install_performed": False,
        "projection_mutation_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SKILL_INTAKE_REVIEW_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"External skill intake review classified {intake_receipt['skill_id']} as {decision} "
            f"using intake and risk-mode receipts without execution, scanners, network, credentials, install, or mutation."
        ),
    }
