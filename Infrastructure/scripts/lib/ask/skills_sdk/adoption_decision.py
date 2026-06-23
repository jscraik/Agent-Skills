from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ask.skills_sdk.package_build import build_package_digest_receipt
from ask.skills_sdk.skill_intake import build_skill_intake_receipt
from ask.skills_sdk.skill_intake_review import build_skill_intake_review_receipt


ADOPTION_DECISION_SCHEMA_VERSION = "skills-sdk.adoption-decision-receipt.v0"
ADOPTION_DECISION_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/adoption-decision-receipt.v0.schema.json"
)
ADOPTION_DECISION_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001"]


def build_adoption_decision_receipt(
    repo_root: Path,
    *,
    source: str,
    source_kind: str = "directory",
    trust_receipt_path: str | None = None,
) -> dict[str, Any]:
    source_path = _source_path(repo_root, source)
    intake = build_skill_intake_receipt(repo_root, source=source, source_kind=source_kind)
    review = _build_intake_review_receipt(repo_root, source, source_kind)
    package = _build_package_receipt(repo_root, source_path, source)
    trust_receipt, trust_error = _load_trust_receipt(repo_root, trust_receipt_path)
    checks = _adoption_checks(intake, review, package, trust_receipt, trust_error)
    blockers = [check for check in checks if check["status"] == "blocker"]
    status = "ready" if not blockers else "blocked"
    return _adoption_receipt(source, source_kind, status, package, intake, review, trust_receipt, checks, blockers)


def _adoption_checks(
    intake: dict[str, Any],
    review: dict[str, Any],
    package: dict[str, Any],
    trust_receipt: dict[str, Any] | None,
    trust_error: str | None,
) -> list[dict[str, Any]]:
    return [
        _check(
            "intake_quarantine_preview",
            "pass" if intake["status"] == "preview" else "blocker",
            "External sources must pass non-mutating quarantine inspection before adoption.",
            [intake["status"]],
        ),
        _check(
            "intake_review_preview",
            "pass" if _intake_review_completed(review) else "blocker",
            "Permission, data exposure, action-surface, semantic, and approval review must complete before adoption.",
            [review["status"]],
        ),
        _check(
            "package_identity_built",
            "pass" if package["status"] == "built" else "blocker",
            "Adoption decisions must bind to an immutable package digest.",
            [package.get("package_digest") or "package_digest:missing"],
        ),
        _trust_check(package, trust_receipt, trust_error),
    ]


def _adoption_receipt(
    source: str,
    source_kind: str,
    status: str,
    package: dict[str, Any],
    intake: dict[str, Any],
    review: dict[str, Any],
    trust_receipt: dict[str, Any] | None,
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": ADOPTION_DECISION_SCHEMA_VERSION,
        "schema_uri": ADOPTION_DECISION_SCHEMA_URI,
        "status": status,
        "operation": "adoption_decision_preview",
        "source": source,
        "source_kind": source_kind,
        "package_id": package["package_id"],
        "package_digest": package["package_digest"],
        "intake_receipt_status": intake["status"],
        "intake_review_receipt_status": review["status"],
        "trust_receipt_status": trust_receipt.get("status") if trust_receipt else None,
        "trust_decision": trust_receipt.get("decision") if trust_receipt else None,
        "checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": ADOPTION_DECISION_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Adoption decision preview is {status} for {package['package_id']}; "
            "intake, review, package identity, and local trust evidence are evaluated as separate lanes."
        ),
    }


def _build_package_receipt(repo_root: Path, source_path: Path, source: str) -> dict[str, Any]:
    try:
        return build_package_digest_receipt(repo_root, source_path=source_path, query=source)
    except (OSError, ValueError, KeyError) as exc:
        return {
            "status": "blocked",
            "package_id": None,
            "package_digest": None,
            "blocker": f"package_identity_unavailable:{exc}",
        }


def _build_intake_review_receipt(repo_root: Path, source: str, source_kind: str) -> dict[str, Any]:
    try:
        return build_skill_intake_review_receipt(repo_root, source=source, source_kind=source_kind)
    except (OSError, ValueError, KeyError) as exc:
        return {
            "status": "blocked",
            "review_items": [],
            "blocker": f"intake_review_unavailable:{exc}",
        }


def _source_path(repo_root: Path, source: str) -> Path:
    path = Path(source).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return path


def _load_trust_receipt(repo_root: Path, trust_receipt_path: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not trust_receipt_path:
        return None, "trust_receipt_missing"
    path = Path(trust_receipt_path).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(repo_root.resolve()):
        return None, "trust_receipt_outside_repo"
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"trust_receipt_unreadable:{exc}"
    if not isinstance(payload, dict):
        return None, "trust_receipt_not_object"
    return payload, None


def _check(check_id: str, status: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker" if status == "blocker" else "info",
        "message": message,
        "evidence": evidence,
    }


def _trust_check(
    package_receipt: dict[str, Any],
    trust_receipt: dict[str, Any] | None,
    trust_error: str | None,
) -> dict[str, Any]:
    if trust_error:
        return _check(
            "local_trust_decision",
            "blocker",
            "A local trust decision receipt is required before an external skill is adoption-ready.",
            [trust_error],
        )
    assert trust_receipt is not None
    evidence = [
        f"status:{trust_receipt.get('status')}",
        f"decision:{trust_receipt.get('decision')}",
        f"package_digest:{trust_receipt.get('package_digest')}",
        f"expires_at:{trust_receipt.get('expires_at')}",
    ]
    expiry_valid, expiry_reason = _trust_expiry_status(trust_receipt)
    if expiry_reason:
        evidence.append(expiry_reason)
    trusted = (
        trust_receipt.get("schema_version") == "skills-sdk.trust-decision-receipt.v0"
        and trust_receipt.get("status") in {"preview", "recorded"}
        and trust_receipt.get("decision") == "trust"
        and trust_receipt.get("package_digest") == package_receipt["package_digest"]
        and expiry_valid
    )
    return _check(
        "local_trust_decision",
        "pass" if trusted else "blocker",
        "The trust receipt must trust the exact package digest under review and must not be expired.",
        evidence,
    )


def _trust_expiry_status(trust_receipt: dict[str, Any]) -> tuple[bool, str | None]:
    expires_at = trust_receipt.get("expires_at")
    if expires_at is None:
        # Trust receipts require the field, but null intentionally means no expiry.
        return True, None
    if not isinstance(expires_at, str) or not expires_at.strip():
        return False, "expires_at:invalid"
    try:
        expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False, "expires_at:invalid"
    if expires_at_dt.tzinfo is None:
        expires_at_dt = expires_at_dt.replace(tzinfo=UTC)
    if expires_at_dt <= datetime.now(UTC):
        return False, "expires_at:expired"
    return True, None


def _intake_review_completed(review_receipt: dict[str, Any]) -> bool:
    if review_receipt.get("status") != "pass":
        return False
    items = review_receipt.get("review_items")
    if not isinstance(items, list):
        return False
    return not any(isinstance(item, dict) and item.get("status") == "block" for item in items)
