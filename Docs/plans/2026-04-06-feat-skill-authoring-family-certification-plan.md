---
plan_id: ASK-SKILL-AUTHORING-CERT-20260406
title: Skill Authoring Family — Release-Ready Certification
date: 2026-04-06
status: active
type: feat
origin: docs/brainstorms/2026-04-06-skill-authoring-family-certification-requirements.md
risk_level: medium
complexity: medium
---

# Skill Authoring Family — Release-Ready Certification Plan

## Table of Contents

- [Problem Frame](#problem-frame)
- [Root Cause Diagnosis](#root-cause-diagnosis)
- [Scope Boundaries](#scope-boundaries)
- [Critical Path](#critical-path)
- [Implementation Phases](#implementation-phases)
- [Task Graph (id and depends_on)](#task-graph-id-and-depends_on)
- [Acceptance Criteria](#acceptance-criteria)
- [Execution Ledger](#execution-ledger)
- [Risks](#risks)

## Problem Frame

Three gaps block release-ready certification of the skill-authoring family
(skill-builder, skill-creator, skill-installer, plugin-creator) after the P0-P3
gold-standard gate upgrade:

| Gap                 | Current state                                                | Required state                                         |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| Telemetry freshness | `TELEMETRY_HEALTH_STALE`: generated 2026-03-31 (~5 days ago) | `daily-skill-health.md` Generated at < 24h             |
| Artifact parity     | 0% compliant (85/87 `missing_mandatory`)                     | compliance_rate > 0%                                   |
| Release certificate | No `evidence-index.json` exists                              | Gate exits 0; index has all 4 skills `outcome: passed` |

Gaps 1 and 2 share a root cause and a single fix (see below).

## Root Cause Diagnosis

The shadow cycle CI workflow (`.github/workflows/recursive-skill-shadow.yml`) has two bugs:

1. **Weekly schedule vs 24h threshold** — cron runs every Monday (`0 13 * * 1`), but
   `validate_skill_graph_profiles.py` treats telemetry as stale after 24h. The artifact
   is always stale within hours of the Monday run.

2. **No write-back** — the workflow has `permissions: contents: read`. It uploads
   `daily-skill-health.md` to GitHub Actions artifact storage but never commits it back
   to the repo. The in-repo file never updates.

`recursive_skill_loop.py` makes zero external API calls — the cycle is fully deterministic
and needs no credentials or model access.

## Scope Boundaries

**In scope:**

- Fix shadow cycle workflow: daily schedule + `contents: write` + commit-back step
- Manual one-shot shadow cycle run to generate fresh telemetry and run artifacts
- Regenerate `wave-readiness.json` to verify `wave-0-controls.ready: true`
- Regenerate `artifact-parity-manifest.json` to verify compliance_rate > 0%
- Run release-ready family gate; verify `evidence-index.json` produced
- Commit updated artifacts + CI fix as a PR

**Out of scope:**

- Changes to validator scripts
- Skill content changes
- Wave-1 / wave-2 onboarding
- Changing the 24h telemetry freshness threshold

## Critical Path

```text
P0 (CI fix) ──► P1 (shadow run) ──► P2 (wave-0 verify) ──► P3 (release gate)
                     │
                     └──► also produces run artifacts (fixes parity — no separate step needed)
```

P0 can be written now; P1–P3 execute sequentially after P0's CI change lands (or locally).

## Implementation Phases

---

### P0 — Fix the shadow cycle CI workflow

**Goal:** Make the shadow cycle run daily and commit generated artifacts back to `main`
so `daily-skill-health.md` is always fresh in the repo.

**File:** `.github/workflows/recursive-skill-shadow.yml`

**Changes:**

1. Change schedule from weekly to daily at 06:00 UTC:

   ```yaml
   schedule:
     - cron: "0 6 * * *"
   ```

2. Upgrade `permissions` to allow write-back:

   ```yaml
   permissions:
     contents: write
   ```

3. Pin third-party actions to full SHA (security baseline — April 2026):
   - `actions/checkout` → pin to commit SHA for v4
   - `actions/setup-python` → pin to commit SHA for v5
   - `actions/upload-artifact` → pin to commit SHA for v4

4. Add commit-back step after shadow cycle run, before artifact upload:

   ```yaml
   - name: Commit telemetry artifacts
     run: |
       git config user.name "github-actions[bot]"
       git config user.email "github-actions[bot]@users.noreply.github.com"
       git add docs/skill-graphs/telemetry/daily-skill-health.md \
               Infrastructure/artifacts/skill-graphs/runs/ \
               Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json \
               Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json \
               Infrastructure/artifacts/skill-graphs/telemetry/ || true
       git diff --cached --quiet || git commit \
         -m "chore(telemetry): daily skill-health refresh [skip ci]"
       git push
   ```

   Note: `[skip ci]` prevents the commit from re-triggering itself. `git diff --cached --quiet || git commit` skips the commit when nothing changed (idempotent).

5. Add a failure guard — fail the job if `daily-skill-health.md` is not updated:
   ```yaml
   - name: Verify telemetry freshness
     run: |
       python3 - <<'PY'
       import json, sys
       from pathlib import Path
       from datetime import datetime, timezone, timedelta
       content = Path("docs/skill-graphs/telemetry/daily-skill-health.md").read_text()
       for line in content.splitlines():
           if line.startswith("- Generated at:"):
               ts = line.split("`")[1].strip()
               generated = datetime.fromisoformat(ts.replace("Z", "+00:00"))
               age = datetime.now(timezone.utc) - generated
               if age > timedelta(hours=24):
                   print(f"FAIL: daily-skill-health.md is {age} old (limit: 24h)", file=sys.stderr)
                   sys.exit(1)
               print(f"OK: telemetry age {age}")
               sys.exit(0)
       print("FAIL: could not parse Generated at timestamp", file=sys.stderr)
       sys.exit(1)
       PY
   ```

**Test scenario:** On next daily trigger, `daily-skill-health.md` in the repo has a
`Generated at` timestamp within 24h of current time. Commit appears in git log with
`[skip ci]` tag. Wave-readiness would pass telemetry check.

**Verification:**

- `git log --oneline -5` — shows telemetry commit
- `head -3 docs/skill-graphs/telemetry/daily-skill-health.md` — shows fresh timestamp
- Job exits 0 in Actions UI

**Execution note:** Write this change first so CI automation handles future runs
after the manual one-shot in P1.

---

### P1 — Run shadow cycle locally (one-shot, manual)

**Goal:** Immediately fix both telemetry freshness and artifact parity without waiting
for the next CI trigger. This is the fastest path to gap closure.

**Commands (run from repo root):**

```bash
# 1. Run the shadow cycle
bash Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle.sh \
  --runs-per-profile 2 \
  --window-days 7

# 2. Regenerate wave-readiness (the shadow report script updates telemetry; the
#    profile validator regenerates wave-readiness.json)
python3 Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py \
  --wave-readiness-out Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json

# 3. Regenerate artifact-parity-manifest
python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py \
  --runs-root Infrastructure/artifacts/skill-graphs/runs \
  --manifest Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json
```

**Files produced / updated:**

- `docs/skill-graphs/telemetry/daily-skill-health.md` — fresh Generated at timestamp
- `Infrastructure/artifacts/skill-graphs/runs/run_*/` — populated with mandatory files
- `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json` — wave-0 re-evaluated
- `Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json` — parity re-evaluated

**Test scenarios:**

- Shadow cycle exits 0
- `daily-skill-health.md` Generated at is within 24h of now
- At least one `run_*/` directory contains all six mandatory files
- `artifact-parity-manifest.json` compliance_rate > 0.0

**Verification:**

```bash
# Telemetry fresh
head -3 docs/skill-graphs/telemetry/daily-skill-health.md

# Wave-0 clear
python3 -c "
import json
wr = json.loads(open('Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json').read())
w0 = wr['waves']['wave-0-controls']
print('wave-0 ready:', w0['ready'])
print('blockers:', w0.get('blockers', []))
"

# Parity improved
python3 -c "
import json
m = json.loads(open('Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json').read())
print('compliance_rate:', m['compliance_rate'])
print('compliant:', m['counts']['compliant'])
"
```

**Execution note:** This is a local run using the deterministic scaffold — no model
credentials required.

---

### P2 — Verify wave-0-controls passes

**Goal:** Confirm `wave-0-controls.ready: true` before running the release-ready gate.
This is a checkpoint gate, not a separate fix.

**Check command:**

```bash
python3 -c "
import json, sys
wr = json.loads(open('Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json').read())
w0 = wr['waves']['wave-0-controls']
if not w0['ready']:
    print('BLOCKED — wave-0 not ready:', json.dumps(w0['blockers'], indent=2))
    sys.exit(1)
print('PASS — wave-0-controls ready')
"
```

**If wave-0 is still blocked:** Diagnose the remaining blockers before proceeding to P3.
Common cause: `TELEMETRY_WINDOW_MISMATCH` — the health file window doesn't overlap the
expected date range. If this persists after P1, re-run with `--window-days 14`.

**Acceptance:** Script exits 0 with `PASS — wave-0-controls ready`.

---

### P3 — Run release-ready family gate

**Goal:** Run the family gate in full release-ready mode to produce the first
`evidence-index.json` certifying all four skill-authoring family members.

**Command:**

```bash
SKILL_FAMILY_RELEASE_READY=1 \
SKILL_FAMILY_LIVE_EVALS=1 \
SKILL_FAMILY_LIVE_EVALS_TRUSTED=1 \
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

**Expected output:**

- `[family-gate] release-ready mode: evidence will be captured at Infrastructure/artifacts/validation/family-gate/<timestamp>/`
- Per-skill: `[family-gate] contract/eval/security benchmarks passed: <skill>`
- `[family-gate] pass (release-ready): all authoring-family skills met trusted live eval/security benchmarks`
- `[family-gate] evidence artifacts: Infrastructure/artifacts/validation/family-gate/<timestamp>/`

**Verify evidence index:**

```bash
EVIDENCE=$(ls -d Infrastructure/artifacts/validation/family-gate/*/  | sort | tail -1)
python3 -c "
import json, sys
idx = json.loads(open('${EVIDENCE}/evidence-index.json').read())
skills = idx['skill_coverage']
failed = [s for s in skills if s['outcome'] != 'passed']
if failed:
    print('FAIL:', failed); sys.exit(1)
print('PASS — all', len(skills), 'skills certified')
print('branch:', idx['branch'], 'sha:', idx['commit_sha'])
"
```

**Files produced:**

- `Infrastructure/artifacts/validation/family-gate/<timestamp>/evidence-index.json`
- Per-skill eval reports under `Infrastructure/artifacts/validation/family-gate/<timestamp>/<skill-slug>/`

Note: `Infrastructure/artifacts/validation/family-gate/` is gitignored. Evidence stays local/CI-only
by design — the gate exit code is the repo-visible certification signal.

**Fallback if gate fails mid-run:**

- If one skill fails, fix the specific contract/eval finding and re-run only that skill
  using `quick_validate.py <skill_dir> --mode compat`
- Retry the full release-ready gate after fixing

---

### P4 — Commit artifacts and open PR

**Goal:** Land the CI workflow fix and the updated artifacts (fresh telemetry, run
artifacts, parity manifest, wave-readiness) in a PR so CI automation takes over.

**Files to commit:**

```text
.github/workflows/recursive-skill-shadow.yml   # daily schedule + write-back
docs/skill-graphs/telemetry/daily-skill-health.md
Infrastructure/artifacts/skill-graphs/runs/                   # new compliant run dirs
Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json
Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json
```

**Do NOT commit:**

- `Infrastructure/artifacts/validation/family-gate/` — gitignored (eval run outputs with absolute paths)

**Commit strategy:** Two logical commits:

1. `fix(ci): run shadow cycle daily and commit telemetry write-back` — CI workflow only
2. `chore(telemetry): first certified telemetry refresh and wave-0 clearance` — artifacts

**PR checklist:**

- [ ] AC1 — `daily-skill-health.md` Generated at < 24h at time of push (AC1)
- [ ] AC2 — `wave-readiness.json` `wave-0-controls.ready: true` (AC2)
- [ ] AC3 — `artifact-parity-manifest.json` compliance_rate > 0.0 (AC3)
- [ ] AC4 — Shadow cycle CI job passes in PR checks (AC4)
- [ ] AC5 — `validate_skill_authoring_family.sh` exits 0 in structural mode in PR checks (AC5)
- [ ] AI artifact governance: save session summary to `Infrastructure/artifacts/ai/sessions/2026-04-06-skill-authoring-family-certification.json`

## Task Graph (id and depends_on)

```yaml
tasks:
  - id: P0
    title: Fix shadow-cycle workflow schedule, permissions, and telemetry write-back.
    depends_on: []
  - id: P1
    title: Run one-shot local shadow cycle to refresh telemetry and run artifacts.
    depends_on: [P0]
  - id: P2
    title: Validate wave-0 readiness gate from regenerated readiness artifacts.
    depends_on: [P1]
  - id: P3
    title: Execute release-ready family gate and verify evidence index outcomes.
    depends_on: [P2]
  - id: P4
    title: Commit refreshed artifacts and open PR with certification evidence.
    depends_on: [P0, P1, P2, P3]
```

---

## Acceptance Criteria

| ID  | Criterion                                                                 | Source | Verification                                                                                                                |
| --- | ------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| AC1 | `daily-skill-health.md` Generated at < 24h                                | R1     | `head -3` shows today's timestamp                                                                                           |
| AC2 | `wave-readiness.json` `wave-0-controls.ready: true`, zero blockers        | R3     | Python check exits 0                                                                                                        |
| AC3 | `artifact-parity-manifest.json` compliance_rate > 0.0                     | R2     | `jq .compliance_rate` > 0 — NOT MET (compliance_rate currently 0.0)                                                         |
| AC4 | `recursive-skill-shadow.yml` CI job passes on schedule with commit-back   | R5     | Actions UI shows green; git log shows telemetry commit                                                                      |
| AC5 | Family gate exits 0 in structural mode (PR CI)                            | R4     | `authoring-family-gate` CI job passes                                                                                       |
| AC6 | Release-ready gate exits 0 with `evidence-index.json` (local/manual cert) | R4     | Evidence index shows all 4 skills `outcome: passed` — NOT MET (evidence-index.json not yet generated with passing outcomes) |

## Execution Ledger

| Phase                           | Status | Notes                                                                                             |
| ------------------------------- | ------ | ------------------------------------------------------------------------------------------------- |
| P0 — Fix shadow CI workflow     | `done` | Already committed in c3ab24d (daily schedule, write-back, freshness check)                        |
| P1 — Local shadow cycle run     | `done` | 8 runs across 4 profiles, 6 passed, 2 escalated (expected)                                        |
| P2 — Verify wave-0 passes       | `done` | wave-0-controls.ready=true, zero blockers                                                         |
| P3 — Release-ready gate         | `open` | Structural gate passed; AC3 and AC6 not yet met (compliance_rate=0.0, evidence not release-ready) |
| P4 — PR with artifacts + CI fix | `open` | PR #86 updated; plan open pending AC3/AC6 completion                                              |

## Risks

| Risk                                                              | Likelihood | Impact | Mitigation                                                                                                            |
| ----------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| Shadow cycle exits non-zero (missing profiles or schema mismatch) | Low        | High   | Check `docs/skill-graphs/schemas/examples/pilot-profiles.json` exists; run with `--runs-per-profile 1` to reduce time |
| `TELEMETRY_WINDOW_MISMATCH` persists after P1                     | Low        | Medium | Re-run with `--window-days 14`; the window expands to cover current date range                                        |
| Release-ready gate times out (60+ min)                            | Low        | Medium | Run smoke evals separately first; use `SKILL_FAMILY_CODEX_PROFILE=fast`                                               |
| `contents: write` commit creates a loop on main                   | Low        | Medium | `[skip ci]` tag on the telemetry commit prevents re-trigger                                                           |
| evidence-index freshness (7 days) violated before PR merges       | Low        | Low    | Produce cert evidence immediately before PR creation; merge same day                                                  |
