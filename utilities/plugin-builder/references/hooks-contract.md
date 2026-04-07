# Codex Hooks Contract (Official-Backed)

Use this reference when `hooks/` are requested in a plugin scaffold or conversion.

## Scope
- Define what is currently implemented in Codex hooks runtime.
- Separate stable behavior from provisional behavior.
- Provide traceable source anchors for conversion decisions.

## Baseline Revision
- `openai/codex@8614f92fc433fff20b1bf745be8b23cfb01d3d98` (captured 2026-04-07)

## Official source anchors
- Hooks config model: `codex-rs/hooks/src/engine/config.rs @ 8614f92fc433fff20b1bf745be8b23cfb01d3d98`
  - Defines `hooks` with events `SessionStart` and `Stop`.
  - Defines handler types: `command`, `prompt`, `agent`.
  - Command supports `timeout`/`timeoutSec`, `async`, `statusMessage`.
- Hook discovery/runtime support: `codex-rs/hooks/src/engine/discovery.rs @ 8614f92fc433fff20b1bf745be8b23cfb01d3d98`
  - Hooks are loaded from `hooks.json` in config layers.
  - `command` handlers run.
  - `prompt`, `agent`, and `async=true` are parsed but skipped with warnings.
- SessionStart output schema: `codex-rs/hooks/schema/generated/session-start.command.output.schema.json @ 8614f92fc433fff20b1bf745be8b23cfb01d3d98`
  - Supports `continue`, `stopReason`, `systemMessage`, `suppressOutput`.
  - `hookSpecificOutput.additionalContext` is available for `SessionStart`.
- Stop output schema: `codex-rs/hooks/schema/generated/stop.command.output.schema.json @ 8614f92fc433fff20b1bf745be8b23cfb01d3d98`
  - Supports `continue`, `stopReason`, `systemMessage`, `suppressOutput`.
  - Supports `decision: "block"` with `reason`.
- Stop behavior: `codex-rs/hooks/src/events/stop.rs @ 8614f92fc433fff20b1bf745be8b23cfb01d3d98`
  - `decision: "block"` requires non-empty `reason`.
  - Exit code `2` with stderr is treated as block feedback path.

## Stable conversion rules
- Emit `hooks.json` with explicit event buckets:
  - `hooks.SessionStart[]`
  - `hooks.Stop[]`
- Prefer `type: "command"` handlers for working conversions.
- Keep `timeout` explicit for each command hook.
- Use `matcher` only where runtime supports event matching semantics.
- For `Stop` hooks, include deterministic block rationale paths.

## Provisional/unsupported notes (must be flagged)
- `type: "prompt"`: parsed, not executed.
- `type: "agent"`: parsed, not executed.
- `"async": true`: parsed, skipped.
- Any behavior not tied to the source anchors above must be marked as inferred.

## Output contract for plugin conversion reports
When `hooks/` are touched, include:
- `verified_hooks_behavior`: list with source anchors.
- `provisional_hooks_behavior`: list with reason and risk.
- `hook_conversion_assumptions`: concise assumptions requiring follow-up validation.
