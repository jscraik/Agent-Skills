# Testing Standards

## Table of Contents
- [Scope](#scope)
- [Required test layers](#required-test-layers)
- [TDD default workflow](#tdd-default-workflow)
- [Test quality standards](#test-quality-standards)
- [Exact behavior checks](#exact-behavior-checks)
- [Evidence-bearing tests](#evidence-bearing-tests)
- [Coverage and gates](#coverage-and-gates)
- [Enforcement](#enforcement)

## Scope
- This module defines testing standards for implementation and release confidence.

## Required test layers
- Test strategy SHOULD include:
  - Unit tests for core logic.
  - Integration tests for boundary interactions.
  - End-to-end tests for critical user workflows when applicable.
- This repository's TypeScript test runner is Vitest; keep unit, related, CI, coverage, e2e, and artifact checks routed through the package scripts unless a narrower documented invocation is needed for iteration.

## TDD default workflow
1. Write a failing test (RED).
2. Implement the smallest change to pass (GREEN).
3. Refactor safely while keeping tests green (REFACTOR).

## Test quality standards
- Tests MUST remain deterministic and isolated.
- Tests SHOULD use Arrange-Act-Assert structure when practical.
- Test names SHOULD describe behavior and expected outcome.
- If behavior is wrong, implementations MUST be fixed; tests SHOULD be rewritten only when assertions are invalid.
- Tests MUST NOT use the implementation under test as its own oracle, such as `expect(fn(input)).toBe(fn(input))` or comparing two variables initialized from the same implementation call. Use a requirement-derived expected value, fixture, schema, snapshot, or explicit property test instead. Legitimate determinism, idempotency, or defensive-copy assertions MUST carry a local `self-affirming-ok:` comment that explains the property being tested and SHOULD have adjacent assertions that pin externally visible behavior.
- Changed production `src/**` files MUST have a related Vitest path via `pnpm run test:related`; the gate must not pass silently when no test covers the changed source.

## Exact behavior checks
- When executable behavior changes, the smallest real code path that exercises the exact production code touched MUST run before the change is described as verified.
- Prefer invoking the production function, class, CLI command, shell script, validator, or route directly.
- If a change replaces regex parsing with structured parsing, or replaces
  duplicated command setup with a helper/wrapper, tests SHOULD include the
  boundary case that motivated the change and at least one failure or fallback
  case when the workflow is a gate.
- Shell script changes SHOULD have either a process-level test, a fixture-driven
  wrapper test, or the nearest repository shell validation command that
  exercises the exact script path.
- Package script routing changes SHOULD prove both the package command and the
  underlying wrapper path when practical.
- If no existing test covers the path, agents MAY create a temporary local reproduction harness under `codex-scripts/`, but it MUST remain gitignored and MUST import or invoke production code directly instead of copying implementation into the harness.
- If the exact path cannot run because it depends on unavailable credentials, external services, unsafe side effects, or missing generated runtime state, the blocker MUST be stated explicitly and the nearest meaningful validation SHOULD run instead.
- Production behavior MUST NOT be described as verified unless the touched path actually ran.

## Evidence-bearing tests
- Tests for validators, generated scaffolds, runtime-card, pr-closeout, replay,
  gate outputs, and workflow contracts SHOULD assert machine-readable evidence
  references, blocked/unknown states, and current-head freshness where the
  behavior depends on external proof.
- Evidence-bearing trust-boundary suites MUST be registered in
  `src/lib/testing/behavior-test-suites.json` and include at least one
  `expectBehavior({ given, should, actual, expected })` assertion. Add the
  suite owner, rationale, and proving command when registering a new suite.
- The behavior-test suite manifest is the owner table for this guard. Update
  `scripts/check-behavior-tests.mjs`, package scripts, and hook validation only
  when the manifest contract itself changes.
- Security-sensitive trace or browser-evidence tests MUST assert that sensitive
  headers, environment values, metadata, and nested payloads are redacted before
  artifacts are persisted.
- High-trust evidence-bearing suites registered in
  `src/lib/testing/behavior-test-suites.json` MUST keep at least one
  `expectBehavior({ given, should, actual, expected })` assertion so failing
  trust-boundary tests include reproduction context, expected behavior, actual
  output, and expected output. Add new evidence-bearing trust-boundary suites
  to the manifest before relying on `pnpm run quality:behavior-tests` for
  enforcement.
- Provider error, retry, and rate-limit tests SHOULD use mocks or fixtures unless
  a live integration test is explicitly budgeted and isolated.
- Long TDD arcs are a decomposition signal: if a behavior change needs many
  red/green/refactor steps, split the scenario into smaller proof points before
  widening validation.

## Coverage and gates
- Default target is >= 80% coverage unless a repository contract defines a different threshold.
- Generated artifacts, init scaffolds, and runtime/output contracts require artifact or deep validation when their emitted behavior changes.
- Repository-defined baseline gates are mandatory:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm run quality:self-affirming`
  - `pnpm run quality:behavior-tests`
  - `pnpm run test:related`
  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`

## Enforcement
- Testing evidence MUST list exact commands and outcomes in this form: `Command: <exact command> -> pass|fail|blocked (<reason>)`.
- Blocked test steps MUST include concrete blocker reasons.
