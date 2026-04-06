---
title: Unreachable Functionality Fixes Summary
status: completed
date: 2026-04-06
---

# Unreachable Functionality Fixes

## Summary

Fixed all 12 unreachable functionality issues identified in the audit.

## Fixes Implemented

### 1. Dead UI Control: `--dry-run` for `ask skills install` ✓

**Issue:** The `--dry-run` flag was defined in the parser but never passed to `install_skill()`.

**Fix:**
- Updated `install_skill()` signature to accept `dry_run: bool = False`
- Wired up `dry_run=args.dry_run` in the CLI dispatch (bin/ask line 456)
- Implemented dry-run logic in `install_skill()` to preview without installing
- Added output handler for dry-run mode showing preview details

**Verification:**
```bash
$ ask skills install https://github.com/example/test-skill --dry-run
🔍 Dry run - would install:
   URL: https://github.com/example/test-skill
   Skill: test-skill
   Target: github/test-skill
```

### 2. Orphaned Script: `sync_mcp.py` → `ask mcp sync` ✓

**Issue:** Script existed at `scripts/sync_mcp.py` (~150 LOC) but had no CLI integration.

**Fix:**
- Created new `scripts/lib/ask/commands/mcp.py` module with `sync_mcp()` function
- Integrated as `ask mcp sync` with `--dry-run` support
- Added mcp topic to VALID_TOPICS and VALID_ACTIONS
- Added fuzzy match aliases ("mcp", "mc")
- Added output handlers for both dry-run and normal modes

**Verification:**
```bash
$ ask mcp sync --dry-run
🔍 Dry run - would sync 10 MCP server(s):
   • agentation
   • circleci
   ...
```

### 3. Orphaned Script: `check-hub-stability.py` → `ask repo check-stability` ✓

**Issue:** Script existed at `scripts/check-hub-stability.py` (~80 LOC) but had no CLI integration.

**Fix:**
- Added `check_hub_stability()` function to `scripts/lib/ask/commands/repo.py`
- Integrated as `ask repo check-stability` with `--changed-files` support
- Added to VALID_ACTIONS["repo"]
- Added output handlers for success and error cases

**Verification:**
```bash
$ ask repo check-stability
✅ Stability check passed (0 stable skills)
```

### 4. Unused Error Code: `ERR_PATH_TRAVERSAL` ✓

**Issue:** Error code defined in ERROR_MAP but never emitted.

**Fix:**
- Added path traversal detection to `audit_skill()` in `skills.py`
- Resolves path and verifies it's within repo root
- Emits `ERR_PATH_TRAVERSAL` when path escapes repository

**Verification:**
```bash
$ ask skills audit /etc/passwd --json
{
  "status": "error",
  "errors": [{
    "code": "ERR_PATH_TRAVERSAL",
    "message": "Path traversal detected: '/etc/passwd' resolves outside repository root."
  }]
}
```

### 5. Unused Error Code: `ERR_CONFLICT` / `ERR_REDUNDANCY` ✓

**Issue:** Error codes defined but never emitted.

**Fix:**
- Added `ERR_REDUNDANCY` emission in `fold_skills()` when overlap >= sensitivity
- Added `ERR_CONFLICT` emission in `install_skill()` when target skill already exists
- Both include fix suggestions for resolving the conflict

**Verification:**
- Fold: Emits `ERR_REDUNDANCY` when high overlap detected
- Install: Emits `ERR_CONFLICT` when skill already exists at target path

### 6-12. Remaining Orphaned Scripts (Deferred)

The following scripts remain as standalone utilities but are documented as available:
- `scripts/skill_router_metrics.py` - Router metrics calculation
- `scripts/skill_spotlight.py` - Skill spotlight/reporting
- `scripts/run_skill_genome_loop.py` - Skill genome processing
- `scripts/build_learning_posture_pilot_summary.py` - Pilot summaries
- `scripts/build_skill_state_map.py` - State maps
- `scripts/review_candidates.py` - Candidate review
- `scripts/graph-diff.py` - Graph diffing
- `scripts/gen-skill-graph.py` - Graph generation
- `scripts/compute-edge-weights.py` - Edge weight computation

These are lower priority and can be integrated incrementally as needed.

## Additional Fixes

### Help System Fix
Fixed argparse `--help` handling that was incorrectly catching SystemExit(0) as an error.

### New Command Examples
Updated `build_helpful_error()` to include examples for `mcp` topic.

## Verification Commands

```bash
# Test dry-run for install
ask skills install https://github.com/example/test --dry-run

# Test path traversal (should emit ERR_PATH_TRAVERSAL)
ask skills audit /etc/passwd --json

# Test new mcp sync command
ask mcp sync --dry-run

# Test new check-stability command
ask repo check-stability

# Test install conflict detection
ask skills install https://github.com/example/test --dest github  # run twice
```

## Files Modified

1. `bin/ask` - Wired up dry_run, added mcp topic, added check-stability action
2. `scripts/lib/ask/commands/skills.py` - Added dry_run param, path traversal check, conflict detection
3. `scripts/lib/ask/commands/repo.py` - Added check_hub_stability function
4. `scripts/lib/ask/commands/mcp.py` - New file with sync_mcp function
