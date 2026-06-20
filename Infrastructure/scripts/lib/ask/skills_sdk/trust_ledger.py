from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TRUST_DECISION_RECEIPT_SCHEMA_VERSION = "skills-sdk.trust-decision-receipt.v0"
TRUST_DECISION_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/trust-decision-receipt.v0.schema.json"
)
TRUST_LEDGER_DEFAULT_PATH = Path(".harness/skills-sdk/trust-ledger.jsonl")
TRUST_DECISION_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "SEC-001", "VP-025"]
TRUST_DECISIONS = frozenset({"trust", "distrust", "revoke"})


class TrustLedgerError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_ledger_path(repo_root: Path, ledger_path: str | None) -> Path:
    candidate = Path(ledger_path) if ledger_path else TRUST_LEDGER_DEFAULT_PATH
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate


def _ledger_path_allowed(repo_root: Path, ledger_path: Path) -> bool:
    resolved = ledger_path.resolve(strict=False)
    allowed_roots = (
        repo_root.resolve(),
        Path(tempfile.gettempdir()).resolve(),
        Path("/private/tmp").resolve(),
        Path("/tmp").resolve(),
    )
    return any(resolved == root or root in resolved.parents for root in allowed_roots)


def _check(check_id: str, status: str, severity: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": evidence or [],
    }


def _public_text(value: str, fallback: str) -> str:
    stripped = value.strip()
    return stripped if stripped else fallback


def _trust_decision_shape_check(
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
) -> dict[str, Any]:
    evidence: list[str] = []
    if decision not in TRUST_DECISIONS:
        evidence.append(f"decision:{decision}")
    if not reason.strip():
        evidence.append("reason:missing")
    if not owner.strip():
        evidence.append("owner:missing")
    if expires_at is not None:
        try:
            datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except ValueError:
            evidence.append(f"expires_at:{expires_at}")
    if decision == "revoke" and not revoked_package_digest:
        evidence.append("revoked_package_digest:missing")
    if revoked_package_digest is not None and not revoked_package_digest.startswith("sha256:"):
        evidence.append(f"revoked_package_digest:{revoked_package_digest}")
    return _check(
        "trust_decision_shape",
        "blocker" if evidence else "pass",
        "blocker",
        "Trust decisions require a known decision, reason, owner, valid expiry, and revocation digest when revoking.",
        evidence,
    )


def _ledger_path_check(repo_root: Path, ledger_path: Path) -> dict[str, Any]:
    return _check(
        "ledger_path_allowed",
        "pass" if _ledger_path_allowed(repo_root, ledger_path) else "blocker",
        "blocker",
        "Trust ledger writes must stay inside the repository or a temporary test path.",
        [_repo_relative(repo_root, ledger_path)],
    )


def _ledger_entry(
    package_receipt: dict[str, Any],
    *,
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
) -> dict[str, Any]:
    recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": TRUST_DECISION_RECEIPT_SCHEMA_VERSION,
        "recorded_at": recorded_at,
        "package_id_digest": _sha256_text(package_receipt["package_id"]),
        "version_digest": _sha256_text(package_receipt["version"]),
        "package_digest_digest": _sha256_text(package_receipt["package_digest"]),
        "decision": decision,
        "reason_digest": _sha256_text(_public_text(reason, "missing reason")),
        "owner_digest": _sha256_text(_public_text(owner, "missing owner")),
        "expires_at_digest": _sha256_text(expires_at) if expires_at is not None else None,
        "revoked_package_digest_digest": _sha256_text(revoked_package_digest)
        if revoked_package_digest is not None
        else None,
    }


def _receipt_base(status: str, decision: str, reason: str, owner: str) -> dict[str, Any]:
    return {
        "schema_version": TRUST_DECISION_RECEIPT_SCHEMA_VERSION,
        "schema_uri": TRUST_DECISION_RECEIPT_SCHEMA_URI,
        "status": status,
        "operation": "trust_decision",
        "decision": decision if decision in TRUST_DECISIONS else "distrust",
        "reason": _public_text(reason, "missing reason"),
        "owner": _public_text(owner, "missing owner"),
    }


def _receipt_package(package_receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_id": package_receipt["package_id"],
        "version": package_receipt["version"],
        "source_digest": package_receipt["source_digest"],
        "manifest_digest": package_receipt["manifest_digest"],
        "package_digest": package_receipt["package_digest"],
    }


def _receipt_ledger(
    repo_root: Path,
    ledger_path: Path,
    ledger_before_digest: str | None,
    ledger_after_digest: str | None,
    ledger_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "ledger_path": _repo_relative(repo_root, ledger_path),
        "ledger_before_digest": ledger_before_digest,
        "ledger_after_digest": ledger_after_digest,
        "ledger_entry": ledger_entry,
        "ledger_entry_digest": _sha256_json(ledger_entry) if ledger_entry else None,
    }


