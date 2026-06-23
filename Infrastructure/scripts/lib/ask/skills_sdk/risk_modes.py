from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import read_skill_frontmatter_fields
from ask.skills_sdk.package_build import build_package_digest_receipt
from ask.skills_sdk.risk import build_risk_classification


RISK_MODE_TAXONOMY_SCHEMA_VERSION = "skills-sdk.risk-mode-taxonomy-receipt.v0"
RISK_MODE_TAXONOMY_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/risk-mode-taxonomy-receipt.v0.schema.json"
)
RISK_MODE_TAXONOMY_ACCEPTANCE_TRACE = ["PU-033", "FR-008", "SA-004", "SEC-001", "VP-033"]

RISK_MODE_ORDER = (
    "malicious_supply_chain",
    "negligent_instruction",
    "vulnerable_operation",
    "unknown_insufficient_evidence",
)

MODE_DEFINITIONS: dict[str, dict[str, str]] = {
    "malicious_supply_chain": {
        "label": "Malicious supply-chain risk",
        "description": "The skill package includes indicators that it may intentionally cause harm, hide behavior, or bypass review.",
        "severity": "critical",
    },
    "negligent_instruction": {
        "label": "Negligent instruction risk",
        "description": "The skill urges impactful behavior without enough boundaries, review gates, or rollback language.",
        "severity": "high",
    },
    "vulnerable_operation": {
        "label": "Vulnerable operation risk",
        "description": "The skill handles secrets, credentials, logs, external calls, or data exposure paths without clear safeguards.",
        "severity": "high",
    },
    "unknown_insufficient_evidence": {
        "label": "Unknown or insufficient-evidence risk",
        "description": "The package lacks enough structured provenance, purpose, or review evidence to classify confidently.",
        "severity": "medium",
    },
}

INDICATORS: dict[str, tuple[tuple[str, str], ...]] = {
    "malicious_supply_chain": (
        ("hidden_instruction", r"ignore (all )?(previous|prior) instructions|do not (tell|reveal|disclose)"),
        ("unreviewed_remote_fetch", r"curl\s+[^\n]+\|\s*(sh|bash)|wget\s+[^\n]+\|\s*(sh|bash)"),
        ("destructive_action", r"rm\s+-rf|delete all|drop table|wipe\s+(the\s+)?(repo|disk|database)"),
        ("credential_exfiltration", r"exfiltrat|send (the )?(token|secret|credential)|steal"),
    ),
    "negligent_instruction": (
        ("impactful_write_without_review", r"\b(write|modify|delete|publish|install|commit|push|deploy|message|ticket)\b"),
        ("missing_safety_language", r""),
    ),
    "vulnerable_operation": (
        ("secret_handling", r"\b(secret|credential|token|api key|password)\b"),
        ("log_exposure", r"\b(log|stdout|stderr|transcript|trace)\b"),
        ("external_network", r"https?://|\b(network|api|webhook|browser)\b"),
    ),
    "unknown_insufficient_evidence": (
        ("missing_provenance", r""),
        ("missing_purpose", r""),
    ),
}

SAFETY_TERMS = (
    "approval",
    "ask",
    "block",
    "rollback",
    "sandbox",
    "least privilege",
    "redact",
    "do not",
    "preview",
    "dry-run",
    "non-mutating",
)


def _body_without_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def _digest_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _text_signals(frontmatter: dict[str, Any], body: str) -> str:
    return json.dumps(frontmatter, sort_keys=True, separators=(",", ":")) + "\n" + body


def _indicator(indicator_id: str, evidence_ref: str, reason: str) -> dict[str, str]:
    return {"id": indicator_id, "evidence_ref": evidence_ref, "reason": reason}


def _regex_indicators(mode: str, text: str, evidence_ref: str) -> list[dict[str, str]]:
    indicators: list[dict[str, str]] = []
    for indicator_id, pattern in INDICATORS[mode]:
        if not pattern:
            continue
        if re.search(pattern, text, flags=re.IGNORECASE):
            indicators.append(_indicator(indicator_id, evidence_ref, f"Matched deterministic signal {indicator_id}."))
    return indicators


def _has_safety_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in SAFETY_TERMS)


def _frontmatter_value(frontmatter: dict[str, Any], key: str) -> Any:
    value = frontmatter.get(key)
    if value not in (None, "", [], {}):
        return value
    metadata = frontmatter.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    return None


def _mode_indicators(
    mode: str,
    *,
    source_kind: str,
    frontmatter: dict[str, Any],
    body: str,
    evidence_ref: str,
) -> list[dict[str, str]]:
    text = _text_signals(frontmatter, body)
    indicators = _regex_indicators(mode, text, evidence_ref)
    return _mode_specific_indicators(
        mode,
        indicators=indicators,
        text=text,
        source_kind=source_kind,
        frontmatter=frontmatter,
        evidence_ref=evidence_ref,
    )


