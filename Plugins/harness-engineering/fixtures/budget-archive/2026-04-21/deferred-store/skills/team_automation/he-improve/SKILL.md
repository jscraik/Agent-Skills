---
name: he-improve
description: Analyze and improve an existing implementation through metric-driven, bounded iteration loops. Use when the user wants Harness Engineering optimization or tuning rather than one-shot implementation.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Optimize with measurable evidence, not subjective preference.
- Keep experiments bounded and reversible.
- Persist experiment state to disk as the source of truth; chat context is not durable state.

## When to use

- Use when behavior exists and needs targeted quality, reliability, or performance improvement.
- Use after baseline implementation when iterative tuning is appropriate.
- Use when multiple plausible changes should be compared under explicit gates instead of picking one implementation path up front.

## Inputs

- Baseline behavior, metrics, and current constraints.
- Candidate improvement hypotheses and acceptable risk bounds.
- Optimization goal or spec path.
- Metric mode and rubric needs: `hard`, `judge`, or hybrid gate-plus-judge.

## Outputs

- Prioritized improvement plan with measurable success criteria.
- Iteration outcomes and next-step recommendation.
- Explicit run mode: `fresh` or `resume`.
- Durable experiment-log path and best-so-far outcome when optimization runs are started.
- Include `schema_version: 1` when structured output is requested.

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
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Tuning without baseline metrics.
- Keeping changes that do not improve target outcomes.
- Running parallel experiments before baseline and readiness probe confidence exists.
- Treating optimization as one-shot implementation instead of a measured keep-or-revert loop.

## Examples

- "When the user asks, `Can you inspect why the build got slower after the refactor and keep only changes that measurably help?`"
- "Please improve search quality, but validate the winner with a judge-backed loop because raw metrics can be gamed."
- "Help me resume the last optimization run if the experiment state is still trustworthy; otherwise start clean from a baseline."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
Read when: you need full workflow behavior, gating, and deliverable expectations.
Read when: you need schema contracts, eval cases, donor-parity notes, and prompt templates.
Read when: you need executable measurement or probe helpers.
Read when: you need icon/display metadata and invocation policy.
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
Read when: you need canonical stage policy and fallback behavior.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
