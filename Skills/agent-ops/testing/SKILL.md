---
name: testing
description: "Choose validation proof for tests, CI, coverage, evals, and closeout evidence: map changed files to repo-native commands, classify pass/fail/blocked ownership, preserve trace/regression artifacts, and keep local, CI, Tessl, external-review, tracker, and runtime truth separate. Use when users ask what tests to run, why validation failed, what proof is enough, or whether command evidence supports a claim."
metadata:
  version: "1.0.0"
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-06-16:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-06-16"
  metadata_source: frontmatter
  compatible_roles: default, worker, skill-inspector
  runtime_needs: target repo and changed files; repo-owned validation wrappers or package scripts; exact command output or artifact evidence
---

# Testing

Select the smallest real proof that exercises the changed behavior, then widen only as the repo contract and risk surface require.

## When To Use

- Choose validation for code, docs, config, workflow, skill, or eval changes.
- Fix failing tests, classify validation ownership, or design coverage.
- Prove completion before handoff, PR, merge, release, or closeout claims.

## Required Inputs

- Target repo, changed files, nearest instructions, claim under test, repo command contracts, prior failures, and known blockers.

## Deliverables

- Exact commands with pass, fail, or blocked outcomes.
- Failure ownership plus the evidence artifact: log, trace, schema output, eval fixture, package receipt, or workflow-closeout receipt.
- Coverage gaps and next minimal diagnostic.

## Workflow

1. Read the repo instructions and command contracts.
2. Name the claim and proof lane: structural, deterministic behavior, trace analysis, calibrated judge, baseline comparison, regression retention, or production guardrail.
3. Run the narrowest command that exercises production code, a real CLI/script, validator, schema, or artifact path.
4. If it fails, classify ownership, fix only the in-scope cause, and rerun that same command before widening.
5. If behavior changed without meaningful proof, add or update a focused test or retained regression case.
6. Report only the lanes actually proven.

Evidence shape: unit/workflow; lane; given/should/actual/expected; reproduce command; ownership; status.

## Command Templates

- Skill package: `./bin/ask skills package verify Skills/agent-ops/testing --json --robot`
- Strict audit: `./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot`
- External review: `./bin/ask skills external-review Skills/agent-ops/testing --json --robot`
- Focused repo proof: run the discovered command, then report `Command: <exact command> -> pass|fail|blocked (<reason>)`.

## Validation

- Prefer repo-native wrappers: `./bin/ask`, `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`, `bash Infrastructure/scripts/validation-and-linting/validate-codestyle.sh`, package scripts, `just`, or documented validators.
- Testing evidence must use: `Command: <exact command> -> pass|fail|blocked (<reason>)`.
- Fail fast: stop at the first failed required gate; do not proceed to wider proof until that gate is fixed or classified blocked.
- Blocked steps must name the blocker, the nearest meaningful validation that did run, and what would unblock the exact proof.
- Treat repeated failures, conflicting instructions, dirty worktrees, credentials, network, Tessl, external-review, and runtime checks as separate blocker lanes.
- Do not run destructive commands unless explicitly requested and allowed.
- Schema-bound outputs include `schema_version`.

## Gotchas

- A broad green suite does not prove a touched path unless the command exercises it.
- A process exit code is not enough when the JSON receipt says `status: error`.

## Anti-Patterns

- Reporting a command as green when only a summary or stale artifact was inspected.
- Letting a judge decide objective properties that a parser, schema, or fixture can check.
- Claiming one evidence lane passed because a neighboring lane passed.

## Examples

- Worked flow:
  - Change: `Skills/agent-ops/testing/SKILL.md`
  - Lane: skill/package quality
  - Run: `./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot`
  - If JSON says `status: error` with `SEC_CANONICAL_HEADER_ORDER`, ownership is current patch.
  - Fix the header order, then rerun that same audit before external review.
  - Report: `Command: ./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot -> pass (trace <id>)`
- Skill package:
  - Run: `./bin/ask skills package verify Skills/agent-ops/testing --json --robot`
  - Report: `Command: ./bin/ask skills package verify Skills/agent-ops/testing --json --robot -> pass (trace <id>)`
- Related test:
  - Run: `pnpm run test:related`
  - Report: `Command: pnpm run test:related -> fail (current patch; src/lib/pr-closeout.ts assertion mismatch)`
  - Next: fix that assertion and rerun `pnpm run test:related`.
- Regression route:
  - Change: `src/lib/pr-closeout.ts`
  - Claim: invalid closeout receipts are rejected.
  - Run: `pnpm run test:related -- --grep closeout-receipt`
  - If it fails on accepted invalid input, ownership is current patch; add a rejecting fixture and rerun the same grep command.
  - Report: `Command: pnpm run test:related -- --grep closeout-receipt -> pass`
- Blocked artifact proof:
  - Report: `Command: ./bin/ask artifact-routine --json --robot -> blocked (missing fixture; nearest check ./bin/ask artifact-routine --help passed)`

## Progressive Disclosure

- Start with this active contract.
- Load only the reference needed for the current repo and change surface: [harness assurance](references/harness-assurance.md), [skill package validation](references/skill-package-validation.md), [eval artifact proof](references/eval-artifact-proof.md), [repo route matrix](references/repo-route-matrix.md), or [persona lenses](references/persona-lenses.md).
- For imported capsules, use [knowledge capsule routing](references/knowledge-capsule-routing.md), [knowledge capsule index](references/knowledge-capsules.md), [manifest](references/knowledge-capsule.manifest.yaml), and [knowledge demand](references/knowledge-demand.yaml); treat references/evals.yaml and references/evals notes as evidence, not runners.
