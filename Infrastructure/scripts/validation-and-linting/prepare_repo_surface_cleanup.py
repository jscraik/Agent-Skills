#!/usr/bin/env python3
"""Prepare non-destructive repo surface cleanup evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "reports" / "repo-surface"
DEFAULT_PLAN = (
    REPO_ROOT
    / "Docs"
    / "plans"
    / "2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md"
)
DEFAULT_RETIRED_SKILL_NAMES = [
    "playwright-interactive",
    "swift-development",
    "slides",
    "spreadsheet",
    "react-ui-patterns",
    "shadcn-ui",
    "security-best-practices",
    "security-threat-model",
    "gh-workflow",
]
REFERENCE_ROOTS = [
    "Skills",
    "Plugins",
    "Infrastructure/references",
    "Infrastructure/scripts",
    "Infrastructure/tests",
    "Infrastructure/ops",
    "Docs",
    ".skillsets",
    ".agents",
]
REFERENCE_SCAN_GLOBS = [
    "--glob",
    "!Infrastructure/artifacts/**",
    "--glob",
    "!artifacts/**",
    "--glob",
    "!Infrastructure/tmp/**",
]
MAX_REPORTED_REFERENCES = 25
MAX_REPORTED_CANDIDATES = 250


@dataclass(frozen=True)
class ReferenceEvidence:
    command: str
    exit_code: int
    total_hits: int
    sample: list[str]

    @property
    def has_references(self) -> bool:
        return self.total_hits > 0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_inventory(repo_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["./bin/ask", "repo", "surface", "--json"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "repo surface inventory failed with exit "
            f"{result.returncode}: {result.stderr.strip() or result.stdout[:500]}"
        )
    envelope = json.loads(result.stdout)
    return envelope["data"]["repo_surface"]


def _existing_reference_roots(repo_root: Path) -> list[str]:
    return [root for root in REFERENCE_ROOTS if (repo_root / root).exists()]


def _reference_scan(repo_root: Path, patterns: list[str]) -> ReferenceEvidence:
    roots = _existing_reference_roots(repo_root)
    if not patterns or not roots:
        return ReferenceEvidence(command="", exit_code=1, total_hits=0, sample=[])
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as pattern_file:
        pattern_file.write("\n".join(patterns))
        pattern_file.write("\n")
        pattern_path = Path(pattern_file.name)
    command = ["rg", "-n", "-F", "-f", str(pattern_path), *REFERENCE_SCAN_GLOBS, *roots]
    try:
        result = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        pattern_path.unlink(missing_ok=True)
    if result.returncode not in {0, 1}:
        raise RuntimeError(
            f"reference scan failed with exit {result.returncode}: {result.stderr.strip()}"
        )
    hits = [line for line in result.stdout.splitlines() if line.strip()]
    return ReferenceEvidence(
        command=(
            "rg -n -F -f <pattern-file> "
            + " ".join([*REFERENCE_SCAN_GLOBS, *roots])
            + f" # pattern_count={len(patterns)}"
        ),
        exit_code=result.returncode,
        total_hits=len(hits),
        sample=hits[:MAX_REPORTED_REFERENCES],
    )


def _path_prefix(path: str) -> str:
    parts = Path(path).parts
    if len(parts) >= 2 and parts[0] == "Infrastructure":
        return "/".join(parts[:2])
    return parts[0] if parts else path


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _summarize_paths(findings: list[dict[str, Any]]) -> dict[str, Any]:
    prefixes = Counter(_path_prefix(finding["path"]) for finding in findings)
    return {
        "total": len(findings),
        "counts_by_prefix": dict(sorted(prefixes.items())),
        "paths": [finding["path"] for finding in findings[:MAX_REPORTED_CANDIDATES]],
        "truncated": len(findings) > MAX_REPORTED_CANDIDATES,
    }


def _candidate_state(evidence: ReferenceEvidence, *, ownership_blocked: bool = False) -> str:
    if ownership_blocked or evidence.has_references:
        return "blocked"
    return "candidate"


def _state_buckets(state: str, candidate_summary: dict[str, Any]) -> dict[str, Any]:
    empty_summary = {"total": 0}
    return {
        "candidate": candidate_summary if state == "candidate" else empty_summary,
        "blocked": candidate_summary if state == "blocked" else empty_summary,
        "safe_to_delete": empty_summary,
    }


def _group(
    *,
    name: str,
    description: str,
    patterns: list[str],
    reference_evidence: ReferenceEvidence,
    candidate_summary: dict[str, Any],
    ownership_blocked: bool = False,
    retention_decision: str,
) -> dict[str, Any]:
    state = _candidate_state(reference_evidence, ownership_blocked=ownership_blocked)
    reported_patterns = patterns[:MAX_REPORTED_CANDIDATES]
    blockers: list[str] = []
    if reference_evidence.has_references:
        blockers.append("reference_scan_found_hits")
    if ownership_blocked:
        blockers.append("ownership_decision_required")
    if state == "candidate":
        blockers.append("future_cleanup_pr_must_confirm_owner_allowlist_or_retention")
    return {
        "name": name,
        "description": description,
        "state": state,
        "retention_decision": retention_decision,
        "state_buckets": _state_buckets(state, candidate_summary),
        "reference_scan": {
            "pattern_count": len(patterns),
            "patterns": reported_patterns,
            "patterns_truncated": len(patterns) > len(reported_patterns),
            "command": reference_evidence.command,
            "exit_code": reference_evidence.exit_code,
            "total_hits": reference_evidence.total_hits,
            "sample": reference_evidence.sample,
        },
        "candidate_summary": candidate_summary,
        "blockers": blockers,
        "safe_to_delete": [],
        "safe_to_delete_policy": (
            "Preparation mode never marks candidates safe_to_delete. A later deletion "
            "phase must attach a completed falsification pass."
        ),
    }


def build_cleanup_report(
    inventory: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    retired_skill_names: list[str] | None = None,
) -> dict[str, Any]:
    if retired_skill_names is None:
        retired_skill_names = DEFAULT_RETIRED_SKILL_NAMES
    findings = inventory.get("findings", [])
    historical = [
        finding
        for finding in findings
        if finding.get("classification") == "historical_artifact"
        and finding.get("status") in {"violation", "warning"}
    ]
    nested_infra = [
        finding
        for finding in findings
        if finding.get("code") == "duplicated_infrastructure_path"
    ]
    unresolved_ownership = [
        finding
        for finding in findings
        if finding.get("code")
        in {
            "ownership_decision_required",
            "tracked_runtime_database",
            "tracked_runtime_state",
            "tracked_plugin_cache",
        }
    ]

    historical_patterns = [finding["path"] for finding in historical]
    nested_patterns = [finding["path"] for finding in nested_infra]
    ownership_patterns = [finding["path"] for finding in unresolved_ownership]

    groups = [
        _group(
            name="historical_generated_artifacts",
            description="Tracked generated evidence and run output that needs a later cleanup PR.",
            patterns=historical_patterns,
            reference_evidence=_reference_scan(repo_root, historical_patterns),
            candidate_summary=_summarize_paths(historical),
            retention_decision="Keep only documented fixtures, summaries, indexes, or intentional archives.",
        ),
        _group(
            name="retired_skill_debris",
            description="Skill names suspected to be retired, folded, plugin-owned, or stale.",
            patterns=retired_skill_names,
            reference_evidence=_reference_scan(repo_root, retired_skill_names),
            candidate_summary={
                "total": len(retired_skill_names),
                "names": retired_skill_names,
            },
            retention_decision="Fix active references, move needed context behind indexes, or archive with reason.",
        ),
        _group(
            name="suspicious_nested_infra_paths",
            description="Duplicated Infrastructure/Infrastructure path shapes.",
            patterns=nested_patterns,
            reference_evidence=_reference_scan(repo_root, nested_patterns),
            candidate_summary=_summarize_paths(nested_infra),
            retention_decision="Delete only after proving no source, runtime, or deferred-context reader exists.",
        ),
        _group(
            name="unresolved_generated_runtime_ownership",
            description="Tracked surfaces that need owner, generator, fixture, or vendoring decisions.",
            patterns=ownership_patterns,
            reference_evidence=_reference_scan(repo_root, ownership_patterns),
            candidate_summary=_summarize_paths(unresolved_ownership),
            ownership_blocked=True,
            retention_decision="Document owner/update command or remove from tracked source in a later reviewed slice.",
        ),
    ]

    counts_by_state = Counter(group["state"] for group in groups)
    return {
        "schema_version": 1,
        "status": "success",
        "linear_issue": "JSC-246",
        "plan": _display_path(DEFAULT_PLAN, repo_root),
        "summary": {
            "groups": len(groups),
            "counts_by_state": dict(sorted(counts_by_state.items())),
            "safe_to_delete_total": sum(len(group["safe_to_delete"]) for group in groups),
        },
        "groups": groups,
        "metadata": {
            "mode": "preparation_only",
            "deletions_performed": False,
            "inventory_summary": inventory.get("summary", {}),
            "reference_roots": _existing_reference_roots(repo_root),
            "report_retention": "generated_ignored",
            "next_steps": [
                {
                    "type": "review",
                    "command": "review artifacts/reports/repo-surface/repo-surface-cleanup-prep.json",
                    "rationale": "Inspect candidate groups before authorizing any cleanup PR.",
                },
                {
                    "type": "cleanup",
                    "command": "run a deletion PR only after owner and falsification evidence is attached",
                    "rationale": "P3 is evidence preparation, not artifact deletion.",
                },
            ],
        },
    }


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Repo Surface Cleanup Preparation",
        "",
        f"- Linear issue: `{report['linear_issue']}`",
        f"- Plan: `{report['plan']}`",
        f"- Mode: `{report['metadata']['mode']}`",
        f"- Deletions performed: `{report['metadata']['deletions_performed']}`",
        f"- Safe to delete total: `{report['summary']['safe_to_delete_total']}`",
        "",
        "## Groups",
        "",
    ]
    for group in report["groups"]:
        lines.extend(
            [
                f"### {group['name']}",
                "",
                f"- State: `{group['state']}`",
                f"- Candidates: `{group['candidate_summary']['total']}`",
                f"- Reference hits: `{group['reference_scan']['total_hits']}`",
                f"- Retention decision: {group['retention_decision']}",
                f"- Scan command: `{group['reference_scan']['command']}`",
                "",
            ]
        )
        if group["reference_scan"]["sample"]:
            lines.append("Sample references:")
            lines.append("")
            for item in group["reference_scan"]["sample"][:5]:
                lines.append(f"- `{item}`")
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_reports(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "repo-surface-cleanup-prep.json"
    md_path = output_dir / "repo-surface-cleanup-prep.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report, md_path)
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit the cleanup report JSON to stdout.")
    parser.add_argument(
        "--inventory-json",
        help="Use an existing repo surface inventory JSON file instead of running ./bin/ask.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Generated report output directory.",
    )
    parser.add_argument(
        "--retired-skill-name",
        action="append",
        dest="retired_skill_names",
        help="Retired skill name to scan. May be repeated; defaults to the P3 seed set.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root. Defaults to this checkout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    inventory = _load_json(Path(args.inventory_json)) if args.inventory_json else _run_inventory(repo_root)
    report = build_cleanup_report(
        inventory,
        repo_root=repo_root,
        retired_skill_names=args.retired_skill_names,
    )
    json_path, md_path = write_reports(report, Path(args.output_dir))
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
