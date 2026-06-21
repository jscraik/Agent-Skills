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
- KnowledgeOS handoff eval references from
  `~/dev/knowledge-OS/exports/evals/references/evals/*.md` when converting
  portable handoff scenarios into SDK-owned eval assets.
- Latest internal eval, dry Tessl, live Tessl, or Plugin Eval result when available.
- Tessl workspace name and run-budget evidence before any live scoring plan.
- Tessl tile scenario-generation constraints when producing portable `evals/` folders:
  no preinstalled proprietary dependencies, no extra input files, no API keys,
  no interactive follow-up, 10-minute task budget, and file-only grading.
- Tessl tile or registry context when readiness, publishing, installability, or
  workspace distribution is part of the scenario request.
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

1. Confirm SDK setup with `references/sdk-pipeline-setup.md`: use `./bin/ask`,
   check `ask sdk status` when SDK state matters, and keep package, scenario
   quality, eval runner, and Tessl staging proof as separate lanes.
2. Use evals-router to classify the eval route and assertion contract.
3. Inspect `SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, generated fixtures, knowledge capsules, KnowledgeOS handoff eval references, latest eval results, and `scenario-sources.json` when present.
4. Prepare Tessl scenario generation with: `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`.
5. When importing KnowledgeOS handoff eval scenarios, follow
   `references/knowledgeos-handoff-conversion.md`: preserve claim, behavior,
   failure mode, given/should, bad/good answer patterns, fixture path, and
   promotion status as SDK metadata; do not treat export existence as reviewed
   or runtime-ready proof.
6. When the requested output is a Tessl tile eval pack, follow
   `references/tessl-tile-scenario-contract.md`:
   inventory line-level instructions, plan feasible scenarios before writing,
   create only self-contained scenario folders, and put infeasible capabilities
   in `summary_infeasible.json` with no folder.
7. Generate bespoke scenarios with the Tessl scenario workflow when available; treat its output as drafts.
8. Review every draft against `references/gold-scenario-contract.md` before canonical import or tile export.
9. Apply the concrete-evidence check before import: rewrite prompts that ask
   what an agent, user, or maintainer "would" do; deflect praise such as
   "this looks great"; and require a specific artifact, prior failure, current
   workflow, observed behavior, or committed next step that the scorer can see.
10. Import reviewed cases into `references/evals.yaml` and `references/evals/*.md`; do not import raw target-tile output.
11. Run SDK scenario-quality and internal eval lanes before Tessl dry-run staging:
   `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`
   and the relevant `./bin/ask sdk eval run ... --json --robot` command when a
   deterministic dataset or runner is available.
12. Run Tessl dry-run staging only after `scenario-sources.json` shows
    skill-owned and reviewed generated cases.
13. For behavioral skills, live Tessl readiness requires at least 20 gold-standard structured scenarios, a run-budget preflight, usage score >= 90%, and usage score not below baseline.

## Concrete Evidence Check

Treat discovery-style material like scenario source evidence, not validation by
itself. Prefer prompts built from what happened, what exists, or what the agent
must produce. Reject or rewrite drafts that mainly ask for opinions, enthusiasm,
future intent, or generic preference.

- Replace "would you use", "do you think", "could you see", and similar future
  or opinion prompts with a concrete prior incident, current workflow, supplied
  file, failing scorecard, or observable output requirement.
- Treat compliments such as "looks great" or "teams will love it" as weak data;
  require internal eval results, scenario-source review, dry-run staging,
  run-budget evidence, or another concrete proof lane before readiness claims.
- When a source note contains a real past failure, preserve its concrete details
  as task context while moving expected moves, bad patterns, and good patterns
  into hidden acceptance metadata.

## Eval-Result Diagnosis

When the input is an eval-improvement scenario, classify every criterion before
writing fixes or scenarios:

- Bucket A, working: with-context score is at least 80% of max and clearly above baseline.
- Bucket B, tile gap: baseline and with-context are both below 80%; the tile or
  context does not teach the criterion yet.
- Bucket C, redundant: baseline is already at least 80%; the scenario may not
  measure tile lift.
- Bucket D, regression: with-context is lower than baseline; investigate this
  before ordinary tile gaps because context is actively confusing the agent.

For Bucket B and D items, read the relevant `criteria.json` and tile or context
files, then show the proposed file edits before applying them when the user asks
for a preview. Keep fixes minimal, preserve Bucket A behavior, and rerun the
same eval lane after committing only changed files.

## Lift Curation

When curating existing scenarios, calculate lift as
`with_context_score - baseline_score`. Prefer lift over aggregate attainment.
Measure retire decisions on the floor model for the consumer spectrum; a strong
solver's no-lift result is not enough to retire a scenario when the floor model
still benefits.

For weak or no lift, diagnose the cause before changing files:

- universal competence: retire only when no plugin-specific replacement exists;
- task leaked the technique: rewrite `task.md` and keep the criterion;
- criteria grade universal competence: rewrite `criteria.json` to check the
  specific skill-prescribed behavior.

For non-zero lift with imperfect with-context scores, decide whether the owner is
the skill, task, or criteria before editing.

## Constraints

- Do not put the exact expected answer in task text, `given`, `should`, or prompt.
- Do not mention Tessl, rubric, criteria, fixture, generated scenario, hidden answer, or "use this skill" in task text.
- Do not score skill-name mentions, file paths, generic quality phrases, or copied rubric text as the primary criterion.
- Do not treat opinions, compliments, future promises, or "would use" answers as
  scenario-quality evidence.
- Do not accept all-green results when baseline ties or beats usage; tighten scenarios or skill behavior first.
- Do not run live Tessl when scenario count, scenario quality, or run-budget evidence is below the gate.
- Redact secrets, tokens, private URLs, credentials, and sensitive local paths from scenario text and run reports.
- Do not assume scenario graders can see tool logs, chat transcripts, or process
  traces; require file artifacts when workflow evidence must be scored.
- Do not create scenario folders for infeasible capabilities; record them only in
  `summary_infeasible.json`.
- Do not treat local Tessl lint/review, local install state, Registry metadata,
  workspace membership, publication, or repo-local tile presence as proving any
  other lane unless current evidence explicitly joins them.
- Do not collapse eval analysis, patch application, commit state, and rerun
  results into one proof claim; report each lane with its own evidence.
- Do not retire low-lift scenarios from a strong solver until the floor model
  shows near-zero lift or the scenario has no skill-specific replacement.

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
- For behavioral skills, run Tessl dry-run staging only after `references/evals.yaml`, reviewed `references/evals/*.md` fixtures, and `scenario-sources.json` prove the minimum gold-scenario set exists.
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
