---
name: sdk-scenario-generator
description: "Create, review, and maintain gold-standard Skills SDK eval scenarios before internal evals, dry Tessl staging, or live private Tessl scoring. Use when creating or updating a skill, importing KnowledgeOS or Tessl scenario suggestions, checking scenario drift, hardening evals that are too easy, or preparing a minimum 20-scenario live Tessl set."
metadata:
  version: "1.0.0"
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-06-17:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-06-17"
  metadata_source: frontmatter
  compatible_roles: [default, worker, skill-inspector]
  runtime_needs: [target skill, references/evals.yaml, references/evals/*.md, references/contract.yaml, Tessl dry-run staging]
---

# SDK Scenario Generator

Create gold-standard Skills SDK scenarios, then stage them for internal evals and Tessl without making the evals easy to game.

## Philosophy

- Scenario count is a floor, not quality proof.
- A good scenario makes the right skill useful and a strong baseline plausibly wrong.
- Task text is for the agent; criteria are for the scorer. Do not leak the answer into the task.

## When To Use

- Creating, installing, or updating a skill that will be evaluated.
- Adding KnowledgeOS capabilities with suggested eval scenarios.
- Turning Tessl scenario-skill output into repo-owned SDK eval assets.
- Checking whether scenarios are stale after a skill change.
- Live private Tessl readiness, dry Tessl staging, or internal eval hardening.

## Avoid

- Do not use this skill to bypass a failed live eval by making scenarios easier.
- Do not use it for structure-only package checks unless the skill contract explicitly declares that exception.

## Required inputs

- Target skill path and latest `SKILL.md`.
- `references/contract.yaml`, `references/evals.yaml`, and any `references/evals/*.md` fixtures.
- Knowledge capsules or extracted evidence when the skill was enriched from KnowledgeOS.
- Latest internal eval, dry Tessl, live Tessl, or Plugin Eval result when available.
- Tessl workspace name and run-budget evidence before any live scoring plan.

## Outputs

- Scenario inventory with keep, update, add, or remove decisions.
- Gold-standard scenario drafts or canonical eval patches.
- Weak-eval critique and anti-easy notes.
- Tessl run-budget evidence or blocker.
- Internal eval, dry Tessl, and live Tessl readiness summary.

## Workflow

1. Use evals-router to classify the eval route and assertion contract.
2. Inspect `SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, generated fixtures, knowledge capsules, and latest eval results.
3. Prepare Tessl scenario generation with: `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`.
4. Generate bespoke scenarios with the Tessl scenario workflow when available; treat its output as drafts.
5. Review every draft against `references/gold-scenario-contract.md` before canonical import.
6. Import reviewed cases into `references/evals.yaml` and `references/evals/*.md`; do not import raw target-tile output.
7. Run internal evals and Tessl dry-run staging. Require `scenario-sources.json` to show skill-owned and reviewed generated cases.
8. For behavioral skills, live Tessl readiness requires at least 20 gold-standard structured scenarios, a run-budget preflight, usage score >= 90%, and usage score not below baseline.

## Constraints

- Do not put the exact expected answer in task text, `given`, `should`, or prompt.
- Do not mention Tessl, rubric, criteria, fixture, generated scenario, hidden answer, or "use this skill" in task text.
- Do not score skill-name mentions, file paths, generic quality phrases, or copied rubric text as the primary criterion.
- Do not accept all-green results when baseline ties or beats usage; tighten scenarios or skill behavior first.
- Do not run live Tessl when scenario count, scenario quality, or run-budget evidence is below the gate.
- Redact secrets, tokens, private URLs, credentials, and sensitive local paths from scenario text and run reports.

## Execution Boundaries

- Edit only canonical skill eval assets and references unless the user explicitly approves broader skill changes.
- Treat Tessl-generated scenarios as drafts until reviewed against `references/gold-scenario-contract.md`.
- Keep target-tile or staged Tessl output disposable; import only reviewed cases into canonical sources.
- Do not run live Tessl scoring when dry-run staging, run-budget evidence, or scenario quality gates are missing.

## Failure Mode

If generated scenarios are too easy, classify the failure before changing the skill:
scenario leakage, weak comparator, vague criteria, baseline tie, usage regression, stale scenario, or unsupported hidden dependency.
Fix the scenario set before rerunning live Tessl unless per-scenario evidence proves the skill itself is wrong.

## Validation

- `./bin/ask skills package verify <skill-path> --json --robot`
- `./bin/ask evals run <skill-path> --mode smoke --tessl-live-private --tessl-workspace <workspace> --tessl-live-dry-run --json --robot`
- `./bin/plugin-eval analyze <skill-path> --format json`
- Live Tessl only after dry-run and run-budget gates pass.
- Fail fast at the first failed gate and classify the blocker before rerunning.

## Gotchas

- A high usage score is not enough when baseline ties or beats usage.
- Scenario count can hide weak coverage; require a plausible baseline failure mode for each behavioral scenario.
- User-facing task text must not contain hidden scoring language or exact expected answers.
- Any skill behavior change can make previously good scenarios stale.

## Anti-Patterns

- Making scenarios easier to raise a score.
- Treating a completed live run as readiness when usage ties or trails baseline.
- Importing target-tile drafts without review.
- Reusing generic structure scenarios as behavioral proof.

## Progressive Disclosure

- Read `references/gold-scenario-contract.md` for required shape and anti-easy gates.
- Read `references/contract.yaml` for package contract, run budget, and live Tessl thresholds.
- Read `references/evals.yaml` for starter scenarios that validate this skill.

## See Also

| Skill | When to use together |
|---|---|
| [[evals-router]] | Choose the eval route, assertion contract, and evidence lane before scenario generation |
| [[skill-builder]] | Repair skill gates, check scenario drift, and validate release readiness |
