---
name: he-improve
description: Improve existing Harness Engineering implementations or workflows with evidence-backed changes. Use when users ask for targeted enhancement of shipped or drafted work.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Optimize with measurable evidence, not subjective preference.
- Keep experiments bounded and reversible.
- Persist experiment state to disk as the source of truth; chat context is not durable state.

## When to use

- Use when behavior exists and needs targeted quality, reliability, or performance improvement.
- Use after baseline implementation when iterative tuning is appropriate.
- Use when multiple plausible changes should be compared under explicit gates instead of picking one implementation path up front.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Load or create the optimization spec and validate metric type, scope, gates, and stopping limits.
2. Decide whether the target should use direct hard metrics, judge scoring, or hybrid gates plus judge evaluation.
3. Detect and resolve `fresh` versus `resume` state before running new experiments.
4. Establish a trusted baseline with the measurement harness and run the parallel-readiness probe before widening execution.
5. Run bounded iterations with explicit measurement gates and isolated experiment state.
6. After each experiment, write results to disk immediately, verify the write, and only then report or compare outcomes.
7. Keep, revise, or discard changes based on measured outcomes and route proven results to the next stage.

## Validation

- Ensure the spec, metric mode, and measurement command are valid before experimentation starts.
- Ensure each iteration has explicit metric target and rollback posture.
- Ensure accepted changes are justified by observed improvement.
- Ensure critical experiment state is written to disk and verified before moving on.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not broaden scope beyond bounded optimization goals.
- Do not mutate the measurement harness or declared immutable surfaces inside experiment edits.
- Do not summarize optimization results before they have been durably logged.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Tuning without baseline metrics.
- Keeping changes that do not improve target outcomes.
- Running parallel experiments before baseline and readiness probe confidence exists.
- Treating optimization as one-shot implementation instead of a measured keep-or-revert loop.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)

## Examples

- "Can you inspect this shipped retry workflow and prove the improvement with before and after metrics?"
- "Help me tune this validation lane, but keep each experiment reversible and stop if the metric gets worse."
- "This feature works, but the review loop is slow. Compare two bounded improvements and keep only the measured winner."
