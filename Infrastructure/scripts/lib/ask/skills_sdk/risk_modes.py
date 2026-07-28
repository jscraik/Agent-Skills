from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import body_without_frontmatter, read_skill_frontmatter_fields
from ask.skills_sdk.package_build import build_package_digest_receipt
from ask.skills_sdk.package_security_signature import build_package_security_signature_receipt
from ask.skills_sdk.risk import build_risk_classification


RISK_MODE_TAXONOMY_SCHEMA_VERSION = "skills-sdk.risk-mode-taxonomy-receipt.v0"
RISK_MODE_TAXONOMY_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/risk-mode-taxonomy-receipt.v0.schema.json"
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


def _digest_json(value: object) -> str:
    """
    Compute a SHA-256 digest of a JSON-serialized object.
    
    Parameters:
    	value (object): The object to digest
    
    Returns:
    	str: A digest string in the format `sha256:<hexdigest>`
    """
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    """
    Converts a path to a POSIX string, relative to the repository root if possible.
    
    Returns:
    	A POSIX path string, relative to repo_root if the path is within it, or the absolute path otherwise.
    """
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.name


def _text_signals(frontmatter: dict[str, Any], body: str) -> str:
    """
    Combine frontmatter and body into a single text blob for evidence scanning.
    
    Returns:
        A string containing the frontmatter as compact JSON (with sorted keys) on the first line, followed by the body text.
    """
    return json.dumps(frontmatter, sort_keys=True, separators=(",", ":")) + "\n" + body


def _indicator(indicator_id: str, evidence_ref: str, reason: str) -> dict[str, str]:
    """
    Construct an indicator record from the provided fields.
    
    Returns:
        dict[str, str]: A dictionary containing `id`, `evidence_ref`, and `reason` keys.
    """
    return {"id": indicator_id, "evidence_ref": evidence_ref, "reason": reason}


def _regex_indicators(mode: str, text: str, evidence_ref: str) -> list[dict[str, str]]:
    """
    Detect risk indicators by matching configured regex patterns for a given mode against text.
    
    Parameters:
        mode (str): The risk mode whose patterns to match against.
        text (str): The text to search within.
        evidence_ref (str): A reference identifier for the evidence source.
    
    Returns:
        list[dict[str, str]]: A list of indicator dictionaries for each matched pattern.
    """
    indicators: list[dict[str, str]] = []
    for indicator_id, pattern in INDICATORS[mode]:
        if not pattern:
            continue
        if re.search(pattern, text, flags=re.IGNORECASE):
            indicators.append(_indicator(indicator_id, evidence_ref, f"Matched deterministic signal {indicator_id}."))
    return indicators


def _has_safety_language(text: str) -> bool:
    """
    Determines whether text contains any safety-related terms.
    
    Returns:
    	True if text contains any term from SAFETY_TERMS, False otherwise.
    """
    lowered = text.lower()
    return any(term in lowered for term in SAFETY_TERMS)


def _frontmatter_value(frontmatter: dict[str, Any], key: str) -> Any:
    """
    Retrieve a value from frontmatter, falling back to a nested metadata dictionary.
    
    Treats None, empty string, empty list, and empty dict as missing values. When a top-level
    lookup yields a missing value, attempts to retrieve the value from the metadata sub-dictionary.
    
    Returns:
        The value from frontmatter or its metadata sub-dictionary if found, or None otherwise.
    """
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
    package_indicators: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """
    Collect and refine risk indicators for a given risk mode.
    
    Extracts regex-based indicators from the skill content, then applies
    mode-specific refinements based on the source kind and frontmatter context.
    
    Parameters:
        mode: The risk mode to analyze
        source_kind: The source kind (e.g., "external") affecting mode-specific detection
        frontmatter: The parsed YAML frontmatter of the skill file
        body: The text body of the skill file without frontmatter
        evidence_ref: A path reference to the skill file for evidence tracking
    
    Returns:
        A list of indicators, each containing id, evidence_ref, and reason fields
    """
    text = _text_signals(frontmatter, body)
    indicators = _regex_indicators(mode, text, evidence_ref)
    indicators.extend(_package_indicators_for_mode(mode, package_indicators or []))
    return _mode_specific_indicators(
        mode,
        indicators=indicators,
        text=text,
        source_kind=source_kind,
        frontmatter=frontmatter,
        evidence_ref=evidence_ref,
    )


