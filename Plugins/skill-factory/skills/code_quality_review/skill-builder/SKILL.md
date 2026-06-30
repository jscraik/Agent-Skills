---
name: skill-builder
description: "Reviews and improves SKILL.md packages by fixing audit findings, triggers, examples, evals, token budget, release proof, safety verdicts, comparator/baseline choices, and bounded code-lens hardening. Use when the user says improve a skill, fix a skill file, review SKILL.md, raise Tessl score, reduce context cost, add skill evals, or prepare a plugin skill for release."
metadata:
  version: "1.0.0"
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  provenance: frontmatter:Agent Skills Team:2026-05-15:canonical-source
  share_readiness: ready
  review_cadence: quarterly
  last_reviewed: "2026-05-15"
  metadata_source: frontmatter
  compatible_roles:
    - default
    - worker
    - skill-inspector
  runtime_needs:
    - repo-owned skill source path
    - ./bin/ask skills audit and eval wrappers
    - python3 standard library validators
---

# Skill Builder

Repair one failing skill gate at a time.

## Philosophy

Prefer one evidence-backed repair over broad rewriting. A score is useful only when the artifact, command, baseline, and failed contract are preserved.

## First-Principles Gate

- Desired outcome: repair an existing skill through the Skills SDK proof ladder without replacing release evidence with prose.
- User-specific constraints: use repo wrappers, keep oss-local before oss-cloud, keep Tessl live as confirmation only, and record lessons as guardrails.
- Rejected copied assumption: a better SKILL.md alone proves release readiness.
- Fundamental constraints: existing skill source is canonical; each failed gate owns the next patch; warnings must be repaired before promotion.
- Smallest effective mechanism: patch the smallest failed skill, reference, eval, or validator surface that changes the failing gate.
- Artifact decision: IMPROVE_EXISTING.
- Rejected alternatives: rewriting the whole skill, running Tessl live before SDK receipts, or ignoring scenario drift.
- Evidence required: factory gate receipt, package verify receipt, scenario-quality receipt, and oss-local receipt before oss-cloud.
- Validation proof: rerun the failed gate after each repair.
- Stop or pivot condition: after three flat repair loops, stop with blocker_notes and classify the owning gate.

## When To Use

Use for SKILL.md repair, skill eval hardening, release proof, Tessl score improvement, reference quality fixes, and plugin-skill readiness work.

## Inputs

- Unsafe request: `Safety Verdict: safety constraints intact; refusing unsafe request`.
- Missing target, gate/score, or edit authority: ask `Round 1 question: Which canonical target should I patch? If canonical and .agents/** paths both exist, confirm the source before edits.`.

## Outputs

Return exact validation commands, outcomes, changed files, rollback path, and any evidence artifact locations. For blocked release-eval cases, put the failed Repair Map item in `blocker_notes`.


## Skill Summary

Before edits, confirm target, failing gate/score, allowed edits, validation command, and what to change.

Apply the context-disposition policy: preserve valuable context by relocating it with explicit signposting.

Read when: repairing a skill gate, trimming SKILL.md, moving detail into references, or deciding whether context should remain in the entrypoint.

Context disposition: relocate important still-valid context to `references/`; intentionally discard stale, duplicated, unsafe, inappropriate, superseded, or low-signal text.

## Workflow

1. Find the canonical source and confirm edits are allowed.
2. For review, handoff, rollback, or validation-only work, return the Outputs contract and stop.
3. Run the focused gate; record baseline score, artifact path, and first blocker.
4. Apply one Repair Map change, then rerun the same gate.
5. If score/blocker is flat, undo or narrow and try the next map item. After three flat loops, stop with `blocker_notes:`.
6. On green, run final gates. If any fail, name the gate and next patch target; do not claim release readiness.

~~~bash
./bin/ask skills external-review <target> --audit-level compat --json --robot
~~~

Pass only on parsed fields: ask audit/package/release `status == "success"`; external-review lint ok plus score `>= 90` (`95+` target); Tessl live-private usage, the private Tessl workspace/project evaluation lane, `>= max(0.90, baseline)` only when the workspace/project link is available. On failure, patch the first `errors[]`/blocker. Exit code alone never passes.

