---
name: codex-agent-builder
description: Create and install Codex custom multi-agent roles when role creation, validation, or safe update is requested, using secure minimal-change configuration.
metadata:
  skill-type: scaffolding_templates
---

# Codex Agent Creator

## When to use
- User asks to add, update, or troubleshoot a `[agents.<role>]` entry.
- User needs project/global role installation with explicit developer instructions.
- User needs constrained multi-agent settings validation (`agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds`).

## Required inputs
- Role name and short description.
- Model and reasoning profile.
- Desired developer instructions.
- Scope: `global` or `project`.
- Confirmed target role config path.
- Optional runtime limits and approval mode.

## Deliverables
- Confirmed role configuration plan.
- Generated or updated role config path.
- Validation result with explicit success/failure reasons.
- Optional summary of limits configured.
- Include `schema_version` whenever output is machine-validated.

## Procedure
### 1) Input confirmation
- Confirm required values explicitly: model, reasoning effort, developer instructions, scope.
- Validate that requested limits and path edits are intentional.

### 2) Minimal config generation
- Use minimal keys by default (`model`, `model_reasoning_effort`, `developer_instructions`).
- Keep optional behavior strict and explicit.

### 3) Validation-first execution
- Run role script checks before declaring completion.
- Never skip schema checks when `description`/`config_file` values are updated.

### 4) Install and handoff
- Install global or project scope only after validation.
- Return next-step verification command and residual risk.

## Validation
- Validate all inputs before file changes.
- Run role validation after any config write.
- Fail fast when required inputs are missing.
- Return blocked state when any validation error appears.

## Anti-patterns
- Adding unsupported keys outside schema.
- Assuming required inputs from defaults.
- Reporting success without evidence from validation commands.

## Constraints
- Redact secrets and credentials by default.
- Keep role configs minimal unless explicitly expanded by user request.
- Confirm destructive or far-reaching scope changes before applying.

## Philosophy
- Preserve minimal, reversible configuration paths.
- Prefer explicitness over hidden assumptions.
- Keep scope and security constraints visible in every plan.

## Examples
- "Create a global researcher role with model gpt-5-codex and medium reasoning effort."
- "Can you set project role limits for safer fan-out, then validate the config?"
- "Please install a worker role with a strict developer instruction block and verify it."

## Failure mode
- If required input is missing or ambiguous, ask one precise question and stop.
- If installation conflicts with existing config, report the exact conflict and request consent before overwrite.

## References
- Policy references: `references/role-config-reference.md`, `references/contract.yaml`, `references/evals.yaml`, `references/task-profile.json`.
- Scripts: `scripts/write_role_config.sh`, `scripts/install_role.sh`, `scripts/validate_role.sh`.
- Compatibility and governance notes in `references/task-profile.json`.

## Variation
- Vary by role complexity: for simple roles, do minimal config only; for advanced roles, propose one explicit constrained extension pass after validation.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