PACKAGE_INDICATOR_MODE_MAP: dict[str, tuple[str, ...]] = {
    "malicious_supply_chain": (
        "hidden_unicode_obfuscation",
        "pipe_to_shell_download",
        "suspicious_download_url",
        "runtime_instruction_fetch",
    ),
    "negligent_instruction": (
        "system_service_modification",
        "destructive_local_capability",
    ),
    "vulnerable_operation": (
        "hardcoded_secret_literal",
        "insecure_credential_output",
        "untrusted_external_content_acquisition",
        "composed_capability_risk",
    ),
}


def _package_indicators_for_mode(mode: str, package_indicators: list[dict[str, str]]) -> list[dict[str, str]]:
    wanted = set(PACKAGE_INDICATOR_MODE_MAP.get(mode, ()))
    return [
        _indicator(
            indicator["id"],
            indicator["evidence_ref"],
            f"Package security signature detected {indicator['id']}.",
        )
        for indicator in package_indicators
        if indicator["id"] in wanted
    ]


def _mode_specific_indicators(
    mode: str,
    *,
    indicators: list[dict[str, str]],
    text: str,
    source_kind: str,
    frontmatter: dict[str, Any],
    evidence_ref: str,
) -> list[dict[str, str]]:
    """
    Refine indicators with mode-specific post-processing logic.
    
    For malicious_supply_chain mode with external sources, appends an external-source indicator. Then dispatches to mode-specific refinement handlers which may add or modify indicators based on evidence patterns.
    
    Returns:
    	list[dict[str, str]]: The refined indicators after mode-specific processing.
    """
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
    """
    Refines negligent instruction indicators by validating boundary language presence.
    
    Adds a boundary language indicator if impactful actions lack safeguard language (approval, sandbox, preview, rollback, or redaction). Removes only missing_safety_language; an impactful action remains visible even when boundary language is present.
    
    Parameters:
        indicators: Indicator list to refine.
        text: Text to validate for safety language.
        evidence_ref: Reference to the evidence location.
    
    Returns:
        Refined indicator list.
    """
    has_impactful_action = any(indicator["id"] == "impactful_write_without_review" for indicator in indicators)
    has_safety_boundary = _has_safety_language(text)
    if has_impactful_action and not has_safety_boundary:
        indicators.append(
            _indicator(
                "no_boundary_language",
                evidence_ref,
                "Impactful actions are present without approval, sandbox, preview, rollback, or redaction language.",
            )
        )
    ignored_ids = {"missing_safety_language"}
    retained = [indicator for indicator in indicators if indicator["id"] not in ignored_ids]
    return retained


def _vulnerable_indicators(indicators: list[dict[str, str]], text: str, evidence_ref: str) -> list[dict[str, str]]:
    """
    Appends a secret_without_redaction indicator when secret handling is detected without redaction guidance.
    
    Returns:
        The indicators list, with the indicator appended if applicable.
    """
    has_secret_handling = any(indicator["id"] == "secret_handling" for indicator in indicators)
    has_redaction = "redact" in text.lower() or "do not print" in text.lower()
    if has_secret_handling and not has_redaction:
        indicators.append(_indicator("secret_without_redaction", evidence_ref, "Secret handling is present without explicit redaction guidance."))
    return indicators


def _unknown_evidence_indicators(
    indicators: list[dict[str, str]], frontmatter: dict[str, Any], evidence_ref: str
) -> list[dict[str, str]]:
    """
    Appends indicators for missing provenance and description fields in frontmatter.
    
    Returns:
        The updated indicators list.
    """
    if not (_frontmatter_value(frontmatter, "provenance") or _frontmatter_value(frontmatter, "owner")):
        indicators.append(_indicator("missing_provenance", evidence_ref, "No provenance field was declared."))
    if not _frontmatter_value(frontmatter, "description"):
        indicators.append(_indicator("missing_purpose", evidence_ref, "No description field was declared."))
    return indicators


