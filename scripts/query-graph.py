#!/usr/bin/env python3
"""
query-graph.py — CLI skill graph router.

Subcommands:
  relate <skill>   Related skills sorted by weight (default, also --reverse, --depth, --topic)
  find   <query>   Full-text search across skill names and topics — returns ranked matches
  info   <skill>   Full node details: topic, tier, degree, stability, all direct links
  chain  <a> <b>   Shortest path between two skills (BFS)
  list   [--topic T] [--tier T]   List all skills optionally filtered

Global flags:
  --json           Output JSON
  --depth N        BFS depth for relate/chain (default 1)
  --reverse        Follow in-links instead of out-links (relate only)
  --topic T        Filter by topic cluster
  --tier T         Filter by stability tier (stable|growing|experimental)

Examples:
  python3 scripts/query-graph.py relate mcp-builder
  python3 scripts/query-graph.py find security
  python3 scripts/query-graph.py info writing-plans
  python3 scripts/query-graph.py chain mcp-builder verification-before-completion
  python3 scripts/query-graph.py list --topic agent-ops --tier stable
  python3 scripts/query-graph.py info evals-router --json
"""
import json, pathlib, sys, re
from collections import defaultdict, deque

ROOT     = pathlib.Path(__file__).parent.parent
EDGES_IN = ROOT / "ops/metrics/graph/skill-edges.json"

# ── colours ───────────────────────────────────────────────────────────────────
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
TIER_ICONS = {"stable": "★", "growing": "◆", "experimental": "◇"}
RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
GREEN = "\033[32m"; YELLOW = "\033[33m"; RED = "\033[31m"

# ── graph loading ─────────────────────────────────────────────────────────────
def load_graph() -> dict:
    if not EDGES_IN.exists():
        print(f"ERROR: {EDGES_IN} not found", file=sys.stderr)
        print("  Run: python3 product/domain/arscontexta/reference/scripts/graph/extract-skill-edges.py .", file=sys.stderr)
        sys.exit(1)
    return json.loads(EDGES_IN.read_text())

def build_index(data: dict):
    node_map  = {n["id"]: n for n in data["nodes"]}
    fwd: dict[str, list] = defaultdict(list)
    rev: dict[str, list] = defaultdict(list)
    for e in data["edges"]:
        fwd[e["from"]].append(e)
        rev[e["to"]].append(e)
    return node_map, fwd, rev

def find_node(data: dict, query: str) -> str | None:
    nodes = {n["id"] for n in data["nodes"]}
    if query in nodes:
        return query
    matches = sorted(n for n in nodes if query.lower() in n.lower())
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer exact prefix
        prefixed = [m for m in matches if m.startswith(query.lower())]
        best = prefixed[0] if prefixed else matches[0]
        if len(matches) > 1:
            print(f"{DIM}Ambiguous '{query}' — using '{best}'. Also: {matches[1:5]}{RESET}", file=sys.stderr)
        return best
    return None

# ── BFS helpers ───────────────────────────────────────────────────────────────
def bfs_neighbours(fwd, rev, node_map, start: str, depth: int, reverse: bool, topic_filter=None):
    adj   = rev if reverse else fwd
    in_deg = {n["id"]: n.get("in_degree", 0) for n in node_map.values()}
    visited: dict[str, int] = {start: 0}
    queue   = deque([(start, 0)])
    results = []
    while queue:
        current, d = queue.popleft()
        if d >= depth:
            continue
        edges = sorted(adj.get(current, []), key=lambda e: (-e.get("weight", 1.0), -in_deg.get(e["to"] if not reverse else e["from"], 0)))
        for edge in edges:
            peer = edge["from"] if reverse else edge["to"]
            if peer == start or peer in visited:
                continue
            visited[peer] = d + 1
            queue.append((peer, d + 1))
            pn = node_map.get(peer, {})
            if topic_filter and pn.get("topic") != topic_filter:
                continue
            results.append({
                "skill":    peer,
                "topic":    pn.get("topic", "unknown"),
                "tier":     pn.get("tier", "experimental"),
                "depth":    d + 1,
                "weight":   round(edge.get("weight", 1.0), 3),
                "desc":     edge.get("desc", ""),
                "in_links": in_deg.get(peer, 0),
                "direction": "←" if reverse else "→",
            })
    return sorted(results, key=lambda r: (-r["weight"], -r["in_links"]))

def bfs_path(fwd, start: str, end: str, max_depth: int = 6) -> list[str] | None:
    """Return shortest path from start to end via BFS, or None."""
    if start == end:
        return [start]
    visited: dict[str, str | None] = {start: None}
    queue = deque([(start, 0)])             # (node, depth)
    while queue:
        current, d = queue.popleft()
        if d >= max_depth:
            continue
        for edge in fwd.get(current, []):
            peer = edge["to"]
            if peer in visited:
                continue
            visited[peer] = current
            if peer == end:
                # Reconstruct path by walking predecessors
                path = [end]
                while path[-1] != start:
                    path.append(visited[path[-1]])  # type: ignore[arg-type]
                return list(reversed(path))
            queue.append((peer, d + 1))
    return None

