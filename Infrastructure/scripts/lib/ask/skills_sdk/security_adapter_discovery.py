from __future__ import annotations

from pathlib import Path
from typing import Any


SECURITY_ADAPTER_DISCOVERY_SCHEMA_VERSION = "skills-sdk.security-adapter-discovery-receipt.v0"
SECURITY_ADAPTER_DISCOVERY_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/security-adapter-discovery-receipt.v0.schema.json"
)
SECURITY_ADAPTER_ACCEPTANCE_TRACE = ["PU-031", "FR-008", "SA-004", "SEC-001", "VP-031"]

ADAPTER_SPECS = (
    {
        "adapter_id": "semgrep",
        "display_name": "Semgrep",
        "adapter_kind": "sast",
        "source_paths": (
            ".github/workflows/security-scan.yml",
            ".github/workflows/secret-scan.yml",
            ".github/workflows/semgrep.yml",
        ),
        "tokens": ("semgrep", "returntocorp/semgrep-action"),
        "requires_credentials": False,
    },
    {
        "adapter_id": "trivy",
        "display_name": "Trivy",
        "adapter_kind": "dependency_vulnerability",
        "source_paths": (
            ".github/workflows/security-scan.yml",
            ".github/workflows/secret-scan.yml",
        ),
        "tokens": ("trivy", "aquasecurity/trivy-action"),
        "requires_credentials": False,
    },
    {
        "adapter_id": "gitleaks",
        "display_name": "Gitleaks",
        "adapter_kind": "secret_detection",
        "source_paths": (
            ".github/workflows/security-scan.yml",
            ".github/workflows/secret-scan.yml",
            ".github/scripts/gov_security_gates.py",
            ".gitleaks.toml",
        ),
        "tokens": ("gitleaks",),
        "requires_credentials": False,
    },
    {
        "adapter_id": "codeql",
        "display_name": "CodeQL",
        "adapter_kind": "code_scanning",
        "source_paths": (".github/workflows/codeql.yml",),
        "tokens": ("codeql", "github/codeql-action"),
        "requires_credentials": False,
    },
    {
        "adapter_id": "dependency-review",
        "display_name": "Dependency Review",
        "adapter_kind": "dependency_review",
        "source_paths": (".github/workflows/pr-pipeline.yml",),
        "tokens": ("dependency-review-action", "dependency-review"),
        "requires_credentials": False,
    },
)


class SecurityAdapterDiscoveryError(ValueError):
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


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _source_contains(path: Path, tokens: tuple[str, ...]) -> bool:
    try:
        content = path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return False
    return any(token.lower() in content for token in tokens)


def _discover_adapter(repo_root: Path, spec: dict[str, Any]) -> dict[str, Any] | None:
    evidence_refs: list[str] = []
    for source_path in spec["source_paths"]:
        path = repo_root / source_path
        if path.is_file() and _source_contains(path, spec["tokens"]):
            evidence_refs.append(source_path)
    if not evidence_refs:
        return None
    return {
        "adapter_id": spec["adapter_id"],
        "display_name": spec["display_name"],
        "adapter_kind": spec["adapter_kind"],
        "source": "repo_configuration",
        "configured": True,
        "evidence_refs": evidence_refs,
        "requires_credentials": spec["requires_credentials"],
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
    }


def _discover_adapters(repo_root: Path, repo_available: bool) -> list[dict[str, Any]]:
    if not repo_available:
        return []
    candidates = [_discover_adapter(repo_root, spec) for spec in ADAPTER_SPECS]
    return [candidate for candidate in candidates if candidate is not None]


def _discovery_checks(
    repo_root: Path,
    repo_available: bool,
    adapter_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        _check(
            "repo_root_available",
            "pass" if repo_available else "blocker",
            "Security adapter discovery requires a readable repository root.",
            [_repo_relative(repo_root, repo_root)],
        ),
        _check(
            "local_security_sources_discovered",
            "pass" if adapter_candidates else "blocker",
            "At least one local security adapter configuration must be present before scanner execution is considered.",
            [candidate["adapter_id"] for candidate in adapter_candidates],
        ),
    ]


def _agent_summary(blockers: list[dict[str, Any]], adapter_count: int) -> str:
    if blockers:
        return "security adapter discovery is blocked by local source validation."
    return (
        f"security adapter discovery found {adapter_count} local configured adapter(s) "
        "without executing scanners."
    )


def _build_receipt(
    adapter_candidates: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    adapter_count = len(adapter_candidates)
    return {
        "schema_version": SECURITY_ADAPTER_DISCOVERY_SCHEMA_VERSION,
        "schema_uri": SECURITY_ADAPTER_DISCOVERY_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "security_adapter_discovery_preview",
        "adapter_count": adapter_count,
        "adapter_candidates": [] if blockers else adapter_candidates,
        "discovery_checks": checks,
        "blockers": blockers,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SECURITY_ADAPTER_ACCEPTANCE_TRACE,
        "agent_summary": _agent_summary(blockers, adapter_count),
    }


def build_security_adapter_discovery_receipt(repo_root: Path) -> dict[str, Any]:
    repo_available = repo_root.exists() and repo_root.is_dir()
    adapter_candidates = _discover_adapters(repo_root, repo_available)
    checks = _discovery_checks(repo_root, repo_available, adapter_candidates)
    blockers = [check for check in checks if check["status"] == "blocker"]
    receipt = _build_receipt(adapter_candidates, checks, blockers)
    if blockers:
        raise SecurityAdapterDiscoveryError(receipt)
    return receipt
