---
title: Codex live smoke closeout stabilization
asset_family: skill authoring family live smoke evaluation
owner: Agent Skills Team
source_artifact: Docs/plans/2026-04-04-feat-skill-authoring-family-contract-rollout-plan.md
freshness_reviewed_on: 2026-04-04
last_updated: 2026-04-04
review_after_days: 90
---

# Codex Live Smoke Closeout Stabilization

## Table of Contents
- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

Live `codex exec` smoke evals for the skill-authoring family were repeatedly failing in ways that looked like skill-contract regressions even when the repo-side rollout work was correct.

The recurring failure pattern had three layers:
- repo-local `CODEX_HOME` replacement dropped authenticated state and produced `401 Unauthorized` plus empty `final.txt` outputs;
- the normal authenticated Codex home could fail before model execution when the global automation rule pack was invalid;
- slow live smoke cases could hit the default 60-second timeout before returning a final response.

That combination left the rollout plan and maturity matrix in a degraded closeout state because live smoke failures were initially indistinguishable from real routing or provenance regressions.

After infrastructure recovery, one residual failure remained in the new builder round contract case: acceptance regex wording used hyphenated readiness tokens while the contract and harness used underscore state names (`comparison_incomplete`, `comparison_blocked`, and related values). That mismatch looked like a contract regression even though the underlying logic was correct.

## Resolution

Stabilize live smoke closeout in this order:

1. Fail fast on invalid Codex homes before running live evals.
   `run_skill_evals.py` now checks the effective `CODEX_HOME`, verifies Codex login state, and stops with a remediation message instead of letting unauthenticated repo-local homes fail later with transport or auth noise.
2. Keep the authenticated default home bootable.
   The protected-branch automation rule was repaired so the normal Codex home no longer aborts because of a broken `git branch -d` rule example.
3. Give live Codex smoke the normal heavy timeout where needed.
   The skill-authoring family clarification and provenance cases now use `timeout_profile: codex-heavy`, which restores the expected 180-second budget for real live runs.
4. Preserve runner-failure truth in the harness.
   Empty-output non-zero live runs stay classified as runner failures rather than being mislabeled as regex or acceptance failures.
5. Tighten the surviving skill contract once infrastructure is healthy.
   `skill-builder` now treats undecided `standalone skill` versus `plugin` requests as explicit `route clarification` and asks the deliverable-boundary question directly, so the clarification smoke case passes for the right reason.
6. Keep eval acceptance token conventions aligned with canonical state enums.
   The builder metadata case now accepts readiness tokens with `[_-]` matching so live output using underscore enums still satisfies acceptance checks.

The durable closeout pattern for future work is:
- preflight the repo;
- run live smoke with an authenticated Codex home;
- rely on per-case `codex-heavy` timeouts for the slow family cases;
- only treat remaining failures as skill-contract problems after those runner prerequisites are satisfied;
- verify acceptance token conventions against the harness enum source before classifying a failure as behavioral drift.

## Evidence

- Rollout artifact that exposed the degraded closeout state:
  [2026-04-04-feat-skill-authoring-family-contract-rollout-plan.md](/Users/jamiecraik/dev/agent-skills/Docs/plans/2026-04-04-feat-skill-authoring-family-contract-rollout-plan.md)
- Iteration-upgrade artifact that captured the final green closeout evidence:
  [2026-04-04-feat-skill-authoring-family-iteration-upgrade-plan.md](/Users/jamiecraik/dev/agent-skills/Docs/plans/2026-04-04-feat-skill-authoring-family-iteration-upgrade-plan.md)
- Runner-side hardening and Codex-home preflight:
  [run_skill_evals.py](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py)
- Case-level 180-second routing for the affected live smoke checks:
  [evals.yaml](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/references/evals.yaml)
- Regression coverage for timeout-profile and live-runner handling:
  [test_run_skill_evals.py](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/scripts/test_run_skill_evals.py)
- Clarification-contract fix for ambiguous standalone-skill versus plugin prompts:
  [SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/SKILL.md)
- Authenticated Codex-home rule-pack repair:
  [automation.rules](/Users/jamiecraik/dev/configs/codex/rules/automation.rules)

Validated on 2026-04-04 with:
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --runner codex --case builder-round-metadata-contract`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke --runner codex --case clarification-package-ambiguous --case provenance-import-rollback`
- `python3 Skills/skill-builder/Infrastructure/scripts/test_run_skill_evals.py`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`

## Follow-up

- Refresh rollout artifacts that still describe the pre-fix degraded state if they are needed as current readiness evidence.
- If live Codex smoke regresses again, check effective `CODEX_HOME`, login state, rule-pack self-test validity, and resolved case timeout before changing skill prose or acceptance regexes.
