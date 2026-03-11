# Unreachable Functionality Audit

Generated: 2026-03-11

## Summary

| Category | Count | Files |
|----------|-------|-------|
| Orphaned scripts (root) | 13 | See section 1 |
| Orphaned skill-builder scripts | 10 | See section 2 |
| Dead commands/UI | 3 | See section 3 |
| Partially wired | 4 | See section 4 |

---

## 1. Orphaned Scripts in `scripts/`

These scripts exist but are not referenced in justfile, CI workflows, or other scripts.

### 1.1 `skill_spotlight.py`
**Purpose**: Generate daily "skill spotlight" for health reports—picks skills needing attention based on failed promotions and confusion signals.

**Current state**: Fully implemented but never called.

**Wiring change**:
```bash
# Add to justfile
spotlight:
    python3 scripts/skill_spotlight.py
```

**Verification**:
```bash
just spotlight
# Expected: Outputs markdown with skill spotlight section
```

---

### 1.2 `skill_router_metrics.py`
**Purpose**: Aggregate router telemetry into first-hit and guardrail metrics. Computes override regret rates, correction latency, repeat misroute counts.

**Current state**: CLI tool with argparse, not integrated.

**Wiring change**:
```bash
# Add to justfile (requires events file)
router-metrics events='artifacts/skill-graphs/telemetry/route-events.jsonl':
    python3 scripts/skill_router_metrics.py --events {{events}} --json
```

**Verification**:
```bash
just router-metrics
# Expected: JSON with first_hit_by_actor, override_regret_rate, etc.
```

---

### 1.3 `find_skill_path.py`
**Purpose**: Locate skill directory by name across the categorized folder structure.

**Current state**: Utility script, no callers.

**Wiring change**:
```bash
# Add to justfile
find-skill name:
    python3 scripts/find_skill_path.py --name {{name}}
```

**Verification**:
```bash
just find-skill skill-builder
# Expected: Outputs path to skill directory
```

---

### 1.4 `run_recursive_rollout_drill.sh`
**Purpose**: Execute rollback drill scenarios (kill-switch, rollout modes, rollback-required) for resilience testing.

**Current state**: Complete drill harness, not wired.

**Wiring change**:
```bash
# Add to justfile
rollout-drill:
    bash scripts/run_recursive_rollout_drill.sh
```

**Verification**:
```bash
just rollout-drill
# Expected: Runs drill scenarios, outputs report to artifacts/skill-graphs/pilot/rollback-drill.md
```

---

### 1.5 `run_skill_router_rollback_drill.sh`
**Purpose**: Dedicated drill for router rollback scenarios.

**Current state**: Imports `router_controls` but never executed.

**Wiring change**:
```bash
# Add to justfile
router-rollback-drill:
    bash scripts/run_skill_router_rollback_drill.sh
```

**Verification**:
```bash
just router-rollback-drill
# Expected: Runs router-specific rollback tests
```

---

### 1.6 `bootstrap_recursive_skill_graph_artifacts.py`
**Purpose**: Bootstrap initial skill graph artifact structure for new skills.

**Current state**: Utility for creating skeleton artifacts.

**Wiring change**:
```bash
# Add to justfile
bootstrap-artifacts skill:
    python3 scripts/bootstrap_recursive_skill_graph_artifacts.py --skill {{skill}}
```

**Verification**:
```bash
just bootstrap-artifacts skill-builder
# Expected: Creates skeleton run directories
```

---

### 1.7 `build_learning_posture_pilot_summary.py`
**Purpose**: Generate conformance summary for learning posture pilot.

**Current state**: Builds pilot reports, not wired to automation.

**Wiring change**:
```bash
# Add to justfile
posture-summary:
    python3 scripts/build_learning_posture_pilot_summary.py
```

**Verification**:
```bash
just posture-summary
# Expected: Updates artifacts/skill-graphs/pilot/learning-posture-pilot-conformance-summary.json
```

---

### 1.8 `build_skill_state_map.py`
**Purpose**: Build comprehensive skill state map visualization.

**Current state**: State mapping utility, no callers.

