#!/usr/bin/env python3
"""
compute-edge-weights.py  —  Analyse Codex session logs for skill co-invocation
and produce a weight delta file that extract-skill-edges.py can merge into the
edge JSON.

Output: ops/metrics/graph/session-weights.json
  {"skill-a:skill-b": 3, ...}  — co-occurrence count (both orderings collapsed)
"""
import json, pathlib, re, sys
from collections import Counter, defaultdict
from itertools import combinations

SESSIONS_DIR = pathlib.Path.home() / ".codex/sessions"
ROOT         = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT          = ROOT / "ops/metrics/graph/session-weights.json"

# Load known skill names from edges file so we only track real skills
edges_file = ROOT / "ops/metrics/graph/skill-edges.json"
known_skills: set[str] = set()
if edges_file.exists():
    data = json.loads(edges_file.read_text())
    known_skills = {n["id"] for n in data["nodes"]}

def extract_session_skills(jsonl_path: pathlib.Path) -> list[str]:
    """Return ordered list of skill names mentioned in a session."""
    mentioned: list[str] = []
    seen = set()
    for line in jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev   = json.loads(line)
            text = json.dumps(ev.get("payload", ""))
        except Exception:
            continue
        # Match skill names in file paths, wikilinks, and skill mentions
        for m in re.finditer(r"/([a-z][a-z0-9_-]+)/SKILL\.md", text):
            s = m.group(1)
            if s in known_skills and s not in seen:
                seen.add(s)
                mentioned.append(s)
        for m in re.finditer(r"\[\[([a-z][a-z0-9_-]+)\]\]", text):
            s = m.group(1)
            if s in known_skills and s not in seen:
                seen.add(s)
                mentioned.append(s)
    return mentioned

co_counts: Counter = Counter()
session_files = sorted(SESSIONS_DIR.rglob("*.jsonl"))

processed = 0
for sf in session_files:
    try:
        skills = extract_session_skills(sf)
        if len(skills) < 2:
            continue
        for a, b in combinations(skills, 2):
            key = ":".join(sorted([a, b]))
            co_counts[key] += 1
        processed += 1
    except Exception:
        continue

# Normalise: weight = log1p(count) so single co-occurrence = 0.69, 10 = 2.4
import math
weights = {
    k: round(1.0 + math.log1p(v), 3)
    for k, v in co_counts.most_common(500)
    if v >= 1
}

result = {
    "schema_version": 1,
    "sessions_scanned": processed,
    "pairs_found": len(weights),
    "weights": weights,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n")
print(f"compute-edge-weights: {processed} sessions, {len(weights)} weighted pairs → {OUT}")
if weights:
    print("Top pairs:")
    for k, v in sorted(weights.items(), key=lambda x: -x[1])[:10]:
        print(f"  {v:.2f}  {k}")
