#!/usr/bin/env python3
"""Render trend report from graph metrics NDJSON history."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from _graph_lib import read_ndjson_lines, write_text_atomic

METRICS = (
    "node_count",
    "edge_count",
    "density",
    "orphan_count",
    "dangling_count",
    "avg_degree",
)

# Metrics where lower values are better (for trend labeling)
LOWER_IS_BETTER = {"orphan_count", "dangling_count"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndjson", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def pct_change(new_value: float, old_value: float) -> str:
    if old_value == 0:
        return "n/a"
    delta = new_value - old_value
    pct = (delta / old_value) * 100
    return f"{pct:+.1f}%"


def status_label(delta: float, metric: str = "") -> str:
    if abs(delta) < 1e-12:
        return "stable"
    # For "lower is better" metrics, invert the trend labels
    if metric in LOWER_IS_BETTER:
        if delta > 0:
            return "regressing"
        return "improving"
    if delta > 0:
        return "improving"
    return "regressing"


def find_lookback(snapshot_rows: List[Dict[str, Any]], seconds: int) -> Dict[str, Any]:
    if not snapshot_rows:
        return {}

    latest_row = snapshot_rows[-1]
    latest_time = datetime.fromisoformat(str(latest_row["run_ts"]).replace("Z", "+00:00"))

    cutoff = latest_time.timestamp() - seconds
    target = None
    # Find the first snapshot at or after the cutoff (closest to lookback window)
    for row in snapshot_rows[:-1]:
        row_time = datetime.fromisoformat(str(row["run_ts"]).replace("Z", "+00:00")).timestamp()
        if row_time >= cutoff:
            target = row
            break
    if target is None:
        target = snapshot_rows[0]
    return {metric: target.get(metric) for metric in METRICS if metric in target}


def trend_line(latest: Dict[str, Any], previous: Dict[str, Any], metric: str) -> Tuple[str, str, str]:
    latest_value = float(latest.get(metric, 0))
    previous_value = float(previous.get(metric, 0))
    delta = latest_value - previous_value
    return (
        f"{latest_value:.4f}" if isinstance(latest_value, float) else str(int(latest_value)),
        pct_change(latest_value, previous_value),
        status_label(delta, metric),
    )


def build_report(snapshot_rows: List[Dict[str, Any]], latest: Dict[str, Any], previous: Dict[str, Any]) -> str:
    if not snapshot_rows:
        return "# Graph Evolution\n\nNo metrics snapshots available yet. Run /graph evolution with additional runs to begin trend tracking.\n"

    lines = [
        "# Graph Evolution",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Snapshots: {len(snapshot_rows)}",
        f"Latest run: {latest.get('run_ts', '')}",
    ]

    if len(snapshot_rows) < 2:
        lines.extend(
            [
                "",
                "Insufficient history: only one snapshot found.",
                "Use this first snapshot as a bootstrap reference until a second point exists.",
                "",
            ]
        )
    else:
        lines.append("\n## All-time trend vs previous")
        for metric in METRICS:
            value, change, trend = trend_line(latest, previous, metric)
            lines.append(f"- {metric}: value={value}, change={change}, trend={trend}")

    # Only show lookback trends if we have enough history (at least 2 snapshots)
    if len(snapshot_rows) >= 2:
        lookback_7d = find_lookback(snapshot_rows, 7 * 24 * 3600)
        if lookback_7d:
            lines.extend(
                [
                    "",
                    "## 7d trend",
                    "(baseline is nearest snapshot at/after 7-day lookback)",
                ]
            )
            for metric in METRICS:
                # Use lookback value if present (even if 0), else fall back to latest
                old_val = lookback_7d.get(metric)
                old = float(old_val if old_val is not None else latest.get(metric, 0))
                now = float(latest.get(metric, 0))
                delta = now - old
                lines.append(
                    f"- {metric}: value={now:.4f}, change={pct_change(now, old)}, trend={status_label(delta, metric)}"
                )

        lookback_30d = find_lookback(snapshot_rows, 30 * 24 * 3600)
        if lookback_30d:
            lines.extend(
                [
                    "",
                    "## 30d trend",
                    "(baseline is nearest snapshot at/after 30-day lookback)",
                ]
            )
            for metric in METRICS:
                # Use lookback value if present (even if 0), else fall back to latest
                old_val = lookback_30d.get(metric)
                old = float(old_val if old_val is not None else latest.get(metric, 0))
                now = float(latest.get(metric, 0))
                delta = now - old
                lines.append(
                    f"- {metric}: value={now:.4f}, change={pct_change(now, old)}, trend={status_label(delta, metric)}"
                )

    latest_warnings = latest.get("warning_count", 0)
    historical_warning = [row.get("warning_count", 0) for row in snapshot_rows]
    max_warning = max(historical_warning) if historical_warning else 0
    avg_warning = sum(historical_warning) / max(1, len(historical_warning)) if historical_warning else 0

    lines.extend(
        [
            "",
            "## Health summary",
            f"- latest warning_count: {latest_warnings}",
            f"- average warning_count: {avg_warning:.2f}",
            f"- max warning_count: {max_warning}",
            "- warning trend is monitored by ndjson snapshots.",
            "",
            "## Recommendations",
            "- If density regresses for 3+ runs, inspect orphaning notes or aggressive truncation.",
            "- If orphan_count grows while edge_count increases, check for duplicate note basenames and broken clustering.",
            "- Track dangling_count: sustained growth often indicates unresolved references in your workflow.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    snapshot_rows = read_ndjson_lines(Path(args.ndjson))
    latest = {}
    previous = {}
    if snapshot_rows:
        latest = snapshot_rows[-1]
        if len(snapshot_rows) > 1:
            previous = snapshot_rows[-2]

    report = build_report(snapshot_rows, latest, previous)
    write_text_atomic(Path(args.output), report)


if __name__ == "__main__":
    main()
