---
schema_version: 1
artifact_id: agent-skills-skill-quality-baseline-projection-solution
artifact_type: he-compound-solution
canonical_slug: agent-skills-skill-quality-baseline-projection
title: Skill Quality Baseline Projection Solution
date: 2026-05-08
harness_stage: he-compound
status: complete
traceability_required: true
origin: "PR #153 structure-gate failure"
linear_issue: JSC-246
linear_milestone: Command surface and ask reliability
asset_family: skill quality baseline projection
owner: Agent Skills Team
source_artifact: Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_repo_skill_quality.py
freshness_reviewed_on: 2026-05-08
review_after_days: 90
project_brain_status: not_applicable
---

# Skill Quality Baseline Projection Solution

Freshness: 2026-05-08
Project Brain status: not_applicable; no `.harness/knowledge/**` tree is present.

## Governed Asset

- `Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_repo_skill_quality.py`
- `Plugins/skill-factory/skills/code_quality_review/skill-builder/references/skill-quality-baseline.json`
- `Plugins/skill-factory/fixtures/budget-archive/**/skill-quality-baseline.json`

## Problem

The repo-wide skill structure gate can misclassify every existing structure
failure as new when the compact baseline file is read through a projected skill
path and the command resolves the baseline path before interpreting the
baseline's `archive` pointer.

In this state:

- the compact baseline stub remains readable;
- the archived baseline exists;
- the loader still returns an empty allowlist because archive-relative paths
are interpreted after projection resolution;
- CI reports large false-positive `new_structure_failures` instead of the real
baseline delta.

## Evidence

- `structure-gate` on PR #153 reported `Skills scanned: 75`,
  `Structure failures: 71`, and `New structure failures vs baseline: 71`.
- Local reproduction with `/private/tmp` artifact outputs reproduced the same
  empty-baseline behavior.
- Loading the projected baseline path directly returned `0` allowed failures
  before the fix.
- After preserving lexical baseline paths and normalizing archive candidates,
  the loader returned `102` archived allowed failures.
- After refreshing the archived baseline to the current scan, the same gate
  reported `New structure failures vs baseline: 0`,
  `Resolved structure failures vs baseline: 0`, and `RESULT: PASS`.

## Resolution

Preserve the caller-provided baseline path when reading or writing the baseline.
For compact archive stubs, normalize lexical archive candidates before checking
existence, and use projection-resolved parents only as fallback candidates.

When the loader fix exposes a smaller set of real new/resolved failures, refresh
the archived baseline through the repo's skill-quality baseline lane rather than
hand-editing unrelated skill files.

## Maintenance Ownership

Skill Factory owns the baseline loader and archived baseline. Harness
Engineering owns using this evidence to classify PR blockers correctly before
closing HE execution slices.

## Recovery Command Pattern

The default Agent Operating Contract behavior is to use the repo wrapper:

```bash
./bin/ask repo validate --json --robot
```

For focused diagnostics when troubleshooting baseline projection issues, use
temporary artifact paths to avoid generated churn:

```bash
python3 Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_repo_skill_quality.py \
  --root . \
  --reports-dir ${TMPDIR:-/tmp}/agent-skills-structure-gate-repro/reports \
  --baseline-file Plugins/skill-factory/skills/code_quality_review/skill-builder/references/skill-quality-baseline.json \
  --benchmark-mode off \
  --benchmark-config Plugins/skill-factory/skills/code_quality_review/skill-builder/references/benchmark-policy.json \
  --benchmark-output-json ${TMPDIR:-/tmp}/agent-skills-structure-gate-repro/industry-benchmark-latest.json \
  --sarif-out ${TMPDIR:-/tmp}/agent-skills-structure-gate-repro/skill-structure-gates.sarif \
  --format text
```

Do not treat generated `Infrastructure/artifacts/skills/**` churn from local
diagnosis as source change unless the execution slice explicitly requires it.
