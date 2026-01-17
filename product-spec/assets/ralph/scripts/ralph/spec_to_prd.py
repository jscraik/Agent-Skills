#!/usr/bin/env python3
"""
spec_to_prd.py — Compile a .spec/spec-*.md into prd.json (Ralph loop execution state).

Design goals:
- Deterministic, testable transformation (no agent reasoning).
- Stable story IDs: STORY-001, STORY-002, ...
- Preserve execution state across recompiles (status/passes/attempts/timestamps/errors).
- Fail fast on malformed specs when --strict is enabled.

Usage:
  python3 scripts/ralph/spec_to_prd.py --spec .spec/spec-2026-01-13-foo.md --out prd.json

Optional:
  --branch <name>         (defaults to current git branch if available)
  --project <name>        (defaults to PRD title in spec)
  --existing prd.json     (defaults to --out if present)
  --stale-seconds 7200    (used only for validation metadata; loop uses this separately)
  --final-test "cmd"      (repeatable)
  --strict                (reject missing/empty required fields)

Spec contract (PRD section):
- Project name from: "# PRD: <name>"
- Story headers (either):
  A) "1) **Story [STORY-001]:** As a ..., I want ... so that ..."
  B) "### STORY-001 — As a ..., I want ... so that ..."
- Priority line: "**Priority:** Must | Should | Could"  (maps to 0/1/2)
- Acceptance criteria block:
    **Acceptance criteria:**
    - [ ] ...
    - [ ] ...
- Optional tests block per story:
    **Tests:**
    - ...
"""

