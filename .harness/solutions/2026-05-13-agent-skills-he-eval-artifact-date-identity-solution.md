---
schema_version: 1
artifact_id: agent-skills-he-eval-artifact-date-identity-solution
artifact_type: he-compound-solution
canonical_slug: agent-skills-he-eval-artifact-date-identity
title: HE Eval Artifact Date Identity Solution
harness_stage: he-compound
status: complete
date: 2026-05-13
traceability_required: true
origin: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate
module: harness-engineering/eval-report
problem_type: validation
project_brain_sync: explicitly_deferred
tags:
  - he-eval-report
  - artifact-identity
  - frontmatter
  - validation
---

# HE Eval Artifact Date Identity Solution

## Command Summary

BLUF: This solution records a solved Harness Engineering artifact-identity
failure for Jamie and future agents. The job of this artifact is to prevent a
repeat mistake where an existing date-prefixed eval report is refreshed and its
frontmatter date is changed without renaming the file. The practical rule is
simple: future agents must keep filename date and frontmatter date aligned, then
run the artifact identity and frontmatter validators before committing refreshed HE proof
artifacts because report-specific validation alone can miss identity drift.

Decision Needed: Keep this as the durable solution note for the solved
frontmatter-date drift; do not create a broader Project Brain rule unless the
same failure repeats.

Top Risks: The main risk is that future agents treat frontmatter date as a
last-updated field, causing HE artifact identity validation to fail after an
otherwise valid closure report update.

Next Action: Use the validator trio listed below before committing refreshed
HE eval, review, spec, plan, or solution artifacts.

## Problem

The aggregate first-principles factory-gate eval report was updated from a
Phase 1-only draft into a four-phase complete_with_followup closure report.
During that refresh, the frontmatter date was changed from 2026-05-09 to
2026-05-13 while the filename stayed:

.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md

That made the report look current but invalid under the HE artifact identity
contract.

## Evidence

- Command: python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
  Result: passed, proving the eval-report content shape was valid.
- Command: python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
  Result: failed with date-prefixed filenames must have matching frontmatter date.
- Restoring frontmatter date 2026-05-09 made the same artifact pass
  validate_eval_report.py, he_artifact_identity_lint.py, and
  he_frontmatter_safety_lint.py.
- The fix was committed as e713a7fa1 fix(factory): align aggregate eval
  artifact date.

## Root Cause

The aggregate eval report was treated as if its frontmatter date represented the
latest refresh date. In this repo's HE artifact contract, the frontmatter date
is part of artifact identity when the filename starts with a date. Updating it
without renaming the artifact creates identity drift.

## Fix Or Durable Guidance

For existing HE artifacts whose filenames start with YYYY-MM-DD, keep
frontmatter date equal to that filename date.

Use status, body text, validation sections, proof links, or a new dated
follow-up artifact to show later progress. Rename the artifact only when the
artifact identity itself is intentionally changing and all links/references are
updated.

Before committing an HE eval, review, spec, plan, solution, or related artifact
after a refresh, run the identity validators on the exact touched artifact path:

- python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/REPORT.md
- python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/REPORT.md
- python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/REPORT.md

For non-eval artifacts, use the artifact identity and frontmatter safety lints,
plus the stage-specific validator when one exists.

## Validation

Final validation for the solved issue:

- python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md: pass.
- python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md: pass.
- python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md: pass.
- Commit hooks passed for the corrective commit.

## Prevention

- Treat HE artifact identity validation as required before committing refreshed
  .harness artifacts, even if the report-specific validator passes.
- Do not use frontmatter date as a last-updated field for date-prefixed HE
  artifacts.
- If a future report needs an explicit refresh timestamp, add that only through
  an approved schema field or body prose, not by drifting the identity date.
- When he-eval-report is invoked after closure commits, rerun the three
  validators before reporting closure-grade status.

## Project Brain / Routing

Project Brain sync is explicitly deferred for this run because the durable
learning belongs first in .harness/solutions and no broader decision, rule, or
knowledge classification was necessary to fix the validated failure. Future HE
instruction or validator work may link this solution from artifact routing
guidance if the same failure repeats.

## Related Artifacts

- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
- .harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md
- .harness/review/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-technical-review.md
- e713a7fa1 fix(factory): align aggregate eval artifact date
