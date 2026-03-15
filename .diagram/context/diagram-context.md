# Diagram Context Pack

**Generated:** 2026-03-15T19:03:34Z  
**Tool:** `@brainwav/diagram v1.0.8` (npx)  
**Manifest:** 10/10 types · 0 placeholders · all gates passed  

> This file is maintained by `scripts/refresh-diagram-context.sh`.  
> Agents: read this before making architecture claims about this repo.

---

## Table of Contents

- [Repository purpose](#repository-purpose)
- [Core components](#core-components)
- [Architecture diagram](#architecture-diagram)
- [Security surface](#security-surface)
- [Auth boundary](#auth-boundary)
- [Dependency graph (key paths)](#dependency-graph-key-paths)
- [Events and queues](#events-and-queues)
- [Quality and risk signals](#quality-and-risk-signals)
- [Refresh instructions](#refresh-instructions)

---

## Repository purpose

A canonical skill library and CI quality system for AI coding agents (Codex, Claude Code, Gemini).
Primary concern: skill authoring, cross-runtime symlink projection, automated quality gates,
and a human-gated recursive improvement loop.

No database, no HTTP server, no client-facing UI. All components are local tooling scripts
(Python/Shell) or Mermaid diagram assets.

---

## Core components

| Component | Location | Role |
|-----------|----------|------|
| `skill_router` | `utilities/skill-builder/scripts/skill_router.py` | Intent-first routing engine; scores queries against catalog |
| `skill_gate` | `utilities/skill-builder/scripts/skill_gate.py` | Tier-1 structure gate; validates SKILL.md schema |
| `openclaw_skill_guard` | `utilities/skill-builder/scripts/openclaw_skill_guard.py` | Readiness + security checks on high-risk skills |
| `recursive_skill_loop` | `utilities/skill-builder/scripts/recursive_skill_loop.py` | Bounded `generate→evaluate→diagnose→improve→re-score` loop |
| `run_skill_genome_loop` | `scripts/run_skill_genome_loop.py` | Nightly candidate generator; kill-switch aware |
| `validate_recursive_promotion` | `utilities/skill-builder/scripts/validate_recursive_promotion.py` | Secret redaction + promotion artifact verifier |
| `refresh_benchmark_policy` | `utilities/skill-builder/scripts/refresh_benchmark_policy.py` | Weekly Context7-backed threshold ratchet |
| `sync_mcp` | `scripts/sync_mcp.py` | Projects Codex MCP config → Antigravity; no browser dep |
| `run_repo_skill_quality` | `utilities/skill-builder/scripts/run_repo_skill_quality.py` | CI quality orchestrator (Tier 1 + optional Tier 2) |
| `record_skill_feedback` | `utilities/skill-builder/scripts/record_skill_feedback.py` | Persists decision feedback; feeds subject scoreboard |

**Routing invariant** (from `.architecture.yml`):  
`skill_router` → `skill_gate` → `openclaw_skill_guard` must remain reachable in that order.

---

## Architecture diagram

```mermaid
graph TD
  subgraph utilities_systematic_debugging["utilities/systematic-debugging"]
    condition_based_waiting_example["condition-based-waiting-example"]
  end
  subgraph utilities_beautiful_mermaid_scripts["utilities/beautiful-mermaid/scripts"]
    render["render"]
    create_html["create-html"]
  end
  subgraph skills_antigravity_workers_mcp_assets["skills-antigravity/workers-mcp/assets"]
    tool_template["tool-template"]
  end
  subgraph utilities_skill_builder_scripts["utilities/skill-builder/scripts"]
    validate_skill_graph_profiles["validate_skill_graph_profiles"]
    validate_recursive_promotion["validate_recursive_promotion"]
    skill_router["skill_router"]
    skill_gate["skill_gate"]
    skill_catalog["skill_catalog"]
    run_skill_evals["run_skill_evals"]
    run_repo_skill_quality["run_repo_skill_quality"]
    router_controls["router_controls"]
    refresh_benchmark_policy["refresh_benchmark_policy"]
    recursive_skill_loop["recursive_skill_loop"]
    record_skill_feedback["record_skill_feedback"]
    openclaw_skill_guard["openclaw_skill_guard"]
  end
  subgraph scripts["scripts"]
    sync_mcp["sync_mcp"]
    skill_spotlight["skill_spotlight"]
    run_skill_genome_loop["run_skill_genome_loop"]
    diagnose_skill["diagnose_skill"]
    docs_lint["docs_lint"]
    build_skill_state_map["build_skill_state_map"]
  end
  skill_router --> skill_gate
  skill_router --> skill_catalog
  skill_router --> router_controls
  skill_router --> openclaw_skill_guard
  run_repo_skill_quality --> skill_gate
  run_repo_skill_quality --> run_skill_evals
  refresh_benchmark_policy --> validate_skill_graph_profiles
```

---

## Security surface

Scripts that accept untrusted input (from `security.mmd`):

```mermaid
flowchart TD
  Untrusted["Untrusted input"]
  Untrusted --> run_skill_genome_loop["run_skill_genome_loop"]
  Untrusted --> docs_lint["docs_lint"]
  Untrusted --> build_skill_state_map["build_skill_state_map"]
  Untrusted --> validate_recursive_promotion["validate_recursive_promotion"]
  Untrusted --> skill_router["skill_router"]
  Untrusted --> verify_recursive_skill_graph_artifacts["verify_recursive_skill_graph_artifacts"]
  Untrusted --> verify_router_schema["verify_router_schema"]
  Untrusted --> verify_skill_catalog_freshness["verify_skill_catalog_freshness"]
  classDef securityNode fill:#dc2626,color:#fff
```

**Not in untrusted surface:** `sync_mcp` — consistent with `.architecture.yml` rule `sync_mcp_isolated`.

---

## Auth boundary

Scripts inside the auth boundary (from `auth.mmd`):

```mermaid
flowchart TD
  Request["Authentication request"]
  Boundary{"Auth Boundary"}
  Request --> Boundary
  Boundary --> skill_router["skill_router"]
  Boundary --> skill_gate["skill_gate"]
  Boundary --> validate_recursive_promotion["validate_recursive_promotion"]
  Boundary --> sync_mcp["sync_mcp"]
  Boundary --> build_skill_state_map["build_skill_state_map"]
  Boundary --> record_skill_feedback["record_skill_feedback"]
  classDef authNode fill:#7c3aed,color:#fff
```

---

## Dependency graph (key paths)

External dependencies confirmed from `dependency.mmd` — **stdlib only at runtime** (no third-party PyPI at import time except `pyyaml` and `tomli`/`tomllib`):

```
skill_router.py
  ├── skill_catalog.py      (loads SKILL.md frontmatter from disk)
  ├── skill_router_schema.py (Candidate + RouterResult dataclasses)
  ├── router_controls.py    (rollout-mode / kill-switch file reads)
  └── openclaw_skill_guard.py
       └── scans .py/.js/.ts/.sh files for readiness/security patterns

recursive_skill_loop.py
  └── artifacts/skill-graphs/runs/<run_id>/
       ├── run.json
       ├── iteration_journal.jsonl
       ├── promotion_decision.json
       └── lesson_candidates.json

refresh_benchmark_policy.py
  └── Context7 (external MCP / urllib — runs only in scheduled CI)

sync_mcp.py
  ├── ~/.codex/config.toml  (source)
  └── ~/.gemini/antigravity/mcp_config.json  (target)
```

One mirror pattern throughout: `frontend/<skill>/` ↔ `skills-antigravity/<skill>/` — these are sync artifacts, not divergence.

---

## Events and queues

Event-driven scripts (from `events.mmd`):

| Script | Trigger mechanism |
|--------|-------------------|
| `run_skill_genome_loop` | JSONL watermark + nightly cron / `just genome-loop` |
| `recursive_skill_loop` | Per-run invocation; writes `iteration_journal.jsonl` |
| `validate_recursive_promotion` | CI PR gate on promotion artifact changes |
| `run_skill_evals` | CI `workflow_dispatch` or manual |
| `skill_router` | Appends to `route-events.jsonl` on each route call |
| `test_skill_router` | Unit tests (pytest) |
| `upgrade_skill` | Manual CLI invocation |

---

## Quality and risk signals

| Signal | Status |
|--------|--------|
| Manifest completeness | ✅ 10/10 types, 0 placeholders |
| `diagram test` (.architecture.yml rules) | ⚠️ Skipped — `./rules` module missing in v1.0.8 |
| External HTTP surface | `refresh_benchmark_policy` only (scheduled CI, not runtime) |
| Supply-chain risk | Low — stdlib-only Python, no third-party runtime imports |
| Mirror fidelity | `frontend/` ↔ `skills-antigravity/` mirrors; verify with `diff -r` periodically |
| `sync_mcp` isolation | ✅ Confirmed isolated from browser subsystem |

**Known gap:** `.architecture.yml` rules (`skill_gate_reachable`, `openclaw_guard_reachable`, `sync_mcp_isolated`, etc.) are not CI-enforced because `diagram test` subcommand is missing in v1.0.8. Manual verification only until the fix lands.

---

## Refresh instructions

The `pnpm exec` path in `refresh-diagram-context.sh` requires a local install.  
Use `npx` as the direct alternative:

```bash
# Regenerate all diagrams
npx --yes @brainwav/diagram all . --output-dir .diagram

# Re-gate artifacts
npx --yes @brainwav/diagram manifest . \
  --manifest-dir .diagram \
  --require-types architecture,dependency,security,auth \
  --fail-on-placeholder

# Commit updated context + diagrams
git add .diagram/
git commit -m "chore: refresh diagram context pack"
```