Before any live-private Tessl score for a created, updated, installed, refactored, or skillified candidate, run `./bin/ask sdk start <skill-path> --json --robot`, then the SDK proof ladder in order: strict audit, package verify, security risk-modes, scenario-quality, scorer-quality, scorer-calibration, oss-local, oss-cloud, Tessl local proof with `--execute`, Tessl live-private dry-run, then handoff-readiness. The improve-skill Tessl lanes use the product workspace `jscraik`, and every staged plugin starts `private: true` until a separate publish lane changes visibility. Treat oss-local as the 70-75 internal discovery band, oss-cloud as the iterative path to >=90 internal success, and Tessl live as external confirmation at >=90 and >= baseline.
For scenario prep, use sdk-scenario-generator with the installed Tessl scenario skill to generate bespoke scenarios for that exact skill, review them, and import useful cases into canonical skill assets. The live-private lane must stage both `references/evals.yaml` skill-owned cases and reviewed generated scenarios from `references/evals/*.md`; structure-only package checks are the only explicit exception.
After every skill change, review scenario drift before live scoring: compare changed triggers, constraints, outputs, references, and behavior claims with `references/evals.yaml` and `references/evals/*.md`, then classify scenarios as keep, update, add, or remove.
Before live Tessl scoring, bump the skill or plugin package version whenever the staged package changed since the previous live run. Identical retry runs may reuse the same version, but changed SKILL.md, scenarios, contract, or runtime-context references must not be scored under the previous tile version.
Behavioral skills need at least 20 gold-standard structured scenarios before live Tessl readiness scoring. Generic structure/layout scenarios can prove SDK shape, but bespoke scenarios must prove the skill-specific behavior. Do not pad the count with duplicate, weak, or scoring-mechanics scenarios.
Before any live Tessl run, check the workspace run budget. Treat 300 live eval runs as the operator-provided limit unless Tessl reports a different operator-approved limit, and preserve a 20-run remediation reserve. If capacity is unknown or below reserve, use dry-run/local gates instead of burning a live run.

## Repair Map

- Repeated guidance -> delete the duplicate `SKILL.md` sentence; same score gate improves.
- Vague validation -> add `Command: ... -> pass|fail|blocked`; audit/release `status == "success"`.
- Missing recovery -> add the named failed-gate branch; rerun that gate.
- Weak eval/reference -> patch cited `references/**`; package verify `reference_quality:true`, including `reference_heading_invocable` for Markdown references and vendored KnowledgeOS capsule bodies.
- Unsafe request -> emit `Safety Verdict:`; make no edits.
- Package handle -> keep `codex-eval-creation-loop` and `software-literature-expert-lens-pack`; use [package repairs](./references/package-specific-repairs.md).
- Tessl or KnowledgeOS capsule handling -> load source handle `Plugins/skill-factory/references/tessl-knowledgeos-capsule.md`, prefer plugin-first Tessl layout, and keep KnowledgeOS evidence, Skill Factory package validation, Tessl review/eval proof, registry state, and runtime visibility as separate lanes.

Example cycle: fail `errors[0].message: missing Output Contract`.

```diff
+## Outputs
+validation_evidence: [{command: "<exact command>", outcome: pass|fail|blocked}]
```

Proof: rerun the failed gate until its pass field is green, then record the artifact.

## Constraints

- Redact secrets and sensitive data by default in prompts, outputs, temporary evidence, and copied artifacts.
- Never suppress failed-gate evidence, hide blockers, publish/upload, delete evals, or widen permissions.
- Keep detailed examples in `references/`.

## Execution Boundaries

