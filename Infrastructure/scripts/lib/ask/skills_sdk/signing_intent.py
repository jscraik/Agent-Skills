from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ask.skills_sdk.signing_contracts import validate_signing_policy


SIGNING_POLICY_SCHEMA_VERSION = "skills-sdk.signing-policy.v0"
SIGNING_POLICY_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/signing-policy.v0.schema.json"
)
SIGNING_INTENT_RECEIPT_SCHEMA_VERSION = "skills-sdk.signing-intent-receipt.v0"
SIGNING_INTENT_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/signing-intent-receipt.v0.schema.json"
)
SIGNING_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001", "VP-021"]

_ALLOWED_ALGORITHMS = {"cosign-keyless", "minisign", "ssh-sig"}
_ALLOWED_REDACTION_POLICIES = {"manifest_only", "manifest_and_receipts"}
_ALLOWED_KEY_POLICIES = {"external_ref_required", "keyless_required"}


class SigningIntentError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _read_policy(policy_path: Path) -> tuple[dict[str, Any] | None, str | None, list[dict[str, Any]]]:
    if not policy_path.is_file():
        return None, None, [_check("policy_readable", "blocker", "blocker", "Signing policy file is missing.", [str(policy_path)])]
    try:
        raw = policy_path.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, None, [_check("policy_parseable", "blocker", "blocker", "Signing policy must be readable JSON.", [str(exc)])]
    if not isinstance(payload, dict):
        return None, None, [_check("policy_object", "blocker", "blocker", "Signing policy must be a JSON object.", [type(payload).__name__])]
    return payload, _sha256_json(payload), []


def _check(check_id: str, status: str, severity: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": evidence or [],
    }


def _list_value(policy: dict[str, Any], key: str) -> list[str]:
    value = policy.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _policy_schema_check(policy: dict[str, Any]) -> dict[str, Any]:
    schema_version = policy.get("schema_version")
    schema_uri = policy.get("schema_uri")
    return _check(
        "policy_schema",
        "pass" if schema_version == SIGNING_POLICY_SCHEMA_VERSION and schema_uri == SIGNING_POLICY_SCHEMA_URI else "blocker",
        "blocker",
        "Signing policy must use the supported v0 schema identity.",
        [f"schema_version:{schema_version!s}", f"schema_uri:{schema_uri!s}"],
    )


