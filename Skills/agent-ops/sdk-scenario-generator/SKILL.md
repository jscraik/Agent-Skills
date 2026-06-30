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
  compatible_roles:
    - default
    - worker
    - skill-inspector
  runtime_needs:
    - target skill
    - references/evals.yaml
    - references/contract.yaml
    - Tessl dry-run staging
---

# SDK Scenario Generator

Create gold-standard Skills SDK scenarios, then stage them for internal evals and Tessl without making the evals easy to game.

## Philosophy

- Scenario count is a floor, not quality proof.
- SDK scenario-quality and Tessl live-private staging must use the same
  behavioral quality gate; a scenario blocked by Tessl must also block SDK
  scenario-quality promotion.
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
- `references/contract.yaml`, `references/evals.yaml`, and selected
  `references/evals/*.md` fixture notes.
- KnowledgeOS capsule or handoff evidence only when the task requires it; route
  through `references/source-context.yaml` and
  `references/knowledge-capsule-routing.md`.
- Latest internal, oss-local, oss-cloud, dry Tessl, live Tessl, or Plugin Eval
  receipt when the task asks for diagnosis or readiness.
- Tessl workspace, run-budget, registry, or tile context only for the named
  Tessl lane; keep package shape, registry, runtime, and live proof separate.

## Outputs

- Every machine-readable output or scenario inventory must include
  `schema_version` so downstream validators can reject stale or ambiguous
  shapes deterministically.
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

1. Confirm the named gate with `references/sdk-pipeline-setup.md`; start with
   the two or three surfaces needed for that gate and widen only after evidence.
2. Use evals-router to choose assertion, scorer-quality, and calibration checks.
3. Inspect the target skill, contract, eval YAML, selected fixture notes,
   selected KnowledgeOS capsule or handoff evidence, and latest receipts.
4. Review drafts against `references/gold-scenario-contract.md` before import.
   Apply concrete-evidence, measurement-quality, break-test, anti-easy, and
   registry-boundary checks.
5. Import only reviewed cases into canonical eval assets; never import raw
   generated output.
6. Run package, scenario-quality, scorer-quality, and scorer-calibration gates
   before oss-local, oss-cloud, Tessl local proof, dry Tessl, or live Tessl.
7. Use read-only Codex profile lanes for behavioral proof: `oss-local` before
   `oss-cloud`. A wrapper counts only when its receipt proves
   `codex_exec_invoked=true` and the matching profile. `fast` is smoke only.
8. Treat Tessl as staged confirmation: local proof execute receipt, dry-run
   receipt, and live score receipt stay separate from internal SDK proof.

When checking behavior proof, use KnowledgeOS eval scenario IDs wired through
`references/evals.yaml`; vendored scenario files are evidence, not an alternate
eval runner.

## Constraints

- Do not leak exact expected answers or scoring mechanics in task text.
- Do not score skill-name mentions, file paths, generic quality phrases, or copied rubric text as primary proof.
- Do not treat opinions, compliments, future promises, or "would use" answers as quality evidence.
- Do not collapse unrelated measured dimensions into one aggregate score or readiness claim.
- Do not ship happy-path-only suites or accept all-green results when baseline ties or beats usage.
- Do not run live Tessl when scenario count, quality, or run-budget evidence is below the gate.
- Redact secrets, tokens, private URLs, credentials, and sensitive local paths from scenario text and run reports.
- Do not assume graders can see tool logs, chat transcripts, or process traces.
- Do not create scenario folders for infeasible capabilities; record them only in `summary_infeasible.json`.
- Do not treat Tessl lint/review, install state, Registry metadata, workspace
  membership, publication, or repo-local tile presence as proving any other lane.
- Do not install, update, or trust a Registry tile from review score alone.
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
Use concrete evidence, named measurement constructs, realistic break tests, and
Bucket A/B/C/D diagnosis; see `references/gold-scenario-contract.md` and
`references/eval-improvement-contract.md` for anchors.

## Validation

- `./bin/ask skills package verify <skill-path> --json --robot`
- `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`
- `codex exec --profile oss-local` then `codex exec --profile oss-cloud`, or
  SDK receipts proving `codex_exec_invoked=true` and the matching profile.
- `codex exec --profile fast` only as a quick smoke/check lane.
- `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --execute --json --robot`
- `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot`
- `./bin/plugin-eval analyze <skill-path> --format json`
- Run Tessl scenario preparation only when workspace auth/project link exists.
- Live Tessl only after Tessl local proof, dry-run staging, and run-budget gates.
- Fail fast: stop at first failed gate; do not proceed. Classify the blocker
  before rerunning.

## Gotchas

- `realistic: true` is not enough; each realistic case needs concrete task
  context, observable artifacts, and a plausible weak-answer path.
- A forbidden-command list is scorer metadata, not permission to execute those
  commands.
- If live capacity, workspace link, or project identity cannot be verified,
  record the blocker and continue internal repair lanes.
- Bucket D regressions can mean the context makes the agent worse; inspect
  contradictions before adding more instructions.

## Anti-Patterns

- Importing raw generated scenarios directly into `references/evals.yaml`.
- Fixing a live-score gap by weakening the prompt or criteria.
- Treating a package-shape pass, Registry score, or Tessl auth state as live
  behavioral readiness.
- Expanding a repair loop across unrelated skill, scorer, and runtime surfaces
  before one failure cluster has a classified owner.

## Examples

- "technical-writer oss-local is stuck at 15/20": classify one scenario owner,
  name the smallest TDD guardrail, and keep oss-cloud/Tessl blocked.
- "KnowledgeOS exported eval references": preview ingest, reject warnings before
  apply, import reviewed cases only, then run package and scenario quality.
- "Tessl beat neither baseline nor 90 percent": classify Bucket D regressions
  first and rerun the same lane only after repair evidence.

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
- Read `references/source-context.yaml` to identify the allowed KnowledgeOS
  source surfaces before loading capsules.
- Read `references/knowledge-capsule-routing.md` to select one top-level
  capsule facet before opening capsule content.
- Read `references/knowledge-capsule.manifest.yaml` only after routing selects
  a bounded capsule or fixture.
- Read `references/contract.yaml` for package contract, run budget, and live Tessl thresholds.
- Read `references/evals.yaml` for starter scenarios that validate this skill.
