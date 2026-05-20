#!/usr/bin/env python3
"""Benchmark skill portfolio marker coverage and distribution.

This script hardens benchmark checks beyond binary pass/fail gates by adding
cluster-level marker distribution requirements.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from skill_graph_inventory import discover_inventory_skills, load_inventory_policy


@dataclass(frozen=True)
class Cluster:
    id: str
    description: str
    include_prefixes: List[str]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Benchmark skill portfolio marker coverage.")
    p.add_argument("--root", default=".", help="Repository root")
    p.add_argument(
        "--config",
        default="Skills/skill-builder/Infrastructure/references/benchmark-policy.json",
        help="Benchmark policy JSON path (relative to root or absolute)",
    )
    p.add_argument("--mode", choices=["off", "warn", "fail"], default="warn")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--output-json", default=None, help="Optional output JSON path")
    p.add_argument("--output-md", default=None, help="Optional output markdown path")
    return p.parse_args()


def find_skill_files(root: Path) -> List[Path]:
    policy = load_inventory_policy(root)
    inventory_skills = discover_inventory_skills(root, policy)
    return sorted({row.skill_md.resolve() for row in inventory_skills})


def rel_skill(root: Path, skill_md: Path) -> str:
    return str(skill_md.parent.resolve().relative_to(root.resolve()))


def load_policy(path: Path) -> Dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("benchmark policy must be a JSON object")
    for key in ["markers", "clusters", "rules"]:
        if key not in obj:
            raise ValueError(f"benchmark policy missing `{key}`")
    return obj


def compile_markers(markers_obj: Dict) -> Dict[str, re.Pattern[str]]:
    out: Dict[str, re.Pattern[str]] = {}
    for marker_id, marker in markers_obj.items():
        pattern = marker.get("regex") if isinstance(marker, dict) else None
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError(f"marker `{marker_id}` missing regex")
        out[marker_id] = re.compile(pattern, re.IGNORECASE)
    return out


def pick_cluster(skill_rel: str, clusters: Dict[str, Cluster]) -> str | None:
    for cluster_id, cluster in clusters.items():
        for prefix in cluster.include_prefixes:
            if skill_rel.startswith(prefix):
                return cluster_id
    return None


def safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def evaluate_cluster(
    rule: Dict,
    marker_hits: Dict[str, int],
    total_skills: int,
) -> Tuple[List[str], List[str]]:
    fails: List[str] = []
    warns: List[str] = []

    required_all = rule.get("required_all", []) if isinstance(rule, dict) else []
    required_any = rule.get("required_any", []) if isinstance(rule, dict) else []
    min_hits_fail = rule.get("min_hits_fail", {}) if isinstance(rule, dict) else {}
    min_hits_warn = rule.get("min_hits_warn", {}) if isinstance(rule, dict) else {}
    min_coverage_fail = safe_float(rule.get("min_coverage_fail"), 0.0) if isinstance(rule, dict) else 0.0
    min_coverage_warn = safe_float(rule.get("min_coverage_warn"), 0.0) if isinstance(rule, dict) else 0.0

    for marker_id in required_all:
        if marker_hits.get(marker_id, 0) <= 0:
            fails.append(f"required_all missing `{marker_id}`")

    for group in required_any:
        if not isinstance(group, list) or not group:
            continue
        if not any(marker_hits.get(marker_id, 0) > 0 for marker_id in group):
            fails.append("required_any missing any of ({})".format("|".join(group)))

    for marker_id, threshold in min_hits_fail.items():
        if marker_hits.get(marker_id, 0) < int(threshold):
            fails.append(
                f"distribution fail: `{marker_id}` hits {marker_hits.get(marker_id, 0)} < {int(threshold)}"
            )

    for marker_id, threshold in min_hits_warn.items():
        if marker_hits.get(marker_id, 0) < int(threshold):
            warns.append(
                f"distribution warn: `{marker_id}` hits {marker_hits.get(marker_id, 0)} < {int(threshold)}"
            )

    if total_skills > 0:
        # coverage over skills: count skills with at least one tracked marker
        # caller inserts actual value via marker_hits["__skills_with_any__"]
        skills_with_any_actual = marker_hits.get("__skills_with_any__", 0)
        coverage = skills_with_any_actual / total_skills
        if coverage < min_coverage_fail:
            fails.append(f"coverage fail: {coverage:.3f} < {min_coverage_fail:.3f}")
        if coverage < min_coverage_warn:
            warns.append(f"coverage warn: {coverage:.3f} < {min_coverage_warn:.3f}")

    return fails, warns


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path

    policy = load_policy(config_path)
    marker_patterns = compile_markers(policy["markers"])

    clusters: Dict[str, Cluster] = {}
    for cluster_id, cluster_obj in policy["clusters"].items():
        prefixes = cluster_obj.get("include_prefixes", []) if isinstance(cluster_obj, dict) else []
        clusters[cluster_id] = Cluster(
            id=cluster_id,
            description=(cluster_obj.get("description", "") if isinstance(cluster_obj, dict) else ""),
            include_prefixes=[str(x) for x in prefixes],
        )

    skill_files = find_skill_files(root)
    cluster_skills: Dict[str, List[str]] = {cluster_id: [] for cluster_id in clusters}
    cluster_marker_hits: Dict[str, Dict[str, int]] = {
        cluster_id: {marker_id: 0 for marker_id in marker_patterns.keys()} for cluster_id in clusters
    }
    cluster_skills_with_any: Dict[str, int] = {cluster_id: 0 for cluster_id in clusters}

    uncategorized: List[str] = []

    for skill_md in skill_files:
        skill_rel = rel_skill(root, skill_md)
        cluster_id = pick_cluster(skill_rel, clusters)
        if cluster_id is None:
            uncategorized.append(skill_rel)
            continue

        cluster_skills[cluster_id].append(skill_rel)
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        any_hit = False
        for marker_id, pattern in marker_patterns.items():
            if pattern.search(text):
                cluster_marker_hits[cluster_id][marker_id] += 1
                any_hit = True
        if any_hit:
            cluster_skills_with_any[cluster_id] += 1

    cluster_results = []
    fail_count = 0
    warn_count = 0

    for cluster_id, cluster in clusters.items():
        total = len(cluster_skills[cluster_id])
        marker_hits = dict(cluster_marker_hits[cluster_id])
        marker_hits["__skills_with_any__"] = cluster_skills_with_any[cluster_id]
        rule = policy["rules"].get(cluster_id, {})
        fails, warns = evaluate_cluster(rule, marker_hits, total)
        fail_count += len(fails)
        warn_count += len(warns)
        coverage = (cluster_skills_with_any[cluster_id] / total) if total else 0.0
        cluster_results.append(
            {
                "cluster": cluster_id,
                "description": cluster.description,
                "skills": total,
                "skills_with_any_marker": cluster_skills_with_any[cluster_id],
                "coverage": round(coverage, 4),
                "marker_hits": cluster_marker_hits[cluster_id],
                "fails": fails,
                "warns": warns,
                "pass": len(fails) == 0,
            }
        )

    overall_pass = True
    if args.mode == "warn":
        overall_pass = fail_count == 0
    elif args.mode == "fail":
        overall_pass = fail_count == 0 and warn_count == 0

    # Use repo-relative path for reproducibility across machines/CI
    relative_policy_path = str(config_path.relative_to(root)) if config_path.is_relative_to(root) else str(config_path)

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "policy_path": relative_policy_path,
        "skills_scanned": len(skill_files),
        "uncategorized_skills": uncategorized,
        "cluster_results": cluster_results,
        "summary": {
            "cluster_count": len(cluster_results),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "overall_pass": overall_pass,
        },
    }

    if args.output_json:
        out_json = Path(args.output_json)
        if not out_json.is_absolute():
            out_json = root / out_json
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.output_md:
        out_md = Path(args.output_md)
        if not out_md.is_absolute():
            out_md = root / out_md
        out_md.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Skill Portfolio Benchmark", "", f"- Mode: `{args.mode}`", f"- Skills scanned: `{len(skill_files)}`"]
        lines.append(f"- Overall pass: `{'PASS' if overall_pass else 'FAIL'}`")
        lines.append("")
        for row in cluster_results:
            lines.append(
                f"- {row['cluster']}: skills={row['skills']}, coverage={row['coverage']}, fails={len(row['fails'])}, warns={len(row['warns'])}"
            )
        out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Skills scanned: {len(skill_files)}")
        print(f"Cluster checks: {len(cluster_results)}")
        print(f"Fails: {fail_count}")
        print(f"Warnings: {warn_count}")
        print(f"RESULT: {'PASS' if overall_pass else 'FAIL'}")

    return 0 if overall_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())