# Agentic CLI Design (Codex/Cortex Style)

Use this when designing CLIs for AI/agentic tooling or safety-gated workflows.

## Core goals (non-negotiable)
- Human-first
- Script-friendly
- Safe by default
- Model-agnostic

## Command surface (keep it shallow)
Prefer a small verb set:
- `run` (plan)
- `review` (validate)
- `apply` (execute)
- `inspect` (read-only state)
- `doctor` (env checks)

## Phase semantics
- `run`: never writes, no network, no exec
- `review`: validation only, no writes
- `apply`: requires explicit risk flags; should fail without them

## Risk flags (named consent)
- `--write`
- `--exec`
- `--network`
- `--unsafe`

## Output contracts
- `--json` => no logs, no color, no prose
- Stable schema versioning (e.g., `schema: tool.plan.v1`)
- stdout for data; stderr for diagnostics

## Exit codes (stable)
- `0` success
- `1` misuse
- `2` validation failed
- `3` policy refusal
- `4` partial success
- `130` user abort

## Determinism controls
- `--seed <int>`
- `--temperature <float>`
- `--max-steps <int>`

## Help expectations
- One-screen summary
- Common workflows
- Defaults (write/network/exec: off)

## Anti-patterns
- Hidden side effects
- Model-specific flags
- Auto-write on `run`
- Too many subcommands

## Codex CLI references (if aligning with Codex agentic UX)
- Codex CLI docs:
  https://developers.openai.com/codex/cli/
- Codex models:
  https://developers.openai.com/codex/models/
- Codex repo:
  https://github.com/openai/codex
