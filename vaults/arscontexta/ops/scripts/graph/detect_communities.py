#!/usr/bin/env python3
"""Detect connected communities and produce split/merge guidance."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from _graph_lib import compute_components, compute_metric_payload, read_json, write_json_atomic, write_text_atomic

STOPWORDS = {
    "and",
    "are",
    "at",
    "for",
    "from",
    "had",
    "has",
    "have",
    "its",
    "not",
    "the",
    "that",
    "this",
    "those",
    "these",
    "was",
    "were",
    "with",
    "your",
    "you",
}


def tokenize(text: str) -> List[str]:
    tokens = [token for token in re.findall(r"[\w']+", (text or "").lower()) if len(token) > 2]
    return sorted(set(token for token in tokens if token not in STOPWORDS))


def overlap_similarity(left_tokens: List[str], right_tokens: List[str]) -> float:
    left = set(left_tokens)
    right = set(right_tokens)
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    parser.add_argument("--min-size", type=int, default=3)
    return parser.parse_args()


def build_communities(index: Dict[str, Any], min_size: int) -> Dict[str, Any]:
    communities, node_in, node_out = compute_components(index)
    community_records: List[Dict[str, Any]] = []

    for idx, component in enumerate(communities):
        status = "observe"
        recommendation = "Observe for growth or future split opportunities."
        if len(component) >= max(min_size * 3, 8):
            status = "split"
            recommendation = "Consider splitting this component into clearer topic clusters."

        community_id = f"community-{idx + 1:02d}"
        community_records.append(
            {
                "community_id": community_id,
                "size": len(component),
                "nodes": component,
                "status": status,
                "recommendation": recommendation,
                "node_count": len(component),
            }
        )

    community_records.sort(key=lambda row: (-row["size"], row["community_id"]))

    splits = [c for c in community_records if c["status"] == "split"]
    observes = [c for c in community_records if c["status"] == "observe"]

    community_tokens = []
    node_by_id = {node["id"]: node for node in index.get("nodes", [])}

    for record in community_records:
        token_bag: List[str] = []
        for node_id in record["nodes"]:
            node = node_by_id.get(node_id, {})
            token_bag.extend(tokenize(node_id))
            token_bag.extend(tokenize(str(node.get("title", ""))))
            token_bag.extend(tokenize(str(node.get("path", ""))))
        community_tokens.append({"id": record["community_id"], "tokens": sorted(set(token_bag))})

    merges: List[Dict[str, Any]] = []
    for i in range(len(community_tokens)):
        left = community_tokens[i]
        for j in range(i + 1, len(community_tokens)):
            right = community_tokens[j]
            score = overlap_similarity(left["tokens"], right["tokens"])
            if score < 0.30:
                continue
            merges.append(
                {
                    "left": left["id"],
                    "right": right["id"],
                    "score": round(score, 6),
                    "reason": "Vocabulary overlap suggests shared concepts to consider merging.",
                }
            )

    merges.sort(key=lambda item: item["score"], reverse=True)

    return {
        "communities": community_records,
        "metrics": compute_metric_payload(index, communities, node_in, node_out),
        "recommendations": {
            "split": splits,
            "observe": observes,
            "merge": merges[:20],
        },
    }


def build_markdown(payload: Dict[str, Any], index_path: Path, min_size: int) -> str:
    communities = payload["communities"]
    recommendations = payload["recommendations"]
    metrics = payload["metrics"]

    lines = [
        "# Graph Communities",
        f"Generated: {payload['built_at']}",
        "",
        f"Source index: `{index_path}`",
        "",
        "## Overview",
        f"- communities: {payload['stats']['communities']}",
        f"- min_size: {min_size}",
        f"- split_candidates: {len(recommendations['split'])}",
        f"- merge_candidates: {len(recommendations['merge'])}",
        f"- orphan_count: {metrics.get('orphan_count', 0)}",
        f"- dangling_count: {metrics.get('dangling_count', 0)}",
        "",
        "## Community List",
    ]

    for community in communities:
        lines.append(f"- {community['community_id']}: size={community['size']} status={community['status']}")
        lines.append(f"  - recommendation: {community['recommendation']}")
        lines.append(
            f"  - nodes: {', '.join(community['nodes'][:10])}"
            + ("..." if len(community['nodes']) > 10 else "")
        )

    lines.extend(["", "## Split recommendations", ""])
    if recommendations["split"]:
        for item in recommendations["split"]:
            lines.append(f"- {item['community_id']} ({item['size']} nodes): {item['recommendation']}")
    else:
        lines.append("No split recommendations at the current threshold.")

    lines.extend(["", "## Merge recommendations", ""])
    if recommendations["merge"]:
        for item in recommendations["merge"]:
            lines.append(f"- {item['left']} ↔ {item['right']} (score {item['score']})")
            lines.append(f"  - {item['reason']}")
    else:
        lines.append("No merge candidates above the configured overlap threshold.")

    lines.extend(["", "## Notes", "- Recommendations are heuristic and should be validated by content review."])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    index = read_json(Path(args.index))

    payload = build_communities(index, args.min_size)
    payload.update(
        {
            "schema": "arscontexta_graph_communities.v1",
            "built_at": index.get("built_at"),
            "input_index": str(args.index),
            "min_size": args.min_size,
            "stats": {
                "nodes": len(index.get("nodes", [])),
                "edges": len(index.get("edges", [])),
                "communities": len(payload["communities"]),
                "split_count": len(payload["recommendations"]["split"]),
                "merge_count": len(payload["recommendations"]["merge"]),
            },
            "warnings": index.get("warnings", []),
        }
    )

    write_json_atomic(Path(args.json_output), payload)
    write_text_atomic(Path(args.markdown_output), build_markdown(payload, Path(args.index), args.min_size))


if __name__ == "__main__":
    main()
