#!/usr/bin/env python3
"""Generate deterministic latent skill-set manifests for rooted routing."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import build_skill_modules, modules_by_skill_set, rel, repo_root

DEFAULT_OUTPUT_DIR = repo_root() / ".skillsets"
SCOPE_PRECEDENCE = {
    "global": 10,
    "local-plugin": 20,
    "project": 30,
}


def _apply_scope_precedence(modules: list[Any]) -> list[Any]:
    """
    Keep only modules with the highest scope precedence for each (skill_set, id) identity.
    
    This function groups the input modules by their manifest identity (skill_set, id)
    and selects modules whose scope has the highest precedence according to
    SCOPE_PRECEDENCE (e.g., project > local-plugin > global). The selected modules
    are returned in a deterministic order.
    
    Returns:
        list[Any]: Selected modules sorted by (module.skill_set, module.id, module.source_path).
    """
    rows_by_identity: dict[tuple[str, str], list[Any]] = defaultdict(list)
    selected: list[Any] = []
    for module in modules:
        rows_by_identity[(module.skill_set, module.id)].append(module)
    for rows in rows_by_identity.values():
        best_rank = max(SCOPE_PRECEDENCE.get(row.scope, 0) for row in rows)
        selected.extend(row for row in rows if SCOPE_PRECEDENCE.get(row.scope, 0) == best_rank)
    return sorted(selected, key=lambda module: (module.skill_set, module.id, module.source_path))


def build_manifest_report(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """
    Builds a validation report and per-skill-set manifest descriptors for rooted manifests under the given output directory.
    
    Parameters:
        output_dir (Path): Target base directory where manifests would be written (used to compute manifest paths in the report).
    
    Returns:
        dict[str, Any]: A report containing:
            - status: "pass" if no violations, "fail" otherwise.
            - projection_mode: "rooted".
            - policy_identity: policy identity string.
            - manifest_count: number of skill-set manifests described.
            - module_count: number of modules selected after scope precedence.
            - unmapped: unmapped data returned by the skill module builder.
            - duplicate_ids: list of duplicate (skill_set, id) entries with their source paths.
            - duplicate_source_paths: list of source paths shared by multiple modules with their entries.
            - violations: list of violation objects (each with a `code` and details) for:
                - DUPLICATE_MANIFEST_IDS
                - DUPLICATE_MANIFEST_SOURCE_PATHS
                - MISSING_MANIFEST_PROVENANCE
            - manifests: list of manifest descriptors for each root skill set, each including:
                - skill_set: skill set name
                - path: relative manifest path
                - count: number of rows
                - metadata_status_counts: counts of `metadata_status` values
                - rows: list of row dictionaries suitable for serialization
    """
    discovered_modules, unmapped = build_skill_modules()
    modules = _apply_scope_precedence(discovered_modules)
    grouped = modules_by_skill_set(modules)
    duplicate_ids: list[dict[str, Any]] = []
    duplicate_source_paths: list[dict[str, Any]] = []
    rows_by_identity: dict[tuple[str, str], list[Any]] = defaultdict(list)
    rows_by_source: dict[str, list[Any]] = defaultdict(list)
    for module in modules:
        rows_by_identity[(module.skill_set, module.id)].append(module)
        rows_by_source[module.source_path].append(module)
    for (skill_set, module_id), rows in sorted(rows_by_identity.items()):
        if len(rows) > 1:
            duplicate_ids.append({
                "skill_set": skill_set,
                "id": module_id,
                "source_paths": [row.source_path for row in rows],
            })
    for source_path, rows in sorted(rows_by_source.items()):
        if len(rows) > 1:
            duplicate_source_paths.append({
                "source_path": source_path,
                "entries": [{"skill_set": row.skill_set, "id": row.id} for row in rows],
            })
    missing_provenance = [
        module.source_path
        for module in modules
        if not module.provenance.get("generator")
        or not module.provenance.get("policy_identity")
        or not module.provenance.get("source_sha256")
    ]
    violations: list[dict[str, Any]] = []
    if duplicate_ids:
        violations.append({"code": "DUPLICATE_MANIFEST_IDS", "duplicates": duplicate_ids})
    if duplicate_source_paths:
        violations.append({"code": "DUPLICATE_MANIFEST_SOURCE_PATHS", "duplicates": duplicate_source_paths})
    if missing_provenance:
        violations.append({"code": "MISSING_MANIFEST_PROVENANCE", "source_paths": missing_provenance})
    manifests = []
    for skill_set in ROOT_SKILL_SET_NAMES:
        rows = grouped.get(skill_set, [])
        manifest_path = output_dir / skill_set / "manifest.jsonl"
        manifests.append({
            "skill_set": skill_set,
            "path": rel(manifest_path),
            "count": len(rows),
            "metadata_status_counts": _count_by(rows, "metadata_status"),
            "rows": [row.to_manifest_row() for row in rows],
        })
    return {
        "status": "pass" if not violations else "fail",
        "projection_mode": "rooted",
        "policy_identity": policy_identity(),
        "manifest_count": len(manifests),
        "module_count": len(modules),
        "unmapped": unmapped,
        "duplicate_ids": duplicate_ids,
        "duplicate_source_paths": duplicate_source_paths,
        "violations": violations,
        "manifests": manifests,
    }


def _count_by(rows: list[Any], attr: str) -> dict[str, int]:
    """
    Count occurrences of an attribute's values across a sequence of row-like objects.
    
    Parameters:
        rows (list[Any]): Iterable of objects from which the attribute will be read.
        attr (str): Name of the attribute to count on each row; each attribute value is converted to a string.
    
    Returns:
        dict[str, int]: Mapping from the stringified attribute value to the number of times it appears, sorted by key.
    """
    counts: dict[str, int] = {}
    for row in rows:
        value = str(getattr(row, attr))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def write_manifests(report: dict[str, Any], output_dir: Path) -> list[dict[str, str]]:
    """
    Write manifest JSONL files for each skill set described in `report["manifests"]`.
    
    Parameters:
    	report (dict): Report containing a "manifests" iterable. Each manifest must be a mapping with at least:
    		- "skill_set" (str): target skill set directory name.
    		- "rows" (Iterable[dict]): manifest rows; each row must include "id" and "source_path" keys used for sorting.
    	output_dir (Path): Base directory where per-skill-set subdirectories and `manifest.jsonl` files will be created.
    
    Returns:
    	writes (list[dict[str, str]]): List of write action records with keys:
    		- "path": relative path to the written manifest file,
    		- "action": the action performed (always "write"),
    		- "count": number of rows written as a string.
    """
    writes: list[dict[str, str]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for manifest in report["manifests"]:
        target = output_dir / manifest["skill_set"] / "manifest.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        rows = sorted(manifest["rows"], key=lambda row: (row["id"], row["source_path"]))
        content = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
        target.write_text(content, encoding="utf-8")
        writes.append({"path": rel(target), "action": "write", "count": str(len(rows))})
    return writes


def public_report(report: dict[str, Any]) -> dict[str, Any]:
    """
    Produce a copy of a manifest report with each manifest's "rows" field omitted.
    
    Parameters:
        report (dict[str, Any]): A manifest report containing a "manifests" key whose value is an iterable of manifest dictionaries.
    
    Returns:
        dict[str, Any]: A shallow copy of `report` where each manifest dict in `"manifests"` excludes the `"rows"` key.
    """
    return {
        **report,
        "manifests": [
            {key: value for key, value in manifest.items() if key != "rows"}
            for manifest in report["manifests"]
        ],
    }


def main() -> int:
    """
    CLI entrypoint that builds rooted skill-set manifest reports and optionally writes manifest files.
    
    Parses command-line flags (--output-dir, --dry-run, --write, --json), invokes the manifest build process, optionally writes manifest.jsonl files when validations pass, and emits either a JSON payload or a human-readable summary.
    
    Returns:
        int: `0` if the generated report has status "pass", `1` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_manifest_report(args.output_dir)
    writes: list[dict[str, str]] = []
    if args.write and not args.dry_run:
        if report["status"] != "pass":
            if args.json:
                print(json.dumps(public_report(report), indent=2, sort_keys=True))
            return 1
        writes = write_manifests(report, args.output_dir)
    payload = {**public_report(report), "writes": writes, "dry_run": bool(args.dry_run or not args.write)}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"skill-set manifests: {payload['status']} ({payload['module_count']} modules)")
        for violation in payload["violations"]:
            print(f"- {violation['code']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
