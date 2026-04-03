# Codex Hooks Runtime Contract

Read when: you need the exact currently documented Codex hooks surface before scaffolding, upgrading, or refusing unsupported behavior.

## Table of Contents
- [Why this matters](#why-this-matters)
- [Docs snapshot](#docs-snapshot)
- [Runtime surface](#runtime-surface)
- [Field support and caveats](#field-support-and-caveats)
- [Design implications](#design-implications)
- [Source anchors](#source-anchors)

## Why this matters
Codex hooks are contract-sensitive. This skill should scaffold only what is explicitly documented as supported and should label anything else as deferred.

## Docs snapshot
- Primary source checked: `https://developers.openai.com/codex/hooks`.
- Verification date for this skill: March 30, 2026.

## Runtime surface
`hooks.json` is discovered from active config-layer folders.

Documented event buckets:
- `SessionStart`
- `PreToolUse`
- `PostToolUse`
- `UserPromptSubmit`
- `Stop`

Documented handler type:
- `type: "command"`

Matcher behavior:
- `SessionStart.matcher` matches `source` (`startup` or `resume`).
- `PreToolUse.matcher` matches `tool_name` (currently always `Bash`).
- `PostToolUse.matcher` matches `tool_name` (currently always `Bash`).
- `UserPromptSubmit.matcher` is currently not used.
- `Stop.matcher` is currently not used.

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
- `PreToolUse`
  - currently supports Bash tool interception only.
  - JSON supports `hookSpecificOutput.permissionDecision: "deny"` and `permissionDecisionReason`.
  - legacy block shape (`decision: "block"` + `reason`) and exit code `2` are accepted.
  - `permissionDecision: "allow"`/`"ask"` and several extra fields are parsed but currently fail open.
- `PostToolUse`
  - currently supports Bash tool results only.
  - cannot undo side effects from the command that already ran.
  - JSON supports `systemMessage`, `decision: "block"` feedback shape, and `hookSpecificOutput.additionalContext`.
  - `continue: false` can stop normal processing of the original tool result.
  - `updatedMCPToolOutput` and `suppressOutput` are parsed but currently fail open.
- `UserPromptSubmit`
  - plain text on stdout is added as extra developer context.
  - JSON supports `hookSpecificOutput.additionalContext`.
  - prompt blocking supports `decision: "block"` + `reason` (or exit code `2` + stderr).
- `Stop`
  - expects JSON on stdout when exiting `0`; plain text is invalid.
  - `decision: "block"` creates a continuation prompt rather than rejecting the turn.
  - if any matching `Stop` hook returns `continue: false`, that takes precedence.

## Design implications
- Keep the default scaffold to the three-hook starter (`SessionStart`, `UserPromptSubmit`, `Stop`) because it provides strong baseline value with minimal latency.
- Add `PreToolUse` or `PostToolUse` only when the user asks for command guardrails that justify additional turn-time cost.
- Keep command paths absolute in generated packs to prevent cwd-dependent failures.
- Keep guardrails narrow and auditable; document that Bash interception is helpful but not a complete enforcement boundary.

## Source anchors
Official documentation:
- Hooks reference and runtime behavior:
  - `https://developers.openai.com/codex/hooks`

Codex repo schema source:
- Generated hook schemas:
  - `https://github.com/openai/codex/tree/main/codex-rs/hooks/schema/generated`
  - includes `pre-tool-use`, `post-tool-use`, `session-start`, `user-prompt-submit`, and `stop` command input/output schemas.

Local operational reference used as a builder-pattern source:
- `/Users/jamiecraik/dev/config/codex/hooks/README.md`
- `/Users/jamiecraik/dev/config/codex/hooks/hooks.json`
- `/Users/jamiecraik/dev/config/codex/hooks/session-start.sh`
- `/Users/jamiecraik/dev/config/codex/hooks/user-prompt-submit.sh`
- `/Users/jamiecraik/dev/config/codex/hooks/stop-guard.sh`
