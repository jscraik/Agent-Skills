# Harness Engineering Code Review Anti-Patterns

## Table of Contents
- [Purpose](#purpose)
- [Detection and correction](#detection-and-correction)
- [Anti-pattern catalog](#anti-pattern-catalog)

## Purpose
This reference captures common failure modes for `he-code-review` so they can be detected and corrected consistently.

## Detection and correction
Use this loop during synthesis:
1. detect the anti-pattern from evidence,
2. correct behavior before final output,
3. capture residual risk as an explicit unknown when correction is incomplete.

## Anti-pattern catalog

### Reviewing the wrong target
Signals:
- findings mention files outside the requested PR/branch/artifact,
- recommendation assumes a different base than the resolved setup.

Correction:
- re-run setup resolution,
- restate exact target and `base:` assumptions,
- discard off-target findings.

### Stale diff or stale artifact context
Signals:
- comments reference outdated lines,
- recommendation conflicts with current changed files/artifact content.

Correction:
- refresh branch/diff/document snapshot,
- rerun affected reviewer lenses.

### Maximal fanout for low-risk scope
Signals:
- reviewer set is large relative to change risk,
- synthesis contains repetitive low-value findings.

Correction:
- reduce to smallest useful reviewer set,
- keep only additive findings with clear evidence.

### Protected-artifact cleanup chatter
Signals:
- suggestions to delete, ignore, or tidy protected Harness Engineering artifacts.

Correction:
- drop cleanup findings for protected artifacts,
- keep only readiness-relevant issues.

### Style over substance
Signals:
- style nits dominate when contract acceptance is failing,
- recommendation underweights correctness, security, or rollout risk.

Correction:
- run contract acceptance gate first,
- prioritize blockers and acceptance failures.

### Silent mode drift
Signals:
- behavior doesn’t match requested `mode:`,
- report-only mode mutates work or autofix mode skips residual routing.

Correction:
- reapply mode-driven handoff rules from `references/review-modes.md`,
- clearly label residual work ownership.

### Overstated confidence
Signals:
- strong conclusions without sufficient evidence,
- no unknowns listed despite missing verification.

Correction:
- downgrade unsupported claims,
- convert weak evidence into explicit open questions.
