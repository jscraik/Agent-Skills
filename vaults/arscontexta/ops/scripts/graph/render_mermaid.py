#!/usr/bin/env python3
"""Render Mermaid diagram and summary for graph index artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from _graph_lib import read_json, write_text_atomic


def _sanitize_node_key(node_id: str, seen: Dict[str, int]) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "_", node_id)
    safe = safe.strip("_") or "node"
    if safe[0].isdigit():
        safe = f"n_{safe}"

    base = safe
    if safe in seen:
        seen[safe] += 1
        safe = f"{base}_{seen[base]}"
    else:
        seen[base] = 0
    return safe


def _render_node_id(raw_id: str) -> str:
    sanitized = re.sub(r"[\"'\\]", lambda match: f"\\{match.group(0)}", raw_id)
    return sanitized.replace("\n", " ").replace("\r", " ")


def render_mermaid_graph(nodes: List[Dict[str, object]], edges: List[Dict[str, str]]) -> Tuple[str, Dict[str, str], Counter]:
    seen_ids: Dict[str, int] = {}
    id_map: Dict[str, str] = {}
    for node in nodes:
        node_id = str(node["id"])
        id_map[node_id] = _sanitize_node_key(node_id, seen_ids)

    lines = ["flowchart TD"]
    for node in nodes:
        raw_id = str(node["id"])
        label = str(node.get("title") or raw_id)
        mermaid_id = id_map[raw_id]
        lines.append(f'    {mermaid_id}["{_render_node_id(label)}"]')

    for edge in edges:
        source = id_map[str(edge["from"])]
        target = id_map[str(edge["to"])]
        lines.append(f"    {source} --> {target}")

    line_count = Counter({
        "nodes": len(nodes),
        "edges": len(edges),
    })
    return "\n".join(lines), id_map, line_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-nodes", type=int, default=200)
    parser.add_argument("--max-edges", type=int, default=1000)
    return parser.parse_args()


def build_warning_block(warnings: List[Dict[str, str]]) -> List[str]:
    if not warnings:
        return ["No parser or link warnings detected."]

    by_code: Dict[str, int] = Counter(w["code"] for w in warnings)
    lines = ["Warnings:"]
    for code in sorted(by_code):
        lines.append(f"- {code}: {by_code[code]}")
    return lines


def main() -> None:
    args = parse_args()
    index = read_json(Path(args.index))
    nodes = index.get("nodes", [])
    edges = index.get("edges", [])
    stats = index.get("stats", {})
    warnings = index.get("warnings", [])

    warnings = [dict(w) for w in warnings]

    header = [
        "# Graph Visual",
        "",
        "Rendered from `graph-index.json` using Ars Contexta graph operations.",
        f"Generated: {index.get('built_at', '')}",
        "",
    ]

    if not nodes:
        md_body = [
            "No markdown notes were discovered in the vault for graph generation.",
            "Empty-state summary: node_count=0, edge_count=0, status=empty.",
        ]
        content = "\n".join(header + md_body)
        write_text_atomic(Path(args.output), content)
        return

    mermaid_body, _id_map, line_count = render_mermaid_graph(nodes, edges)
    truncated_nodes = stats.get("truncated_nodes", False)
    truncated_edges = stats.get("truncated_edges", False)
    source_node_count = stats.get("source_node_count", stats.get("node_count", len(nodes)))
    source_edge_count = stats.get("source_edge_count", len(edges))

    summary = [
        "## Summary",
        f"- nodes: {stats.get('node_count', len(nodes))}",
        f"- edges: {stats.get('edge_count', len(edges))}",
        f"- source_nodes: {source_node_count}",
        f"- source_edges: {source_edge_count}",
        f"- truncated_nodes: {str(bool(truncated_nodes)).lower()}",
        f"- truncated_edges: {str(bool(truncated_edges)).lower()}",
        "",
        "## Parser Health",
        *build_warning_block(warnings),
        "",
    ]

    max_nodes = int(args.max_nodes)
    max_edges = int(args.max_edges)
    if max_nodes > 0 and source_node_count > max_nodes:
        summary.append(f"Node truncation applied at max_nodes={max_nodes}.")
    if max_edges > 0 and source_edge_count > max_edges:
        summary.append(f"Edge truncation applied at max_edges={max_edges}.")

    lines = [
        *header,
        *summary,
        "## Mermaid",
        "```mermaid",
        mermaid_body,
        "```",
        "\n",
    ]

    # deterministic top hub output
    hubs = []
    for node in sorted(
        nodes,
        key=lambda item: (-(item.get("in_degree", 0) + item.get("out_degree", 0)), str(item.get("id"))),
    )[:10]:
        hubs.append(
            f"- {node['id']} (in: {node.get('in_degree', 0)}, out: {node.get('out_degree', 0)})"
        )

    lines.append("## Top Hubs")
    lines.extend(hubs)
    content = "\n".join(lines) + "\n"
    write_text_atomic(Path(args.output), content)


if __name__ == "__main__":
    main()
