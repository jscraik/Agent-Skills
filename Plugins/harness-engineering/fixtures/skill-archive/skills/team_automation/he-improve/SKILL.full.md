---
name: he-improve
description: Run metric-driven iterative improvement loops for an existing implementation with explicit gates, repeatable measurement, and bounded experiments. Use when the user wants Harness Engineering optimization or tuning rather than one-shot implementation.
metadata:
  skill-type: team_automation
---

# Harness Engineering Improve

**Note: The current year is 2026.** Use this when dating optimization artifacts and validating recency-sensitive references.

`he-plan` defines the initial execution approach. `he-improve` searches for better measurable outcomes. `he-work` applies finalized implementation changes in normal delivery flow.

This stage is for repeatable optimization loops, not generic coding from scratch.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Interaction Method](#interaction-method)
- [Workflow](#workflow)
- [Subagent policy](#subagent-policy)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [References](#references)

## Working agreement
- Treat this as a Harness Engineering optimization stage for measurable outcomes.
- Prefer small, reversible experiments with clear metrics and explicit gating.
- Keep a durable experiment log on disk; do not rely on chat context as state.
- Preserve immutable measurement surfaces so the metric cannot be gamed.
- Stop when the current best result is clearly better, reproducible, and documented.

## When to use
Use this skill when:
- the user asks to optimize, tune, or improve a measurable outcome,
- multiple plausible approaches exist and one-shot choice is weak,
- there is (or can be) a repeatable evaluation command,
- quality requires either hard metrics, LLM-judge scoring, or both.

Route elsewhere when:
- the user needs first-pass ideation/spec/planning (`he-ideate`, `he-spec`, `he-plan`),
- the user needs direct feature implementation without experiment loops (`he-work`),
- the problem has no measurable output contract.

## Required inputs
- optimization goal or spec path,
- measurement command with timeout and working directory (shell-free executable invocation),
- measurement command provenance (`HE_IMPROVE_COMMAND_PROVENANCE`),
- mutable scope and immutable scope,
- minimum acceptable gates,
- stopping limits (iterations and/or time),
- optional judge rubric when hard metrics are insufficient.

If critical inputs are missing, ask one blocking question before execution.

## Deliverables
- normalized optimization spec,
- baseline measurement with confidence notes,
- hypothesis backlog and batch plan,
- per-experiment log entries with outcomes (`kept`, `reverted`, `degenerate`, `error`, `deferred`),
- best-so-far snapshot with improvement delta,
- explicit next-step recommendation (`continue`, `handoff to he-work`, or `stop`),
- `schema_version: 1` in machine-readable summaries.

## Interaction Method

Use the platform's blocking question tool when available (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.

Ask one question at a time. Prefer concise single-select choices when natural options exist.

## Workflow
1. Load or create the optimization spec.
2. Validate spec structure against `references/optimize-spec-schema.yaml`.
3. Capture baseline using `scripts/measure.sh`.
4. Run a readiness probe for parallel blockers with `scripts/parallel-probe.sh`.
5. Generate hypotheses and mark dependency approval status.
6. Execute iterative experiments (`serial` or `parallel`) in isolated branches/worktrees.
7. For each experiment: measure, evaluate gates, optionally run judge scoring, and append to disk log immediately.
8. Keep only proven improvements and update the strategy digest.
9. Stop on target reached, plateau, budget cap, max iterations/hours, or explicit user stop.
10. Return final summary and recommended next stage.

### Persistence discipline
- Canonical scratch root: `.context/harness-engineering/he-improve/<spec-name>/`.
- Always write experiment state to `experiment-log.yaml` before reporting progress.
- Read back and verify critical writes before moving to the next experiment.

### Metric modes
- `hard`: optimize direct numeric metrics.
- `judge`: optimize sampled quality scores using structured rubric output.
- Hybrid pattern: run cheap degenerate gates first, judge second.

## Subagent policy
- Stage policy is defined in `../../../../../references/routing-map.json` under `he-improve`.
- Resolve role availability from `~/.codex/agents/manifest.json`.
- If auto-spawn is unavailable, continue inline and provide manual role guidance.
- If required roles are missing, route creation/install to `[[codex-agent-creator]]`.

## Validation
- Verify spec validity.
- Verify baseline measurement command output.
- Verify command provenance is declared and trust guardrails are satisfied before execution.
- Verify every experiment log append succeeded.
- Verify best-result selection is tied to configured metric direction and thresholds.
- Verify immutable paths were not changed by experiment workers.

## Anti-patterns
- running optimization without a measurable target,
- changing measurement harness logic in mutable experiment edits,
- summarizing results before durable log write,
- keeping non-improving changes because they "look promising",
- enabling broad parallelism before baseline/probe confidence exists.

## References
- `references/usage-guide.md`
- `references/optimize-spec-schema.yaml`
- `references/experiment-log-schema.yaml`
- `references/experiment-prompt-template.md`
- `references/judge-prompt-template.md`
- `references/example-hard-spec.yaml`
- `references/example-judge-spec.yaml`
- `references/source-parity.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/sub-agent-map.md`
- `scripts/experiment-worktree.sh`
- `scripts/measure.sh`
- `scripts/parallel-probe.sh`

## See Also
| Skill | When to use |
|---|---|
| [[he-plan]] | Build the initial implementation plan before optimization |
| [[he-work]] | Execute validated changes outside optimization loops |
| [[he-code-review]] | Run readiness review on optimized outcomes |
