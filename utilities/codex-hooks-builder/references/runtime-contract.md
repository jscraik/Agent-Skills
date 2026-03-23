# Codex Hooks Runtime Contract

Read when: you need the exact March 2026 Codex hooks surface before scaffolding, upgrading, or refusing unsupported behavior.

## Table of Contents
- [Why this matters](#why-this-matters)
- [Release snapshot](#release-snapshot)
- [Stable runtime surface](#stable-runtime-surface)
- [Field support and caveats](#field-support-and-caveats)
- [Alpha nuance](#alpha-nuance)
- [Design implications](#design-implications)
- [Source anchors](#source-anchors)

## Why this matters
Codex hooks are version-sensitive. This skill should scaffold only what is demonstrably implemented in current released Codex and should label anything else as provisional.

## Release snapshot
- Stable release checked: `0.116.0`, published March 19, 2026.
- Latest alpha checked: `0.117.0-alpha.8`, published March 21, 2026.
- Verification date for this skill scaffold: March 22, 2026.

## Stable runtime surface
`hooks.json` is discovered from active config-layer folders.

Supported event buckets:
- `SessionStart`
- `UserPromptSubmit`
- `Stop`

Supported handler type:
- `type: "command"`

Parsed but skipped handler types:
- `type: "prompt"`
- `type: "agent"`
- `"async": true` on command hooks

Matcher behavior:
- `SessionStart.matcher` is honored.
- `UserPromptSubmit.matcher` is ignored during discovery.
- `Stop.matcher` is ignored during discovery.

## Field support and caveats
Dependable fields for command hook outputs:
- `continue`
- `stopReason`
- `systemMessage`
- `suppressOutput`
  Note: parsed by handlers, but current runtime path does not appear to apply it meaningfully.

Event-specific behavior:
- `SessionStart`
  - supports `hookSpecificOutput.additionalContext`
  - plain non-JSON stdout becomes context
  - invalid JSON-like stdout becomes a failure
- `UserPromptSubmit`
  - supports `decision: "block"` with `reason`
  - supports `hookSpecificOutput.additionalContext`
  - exit code `2` with stderr is also treated as block feedback
  - invalid JSON-like stdout becomes a failure
- `Stop`
  - supports `decision: "block"` with `reason`
  - exit code `2` with stderr is also treated as a block path
  - malformed stdout is treated as failure, not ignored

## Alpha nuance
The latest alpha keeps the same external `hooks.json` event and handler surface as stable.

Observed internal change in `0.117.0-alpha.8`:
- `Stop` converts block reasons into continuation fragments internally instead of a single continuation prompt string.

Implication:
- scaffold against the stable external JSON contract because the user-facing hook output shape is unchanged;
- avoid claiming new external fields unless a released schema or docs page exposes them.

## Design implications
- Use command hooks with explicit timeouts because that is the stable, released path.
- Keep `hooks.json` command paths absolute because discovery loads config by layer, but command execution happens against session cwd.
- Prefer JSON outputs for `UserPromptSubmit` and `Stop` because JSON gives auditable reasons and cleaner maintenance than stderr-only block paths.
- Keep `SessionStart.additionalContext` short and durable because it is model context, not a place for long procedural text.

## Source anchors
Official documentation:
- OpenAI docs: configuration precedence and project config layering
  - `https://developers.openai.com/codex/config-basic/#configuration-precedence`
  - `https://developers.openai.com/codex/config-advanced/#project-root-detection`
- OpenAI docs: customization and best-practice validation loop
  - `https://developers.openai.com/codex/concepts/customization/#next-step`
  - `https://developers.openai.com/codex/learn/best-practices/#improve-reliability-with-testing-and-review`

Codex repo source:
- `codex-rs/hooks/src/engine/config.rs`
- `codex-rs/hooks/src/engine/discovery.rs`
- `codex-rs/hooks/src/events/session_start.rs`
- `codex-rs/hooks/src/events/user_prompt_submit.rs`
- `codex-rs/hooks/src/events/stop.rs`
- `codex-rs/hooks/schema/generated/session-start.command.output.schema.json`
- `codex-rs/hooks/schema/generated/user-prompt-submit.command.output.schema.json`
- `codex-rs/hooks/schema/generated/stop.command.output.schema.json`

Local operational reference used as a builder pattern source:
- `/Users/jamiecraik/dev/config/codex/hooks/README.md`
- `/Users/jamiecraik/dev/config/codex/hooks/hooks.json`
- `/Users/jamiecraik/dev/config/codex/hooks/session-start.sh`
- `/Users/jamiecraik/dev/config/codex/hooks/user-prompt-submit.sh`
- `/Users/jamiecraik/dev/config/codex/hooks/stop-guard.sh`
