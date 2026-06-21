---
name: sdk-scenario-generator
description: "Create, review, and maintain gold-standard Skills SDK eval scenarios before internal evals, dry Tessl staging, or live private Tessl scoring. Use when creating or updating a skill, writing skill tests, adding eval cases, importing KnowledgeOS or Tessl suggestions, checking scenario drift, or hardening evals that are too easy."
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
  compatible_roles: "default, worker, skill-inspector"
  runtime_needs: "target skill, references/evals.yaml, references/contract.yaml, Tessl dry-run staging"
---

# SDK Scenario Generator

Create gold-standard Skills SDK scenarios, then stage them for internal evals and Tessl without making the evals easy to game.

## Philosophy

- Scenario count is a floor, not quality proof.
- A good scenario makes the right skill useful and a strong baseline plausibly wrong.
- Task text is for the agent; criteria are for the scorer. Do not leak the answer into the task.
- Strong scenarios are grounded in concrete past or current evidence, not
  opinions, compliments, hypotheticals, or future promises.

## When To Use

- Creating, installing, or updating a skill that will be evaluated.
- Adding KnowledgeOS capabilities with suggested eval scenarios.
- Turning Tessl scenario-skill output into repo-owned SDK eval assets.
- Checking whether scenarios are stale after a skill change.
- Live private Tessl readiness, dry Tessl staging, or internal eval hardening.

## Avoid

- Do not use this skill to work around a failed live eval by making scenarios easier.
- Do not use it for structure-only package checks unless the skill contract explicitly declares that exception.

## Required inputs

- Target skill path and latest `SKILL.md`.
- `references/contract.yaml`, `references/evals.yaml`, and any `references/evals/*.md` fixtures.
- Knowledge capsules or extracted evidence when the skill was enriched from KnowledgeOS.
- Operator-provided KnowledgeOS handoff eval references when converting
  portable handoff scenarios into SDK-owned eval assets; do not assume a
  user-home path.
- Latest internal eval, dry Tessl, live Tessl, or Plugin Eval result when available.
- Tessl workspace name and run-budget evidence before any live scoring plan.
- Tessl tile scenario-generation constraints when producing portable `evals/` folders:
  no preinstalled proprietary dependencies, no extra input files, no API keys,
  no interactive follow-up, 10-minute task budget, and file-only grading.
- Tessl tile or registry context when readiness, publishing, installability, or
  workspace distribution is part of the scenario request.
- For Registry-sourced context, the package id, pinned version or commit source,
  publisher/workspace, install state, and visible quality, impact, and security
  signals. Treat high or critical security warnings as blockers until the
  operator accepts them.
- Latest eval result details when scenarios are intended to diagnose or improve
  a tile or context pack: criterion name, max score, baseline score,
  with-context score, scenario path, and compare output.
- Skills SDK setup state: `./bin/ask` availability, `ask sdk status`,
  package verification, scenario-quality preview, SDK eval runner, and scenario
  source evidence.

## Outputs

- Scenario inventory with keep, update, add, or remove decisions.
- Gold-standard scenario drafts or canonical eval patches.
- Tessl tile scenario assets when requested:
  `instructions.json`, `summary.json`, `summary_infeasible.json`, and
  sequential `scenario-N/{task.md,criteria.json,capability.txt}` folders.
- Eval-result diagnosis when requested: Bucket A/B/C/D classification,
  prioritized fix plan, file-to-fix hypotheses, and before/after rerun plan.
- Lift analysis when curation is requested: floor-model lift, weak/no-lift
  cause, skill/task/criteria owner, and keep/rewrite/retire decision.
- Weak-eval critique and anti-easy notes.
- Tessl run-budget evidence or blocker.
- Internal eval, dry Tessl, and live Tessl readiness summary.

## Workflow

1. Confirm SDK setup with `references/sdk-pipeline-setup.md`; keep package,
   scenario quality, eval runner, dry-run, and live Tessl proof separate.
2. Use evals-router to choose the assertion contract before writing scenarios.
3. Inspect the target `SKILL.md`, `references/contract.yaml`,
   `references/evals.yaml`, available fixture notes, KnowledgeOS handoff
   evidence, latest eval results, and `scenario-sources.json` when present.
4. Generate drafts only after setup evidence. Use
   `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`
   when Tessl scenario prep is available.
5. Review drafts against `references/gold-scenario-contract.md`; apply the
   concrete-evidence, measurement-quality, break-test, anti-easy, and
   Registry-boundary checks before canonical import.
6. Import only reviewed cases into `references/evals.yaml` or reviewed fixture
   notes under `references/evals/`; do not import raw generated output.
7. Run scenario-quality, internal evals when available, package verification,
   and external review before any readiness claim.
8. For behavioral skills, live Tessl readiness also requires at least 20
   gold-standard scenarios, run-budget proof, usage score >= 90%, and usage not
   below baseline.

## Minimal Scenario Shape

```yaml
- id: pressure-readiness-overclaim
  category: pressure
  eval_modes: [smoke, release]
  given: Local package verification passed, but hosted CI was not checked.
  should: Report local proof separately and leave CI readiness unclaimed.
  prompt: Summarize release readiness from the supplied package result.
  acceptance:
  - type: expected_signal
    value: Separates local package proof from hosted CI and live Tessl evidence.
  - type: expected_signal
    value: Does not claim CI passed, live Tessl passed, or merge readiness.
  deterministic_checks:
    forbidden_commands: [npx, "tessl skill publish"]
```