def _policy_contract_check(policy: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_signing_policy(policy)
    except ValidationError as exc:
        errors = [f"{'.'.join(str(part) for part in item['loc'])}:{item['type']}" for item in exc.errors()]
        return _check(
            "policy_contract_valid",
            "blocker",
            "blocker",
            "Signing policy must satisfy the complete v0 schema contract.",
            errors,
        )
    return _check(
        "policy_contract_valid",
        "pass",
        "blocker",
        "Signing policy satisfies the complete v0 schema contract.",
    )


def _signer_identity_check(policy: dict[str, Any]) -> dict[str, Any]:
    signer_id = policy.get("signer_id")
    return _check(
        "signer_identity_declared",
        "pass" if isinstance(signer_id, str) and bool(signer_id.strip()) else "blocker",
        "blocker",
        "Signing policy must declare a signer_id before a signature can be requested.",
        [str(signer_id)],
    )


def _algorithm_check(policy: dict[str, Any]) -> dict[str, Any]:
    algorithms = _list_value(policy, "allowed_algorithms")
    return _check(
        "approved_algorithm",
        "pass" if algorithms and set(algorithms).issubset(_ALLOWED_ALGORITHMS) else "blocker",
        "blocker",
        "Signing policy algorithms must be from the approved local allowlist.",
        algorithms,
    )


def _key_material_check(policy: dict[str, Any]) -> dict[str, Any]:
    key_material_policy = policy.get("key_material_policy")
    return _check(
        "key_material_policy",
        "pass" if key_material_policy in _ALLOWED_KEY_POLICIES else "blocker",
        "blocker",
        "Signing policy must keep key material external to the SDK receipt path.",
        [str(key_material_policy)],
    )


def _redaction_check(policy: dict[str, Any]) -> dict[str, Any]:
    redaction_policy = policy.get("redaction_policy")
    return _check(
        "redaction_policy",
        "pass" if redaction_policy in _ALLOWED_REDACTION_POLICIES else "blocker",
        "blocker",
        "Signing policy must choose an approved redaction policy before signing.",
        [str(redaction_policy)],
    )


def _hardening_required_check(policy: dict[str, Any]) -> dict[str, Any]:
    return _check(
        "hardening_required",
        "pass" if policy.get("requires_hardening_pass") is True else "blocker",
        "blocker",
        "Signing policy must require a passing package hardening receipt.",
        [f"requires_hardening_pass:{policy.get('requires_hardening_pass')!s}"],
    )


def _archive_not_required_check(policy: dict[str, Any]) -> dict[str, Any]:
    return _check(
        "archive_not_required_for_intent",
        "pass" if policy.get("archive_required") is False else "blocker",
        "blocker",
        "Signing intent must not require or emit an archive before archive ownership is approved.",
        [f"archive_required:{policy.get('archive_required')!s}"],
    )


def _policy_shape_checks(policy: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _policy_schema_check(policy),
        _policy_contract_check(policy),
        _signer_identity_check(policy),
        _algorithm_check(policy),
        _key_material_check(policy),
        _redaction_check(policy),
        _hardening_required_check(policy),
        _archive_not_required_check(policy),
    ]


def _package_identity_check(policy: dict[str, Any], package_receipt: dict[str, Any]) -> dict[str, Any]:
    package_id = str(package_receipt.get("package_id") or "")
    allowed_packages = _list_value(policy, "allowed_package_ids")
    return _check(
        "package_identity_allowed",
        "pass" if package_id in allowed_packages else "blocker",
        "blocker",
        "Signing policy must explicitly allow the package id.",
        [f"package_id:{package_id}", *allowed_packages],
    )


def _package_digest_check(policy: dict[str, Any], package_receipt: dict[str, Any]) -> dict[str, Any]:
    package_digest = str(package_receipt.get("package_digest") or "")
    allowed_digests = _list_value(policy, "allowed_package_digests")
    return _check(
        "package_digest_pinned",
        "pass" if package_digest in allowed_digests else "blocker",
        "blocker",
        "Signing policy must pin the exact package digest before requesting a signature.",
        [f"package_digest:{package_digest}", *allowed_digests],
    )


def _hardening_passed_check(hardening_receipt: dict[str, Any]) -> dict[str, Any]:
    return _check(
        "package_hardening_passed",
        "pass" if hardening_receipt.get("status") == "pass" else "blocker",
        "blocker",
        "Signing intent requires a passing package hardening receipt.",
        [f"hardening_status:{hardening_receipt.get('status')!s}"],
    )


def _read_only_package_check(package_receipt: dict[str, Any], hardening_receipt: dict[str, Any]) -> dict[str, Any]:
    read_only = (
        package_receipt.get("mutation_performed") is False
        and hardening_receipt.get("mutation_performed") is False
    )
    return _check(
        "package_receipt_read_only",
        "pass" if read_only else "blocker",
        "blocker",
        "Signing intent only accepts read-only package and hardening receipts.",
        [
            f"package_mutation:{package_receipt.get('mutation_performed')!s}",
            f"hardening_mutation:{hardening_receipt.get('mutation_performed')!s}",
        ],
    )


def _package_policy_checks(
    policy: dict[str, Any],
    package_receipt: dict[str, Any],
    hardening_receipt: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _package_identity_check(policy, package_receipt),
        _package_digest_check(policy, package_receipt),
        _hardening_passed_check(hardening_receipt),
        _read_only_package_check(package_receipt, hardening_receipt),
    ]


def _blocked_receipt(
    *,
    policy_path: Path,
    policy_digest: str | None,
    package_receipt: dict[str, Any],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    warnings = [check for check in checks if check["status"] == "warning"]
    receipt = _receipt(
        status="blocked",
        policy_path=policy_path,
        policy_digest=policy_digest,
        package_receipt=package_receipt,
        checks=checks,
        blockers=blockers,
        warnings=warnings,
    )
    receipt["agent_summary"] = f"skills-sdk signing intent blocked with {len(blockers)} blocker(s)."
    return receipt


def _receipt(
    *,
    status: str,
    policy_path: Path,
    policy_digest: str | None,
    package_receipt: dict[str, Any],
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": SIGNING_INTENT_RECEIPT_SCHEMA_VERSION,
        "schema_uri": SIGNING_INTENT_RECEIPT_SCHEMA_URI,
        "status": status,
        "policy_path": policy_path.as_posix(),
        "policy_digest": policy_digest,
        "package_id": str(package_receipt.get("package_id") or ""),
        "version": str(package_receipt.get("version") or ""),
        "source_digest": str(package_receipt.get("source_digest") or ""),
        "manifest_digest": str(package_receipt.get("manifest_digest") or ""),
        "package_digest": str(package_receipt.get("package_digest") or ""),
        "signing_checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "signature_requested": False,
        "signing_performed": False,
        "key_material_accessed": False,
        "artifact_emitted": False,
        "mutation_performed": False,
        "acceptance_trace": SIGNING_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"skills-sdk signing intent {status} for {package_receipt.get('package_id')!s} without signing."
        ),
    }


def build_signing_intent_receipt(
    *,
    policy_path: Path,
    package_receipt: dict[str, Any],
    hardening_receipt: dict[str, Any],
) -> dict[str, Any]:
    policy, policy_digest, checks = _read_policy(policy_path)
    if policy is None:
        receipt = _blocked_receipt(
            policy_path=policy_path,
            policy_digest=policy_digest,
            package_receipt=package_receipt,
            checks=checks,
        )
        raise SigningIntentError(receipt)

    checks.extend(_policy_shape_checks(policy))
    checks.extend(_package_policy_checks(policy, package_receipt, hardening_receipt))
    blockers = [check for check in checks if check["status"] == "blocker"]
    warnings = [check for check in checks if check["status"] == "warning"]
    status = "blocked" if blockers else "ready"
    receipt = _receipt(
        status=status,
        policy_path=policy_path,
        policy_digest=policy_digest,
        package_receipt=package_receipt,
        checks=checks,
        blockers=blockers,
        warnings=warnings,
    )
    if status != "ready":
        receipt["agent_summary"] = f"skills-sdk signing intent blocked with {len(blockers)} blocker(s)."
        raise SigningIntentError(receipt)
    return receipt
