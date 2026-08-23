# Event Capture Fix Documentation

## Issue

Historical runs (2026-02-20) were missing `events.jsonl` files, preventing proper telemetry analysis.

## Root Cause

The `recursive_skill_loop.py` script initially didn't write `events.jsonl` files. Event writing was added in a later version, but historical runs created before that change were missing the files.

## Solution

### 1. Backfill Script

Created `Skills/skill-builder/Infrastructure/scripts/backfill_missing_events.py` to reconstruct minimal events from `run.json` metadata:

**Features:**

- Reconstructs 3 event types: `run_initialized`, `run_state_changed`, and `failure_event` (for failed runs)
- Preserves historical timestamps and metadata
- Validates all runs have complete event telemetry
- Can be run idempotently (skips runs that already have events)

**Usage:**

```bash
# Dry run
python3 Skills/skill-builder/Infrastructure/scripts/backfill_missing_events.py --dry-run --verbose

# Apply backfill
python3 Skills/skill-builder/Infrastructure/scripts/backfill_missing_events.py --verbose

# Verify all runs have events
python3 Skills/skill-builder/Infrastructure/scripts/backfill_missing_events.py
```

### 2. Validation Tests

Created `Skills/skill-builder/Infrastructure/scripts/test_events_jsonl_required.py` to ensure:

- `events.jsonl` is in `RUN_REQUIRED_FILES`
- All runs have `events.jsonl` files
- Files have valid JSON Lines format
- Event types are recognized

**Usage:**

```bash
pytest Skills/skill-builder/Infrastructure/scripts/test_events_jsonl_required.py -v
```

## Results

**Before Fix:**

```
Event envelope errors: 7
- run_20260220T195545Z_8799c2: missing events.jsonl
- run_20260220T150021Z_82ecf7: missing events.jsonl
- run_20260220T150021Z_9b592b: missing events.jsonl
- run_20260220T150021Z_bb9acb: missing events.jsonl
- run_20260220T144736Z_425b7a: missing events.jsonl
- run_20260220T144710Z_425b7a: missing events.jsonl
- run_20260220T144703Z_425b7a: missing events.jsonl
```

**After Fix:**

```
Event envelope errors: 0
All runs have events.jsonl ✓
```

## Prevention

### Going Forward

1. **Validation**: The `validate_recursive_promotion.py` script already checks for `events.jsonl` as a required file
2. **Tests**: Run `test_events_jsonl_required.py` to catch missing events early
3. **CI Integration**: Add to CI pipeline to prevent regressions

### Monitoring

Regenerate telemetry reports after any batch of runs:

```bash
python3 Skills/skill-builder/Infrastructure/scripts/build_recursive_skill_shadow_report.py \
  --runs-root .tmp/agent-skills-artifacts/skill-graphs/runs \
  --window-days 7
```

Check `.harness/evidence/skill-graphs/telemetry/daily-skill-health.md` for:
- Event envelope errors should be 0
- Capture coverage should be 100%

## Event Schema

Events are JSON Lines with the following structure:

```json
{
  "schema_version": "1.0",
  "event_id": "<hash>",
  "ts": "<ISO8601 timestamp>",
  "run_id": "<run identifier>",
  "skill_name": "<skill name>",
  "task_profile": "<profile id>",
  "event_type": "<run_initialized|run_state_changed|run_blocked|failure_event|promotion_approved>",
  "severity": "<info|warn|fail>",
  "terminal_status": "<passed|failed|escalated|aborted|null>",
  "stop_reason": "<pass|budget_exhausted|escalated|aborted|policy_failed|evaluator_conflict|dependency_missing|null>",
  "actor_id": "<actor identifier>",
  "evaluator_version": "<version>",
  "rubric_version": "<version>",
  "prompt_hash": "<sha256 hash>"
}
```

## Files Modified

1. `Skills/skill-builder/Infrastructure/scripts/backfill_missing_events.py` - New
2. `Skills/skill-builder/Infrastructure/scripts/test_events_jsonl_required.py` - New
3. `.tmp/agent-skills-artifacts/skill-graphs/runs/run_20260220*/events.jsonl` - Backfilled (8 files)

## References

- [Skill Knowledge Graph Operating Model](/docs/skill-graphs/knowledge-graph-operating-model.md)
- Generated daily-health telemetry: `.harness/evidence/skill-graphs/telemetry/daily-skill-health.md`
- [Recursive Skill Loop Script](/Skills/skill-builder/Infrastructure/scripts/recursive_skill_loop.py)