**Wiring change**:
```bash
# Add to justfile
state-map:
    python3 scripts/build_skill_state_map.py --output artifacts/skill-graphs/state-map.json
```

**Verification**:
```bash
just state-map
# Expected: Generates skill state map artifact
```

---

### 1.9 `check-environment.sh`
**Purpose**: Pre-flight environment validation (mise, tools, dependencies).

**Current state**: Environment checker, not in CI or justfile.

**Wiring change**:
```bash
# Add to justfile as first-run check
env-check:
    bash scripts/check-environment.sh
```

**Verification**:
```bash
just env-check
# Expected: Reports environment readiness
```

---

### 1.10 `codex-preflight.sh`
**Purpose**: Codex-specific preflight checks before complex operations.

**Current state**: Referenced only in its own comments.

**Wiring change**:
```bash
# Add to justfile
codex-preflight:
    bash scripts/codex-preflight.sh
```

---

### 1.11 `setup-git-hooks.js`
**Purpose**: Install git hooks for the repository.

**Current state**: Hook installer, not referenced.

**Wiring change**:
```bash
# Add to justfile
install-hooks:
    node scripts/setup-git-hooks.js
```

**Verification**:
```bash
just install-hooks
# Expected: Installs git hooks to .git/hooks/
```

---

### 1.12 `install_cron.sh`
**Purpose**: Install nightly genome loop cron job.

**Current state**: Referenced by no one, though `cron_genome_loop.sh` exists.

**Wiring change**:
```bash
# Add to justfile (already has genome-loop-live but not cron install)
install-cron:
    bash scripts/install_cron.sh
```

**Verification**:
```bash
just install-cron
# Expected: Installs cron entry for nightly runs
```

---

## 2. Orphaned Scripts in `utilities/skill-builder/scripts/`

### 2.1 `skill_subject_scoreboard.py`
**Purpose**: Aggregate skill feedback logs into subject-level scoreboards (by domain: ui, backend, security, etc.).

**Current state**: Full CLI tool with --write-report option, no callers.

**Wiring change**:
```bash
# Add to justfile
subject-scoreboard:
    python3 utilities/skill-builder/scripts/skill_subject_scoreboard.py --write-report
```

**Verification**:
```bash
just subject-scoreboard
# Expected: Outputs scoreboard table and writes to ops/metrics/skill-feedback/reports/subject-scoreboard-latest.md
```

---

### 2.2 `generate_skill_graph_profiles.py`
**Purpose**: Generate skill graph profiles from inventory.

**Current state**: Referenced only in error message from `run_skill_graph_smoke.py`.

**Wiring change**:
```bash
# Add to justfile
generate-profiles:
    python3 utilities/skill-builder/scripts/generate_skill_graph_profiles.py
```

**Verification**:
```bash
just generate-profiles
# Expected: Creates profile-index.json
```

---

### 2.3 `validate_skill_graph_profiles.py`
**Purpose**: Validate generated skill graph profiles.

**Current state**: Referenced only in error messages, not called proactively.

**Wiring change**:
```bash
# Add to justfile
validate-profiles:
    python3 utilities/skill-builder/scripts/validate_skill_graph_profiles.py
```

---

### 2.4 `upgrade_skill.py`
**Purpose**: Upgrade skill from one version to another (schema migrations).

**Current state**: Migration utility, not wired.

**Wiring change**:
```bash
# Add to justfile
upgrade-skill skill from to:
    python3 utilities/skill-builder/scripts/upgrade_skill.py --skill {{skill}} --from {{from}} --to {{to}}
```

---

### 2.5 `migrate_evals_v2.py`
**Purpose**: Migrate evals from v1 to v2 format.

**Current state**: Migration script for eval format upgrades.

**Wiring change**:
```bash
# Add to justfile (one-time use)
migrate-evals:
    python3 utilities/skill-builder/scripts/migrate_evals_v2.py
```

---

### 2.6 `record_skill_feedback.py`
**Purpose**: Record structured feedback about skill performance.

**Current state**: Feedback recording utility, no integration.

