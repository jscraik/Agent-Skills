#!/usr/bin/env python3
"""
validate-adjacency.py  —  Detect drift between adjacency.yaml and SKILL.md See Also tables.

Outputs:
  - edges in SKILL.md but NOT in adjacency.yaml (missing from data source)
  - edges in adjacency.yaml but NOT in any SKILL.md (stale seed entries)

Usage:
  python3 scripts/validate-adjacency.py [vault_root]

Exit codes:
  0 = clean
  1 = drift detected (configurable threshold via DRIFT_THRESHOLD env var, default 0)
"""
import json, os, pathlib, re, sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT      = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
ADJ_YAML  = ROOT / "docs/skill-graphs/adjacency.yaml"
THRESHOLD = int(os.environ.get("DRIFT_THRESHOLD", "0"))
CANONICAL_PREFIXES = {
    "auth/",
    "backend/",
    "frontend/",
    "github/",
    "interview/",
    "personas/",
    "product/",
    "skills-system/",
    "utilities/",
}

TOPIC_MAPS = {
    "frontend-ui", "backend-platform", "agent-ops",
    "product-strategy", "security-ops", "content-publishing",
    "mobile-native", "index",
}

# ── 1. Extract SKILL.md edges ─────────────────────────────────────────────────
skill_edges: set[tuple] = set()
seen_skills: set[str] = set()   # dedup by skill name — matches build-adjacency-yaml.py


def is_canonical_skill_md(path: pathlib.Path) -> bool:
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if rel == "SKILL.md":
        return False
    return any(rel.startswith(prefix) for prefix in CANONICAL_PREFIXES)

for md in sorted(ROOT.rglob("SKILL.md")):
    if not is_canonical_skill_md(md):
        continue
    skill = md.parts[-2]
    if skill in seen_skills:          # first path wins (same as builder)
        continue
    seen_skills.add(skill)

    content = md.read_text(encoding="utf-8", errors="replace")
    sa_block = re.search(r"## See Also\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not sa_block:
        continue
    for row in sa_block.group(1).splitlines():
        m = re.match(r"\|\s*\[\[([^\]]+)\]\]\s*\|", row)
        if m:
            target = m.group(1).strip()
            if target not in TOPIC_MAPS:
                skill_edges.add((skill, target))

# ── 2. Load adjacency.yaml edges ──────────────────────────────────────────────
yaml_edges: set[tuple] = set()
if ADJ_YAML.exists() and HAS_YAML:
    adj = yaml.safe_load(ADJ_YAML.read_text()) or {}
    for skill, refs in adj.items():
        if not isinstance(refs, dict):
            continue
        for target in refs:
            if target not in TOPIC_MAPS:
                yaml_edges.add((skill, target))
elif not HAS_YAML:
    print("WARNING: pyyaml not installed — skipping adjacency.yaml validation", file=sys.stderr)
    sys.exit(0)
elif not ADJ_YAML.exists():
    print(f"WARNING: {ADJ_YAML} not found — skipping", file=sys.stderr)
    sys.exit(0)

# ── 3. Diff ───────────────────────────────────────────────────────────────────
in_skill_not_yaml = sorted(skill_edges - yaml_edges)
in_yaml_not_skill = sorted(yaml_edges - skill_edges)

total_drift = len(in_skill_not_yaml) + len(in_yaml_not_skill)

print(f"validate-adjacency: SKILL.md edges={len(skill_edges)} YAML edges={len(yaml_edges)} drift={total_drift}")

if in_skill_not_yaml:
    print(f"\nIn SKILL.md but NOT in adjacency.yaml ({len(in_skill_not_yaml)}):")
    for frm, to in in_skill_not_yaml[:20]:
        print(f"  MISSING  {frm} → {to}")
    if len(in_skill_not_yaml) > 20:
        print(f"  … and {len(in_skill_not_yaml)-20} more")

if in_yaml_not_skill:
    print(f"\nIn adjacency.yaml but NOT in any SKILL.md ({len(in_yaml_not_skill)}):")
    for frm, to in in_yaml_not_skill[:20]:
        print(f"  STALE    {frm} → {to}")
    if len(in_yaml_not_skill) > 20:
        print(f"  … and {len(in_yaml_not_skill)-20} more")

if total_drift == 0:
    print("  ✓ adjacency.yaml and SKILL.md See Also are in sync")

if total_drift > THRESHOLD:
    print(f"\nExit 1: drift ({total_drift}) exceeds threshold ({THRESHOLD})", file=sys.stderr)
    sys.exit(1)

sys.exit(0)