- Edit canonical skill sources, package-owned references, and eval fixtures only after confirming path ownership.
- Use repo wrappers first. Patch scripts only when the wrapper failure proves the script is the repair target.
- Tessl lanes stage controlled copies under `/tmp`; preserve temp evidence and never point Tessl at live repo source.
- For create/update/install/refactor/skillify work, do not run live Tessl scoring until bespoke generated scenarios have been prepared, reviewed, imported, and counted in the staged `scenario-sources.json`; use `./bin/ask evals prepare-tessl-scenarios <target> --tessl-workspace jscraik --json --robot` for the prep lane.
- If Tessl live finds scenario, rubric, judge, or package-shape failures, classify that as an upstream SDK pipeline defect and patch the deterministic guardrail before rerunning from oss-local.
- Route basic skill-behavior, reference, and security failures to the owning skill/source repair path before rerunning.
- Do not treat `./bin/ask evals run --runner codex`, preview-only Tessl local proof, or a Tessl dry-run command string as handoff evidence. Handoff proof requires SDK receipts for `oss-local`, `oss-cloud`, `tessl-local-proof --execute`, and a dry-run receipt with `tessl_eval.dry_run=true`.
- When a skill changes, do not reuse the old scenario set blindly; update, add, or remove scenarios so the eval suite still matches the skill contract.
- For behavioral skill readiness, do not run live Tessl until the canonical scenario set has at least 20 gold-standard structured scenarios. Runs below 20 are transition diagnostics, not readiness proof.
- Do not run live Tessl when the workspace is near the 300-run limit or would consume the 20-run remediation reserve.
## Failure Mode

If three repair loops leave the same score or blocker unchanged, stop and return `blocker_notes:` with the failed gate, artifact path, and next smallest patch.

## Validation

- Fail fast: stop at the first failed gate, do not proceed to later gates, and parse JSON fields instead of exit code alone.
- Required release evidence: audit/package/release success, external-review lint ok, Tessl review score `>= 90`, and live-private usage `>= max(0.90, baseline)` when the workspace/project link is available.
- Live-private release evidence also requires scenario-source proof: `scenario-sources.json` must show skill-owned eval cases and reviewed generated fixture cases, unless the package contract explicitly declares a structure-only exception.
- Live-private release evidence for behavioral skills requires `scenario-sources.json` to show at least 20 gold-standard structured scenarios.
- Live-private release evidence requires Tessl run-budget proof or an explicit blocker that preserves the 300-run operator-provided workspace limit and 20-run remediation reserve.
- Live-private release evidence requires `./bin/ask sdk eval handoff-readiness --skill <target> --preview --json --robot` to pass for the current candidate.
- Live-private release evidence requires scenario drift review after the latest skill change; stale or obsolete scenarios block professional readiness even when the live run completes.
- References and scripts must be checked when they affect the skill behavior; weak supporting material blocks release claims. Markdown reference and capsule-body H1 headings must be specific, filename-aligned, and invocable before OSS, Tessl, or registry movement.

## Gotchas

- Do not call a lower score “better” unless the reported improvement over baseline is positive.
- Do not treat a 100% unit row as release success when the tile score or baseline comparison is worse.
- Do not let package-specific repair details crowd the entrypoint; keep them in verified references.

## Anti-Patterns

- Editing only `SKILL.md` while leaving bad references, scripts, or eval fixtures untouched.
- Creating fresh temp directories by deleting old Tessl evidence.
- Claiming pass from a completed command when parsed score, baseline, or readiness fields fail.
- Running live Tessl directly after editing a skill without first refreshing or confirming bespoke generated scenarios for that skill.

## Examples

- `Improve skill-builder after Tessl review score 88`: patch one finding, preserve `/tmp/ask-tessl-*`, rerun external review, and report score versus threshold.
- `Fix release eval for a plugin-owned skill`: update canonical references/evals, run package verify, then live-private against the plugin project.
- `A skill scores 100% on one unit but 68% overall`: treat the tile score and baseline comparison as blockers before claiming improvement.

See [repair examples](./references/repair-examples.md) and [package repairs](./references/package-specific-repairs.md) for more patch patterns.

## References

- Policies: [generated artifacts](./references/generated-artifact-policy.md), [audit boundaries](./references/repo-local-audit-boundaries.md), [eval contract](./references/eval-enforcement-contract.md).
- Templates: [discovery interview](./references/discovery-interview.md), [repair examples](./references/repair-examples.md), [package repairs](./references/package-specific-repairs.md).
- Factory gate: `Infrastructure/references/first-principles-factory-gate.md`.
- Helper scripts: `scripts/` supports repo wrappers; invoke wrappers first unless repairing a script failure.
- References and scripts are package-verified support and must pass `reference_quality:true`.
- Tessl/KnowledgeOS source handle: `Plugins/skill-factory/references/tessl-knowledgeos-capsule.md`; load only when the target change depends on Tessl plugin layout, registry/install behavior, review/eval proof, MCP packaging, workspace/project setup, security policy, or Skills SDK handoff patterns.
