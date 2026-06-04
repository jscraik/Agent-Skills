# PU-001 Improve Codebase Architecture Review

schema_version: 1
capability_surface: governed Skills SDK V1.0 implementation setup

## Complexity Symptoms

- The plan requires strict separation of local validation, review artifacts, PR/CI state, tracker state, merge readiness, and pulled-main truth. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:47`.
- The primary checkout began dirty with setup artifacts, so branch/worktree identity needed to be made explicit before implementation code edits. Evidence: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html:193`.

## Fresh Evidence

- Goal board enforces one slice at a time and no next slice before PR merge and pulled-main proof. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:16`.
- `./bin/ask` remains the repo control plane, with `skills-sdk` only as the product facade. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:12`.
- The board records forbidden generated/runtime/global surfaces. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:68`.
- Browser-visible notes are now part of the verification surface. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:53`.

## Missing Evidence

- No V1.0 parent tracker issue was found; tracker completion remains separate from local implementation. Evidence: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html:187`.
- Setup branch is not yet committed, pushed, merged, or pulled back into main. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/state.yaml:91`.

## Reviewer Coverage

- `$simplify`: required and written for PU-001.
- `$codex-review`: attempted through helper; nested runtime blocked, local fallback required.
- `$testing`: required and written for PU-001.
- `$ubiquitous-language`: required and written for PU-001.
- `@adversarial-reviewer` and `@agent-native-reviewer`: still pending.

## Experience Lenses

- Deep Module Examiner: pass for PU-001 setup because implementation modules are not edited and future module boundaries remain in the plan.
- Domain Language Guardian: pass with caveat because the goal keeps `ask CLI`, `skills-sdk`, `Runtime Projection`, and tracker vocabulary separate.
- Pragmatic Delivery Partner: pass with caveat because the branch isolation decision is necessary, but PR/merge/pull proof still remains.

## Agent Safe Boundary

`risky_until_merged`: the board is agent-readable and validator-backed, but agents must not start PU-002 until the setup branch lands and main is refreshed.

## Patch Design

Keep PU-001 as governance setup only: branch, goal board, notes, receipts, plan/spec artifacts, and review artifacts.

## Interface Design

Use the Goal Governor board as the stable interface for the next worker. The worker reads `goal.md`, `state.yaml`, `receipts.jsonl`, and the HTML notes before making implementation edits.

## Selected Design Decision

Proceed with a setup branch first, then create implementation worktrees from committed setup state. Evidence: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html:230`.

## Validation

- `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/skills-sdk-v1-0-product-implementation` -> pass
- `git diff --check` -> pass

## Confidence

Medium-high for PU-001 setup architecture. Confidence is not high until the branch is merged and main is pulled back, because later slices depend on that delivery state.