## Concrete Evidence Check

Use concrete source evidence, not opinions, praise, hypotheticals, or future
intent. Keep observed facts in the task and scorer-only expectations in
acceptance metadata. Detailed gates and examples live in
`references/gold-scenario-contract.md`.

## Measurement Quality Check

Name the construct each scenario measures. Split unrelated dimensions into
separate criteria and never average local proof, Registry quality, user
preference, and live usage into one fake readiness score. See
`references/gold-scenario-contract.md` and `references/eval-improvement-contract.md`.

## Break-Test Check

Add realistic pressure for invalid inputs, boundaries, sequencing, shared state,
stale assets, file problems, and permission or capacity failures. Every break
test must remain scoreable from final artifacts. See
`references/gold-scenario-contract.md`.

## Eval-Result Diagnosis

When the input is an eval-improvement result, classify criteria as Bucket A/B/C/D
before editing. Bucket D regressions outrank ordinary gaps. Use
`references/eval-improvement-contract.md` for bucket definitions, consistency
audits, preview rules, and rerun evidence.

## Lift Curation

For curation, prefer `with_context_score - baseline_score` over aggregate
attainment. Do not retire a case from a strong solver alone; check floor-model
lift and diagnose whether the owner is the skill, task, or criteria. Details:
`references/sdk-pipeline-setup.md` and `references/eval-improvement-contract.md`.

## Constraints

- Do not put the exact expected answer in task text, `given`, `should`, or prompt.
- Do not mention Tessl, rubric, criteria, fixture, generated scenario, hidden answer, or "use this skill" in task text.
- Do not score skill-name mentions, file paths, generic quality phrases, or copied rubric text as the primary criterion.
- Do not treat opinions, compliments, future promises, or "would use" answers as scenario-quality evidence.
- Do not collapse unrelated measured dimensions into one aggregate score.
- Do not ship only happy-path scenarios.
- Do not accept all-green results when baseline ties or beats usage; tighten scenarios or skill behavior first.
- Do not run live Tessl when scenario count, scenario quality, or run-budget evidence is below the gate.
- Redact secrets, tokens, private URLs, credentials, and sensitive local paths from scenario text and run reports.
- Do not assume graders can see tool logs, chat transcripts, or process traces.
- Do not create scenario folders for infeasible capabilities; record them only in `summary_infeasible.json`.
- Do not treat local Tessl lint/review, local install state, Registry metadata,
  workspace membership, publication, or repo-local tile presence as proving any
  other lane unless current evidence explicitly joins them.
- Do not install, update, or trust a Registry tile from review score alone.
- Do not collapse eval analysis, patch application, commit state, and rerun results into one proof claim.
- Do not retire low-lift scenarios from a strong solver alone.

## Execution Boundaries

- Edit only canonical skill eval assets and references unless the user explicitly approves broader skill changes.
- Treat Tessl-generated scenarios as drafts until reviewed against `references/gold-scenario-contract.md`.
- Keep target-tile or staged Tessl output disposable; import only reviewed cases into canonical sources.
- When exporting a tile eval pack, keep every task self-contained: inline any
  required input files in `task.md`, avoid heavyweight downloads, and require
  cleanup of files larger than 50 MB.
- Do not run live Tessl scoring when dry-run staging, run-budget evidence, or scenario quality gates are missing.

## Failure Mode

If generated scenarios are too easy, classify the failure before changing the skill:
scenario leakage, weak comparator, vague criteria, baseline tie, usage regression, stale scenario, or unsupported hidden dependency.
Fix the scenario set before rerunning live Tessl unless per-scenario evidence proves the skill itself is wrong.

## Validation

- `./bin/ask skills package verify <skill-path> --json --robot`
- `./bin/plugin-eval analyze <skill-path> --format json`
- Run Tessl scenario preparation only when the workspace auth/project link is available.
- For behavioral skills, run Tessl dry-run staging only after `references/evals.yaml`, reviewed fixture notes, and `scenario-sources.json` prove the minimum gold-scenario set exists.
- Live Tessl only after dry-run staging and run-budget gates pass.
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
- Read `references/tessl-tile-scenario-contract.md` when producing portable
  `evals/` folders for Tessl tile scoring.
- Read `references/tessl-registry-boundaries.md` when scenarios involve
  Tessl tiles, `plugin.json`, registry publication, workspace access, installs,
  or repo-local versus registry distribution.
- Read `references/eval-improvement-contract.md` when scenarios involve
  diagnosing eval results, fixing tile/context regressions, committing changes,
  or rerunning Tessl evals.
- Read `references/sdk-pipeline-setup.md` before making SDK readiness claims or
  choosing validation commands for this skill.
- Read `references/knowledgeos-handoff-conversion.md` before converting
  KnowledgeOS handoff eval markdown into SDK scenario YAML or reviewed fixtures.
- Read `references/contract.yaml` for package contract, run budget, and live Tessl thresholds.
- Read `references/evals.yaml` for starter scenarios that validate this skill.

## See Also

| Skill | When to use together |
|---|---|
| [[evals-router]] | Choose the eval route, assertion contract, and evidence lane before scenario generation |
| [[skill-builder]] | Repair skill gates, check scenario drift, and validate release readiness |
