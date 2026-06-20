from __future__ import annotations

from typing import Any


CI_POLICY_PREVIEW_SCHEMA_VERSION = "skills-sdk.ci-policy-preview-receipt.v0"
CI_POLICY_PREVIEW_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/ci-policy-preview-receipt.v0.schema.json"
)
CI_POLICY_ACCEPTANCE_TRACE = ["PU-028", "FR-008", "SA-004", "VP-028"]
RISK_TIERS = ("low", "medium", "high", "privileged", "published")

BASE_REQUIRED_CHECKS = (
    "lint",
    "test",
    "typecheck",
    "docs-test",
    "security-scan",
    "pr-template",
)
RISK_CHECKS = {
    "low": (),
    "medium": ("risk-policy-gate",),
    "high": ("risk-policy-gate", "Semgrep (SAST)", "Trivy (dependency CVE scan)"),
    "privileged": (
        "risk-policy-gate",
        "Semgrep (SAST)",
        "Trivy (dependency CVE scan)",
        "Gitleaks (secrets scan)",
        "Artifact secrets pre-check",
    ),
    "published": (
        "risk-policy-gate",
        "Semgrep (SAST)",
        "Trivy (dependency CVE scan)",
        "Gitleaks (secrets scan)",
        "Artifact secrets pre-check",
        "dependency-review",
        "actions-pinning",
    ),
}


class CiPolicyPreviewError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker",
        "message": message,
        "evidence": evidence or [],
    }


def _required_checks(risk_tier: str) -> list[dict[str, Any]]:
    names = [*BASE_REQUIRED_CHECKS, *RISK_CHECKS.get(risk_tier, ())]
    return [
        {
            "name": name,
            "required": True,
            "source": "base" if name in BASE_REQUIRED_CHECKS else "risk_tier",
        }
        for name in dict.fromkeys(names)
    ]


def build_ci_policy_preview_receipt(*, risk_tier: str) -> dict[str, Any]:
    normalized_tier = risk_tier.strip().lower()
    checks = [
        _check(
            "risk_tier_supported",
            "pass" if normalized_tier in RISK_TIERS else "blocker",
            "CI policy preview requires a known SDK risk tier.",
            [risk_tier],
        )
    ]
    blockers = [check for check in checks if check["status"] == "blocker"]
    receipt = {
        "schema_version": CI_POLICY_PREVIEW_SCHEMA_VERSION,
        "schema_uri": CI_POLICY_PREVIEW_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "ci_policy_preview",
        "risk_tier": normalized_tier,
        "required_checks": [] if blockers else _required_checks(normalized_tier),
        "policy_checks": checks,
        "blockers": blockers,
        "live_ci_evidence_attached": False,
        "branch_protection_mutated": False,
        "mutation_performed": False,
        "acceptance_trace": CI_POLICY_ACCEPTANCE_TRACE,
        "agent_summary": (
            "CI policy preview is blocked by contract validation."
            if blockers
            else f"CI policy preview selected {len(_required_checks(normalized_tier))} required check(s) for {normalized_tier} risk."
        ),
    }
    if blockers:
        raise CiPolicyPreviewError(receipt)
    return receipt
