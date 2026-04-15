---
name: systematic-debugging
description: Diagnose production bugs, regressions, or failing checks from concrete evidence before code changes. Use when the user wants a safe root-cause analysis and fix plan, not immediate speculative implementation.
metadata:
  skill-type: runbook
---

# Systematic Debugging

## When to use
- User reports failure, regression, test failure, instability, or unexpected behavior.
- The user needs a reproducible diagnosis before any code fix.

## Required inputs
- Observable symptoms (errors, stack traces, repro steps).
- Recent changes and recent deploy context.
- Environment details and execution constraints.
- Whether execution changes are allowed.

## Deliverables
- A structured diagnostic plan and prioritized root-cause hypothesis.
- Evidence list (commands, logs, file paths, and observed outputs).
- Recommended fix plan only after root cause confirmation.
- Explicit partial/blocked status when data is insufficient.
- Include `schema_version` in machine-readable output contracts.

## Procedure
### 1) Stabilize scope
- Reproduce consistently and collect error signatures first.
- Avoid speculative fixes before evidence.

### 2) Layered investigation
- Isolate component boundaries (client/server, CI/tooling/runtime, external dependencies).
- Confirm where signals drop and gather targeted evidence.

### 3) Hypothesis and verification
- Propose a narrow hypothesis linked to observed data.
- Add a minimal check for each hypothesis before change.

### 4) Fix only after confirmation
- Apply one minimal change at a time.
- Re-run checks to confirm the causal hypothesis.

## Constraints
- Redact secrets, tokens, credentials, and user identifiers in output.
- Prefer non-destructive commands; require explicit confirmation for risky commands.
- Respect user-defined execution limits and approval gates.

## Anti-patterns
- Guessing without reproducible evidence.
- Multiple speculative edits in one cycle.
- Declaring completion from partial checks.
- Skipping regression checks after a fix.

## Validation
- Stop and confirm at the first hard blocker.
- Include clear "blocked", "partial", or "complete" status with verification evidence.
- If no reproducible command can confirm the fix, return partial + next required data.
- Validation is fail-fast: if any blocking check fails or evidence is insufficient, stop and ask for confirmation before proceeding.

## Variation
- Vary investigation depth by incident criticality: start with one narrow, high-confidence hypothesis path and only add additional branches when the first set of checks is inconclusive.

## Examples
- "The test suite started failing after yesterday's refactor; can you inspect the first regression point and validate the blast radius?"
- "I see intermittent timeouts in CI; help me identify the root-cause path before proposing a fix."
- "Please debug a 500 error that only appears when feature flags are enabled."

## Failure mode
- If key logs, config, or context is missing, ask concise follow-up questions and pause execution.
- If an investigation path is blocked by permissions or missing tooling, provide a safe fallback plan.

## Philosophy
- Keep the workflow evidence-driven and reversible.
- Root cause comes before remediation.
- One proven change is better than a chain of speculative fixes.

## References
- Contract and scope: `Infrastructure/references/contract.yaml` and `Infrastructure/references/task-profile.json`.
- Evaluation coverage: `Infrastructure/references/evals.yaml`.
- Folded modes and compatibility notes: `Infrastructure/references/folded-legacy-modes-core60.md`, `Infrastructure/references/folded-legacy-modes-phase4.md`.
- Visual trace assets: `assets/systematic-debugging.png`.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## See Also
| Skill | When to use |
|---|---|
| [[gh-workflow]] | Use `ci_diagnose` mode for GitHub check failures that need lifecycle context |
| [[test-driven-development]] | Capture the root cause as a failing test before or alongside the fix |
| [[verification-before-completion]] | Prove the fix works before claiming the debugging loop is done |
| [[ce-plan]] | Re-plan the approach when repeated fixes fail and the current path is not converging |

**Topic map:** [[agent-ops]]
