# HE Code Review Loop Patterns

Use these patterns when review needs more than a static diff read: disputed bot feedback, readiness claims, flaky behavior, external PRs, or repeated context failures.

## Evidence Loop Before Verdict

Before approving readiness or rejecting feedback, identify the shortest proof loop that can falsify the claim:

- Failing or targeted test for logic regressions.
- CLI fixture diff for generated files, config, schemas, reports, and command contracts.
- Browser, API, or local server check for interactive/user-facing behavior.
- Captured trace, log, replay, or artifact comparison for intermittent failures.
- Human-in-the-loop proof when only the user can drive the environment.

Good loops are fast, deterministic, and tied to the reviewed behavior. Improve the loop before adding broad fixes.

## Reproduction Status

Report one of these states when behavior is disputed:

- `reproduced`: live evidence confirms the issue.
- `source_verified`: code/path evidence proves the issue even without a runnable repro.
- `not_reproduced`: a relevant loop ran and did not show the issue; include the command and residual risk.
- `unclear`: access, environment, artifacts, or instrumentation are missing; list attempts and the smallest needed recovery step.
- `not_applicable`: the review is static policy, docs, or traceability only.

Do not hypothesize from vibes. If no useful loop can be built, stop and name the missing artifact, environment, or instrumentation.

## Falsifiable Hypotheses

For unclear regressions, flaky behavior, performance, or disputed review feedback, write three to five ranked hypotheses in this shape:

`If <cause> is responsible, changing or observing <specific variable> will produce <expected result>.`

Instrument one variable at a time. Give temporary logs unique prefixes and remove them before closeout.

## Deep Review Before Closure

Do not decide from the PR title, branch name, one search hit, or one bot comment. Read discussion and inspect nearby implementation, call sites, tests, docs, old names, and history when the verdict depends on prior behavior.

For likely-owner routing, use neutral evidence such as blame, log, follow renames, string searches, and shortlog. Do not frame routing as fault.

## Mutation Boundary

Keep review-only work byte-clean. Do not resolve threads, edit files, push commits, or close issues unless the user explicitly shifts into repair, autofix, or merge-readiness work.

Before fixes or thread resolution, re-fetch live PR state and confirm head, unresolved thread count, failed checks, and protected labels or maintainer-authored decisions still match the work plan.

## Readiness Sub-Passes

For PR readiness, include:

Core traceability chain: Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation.

- `security_review`: required for workflows, dependencies, secrets, permissions, downloads, generated code, vendored code, minified code, and public surfaces.
- `real_behavior_proof`: required when tests alone do not demonstrate the user-visible or operational behavior.
- `work_candidate`: separate the review verdict from whether a narrow repair/autofix path exists.
- `confidence_cap`: lower confidence when target/base, review threads, checks, instructions, or live behavior proof are unavailable.

Green CI is supporting evidence, not a substitute for the proof loop the change actually needs.

## Closeout Cleanup

Before a clean verdict or handoff, confirm:

- Original reproduction or proof loop is resolved, or the missing loop is documented as the blocker.
- Regression coverage exists at the right seam, or seam absence is itself reported as a finding.
- Temporary instrumentation and throwaway harnesses are removed.
- Exact validation commands and outcomes are recorded.
- Any repeated feedback is routed to the immediate PR fix and, separately, to HE skill/eval/context follow-up when the pattern keeps recurring.
