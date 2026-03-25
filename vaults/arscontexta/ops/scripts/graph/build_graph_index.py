#!/usr/bin/env python3
"""Build deterministic graph index artifacts from markdown wiki links."""

from __future__ import annotations

import argparse
from pathlib import Path

from _graph_lib import build_graph_index, build_truncated_view, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notes-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-nodes", type=int, default=200)
    parser.add_argument("--max-edges", type=int, default=1000)
    parser.add_argument("--vault-root", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = build_graph_index(Path(args.notes_dir))
    if args.max_nodes > 0 or args.max_edges > 0:
        index, _ = build_truncated_view(index, args.max_nodes, args.max_edges)

    index["stats"]["max_nodes_requested"] = args.max_nodes
    index["stats"]["max_edges_requested"] = args.max_edges
    if args.vault_root:
        index["vault_root"] = args.vault_root

    write_json_atomic(Path(args.output), index)


if __name__ == "__main__":
    main()
