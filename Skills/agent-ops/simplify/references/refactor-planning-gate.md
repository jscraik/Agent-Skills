# Refactor Planning Gate

Read when:
- a simplify request could become a multi-file refactor;
- the user asks for a refactor plan, RFC, issue, or implementation sequence;
- test coverage, behavior boundaries, or allowed scope are unclear.

Use this because risky cleanup should still feel like simplify: scoped, evidence-backed, and executable in small working steps.

## Inputs

- Current diff or user-named files.
- User goal in plain language.
- Nearby tests, prior validation commands, or evidence that tests are missing.
- Project tracking surface when durable planning is needed.

## Planning Modes

- `n/a`: ordinary small cleanup; no plan section required.
- `inline-plan`: write a compact plan, then execute the smallest safe steps.
- `plan-only`: stop after the plan because the user asked for planning, approval, RFC, or issue text.

Default to `inline-plan` for non-trivial simplify work. Use `plan-only` only when requested or when execution would be unsafe without a user decision.

## Planning Checklist

1. Verify the stated problem against repo evidence.
2. Identify the behavior that must remain unchanged.
3. Define `scope_in` as the smallest files, modules, or behavior area that can solve the smell.
4. Define `scope_out` so the cleanup does not expand into architecture work.
5. Inspect tests or comparable validation patterns before choosing the edit strategy.
6. Break work into tiny steps where each step leaves the codebase working.
7. Record decisions that would surprise a future maintainer.
8. Pick the project tracking surface only when durable coordination is needed.

## Output Shape

```yaml
refactor_plan:
  mode: "inline-plan|plan-only"
  problem: "<verified maintainability problem>"
  behavior_to_preserve:
    - "<api, error, ordering, data shape, side effect, or observability contract>"
  scope_in:
    - "<file, module, or behavior area>"
  scope_out:
    - "<explicit non-goal>"
  tiny_steps:
    - "<small working-state-preserving step>"
  test_strategy:
    existing_coverage: "<found|missing|blocked>"
    validation:
      - "<exact command, comparable test, or manual equivalence proof>"
  evidence:
    - "<diff, test, artifact, prior pattern, or repeated failure>"
  tracking: "<chat-handoff|Linear issue|GitHub issue only if requested|n/a>"
```

## Evidence Ranking

When several refactor ideas compete, rank them by:

1. Behavioral risk and reversibility.
2. Strength of evidence: diff, tests, runtime output, artifacts, repeated failures, or prior project patterns.
3. User impact and maintenance payoff.
4. Confidence that the refactor is behavior-preserving.
5. Implementation cost.

Prefer findings with concrete evidence over broad taste-based rewrites. Mark low-evidence ideas as skipped instead of stretching the scope.

## Tracking Adaptation

Use the project's normal coordination surface:

- Linear issue: when the project uses Linear or the user says to track work in Linear.
- Chat handoff: when the plan is only for immediate execution.
- GitHub issue: only when explicitly requested or when that repository clearly uses GitHub issues for planning.
- ADR: do not create one from simplify unless the user explicitly asks and the repo already uses ADRs.

Long-lived issue text may avoid brittle file paths, but chat handoffs should include exact local paths and validation evidence.

## Stop Conditions

Stop before editing when:

- the requested behavior change is not actually behavior-preserving;
- the safe scope cannot be inferred;
- no test or equivalence strategy exists for a risky public contract change;
- the user explicitly requires durable tracking before implementation and the project convention is unclear.

When tracking is not required before implementation, use `chat-handoff` and continue with the smallest safe execution step.
