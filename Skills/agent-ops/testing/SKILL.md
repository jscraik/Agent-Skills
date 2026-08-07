---
name: testing
description: "Validate and choose proportionate test proof for tests, CI, coverage, evals, and closeout evidence: map changed files to repo-native commands, place checks at commit, push, and pull-request gates, classify pass/fail/blocked ownership, and preserve trace/regression artifacts. Use when users ask what tests or gates to run, how to design coverage, why validation failed, or what proof supports a claim."
metadata:
  version: "1.1.0"
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
- Design or audit a repository's test layers and local/CI gate placement.
- Prove completion before handoff, PR, merge, release, or closeout claims.

## Inputs

- Target repo, changed files, nearest instructions, claim under test, repo
  command contracts, wrapper working directory, environment or credential
  materialization, prior failures, and known blockers.

## Outputs

- Exact commands with pass, fail, or blocked outcomes.
- Failure ownership plus the evidence artifact: log, trace, schema output, eval fixture, package receipt, or workflow-closeout receipt.
- Coverage gaps and next minimal diagnostic.
- When delivery is in scope, the validated report path, delivery receipt path,
  and exact command that checked each artifact.

## Workflow

1. Read the repo instructions and command contracts.
2. Inspect the changed behavior, existing tests or fixtures, and the canonical
   wrapper that owns them. Identify what is already proved, what rejection or
   boundary behavior is missing, and whether the wrapper changes into a package
   root or rewrites paths.
3. Name the exact invariant and proof lane: structural, deterministic behavior,
   trace analysis, calibrated judge, baseline comparison, regression retention,
   production guardrail, or delivery receipt.
4. Run the narrowest command that exercises production code, a real CLI/script,
   validator, schema, artifact path, or installed/package path.
5. If it fails, classify ownership and fix only the in-scope cause. Rerun the
   same proof before widening. Use the exact same command when it was valid;
   when the failure came from wrapper-relative paths, working-directory
   semantics, tool shims, environment materialization, or unsupported flags,
   preserve the failed command and rerun the corrected canonical command.
6. For validators, schemas, parsers, policy gates, and artifact contracts,
   require at least one accepted case and one rejected case for each meaningful
   invariant. Include boundary or false-positive protection when widening
   detection.
7. Widen through the canonical wrapper, affected suite, schema or artifact
   lane, and repository-required diff or generated-state checks. Run hosted,
   review, external, Tessl, runtime, or delivery lanes only when they are in
   scope.
8. Report only the lanes actually proven. When durable delivery is required,
   validate the report and delivery receipt after code and test proof.

Evidence shape: unit/workflow; lane; given/should/actual/expected; reproduce command; ownership; status.

Ownership values should distinguish current patch, pre-existing repository
defect, unrelated dirty-worktree or generated-state interference, invalid or
unsupported command shape, wrapper working-directory mismatch, environment or
toolchain failure, trust or credential failure, certificate or network failure,
hosted policy or approval boundary, external or runtime dependency, and unknown
after bounded diagnostics.

Default widening ladder:

1. Focused regression for the exact invariant.
2. Direct CLI, validator, fixture, or artifact probe of the changed behavior.
3. Canonical package or repo wrapper proving the focused test is wired into the
   maintained validation route.
4. Wider affected suite, schema spine, typecheck, or scenario/eval preview.
5. Diff, formatting, generated-state, or changed-files checks required by the
   repository contract.
6. Hosted checks, review-thread state, external review, Tessl, runtime, or
   delivery receipts only when those lanes are in scope.

Skip a rung when it does not apply, but record the reason. Do not treat a later
rung as a substitute for missing earlier behavior proof.

## Test Strategy And Gate Placement

Start from the user-visible promise and its failure modes, not a universal test
percentage or a copied toolchain. Select the smallest layers that would detect
the meaningful ways that promise could fail:

| Layer | Use it for | Keep the proof focused on |
| --- | --- | --- |
| Unit | Pure rules, transforms, validation, and explicit error paths. | Observable inputs, outputs, boundaries, and rejected cases. |
| Integration or contract | CLI, filesystem, package, API, configuration, or service boundaries. | Real message, file, command, or schema shape at the boundary. |
| End-to-end smoke | A small number of critical user journeys. | The main action completes with a usable result; do not duplicate every lower-level case. |
| Regression | A fixed defect or stable production failure. | The original failure first, then the corrected behavior. |
| Property-based or generative | Many input combinations share a clear invariant. | The invariant, generated input domain, shrinking, and the retained counterexample. |
| Mutation or exploratory | Assertions may be weak, or the unknown risk needs investigation. | Surviving mutations or an exploration charter; treat both as gap-finding evidence, not total correctness proof. |

Place only work that is fast enough and relevant enough at each gate:

1. **Pre-commit:** formatting, linting, type checks, and affected fast tests.
   Do not make every commit wait for a broad suite unless the repository has a
   measured reason to do so.
2. **Pre-push:** the wider affected suite and repository-specific checks that
   are too slow for ordinary commits but cheap enough to stop a bad push.
