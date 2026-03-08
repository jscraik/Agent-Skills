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
import pathlib
import re
import sys
from collections import deque

notes_dir = pathlib.Path(sys.argv[1])
top_n = int(sys.argv[2])

files = sorted(notes_dir.rglob("*.md"))
if not files:
    print("mode: betweenness")
    print("notes: 0")
    print("edges: 0")
    print("result: no markdown notes found")
    sys.exit(0)

title_to_path = {}
for f in files:
    title = f.stem
    if title in title_to_path:
        continue
    title_to_path[title] = f

nodes = sorted(title_to_path.keys())
node_set = set(nodes)
adj = {n: set() for n in nodes}

link_pattern = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")

for src in nodes:
    text = title_to_path[src].read_text(encoding="utf-8", errors="ignore")
    for raw in link_pattern.findall(text):
        dst = raw.strip()
        if dst in node_set and dst != src:
            adj[src].add(dst)
            adj[dst].add(src)

n = len(nodes)
edge_count = sum(len(v) for v in adj.values()) // 2

if n < 3:
    print("mode: betweenness")
    print(f"notes: {n}")
    print(f"edges: {edge_count}")
    print("normalized: true")
    print("\nrank\tscore\tdegree\tnote")
    for i, name in enumerate(nodes[:top_n], start=1):
        print(f"{i}\t0.000000\t{len(adj[name])}\t[[{name}]]")
    sys.exit(0)

cb = {v: 0.0 for v in nodes}

# Brandes algorithm for unweighted graphs (undirected).
for s in nodes:
    stack = []
    pred = {w: [] for w in nodes}
    sigma = {w: 0.0 for w in nodes}
    dist = {w: -1 for w in nodes}

    sigma[s] = 1.0
    dist[s] = 0
    q = deque([s])

    while q:
        v = q.popleft()
        stack.append(v)
        for w in adj[v]:
            if dist[w] < 0:
                q.append(w)
                dist[w] = dist[v] + 1
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
                pred[w].append(v)

    delta = {w: 0.0 for w in nodes}
    while stack:
        w = stack.pop()
        if sigma[w] > 0:
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
        if w != s:
            cb[w] += delta[w]

# Undirected correction.
for v in nodes:
    cb[v] /= 2.0

# Normalized to [0,1] for undirected graphs.
norm = ((n - 1) * (n - 2)) / 2.0
if norm > 0:
    for v in nodes:
        cb[v] /= norm

ranked = sorted(nodes, key=lambda x: (-cb[x], x))[:top_n]

print("mode: betweenness")
print(f"notes: {n}")
print(f"edges: {edge_count}")
print("normalized: true")
print("\nrank\tscore\tdegree\tnote")
for i, name in enumerate(ranked, start=1):
    print(f"{i}\t{cb[name]:.6f}\t{len(adj[name])}\t[[{name}]]")
PY
