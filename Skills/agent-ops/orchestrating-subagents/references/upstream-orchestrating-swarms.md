# Upstream Orchestrating Swarms Migration Notes

Provenance for the upstream source used in this conversion:

- Source: `Plugins/compound-engineering/skills/orchestrating-swarms/SKILL.md`
- Ref: `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`
- URL: https://github.com/EveryInc/compound-engineering-plugin/tree/0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b/Plugins/compound-engineering/skills/orchestrating-swarms

## Table of Contents
- [Why this is a migration, not a direct copy](#why-this-is-a-migration-not-a-direct-copy)
- [High-value upstream doctrine preserved](#high-value-upstream-doctrine-preserved)
- [Concept mapping](#concept-mapping)
- [Patterns kept and translated](#patterns-kept-and-translated)
- [Sections intentionally not ported verbatim](#sections-intentionally-not-ported-verbatim)

## Why this is a migration, not a direct copy
The upstream skill is excellent operational doctrine, but it is tightly coupled to Codex primitives that do not exist in Codex:
- `Teammate`
- `Task`
- `TaskCreate`
- `TaskUpdate`
- shared team config JSON
- inbox files
- tmux and iTerm2 spawn backends

Copying those mechanics directly into Codex would create a misleading skill. The goal of this migration is to preserve the orchestration wisdom while rewriting the runtime model around Codex subagents.

## High-value upstream doctrine preserved
- Use a leader or parent coordinator with a small number of focused workers.
- Match worker type to task instead of using one generic worker for everything.
- Prefer clear prompts with explicit deliverables.
- Use parallel specialist review for large PRs and broad audits.
- Use sequential pipelines only when dependencies are real.
- Clean up workers when they are done.
- Be careful with large logs, background activity, and stale worker state.

## Concept mapping

| Upstream Codex concept | Codex-native translation |
|---|---|
| Team lead | Parent Codex thread |
| Teammate | Spawned subagent |
| Team / member list | Active agent thread set owned by the parent |
| Inbox messages | Parent-mediated results and follow-up instructions |
| `Task` one-off subagent | `spawn_agent` for a bounded worker |
| `Task` plus `team_name` persistent teammate | Long-lived spawned subagent that the parent may steer with `send_input` |
| `TaskCreate` / `TaskUpdate` queue | Parent-owned plan and explicit task briefs |
| `requestShutdown` / `cleanup` | `close_agent` after integration |
| tmux / iTerm2 worker visibility | Codex app and CLI thread visibility via `/agent` and activity surfaces |

## Patterns kept and translated

### Parallel specialist review
Keep:
- one specialist per concern
- synthesize centrally

Translate to Codex:
- use `explorer`, `correctness-reviewer`, `framework-docs-researcher`, and narrower installed specialists
- wait on subagents from the parent thread
- integrate findings before returning

### Research -> plan -> implement -> verify pipeline
Keep:
- dependency-aware sequencing

Translate to Codex:
- do not emulate a shared task queue
- run sequential phases through parent orchestration or limited worker reuse
- keep only truly independent phases in parallel

### Self-organizing queue idea
Keep:
- desire for autonomous parallel coverage over many similar units

Translate to Codex:
- prefer explicit worker briefs and shallow delegation in normal sessions
- if the runtime exposes batch fan-out helpers, treat them as optional extensions rather than the baseline pattern

## Sections intentionally not ported verbatim
- File layouts under `~/.codex/teams/` and `~/.codex/tasks/`
- JSON message formats for inbox communication
- Backend detection and troubleshooting for `tmux` or `iterm2`
- Codex-specific `subagent_type` naming and `run_in_background` examples
- Codex plugin role prefixes such as `compound-engineering:review:*`

Those sections were dropped as mechanics, not as doctrine. Their useful operational lessons were preserved in the Codex-native skill and in the local overlap and docs references.
