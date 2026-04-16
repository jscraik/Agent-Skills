# Activation and operational notes

## Skill activation
- Supported locations: `~/.codex/skills/<name>` or `.codex/skills/<name>` in a repo.
- `SKILL.md` must exist with valid, single-line `name` (<= 100 chars) and `description` (<= 500 chars).
- Restart Codex to reload skill metadata after changes.
- Avoid symlinked skill directories; Codex skips them.

## AGENTS behavior
- Place `AGENTS.md` at the repo root for guardrails to apply.
- `AGENTS.override.md` takes precedence over `AGENTS.md` at the same scope; the instruction chain is root-to-current.

## Execpolicy rules
- Store rules under `~/.codex/rules/*.rules`.
- Validate with `codex execpolicy check` before relying on them.
- Restart Codex after adding or changing rules.

## codex exec usage
- `codex exec` expects a Git repo; use `--skip-git-repo-check` only when appropriate.
- Use `--output-schema` and `-o` for deterministic JSON outputs.
