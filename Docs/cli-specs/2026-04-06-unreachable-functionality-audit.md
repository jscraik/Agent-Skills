# Implemented-but-Unreachable Functionality Audit

## Table of Contents

- [1. Dead UI Controls (CLI Arguments Defined but Not Used)](#1-dead-ui-controls-cli-arguments-defined-but-not-used)
  - [Issue: `--dry-run` for `ask skills install`](#issue---dry-run-for-ask-skills-install)
- [2. Orphaned Standalone Scripts (Implemented but No CLI Integration)](#2-orphaned-standalone-scripts-implemented-but-no-cli-integration)
  - [2.1 `Infrastructure/scripts/lifecycle-and-sync/sync_mcp.py`](#21-infrastructurescriptslifecycle-and-syncsync_mcppy)
  - [2.2 `Infrastructure/scripts/lifecycle-and-sync/check-hub-stability.py`](#22-infrastructurescriptslifecycle-and-synccheck-hub-stabilitypy)
  - [2.3 `Infrastructure/scripts/lifecycle-and-sync/skill_router_metrics.py`](#23-infrastructurescriptslifecycle-and-syncskill_router_metricspy)
  - [2.4 `Infrastructure/scripts/lifecycle-and-sync/skill_spotlight.py`](#24-infrastructurescriptslifecycle-and-syncskill_spotlightpy)
  - [2.5 `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py`](#25-infrastructurescriptslifecycle-and-syncrun_skill_genome_looppy)
  - [2.6 Analysis/Build Scripts (No CLI Wiring)](#26-analysisbuild-scripts-no-cli-wiring)
- [3. Unused Error Codes (Defined but Never Emitted)](#3-unused-error-codes-defined-but-never-emitted)
- [4. Partially Implemented Features](#4-partially-implemented-features)
  - [4.1 `ask plugins init` companion folders](#41-ask-plugins-init-companion-folders)
  - [4.2 `ask skills fold` sensitivity parameter](#42-ask-skills-fold-sensitivity-parameter)
  - [4.3 Graph command filters](#43-graph-command-filters)
- [5. Summary Table](#5-summary-table)
- [6. Recommended Priority](#6-recommended-priority)

## 1. Dead UI Controls (CLI Arguments Defined but Not Used)

### Issue: `--dry-run` for `ask skills install`
**Location:** `bin/ask` line 302, 529

**Problem:**
- Argument defined: `skills_install_parser.add_argument("--dry-run", action="store_true", help="Preview installation")`
- NOT passed to function: `install_skill(repo_root, url=args.url, remediate=args.remediate, dest=args.dest)`
- Missing: `dry_run=args.dry_run`

**Wiring Fix:**
```python
# In bin/ask, line 529, change:
result = install_skill(repo_root, url=args.url, remediate=args.remediate, dest=args.dest)
# To:
result = install_skill(repo_root, url=args.url, remediate=args.remediate, dest=args.dest, dry_run=args.dry_run)
```

**Also requires:**
- Update `Infrastructure/scripts/lib/ask/commands/skills.py::install_skill()` signature to accept `dry_run: bool = False`
- Pass `--dry-run` to underlying `install-skill-from-github.py` if it supports it, or implement preview logic

**Verification:**
```bash
./bin/ask skills install https://github.com/user/repo --dry-run
# Should: Show preview without making changes
# Currently: Argument accepted but ignored
```

---

## 2. Orphaned Standalone Scripts (Implemented but No CLI Integration)

### 2.1 `Infrastructure/scripts/lifecycle-and-sync/sync_mcp.py`
**Purpose:** Sync MCP (Model Context Protocol) configuration between Codex and Antigravity
**Lines of Code:** ~150
**Status:** Fully implemented but unreachable

**Wiring Fix:**
```python
# Add to bin/ask:
# 1. New subparser:
# mcp_parser = subparsers.add_parser("mcp", help="MCP configuration sync")
# mcp_subparsers = mcp_parser.add_subparsers(dest="action")
# mcp_sync_parser = mcp_subparsers.add_parser("sync", help="Sync MCP config")
#
# 2. New dispatch:
# elif args.topic == "mcp":
#     if args.action == "sync":
#         result = sync_mcp(repo_root)  # Wrap sync_mcp.py logic
```

**Verification:**
```bash
./bin/ask mcp sync
# Should: Sync MCP configuration between Codex and Antigravity
```

---

### 2.2 `Infrastructure/scripts/lifecycle-and-sync/check-hub-stability.py`
**Purpose:** CI gate to block deletion/rename of stable skills
**Lines of Code:** ~80
**Status:** Implemented, has `--changed-files` flag, not integrated

**Wiring Fix:**
```python
# Add to `ask repo validate` or as new `ask repo check-stability`:
# Option 1: Integrate into validate
# In repo_validate(), add:
# if check_stability:
#     subprocess.run(["python3", "Infrastructure/scripts/lifecycle-and-sync/check-hub-stability.py", str(repo_root)])
#
# Option 2: New command
# repo_subparsers.add_parser("check-stability", help="Check stable skill changes")
```

**Verification:**
```bash
./bin/ask repo check-stability --changed-files file1 file2
# Should: Exit 1 if stable skills deleted/renamed without deprecation
```

---

### 2.3 `Infrastructure/scripts/lifecycle-and-sync/skill_router_metrics.py`
**Purpose:** Router metrics calculation
**Lines of Code:** ~100
**Status:** Standalone script, no CLI integration

**Wiring Fix:**
```python
# Add to ask graph:
# graph_subparsers.add_parser("metrics", help="Show router metrics")
# Dispatch to skill_router_metrics logic
```

---

### 2.4 `Infrastructure/scripts/lifecycle-and-sync/skill_spotlight.py`
**Purpose:** Skill spotlight/reporting
**Lines of Code:** ~80
**Status:** Standalone script, no CLI integration

**Wiring Fix:**
```python
# Add to ask skills or ask graph as "spotlight" or "report" command
```

---

### 2.5 `Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py`
**Purpose:** Run skill genome processing loop
**Lines of Code:** ~150
**Status:** Standalone script, no CLI integration

**Wiring Fix:**
```python
# Add to ask evals:
# evals_subparsers.add_parser("genome", help="Run skill genome loop")
```

---

### 2.6 Analysis/Build Scripts (No CLI Wiring)

| Script | Purpose | Wiring Option |
|--------|---------|---------------|
| `build_learning_posture_pilot_summary.py` | Generate pilot summaries | Add to `ask repo report` |
| `build_skill_state_map.py` | Build state maps | Add to `ask graph state` |
| `review_candidates.py` | Review skill candidates | Add to `ask skills review` |
| `graph-diff.py` | Diff skill graphs | Add to `ask graph diff` |
| `gen-skill-graph.py` | Generate skill graph | Add to `ask graph generate` |
| `compute-edge-weights.py` | Compute edge weights | Add to `ask graph weights` |

---

## 3. Unused Error Codes (Defined but Never Emitted)

### Issue: `ERR_PATH_TRAVERSAL` and `ERR_CONFLICT`
**Location:** `bin/ask` lines 39, 41

**Current State:**
```python
ERROR_MAP = {
    "ERR_PATH_TRAVERSAL": 2,  # Never used
    "ERR_CONFLICT": 4,        # Never used
}
```

**Intended Use:**
- `ERR_PATH_TRAVERSAL`: Should be emitted when path escapes repo root
- `ERR_CONFLICT`: Should be emitted when operations conflict (e.g., sync conflicts)

**Wiring Fix for PATH_TRAVERSAL:**
```python
# In audit_skill() or other path-handling functions:
from pathlib import Path

def safe_resolve_path(repo_root: Path, user_path: str) -> Path:
    resolved = (repo_root / user_path).resolve()
    try:
        resolved.relative_to(repo_root)
        return resolved
    except ValueError:
        raise PathTraversalError(f"Path {user_path} escapes repo root")
```

**Verification:**
```bash
./bin/ask skills audit /etc/passwd
# Should: Exit 2 with ERR_PATH_TRAVERSAL
# Currently: Generic ERR_VALIDATION
```

---

## 4. Partially Implemented Features

### 4.1 `ask plugins init` companion folders
**Working:** `--with-marketplace`, `--with-scripts`, `--with-assets`, `--with-references`, `--with-workflows`
**Verified:** All wired correctly in bin/ask lines 318-326 and dispatched at line 537

### 4.2 `ask skills fold` sensitivity parameter
**Working:** `--sensitivity` argument passed to fold_skills()
**Verified:** Line 535 passes `sensitivity=args.sensitivity`

### 4.3 Graph command filters
**Working:** `--topic-filter`, `--tier`, `--depth`, `--reverse`
**Verified:** All wired in bin/ask lines 341-364 and dispatched lines 547-559

---

## 5. Summary Table

| Category | Count | Items |
|----------|-------|-------|
| Dead UI Controls | 1 | `--dry-run` for install |
| Orphaned Scripts | 9 | sync_mcp, check-hub-stability, skill_router_metrics, skill_spotlight, run_skill_genome_loop, build_*, review_candidates, graph-diff, gen-skill-graph |
| Unused Error Codes | 2 | ERR_PATH_TRAVERSAL, ERR_CONFLICT |
| **Total Issues** | **12** | |

---

## 6. Recommended Priority

### P1 (Fix Immediately)
1. **Remove or wire `--dry-run`** – Currently misleading users

### P2 (Add CLI Integration)
2. **sync_mcp** – High value for MCP users
3. **check-hub-stability** – Important for CI/CD

### P3 (Nice to Have)
4. **skill_router_metrics** – Expose via `ask graph metrics`
5. **skill_spotlight** – Expose via `ask skills spotlight`
6. **Analysis scripts** – Add to `ask repo report` or similar

### P4 (Cleanup)
7. **Remove unused error codes** or implement path traversal checking