def _mode_status(indicators: list[dict[str, str]]) -> str:
    """
    Determine the status of a risk mode based on indicator presence.
    
    Returns:
    	status (str): `'detected'` if any indicators are present, `'not_detected'` otherwise.
    """
    return "detected" if indicators else "not_detected"


def _mode_result(
    mode: str,
    *,
    source_kind: str,
    frontmatter: dict[str, Any],
    body: str,
    evidence_ref: str,
    package_indicators: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Assesses whether a risk mode is present in the skill source.
    
    Returns:
        A dictionary containing the mode name, label, severity, description, detection status
        ("detected" or "not_detected"), and matched indicators.
    """
    indicators = _mode_indicators(
        mode,
        source_kind=source_kind,
        frontmatter=frontmatter,
        body=body,
        evidence_ref=evidence_ref,
        package_indicators=package_indicators,
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
    """
    Identify the highest-priority detected risk mode.
    
    Parameters:
        mode_results (list[dict[str, Any]]): Per-mode result dictionaries, each
            containing "mode" (str) and "status" (str) keys.
    
    Returns:
        str: The name of the primary risk mode if detected, or `"none_detected"`.
    """
    for mode in RISK_MODE_ORDER:
        for result in mode_results:
            if result["mode"] == mode and result["status"] == "detected":
                return mode
    return "none_detected"


def build_risk_mode_taxonomy_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    package_security_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a risk taxonomy receipt by analyzing a skill package for risk indicators across defined modes.
    
    Returns:
        A taxonomy receipt dictionary containing schema metadata, source classification, mode-based analysis results, detected risk modes, and operation metadata.
    """
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    frontmatter = read_skill_frontmatter_fields(source)
    text = source.read_text(encoding="utf-8")
    body = body_without_frontmatter(text)
    classification = build_risk_classification(source, frontmatter, text)
    package_receipt = build_package_digest_receipt(repo_root, source_path=source, query=query)
    if package_security_receipt is None:
        package_security_receipt = build_package_security_signature_receipt(repo_root, source_path=source, query=query)
    evidence_ref = _repo_relative(repo_root, source)
    mode_results = [
        _mode_result(
            mode,
            source_kind=str(classification["source_kind"]),
            frontmatter=frontmatter,
            body=body,
            evidence_ref=evidence_ref,
            package_indicators=package_security_receipt["indicators"],
        )
        for mode in RISK_MODE_ORDER
    ]
    detected_modes = [result["mode"] for result in mode_results if result["status"] == "detected"]
    return _taxonomy_receipt(
        query=query,
        package_receipt=package_receipt,
        package_security_receipt=package_security_receipt,
        classification=classification,
        mode_results=mode_results,
        detected_modes=detected_modes,
    )


def _taxonomy_receipt(
    *,
    query: str,
    package_receipt: dict[str, Any],
    package_security_receipt: dict[str, Any],
    classification: dict[str, Any],
    mode_results: list[dict[str, Any]],
    detected_modes: list[str],
) -> dict[str, Any]:
    """
    Assemble a risk-mode taxonomy receipt combining query context, package metadata, and mode analysis results.
    
    Parameters:
    	query (str): The query string identifying the inspection task.
    	package_receipt (dict[str, Any]): Package metadata containing package_id, package_digest, and source_digest.
    	classification (dict[str, Any]): Risk classification containing source_kind and risk_tier.
    	mode_results (list[dict[str, Any]]): Per-mode detection results with indicators and status.
    	detected_modes (list[str]): List of detected risk mode names.
    
    Returns:
    	dict[str, Any]: A structured receipt dictionary with schema metadata, classification, mode results, digests, and execution flags indicating preview-only behavior.
    """
    return {
        "schema_version": RISK_MODE_TAXONOMY_SCHEMA_VERSION,
        "schema_uri": RISK_MODE_TAXONOMY_SCHEMA_URI,
        "status": "pass",
        "operation": "risk_mode_taxonomy_preview",
        "query": query,
        "package_id": package_receipt["package_id"],
        "package_digest": package_receipt["package_digest"],
        "source_digest": package_receipt["source_digest"],
        "package_security_signature_digest": package_security_receipt["package_security_signature_digest"],
        "package_security_indicator_summary": package_security_receipt["indicator_summary"],
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
