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

Repair one failing skill gate at a time. Preserve the artifact, command,
baseline, failed contract, patch, and rerun evidence for every repair.

## When To Use

Use for SKILL.md repair, skill eval hardening, release proof, Tessl score
improvement, reference quality fixes, and plugin-skill readiness work.

## Inputs

- Canonical skill source path, failing gate or score, allowed edit scope, and
  required validation command.
- Baseline package, audit, eval, Tessl, or review receipt when a score or gate
  is being improved.
- Factory gate answers from references/repair-policy.md before create, harden,
  refactor, skillify, plugin, hook, or package-design work.
- Redact secrets and sensitive data by default in prompts, outputs, temporary
  evidence, copied artifacts, and review notes.
- For unsafe requests, return Safety Verdict: safety constraints intact;
  refusing unsafe request.
- If the target, failing gate, score, or edit authority is missing, ask Round 1
  question: Which canonical target should I patch? If canonical and .agents/**
  paths both exist, confirm the source before edits.

## Outputs

- Exact validation commands and pass, fail, or blocked outcomes.
- Changed files, rollback path, and evidence artifact locations.
- For blocked release-eval cases, the failed repair-policy item in
  blocker_notes.
- Lane-separated readiness summary covering SDK, OSS, Tessl, runtime, registry,
  and publication truth only when those lanes have current evidence.
- Schema-bound outputs include schema_version and preserve the validation
  command that produced the result.

## Workflow

1. Find the canonical source and confirm edits are allowed.
2. Read references/repair-policy.md for first-principles gate, repair map,
   Tessl policy, and scenario policy.
3. For review, handoff, rollback, or validation-only work, return the Outputs
   contract and stop.
4. Run the focused gate; record baseline score, artifact path, and first
   blocker.
5. Apply one Repair Map change from references/repair-policy.md, then rerun the
   same gate.
6. If score or blocker is flat, undo or narrow and try the next map item. After
   three flat loops, stop with blocker_notes.
7. On green, run final gates. If any fail, name the gate and next patch target;
   do not claim release readiness.

Command: ./bin/ask skills external-review <target> --audit-level compat --json --robot

Pass only on parsed fields: ask audit, package, and release status == success;
external-review lint ok plus score >= 90 with 95+ target; Tessl live-private
usage >= max(0.90, baseline) only when the workspace/project link is available.
On failure, patch the first errors[] item or blocker. Exit code alone never
passes.

## Failure Mode

If three repair loops leave the same score or blocker unchanged, stop and return
blocker_notes with the failed gate, artifact path, and next smallest patch.

## Validation

- Fail fast: stop at the first failed gate, do not proceed to later gates, and
  parse JSON fields instead of exit code alone.
- Rerun the exact failed gate after each repair before widening scope.
- Start SDK movement with ./bin/ask sdk start <skill-path> --json --robot.
- For package readiness, run ./bin/ask skills package verify <skill-path>
  --json --robot and preserve the receipt.
- Package reference quality must keep reference_heading_invocable true for
  Markdown references and vendored capsule bodies.
- Before OSS, Tessl, registry, or release claims, run scenario-quality,
  scorer-quality, and scorer-calibration through the SDK eval commands.
- Required release evidence: audit/package/release success, external-review
  lint ok, Tessl review score >= 90, and live-private usage >= max(0.90,
  baseline) when the workspace/project link is available.
- Live-private release evidence also requires scenario-source proof:
  scenario-sources.json must show skill-owned eval cases and reviewed generated
  fixture cases, unless the package contract explicitly declares a
  structure-only exception.
- Live-private release evidence for behavioral skills requires
  scenario-sources.json to show at least 20 gold-standard structured scenarios.
- Live-private release evidence requires Tessl run-budget proof or an explicit
  blocker that preserves the 300-run operator-provided workspace limit and
  20-run remediation reserve.
- Live-private release evidence requires ./bin/ask sdk eval handoff-readiness
  --skill <target> --preview --json --robot to pass for the current candidate.
- Live-private release evidence requires scenario drift review after the latest
  skill change; stale or obsolete scenarios block professional readiness even
  when the live run completes.
- References and scripts must be checked when they affect skill behavior; weak
  supporting material blocks release claims. Markdown reference and capsule-body
  H1 headings must be specific, filename-aligned, and invocable before OSS,
  Tessl, or registry movement.

## Gotchas

- Do not call a lower score better unless the reported improvement over
  baseline is positive.
- Do not treat a 100% unit row as release success when the tile score or
  baseline comparison is worse.
- Do not let package-specific repair details crowd the entrypoint; keep them in
  verified references.
- Editing only SKILL.md while leaving bad references, scripts, or eval fixtures
  untouched is not a package repair.
- Creating fresh temp directories by deleting old Tessl evidence destroys
  review evidence.
- Claiming pass from a completed command is invalid when parsed score,
  baseline, or readiness fields fail.
- Running live Tessl directly after editing a skill without first refreshing or
  confirming bespoke generated scenarios for that skill skips the SDK pipeline.

## Execution Boundaries

- Edit canonical skill sources, package-owned references, and eval fixtures only
  after confirming path ownership.
- Use repo wrappers first. Patch scripts only when the wrapper failure proves
  the script is the repair target.
- Tessl lanes stage controlled copies under /tmp; preserve temp evidence and
  never point Tessl at live repo source.
- For create/update/install/refactor/skillify work, do not run live Tessl
  scoring until bespoke generated scenarios have been prepared, reviewed,
  imported, and counted in staged scenario-sources.json.
- If Tessl live finds scenario, rubric, judge, or package-shape failures,
  classify that as an upstream SDK pipeline defect and patch the deterministic
  guardrail before rerunning from oss-local.
- Route basic skill-behavior, reference, and security failures to the owning
  skill/source repair path before rerunning.
- Do not treat ./bin/ask evals run --runner codex, preview-only Tessl local
  proof, or a Tessl dry-run command string as handoff evidence.
- Handoff proof requires SDK receipts for oss-local, oss-cloud,
  tessl-local-proof --execute, and a dry-run receipt with
  tessl_eval.dry_run=true.
- When a skill changes, do not reuse the old scenario set blindly; update, add,
  or remove scenarios so the eval suite still matches the skill contract.
- For behavioral skill readiness, do not run live Tessl until the canonical
  scenario set has at least 20 gold-standard structured scenarios. Runs below
  20 are transition diagnostics, not readiness proof.
- Do not run live Tessl when the workspace is near the 300-run limit or would
  consume the 20-run remediation reserve.

## References

- Repair policy: references/repair-policy.md.
- Policies: references/generated-artifact-policy.md,
  references/repo-local-audit-boundaries.md, and
  references/eval-enforcement-contract.md.
- Templates: references/discovery-interview.md, references/repair-examples.md,
  and references/package-specific-repairs.md.
- Factory gate: Infrastructure/references/first-principles-factory-gate.md.
- Helper scripts: scripts/ supports repo wrappers; invoke wrappers first unless
  repairing a script failure.
- References and scripts are package-verified support and must pass
  reference_quality:true.
- Tessl/KnowledgeOS source handle:
  Plugins/skill-factory/references/tessl-knowledgeos-capsule.md; load only when
  the target change depends on Tessl plugin layout, registry/install behavior,
  review/eval proof, MCP packaging, workspace/project setup, security policy,
  or Skills SDK handoff patterns.
