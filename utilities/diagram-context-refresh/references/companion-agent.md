# Companion agent mapping

This skill can pair with the local `diagram-cli` custom agent when it exists.

## Table of Contents

- [Local agent files](#local-agent-files)
- [Link contract](#link-contract)

## Local agent files

- `~/.codex/agents/diagram-cli/diagram-cli.toml`
- `~/.codex/agents/diagram-cli/diagram-cli.instructions.md`

## Link contract

- The skill owns trigger routing (`name` + `description`) and workflow steps.
- The companion `diagram-cli` agent contributes runtime guardrails:
  - prefer deterministic local CLI execution,
  - keep `.diagram/context/diagram-context.md` synchronized,
  - avoid unrelated file edits and dependency churn.
- If these files are absent, continue with this skill only.
