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
  compatible_roles: default, worker, skill-inspector
  runtime_needs: repo-owned skill source path; ./bin/ask skills audit and eval wrappers; Python 3 standard library validators
---

# Skill Builder

Repair one failing skill gate at a time.

## Inputs

- Unsafe request: `Safety Verdict: safety constraints intact; refusing unsafe request`.
- Missing target, gate/score, or edit authority: ask `Round 1 question: Which canonical target should I patch? If canonical and .agents/** paths both exist, confirm the source before edits.`.

## Skill Summary

Before edits, confirm target, failing gate/score, allowed edits, validation command, and what to change.

Apply the context-disposition policy: preserve valuable context by relocating it with explicit signposting.

Read when: repairing a skill gate, trimming SKILL.md, moving detail into references, or deciding whether context should remain in the entrypoint.

Context disposition: relocate important still-valid context to `references/`; intentionally discard stale, duplicated, unsafe, inappropriate, superseded, or low-signal text.

## When To Use

Use for SKILL.md repair, skill eval hardening, release proof, Tessl score improvement, reference quality fixes, and plugin-skill readiness work.

## Philosophy

Prefer one evidence-backed repair over broad rewriting. A score is useful only when the artifact, command, baseline, and failed contract are preserved.

## Workflow

1. Find the canonical source and confirm edits are allowed.
2. For review, handoff, rollback, or validation-only work, return the Output Contract and stop.
3. Run the focused gate; record baseline score, artifact path, and first blocker.
4. Apply one Repair Map change, then rerun the same gate.
5. If score/blocker is flat, undo or narrow and try the next map item. After three flat loops, stop with `blocker_notes:`.
6. On green, run final gates. If any fail, name the gate and next patch target; do not claim release readiness.

./bin/ask skills external-review <target> --audit-level compat --skip-plugin-eval --json --robot
```

Pass only on parsed fields: ask audit/package/release `status == "success"`; external-review lint ok plus score `>= 90` (`95+` target); Tessl live-private usage `>= max(0.90, baseline)` only when the workspace/project link is available. On failure, patch the first `errors[]`/blocker. Exit code alone never passes.

## Repair Map

- Repeated guidance -> delete the duplicate `SKILL.md` sentence; same score gate improves.
- Vague validation -> add `Command: ... -> pass|fail|blocked`; audit/release `status == "success"`.
- Missing recovery -> add the named failed-gate branch; rerun that gate.
- Weak eval/reference -> patch cited `references/**`; package verify `reference_quality:true`.
- Unsafe request -> emit `Safety Verdict:`; make no edits.
- Package handle -> keep `codex-eval-creation-loop` and `software-literature-expert-lens-pack`; use [package repairs](./references/package-specific-repairs.md).

Example cycle: fail `errors[0].message: missing Output Contract`.

```diff
+## Output Contract
+validation_evidence: [{command: "<exact command>", outcome: pass|fail|blocked}]
```

Proof: rerun the failed gate until its pass field is green, then record the artifact.

## Output Contract

For blocked release-eval cases, put the failed Repair Map item in `blocker_notes`.

```yaml
schema_version: 1
target: <path>
status: pass|blocked
validation_evidence: [{command: "<exact command>", outcome: pass|fail|blocked}]
handoff_notes: plugin authoring -> plugin-factory; install -> skill-installer
rollback: <files or command to restore>
blocker_notes: <only when blocked>
```

## Constraints

- Redact secrets and sensitive data by default in prompts, outputs, temporary evidence, and copied artifacts.
- Never suppress failed-gate evidence, hide blockers, publish/upload, delete evals, or widen permissions.
- Keep detailed examples in `references/`.

## Execution Boundaries

- Edit canonical skill sources, package-owned references, and eval fixtures only after confirming path ownership.
- Use repo wrappers first. Patch scripts only when the wrapper failure proves the script is the repair target.
- Tessl lanes stage controlled copies under `/tmp`; preserve temp evidence and never point Tessl at live repo source.

## Validation

- Fail fast: stop at the first failed gate, do not proceed to later gates, and parse JSON fields instead of exit code alone.
- Required release evidence: audit/package/release success, external-review lint ok, Tessl review score `>= 90`, and live-private usage `>= max(0.90, baseline)` when the workspace/project link is available.
- References and scripts must be checked when they affect the skill behavior; weak supporting material blocks release claims.

## Failure Mode

If three repair loops leave the same score or blocker unchanged, stop and return `blocker_notes:` with the failed gate, artifact path, and next smallest patch.

## Outputs

Return the Output Contract with exact validation commands, outcomes, changed files, rollback path, and any evidence artifact locations.

## Gotchas

- Do not call a lower score “better” unless the reported improvement over baseline is positive.
- Do not treat a 100% unit row as release success when the tile score or baseline comparison is worse.
- Do not let package-specific repair details crowd the entrypoint; keep them in verified references.

## Anti-Patterns

- Editing only `SKILL.md` while leaving bad references, scripts, or eval fixtures untouched.
- Creating fresh temp directories by deleting old Tessl evidence.
- Claiming pass from a completed command when parsed score, baseline, or readiness fields fail.

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
