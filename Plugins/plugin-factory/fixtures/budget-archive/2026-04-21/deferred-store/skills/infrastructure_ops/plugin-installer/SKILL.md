---
name: plugin-installer
description: Install validated Codex plugins from trusted sources with quarantine validation, provenance, and rollback. Use when distribution and installation are the primary goals.
metadata:
  short-description: Install validated plugins with provenance and rollback safety
  skill-type: infrastructure_ops
---

# Plugin Installer

## Philosophy

- Install only with provenance and rollback evidence.

## When to Use

Use for downstream plugin installation and visibility recovery after build hardening.

Route elsewhere:
- plugin creation -> `[[plugin-creator]]`
- conversion/hardening -> `[[plugin-builder]]`

## Inputs

- source repo/url and plugin path
- destination root
- pinned ref and trust policy
- validation level (`strict|compat`)

## Outputs

Return: `schema_version`, `installed_plugin`, `install_path`, `validation`, `artifacts`, optional `blocked_by`.

## Execution Boundaries

Classify install work as an external or repo write before acting. Use the OpenAI-style plugin design contract to separate preview/quarantine validation from install, projection refresh, rollback, and marketplace or user-level mutation.

Plugin Installer owns provenance checks, quarantine validation, install evidence, visibility checks, and rollback notes. It does not own plugin scaffolding, plugin hardening, marketplace policy invention, or source-of-truth rewrites outside the requested install destination.

## Workflow

Use the staged install protocol in `references/workflow.md`.

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.

Read when:
- You need full install, provenance, and rollback flow details: [references/workflow.md](./references/workflow.md).
- You need confirmation boundaries for write, destructive, open-world, or completion-gating actions: [OpenAI-style plugin design contract](../../../../../Infrastructure/references/openai-style-plugin-design-contract.md).

## Validation

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
```

Fail fast: stop at first failed gate and report blocker text.

## Anti-Patterns

- installing from unpinned moving refs without explicit override
- promoting from quarantine before validation
- omitting provenance or rollback artifacts

## Constraints

- redact secrets and auth tokens in install logs
- do not skip trust policy checks by default
- allow network access only for explicit allowlisted source hosts: `https://github.com`, `https://api.github.com`, `https://raw.githubusercontent.com`

## Failure Mode

- Stop when the source is unpinned, provenance is unclear, trust policy is missing, destination ownership is ambiguous, validation fails, or rollback cannot be described.
- Report the exact blocker and the smallest safe repair instead of partially installing, refreshing projections, or claiming visibility.

## Gotchas

- Quarantine validation is read/prep work; install, projection refresh, rollback, and user-level marketplace changes are stronger side-effect classes.
- A GitHub URL without a pinned ref is not provenance.
- Visibility recovery should not rewrite canonical plugin source unless the source path is explicitly part of the request.

## Examples

- "Install this validated plugin from a pinned GitHub ref and prove it is visible."
- "Quarantine this plugin package first, then tell me whether it is safe to install."
- "Recover plugin visibility without changing the canonical plugin source."

## References

- `references/workflow.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `../../../../../Infrastructure/references/openai-style-plugin-design-contract.md`
- `assets/`
