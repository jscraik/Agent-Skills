#!/usr/bin/env python3
"""
query-graph.py — CLI tool to query the skill graph at runtime.

Usage:
  python3 scripts/query-graph.py <skill-name-or-search-term> [--depth N] [--json] [--reverse]

Arguments:
  skill-name     Name of the skill (exact or partial match)
  --depth N      BFS depth to traverse (default: 1)
  --json         Output JSON instead of plain text
  --reverse      Show skills that link TO this skill (in-links) instead of out-links
  --topic T      Filter results to a specific topic cluster

Examples:
  python3 scripts/query-graph.py mcp-builder
  python3 scripts/query-graph.py "security" --topic security-ops
  python3 scripts/query-graph.py verification-before-completion --reverse
  python3 scripts/query-graph.py writing-plans --depth 2 --json
"""
import json, pathlib, sys, re
from collections import defaultdict, deque

ROOT      = pathlib.Path(__file__).parent.parent
EDGES_IN  = ROOT / "ops/metrics/graph/skill-edges.json"

def load_graph() -> dict:
    if not EDGES_IN.exists():
        print(f"ERROR: edges file not found: {EDGES_IN}", file=sys.stderr)
        print(f"  Run: python3 product/domain/arscontexta/reference/scripts/graph/extract-skill-edges.py .", file=sys.stderr)
        sys.exit(1)
    return json.loads(EDGES_IN.read_text())

def parse_args():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    query   = args[0]
    depth   = 1
    as_json = False
    reverse = False
    topic   = None
    i = 1
    while i < len(args):
        if args[i] == "--depth" and i + 1 < len(args):
            depth = int(args[i + 1]); i += 2
        elif args[i] == "--json":
            as_json = True; i += 1
        elif args[i] == "--reverse":
            reverse = True; i += 1
        elif args[i] == "--topic" and i + 1 < len(args):
            topic = args[i + 1]; i += 2
        else:
            i += 1
    return query, depth, as_json, reverse, topic

def find_node(data: dict, query: str) -> str | None:
    nodes = {n["id"] for n in data["nodes"]}
    if query in nodes:
        return query
    # Partial match
    matches = sorted(n for n in nodes if query.lower() in n.lower())
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Ambiguous: '{query}' matches {matches[:8]}", file=sys.stderr)
        return matches[0]
    return None

def bfs(data: dict, start: str, depth: int, reverse: bool) -> list[dict]:
    """BFS from start node. reverse=True follows in-edges."""
    # Build adjacency
    fwd: dict[str, list] = defaultdict(list)  # from -> edges
    rev: dict[str, list] = defaultdict(list)  # to -> edges

    for e in data["edges"]:
        fwd[e["from"]].append(e)
        rev[e["to"]].append(e)

    adj = rev if reverse else fwd
    node_info = {n["id"]: n for n in data["nodes"]}
    in_deg  = defaultdict(int)
    out_deg = defaultdict(int)
    for e in data["edges"]:
        out_deg[e["from"]] += 1
        in_deg[e["to"]] += 1

    visited: dict[str, int] = {start: 0}
    queue   = deque([(start, 0)])
    results: list[dict] = []

    while queue:
        current, d = queue.popleft()
        if d >= depth:
            continue
        edges = adj.get(current, [])
        # Sort by weight desc then in_degree desc
        edges = sorted(edges, key=lambda e: (-e.get("weight", 1.0), -in_deg.get(e["to"] if not reverse else e["from"], 0)))
        for edge in edges:
            peer = edge["from"] if reverse else edge["to"]
            if peer == start or peer in visited:
                continue
            visited[peer] = d + 1
            queue.append((peer, d + 1))
            pn = node_info.get(peer, {})
            results.append({
                "skill":    peer,
                "topic":    pn.get("topic", "unknown"),
                "depth":    d + 1,
                "weight":   round(edge.get("weight", 1.0), 3),
                "desc":     edge.get("desc", ""),
                "in_links": in_deg[peer],
                "direction": "←" if reverse else "→",
            })

    return sorted(results, key=lambda r: (-r["weight"], -r["in_links"]))

TOPIC_COLORS = {
    "agent-ops":          "\033[35m",
    "backend-platform":   "\033[36m",
    "frontend-ui":        "\033[34m",
    "product-strategy":   "\033[95m",
    "security-ops":       "\033[32m",
    "content-publishing": "\033[33m",
    "mobile-native":      "\033[94m",
    "unknown":            "\033[90m",
}
RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

def main():
    query, depth, as_json, reverse, topic_filter = parse_args()
    data  = load_graph()
    start = find_node(data, query)

    if not start:
        print(f"Skill not found: '{query}'", file=sys.stderr)
        # Show top matches
        all_nodes = sorted(n["id"] for n in data["nodes"] if query.lower() in n["id"])
        if all_nodes:
            print(f"Did you mean: {all_nodes[:5]}", file=sys.stderr)
        sys.exit(1)

    node_info = {n["id"]: n for n in data["nodes"]}
    base_node = node_info.get(start, {})
    results   = bfs(data, start, depth, reverse)

    if topic_filter:
        results = [r for r in results if r["topic"] == topic_filter]

    if as_json:
        out = {
            "query":   start,
            "topic":   base_node.get("topic"),
            "depth":   depth,
            "reverse": reverse,
            "results": results,
        }
        print(json.dumps(out, indent=2))
        return

    # Pretty print
    direction_label = "← in-links from" if reverse else "→ links to"
    color = TOPIC_COLORS.get(base_node.get("topic","unknown"), "")
    print(f"\n{BOLD}{color}{start}{RESET}  {DIM}[{base_node.get('topic','unknown')}]{RESET}")
    print(f"{DIM}{direction_label} (depth={depth}){RESET}\n")

    if not results:
        print(f"  {DIM}No connections found.{RESET}")
        return

    prev_depth = None
    for r in results:
        if r["depth"] != prev_depth:
            if prev_depth is not None:
                print()
            label = "Direct" if r["depth"] == 1 else f"Depth {r['depth']}"
            print(f"  {DIM}{label}:{RESET}")
            prev_depth = r["depth"]
        tc = TOPIC_COLORS.get(r["topic"], "")
        w_badge = f" {DIM}×{r['weight']:.1f}{RESET}" if r["weight"] > 1.2 else ""
        in_badge = f" {DIM}({r['in_links']} in-links){RESET}" if r["in_links"] > 3 else ""
        print(f"    {tc}{'•'} {r['skill']}{RESET}{w_badge}{in_badge}")
        if r["desc"]:
            print(f"      {DIM}{r['desc'][:80]}{RESET}")

    print(f"\n  {DIM}Total: {len(results)} related skill(s){RESET}\n")

if __name__ == "__main__":
    main()
