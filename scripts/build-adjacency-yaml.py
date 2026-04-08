#!/usr/bin/env python3
"""
build-adjacency-yaml.py  —  Extract current See Also adjacency from all SKILL.md
files and write docs/skill-graphs/adjacency.yaml as the canonical data source.

Run once to bootstrap; subsequent updates are made by editing the YAML directly.
"""
import os, pathlib, re, subprocess, sys, yaml  # needs PyYAML

ROOT     = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
OUT_YAML = ROOT / "docs/skill-graphs/adjacency.yaml"
CANONICAL_PREFIXES = {
    "auth/",
    "backend/",
    "frontend/",
    "github/",
    "interview/",
    "skills-antigravity/",
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

adjacency = {}   # skill -> {related_skill: description}
seen_skills: set[str] = set()   # deduplicate by skill name, not resolved path


def is_canonical_skill_md(path: pathlib.Path) -> bool:
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if rel == "SKILL.md":
        return False
    return any(rel.startswith(prefix) for prefix in CANONICAL_PREFIXES)

def iter_skill_md_files(root: pathlib.Path):
    # Prefer tracked files so generated/untracked projections do not pollute output.
    git_cmd = ["git", "-C", str(root), "ls-files"]
    proc = subprocess.run(git_cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0:
        yielded: set[pathlib.Path] = set()
        for rel in proc.stdout.splitlines():
            tracked_path = root / rel
            if rel.endswith("/SKILL.md"):
                skill_path = tracked_path
            elif tracked_path.is_symlink() and tracked_path.resolve().is_dir():
                skill_path = tracked_path / "SKILL.md"
            else:
                continue

            if skill_path.exists() and skill_path not in yielded:
                yielded.add(skill_path)
                yield skill_path
        return

    # Fallback for non-git contexts.
    for current_root, _, files in os.walk(root, followlinks=True):
        if "SKILL.md" in files:
            yield pathlib.Path(current_root) / "SKILL.md"


for md in sorted(iter_skill_md_files(ROOT)):
    if not is_canonical_skill_md(md):
        continue
    skill = md.parts[-2]
    if skill in seen_skills:         # first SKILL.md wins (alphabetical sort = utilities/ before skills-antigravity/ typically)
        continue
    seen_skills.add(skill)

    content = md.read_text(encoding="utf-8", errors="replace")
    sa_block = re.search(
        r"## See Also\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.DOTALL,
    )
    if not sa_block:
        continue

    rows = {}
    for row in sa_block.group(1).splitlines():
        m = re.match(r"\|\s*\[\[([^\]]+)\]\]\s*\|\s*(.+?)\s*\|", row)
        if m:
            target = m.group(1).strip()
            desc   = m.group(2).strip()
            if target not in TOPIC_MAPS and not target.startswith("|"):
                rows[target] = desc

    if rows:
        adjacency[skill] = rows

# Sort for stable diffs
sorted_adj = {
    k: dict(sorted(v.items()))
    for k, v in sorted(adjacency.items())
}

OUT_YAML.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_YAML, "w", encoding="utf-8") as f:
    f.write("# Agent-Skills See Also adjacency map\n")
    f.write("# Auto-bootstrapped from SKILL.md See Also tables.\n")
    f.write("# Edit this file to add/change cross-skill links.\n")
    f.write("# extract-skill-edges.py reads this as a seed.\n")
    f.write("#\n")
    f.write("# Format:\n")
    f.write("#   skill-name:\n")
    f.write("#     related-skill: \"when to use together\"\n")
    f.write("#\n\n")
    yaml.dump(sorted_adj, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

skill_count = len(sorted_adj)
edge_count  = sum(len(v) for v in sorted_adj.values())
print(f"build-adjacency-yaml: {skill_count} skills, {edge_count} edges → {OUT_YAML}")