# ── pretty printer helpers ────────────────────────────────────────────────────
def tc(topic: str) -> str:
    return TOPIC_COLORS.get(topic, "")

def tier_badge(tier: str) -> str:
    icon  = TIER_ICONS.get(tier, "◇")
    color = GREEN if tier == "stable" else (YELLOW if tier == "growing" else DIM)
    return f"{color}{icon} {tier}{RESET}"

# ── subcommands ───────────────────────────────────────────────────────────────

def cmd_relate(data, args):
    query      = args.get("query")
    depth      = args.get("depth", 1)
    reverse    = args.get("reverse", False)
    as_json    = args.get("json", False)
    topic_f    = args.get("topic")
    tier_f     = args.get("tier")
    node_map, fwd, rev = build_index(data)
    start = find_node(data, query)
    if not start:
        _not_found(data, query); sys.exit(1)
    results = bfs_neighbours(fwd, rev, node_map, start, depth, reverse, topic_f)
    if tier_f:
        results = [r for r in results if r.get("tier") == tier_f]
    base = node_map.get(start, {})
    if as_json:
        print(json.dumps({"skill": start, "node": base, "results": results}, indent=2))
        return
    direction_label = "← in-links from" if reverse else "→ links to"
    print(f"\n{BOLD}{tc(base.get('topic',''))}{start}{RESET}  {DIM}[{base.get('topic','?')}]{RESET}  {tier_badge(base.get('tier','experimental'))}")
    print(f"{DIM}{direction_label} (depth={depth}){RESET}\n")
    if not results:
        print(f"  {DIM}No connections found.{RESET}"); return
    prev_depth = None
    for r in results:
        if r["depth"] != prev_depth:
            if prev_depth is not None: print()
            label = "Direct" if r["depth"] == 1 else f"Depth {r['depth']}"
            print(f"  {DIM}{label}:{RESET}")
            prev_depth = r["depth"]
        w_badge  = f" {DIM}×{r['weight']:.1f}{RESET}" if r["weight"] > 1.2 else ""
        in_badge = f" {DIM}({r['in_links']} in-links){RESET}" if r["in_links"] > 3 else ""
        t_badge  = f" {TIER_ICONS.get(r['tier'],'')} " if r.get("tier") != "experimental" else ""
        print(f"    {tc(r['topic'])}• {r['skill']}{RESET}{w_badge}{in_badge}{t_badge}")
        if r["desc"]:
            print(f"      {DIM}{r['desc'][:80]}{RESET}")
    print(f"\n  {DIM}Total: {len(results)} related skill(s){RESET}\n")


def cmd_find(data, args):
    query   = args.get("query", "")
    as_json = args.get("json", False)
    topic_f = args.get("topic")
    tier_f  = args.get("tier")
    node_map, fwd, rev = build_index(data)
    ql = query.lower()
    scored: list[tuple[float, dict]] = []
    for n in data["nodes"]:
        nid   = n["id"]
        score = 0
        if ql == nid:                  score = 100
        elif nid.startswith(ql):       score = 80
        elif ql in nid:                score = 60
        elif ql in n.get("topic",""):  score = 30
        if score == 0: continue
        if topic_f and n.get("topic") != topic_f: continue
        if tier_f  and n.get("tier")  != tier_f:  continue
        score += n.get("in_degree", 0) * 0.5
        scored.append((score, n))
    scored.sort(key=lambda x: -x[0])
    if as_json:
        print(json.dumps([n for _, n in scored], indent=2)); return
    print(f"\n{BOLD}Search: '{query}'{RESET}  {DIM}({len(scored)} match(es)){RESET}\n")
    if not scored:
        print(f"  {DIM}No matches.{RESET}\n"); return
    for _, n in scored[:20]:
        tid = n.get("tier", "experimental")
        print(f"  {tc(n.get('topic',''))}• {n['id']}{RESET}  {tier_badge(tid)}  {DIM}[{n.get('topic','?')}]  ↓{n.get('in_degree',0)} in{RESET}")
    if len(scored) > 20:
        print(f"  {DIM}… and {len(scored)-20} more{RESET}")
    print()


def cmd_info(data, args):
    query   = args.get("query")
    as_json = args.get("json", False)
    node_map, fwd, rev = build_index(data)
    start = find_node(data, query)
    if not start:
        _not_found(data, query); sys.exit(1)
    n = node_map.get(start, {"id": start})
    out_edges = sorted(fwd.get(start, []), key=lambda e: -e.get("weight", 1.0))
    in_edges  = sorted(rev.get(start, []), key=lambda e: -e.get("weight", 1.0))
    if as_json:
        print(json.dumps({"node": n, "out_edges": out_edges, "in_edges": in_edges}, indent=2)); return
    tier = n.get("tier", "experimental")
    print(f"\n{BOLD}{tc(n.get('topic',''))}{start}{RESET}")
    print(f"  Topic:    {n.get('topic','?')}")
    print(f"  Tier:     {tier_badge(tier)}")
    print(f"  Stability:{' ' + n.get('stability','—')}")
    print(f"  In-links: {n.get('in_degree', len(in_edges))}")
    print(f"  Out-links:{n.get('out_degree', len(out_edges))}")
    if out_edges:
        print(f"\n  {DIM}Links to:{RESET}")
        for e in out_edges[:12]:
            w = f"  {DIM}×{e['weight']:.1f}{RESET}" if e.get("weight",1) > 1.2 else ""
            peer_n = node_map.get(e["to"], {})
            print(f"    {tc(peer_n.get('topic',''))}→ {e['to']}{RESET}{w}")
            if e.get("desc"):
                print(f"       {DIM}{e['desc'][:70]}{RESET}")
    if in_edges:
        print(f"\n  {DIM}Linked from:{RESET}")
        for e in in_edges[:12]:
            peer_n = node_map.get(e["from"], {})
            print(f"    {tc(peer_n.get('topic',''))}← {e['from']}{RESET}")
    print()