3. **Pull request CI:** the full maintained unit suite, required integration or
   contract tests, build, static checks, and critical smoke coverage. Confirm
   the workflow actually invokes them; a package script alone is not PR proof.
4. **Scheduled or release depth:** mutation, broader end-to-end, compatibility,
   performance, security, and live-dependency checks when their risk warrants
   them. Report this lane separately from commit or PR evidence.

For a strategy or gate audit, inventory each layer as `present`, `missing`,
`not_applicable`, or `unverified`. Then verify the actual hook or workflow
entrypoint rather than inferring enforcement from a README, package script, or
tool dependency. A green unit suite does not prove its pre-commit, pre-push,
or pull-request gate ran.

### Command Templates

- Skill package: `./bin/ask skills package verify Skills/agent-ops/testing --json --robot`
- Strict audit: `./bin/ask skills audit Skills/agent-ops/testing --level strict --json --robot`
- External review: `./bin/ask skills external-review Skills/agent-ops/testing --json --robot`
- Focused repo proof: run the discovered command, then report `Command: <exact command> -> pass|fail|blocked (<reason>)`.

### Examples

- For a change to `Skills/agent-ops/testing/SKILL.md`, run the strict audit,
  inspect its JSON status and findings, fix a current-patch header-order failure,
  and rerun the same audit before package verification.
- For a validator change, retain one accepted fixture and one rejected fixture,
  run their focused test, then run the canonical wrapper that owns that test.
  Report behavior proof separately from wrapper wiring and hosted checks.
- For a test-strategy request, map promises and failure modes to layers, inspect
  the installed hooks and PR workflow, and report each gate as present, missing,
  not applicable, or unverified before recommending a change.

## Failure Mode

If the repository does not expose its actual hook, workflow, or test entrypoint,
report the affected gate as `unverified` rather than assuming it runs. Ask for
the smallest path or command evidence needed to inspect it, and do not add a
new test layer or mandatory gate until the target repository and its risk are
known.

## Gotchas

- A broad green suite does not prove a touched path unless the command exercises it.
- A process exit code is not enough when the JSON receipt says `status: error`.
- A validator that accepts known-good fixtures but has no known-bad fixture may
  prove loading without proving enforcement.
- A top-level success status is not enough when the claim depends on nested
  counts, findings, validation rows, digests, selected profiles, or receipt
  fields. Name the semantic fields that establish or contradict the claim.
- When summary fields disagree with detailed artifacts, report the
  contradiction and prefer the field designated authoritative by the
  repository contract.

### Anti-Patterns

- Reporting a command as green when only a summary or stale artifact was inspected.
- Letting a judge decide objective properties that a parser, schema, or fixture can check.
- Claiming one evidence lane passed because a neighboring lane passed.

## Validation

- Prefer repo-native wrappers: `./bin/ask`, `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`, `bash Infrastructure/scripts/validation-and-linting/validate-codestyle.sh`, package scripts, `just`, or documented validators.
- Testing evidence must use: `Command: <exact command> -> pass|fail|blocked (<reason>)`.
- Fail fast: stop at the first failed required gate; do not proceed to wider proof until that gate is fixed or classified blocked.
- Blocked steps must name the blocker, the nearest meaningful validation that did run, and what would unblock the exact proof.
- Treat repeated failures, conflicting instructions, dirty worktrees, credentials, network, Tessl, external-review, and runtime checks as separate blocker lanes.
- Before running a discovered wrapper, determine whether it changes directories,
  rewrites paths, requires a trusted tool configuration, or expects credentials
  through an approved wrapper. Do not infer a source regression from a path,
  trust, shim, certificate, or environment-materialization failure.
- When command shape changes, report both attempts and explain why they exercise
  the same proof lane rather than silently replacing the failed invocation.
- Redact secrets, tokens, credential values, and sensitive log content from
  commands, receipts, traces, fixtures, and reported evidence.
- Do not run destructive commands unless explicitly requested and allowed.
- Schema-bound outputs include `schema_version`.

## References

- Start with this active contract.
- Load only the reference needed for the current repo and change surface: [harness assurance](references/harness-assurance.md), [skill package validation](references/skill-package-validation.md), [eval artifact proof](references/eval-artifact-proof.md), [repo route matrix](references/repo-route-matrix.md), or [persona lenses](references/persona-lenses.md).
- For imported capsules, use [knowledge capsule routing](references/knowledge-capsule-routing.md), [knowledge capsule index](references/knowledge-capsules.md), [manifest](references/knowledge-capsule.manifest.yaml), and [knowledge demand](references/knowledge-demand.yaml); treat references/evals.yaml and references/evals notes as evidence, not runners.

## Execution Boundaries

Run only commands that the repository supports and the user has authorized, starting with the smallest relevant proof. Do not invoke destructive, hosted, or live-evaluation paths merely to improve coverage, and do not widen a blocked lane without classifying the blocker.

## Cross-Lane Gotcha

One passing command does not validate adjacent lanes. Preserve exact command shape, distinguish reruns from new evidence, and do not silently replace a blocked production path with a narrower local check.
