# Skill Genome Loop Runbook

## Overview

The Skill Genome Loop is a nightly batch process that:
1. Ingests run/session artifacts from the recursive skill loop
2. Computes routing confusion and outcome quality signals per skill
3. Emits high-confidence, human-gated draft PR candidates for skill-definition improvements

**Scope**: Trigger rules, reference-path corrections, and metadata consistency updates only.
**Non-goals**: Autonomous merge/apply, code generation, or workflow changes.

---

## Quick Reference

```bash
# Run in dry-run mode (no writes)
python3 scripts/run_skill_genome_loop.py --dry-run

# Run with forced mode (override control file)
python3 scripts/run_skill_genome_loop.py --force-mode active

# View pending candidates (awaiting review)
python3 scripts/review_candidates.py --list

# Interactive review of pending candidates
python3 scripts/review_candidates.py

# Approve/reject specific candidates
python3 scripts/review_candidates.py --approve <candidate_id>
python3 scripts/review_candidates.py --reject <candidate_id>

# Approve all pending (use with caution)
python3 scripts/review_candidates.py --approve-all

# View approved candidates
cat artifacts/skill-graphs/telemetry/candidates.jsonl | jq .

# View rejected candidates
cat artifacts/skill-graphs/telemetry/rejected-candidates.jsonl | jq .

# View processing stats
cat artifacts/skill-graphs/telemetry/skill-genome-processing-stats.json | jq .
```

---

## Control Files

### Kill-Switch (highest priority)

**Location**: `artifacts/skill-graphs/controls/kill-switch.txt`

- **Trigger**: File exists (content ignored)
- **Effect**: Immediately aborts candidate generation
- **When to use**: Security incident, data integrity concern, or emergency stop

```bash
# Activate kill-switch
touch artifacts/skill-graphs/controls/kill-switch.txt

# Deactivate kill-switch
rm artifacts/skill-graphs/controls/kill-switch.txt
```

### Rollback

**Location**: `artifacts/skill-graphs/controls/rollback-required.txt`

- Handled by existing recursive skill loop infrastructure
- Takes precedence over rollout mode

### Rollout Mode

**Location**: `artifacts/skill-graphs/controls/rollout-mode.txt`

Valid values:
- `off` - Skip candidate generation entirely
- `observe_only` - Log candidates but don't emit (default)
- `active` - Emit candidates to JSONL

```bash
# Set to active mode
echo "active" > artifacts/skill-graphs/controls/rollout-mode.txt

# Set to observe_only (default)
echo "observe_only" > artifacts/skill-graphs/controls/rollout-mode.txt

# Disable completely
echo "off" > artifacts/skill-graphs/controls/rollout-mode.txt
```

### Control Hierarchy

```
kill-switch > rollback > rollout-mode > feature-switch
```

---

## Candidate Schema

```json
{
  "schema_version": "1.0",
  "skill_path": "ui-ux-creative-coding",
  "proposed_change_type": "trigger_rule_review",
  "composite_score": 0.84,
  "window_id": "2026-W10",
  "decision_reason": "Routing confusion detected (35%)",
  "candidate_id": "a1b2c3d4e5f6g7h8",
  "window_count": 3,
  "redaction_passed": true,
  "created_at": "2026-03-02T04:30:00Z"
}
```

### Fields

| Field | Description |
|-------|-------------|
| `schema_version` | Schema version (currently "1.0") |
| `skill_path` | Skill identifier being analyzed |
| `proposed_change_type` | Type of change proposal |
| `composite_score` | Confidence score (0.0-1.0, threshold: 0.82) |
| `window_id` | Week window identifier (YYYY-WNN) |
| `decision_reason` | Human-readable rationale |
| `candidate_id` | Deterministic ID for deduplication |
| `window_count` | Number of windows with this signal |
| `redaction_passed` | True if no PII/secrets detected |
| `created_at` | ISO 8601 timestamp |

---

## Confidence Gating

A candidate is "high-confidence" if:
- `composite_score >= 0.82`
- `window_count >= 2` (repeated signal across windows)

Candidates not meeting these thresholds are logged but not emitted.

---

## Redaction Pipeline

All candidates are processed through:

1. **Allowlist filtering** - Only approved fields retained
2. **Pattern scanning** - Detection of:
   - OpenAI keys (`sk-...`)
   - GitHub PATs (`ghp_...`)
   - Slack tokens (`xox...`)
   - SSH private keys
   - AWS access keys
   - Generic API keys/tokens
   - JWTs (`eyJ...`)
   - IP addresses
   - Email addresses
   - Home paths (`/Users/...`, `/home/...`)

3. **Fail-closed semantics** - Candidates with `redaction_passed=false` are never emitted

---

## Reviewer Decision Flow

### Human Review Gate

Candidates are **not** emitted directly to `candidates.jsonl`. Instead, they go through a human review gate:

```
Genome Loop → pending-candidates.jsonl → review_candidates.py → candidates.jsonl
                                            ↓
                                     rejected-candidates.jsonl
```

**Why**: Prevents automated emission of unreviewed skill changes, ensuring human oversight.

### 1. View Pending Candidates

```bash
# List all pending candidates
python3 scripts/review_candidates.py --list

# Output example:
# === Pending Candidates (2) ===
#
# [1] Candidate: ca41c34123dc8295
#     Skill: interview-kernel
#     Score: 0.85
#     Windows: 2
#     Reason: Routing confusion detected (100.0%)
#     Created: 2026-03-02T10:25:06.111815+00:00
```

