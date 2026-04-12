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
import os, pathlib, re, subprocess, sys

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
    "plugins/arscontexta/skills/",
    "plugins/coderabbit/skills/",
    "plugins/harness-engineering/skills/",
    "plugins/plugin-factory/skills/",
    "plugins/skill-factory/skills/",
    "product/",
    "skills-antigravity/",
    "skills-system/",
    "utilities/",
}

TOPIC_MAPS = {
    "frontend-ui", "backend-platform", "agent-ops",
    "product-strategy", "security-ops", "content-publishing",
    "mobile-native", "index",
}

SKILL_REF_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


def normalize_skill_ref(target: str) -> str:
    """Normalize optional namespace-qualified refs (e.g. plugin-factory:plugin-builder)."""
    normalized = target.strip()
    if ":" not in normalized:
        return normalized
    _, suffix = normalized.split(":", 1)
    if SKILL_REF_RE.match(suffix):
        return suffix
    return normalized


def resolve_skill_id(path: pathlib.Path, content: str) -> str:
    frontmatter = FRONTMATTER_RE.match(content)
    if frontmatter:
        for raw_line in frontmatter.group(1).splitlines():
            line = raw_line.strip()
            if not line.startswith("name:"):
                continue
            _, value = line.split(":", 1)
            candidate = value.strip().strip("'\"")
            if SKILL_REF_RE.fullmatch(candidate):
                return candidate
            break
    return path.parts[-2]

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

def iter_skill_md_files(root: pathlib.Path):
    # Prefer tracked files so generated/untracked projections do not skew drift.
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
    content = md.read_text(encoding="utf-8", errors="replace")
    skill = resolve_skill_id(md, content)
    if skill in seen_skills:          # first path wins (same as builder)
        continue
    seen_skills.add(skill)
    sa_block = re.search(r"## See Also\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not sa_block:
        continue
    for row in sa_block.group(1).splitlines():
        m = re.match(r"\|\s*\[\[([^\]]+)\]\]\s*\|", row)
        if m:
            target = normalize_skill_ref(m.group(1))
            if target not in TOPIC_MAPS:
                skill_edges.add((skill, target))

# ── 2. Load adjacency.yaml edges ──────────────────────────────────────────────
yaml_edges: set[tuple] = set()
unknown_targets: set[tuple] = set()
known_skill_refs: set[str] = set()

for md in iter_skill_md_files(ROOT):
    if not is_canonical_skill_md(md):
        continue
    content = md.read_text(encoding="utf-8", errors="replace")
    known_skill_refs.add(normalize_skill_ref(resolve_skill_id(md, content)))

if ADJ_YAML.exists() and HAS_YAML:
    adj = yaml.safe_load(ADJ_YAML.read_text()) or {}
    defined_nodes = {
        normalize_skill_ref(skill) for skill, refs in adj.items()
        if isinstance(refs, dict)
    }
    known_skill_refs.update(defined_nodes)
    for skill, refs in adj.items():
        if not isinstance(refs, dict):
            continue
        skill_ref = normalize_skill_ref(skill)
        for target in refs:
            target_ref = normalize_skill_ref(target)
            if target_ref not in TOPIC_MAPS:
                yaml_edges.add((skill_ref, target_ref))
                if target_ref not in known_skill_refs:
                    unknown_targets.add((skill_ref, target_ref))
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

if unknown_targets:
    print(f"\nUnknown adjacency targets ({len(unknown_targets)}):", file=sys.stderr)
    for frm, to in sorted(unknown_targets)[:20]:
        print(f"  UNKNOWN  {frm} → {to}", file=sys.stderr)
    if len(unknown_targets) > 20:
        print(f"  … and {len(unknown_targets)-20} more", file=sys.stderr)
    sys.exit(1)

if total_drift == 0:
    print("  ✓ adjacency.yaml and SKILL.md See Also are in sync")

if total_drift > THRESHOLD:
    print(f"\nExit 1: drift ({total_drift}) exceeds threshold ({THRESHOLD})", file=sys.stderr)
    sys.exit(1)

sys.exit(0)
