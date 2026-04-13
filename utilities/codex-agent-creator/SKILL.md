---
name: codex-agent-builder
description: Create, install, and validate Codex custom subagents as standalone agent TOMLs. With `--scope global`, installs to `~/dev/configs/codex/agents/{name}/{name}.toml` and updates `~/dev/configs/codex/config.toml`. With `--scope project`, installs to `${project_root}/.codex/agents/{name}/{name}.toml` and updates or creates `${project_root}/.codex/config.toml`. Use when the user wants custom agent definitions created or upgraded, not orchestration of running agent threads.
metadata:
  skill-type: scaffolding_templates
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-04-12
  metadata_source: frontmatter
---

# Codex Agent Creator

## When to use
- User asks to create, update, or troubleshoot a custom subagent file in canonical Codex control-plane paths (`~/dev/configs/codex/agents/{name}/{name}.toml`).
- User needs global custom-agent installation with explicit developer instructions.
- User needs constrained global agent runtime settings validation (`agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds`).
- User asks for upgrades from older role-declaration flows to modern standalone custom-agent files.

## Scope and triggers
- Focus on standalone custom-agent authoring, installation, and validation for Codex.
- Default to canonical global write targets in this workspace (`~/dev/configs/codex/agents/`, `~/dev/configs/codex/config.toml`).
- Do not use this skill for orchestrating active subagent threads or deciding whether the capability should be a skill, prompt, or automation.

## Required inputs
- Agent name and short description.
- Model and reasoning profile.
- Desired developer instructions.
- Scope (default `global`; `project` only when explicitly requested):
  - `--scope global`: installs to `~/dev/configs/codex/agents/<name>/<name>.toml` and updates `~/dev/configs/codex/config.toml`
  - `--scope project`: installs to `${project_root}/.codex/agents/<name>/<name>.toml` and updates or creates `${project_root}/.codex/config.toml`
- Confirmed target custom-agent file path.
- Optional `nickname_candidates` override for display-friendly spawned-agent labels.
- Optional runtime limits and approval mode.

## Deliverables
- Confirmed custom-agent configuration plan.
- Generated or updated standalone custom-agent TOML path.
- Validation result with explicit success/failure reasons.
- Optional summary of global runtime limits configured in `~/dev/configs/codex/config.toml` (or explicitly provided override).
- Include `schema_version` whenever output is machine-validated.

## Procedure
### 1) Input confirmation
- Confirm required values explicitly: model, reasoning effort, developer instructions, scope.
- Validate that requested limits and path edits are intentional.

### 2) Minimal custom-agent generation
- Generate a standalone custom-agent TOML with required fields: `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`.
- Treat `model` and `model_reasoning_effort` as mandatory for this repository contract.
- Add `nickname_candidates` only when requested or when display labels are explicitly desired.
- Keep optional behavior strict and explicit.
- Treat legacy `[agents.{name}]` declaration flows as compatibility-only, not the default authoring path.

### 3) Validation-first execution
- Run custom-agent script checks before declaring completion.
- Never skip required-key checks when `name`/`description`/`developer_instructions`/`model`/`model_reasoning_effort` are updated.

### 4) Install and handoff
- Install only after validation by writing into the correct agents directory.
- In this workspace, install to canonical global paths by default: `~/dev/configs/codex/agents/` and `~/dev/configs/codex/config.toml`.
- For global installs, ensure runtime discoverability by updating `[agents.{name}].config_file` to the installed canonical agent file path.
- Scope path contract:
- `--scope global`: write `~/dev/configs/codex/agents/{name}/{name}.toml` and update `~/dev/configs/codex/config.toml`.
- `--scope project`: write `${project_root}/.codex/agents/{name}/{name}.toml` and update or create `${project_root}/.codex/config.toml`.
- Treat non-canonical global paths as compatibility overrides that require explicit opt-in.
- If the user requests runtime limits, update only `[agents]` global keys in the selected global `config.toml`.
- Return next-step verification command and residual risk.

### 5) Upstream alignment checkpoint
- Verify current Codex guidance from OpenAI docs before recommending config keys (`agents.max_threads`, `agents.max_depth`, `agents.job_max_runtime_seconds`, `model_reasoning_effort`).
- Verify current `openai/codex` release track before stating "latest" release details.
- Use the local fork (`~/dev/codex`) to confirm role-loader behavior (discovery from each config-layer `agents/` directory and standalone role validation requirements).
- Record the checked sources in the delivery summary and route deep details to `references/upstream-alignment-2026-04-12.md`.

