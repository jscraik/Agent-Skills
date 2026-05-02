# Codex-Style Review Flow

## Purpose

This reference adapts the useful review discipline from OpenClaw ClawSweeper prompts into Harness Engineering `he-code-review`.

Use it when a PR, branch, diff, or review-thread bundle needs a merge-readiness call rather than a narrow implementation critique.

Source reviewed:
- `https://github.com/openclaw/clawsweeper/tree/5c804ea0936794763ba7e22f107fa78bde919528/prompts`

## Principles to preserve

- Treat issue and PR discussion as evidence, not background.
- Read enough code, tests, docs, comments, checks, and history to make the confidence label honest.
- Prefer no finding over a vague finding.
- Keep looking until every concrete changed-surface blocker is represented.
- Separate a true blocking finding from a condition, watch item, or non-actionable note.
- Make every merge recommendation depend on proof, not intent or title proximity.
- Keep security-sensitive repair and merge decisions conservative and route them to the right reviewer.

## Evidence Pack

Build this before writing findings:

- target: PR, branch, diff, artifact, base/head refs, and requested mode
- intent: PR title/body, linked issue, Linear QA issue, spec, plan, or user request
- changed surface: files, ownership area, generated/protected artifacts, APIs, migrations, CI, dependencies, release scripts, package metadata, credentials, or permissions
- review state: human comments, Codex findings, CodeRabbit/Copilot/bot findings, requested changes, unresolved threads
- validation state: local commands run, CI/check status, failures, skipped gates, stale branch/conflict state
- behavior proof: tests, reproductions, expected behavior, docs, call paths, runtime checks, or release provenance
- history when useful: adjacent commits, previous attempts, moved behavior, likely owners, and prior decisions

If an evidence class is required but missing, record it as a blocker or confidence limit. Do not silently assume it is clean.

## Finding Gate

Only emit a finding when it has all of:

- severity: `P0`, `P1`, `P2`, or `P3`
- confidence: high, medium, or low
- location: exact file and line where possible, or exact review-thread/check reference
- evidence: code path, test/check output, linked artifact, or review-thread proof
- impact: why this blocks merge, release, user behavior, data integrity, security, operability, or maintainability
- minimal remediation: the smallest change or decision that clears it

Discard or demote:

- style-only notes with no readiness impact
- speculative concerns without a code path
- duplicate findings already covered by a higher-severity issue
- protected-artifact cleanup suggestions
- broad rewrites that should become a plan/spec instead of a review finding

## PR Security Pass

For PRs, run a dedicated security and supply-chain pass when the diff touches:

- CI workflows, job permissions, GitHub Actions refs, build scripts, install scripts, release scripts, or package publishing metadata
- dependency sources, lockfiles, downloaded artifacts, generated/vendor/minified code, or lifecycle hooks
- auth, authorization, secrets, tokens, credentials, untrusted input, injection surfaces, network egress, or sensitive data handling

Output:

- `cleared` when no concrete security or supply-chain issue is found
- `needs_attention` when a concrete issue exists, with file/thread evidence
- `not_applicable` for non-PR artifacts or review targets with no security-sensitive report

Security-sensitive repair or closure decisions should route to `security-ops`, `security-reviewer`, or a human owner instead of being auto-mutated.

## Review Thread Disposition

Before recommending `go`, every actionable review thread must be one of:

- addressed by the current diff
- proven non-actionable with concrete evidence
- intentionally deferred with owner and follow-up artifact
- unresolved and therefore blocking

This includes Codex, CodeRabbit, Copilot, and similar automated reviewer findings. Bot findings are not automatically correct, but they must be explicitly resolved, disproven, or escalated.

## Merge Readiness Gate

Recommend `go` only when:

- no unresolved `P0` or `P1` findings remain
- actionable review threads are addressed, disproven, or formally deferred
- linked Linear QA issues are closed by behavior and evidence
- changed-surface validation passed or the blocker is unrelated and documented
- relevant security and supply-chain status is cleared
- branch conflict/staleness state is understood
- protected artifacts are preserved

Use `go-with-conditions` when the remaining work is explicit, bounded, non-blocking, and has an owner.

Use `no-go` when merge would carry unresolved blockers, unknown branch state, relevant failing checks, missing changed-surface validation, or unresolved actionable review comments.

## Repair Handoff

In `mode:autofix`, keep repair narrow:

- list only files expected to change
- address accepted findings in severity order
- preserve contributor credit and existing PR context
- do not create broad feature/config/docs rewrites from review mode
- route security-sensitive repair to security review

Residual actionable work should become a todo or follow-up with evidence, priority, owner, and acceptance criteria.