def _mode_specific_indicators(
    mode: str,
    *,
    indicators: list[dict[str, str]],
    text: str,
    source_kind: str,
    frontmatter: dict[str, Any],
    evidence_ref: str,
) -> list[dict[str, str]]:
    if mode == "malicious_supply_chain" and source_kind == "external":
        indicators.append(_indicator("external_source", evidence_ref, "External source requires supply-chain review before adoption."))
    if mode == "negligent_instruction":
        return _negligent_indicators(indicators, text, evidence_ref)
    if mode == "vulnerable_operation":
        return _vulnerable_indicators(indicators, text, evidence_ref)
    if mode == "unknown_insufficient_evidence":
        return _unknown_evidence_indicators(indicators, frontmatter, evidence_ref)
    return indicators


def _negligent_indicators(indicators: list[dict[str, str]], text: str, evidence_ref: str) -> list[dict[str, str]]:
    has_impactful_action = any(indicator["id"] == "impactful_write_without_review" for indicator in indicators)
    if has_impactful_action and not _has_safety_language(text):
        indicators.append(
            _indicator(
                "no_boundary_language",
                evidence_ref,
                "Impactful actions are present without approval, sandbox, preview, rollback, or redaction language.",
            )
        )
    return [indicator for indicator in indicators if indicator["id"] != "missing_safety_language"]


def _vulnerable_indicators(indicators: list[dict[str, str]], text: str, evidence_ref: str) -> list[dict[str, str]]:
    has_secret_handling = any(indicator["id"] == "secret_handling" for indicator in indicators)
    has_redaction = "redact" in text.lower() or "do not print" in text.lower()
    if has_secret_handling and not has_redaction:
        indicators.append(_indicator("secret_without_redaction", evidence_ref, "Secret handling is present without explicit redaction guidance."))
    return indicators


def _unknown_evidence_indicators(
    indicators: list[dict[str, str]], frontmatter: dict[str, Any], evidence_ref: str
) -> list[dict[str, str]]:
    if not _frontmatter_value(frontmatter, "provenance"):
        indicators.append(_indicator("missing_provenance", evidence_ref, "No provenance field was declared."))
    if not _frontmatter_value(frontmatter, "description"):
        indicators.append(_indicator("missing_purpose", evidence_ref, "No description field was declared."))
    return indicators


def _mode_status(indicators: list[dict[str, str]]) -> str:
    return "detected" if indicators else "not_detected"


def _mode_result(
    mode: str,
    *,
    source_kind: str,
    frontmatter: dict[str, Any],
    body: str,
    evidence_ref: str,
) -> dict[str, Any]:
    indicators = _mode_indicators(
        mode,
        source_kind=source_kind,
        frontmatter=frontmatter,
        body=body,
        evidence_ref=evidence_ref,
    )
    definition = MODE_DEFINITIONS[mode]
    return {
        "mode": mode,
        "label": definition["label"],
        "status": _mode_status(indicators),
        "severity": definition["severity"],
        "description": definition["description"],
        "indicators": indicators,
    }


def _primary_mode(mode_results: list[dict[str, Any]]) -> str:
    for mode in RISK_MODE_ORDER:
        for result in mode_results:
            if result["mode"] == mode and result["status"] == "detected":
                return mode
    return "none_detected"


def build_risk_mode_taxonomy_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    """Build a deterministic, non-mutating risk-mode taxonomy receipt for one skill package."""
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    frontmatter = read_skill_frontmatter_fields(source)
    text = source.read_text(encoding="utf-8")
    body = _body_without_frontmatter(text)
    classification = build_risk_classification(source, frontmatter, text)
    package_receipt = build_package_digest_receipt(repo_root, source_path=source, query=query)
    evidence_ref = _repo_relative(repo_root, source)
    mode_results = [
        _mode_result(
            mode,
            source_kind=str(classification["source_kind"]),
            frontmatter=frontmatter,
            body=body,
            evidence_ref=evidence_ref,
        )
        for mode in RISK_MODE_ORDER
    ]
    detected_modes = [result["mode"] for result in mode_results if result["status"] == "detected"]
    return _taxonomy_receipt(
        query=query,
        package_receipt=package_receipt,
        classification=classification,
        mode_results=mode_results,
        detected_modes=detected_modes,
    )


def _taxonomy_receipt(
    *,
    query: str,
    package_receipt: dict[str, Any],
    classification: dict[str, Any],
    mode_results: list[dict[str, Any]],
    detected_modes: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": RISK_MODE_TAXONOMY_SCHEMA_VERSION,
        "schema_uri": RISK_MODE_TAXONOMY_SCHEMA_URI,
        "status": "pass",
        "operation": "risk_mode_taxonomy_preview",
        "query": query,
        "package_id": package_receipt["package_id"],
        "package_digest": package_receipt["package_digest"],
        "source_digest": package_receipt["source_digest"],
        "source_kind": classification["source_kind"],
        "risk_tier": classification["risk_tier"],
        "primary_mode": _primary_mode(mode_results),
        "detected_modes": detected_modes,
        "mode_results": mode_results,
        "taxonomy_digest": _digest_json(mode_results),
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": RISK_MODE_TAXONOMY_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"risk-mode taxonomy inspected {package_receipt['package_id']} and detected "
            f"{len(detected_modes)} risk mode(s) without execution, scanners, network, or mutation."
        ),
    }