## Scope focus guardrails
- Start with the **smallest viable package boundary**: one custom agent file and one validation pass.
- Keep first pass focused on **2-3 modules** only: write, validate, install.
- Limit scope before extending behavior; only add advanced flags after the base flow passes.
- Use context-specific expansion rather than broad config sprawl.

## Discovery interview
Run discovery for underspecified custom-agent creation or hardening requests.
- Ask one round at a time and wait before moving forward.
- Start each round with one plain-language question and explain why the round matters in a short `Why this matters:` line.
- Avoid dumping the whole interview plan at once; keep the first turn to the current round only.
- Skip already-answered rounds.
- Stop when the custom agent can be built safely with explicit model, reasoning, scope, and instruction constraints.
- Before implementation, summarize confirmed facts, assumptions, and the approval checkpoint.
- Use `references/discovery-interview.md` for reusable round templates.

## Validation
- Validate all inputs before file changes.
- Run custom-agent validation after any file write.
- Fail fast when required inputs are missing.
- Return blocked state when any validation error appears.

## Anti-patterns
- DO NOT default to legacy `[agents.{name}]` declaration-first authoring when standalone files are supported.
- NEVER ship a config change without write + validate evidence.
- Avoid the common pitfall of broad, speculative config changes before the baseline flow passes.
- Treating legacy `[agents.{name}]` role declarations as the primary contract when standalone custom-agent files are available.
- Omitting required standalone fields (`name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`).
- Assuming required inputs from defaults.
- Reporting success without evidence from validation commands.
- Reusing generic or repetitive template output without adapting to the user’s context and constraints.
- Warning: incorrect scope defaults can silently shift agent behavior across projects.

## Constraints
- Redact secrets and credentials by default.
- Keep custom-agent TOML files minimal unless explicitly expanded by user request.
- Confirm destructive or far-reaching scope changes before applying.

## Philosophy
- Principle: preserve minimal, reversible configuration paths before adding optional complexity.
- Framework: establish safe defaults first, then layer context-specific behavior by explicit user intent.
- Tradeoff: optimize for reliable validation evidence over speed when those goals conflict.
- Why: this keeps migrations from legacy declarations predictable and auditable.
- Guiding questions:
- What is the smallest boundary that solves the user request without overbuilding?
- Which extension unlocks real value now, and which one should wait for a second pass?
- How do we keep the custom agent capable while still easy to review, debug, and rollback?

## Empowerment
- Enable users to ship capable custom agents quickly with confidence.
- Empower teams to explore higher-leverage workflows once the baseline contract is stable.
- Keep the workflow creative but grounded: small safe wins first, then innovative extensions.

## Examples
- "Create a global `researcher` custom agent with model gpt-5.4-mini and medium reasoning effort."
- "Can you create a project-scoped custom agent file for UI fixes and set max threads to 4?"
- "Please install a reviewer custom agent with nickname candidates Scout and Archivist, then verify it."
- "Can you inspect my existing reviewer agent, validate it, and migrate only what is outdated?"
- "Help me migrate from legacy role declarations to standalone custom-agent files without breaking limits."

## Failure mode
- If required input is missing or ambiguous, ask one precise question and stop.
- If installation conflicts with existing config, report the exact conflict and request consent before overwrite.

## References
- Policy references: `references/role-config-reference.md`, `references/contract.yaml`, `references/evals.yaml`, `references/task-profile.json`, `references/discovery-interview.md`.
- Upstream alignment snapshot: `references/upstream-alignment-2026-04-12.md`.
- Scripts: `scripts/write_role_config.sh`, `scripts/install_role.sh`, `scripts/validate_role.sh`.
- Compatibility and governance notes in `references/task-profile.json`.

## Variation
- Vary by context-specific custom-agent complexity: keep simple requests minimal, and adapt advanced requests with one constrained extension pass.
- Avoid repetition and cookie-cutter outputs; customize instructions, naming, and limits for each user goal.
- For diverse requests, propose different safe paths and explain why one is best for this environment.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## See Also
| Skill | When to use |
|---|---|
| [[agents-md]] | Update repo instructions to reference or govern the new agent roles |
| [[codex-automation-architect]] | Design recurring automations that orchestrate the installed agents |
| [[decide-build-primitive]] | Decide whether the capability should be an agent, skill, or automation first |

**Topic map:** [[agent-ops]]
