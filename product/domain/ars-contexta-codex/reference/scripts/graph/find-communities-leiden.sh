#!/usr/bin/env bash
set -euo pipefail

NOTES_DIR="${1:-notes}"

if [[ ! -d "$NOTES_DIR" ]]; then
  echo "ERROR: notes directory not found: $NOTES_DIR" >&2
  echo "Usage: $(basename "$0") [notes_dir]" >&2
  exit 1
fi

python3 - "$NOTES_DIR" <<"PY"
import pathlib
import re
import sys
from collections import Counter, defaultdict

notes_dir = pathlib.Path(sys.argv[1])
files = sorted(notes_dir.rglob("*.md"))

if not files:
    print("mode: leiden")
    print("notes: 0")
    print("edges: 0")
    print("communities: 0")
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
idx = {n: i for i, n in enumerate(nodes)}

link_pattern = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
edges = set()
adj = {n: set() for n in nodes}

for src in nodes:
    text = title_to_path[src].read_text(encoding="utf-8", errors="ignore")
    for raw in link_pattern.findall(text):
        dst = raw.strip()
        if dst in node_set and dst != src:
            a, b = sorted((src, dst))
            if (a, b) not in edges:
                edges.add((a, b))
            adj[src].add(dst)
            adj[dst].add(src)

m = len(edges)

if len(nodes) == 1:
    only = nodes[0]
    print("mode: leiden")
    print("notes: 1")
    print("edges: 0")
    print("communities: 1")
    print("quality_metric: modularity")
    print("quality_score: 0.000000")
    print("\ncommunity\tsize\tmembers")
    print(f"1\t1\t[[{only}]]")
    sys.exit(0)


def modularity(communities):
    # communities: dict[int,list[str]] on undirected simple graph
    if m == 0:
        return 0.0
    deg = {n: len(adj[n]) for n in nodes}
    q = 0.0
    for members in communities.values():
        member_set = set(members)
        internal_edges = 0
        degree_sum = 0
        for n in members:
            degree_sum += deg[n]
            for nb in adj[n]:
                if nb in member_set and n < nb:
                    internal_edges += 1
        q += (internal_edges / m) - (degree_sum / (2.0 * m)) ** 2
    return q


def to_communities_from_membership(membership):
    communities = defaultdict(list)
    for i, cid in enumerate(membership):
        communities[int(cid)].append(nodes[i])
    # deterministic order for members
    for cid in list(communities.keys()):
        communities[cid] = sorted(communities[cid])
    return communities


mode = "fallback-label-propagation"
quality_metric = "modularity"
communities = None
quality_score = None

# Attempt real Leiden if optional deps are installed.
try:
    import igraph as ig  # type: ignore
    import leidenalg as la  # type: ignore

    g = ig.Graph()
    g.add_vertices(nodes)
    g.add_edges(list(edges))

    try:
        partition = la.find_partition(
            g,
            la.RBConfigurationVertexPartition,
            n_iterations=-1,
            seed=42,
        )
    except TypeError:
        partition = la.find_partition(
            g,
            la.RBConfigurationVertexPartition,
            n_iterations=-1,
        )

    communities = to_communities_from_membership(partition.membership)
    try:
        quality_score = float(partition.modularity)
    except Exception:
        quality_score = float(modularity(communities))
    mode = "leiden"
except Exception:
    # Deterministic label-propagation fallback.
    labels = {n: i for i, n in enumerate(nodes)}
    max_iter = 50

    for _ in range(max_iter):
        changed = False
        for n in nodes:
            nbs = sorted(adj[n])
            if not nbs:
                continue
            counts = Counter(labels[x] for x in nbs)
            best_freq = max(counts.values())
            candidates = sorted(k for k, v in counts.items() if v == best_freq)
            best = candidates[0]
            if labels[n] != best:
                labels[n] = best
                changed = True
        if not changed:
            break

    comm_map = defaultdict(list)
    for n in nodes:
        comm_map[labels[n]].append(n)
    communities = {}
    for i, members in enumerate(sorted((sorted(v) for v in comm_map.values()), key=lambda x: (-len(x), x)), start=1):
        communities[i] = members
    quality_score = float(modularity(communities))

# Reindex communities for stable output: largest first, then lexical.
sorted_groups = sorted((sorted(v) for v in communities.values()), key=lambda x: (-len(x), x))
communities = {i + 1: grp for i, grp in enumerate(sorted_groups)}

print(f"mode: {mode}")
print(f"notes: {len(nodes)}")
print(f"edges: {m}")
print(f"communities: {len(communities)}")
print(f"quality_metric: {quality_metric}")
print(f"quality_score: {quality_score:.6f}")

print("\ncommunity\tsize\tmembers")
for cid, members in communities.items():
    printable = ", ".join(f"[[{m}]]" for m in members)
    print(f"{cid}\t{len(members)}\t{printable}")
PY
