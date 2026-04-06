#!/usr/bin/env python3
"""
check-see-also.py  —  CI gate: new SKILL.md files in a PR must have a
## See Also table with at least MIN_ENTRIES entries (default: 2).

Usage:
  python3 scripts/check-see-also.py [vault_root] [--changed-files f1 f2 ...]
  python3 scripts/check-see-also.py .                   # scan all, report only
  python3 scripts/check-see-also.py . --changed-files utilities/mcp-builder/SKILL.md

Exit 0 = OK
Exit 1 = one or more new SKILL.md files are missing adequate See Also entries
"""
import pathlib, re, sys, os

ROOT           = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
MIN_ENTRIES    = int(os.environ.get("SEE_ALSO_MIN", "2"))
CHANGED_FLAG   = "--changed-files"
changed_files: list[str] = []
CANONICAL_PREFIXES = (
    "auth/",
    "backend/",
    "frontend/",
    "github/",
    "interview/",
    "personas/",
    "product/",
    "skills-system/",
    "utilities/",
)

if CHANGED_FLAG in sys.argv:
    idx          = sys.argv.index(CHANGED_FLAG)
    changed_files = sys.argv[idx + 1:]

TOPIC_MAPS = {
    "frontend-ui", "backend-platform", "agent-ops",
    "product-strategy", "security-ops", "content-publishing",
    "mobile-native", "index",
}

SA_TABLE_RE = re.compile(
    r"## See Also\s*\n\| Skill \| .+? \|\n\|[-]+\|[-]+\|\n((?:\|.*\|\n?)*)",
    re.DOTALL
)

def see_also_count(path: pathlib.Path) -> int:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    m = SA_TABLE_RE.search(content)
    if not m:
        return 0
    rows = m.group(1).splitlines()
    count = 0
    for row in rows:
        ref = re.search(r"\[\[([^\]]+)\]\]", row)
        if ref and ref.group(1) not in TOPIC_MAPS:
            count += 1
    return count

errors: list[str] = []

def _is_real_skill(path: pathlib.Path) -> bool:
    """Return True only for canonical source skills in the repo."""
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if rel == "SKILL.md":
        return False
    if not any(rel.startswith(prefix) for prefix in CANONICAL_PREFIXES):
        return False
    return True

if not changed_files:
    # Audit mode — scan all, report skills with too-few entries
    poor: list[tuple[str, int]] = []
    seen_real: set[str] = set()
    for md in sorted(ROOT.rglob("SKILL.md")):
        if not _is_real_skill(md):
            continue
        real = str(md.resolve())
        if real in seen_real:
            continue
        seen_real.add(real)
        n = see_also_count(md)
        if n < MIN_ENTRIES:
            poor.append((md.relative_to(ROOT).parent.as_posix(), n))
    if poor:
        print(f"check-see-also: {len(poor)} skill(s) below minimum ({MIN_ENTRIES}):")
        for skill, n in sorted(poor):
            print(f"  ⚠️  {skill}: {n} See Also entries (need ≥{MIN_ENTRIES})")
    else:
        print(f"check-see-also: all skills have ≥{MIN_ENTRIES} See Also entries ✓")
    sys.exit(0)

# CI mode — only check changed files
for f in changed_files:
    p = pathlib.Path(f)
    if p.name != "SKILL.md":
        continue
    if not p.exists():
        continue   # deleted file — skip (hub-stability catches protected deletions)
    if not _is_real_skill(p):
        continue
    skill  = p.relative_to(ROOT).parent.as_posix()
    n      = see_also_count(p)
    if n < MIN_ENTRIES:
        errors.append(
            f"'{skill}' has only {n} See Also entry/entries "
            f"(minimum {MIN_ENTRIES}). Add cross-skill links to ## See Also."
        )

if errors:
    print(f"check-see-also: {len(errors)} error(s)", file=sys.stderr)
    for e in errors:
        print(f"  ERROR: {e}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"check-see-also: OK ({len([f for f in changed_files if f.endswith('SKILL.md')])} SKILL.md file(s) checked — all have ≥{MIN_ENTRIES} See Also entries)")
    sys.exit(0)
