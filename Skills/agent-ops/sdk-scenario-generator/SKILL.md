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

Create gold-standard Skills SDK scenarios that survive internal checks, OSS lanes, and Tessl quality filtering without leaking the answer.

## When To Use

- Create, import, repair, or retire `references/evals.yaml` cases for a skill.
- Turn KnowledgeOS, Tessl, or plugin-generated scenario drafts into canonical SDK evals.
- Diagnose low lift, baseline wins, Tessl quality-filter rejection, or oss-local/oss-cloud failures.
- Prepare dry Tessl or live private Tessl staging after internal gates pass.

Do not use this skill to make scenarios easier after a failed eval. Fix the skill, task, criteria, scorer, fixture, or runtime owner that the evidence names.

## Inputs

- Target skill path, latest `SKILL.md`, `references/contract.yaml`, and `references/evals.yaml`.
- Selected `references/evals/*.md` fixture notes or KnowledgeOS capsule evidence only when routed by the task.
- Latest internal, oss-local, oss-cloud, dry Tessl, live Tessl, or Plugin Eval receipt when diagnosing quality or readiness.
- Tessl `qualityFilterStatus`, leakage, scenario-value, baseline, and with-context evidence when Tessl rejected or down-scored scenarios.

## Outputs

- Scenario inventory with keep, rewrite, retire, or add decisions.
- Canonical eval patches or reviewed scenario drafts with `schema_version`.
- Owner classification for failures: skill, task, criteria, scorer, fixture, runtime, or pipeline guardrail.
- Tessl tile scenario assets when requested: `instructions.json`, `summary.json`, `summary_infeasible.json`, and `scenario-N/{task.md,criteria.json,capability.txt}`.
- Readiness summary that keeps internal proof, OSS proof, Tessl dry-run, live Tessl, Registry, and publication lanes separate.

## Workflow

1. Confirm the named gate in `references/sdk-pipeline-setup.md`; load only the target skill, contract, eval YAML, selected fixtures, and latest relevant receipt.
2. Classify each failing case before editing: leakage, low scenario value, weak comparator, vague criteria, missing fixture, baseline tie, baseline win, stale task, hidden dependency, unsupported assertion, or runtime mismatch.
3. Treat Tessl rejection as a pipeline defect until SDK scenario-quality also blocks that class. Patch the shared quality gate or generator contract before rerunning live Tessl.
4. Feed repeat failures back to the start of the pipeline. Patch the source fixture, scenario adapter, scenario-quality gate, or skill package before `oss-local`; do not spend `oss-cloud` or live Tessl runs rediscovering a shape defect.
5. Keep task text realistic and agent-facing. Do not include `Required behavior`, `Failure mode`, `Return these exact fields`, copied criteria, long expected answers, or scoring mechanics in the visible task.
6. Keep criteria scorer-facing. Put expected behavior, failure modes, and rubric dimensions in acceptance criteria or hidden metadata, not in `prompt` or exported `task.md`.
7. For generated fixture scenarios that score a packaged skill, ask the runner to score package instructions and references, not a fresh chat response. Criteria must not expect `raw_response`, `final.json`, or observable response text unless the runner actually creates that artifact.
8. Keep low-value unrelated negatives in local routing smoke only. Release/Tessl negatives must test realistic safety, authority, evidence, boundary, or should-not-trigger pressure.
9. Use concrete fixtures for repo-audit scenarios. If the case asks for file-path evidence, command evidence, or repo state, inline the relevant files in `task.md` or provide a staged fixture artifact.
10. Import only reviewed cases into canonical eval assets; never copy raw generated scenarios into `references/evals.yaml`.
11. Run package verify, scenario-quality, scorer-quality, and scorer-calibration before oss-local, oss-cloud, Tessl local proof, dry Tessl, or live Tessl.
12. Use `oss-local` before `oss-cloud`; `fast` is smoke only. Treat Tessl as staged confirmation after internal gates and run-budget proof.

## Failure Mode

Stop before the next gate when:

- Tessl rejects any scenario for leakage, low value, hidden dependency, or infeasibility while SDK scenario-quality still marks it promotion-ready.
- A task can be answered by copying the prompt, naming the skill, citing a fixture path, or repeating generic quality language.
- A scenario requires hidden files, credentials, process logs, tool traces, or side effects the runner cannot observe.
- A Bucket D regression shows context made the answer worse than baseline.
- Scenario-quality, scorer-quality, scorer-calibration, dry Tessl, or live Tessl evidence is missing for the claimed gate.

When blocked, classify the owner and patch only that surface before rerunning the same gate.

## Gotchas

- Execution boundaries matter: internal SDK receipts, OSS runs, Tessl local proof, live Tessl scoring, Registry state, and publication are separate proof lanes.
- Do not make a scenario easier to pass when the named owner is the skill, fixture, runner, scorer, or quality gate.

## Execution Boundaries

- Scenario authoring updates canonical eval assets; it does not prove OSS, Tessl, Registry, or publication state.
- Live Tessl work starts only after internal receipts and workspace identity are current, staged, and separated from publication proof.

## Validation

- `./bin/ask skills package verify <skill-path> --json --robot`
- `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`
- `codex exec --profile oss-local`, then `codex exec --profile oss-cloud`, or SDK receipts proving `codex_exec_invoked=true` and the matching profile.
- `codex exec --profile fast` only for quick smoke checks.
- `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --execute --json --robot`
- `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot`
- `./bin/plugin-eval analyze <skill-path> --format json`

Do not run live Tessl until scenario-quality, scorer-quality, scorer-calibration, staged Tessl proof, run-budget proof, and project/workspace identity are current and separated from publication or Registry proof.

Completion evidence is the current gate receipt or command output with explicit pass, fail, or blocked status and the scenario ids affected.

## References

- `references/gold-scenario-contract.md`
- `references/eval-improvement-contract.md`
- `references/tessl-tile-scenario-contract.md`
- `references/tessl-registry-boundaries.md`
- `references/sdk-pipeline-setup.md`
- `references/knowledgeos-handoff-conversion.md`
- `references/source-context.yaml`
- `references/knowledge-capsule-routing.md`
- `references/knowledge-capsule.manifest.yaml`
- `references/contract.yaml`
- `references/evals.yaml`