def _receipt(
    repo_root: Path,
    package_receipt: dict[str, Any],
    *,
    status: str,
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
    ledger_path: Path,
    ledger_before_digest: str | None,
    ledger_after_digest: str | None,
    ledger_entry: dict[str, Any] | None,
    trust_checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    mutation_performed: bool,
) -> dict[str, Any]:
    return {
        **_receipt_base(status, decision, reason, owner),
        "expires_at": expires_at,
        "revoked_package_digest": revoked_package_digest,
        **_receipt_package(package_receipt),
        **_receipt_ledger(repo_root, ledger_path, ledger_before_digest, ledger_after_digest, ledger_entry),
        "trust_checks": trust_checks,
        "blockers": blockers,
        "warnings": [],
        "mutation_performed": mutation_performed,
        "trust_store_mutated": False,
        "acceptance_trace": TRUST_DECISION_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"skills-sdk trust decision {status} for {package_receipt['package_id']} "
            "using a local append-only ledger; no global trust store was mutated."
        ),
    }


def _trust_checks(
    repo_root: Path,
    ledger: Path,
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
) -> list[dict[str, Any]]:
    return [
        _trust_decision_shape_check(decision, reason, owner, expires_at, revoked_package_digest),
        _ledger_path_check(repo_root, ledger),
    ]


def _write_entry_if_apply(ledger: Path, entry: dict[str, Any], *, apply: bool) -> tuple[str, bool, str | None]:
    if not apply:
        return "preview", False, _sha256_file(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
    return "recorded", True, _sha256_file(ledger)


def _blocked_receipt(
    repo_root: Path,
    package_receipt: dict[str, Any],
    *,
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
    ledger: Path,
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    before_digest: str | None,
) -> dict[str, Any]:
    return _receipt(
        repo_root,
        package_receipt,
        status="blocked",
        decision=decision,
        reason=reason,
        owner=owner,
        expires_at=expires_at,
        revoked_package_digest=revoked_package_digest,
        ledger_path=ledger,
        ledger_before_digest=before_digest,
        ledger_after_digest=before_digest,
        ledger_entry=None,
        trust_checks=checks,
        blockers=blockers,
        mutation_performed=False,
    )


def _success_receipt(
    repo_root: Path,
    package_receipt: dict[str, Any],
    *,
    decision: str,
    reason: str,
    owner: str,
    expires_at: str | None,
    revoked_package_digest: str | None,
    apply: bool,
    ledger: Path,
    checks: list[dict[str, Any]],
    before_digest: str | None,
) -> dict[str, Any]:
    entry = _ledger_entry(
        package_receipt,
        decision=decision,
        reason=reason,
        owner=owner,
        expires_at=expires_at,
        revoked_package_digest=revoked_package_digest,
    )
    status, mutation_performed, after_digest = _write_entry_if_apply(ledger, entry, apply=apply)
    return _receipt(
        repo_root,
        package_receipt,
        status=status,
        decision=decision,
        reason=reason,
        owner=owner,
        expires_at=expires_at,
        revoked_package_digest=revoked_package_digest,
        ledger_path=ledger,
        ledger_before_digest=before_digest,
        ledger_after_digest=after_digest,
        ledger_entry=entry,
        trust_checks=checks,
        blockers=[],
        mutation_performed=mutation_performed,
    )


def build_trust_decision_receipt(
    repo_root: Path, *, package_receipt: dict[str, Any], decision: str, reason: str, owner: str, apply: bool,
    ledger_path: str | None = None, expires_at: str | None = None, revoked_package_digest: str | None = None,
) -> dict[str, Any]:
    ledger = _resolve_ledger_path(repo_root, ledger_path)
    checks = _trust_checks(repo_root, ledger, decision, reason, owner, expires_at, revoked_package_digest)
    blockers = [check for check in checks if check["status"] == "blocker"]
    before_digest = _sha256_file(ledger)
    if blockers:
        receipt = _blocked_receipt(
            repo_root,
            package_receipt,
            decision=decision,
            reason=reason,
            owner=owner,
            expires_at=expires_at,
            revoked_package_digest=revoked_package_digest,
            ledger=ledger,
            checks=checks,
            blockers=blockers,
            before_digest=before_digest,
        )
        raise TrustLedgerError(receipt)

    return _success_receipt(
        repo_root,
        package_receipt,
        decision=decision,
        reason=reason,
        owner=owner,
        expires_at=expires_at,
        revoked_package_digest=revoked_package_digest,
        apply=apply,
        ledger=ledger,
        checks=checks,
        before_digest=before_digest,
    )
