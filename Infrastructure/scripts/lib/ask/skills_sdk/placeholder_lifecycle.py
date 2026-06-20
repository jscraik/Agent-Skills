from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PLACEHOLDER_LIFECYCLE_SCHEMA_VERSION = "skills-sdk.placeholder-lifecycle.v1"
PLACEHOLDER_LIFECYCLE_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/placeholder-lifecycle.v1.schema.json"
)
PLACEHOLDER_LIFECYCLE_ACCEPTANCE_TRACE = (
    "FR-012",
    "FR-013",
    "FR-014",
    "FR-015",
    "FR-016",
    "FR-017",
    "FR-018",
    "FR-019",
    "FR-020",
    "FR-021",
    "FR-022",
    "FR-023",
    "SEC-001",
    "SEC-002",
    "SEC-003",
    "SEC-004",
    "SEC-005",
    "SEC-006",
    "SEC-007",
    "SEC-008",
    "SEC-009",
    "SEC-010",
    "SEC-011",
    "SA-007",
    "SA-008",
    "SA-009",
    "SA-010",
    "SA-011",
    "SA-017",
    "SA-018",
    "SA-019",
    "SA-022",
    "VP-006",
    "VP-007",
    "VP-008",
    "VP-009",
    "VP-010",
    "VP-012",
    "VP-013",
    "VP-014",
    "VP-015",
    "VP-016",
    "VP-017",
    "VP-018",
)

SURFACES = ("refs", "evals", "signing", "security_adapter", "explorer")
RISK_TIERS = ("low", "medium", "high", "privileged", "published")
BLOCKING_RISK_TIERS = {"high", "privileged", "published"}
PUBLISHED_RISK_TIERS = {"published"}


@dataclass(frozen=True)
class PlaceholderSurfaceContract:
    surface: str
    lifecycle_stage: str
    optional_reason: str
    blocked_reason: str
    required_risk_tiers: frozenset[str]


SURFACE_CONTRACTS = {
    "refs": PlaceholderSurfaceContract(
        surface="refs",
        lifecycle_stage="reference_ingestion",
        optional_reason="Reference ingestion is reserved for a later Skills SDK milestone and was not attempted in V1.0.",
        blocked_reason="Reference ingestion is required by the selected risk tier but no refs adapter is implemented in V1.0.",
        required_risk_tiers=frozenset(),
    ),
    "evals": PlaceholderSurfaceContract(
        surface="evals",
        lifecycle_stage="evaluation",
        optional_reason="Eval execution is reserved for a later Skills SDK milestone and no external eval service was invoked.",
        blocked_reason="Eval execution is required by the selected risk tier but no eval runner is implemented in V1.0.",
        required_risk_tiers=frozenset({"published"}),
    ),
    "signing": PlaceholderSurfaceContract(
        surface="signing",
        lifecycle_stage="package_signing",
        optional_reason="Package signing is reserved for a later Skills SDK milestone and no key material was accessed.",
        blocked_reason="Package signing is required by the selected risk tier but no signing adapter is implemented in V1.0.",
        required_risk_tiers=frozenset(PUBLISHED_RISK_TIERS),
    ),
    "security_adapter": PlaceholderSurfaceContract(
        surface="security_adapter",
        lifecycle_stage="security_adapter_detection",
        optional_reason="Security adapter detection is optional for this risk tier and no live scanner credentials were used.",
        blocked_reason="Security adapter detection is required by the selected risk tier but no configured adapter is available in V1.0.",
        required_risk_tiers=frozenset(BLOCKING_RISK_TIERS),
    ),
    "explorer": PlaceholderSurfaceContract(
        surface="explorer",
        lifecycle_stage="static_docs_explorer",
        optional_reason="Hosted explorer publishing is out of scope for V1.0; static docs contracts remain local only.",
        blocked_reason="Hosted explorer output is required by the selected risk tier but publishing is not implemented in V1.0.",
        required_risk_tiers=frozenset(),
    ),
}


def _receipt_ref(surface: str) -> str:
    return f".harness/receipts/skills-sdk/placeholders/{surface}.json"


def build_placeholder_lifecycle_receipt(surface: str, risk_tier: str) -> dict[str, Any]:
    """Return one honest placeholder lifecycle receipt without running adapters."""
    normalized_surface = surface.strip()
    normalized_risk_tier = risk_tier.strip()
    if normalized_surface not in SURFACE_CONTRACTS:
        raise ValueError(f"unknown placeholder lifecycle surface: {surface}")
    if normalized_risk_tier not in RISK_TIERS:
        raise ValueError(f"unknown Skills SDK risk tier: {risk_tier}")

    contract = SURFACE_CONTRACTS[normalized_surface]
    required = normalized_risk_tier in contract.required_risk_tiers
    if required:
        status = "blocked"
        adapter_state = "missing"
        reason = contract.blocked_reason
    else:
        status = "skipped_optional" if normalized_surface in {"refs", "evals", "security_adapter", "explorer"} else "not_run"
        adapter_state = "optional" if status == "skipped_optional" else "blocked"
        reason = contract.optional_reason

    return {
        "schema_version": PLACEHOLDER_LIFECYCLE_SCHEMA_VERSION,
        "schema_uri": PLACEHOLDER_LIFECYCLE_SCHEMA_URI,
        "surface": normalized_surface,
        "lifecycle_stage": contract.lifecycle_stage,
        "status": status,
        "adapter_state": adapter_state,
        "reason": reason,
        "feature_executed": False,
        "required_for_risk_tier": required,
        "receipt_ref": _receipt_ref(normalized_surface),
        "acceptance_trace": PLACEHOLDER_LIFECYCLE_ACCEPTANCE_TRACE,
    }


def build_placeholder_lifecycle_receipts(
    *,
    risk_tier: str = "medium",
    surface: str | None = None,
) -> dict[str, Any]:
    """Return schema-shaped placeholder receipts for the selected lifecycle surface(s)."""
    normalized_risk_tier = risk_tier.strip()
    if normalized_risk_tier not in RISK_TIERS:
        raise ValueError(f"unknown Skills SDK risk tier: {risk_tier}")
    selected_surfaces = [surface] if surface else list(SURFACES)
    receipts = [
        build_placeholder_lifecycle_receipt(selected_surface, normalized_risk_tier)
        for selected_surface in selected_surfaces
    ]
    blocked_surfaces = [
        receipt["surface"]
        for receipt in receipts
        if receipt["status"] == "blocked" and receipt["required_for_risk_tier"]
    ]
    status = "blocked" if blocked_surfaces else "placeholder"
    return {
        "schema_version": "skills-sdk-placeholder-lifecycle-set.v1",
        "status": status,
        "risk_tier": normalized_risk_tier,
        "surfaces": [receipt["surface"] for receipt in receipts],
        "blocked_surfaces": blocked_surfaces,
        "receipts": receipts,
        "feature_executed": False,
        "mutation_performed": False,
        "agent_summary": (
            f"Skills SDK lifecycle placeholders are blocked for {', '.join(blocked_surfaces)} at {normalized_risk_tier} risk."
            if blocked_surfaces
            else f"Skills SDK lifecycle placeholders reported {len(receipts)} unimplemented surface(s) without execution."
        ),
    }
