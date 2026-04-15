---
title: Skill Authoring Family — Release-Ready Certification
date: 2026-04-06
status: draft
spec_required: lite
risk_level: medium
complexity: medium
plan: Docs/plans/2026-04-05-feat-skill-authoring-family-gold-standard-upgrade-plan.md
---

# Skill Authoring Family — Release-Ready Certification

## Table of Contents
- [Problem Frame](#problem-frame)
- [Key Insight — Gap Collapse](#key-insight--gap-collapse)
- [Approaches](#approaches)
- [Recommendation](#recommendation)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Scope Boundaries](#scope-boundaries)
- [Risk Register](#risk-register)
- [Resolve Before Planning](#resolve-before-planning)
- [Deferred to Planning](#deferred-to-planning)
- [Next Steps](#next-steps)

## Problem Frame

The skill-authoring family (skill-builder, skill-creator, skill-installer, plugin-creator) has
completed the P0-P3 gold-standard gate upgrade. The validation framework is certified. Three
gaps remain before the family itself can be declared **release-ready**:

| Gap | Symptom | Root cause |
|-----|---------|-----------|
| Telemetry freshness | `TELEMETRY_HEALTH_STALE` blocker in wave-readiness; `wave-0-controls: ready=false` | `daily-skill-health.md` last generated 2026-03-31 (~5 days stale; limit is 24h) |
| Artifact parity 0% | `artifact-parity-manifest.json` shows 85/87 runs `missing_mandatory` | Run directories lack required shadow-cycle output files |
| No release certificate | No `evidence-index.json` from a trusted live eval run | `SKILL_FAMILY_RELEASE_READY=1` gate has never been run |

## Key Insight — Gap Collapse

**Gaps 1 and 2 share the same root cause and the same fix.**

`docs/skill-graphs/telemetry/daily-skill-health.md` is produced by
`Infrastructure/scripts/run_recursive_skill_shadow_cycle.sh`. The same cycle also writes mandatory
artifact files (`capture_record.json`, `events.jsonl`, `evidence_packet.json`,
`iteration_journal.jsonl`, `lesson_candidates.json`, `promotion_decision.json`) into each
`Infrastructure/artifacts/skill-graphs/runs/run_*/` directory.

```
run_recursive_skill_shadow_cycle.sh
  └─► recursive_skill_loop.py         → populates run_*/  (fixes artifact parity)
  └─► build_recursive_skill_shadow_report.py → writes daily-skill-health.md (fixes telemetry)
```

Running the shadow cycle once unblocks both gaps. Gap 3 (release cert) becomes runnable
immediately after.

So the critical path is:

```
Step 1: Run shadow cycle   →   Step 2: Run release-ready family gate
```

## Approaches

### A — Manual one-shot run (recommended for first certification)

Run the shadow cycle locally or in a trusted CI job, then immediately run the family gate in
release-ready mode. Produces the first `evidence-index.json`. Lowest complexity; proves the
pipeline works end-to-end before investing in automation.

**Pros:** Fastest path to certification; no new infra needed; validates the whole pipeline
**Cons:** Telemetry will drift stale again without a recurring schedule; relies on manual trigger

### B — Automate the shadow cycle on a daily schedule

Wire `run_recursive_skill_shadow_cycle.sh` into a scheduled CI job (e.g., GitHub Actions
`schedule: cron`) so telemetry stays fresh and artifact parity is maintained automatically.
Then run the release-ready gate as a separate step.

**Pros:** Prevents future staleness; turns certification into a repeatable, low-effort process
**Cons:** Requires new CI workflow file; `on: schedule` jobs run on `main` only, not branches

### C — Relax the telemetry freshness threshold

Loosen the 24h staleness limit in `validate_skill_graph_profiles.py` to match actual
generation cadence (e.g., 7 days) and waive the artifact parity check.

**Cons:** Weakens the quality gate; masks real operational gaps; not recommended

## Recommendation

**Do A first, then B.** Run the shadow cycle manually to achieve first certification. Then
add a scheduled CI job to keep telemetry fresh so future certification runs are automatic.

This separates "prove it works" (A) from "keep it working" (B) and avoids prematurely
automating a pipeline that hasn't been validated end-to-end.

## Requirements

### R1 — Shadow cycle produces a fresh telemetry artifact

The recursive skill shadow cycle must run successfully and produce a new
`docs/skill-graphs/telemetry/daily-skill-health.md` with a `Generated at` timestamp within
the last 24 hours, containing a parseable window and event-envelope error count.

### R2 — Shadow cycle populates compliant run artifacts

After the cycle runs, `Infrastructure/artifacts/skill-graphs/runs/` must contain at least one run directory
per covered skill with all six mandatory files present:
`capture_record.json`, `events.jsonl`, `evidence_packet.json`, `iteration_journal.jsonl`,
`lesson_candidates.json`, `promotion_decision.json`.

The artifact-parity compliance rate must exceed 0%.

### R3 — Wave-0 controls pass

After R1 and R2 are satisfied, `python3 Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py`
must produce a `wave-readiness.json` with `wave-0-controls.ready: true` and zero
`TELEMETRY_HEALTH_STALE` or `TELEMETRY_WINDOW_MISMATCH` blockers.

### R4 — Release-ready family gate produces evidence-index.json

Running the family gate with:
```bash
SKILL_FAMILY_RELEASE_READY=1 \
SKILL_FAMILY_LIVE_EVALS=1 \
SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 \
bash Infrastructure/scripts/validate_skill_authoring_family.sh
```
must exit 0 and write a valid `evidence-index.json` to
`Infrastructure/artifacts/validation/family-gate/<timestamp>/evidence-index.json`.

The index must contain entries for all four family members with `outcome: passed`.

### R5 — Daily shadow cycle runs on a schedule (Approach B follow-on)

A GitHub Actions workflow (`ci/skill-telemetry.yml` or similar) triggers
`run_recursive_skill_shadow_cycle.sh` daily on `main` via `on: schedule`. The workflow must:
- Use `SKILL_FAMILY_LIVE_EVALS=0` (structural only; no trusted runner required for telemetry)
- Commit the updated `daily-skill-health.md` artifact back to `main`
- Fail the job (not silently pass) if the health file is not updated

## Success Criteria

| Criterion | How to verify |
|-----------|--------------|
| Telemetry fresh | `daily-skill-health.md` Generated at within 24h of current time |
| Wave-0 ready | `wave-readiness.json` → `wave-0-controls.ready: true` |
| Artifact parity > 0% | `artifact-parity-manifest.json` → `compliance_rate > 0.0` |
| Evidence index exists | `Infrastructure/artifacts/validation/family-gate/<ts>/evidence-index.json` exists and all four skills show `outcome: passed` |
| Family gate passes | `bash Infrastructure/scripts/validate_skill_authoring_family.sh` exits 0 in release-ready mode |

## Scope Boundaries

**In scope:**
- Running the shadow cycle to fix telemetry and artifact parity
- Running the family gate in release-ready mode
- Adding a scheduled CI job to maintain telemetry freshness (Approach B follow-on)
- Updating `wave-readiness.json` and `artifact-parity-manifest.json` outputs

**Out of scope:**
- Changes to the validator scripts themselves (gate is already gold standard)
- Skill content changes (skills were uplifted in the prior PR)
- Onboarding wave-1 or wave-2 (dependent on wave-0 clearing first)
- Changing the 24h telemetry freshness threshold

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Shadow cycle Codex runner unavailable or rate-limited | Medium | High | Use `SKILL_FAMILY_CODEX_PROFILE=fast` for cheaper model; retry-limited reruns documented in evidence index |
| Scheduled CI job on `main` triggers on stale branch state | Low | Medium | Pin workflow to `main`; use `actions/checkout@v4` with `persist-credentials: false` |
| Release-ready run takes >60min and times out | Low | Medium | Split smoke and release eval modes; run smoke first, release on success |
| `evidence-index.json` freshness window (7 days) violated before merge | Low | Low | Evidence is produced at certification time; merge promptly after gate passes |

## Resolve Before Planning

None — the approach, scope, and sequencing are clear. Ready to proceed to planning.

## Deferred to Planning

- Exact CI workflow file name and job structure (Approach B)
- Whether to commit `evidence-index.json` to the repo or keep it gitignored
- Whether the scheduled telemetry job should open a PR or commit directly to `main`
- Which `SKILL_FAMILY_CODEX_PROFILE` to use for the trusted live eval run

## Next Steps

Recommended: proceed to `ce-plan` to sequence the two steps (shadow cycle → release gate)
and define the CI workflow structure for Approach B.

---
schema_version: 1
