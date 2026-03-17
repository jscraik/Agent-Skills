#!/usr/bin/env python3
"""
check-hub-stability.py  —  CI gate: block deletion or rename of SKILL.md files
where the skill's YAML frontmatter includes `stability: stable`.

Usage (CI / pre-commit):
  python3 scripts/check-hub-stability.py <vault_root> [--changed-files file1 file2 ...]

Exit 0 = OK
Exit 1 = a stable skill was deleted or renamed without a deprecation notice
"""
import json, pathlib, re, sys

ROOT          = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
CHANGED_FLAG  = "--changed-files"
changed_files: list[str] = []

if CHANGED_FLAG in sys.argv:
    idx = sys.argv.index(CHANGED_FLAG)
    changed_files = sys.argv[idx + 1:]

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
STABLE_RE      = re.compile(r"^stability\s*:\s*stable\s*$", re.MULTILINE)
DEPRECATION_RE = re.compile(r"(?:deprecated|deprecation|migration)", re.IGNORECASE)

errors: list[str] = []
warnings: list[str] = []

# If no changed files provided, scan all and just report stable skills
if not changed_files:
    stable = []
    seen_real = set()
    for md in sorted(ROOT.rglob("SKILL.md")):
        real = str(md.resolve())
        if real in seen_real:
            continue
        seen_real.add(real)
        content = md.read_text(encoding="utf-8", errors="replace")
        fm = FRONTMATTER_RE.search(content)
        if fm and STABLE_RE.search(fm.group(1)):
            skill = md.parts[-2]
            stable.append(skill)
    print(f"check-hub-stability: {len(stable)} stable skill(s): {', '.join(sorted(stable))}")
    sys.exit(0)

# When checking specific changed files (e.g. in CI diff)
for f in changed_files:
    p = pathlib.Path(f)
    if p.name != "SKILL.md":
        continue
    skill = p.parts[-2] if len(p.parts) >= 2 else str(p)

    if not p.exists():
        # File was deleted — check if it was stable
        # In CI this won't work because the file is gone, so we check the edges JSON
        edges_file = ROOT / "ops/metrics/graph/skill-edges.json"
        if edges_file.exists():
            data = json.loads(edges_file.read_text())
            stable_skills = {n["id"] for n in data.get("nodes", []) if n.get("stability") == "stable"}
            if skill in stable_skills:
                errors.append(
                    f"STABLE SKILL DELETED: '{skill}' is marked stable and was deleted "
                    f"without a deprecation notice. Add a ## Deprecation section to the "
                    f"last committed version before removal."
                )
        continue

    content = p.read_text(encoding="utf-8", errors="replace")
    fm = FRONTMATTER_RE.search(content)
    if not (fm and STABLE_RE.search(fm.group(1))):
        continue

    # Stable skill exists — check it still has name/description intact
    if not re.search(r"^name\s*:", fm.group(1), re.MULTILINE):
        errors.append(f"STABLE SKILL MISSING 'name': {skill}")
    if not re.search(r"^description\s*:", fm.group(1), re.MULTILINE):
        errors.append(f"STABLE SKILL MISSING 'description': {skill}")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"check-hub-stability: OK ({len(changed_files)} changed SKILL.md file(s) checked)")
    sys.exit(0)
