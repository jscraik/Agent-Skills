#!/usr/bin/env python3
"""
extract-skill-edges.py  —  extract See Also cross-skill edges from SKILL.md files.

Merges three sources (highest precedence first):
  1. SKILL.md ## See Also tables (authoritative descriptions)
  2. docs/skill-graphs/adjacency.yaml seed (for YAML-only additions)
  3. ops/metrics/graph/session-weights.json (real co-invocation signal)

Outputs ops/metrics/graph/skill-edges.json with weighted edges:
  {"schema_version": 2, "nodes": [...], "edges": [{"from":..,"to":..,"weight":1.4,"desc":".."}]}

Usage:
  python3 extract-skill-edges.py <vault_root> <edges_out>
"""
import json, math, pathlib, re, sys
from datetime import datetime, timezone

VAULT_ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
EDGES_OUT  = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else VAULT_ROOT / "ops/metrics/graph/skill-edges.json"

TOPIC_MAPS = {
    "frontend-ui", "backend-platform", "agent-ops",
    "product-strategy", "security-ops", "content-publishing",
    "mobile-native", "index",
}

# ── 1. Topic assignments from MOC files ──────────────────────────────────────
topic_assignments: dict[str, str] = {}
moc_dir = VAULT_ROOT / "docs/skill-graphs/topic-maps"
if moc_dir.exists():
    for moc in sorted(moc_dir.glob("*.md")):
        if moc.stem == "index":
            continue
        topic = moc.stem
        for m in re.finditer(r"\[\[([a-z0-9_-]+)\]\]", moc.read_text()):
            s = m.group(1)
            if s not in TOPIC_MAPS:
                topic_assignments[s] = topic

# ── 2. Session weights (co-invocation signal) ─────────────────────────────────
session_weights: dict[str, float] = {}
sw_path = VAULT_ROOT / "ops/metrics/graph/session-weights.json"
if sw_path.exists():
    try:
        sw_data = json.loads(sw_path.read_text())
        session_weights = sw_data.get("weights", {})
    except Exception:
        pass

def get_weight(a: str, b: str) -> float:
    key = ":".join(sorted([a, b]))
    return session_weights.get(key, 1.0)

# ── 3. Walk all SKILL.md files ───────────────────────────────────────────────
edge_map: dict[tuple, dict] = {}   # (from,to) -> edge dict
seen_real: set[str] = set()
seen_nodes: dict[str, dict] = {}

for md in sorted(VAULT_ROOT.rglob("SKILL.md")):
    parts = md.parts
    if len(parts) < 2:
        continue
    skill_name = parts[-2]

    real = str(md.resolve())
    if real in seen_real:
        continue
    seen_real.add(real)

    content = md.read_text(encoding="utf-8", errors="replace")

    topic_match = re.search(r"\*\*Topic map:\*\*\s*\[\[([^\]]+)\]\]", content)
    topic = topic_match.group(1) if topic_match else topic_assignments.get(skill_name, "unknown")
    if skill_name not in seen_nodes:
        seen_nodes[skill_name] = {"id": skill_name, "topic": topic}

    sa_block = re.search(r"## See Also\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not sa_block:
        continue

    for row in sa_block.group(1).splitlines():
        m = re.match(r"\|\s*\[\[([^\]]+)\]\]\s*\|\s*(.+?)\s*\|", row)
        if not m:
            continue
        target = m.group(1).strip()
        desc   = m.group(2).strip()
        if target in TOPIC_MAPS:
            continue
        key = (skill_name, target)
        if key not in edge_map:
            edge_map[key] = {
                "from":   skill_name,
                "to":     target,
                "weight": round(get_weight(skill_name, target), 3),
                "desc":   desc,
            }

# ── 4. Merge adjacency.yaml seed (adds YAML-only edges) ──────────────────────
adj_yaml = VAULT_ROOT / "docs/skill-graphs/adjacency.yaml"
if adj_yaml.exists():
    try:
        import yaml  # optional; degrade gracefully without it
        adj = yaml.safe_load(adj_yaml.read_text()) or {}
        for skill, refs in adj.items():
            if not isinstance(refs, dict):
                continue
            if skill not in seen_nodes:
                seen_nodes[skill] = {"id": skill, "topic": topic_assignments.get(skill, "unknown")}
            for target, desc in refs.items():
                if target in TOPIC_MAPS:
                    continue
                key = (skill, target)
                if key not in edge_map:   # SKILL.md takes priority
                    edge_map[key] = {
                        "from":   skill,
                        "to":     target,
                        "weight": round(get_weight(skill, target), 3),
                        "desc":   str(desc),
                        "source": "adjacency_yaml",
                    }
    except ImportError:
        pass  # PyYAML not available — skip YAML seed

nodes = list(seen_nodes.values())
edges = list(edge_map.values())
# Sort edges by weight desc for readable JSON
edges.sort(key=lambda e: -e.get("weight", 1.0))

# ── Annotate nodes with in_degree, out_degree, stability ─────────────────────
from collections import Counter as _Counter
in_deg  = _Counter(e["to"]   for e in edges)
out_deg = _Counter(e["from"] for e in edges)

# Read stability from SKILL.md frontmatter
import re as _re
_FM  = _re.compile(r"^---\n(.*?)\n---", _re.DOTALL)
_STA = _re.compile(r"^stability\s*:\s*(\S+)", _re.MULTILINE)
_stability: dict[str, str] = {}
for _md in VAULT_ROOT.rglob("SKILL.md"):
    _skill = _md.parts[-2] if len(_md.parts) >= 2 else None
    if not _skill or _skill in _stability:
        continue
    try:
        _fm = _FM.match(_md.read_text(encoding="utf-8", errors="replace"))
        if _fm:
            _m = _STA.search(_fm.group(1))
            if _m:
                _stability[_skill] = _m.group(1)
    except Exception:
        pass

for node in nodes:
    node["in_degree"]  = in_deg.get(node["id"], 0)
    node["out_degree"] = out_deg.get(node["id"], 0)
    if node["id"] in _stability:
        node["stability"] = _stability[node["id"]]

# ── I: Stability tiers ────────────────────────────────────────────────────────
# stable    = manually marked OR in_degree >= 15
# growing   = in_degree 5–14
# experimental = in_degree < 5
for node in nodes:
    if node.get("stability") == "stable" or node["in_degree"] >= 15:
        node["tier"] = "stable"
    elif node["in_degree"] >= 5:
        node["tier"] = "growing"
    else:
        node["tier"] = "experimental"

result = {
    "schema_version": 2,
    "generated_at":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    "node_count":     len(nodes),
    "edge_count":     len(edges),
    "nodes":          nodes,
    "edges":          edges,
}

EDGES_OUT.parent.mkdir(parents=True, exist_ok=True)
EDGES_OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

weighted = sum(1 for e in edges if e.get("weight", 1.0) > 1.0)
print(f"extract-skill-edges: nodes={len(nodes)} edges={len(edges)} weighted={weighted}")
print(f"output: {EDGES_OUT}")