### 2. Interactive Review

```bash
python3 scripts/review_candidates.py
```

Commands during interactive review:
- `a` - Approve current candidate
- `r` - Reject current candidate
- `s` - Skip (leave pending for later)
- `q` - Quit (remaining stay pending)
- `A` - Approve all remaining
- `R` - Reject all remaining

### 3. Single-Command Actions

```bash
# Approve by ID
python3 scripts/review_candidates.py --approve ca41c34123dc8295

# Reject by ID
python3 scripts/review_candidates.py --reject ca41c34123dc8295

# Approve all pending (use with caution)
python3 scripts/review_candidates.py --approve-all
```

### 4. Review Outcomes

| Action | Destination | Fields Added |
|--------|-------------|--------------|
| Approve | `candidates.jsonl` | `review_status: approved`, `reviewed_at` |
| Reject | `rejected-candidates.jsonl` | `review_status: rejected`, `reviewed_at` |
| Skip | Stays in `pending-candidates.jsonl` | None |

### 5. View Candidates (Legacy)

```bash
# View all candidates
cat artifacts/skill-graphs/telemetry/candidates.jsonl | jq -c .

# Filter by skill
cat artifacts/skill-graphs/telemetry/candidates.jsonl | jq -c 'select(.skill_path | contains("ui-ux"))'

# Filter high confidence
cat artifacts/skill-graphs/telemetry/candidates.jsonl | jq -c 'select(.composite_score >= 0.82)'
```

### 2. Evaluate Candidate

For each candidate:
1. Review `decision_reason` for context
2. Check `composite_score` and `window_count` for confidence
3. Verify `redaction_passed=true`
4. Examine the skill's SKILL.md for proposed change impact

### 3. Decision Options

- **Approve**: Create draft PR with proposed change
- **Reject**: Document rejection reason in PR comments
- **Defer**: Add to backlog for future review

---

## Rollback Procedures

### If Kill-Switch Activated

```bash
# 1. Check kill-switch exists
ls -la artifacts/skill-graphs/controls/kill-switch.txt

# 2. Review recent processing stats
cat artifacts/skill-graphs/telemetry/skill-genome-processing-stats.json | jq .

# 3. After incident resolution, remove kill-switch
rm artifacts/skill-graphs/controls/kill-switch.txt
```

### If Bad Candidates Emitted

```bash
# 1. Activate kill-switch immediately
touch artifacts/skill-graphs/controls/kill-switch.txt

# 2. Review candidates.jsonl for affected entries
cat artifacts/skill-graphs/telemetry/candidates.jsonl | jq .

# 3. Remove bad entries (manual edit)
# 4. Deactivate kill-switch
rm artifacts/skill-graphs/controls/kill-switch.txt
```

---

## Monitoring

### Processing Stats

**Location**: `artifacts/skill-graphs/telemetry/skill-genome-processing-stats.json`

```json
{
  "window_id": "2026-W10",
  "processing_timestamp": "2026-03-02T04:30:00Z",
  "runs_processed": 8,
  "candidates_raw": 15,
  "candidates_high_confidence": 12,
  "candidates_emitted": 10,
  "candidates_written": 10
}
```

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `candidates_raw` | Total candidates before gating | > 100/run |
| `candidates_high_confidence` | Passing confidence gate | < 10% of raw |
| `candidates_written` | Actually emitted | < `candidates_emitted` |
| `redaction_failures` | Candidates blocked by PII | > 0 (investigate) |

---

## Troubleshooting

### "Kill-switch activated" Error

**Cause**: `kill-switch.txt` file exists
**Fix**: Remove file after verifying incident resolved

### "Rollout mode is off" Message

**Cause**: Control file set to `off`
**Fix**: Update rollout-mode.txt to `observe_only` or `active`

### No Candidates Generated

**Causes**:
1. No runs meeting artifact requirements
2. All candidates below confidence threshold
3. Rollout mode is `off` or `observe_only`

**Debug**:
```bash
python3 scripts/run_skill_genome_loop.py --dry-run
```

### Redaction Failures

**Cause**: PII or secrets detected in candidate
**Action**: Review candidate source data for leaked secrets
**Prevention**: Check upstream artifact generation

### No Pending Candidates to Review

**Cause**: Genome loop not run, or all candidates already reviewed
**Fix**:
```bash
# Run genome loop to generate candidates
python3 scripts/run_skill_genome_loop.py --force-mode active

# Check pending
python3 scripts/review_candidates.py --list
```

### Candidate Already Reviewed

**Cause**: Candidate ID already in `candidates.jsonl` or `rejected-candidates.jsonl`
**Fix**: Each candidate can only be reviewed once. Check destination files.

---

## Scheduled Execution

For nightly cron execution:

```bash
# Add to crontab
0 4 * * * cd /path/to/agent-skills && python3 scripts/run_skill_genome_loop.py >> logs/genome-loop.log 2>&1
```

---

## References

- **Plan**: `docs/plans/2026-03-02-feat-skill-genome-loop-draft-pr-copilot-plan.md`
- **Brainstorm**: `docs/brainstorms/2026-03-01-skill-genome-loop-brainstorm.md`
- **Kill-Switch Runbook**: `docs/skill-graphs/runbooks/kill-switch-and-escalation.md`