**Wiring change**:
```bash
# Add to justfile
record-feedback skill outcome note:
    python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill {{skill}} --outcome {{outcome}} --note "{{note}}"
```

---

### 2.7 `openclaw_skill_guard.py`
**Purpose**: Policy guard for skill routing decisions (OpenClaw pattern).

**Current state**: Has tests, not integrated into router.

**Wiring change**:
```bash
# Import in skill_router.py (already has test coverage)
# Add guard check before route decision
```

**Code change**:
```python
# In skill_router.py, add import:
from openclaw_skill_guard import evaluate_guardrails

# In main(), before returning route result:
violations = evaluate_guardabilities(query, top_candidates)
if violations:
    return blocked_result(violations)
```

---

## 3. Dead Commands/UI Controls

### 3.1 `genome-loop-live` justfile target
**Status**: Exists but documented as "live" yet still dry-run.

**Issue**: Both `genome-loop` and `genome-loop-live` may have same behavior.

**Verification**:
```bash
# Check current implementation
just genome-loop-live --help 2>&1 | head -5
```

**Fix**: Ensure `genome-loop-live` actually runs live (removes --dry-run).

---

### 3.2 `check_watch_mode_readiness.py` CLI
**Purpose**: Deterministic watch-mode readiness checker for Agentation.

**Current state**: Referenced in SKILL.md docs only, not in justfile.

**Wiring change**:
```bash
# Add to frontend/tools/agentation justfile or root justfile
watch-readiness project-root:
    python3 frontend/tools/agentation/scripts/check_watch_mode_readiness.py \
      --project-root {{project-root}} \
      --format json
```

---

## 4. Partially Wired (Referenced but not fully integrated)

### 4.1 `cron_genome_loop.sh`
**Status**: Referenced by `install_cron.sh`, but `install_cron.sh` not in justfile.

**Fix**: Add `install-cron` to justfile (see 1.12).

---

### 4.2 `skill_router_schema.py`
**Status**: Imported by `skill_router.py` and `verify_router_schema.py`, but validation not enforced in router.

**Gap**: `validate_router_result()` function exists but results not used to block invalid routes.

**Fix**: Add validation call in skill_router.py main():
```python
result = build_router_result(...)
errors = validate_router_result(result, fail_on_sensitive_fields=True)
if errors:
    return error_response(errors)
```

---

### 4.3 `router_controls.py`
**Status**: Imported by skill_router.py and rollback drill, but rollout mode enforcement limited.

**Gap**: `resolve_rollout_mode()` used, but control file watching not continuous.

**Fix**: Add control file polling in recursive_skill_loop.py or document in justfile.

---

### 4.4 `test_*` files for orphaned modules
**Files**: `test_bootstrap_recursive_skill_graph_artifacts.py`, `test_validate_recursive_promotions_script.py`, `test_verify_recursive_skill_graph_artifacts.py`

**Status**: Tests exist for orphaned scripts, but tests not run in CI.

**Fix**: Add to CI or justfile:
```bash
# Add to justfile
test-scripts:
    python3 -m pytest scripts/test_*.py -v
```

---

## 5. Quick-Fix Priority List

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 1 | Add `just spotlight` | 1 min | Daily visibility into skill health |
| 2 | Add `just subject-scoreboard` | 1 min | Subject-level quality metrics |
| 3 | Add `just rollout-drill` | 1 min | Resilience testing |
| 4 | Add `just install-cron` | 1 min | Nightly automation setup |
| 5 | Fix `genome-loop-live` dry-run | 2 min | Live loop actually runs live |
| 6 | Wire `openclaw_skill_guard` | 10 min | Policy enforcement in router |

---

## Appendix: Verification Commands

```bash
# Count total scripts vs referenced
ls scripts/*.py scripts/*.sh 2>/dev/null | wc -l
grep -oE 'scripts/[a-zA-Z0-9_-]+\.(py|sh)' justfile | wc -l

# Find unreferenced scripts (run from repo root)
grep -r "skill_spotlight" . --include="*.py" --include="*.sh" --include="*.yml" 2>/dev/null
# Should return nothing = orphaned

# Check justfile syntax after edits
just --list
```
