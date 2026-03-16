#!/usr/bin/env python3
"""
extract-skill-edges.py  —  extract See Also cross-skill edges from SKILL.md files.

Outputs a JSON file at EDGES_OUT with structure:
  {"schema_version": 1, "generated_at": "...", "nodes": [...], "edges": [...]}

Usage:
  python3 extract-skill-edges.py <vault_root> <edges_out>
"""
import json, pathlib, re, sys
from datetime import datetime, timezone

VAULT_ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
EDGES_OUT  = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else VAULT_ROOT / "ops/metrics/graph/skill-edges.json"

TOPIC_MAPS = {
    "frontend-ui", "backend-platform", "agent-ops",
    "product-strategy", "security-ops", "content-publishing",
    "mobile-native", "index",
}

# ── Load topic assignments from MOC files ────────────────────────────────────
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

# ── Walk all SKILL.md files ──────────────────────────────────────────────────
edges: list[dict] = []
nodes: list[dict] = []
seen_real: set[str] = set()       # dedup symlinks
seen_nodes: dict[str, dict] = {}  # skill_name -> node

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

    # Topic from See Also block takes priority, then MOC assignment
    topic_match = re.search(r"\*\*Topic map:\*\*\s*\[\[([^\]]+)\]\]", content)
    topic = topic_match.group(1) if topic_match else topic_assignments.get(skill_name, "unknown")

    if skill_name not in seen_nodes:
        seen_nodes[skill_name] = {"id": skill_name, "topic": topic}

    # Extract See Also edges (skip links to topic maps themselves)
    sa_block = re.search(r"## See Also\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if sa_block:
        for m in re.finditer(r"\[\[([a-z0-9_-]+)\]\]", sa_block.group(1)):
            target = m.group(1)
            if target not in TOPIC_MAPS:
                edges.append({"from": skill_name, "to": target})

nodes = list(seen_nodes.values())

# Dedup edges
unique_edges = list({(e["from"], e["to"]): e for e in edges}.values())

result = {
    "schema_version": 1,
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    "node_count": len(nodes),
    "edge_count": len(unique_edges),
    "nodes": nodes,
    "edges": unique_edges,
}

EDGES_OUT.parent.mkdir(parents=True, exist_ok=True)
EDGES_OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

print(f"extract-skill-edges: nodes={len(nodes)} edges={len(unique_edges)}")
print(f"output: {EDGES_OUT}")
