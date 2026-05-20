#!/usr/bin/env python3
"""Refresh benchmark policy baselines from Context7 and ratchet gate thresholds.

This helper is intentionally conservative:
- Context7 pulls are optional and schedule-window aware.
- Threshold ratcheting is one-way (only tightens, never loosens).
- Writes happen only with --apply.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

API_BASE = "https://context7.com/api/v2"
DEFAULT_POLICY = "Skills/skill-builder/Infrastructure/references/benchmark-policy.json"
DEFAULT_BENCHMARK = "Infrastructure/artifacts/industry-benchmark-latest.json"
DEFAULT_REPORT = "Infrastructure/artifacts/benchmark-policy-refresh-report.json"


@dataclass(frozen=True)
class RefreshSource:
    marker_id: str
    library_name: str
    query: str
    preferred_library_id: str | None
    regex_template: str
    description_template: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Refresh benchmark policy baselines from Context7.")
    p.add_argument("--root", default=".", help="Repository root")
    p.add_argument("--policy", default=DEFAULT_POLICY, help="Benchmark policy JSON path")
    p.add_argument("--benchmark-json", default=DEFAULT_BENCHMARK, help="Benchmark JSON artifact path")
    p.add_argument("--report-json", default=DEFAULT_REPORT, help="Where to write refresh report JSON")
    p.add_argument("--schedule-days", type=int, default=7, help="Minimum days between Context7 baseline pulls")
    p.add_argument("--max-hit-ratchet-step", type=int, default=1, help="Max threshold increment per run for hit counts")
    p.add_argument(
        "--max-coverage-ratchet-step",
        type=float,
        default=0.05,
        help="Max threshold increment per run for coverage thresholds",
    )
    p.add_argument("--context7-env", default="CONTEXT7_API_KEY", help="Environment variable name for Context7 API key")
    p.add_argument("--force-context-refresh", action="store_true", help="Ignore schedule window for Context7 pulls")
    p.add_argument("--no-ratchet", action="store_true", help="Skip ratchet updates from benchmark artifact")
    p.add_argument("--require-context7", action="store_true", help="Fail if Context7 key is missing or calls fail")
    p.add_argument("--apply", action="store_true", help="Write updated policy file")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p.parse_args()


def _resolve_path(root: Path, path_text: str) -> Path:
    p = Path(path_text)
    return p if p.is_absolute() else (root / p)


def _load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _parse_validated_on(policy: Dict[str, Any]) -> date | None:
    raw = policy.get("validated_on")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _is_context_refresh_due(last_validated: date | None, schedule_days: int, force: bool) -> bool:
    if force:
        return True
    if last_validated is None:
        return True
    return date.today() >= (last_validated + timedelta(days=max(schedule_days, 1)))


def _context7_request_json(url: str, api_key: str) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = resp.read().decode("utf-8")
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type and not body.strip().startswith("{"):
            raise ValueError("Context7 response was not JSON")
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError("Context7 JSON root was not an object")
        return parsed


def _context7_search(library_name: str, query: str, api_key: str) -> Dict[str, Any]:
    params = {"libraryName": library_name}
    if query:
        params["query"] = query
    url = f"{API_BASE}/libs/search?{urllib.parse.urlencode(params)}"
    return _context7_request_json(url, api_key)


def _extract_results(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = [
        payload.get("results"),
        payload.get("libraries"),
        payload.get("data"),
    ]
    for item in candidates:
        if isinstance(item, list):
            return [x for x in item if isinstance(x, dict)]
    return []


def _pick_library(results: List[Dict[str, Any]], preferred_library_id: str | None) -> Dict[str, Any] | None:
    if not results:
        return None
    if preferred_library_id:
        for r in results:
            rid = r.get("id") or r.get("libraryId")
            if rid == preferred_library_id:
                return r

    def _score(item: Dict[str, Any]) -> float:
        score = 0.0
        bench = item.get("benchmarkScore")
        if isinstance(bench, (int, float)):
            score += float(bench)
        rep = str(item.get("sourceReputation", "")).lower()
        if rep == "high":
            score += 10.0
        elif rep == "medium":
            score += 5.0
        return score

    return sorted(results, key=_score, reverse=True)[0]


def _parse_major_from_versions(versions: Any) -> int | None:
    if not isinstance(versions, list):
        return None
    majors: List[int] = []
    for raw in versions:
        if not isinstance(raw, str):
            continue
        m = re.search(r"v?(\d+)(?:\.\d+)?(?:\.\d+)?", raw)
        if not m:
            continue
        major = int(m.group(1))
        if 1 <= major <= 99:
            majors.append(major)
    return max(majors) if majors else None


def _build_sources(policy: Dict[str, Any]) -> List[RefreshSource]:
    raw = policy.get("refresh_sources", [])
    out: List[RefreshSource] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        marker_id = str(item.get("marker_id", "")).strip()
        library_name = str(item.get("library_name", "")).strip()
        query = str(item.get("query", "")).strip()
        regex_template = str(item.get("regex_template", "")).strip()
        description_template = str(item.get("description_template", "")).strip()
        preferred = item.get("preferred_library_id")
        preferred_library_id = str(preferred).strip() if isinstance(preferred, str) and preferred.strip() else None
        if not (marker_id and library_name and regex_template and description_template):
            continue
        out.append(
            RefreshSource(
                marker_id=marker_id,
                library_name=library_name,
                query=query,
                preferred_library_id=preferred_library_id,
                regex_template=regex_template,
                description_template=description_template,
            )
        )
    return out


def _refresh_markers_from_context7(
    policy: Dict[str, Any],
    api_key: str,
    sources: List[RefreshSource],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    updates: List[Dict[str, Any]] = []
    warnings: List[str] = []
    markers = policy.get("markers")
    if not isinstance(markers, dict):
        return updates, ["policy missing `markers` object"]

    for source in sources:
        marker = markers.get(source.marker_id)
        if not isinstance(marker, dict):
            warnings.append(f"marker `{source.marker_id}` not found; skipped")
            continue
        try:
            search_payload = _context7_search(source.library_name, source.query, api_key)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            warnings.append(f"context7 search failed for `{source.library_name}`: {exc}")
            continue

        results = _extract_results(search_payload)
        picked = _pick_library(results, source.preferred_library_id)
        if not picked:
            warnings.append(f"no Context7 library candidate found for `{source.library_name}`")
            continue

        major = _parse_major_from_versions(picked.get("versions"))
        if major is None:
            warnings.append(f"no parseable major version found for `{source.library_name}`")
            continue

        new_regex = source.regex_template.format(major=major)
        new_desc = source.description_template.format(major=major)
        old_regex = marker.get("regex")
        old_desc = marker.get("description")
        marker_changed = False
        if old_regex != new_regex:
            marker["regex"] = new_regex
            marker_changed = True
        if old_desc != new_desc:
            marker["description"] = new_desc
            marker_changed = True

        updates.append(
            {
                "marker_id": source.marker_id,
                "library_name": source.library_name,
                "library_id": picked.get("id") or picked.get("libraryId"),
                "detected_major": major,
                "changed": marker_changed,
            }
        )

    return updates, warnings


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ratchet_policy_rules(
    policy: Dict[str, Any],
    benchmark_payload: Dict[str, Any],
    max_hit_step: int,
    max_cov_step: float,
) -> List[Dict[str, Any]]:
    rules = policy.get("rules")
    clusters = benchmark_payload.get("cluster_results")
    if not isinstance(rules, dict) or not isinstance(clusters, list):
        return []

    changes: List[Dict[str, Any]] = []
    max_hit_step = max(0, max_hit_step)
    max_cov_step = max(0.0, max_cov_step)

    cluster_map: Dict[str, Dict[str, Any]] = {}
    for item in clusters:
        if isinstance(item, dict) and isinstance(item.get("cluster"), str):
            cluster_map[item["cluster"]] = item

    for cluster_name, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        observed = cluster_map.get(cluster_name, {})
        observed_hits = observed.get("marker_hits", {})
        observed_cov = _safe_float(observed.get("coverage"), 0.0)
        if not isinstance(observed_hits, dict):
            observed_hits = {}

        cluster_changes: Dict[str, Any] = {"cluster": cluster_name, "updates": []}

        # Ratchet hit thresholds
        for field in ("min_hits_fail", "min_hits_warn"):
            table = rule.get(field)
            if not isinstance(table, dict):
                continue
            for marker_id, current_raw in list(table.items()):
                current = _safe_int(current_raw, 0)
                observed_count = _safe_int(observed_hits.get(marker_id), current)
                if observed_count <= current:
                    continue
                new_value = min(observed_count, current + max_hit_step)
                if new_value > current:
                    table[marker_id] = int(new_value)
                    cluster_changes["updates"].append(
                        {
                            "field": field,
                            "marker_id": marker_id,
                            "from": current,
                            "to": int(new_value),
                            "observed": observed_count,
                        }
                    )

        # Keep fail <= warn
        fail_map = rule.get("min_hits_fail")
        warn_map = rule.get("min_hits_warn")
        if isinstance(fail_map, dict) and isinstance(warn_map, dict):
            for marker_id, fail_raw in list(fail_map.items()):
                if marker_id not in warn_map:
                    continue
                fail_value = _safe_int(fail_raw, 0)
                warn_value = _safe_int(warn_map.get(marker_id), 0)
                if fail_value > warn_value:
                    fail_map[marker_id] = warn_value
                    cluster_changes["updates"].append(
                        {
                            "field": "min_hits_fail",
                            "marker_id": marker_id,
                            "from": fail_value,
                            "to": warn_value,
                            "observed": _safe_int(observed_hits.get(marker_id), warn_value),
                            "note": "normalized to fail<=warn",
                        }
                    )

        # Ratchet coverage thresholds
        for field in ("min_coverage_fail", "min_coverage_warn"):
            if field not in rule:
                continue
            current = _safe_float(rule.get(field), 0.0)
            if observed_cov <= current:
                continue
            new_value = min(observed_cov, current + max_cov_step)
            if new_value > current:
                rounded = round(new_value, 3)
                rule[field] = rounded
                cluster_changes["updates"].append(
                    {
                        "field": field,
                        "from": round(current, 3),
                        "to": rounded,
                        "observed": round(observed_cov, 3),
                    }
                )

        # Keep fail <= warn for coverage
        fail_cov = _safe_float(rule.get("min_coverage_fail"), 0.0)
        warn_cov = _safe_float(rule.get("min_coverage_warn"), 0.0)
        if fail_cov > warn_cov:
            rule["min_coverage_fail"] = round(warn_cov, 3)
            cluster_changes["updates"].append(
                {
                    "field": "min_coverage_fail",
                    "from": round(fail_cov, 3),
                    "to": round(warn_cov, 3),
                    "observed": round(observed_cov, 3),
                    "note": "normalized to fail<=warn",
                }
            )

        if cluster_changes["updates"]:
            changes.append(cluster_changes)

    return changes


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    policy_path = _resolve_path(root, args.policy).resolve()
    benchmark_path = _resolve_path(root, args.benchmark_json).resolve()
    report_path = _resolve_path(root, args.report_json).resolve()

    policy_before = _load_json(policy_path)
    policy_after = copy.deepcopy(policy_before)

    context_refresh_due = _is_context_refresh_due(
        _parse_validated_on(policy_before),
        args.schedule_days,
        args.force_context_refresh,
    )

    api_key = os.environ.get(args.context7_env, "")
    context_updates: List[Dict[str, Any]] = []
    context_warnings: List[str] = []
    context_attempted = False

    sources = _build_sources(policy_after)
    if context_refresh_due and sources:
        context_attempted = True
        if api_key:
            context_updates, context_warnings = _refresh_markers_from_context7(policy_after, api_key, sources)
        else:
            context_warnings.append(
                f"{args.context7_env} is not set; skipped Context7 baseline pull (ratchet can still run)."
            )
            if args.require_context7:
                payload = {
                    "ok": False,
                    "error": "missing_context7_api_key",
                    "context7_env": args.context7_env,
                }
                _write_json(report_path, payload)
                if args.format == "json":
                    print(json.dumps(payload, indent=2, ensure_ascii=False))
                else:
                    print(f"ERROR: {args.context7_env} is not set")
                return 2

    ratchet_changes: List[Dict[str, Any]] = []
    ratchet_warning = None
    if not args.no_ratchet:
        if benchmark_path.exists():
            benchmark_payload = _load_json(benchmark_path)
            ratchet_changes = _ratchet_policy_rules(
                policy_after,
                benchmark_payload,
                max_hit_step=args.max_hit_ratchet_step,
                max_cov_step=args.max_coverage_ratchet_step,
            )
        else:
            ratchet_warning = f"benchmark artifact not found: {benchmark_path}"

    policy_changed = policy_after != policy_before
    if policy_changed:
        policy_after["validated_on"] = date.today().isoformat()
        notes = policy_after.get("validation_notes")
        if not isinstance(notes, list):
            notes = []
        stamp = f"Auto-refreshed via refresh_benchmark_policy.py on {date.today().isoformat()}."
        if stamp not in notes:
            notes.append(stamp)
        policy_after["validation_notes"] = notes

    if args.apply and policy_changed:
        _write_json(policy_path, policy_after)

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_path": str(policy_path),
        "benchmark_path": str(benchmark_path),
        "context_refresh_due": context_refresh_due,
        "context_refresh_attempted": context_attempted,
        "context_updates": context_updates,
        "context_warnings": context_warnings,
        "ratchet_changes": ratchet_changes,
        "ratchet_warning": ratchet_warning,
        "changed": policy_changed,
        "applied": bool(args.apply and policy_changed),
    }

    _write_json(report_path, report)

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Context refresh due: {context_refresh_due}")
        print(f"Context updates: {len(context_updates)}")
        print(f"Ratchet clusters changed: {len(ratchet_changes)}")
        print(f"Policy changed: {policy_changed}")
        print(f"Applied: {bool(args.apply and policy_changed)}")
        if context_warnings:
            print(f"Context warnings: {len(context_warnings)}")
        if ratchet_warning:
            print(f"Ratchet warning: {ratchet_warning}")

    if args.require_context7 and context_refresh_due and not api_key:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
