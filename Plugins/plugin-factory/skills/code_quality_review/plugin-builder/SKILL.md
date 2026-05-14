---
name: plugin-builder
description: Harden and validate Codex plugin packages with contract-grade checks before install or release. Use when the deliverable is a plugin package that needs conversion or hardening.
metadata:
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  metadata_source: frontmatter
---

# Plugin Builder

## Philosophy

- Enforce plugin contract integrity before distribution.

## When to Use

Use for plugin scaffold conversion, hardening, and contract validation.

Route elsewhere:
- first shell only -> `[[plugin-creator]]`
- install/discovery -> `[[plugin-installer]]`

## Inputs

- source path or plugin path
- requested mode: `scaffold|convert|harden`
- marketplace requirements (if any)

## Execution Boundaries

Plugin Builder owns plugin contract review, bundled hook validation, deterministic remediation guidance, validation evidence, and the final hardening handoff.

Delegate first-draft plugin shell creation to `[[plugin-creator]]` and runtime install or visibility checks to `[[plugin-installer]]`. Do not execute third-party install scripts, mutate marketplace policy fields, or package a plugin for release without explicit validation evidence.

Apply the OpenAI-style plugin design contract before release claims: public routing surface must stay small, child skills must be distinguishable, read-only/mutating/external/destructive actions must be separated, and plugin outputs must avoid unnecessary internal context.

Read when: choosing whether the requested factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).

For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

## Outputs

Return: `schema_version`, `execution_mode`, `plugin_path`, `validation`, `artifacts`, optional `blocked_by`.

## Workflow

Use the detailed procedure and command matrix in `references/workflow.md`.

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

Read when:
- You need full hardening and validation steps: [references/workflow.md](./references/workflow.md).
- You need side-effect, context-minimization, output-shape, or user-control checks: [OpenAI-style plugin design contract](../../../../../Infrastructure/references/openai-style-plugin-design-contract.md).

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns

- skipping `validate` before package handoff
- treating plugin hooks as documentation instead of executable runtime behavior
- changing marketplace policy fields without explicit request

## Examples

- "Harden this Codex plugin package and prove the contract before release."
- "Convert this local plugin source into Codex plugin layout, but stop before writes if source ownership is unclear."
- "Audit this plugin against marketplace policy and tell me whether it should fold into an existing plugin."

## Constraints

- redact secrets and sensitive metadata in reports
- do not skip validation gates for speed

## Failure Mode

- Stop when plugin ownership, release authority, side-effect class, marketplace policy, or validation evidence is unclear.
- Report the exact blocker and smallest safe next action instead of making release, install, marketplace, or external-update claims from incomplete evidence.

## Gotchas

- A valid plugin directory is not proof that the plugin is release-ready.
- Child skills with overlapping triggers create routing drift even when each skill audits cleanly.
- Marketplace, install, projection, and external-update behavior are stronger side-effect classes than local contract review and need explicit confirmation boundaries.

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/plugin-contract.md`
- `../../../../../Infrastructure/references/openai-style-plugin-design-contract.md`
- `assets/`