def cmd_chain(data, args):
    a       = args.get("query")
    b       = args.get("query2")
    as_json = args.get("json", False)
    node_map, fwd, rev = build_index(data)
    start = find_node(data, a)
    end   = find_node(data, b) if b else None
    if not start or not end:
        print(f"ERROR: could not resolve both skills ('{a}' → '{b}')", file=sys.stderr); sys.exit(1)
    path = bfs_path(fwd, start, end)
    if as_json:
        print(json.dumps({"from": start, "to": end, "path": path, "hops": len(path)-1 if path else None}, indent=2)); return
    if path is None:
        print(f"\n  {DIM}No path found from{RESET} {tc(node_map.get(start,{}).get('topic',''))}{start}{RESET} {DIM}to{RESET} {tc(node_map.get(end,{}).get('topic',''))}{end}{RESET}\n"); return
    print(f"\n{BOLD}Chain ({len(path)-1} hops):{RESET}\n")
    for i, skill in enumerate(path):
        pn    = node_map.get(skill, {})
        arrow = "  →  " if i < len(path) - 1 else ""
        print(f"  {tc(pn.get('topic',''))}{skill}{RESET}{DIM}{arrow}{RESET}", end="")
    print("\n")


def cmd_list(data, args):
    topic_f = args.get("topic")
    tier_f  = args.get("tier")
    as_json = args.get("json", False)
    nodes   = data["nodes"]
    if topic_f: nodes = [n for n in nodes if n.get("topic") == topic_f]
    if tier_f:  nodes = [n for n in nodes if n.get("tier")  == tier_f]
    nodes = sorted(nodes, key=lambda n: (-n.get("in_degree", 0), n["id"]))
    if as_json:
        print(json.dumps(nodes, indent=2)); return
    filters = f"{topic_f or 'all'} / {tier_f or 'all tiers'}"
    print(f"\n{BOLD}Skills [{filters}]{RESET}  {DIM}{len(nodes)} result(s){RESET}\n")
    for n in nodes:
        tier = n.get("tier", "experimental")
        print(f"  {tc(n.get('topic',''))}{n['id']:<35}{RESET}  {tier_badge(tier)}  {DIM}↓{n.get('in_degree',0)}{RESET}")
    print()


def _not_found(data, query):
    print(f"Skill not found: '{query}'", file=sys.stderr)
    candidates = sorted(n["id"] for n in data["nodes"] if query.lower() in n["id"])[:6]
    if candidates:
        print(f"Did you mean: {candidates}", file=sys.stderr)


# ── argument dispatcher ───────────────────────────────────────────────────────
SUBCOMMANDS = {"relate", "find", "info", "chain", "list"}

def main():
    raw = sys.argv[1:]
    if not raw or raw[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)

    # Determine subcommand
    if raw[0] in SUBCOMMANDS:
        subcmd  = raw[0]
        positional = [a for a in raw[1:] if not a.startswith("-")]
    else:
        # Legacy compat: first positional is a skill → treat as relate
        subcmd     = "relate"
        positional = [a for a in raw if not a.startswith("-")]

    args: dict = {
        "query":   positional[0] if positional else None,
        "query2":  positional[1] if len(positional) > 1 else None,
        "depth":   1,
        "reverse": False,
        "json":    False,
        "topic":   None,
        "tier":    None,
    }
    # Validate depth after flag parsing (set below), guarded at use
    i = 0
    flag_src = raw
    while i < len(flag_src):
        a = flag_src[i]
        if a == "--depth"   and i + 1 < len(flag_src):
            d = int(flag_src[i+1])
            args["depth"] = max(1, d)   # guard: depth must be >= 1
            i += 2; continue
        if a == "--topic"   and i + 1 < len(flag_src): args["topic"]   = flag_src[i+1];       i += 2; continue
        if a == "--tier"    and i + 1 < len(flag_src): args["tier"]    = flag_src[i+1];       i += 2; continue
        if a == "--reverse": args["reverse"] = True
        if a == "--json":    args["json"]    = True
        i += 1

    data = load_graph()
    dispatch = {
        "relate": cmd_relate,
        "find":   cmd_find,
        "info":   cmd_info,
        "chain":  cmd_chain,
        "list":   cmd_list,
    }
    dispatch[subcmd](data, args)

if __name__ == "__main__":
    main()
