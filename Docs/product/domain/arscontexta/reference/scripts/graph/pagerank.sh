#!/usr/bin/env bash
set -euo pipefail

NOTES_DIR="${1:-notes}"
TOP_N="${2:-20}"

if [[ ! -d "$NOTES_DIR" ]]; then
  echo "ERROR: notes directory not found: $NOTES_DIR" >&2
  echo "Usage: $(basename "$0") [notes_dir] [top_n]" >&2
  exit 1
fi

if ! [[ "$TOP_N" =~ ^[0-9]+$ ]] || [[ "$TOP_N" -lt 1 ]]; then
  echo "ERROR: top_n must be a positive integer (got: $TOP_N)" >&2
  exit 1
fi

python3 - "$NOTES_DIR" "$TOP_N" <<"PY"
import math
import pathlib
import re
import sys
from collections import defaultdict

notes_dir = pathlib.Path(sys.argv[1])
top_n = int(sys.argv[2])

files = sorted(notes_dir.rglob("*.md"))
if not files:
    print("mode: pagerank")
    print("notes: 0")
    print("edges: 0")
    print("result: no markdown notes found")
    sys.exit(0)

# Title map uses basename stem because wiki links resolve by title.
title_to_path = {}
for f in files:
    title = f.stem
    if title in title_to_path:
        # Keep first stable path and ignore duplicates for deterministic behavior.
        continue
    title_to_path[title] = f

nodes = sorted(title_to_path.keys())
node_idx = {n: i for i, n in enumerate(nodes)}

link_pattern = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
out_edges = {n: set() for n in nodes}
in_degree = defaultdict(int)

for src in nodes:
    text = title_to_path[src].read_text(encoding="utf-8", errors="ignore")
    for raw in link_pattern.findall(text):
        target = raw.strip()
        if target in node_idx and target != src and target not in out_edges[src]:
            out_edges[src].add(target)
            in_degree[target] += 1

n_nodes = len(nodes)
if n_nodes == 1:
    only = nodes[0]
    print("mode: pagerank")
    print("notes: 1")
    print("edges: 0")
    print("converged: true")
    print("iterations: 0")
    print("\nrank\tscore\tin_degree\tout_degree\tnote")
    print(f"1\t1.000000\t0\t0\t[[{only}]]")
    sys.exit(0)

# Standard PageRank parameters.
damping = 0.85
max_iter = 200
tol = 1e-7

scores = {node: 1.0 / n_nodes for node in nodes}
out_deg = {n: len(out_edges[n]) for n in nodes}

converged = False
iterations = 0
for i in range(max_iter):
    iterations = i + 1
    new_scores = {node: (1.0 - damping) / n_nodes for node in nodes}

    dangling_mass = sum(scores[node] for node in nodes if out_deg[node] == 0)
    dangling_share = damping * dangling_mass / n_nodes

    for node in nodes:
        new_scores[node] += dangling_share

    for src in nodes:
        if out_deg[src] == 0:
            continue
        share = damping * scores[src] / out_deg[src]
        for dst in out_edges[src]:
            new_scores[dst] += share

    delta = sum(abs(new_scores[k] - scores[k]) for k in nodes)
    scores = new_scores
    if delta < tol:
        converged = True
        break

edge_count = sum(len(v) for v in out_edges.values())
print("mode: pagerank")
print(f"notes: {n_nodes}")
print(f"edges: {edge_count}")
print(f"converged: {'true' if converged else 'false'}")
print(f"iterations: {iterations}")

ranked = sorted(nodes, key=lambda x: (-scores[x], x))[:top_n]
print("\nrank\tscore\tin_degree\tout_degree\tnote")
for i, name in enumerate(ranked, start=1):
    print(f"{i}\t{scores[name]:.6f}\t{in_degree[name]}\t{out_deg[name]}\t[[{name}]]")
PY
