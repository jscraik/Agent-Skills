# Codex Hooks Runtime Contract

Read when: you need the exact currently documented Codex hooks surface before scaffolding, upgrading, or refusing unsupported behavior.

## Table of Contents
- [Why this matters](#why-this-matters)
- [Docs snapshot](#docs-snapshot)
- [Release and schema sweep](#release-and-schema-sweep)
- [Runtime surface](#runtime-surface)
- [Field support and caveats](#field-support-and-caveats)
- [Design implications](#design-implications)
- [Source anchors](#source-anchors)

## Why this matters
Codex hooks are contract-sensitive. This skill should scaffold only what is explicitly documented as supported and should label anything else as deferred.

## Docs snapshot
- Primary source checked: `https://developers.openai.com/codex/hooks`.
- Verification date for this skill: April 23, 2026.
- Latest stable release checked: `rust-v0.124.0` (published April 23, 2026).
- Latest alpha release checked: `rust-v0.124.0-alpha.3` (published April 23, 2026).

## Release and schema sweep
Hook-related changes confirmed from current release stream and schema/source checks:
- `PermissionRequest` is part of the current documented event surface and has generated command input/output schemas.
- `#17073` Support clear SessionStart source:
  - current schema enum is `startup`, `resume`, `clear`.
  - scaffold matchers should include all three values.
- `#15118` turn_id extension for `Stop` and `UserPromptSubmit`:
  - `turn_id` is required in current input schemas for `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, and `Stop`.
- `#14532` stop continuation and `stop_hook_active` mechanics:
  - `stop_hook_active` is required in current `Stop` input schema and should be honored to avoid re-block loops.
- `#15211` and `#15531` non-streaming shell-only `PreToolUse` and `PostToolUse` support:
  - current input schema remains shell-only with `tool_name: "Bash"`.
- `#17266` improved hook status rendering:
  - `statusMessage` remains worth setting on slower hooks for visibility.
- `#17268` removed Windows gate that disabled hooks:
  - do not assume hooks are disabled on Windows in current release stream.

## Runtime surface
`hooks.json` is discovered from active config-layer folders.

Documented event buckets:
- `SessionStart`
- `PreToolUse`
- `PermissionRequest`
- `PostToolUse`
- `UserPromptSubmit`
- `Stop`

Documented handler type:
- `type: "command"`

Matcher behavior:
- `SessionStart.matcher` matches `source`:
  - docs page currently lists `startup` and `resume`;
  - latest release notes and generated schema show `startup`, `resume`, and `clear`;
  - this skill should scaffold `^(startup|resume|clear)$` and treat docs-only values as stale until docs catch up.
- `PreToolUse.matcher` matches `tool_name` (current generated input schema uses `const: "Bash"`).
- `PermissionRequest.matcher` matches `tool_name` (current generated input schema uses `tool_name` and runtime currently emits `Bash`).
- `PostToolUse.matcher` matches `tool_name` (current generated input schema uses `const: "Bash"`).
- `UserPromptSubmit.matcher` is currently not used.
- `Stop.matcher` is currently not used.
- For matcher-enabled events, omitted matcher, `*`, and empty string all behave as match-all.

Timeout behavior:
- `timeout` is in seconds.
- `timeoutSec` is accepted as an alias.
- If `timeout` is omitted, Codex defaults to `600` seconds.

Path behavior:
- Commands run with the session `cwd`.
- For repo-local hooks, resolve command paths from git root or use absolute paths to avoid nested-directory drift.

## Field support and caveats
Common output fields for `SessionStart`, `UserPromptSubmit`, and `Stop`:
- `continue`
- `stopReason`
- `systemMessage`
- `suppressOutput`
  - note: parsed today but not fully implemented.

Event-specific behavior:
- `SessionStart`
  - plain text on stdout is added as context.
  - JSON supports `hookSpecificOutput.additionalContext`.
  - docs currently mention `startup` and `resume`, while current Codex release/schema also supports `clear`; generated matchers should include all three values.
- `PreToolUse`
  - currently supports Bash tool interception only.
  - current schema requires `turn_id` in input.
  - JSON supports `hookSpecificOutput.permissionDecision: "deny"` and `permissionDecisionReason`.
  - legacy block shape (`decision: "block"` + `reason`) and exit code `2` are accepted.
  - `permissionDecision: "allow"`/`"ask"` and several extra fields are parsed but currently fail open.
- `PermissionRequest`
  - runs only when Codex is about to request approval.
  - current schema requires `turn_id`, `tool_name`, and `tool_input` in input.
  - matcher applies to `tool_name`; runtime currently emits `Bash`.
  - JSON supports `hookSpecificOutput.decision.behavior` values `allow` and `deny`.
  - deny wins if multiple hooks decide; allow proceeds only when no matching deny exists.
  - plain text on stdout is ignored.
  - reserved decision fields (`updatedInput`, `updatedPermissions`, and `interrupt: true`) currently fail closed.
- `PostToolUse`
  - currently supports Bash tool results only.
  - current schema requires `turn_id` in input.
  - cannot undo side effects from the command that already ran.
  - JSON supports `systemMessage`, `decision: "block"` feedback shape, and `hookSpecificOutput.additionalContext`.
  - `continue: false` can stop normal processing of the original tool result.
  - `updatedMCPToolOutput` and `suppressOutput` are parsed but currently fail open.
- `UserPromptSubmit`
  - plain text on stdout is added as extra developer context.
  - current schema requires `turn_id` in input.
  - JSON supports `hookSpecificOutput.additionalContext`.
  - prompt blocking supports `decision: "block"` + `reason` (or exit code `2` + stderr).
- `Stop`
  - expects JSON on stdout when exiting `0`; plain text is invalid.
  - current schema requires both `turn_id` and `stop_hook_active` in input.
  - `decision: "block"` creates a continuation prompt rather than rejecting the turn.
  - if any matching `Stop` hook returns `continue: false`, that takes precedence.

Config parsing caveats:
- `type: "prompt"` and `type: "agent"` are parsed but skipped with runtime warnings.
- `"async": true` command hooks are parsed but skipped with runtime warnings.
- `statusMessage` is supported and should be used for longer-running hooks.

Cross-runtime forward compatibility:
- Some compatible runtimes include extra hook metadata fields (for example `agent_id` and `agent_type` on subagent-originated hooks).
- Hook scripts should ignore unknown fields and parse only the keys they need.

## Design implications
- Keep the default scaffold to the three-hook starter (`SessionStart`, `UserPromptSubmit`, `Stop`) because it provides strong baseline value with minimal latency.
- Add `PreToolUse`, `PermissionRequest`, or `PostToolUse` only when the user asks for command and approval guardrails that justify additional turn-time cost.
- Keep command paths absolute in generated packs to prevent cwd-dependent failures.
- Keep guardrails narrow and auditable; document that Bash interception is helpful but not a complete enforcement boundary.
- Keep `PreToolUse`, `PermissionRequest`, and `PostToolUse` scripts self-guarding because current matcher scope stops at `Bash`; command intent and file relevance must be classified inside the hook.
- Treat `PostToolUse` as advisory by default because it cannot undo completed side effects.
- Keep `SessionStart` enrichment fail-open on optional dependency failures.
- Use short `statusMessage` strings for hooks that can take more than a second because this improves operator observability.

## Source anchors
Official documentation:
- Hooks reference and runtime behavior:
  - `https://developers.openai.com/codex/hooks`

Release notes:
- Stable:
  - `https://github.com/openai/codex/releases/tag/rust-v0.124.0`
- Alpha:
  - `https://github.com/openai/codex/releases/tag/rust-v0.124.0-alpha.3`

Codex repo schema source:
- Generated hook schemas:
  - `https://github.com/openai/codex/tree/main/codex-rs/hooks/schema/generated`
  - includes `pre-tool-use`, `permission-request`, `post-tool-use`, `session-start`, `user-prompt-submit`, and `stop` command input/output schemas.
  - `session-start.command.input.schema.json` currently lists `source` enum values `startup`, `resume`, and `clear`.
- Runtime selection and matcher behavior:
  - `https://github.com/openai/codex/tree/main/codex-rs/hooks/src/events/common.rs`
  - `https://github.com/openai/codex/tree/main/codex-rs/hooks/src/engine/discovery.rs`
  - `https://github.com/openai/codex/tree/main/codex-rs/hooks/src/engine/config.rs`

Local codex source verification:
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/src/events/session_start.rs`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/src/events/permission_request.rs`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/session-start.command.input.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/pre-tool-use.command.input.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/permission-request.command.input.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/permission-request.command.output.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/post-tool-use.command.input.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/user-prompt-submit.command.input.schema.json`
- `/Users/jamiecraik/dev/codex/codex-rs/hooks/schema/generated/stop.command.input.schema.json`

Cross-runtime compatibility reference:
- `https://github.com/anthropics/codex-code/blob/main/src/entrypoints/sdk/coreSchemas.ts`

Local operational reference used as a builder-pattern source:
- `/Users/jamiecraik/dev/configs/codex/hooks/README.md`
- `/Users/jamiecraik/dev/configs/codex/hooks/hooks.json`
- `/Users/jamiecraik/dev/configs/codex/hooks/session-start.sh`
- `/Users/jamiecraik/dev/configs/codex/hooks/user-prompt-submit.sh`
- `/Users/jamiecraik/dev/configs/codex/hooks/stop-guard.sh`
