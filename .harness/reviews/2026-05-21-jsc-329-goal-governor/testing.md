# Testing Review - JSC-329 T002 (goal-governor review mode guard)

## Findings

### medium - Review-mode test is keyword-presence only and can pass while behavior contract regresses
- Evidence: Skills/agent-ops/goal-governor/tests/test_check_goal_board.py:22-56
- Why this matters: The new test validates plain substring presence in `SKILL.md`/`contract.yaml`/`evals.yaml`, but does not assert structural coupling between trigger, route, and forbidden actions. A contradictory edit could keep these tokens present while effectively changing review-mode behavior, and this test would still pass.
- Suggested fix: Parse `contract.yaml`/`evals.yaml` as YAML and assert:
  - `review_mode_contract.execution_override_phrase` exists and is non-empty.
  - `forbidden_actions` contains the full expected set.
  - eval case `review-goal-prompt-not-start-yet` contains acceptance checks for both explicit review-only signal and prohibited execution side effects.

### medium - New override branch is unproven (review triggers plus explicit execution override)
- Evidence: Skills/agent-ops/goal-governor/SKILL.md:207-210, Skills/agent-ops/goal-governor/references/contract.yaml:51, Skills/agent-ops/goal-governor/references/evals.yaml:11-24
- Why this matters: The contract introduces `execution_override_phrase: "proceed with governed implementation"` but no eval case or unit test exercises the branch where review-language is present and override phrase is present. This leaves the highest-risk routing ambiguity untested.
- Suggested fix: Add a dedicated eval case (and/or test fixture) with mixed prompt content (`check this prompt ... proceed with governed implementation`) and assert route is not `review` and review-only guard language is absent.

## Residual Risks
- Prompt-only contracts remain susceptible to lexical gaming unless structure-level assertions are added.
- Current tests do not verify cross-file consistency (for example, required review fields in `SKILL.md` exactly match `contract.yaml` required fields).

WROTE: .harness/reviews/2026-05-21-jsc-329-goal-governor/testing.md
