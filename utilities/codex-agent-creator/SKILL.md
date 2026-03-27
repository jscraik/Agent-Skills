---
name: codex-agent-builder
description: Create and install Codex multi-agent roles and configs with safe minimal-change updates. Use when the user wants agent roles created or updated, not orchestration of existing roles.
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
- Optional `nickname_candidates` override for display-friendly spawned-agent labels.
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
- Keep role declarations limited to `description`, `config_file`, and `nickname_candidates`.
- Add a single clear nickname by default; let the user override it only when they want a specific display label set.
- Keep optional behavior strict and explicit.

### 3) Validation-first execution
- Run role script checks before declaring completion.
- Never skip schema checks when `description`/`config_file` values are updated.

### 4) Install and handoff
- Install global or project scope only after validation.
- Return next-step verification command and residual risk.

## Discovery interview
Run discovery for underspecified role-creation or role-hardening requests.
- Ask one round at a time and wait before moving forward.
- Start each round with one plain-language question and explain why the round matters in a short `Why this matters:` line.
- Avoid dumping the whole interview plan at once; keep the first turn to the current round only.
- Skip already-answered rounds.
- Stop when the role can be built safely with explicit model, reasoning, scope, and instruction constraints.
- Before implementation, summarize confirmed facts, assumptions, and the approval checkpoint.
- Use `references/discovery-interview.md` for reusable round templates.

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
- "Create a global researcher role with model gpt-5.4-mini and medium reasoning effort."
- "Can you set project role limits for safer fan-out, then validate the config?"
- "Please install a worker role with nickname candidates Scout and Archivist, then verify it."

## Failure mode
- If required input is missing or ambiguous, ask one precise question and stop.
- If installation conflicts with existing config, report the exact conflict and request consent before overwrite.

## References
- Policy references: `references/role-config-reference.md`, `references/contract.yaml`, `references/evals.yaml`, `references/task-profile.json`, `references/discovery-interview.md`.
- Scripts: `scripts/write_role_config.sh`, `scripts/install_role.sh`, `scripts/validate_role.sh`.
- Compatibility and governance notes in `references/task-profile.json`.

## Variation
- Vary by role complexity: for simple roles, do minimal config only; for advanced roles, propose one explicit constrained extension pass after validation.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## See Also
| Skill | When to use |
|---|---|
| [[agents-md]] | Update repo instructions to reference or govern the new agent roles |
| [[codex-automation-architect]] | Design recurring automations that orchestrate the installed agents |
| [[codex-plugin-builder]] | Package agent roles together with hooks or skills in a plugin |
| [[decide-build-primitive]] | Decide whether the capability should be an agent, skill, or automation first |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path utilities/codex-agent-creator/SKILL.md --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->
