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

## Outputs

Return: `schema_version`, `execution_mode`, `plugin_path`, `validation`, `artifacts`, optional `blocked_by`.

## Workflow

Use the detailed procedure and command matrix in `references/workflow.md`.

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns

- skipping `validate` before package handoff
- changing marketplace policy fields without explicit request

## Constraints

- redact secrets and sensitive metadata in reports
- do not skip validation gates for speed

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/plugin-contract.md`
- `assets/`
