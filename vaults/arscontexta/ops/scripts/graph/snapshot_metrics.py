#!/usr/bin/env python3
"""Append graph metrics snapshots for evolution reporting."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from _graph_lib import compute_components, compute_metric_payload, read_json, read_ndjson_lines, write_json_atomic, append_ndjson_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--ndjson-output", required=True)
    parser.add_argument("--latest-output", required=True)
    return parser.parse_args()


def build_metrics_payload(index: Dict[str, Any], historical: list[Dict[str, Any]]) -> Dict[str, Any]:
    communities, node_in, node_out = compute_components(index)
    metrics = compute_metric_payload(index, communities, node_in, node_out)
    metrics = dict(metrics)
    metrics.update(
        {
            "schema": "arscontexta_graph_metrics.v1",
            "run_ts": datetime.now(timezone.utc).isoformat(),
            "input_index": index.get("notes_dir", ""),
            "warning_count": len(index.get("warnings", [])),
            "historical_samples_before": len(historical),
            "insufficient_history": len(historical) < 1,
            "max_nodes": index.get("stats", {}).get("max_nodes_requested"),
            "max_edges": index.get("stats", {}).get("max_edges_requested"),
            "notes_dir": index.get("notes_dir", ""),
            "schema_version": "v1",
        }
    )
    return metrics


def write_latest(latest_output: Path, payload: Dict[str, Any]) -> None:
    write_json_atomic(latest_output, payload)


def main() -> None:
    args = parse_args()
    index = read_json(Path(args.index))

    ndjson_output = Path(args.ndjson_output)
    historical = read_ndjson_lines(ndjson_output)
    payload = build_metrics_payload(index, historical)

    append_ndjson_atomic(ndjson_output, payload)

    if len(historical) == 0:
        payload["insufficient_history"] = True
        payload["history_notes"] = "bootstrap"
    else:
        payload["insufficient_history"] = False

    write_latest(Path(args.latest_output), payload)


if __name__ == "__main__":
    main()