from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STORY_ID_RE = re.compile(r"\b(STORY-\d{3,})\b")
PRD_TITLE_RE = re.compile(r"^\s*#\s*PRD:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# Story header formats
STORY_HDR_A_RE = re.compile(
    r"^\s*\d+\)\s*\*\*Story\s*\[?(STORY-\d{3,})\]?\s*:\*\*\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
STORY_HDR_B_RE = re.compile(
    r"^\s*###\s*(STORY-\d{3,})\s*[—-]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

PRIORITY_RE = re.compile(r"^\s*\*\*Priority:\*\*\s*(Must|Should|Could)\s*$", re.IGNORECASE | re.MULTILINE)
AC_HEADER_RE = re.compile(r"^\s*\*\*Acceptance criteria:\*\*\s*$", re.IGNORECASE | re.MULTILINE)
TESTS_HEADER_RE = re.compile(r"^\s*\*\*Tests:\*\*\s*$", re.IGNORECASE | re.MULTILINE)

CHECKBOX_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$")

PRIORITY_MAP = {"must": 0, "should": 1, "could": 2}

PRESERVE_FIELDS = ["status", "passes", "startedAt", "completedAt", "attempts", "lastError"]

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def git_branch() -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL)
        b = out.decode("utf-8", "replace").strip()
        if b:
            return b
    except Exception:
        return None
    return None

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

def split_story_blocks(md: str) -> List[Tuple[str, str, int, int]]:
    """
    Returns list of (story_id, title, start_idx, end_idx)
    where end_idx is exclusive.
    Supports two header formats; if both match, we take the earliest occurrences.
    """
    matches: List[Tuple[int, str, str]] = []
    for m in STORY_HDR_A_RE.finditer(md):
        matches.append((m.start(), m.group(1), m.group(2).strip()))
    for m in STORY_HDR_B_RE.finditer(md):
        matches.append((m.start(), m.group(1), m.group(2).strip()))
    matches.sort(key=lambda t: t[0])

    blocks: List[Tuple[str, str, int, int]] = []
    for i, (start, sid, title) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(md)
        blocks.append((sid, title, start, end))
    return blocks

def parse_block(md_block: str, strict: bool) -> Tuple[int, List[str], List[str]]:
    # Priority
    pr = PRIORITY_RE.search(md_block)
    if pr:
        pr_val = PRIORITY_MAP[pr.group(1).lower()]
    else:
        pr_val = 1  # default Should
        if strict:
            raise ValueError("Missing **Priority:** Must|Should|Could in story block")

    # Acceptance criteria: capture checkbox bullets after the AC header until blank or next bold header.
    ac: List[str] = []
    ac_hdr = AC_HEADER_RE.search(md_block)
    if ac_hdr:
        tail = md_block[ac_hdr.end():]
        for line in tail.splitlines():
            # stop when we hit another bold header
            if line.strip().startswith("**") and line.strip().endswith("**"):
                break
            if not line.strip():
                # allow blank lines but don't stop immediately; keep scanning
                continue
            m = CHECKBOX_RE.match(line)
            if m:
                ac.append(m.group(2).strip())
    elif strict:
        raise ValueError("Missing **Acceptance criteria:** section in story block")

    if strict and len(ac) == 0:
        raise ValueError("Acceptance criteria section present but no '- [ ] ...' lines found")

    # Tests: optional bullets after **Tests:**
    tests: List[str] = []
    th = TESTS_HEADER_RE.search(md_block)
    if th:
        tail = md_block[th.end():]
        for line in tail.splitlines():
            if line.strip().startswith("**") and line.strip().endswith("**"):
                break
            if not line.strip():
                continue
            bm = BULLET_RE.match(line)
            if bm:
                tests.append(bm.group(1).strip())

    return pr_val, ac, tests

def ensure_story_id_unique(stories: List[Dict[str, Any]]):
    seen = set()
    for s in stories:
        sid = s["id"]
        if sid in seen:
            raise ValueError(f"Duplicate story id detected: {sid}")
        seen.add(sid)

def compile_prd(spec_path: Path, out_path: Path, existing_path: Optional[Path], branch: str,
                project_override: Optional[str], final_tests: List[str], strict: bool,
                keep_removed: bool) -> Dict[str, Any]:
    md = read_text(spec_path)

    # Project name
    m = PRD_TITLE_RE.search(md)
    project = (m.group(1).strip() if m else None)
    if project_override:
        project = project_override.strip()
    if strict and not project:
        raise ValueError('Missing "# PRD: <Product / Feature Name>" heading in spec')

    # Stories
    blocks = split_story_blocks(md)
    if strict and len(blocks) == 0:
        raise ValueError("No stories found. Use Story header format with STORY-###.")

    compiled: List[Dict[str, Any]] = []
    for sid, title, start, end in blocks:
        block_text = md[start:end]
        pr_val, ac, tests = parse_block(block_text, strict=strict)

        compiled.append({
            "id": sid,
            "title": title,
            "priority": pr_val,
            "acceptanceCriteria": ac,
            "tests": tests,
            # state fields defaulted here; may be overwritten by merge
            "status": "open",
            "passes": False,
            "startedAt": None,
            "completedAt": None,
            "attempts": 0,
            "lastError": None
        })

    ensure_story_id_unique(compiled)

    # Load existing and merge state
    existing: Optional[Dict[str, Any]] = None
    if existing_path:
        existing = load_json_if_exists(existing_path)
    elif out_path.exists():
        existing = load_json_if_exists(out_path)

    existing_map: Dict[str, Dict[str, Any]] = {}
    if existing and isinstance(existing.get("userStories"), list):
        for s in existing["userStories"]:
            if isinstance(s, dict) and "id" in s:
                existing_map[str(s["id"])] = s

    for s in compiled:
        prior = existing_map.get(s["id"])
        if prior:
            for f in PRESERVE_FIELDS:
                if f in prior:
                    s[f] = prior[f]

    # Keep removed stories (present in old prd, absent in spec)
    removed: List[Dict[str, Any]] = []
    if keep_removed and existing_map:
        compiled_ids = {s["id"] for s in compiled}
        for sid, prior in existing_map.items():
            if sid not in compiled_ids:
                r = dict(prior)
                r.setdefault("id", sid)
                r["status"] = "removed"
                removed.append(r)

    user_stories = compiled + removed

    # stable ordering: by priority asc, then numeric part of id
    def story_sort_key(s: Dict[str, Any]):
        pr = int(s.get("priority", 1))
        m = re.search(r"STORY-(\d+)", str(s.get("id", "")))
        n = int(m.group(1)) if m else 10**9
        return (pr, n)

    user_stories.sort(key=story_sort_key)

    prd: Dict[str, Any] = {
        "projectName": project or "UNKNOWN",
        "branchName": branch,
        "specRef": str(spec_path),
        "generatedAt": iso_now(),
        "finalTests": final_tests,
        "userStories": user_stories
    }

    # Preserve top-level fields from existing if present (non-conflicting)
    if existing:
        for k in ["projectName", "finalTests"]:
            if k in existing and k not in prd:
                prd[k] = existing[k]
        # If existing had finalTests and caller didn't pass any, keep existing
        if (not final_tests) and isinstance(existing.get("finalTests"), list):
            prd["finalTests"] = existing["finalTests"]

    return prd

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to .spec/spec-*.md")
    ap.add_argument("--out", default="prd.json", help="Output path for prd.json (default: prd.json)")
    ap.add_argument("--existing", default=None, help="Existing prd.json to merge state from (default: --out if exists)")
    ap.add_argument("--branch", default=None, help="Branch name (default: current git branch)")
    ap.add_argument("--project", default=None, help="Override projectName")
    ap.add_argument("--final-test", action="append", default=[], help="Repeatable final test command")
    ap.add_argument("--strict", action="store_true", help="Fail fast on missing required fields")
    ap.add_argument("--keep-removed", action="store_true", help="Keep removed stories (status=removed). Default: true")
    ap.add_argument("--no-keep-removed", dest="keep_removed", action="store_false", help="Drop removed stories")
    ap.set_defaults(keep_removed=True)
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    out_path = Path(args.out).resolve()
    existing_path = Path(args.existing).resolve() if args.existing else None

    if not spec_path.exists():
        raise SystemExit(f"Spec not found: {spec_path}")

    branch = args.branch or git_branch() or "unknown-branch"
    prd = compile_prd(
        spec_path=spec_path,
        out_path=out_path,
        existing_path=existing_path,
        branch=branch,
        project_override=args.project,
        final_tests=args.final_test,
        strict=args.strict,
        keep_removed=args.keep_removed,
    )

    out_path.write_text(json.dumps(prd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} (stories: {len(prd['userStories'])})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
