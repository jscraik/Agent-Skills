# Session Evidence Skillify Triage

Read when: `~/.agents/session-collector` or archived session evidence reports `coverage-gap`, `workflow-capture`, `skillify`, or many apparent HE workflow candidates.

## Goal

Turn repeated session evidence into the smallest durable improvement. A collector `coverage-gap` label is only an intake signal; it is not approval to create a new skill.

## Evidence Inputs

Use bounded collector artifacts before raw transcripts:

- `skill-refactor-evidence.json`
- `skillify-candidates.json`
- `harness-engineering-evidence.json`
- `solved-problems.json`
- `index.json`
- `redaction-report.json`

Record the bundle path, session count, candidate count, and at least one exact sanitized evidence label before deciding.

## Candidate Gates

A candidate may advance only when all gates pass:

- Recurs in at least three sessions, artifacts, or evidence labels, unless one validated high-impact run has explicit user approval.
- Shares the same blocker taxonomy, validation gate, command family, or workflow failure mode.
- Targets the same repo, plugin family, lifecycle stage, or operator audience.
- Has a realistic trigger phrase that maps to user language.
- Has a clear success output and failure boundary.
- Is not already covered by an existing HE stage, folded HE alias, reference doc, validation script, or another plugin skill.
- Has no raw secrets, credentials, private transcript text, or sensitive payloads after checking `redaction-report.json`.

Reject collector noise explicitly. Noncanonical `he-*` text, path fragments, bundle names, and archived file names are evidence labels, not stage names.

## Decision Matrix

Use the first matching decision:

| Decision | Use when | Next action |
| --- | --- | --- |
| `update-existing-stage` | Existing HE skill covers the workflow but lacks trigger, evidence, validation, or failure guidance. | Patch that stage or its task-profile/reference material. |
| `add-reference-material` | The pattern is useful context but too narrow or too detailed for `SKILL.md`. | Add or update a reference and link it from the owning stage. |
| `add-validation-script` | Repeated failures are deterministic and can be checked mechanically. | Add the smallest validator and route it through the owning workflow. |
| `skillify-new-skill` | The workflow is distinct, repeated, audience-specific, and not covered by existing stages. | Route to `skill-factory:skillify` with the triage output as required input. |
| `no-action-noise` | The signal is a path token, broad blocker label, one-off exploration, or already-fixed issue. | Record the reason and do not create a package. |

## Output Contract

When triage influences a decision, return:

- `schema_version: 1`
- `decision`
- `target_stage_or_skill`
- `evidence_source`
- `evidence_labels`
- `blocker_taxonomy`
- `validation_gate`
- `redaction_checked`
- `next_action`
- `rejected_reason` when `no-action-noise`

## Skillify Handoff

Only invoke `skill-factory:skillify` after `skillify-new-skill` passes. The handoff must include destination path, target audience, trigger text, source evidence, validation expectations, and failure boundaries.

Do not pass raw transcripts. Pass sanitized collector labels, summarized commands, exact artifact paths, and validation outcomes.
