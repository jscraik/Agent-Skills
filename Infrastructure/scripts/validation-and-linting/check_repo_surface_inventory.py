#!/usr/bin/env python3
"""Classify tracked repository paths by repo surface ownership policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ALLOWLIST = Path("Infrastructure") / "policy" / "repo_surface_allowlist.json"

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class AllowlistEntry:
    id: str
    match_type: str
    pattern: str
    classification: str
    reason: str
    owner: str
    review_after: str | None = None
    expires: str | None = None


@dataclass(frozen=True)
class SurfaceFinding:
    path: str
    classification: str
    status: str
    code: str
    severity: str
    blocking: bool
    allowlist_entry: str | None
    reason: str
    recommendation: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _normalize_path(path: str | Path) -> str:
    normalized = Path(str(path).strip()).as_posix()
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def _path_parts(path: str) -> tuple[str, ...]:
    return tuple(part for part in Path(path).parts if part not in ("", "."))


def _starts_with(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")


def _matches_plugin_subpath(path: str, subpath: str) -> bool:
    parts = _path_parts(path)
    return len(parts) >= 3 and parts[0] == "Plugins" and parts[2] == subpath


def _is_root_doc(path: str) -> bool:
    return "/" not in path and path.endswith((".md", ".txt"))


def _is_root_config(path: str) -> bool:
    if "/" in path:
        return False
    names = {
        ".architecture.yml",
        ".coderabbit.yaml",
        ".diagramrc",
        ".gitignore",
        ".gitleaks.toml",
        ".markdownlint.yaml",
        ".memory-metrics.json",
        ".mise.toml",
        ".npmrc",
        ".pylintrc",
        ".qdrant-initialized",
        ".semgrepignore",
        ".vale.ini",
        "biome.json",
        "docs-policy.json",
        "harness.contract.json",
        "justfile",
        "Makefile",
        "memory.json",
        "package-lock.json",
        "prek.toml",
    }
    return path in names


def _make_finding(
    path: str,
    *,
    classification: str,
    status: str,
    code: str,
    severity: str,
    blocking: bool,
    reason: str,
    recommendation: str,
    allowlist_entry: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SurfaceFinding:
    metadata = _normalize_metadata(metadata or {})
    return SurfaceFinding(
        path=path,
        classification=classification,
        status=status,
        code=code,
        severity=severity,
        blocking=blocking,
        allowlist_entry=allowlist_entry,
        reason=reason,
        recommendation=recommendation,
        metadata=metadata,
    )


def _next_step(step_type: str, command: str, rationale: str) -> dict[str, str]:
    return {
        "type": step_type,
        "command": command,
        "rationale": rationale,
    }


def _step_from_token(token: str) -> dict[str, str]:
    return _next_step(
        "manual",
        token,
        f"Complete the {token.replace('_', ' ')} step before changing tracked content.",
    )


def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    next_steps = metadata.get("next_steps")
    if isinstance(next_steps, list) and all(isinstance(step, str) for step in next_steps):
        metadata = {
            **metadata,
            "next_steps": [_step_from_token(step) for step in next_steps],
        }
    return metadata


def classify_path(path: str | Path) -> SurfaceFinding:
    normalized = _normalize_path(path)
    suffix = Path(normalized).suffix.lower()

    if _starts_with(normalized, "Infrastructure/Infrastructure"):
        return _make_finding(
            normalized,
            classification="unknown",
            status="violation",
            code="duplicated_infrastructure_path",
            severity="error",
            blocking=True,
            reason="Duplicated Infrastructure/Infrastructure path shape is suspicious.",
            recommendation="Reference-scan and either delete generated debris or add a documented allowlist entry.",
            metadata={"next_steps": ["scan_references", "decide_owner_or_cleanup"]},
        )

    if _starts_with(normalized, "Plugins/cache"):
        return _make_finding(
            normalized,
            classification="generated_ignored",
            status="violation",
            code="tracked_plugin_cache",
            severity="error",
            blocking=True,
            reason="Plugin cache content is generated runtime state and should not be newly tracked.",
            recommendation="Remove from git after verifying no fixture or vendored snapshot contract applies.",
            metadata={"next_steps": ["verify_no_fixture_consumer", "remove_from_tracked_surface"]},
        )

    if _starts_with(normalized, ".skill-telemetry"):
        return _make_finding(
            normalized,
            classification="runtime_state",
            status="violation",
            code="tracked_runtime_state",
            severity="error",
            blocking=True,
            reason="Skill telemetry is local runtime output.",
            recommendation="Keep telemetry untracked unless converted into a documented fixture.",
            metadata={"next_steps": ["verify_fixture_role", "remove_or_relocate"]},
        )

    if normalized.startswith(".harness/") and suffix == ".db":
        return _make_finding(
            normalized,
            classification="runtime_state",
            status="violation",
            code="tracked_runtime_database",
            severity="error",
            blocking=True,
            reason="Harness database files are runtime state by default.",
            recommendation="Move under fixtures with a documented consumer or remove from tracked source.",
            metadata={"next_steps": ["prove_fixture_consumer", "document_or_untrack"]},
        )

    if _starts_with(normalized, ".skillsets"):
        return _make_finding(
            normalized,
            classification="unknown",
            status="unknown",
            code="ownership_decision_required",
            severity="error",
            blocking=True,
            reason=".skillsets ownership is explicitly unresolved by policy.",
            recommendation="Decide whether this is generated output, a fixture subset, or canonical source.",
            metadata={"next_steps": ["identify_generator", "document_owner"]},
        )

    if _starts_with(normalized, "skills-system"):
        return _make_finding(
            normalized,
            classification="unknown",
            status="unknown",
            code="ownership_decision_required",
            severity="error",
            blocking=True,
            reason="skills-system ownership is explicitly unresolved by policy.",
            recommendation="Document vendoring/update command, active runtime reader, or cleanup evidence.",
            metadata={"next_steps": ["identify_reader_or_update_command", "document_owner"]},
        )

    if _starts_with(normalized, "Infrastructure/tmp") or _starts_with(normalized, "Infrastructure/todos"):
        return _make_finding(
            normalized,
            classification="historical_artifact",
            status="violation",
            code="tracked_generated_work_area",
            severity="error",
            blocking=True,
            reason="Temporary and backlog work areas are not canonical source surfaces by default.",
            recommendation="Reference-scan and retain only documented fixtures, indexes, or source migrations.",
            metadata={"next_steps": ["reference_scan", "decide_fixture_or_cleanup"]},
        )

    if _starts_with(normalized, "Infrastructure/artifacts") or _starts_with(normalized, "artifacts"):
        return _make_finding(
            normalized,
            classification="historical_artifact",
            status="violation",
            code="tracked_historical_artifact",
            severity="error",
            blocking=True,
            reason="Generated evidence and run artifacts are ignored by default.",
            recommendation="Keep only allowlisted fixtures, summaries, indexes, or intentional archives.",
            metadata={"next_steps": ["reference_scan", "retain_fixture_or_archive_reason"]},
        )

    if suffix in {".jsonl", ".log"}:
        return _make_finding(
            normalized,
            classification="historical_artifact",
            status="warning",
            code="generated_evidence_pattern",
            severity="warning",
            blocking=False,
            reason="JSONL and log files often represent generated evidence.",
            recommendation="Confirm this file is a fixture or move it to generated output.",
            metadata={"next_steps": ["confirm_fixture_or_generated_output"]},
        )

    if _starts_with(normalized, ".agents/skills"):
        return _make_finding(
            normalized,
            classification="generated_tracked",
            status="ok",
            code="generated_command_handle",
            severity="info",
            blocking=False,
            reason="Generated command handles are tracked compatibility surfaces.",
            recommendation="Regenerate through sync rather than hand-editing.",
            metadata={"next_steps": ["validate_projection_if_changed"]},
        )

    if _matches_plugin_subpath(normalized, "fixtures"):
        return _make_finding(
            normalized,
            classification="fixture",
            status="ok",
            code="plugin_fixture_surface",
            severity="info",
            blocking=False,
            reason="Path is a plugin-owned fixture or archived budget fixture with an explicit consumer.",
            recommendation="Track only when tests, packaging, or preservation indexes reference it.",
            metadata={"next_steps": ["keep_consumer_documented"]},
        )

    if _matches_plugin_subpath(normalized, "references"):
        return _make_finding(
            normalized,
            classification="reference",
            status="ok",
            code="plugin_reference_surface",
            severity="info",
            blocking=False,
            reason="Path is plugin-owned reference context loaded through progressive disclosure.",
            recommendation="Keep indexed from the owning plugin front door.",
            metadata={"next_steps": ["preserve_index_link_if_changed"]},
        )

    if (
        _starts_with(normalized, "Skills")
        or _matches_plugin_subpath(normalized, "skills")
        or _starts_with(normalized, "Infrastructure/scripts")
        or _starts_with(normalized, "Infrastructure/bin")
        or _starts_with(normalized, "Infrastructure/tests")
        or _starts_with(normalized, "bin")
        or _starts_with(normalized, "scripts")
        or _starts_with(normalized, "utilities")
        or _starts_with(normalized, "brand")
    ):
        return _make_finding(
            normalized,
            classification="source",
            status="ok",
            code="source_path",
            severity="info",
            blocking=False,
            reason="Path is authored source or test/tooling source.",
            recommendation="Track and edit through the canonical source path.",
            metadata={"next_steps": ["run_focused_validation_if_changed"]},
        )

    if _matches_plugin_subpath(normalized, ".codex-plugin"):
        return _make_finding(
            normalized,
            classification="source",
            status="ok",
            code="plugin_metadata_source",
            severity="info",
            blocking=False,
            reason="Plugin package metadata is tracked source/policy.",
            recommendation="Track with plugin package validation.",
            metadata={"next_steps": ["run_plugin_validation_if_changed"]},
        )

    if (
        _starts_with(normalized, "Infrastructure/references")
        or _starts_with(normalized, "Wiki")
        or _starts_with(normalized, ".harness/knowledge")
        or _starts_with(normalized, ".harness/decisions")
        or _starts_with(normalized, ".harness/memory")
    ):
        return _make_finding(
            normalized,
            classification="reference",
            status="ok",
            code="indexed_reference_surface",
            severity="info",
            blocking=False,
            reason="Path is supporting context loaded through progressive disclosure.",
            recommendation="Keep indexed and intentionally reachable.",
            metadata={"next_steps": ["preserve_index_link_if_changed"]},
        )

    if (
        _starts_with(normalized, "Docs")
        or _starts_with(normalized, ".github")
        or _starts_with(normalized, ".agents/workflows")
        or _starts_with(normalized, ".circleci")
        or _starts_with(normalized, ".codex")
        or _starts_with(normalized, ".diagram")
        or _starts_with(normalized, ".vale")
        or _starts_with(normalized, "Infrastructure/COMPLIANCE")
        or _starts_with(normalized, "Infrastructure/EVALUATION")
        or _starts_with(normalized, "Infrastructure/GOVERNANCE")
        or _starts_with(normalized, "Infrastructure/SECURITY")
        or _starts_with(normalized, "Infrastructure/config")
        or _starts_with(normalized, "Infrastructure/catalog")
        or _starts_with(normalized, "Infrastructure/policy")
        or normalized in {
            ".agents/PLANS.md",
            ".harness/ci-provider-transition-status.json",
            ".harness/ci-required-checks.json",
            ".harness/restore-manifest.json",
            ".harness/upgrade-manifest.json",
            "CODEOWNERS",
            "GOVERNANCE",
            "Infrastructure/docs-policy.json",
            "Infrastructure/Makefile",
            "Infrastructure/memory.json",
            "Infrastructure/prek.toml",
            "LICENSE",
        }
        or _is_root_config(normalized)
    ):
        return _make_finding(
            normalized,
            classification="policy",
            status="ok",
            code="policy_surface",
            severity="info",
            blocking=False,
            reason="Path is governance, routing, configuration, or validation policy.",
            recommendation="Track and keep linked from the relevant front door.",
            metadata={"next_steps": ["run_policy_validation_if_changed"]},
        )

    if (
        _starts_with(normalized, ".workouts")
        or _starts_with(normalized, "Infrastructure/templates")
        or _starts_with(normalized, "Infrastructure/vendor")
    ):
        return _make_finding(
            normalized,
            classification="fixture",
            status="ok",
            code="fixture_or_template_surface",
            severity="info",
            blocking=False,
            reason="Path is a stable fixture, template, or vendored support input.",
            recommendation="Track only with a clear consumer and reason.",
            metadata={"next_steps": ["keep_consumer_documented"]},
        )

    if (
        _starts_with(normalized, "Plugins")
        or _starts_with(normalized, "Infrastructure/factory")
        or _starts_with(normalized, "Infrastructure/ops")
        or _starts_with(normalized, "Infrastructure/reports")
        or _starts_with(normalized, "Infrastructure/storage")
        or _starts_with(normalized, ".harness/ci-migrate-snapshots")
        or _starts_with(normalized, ".harness/quality")
        or _is_root_doc(normalized)
        or normalized in {".move-docs.sh", ".move.sh"}
    ):
        return _make_finding(
            normalized,
            classification="source",
            status="ok",
            code="authored_source_surface",
            severity="info",
            blocking=False,
            reason="Path is authored repository source.",
            recommendation="Track and validate through the owning workflow.",
            metadata={"next_steps": ["run_owner_validation_if_changed"]},
        )

    return _make_finding(
        normalized,
        classification="unknown",
        status="unknown",
        code="unknown_surface",
        severity="error",
        blocking=True,
        reason="No repo surface ownership rule matched this tracked path.",
        recommendation="Classify the path in policy or add a documented allowlist entry.",
        metadata={"next_steps": ["inspect_owner", "update_policy_or_allowlist"]},
    )


def load_allowlist(path: Path) -> list[AllowlistEntry]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"{path}: entries must be a list")

    parsed: list[AllowlistEntry] = []
    for raw in entries:
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: each entry must be an object")
        missing = [
            key
            for key in ("id", "match_type", "pattern", "classification", "reason", "owner")
            if not raw.get(key)
        ]
        if missing:
            raise ValueError(f"{path}: allowlist entry missing required keys: {', '.join(missing)}")
        if raw["match_type"] not in {"exact", "prefix", "glob"}:
            raise ValueError(f"{path}: invalid match_type for {raw['id']}")
        if not raw.get("review_after") and not raw.get("expires"):
            raise ValueError(f"{path}: allowlist entry {raw['id']} needs review_after or expires")
        parsed.append(
            AllowlistEntry(
                id=str(raw["id"]),
                match_type=str(raw["match_type"]),
                pattern=_normalize_path(str(raw["pattern"])),
                classification=str(raw["classification"]),
                reason=str(raw["reason"]),
                owner=str(raw["owner"]),
                review_after=raw.get("review_after"),
                expires=raw.get("expires"),
            )
        )
    return parsed


def _allowlist_score(entry: AllowlistEntry) -> tuple[int, int, str]:
    match_rank = {"exact": 0, "prefix": 1, "glob": 2}[entry.match_type]
    return (match_rank, -len(entry.pattern), entry.id)


def _entry_matches(entry: AllowlistEntry, finding: SurfaceFinding) -> bool:
    if entry.classification != finding.classification:
        return False
    if entry.match_type == "exact":
        return finding.path == entry.pattern
    if entry.match_type == "prefix":
        return _starts_with(finding.path, entry.pattern)
    return fnmatch.fnmatchcase(finding.path, entry.pattern)


def matching_allowlist_entry(
    finding: SurfaceFinding, allowlist_entries: list[AllowlistEntry]
) -> AllowlistEntry | None:
    matches = [entry for entry in allowlist_entries if _entry_matches(entry, finding)]
    if not matches:
        return None
    return sorted(matches, key=_allowlist_score)[0]


def apply_allowlist(
    finding: SurfaceFinding, allowlist_entries: list[AllowlistEntry]
) -> SurfaceFinding:
    entry = matching_allowlist_entry(finding, allowlist_entries)
    if entry is None or finding.status == "ok":
        return finding

    return _make_finding(
        finding.path,
        classification=finding.classification,
        status="warning",
        code=finding.code,
        severity="warning",
        blocking=False,
        allowlist_entry=entry.id,
        reason=f"{finding.reason} Allowlisted: {entry.reason}",
        recommendation=f"Review allowlist entry {entry.id} by {entry.review_after or entry.expires}.",
        metadata={**finding.metadata, "allowlist_owner": entry.owner},
    )


def classify_paths(
    paths: list[str | Path],
    allowlist_entries: list[AllowlistEntry] | None = None,
) -> list[SurfaceFinding]:
    allowlist_entries = allowlist_entries or []
    findings = [apply_allowlist(classify_path(path), allowlist_entries) for path in paths]
    return sorted(
        findings,
        key=lambda finding: (
            -int(finding.blocking),
            SEVERITY_ORDER[finding.severity],
            finding.path,
            finding.code,
        ),
    )


def git_ls_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_report(findings: list[SurfaceFinding], *, strict: bool) -> dict[str, Any]:
    counts_by_classification: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}
    counts_by_code: dict[str, int] = {}
    for finding in findings:
        counts_by_classification[finding.classification] = counts_by_classification.get(finding.classification, 0) + 1
        counts_by_status[finding.status] = counts_by_status.get(finding.status, 0) + 1
        counts_by_code[finding.code] = counts_by_code.get(finding.code, 0) + 1

    blocking_count = sum(1 for finding in findings if finding.blocking)
    status = "warning" if blocking_count else "success"
    if strict and blocking_count:
        status = "error"
    if status == "success" and any(finding.status == "warning" for finding in findings):
        status = "warning"

    return {
        "schema_version": 1,
        "status": status,
        "summary": {
            "total_paths": len(findings),
            "blocking_findings": blocking_count,
            "counts_by_classification": dict(sorted(counts_by_classification.items())),
            "counts_by_status": dict(sorted(counts_by_status.items())),
            "counts_by_code": dict(sorted(counts_by_code.items())),
        },
        "findings": [asdict(finding) for finding in findings],
        "metadata": {
            "inventory_scope": "tracked_files",
            "strict": strict,
            "next_steps": [
                _next_step(
                    "review",
                    "python3 Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py --json",
                    "Inspect the full machine-readable inventory before changing tracked surfaces.",
                ),
                _next_step(
                    "policy",
                    "edit Docs/agents/15-repo-surface-ownership.md or Infrastructure/policy/repo_surface_allowlist.json",
                    "Document intentional exceptions instead of hiding policy debt.",
                ),
                _next_step(
                    "safety",
                    "rg -n '<candidate-path-or-skill-name>' Skills Plugins Infrastructure Docs .skillsets .agents",
                    "Reference-scan candidates before any cleanup action.",
                ),
            ],
        },
    }


def print_human_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Repo surface inventory")
    print(f"- status: {report['status']}")
    print(f"- tracked paths: {summary['total_paths']}")
    print(f"- blocking findings: {summary['blocking_findings']}")
    print("- counts by classification:")
    for classification, count in summary["counts_by_classification"].items():
        print(f"  - {classification}: {count}")
    print("- notable findings:")
    notable = [
        finding
        for finding in report["findings"]
        if finding["status"] in {"unknown", "violation"} or finding["severity"] == "error"
    ][:20]
    if not notable:
        print("  - none")
        return
    for finding in notable:
        print(
            "  - {path}: {classification}/{status} ({code})".format(
                path=finding["path"],
                classification=finding["classification"],
                status=finding["status"],
                code=finding["code"],
            )
        )
    if len(notable) < summary["blocking_findings"]:
        print(f"  - ... {summary['blocking_findings'] - len(notable)} more blocking findings")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON-only stdout.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when blocking findings exist.")
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to inventory. Defaults to this checkout.",
    )
    parser.add_argument(
        "--allowlist",
        default=str(DEFAULT_ALLOWLIST),
        help="Allowlist JSON path. Missing file is treated as an empty allowlist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    allowlist_path = Path(args.allowlist)
    if not allowlist_path.is_absolute():
        allowlist_path = repo_root / allowlist_path

    try:
        allowlist_entries = load_allowlist(allowlist_path)
        paths = git_ls_files(repo_root)
        findings = classify_paths(paths, allowlist_entries)
        report = build_report(findings, strict=args.strict)
    except Exception as exc:
        if args.json:
            print(
                json.dumps(
                    {
                        "schema_version": 1,
                        "status": "error",
                        "summary": {
                            "total_paths": 0,
                            "blocking_findings": 1,
                            "counts_by_classification": {},
                            "counts_by_status": {"violation": 1},
                            "counts_by_code": {"inventory_error": 1},
                        },
                        "findings": [
                            {
                                "path": "",
                                "classification": "unknown",
                                "status": "violation",
                                "code": "inventory_error",
                                "severity": "error",
                                "blocking": True,
                                "allowlist_entry": None,
                                "reason": str(exc),
                                "recommendation": "Fix the inventory command inputs or allowlist schema.",
                                "metadata": {
                                    "next_steps": [
                                        _next_step(
                                            "fix",
                                            "python3 Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py --help",
                                            "Fix the inventory command inputs or allowlist schema.",
                                        )
                                    ]
                                },
                            }
                        ],
                        "metadata": {"inventory_scope": "tracked_files", "strict": args.strict},
                    },
                    sort_keys=True,
                )
            )
        else:
            print(f"repo surface inventory failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print_human_report(report)

    if args.strict and report["summary"]["blocking_findings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
