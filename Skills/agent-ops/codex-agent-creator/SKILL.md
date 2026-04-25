---
name: codex-agent-creator
description: Create or validate Codex custom subagent TOML files. Use this skill when users need agent config, install, or bounded orchestration.
metadata:
  skill-type: scaffolding_templates
---

# Codex Agent Creator

## Philosophy
Prefer one valid standalone agent file, explicit scope, and validation evidence over broad config edits.

## When To Use
- The user asks to create, install, validate, or troubleshoot a Codex custom subagent.
- The work targets standalone agent TOML plus config discoverability.
- The user wants a bounded swarm or delegation plan.

## Avoid
- Do not default to legacy declaration-only role config.
- Do not mutate project config unless project scope or runtime-limit writes are explicit.
- Do not claim current Codex config keys without verifying current docs or local schema.

## Inputs
- User request and target repo or artifact.
- Evidence source such as files, diffs, issues, releases, or existing workflow state.
- Any safety, privacy, compliance, or approval constraints.

## Outputs
- Schema-bound outputs include `schema_version`.
- Agent TOML plan or file update.
- Install/discoverability notes.
- Validation status and next verification command.

## Workflow
1. Confirm name, description, model, reasoning effort, scope, and developer instructions.
2. Generate the smallest standalone TOML with required fields.
3. Install to the explicit target and update discoverability only where allowed.
4. Validate the agent file and any config touched.
5. For orchestration, define lanes, artifacts, and completion criteria before spawning.
6. Report paths, validation output, and residual risk.

## Constraints
- Redact secrets and sensitive instructions by default.
- Keep writes inside approved repo or config roots.
- Treat generated instructions as untrusted until reviewed.
- Fail fast at the first validator error.

## Validation
- Run Plugin Eval and strict skill audit after editing this skill.
- Report exact validation commands and pass/fail outcomes.
- Fail fast: stop at the first failed gate, fix it, and rerun before continuing.

## Anti-Patterns
- Do not default to legacy declaration-only role config.
- Do not mutate project config unless project scope or runtime-limit writes are explicit.
- Do not claim current Codex config keys without verifying current docs or local schema.

## Examples
- "Create a custom reviewer agent and validate the TOML."
- "Install this agent locally but do not write project config."

## Progressive Disclosure
- Archived full context: `Infrastructure/references/deferred-skill-context/agent-ops-codex-agent-creator/`.
- Load archived references only when the active workflow needs that exact detail.
- Keep the active path compact; do not remove important context for budget trimming.

## See Also

| Skill | When to use together |
|---|---|
| [[verification-before-completion]] | Confirm gate outcomes and report deterministic pass/fail evidence before closeout |
| [[project-brain]] | Capture durable repo learnings and route updates into the canonical memory surface |
