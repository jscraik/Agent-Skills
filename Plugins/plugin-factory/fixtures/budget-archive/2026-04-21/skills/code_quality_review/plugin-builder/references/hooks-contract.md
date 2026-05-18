# Codex Hooks Contract (Official-Backed)

Use this reference when `hooks/` are requested in a plugin scaffold or conversion.

## Scope
- Define what is currently implemented in Codex hooks runtime.
- Separate stable behavior from provisional behavior.
- Provide traceable source anchors for conversion decisions.

## Baseline Revision
- Local verification against `/Users/jamiecraik/dev/codex` on 2026-05-09.

## Template scaffold workflow

Canonical scaffold files for this skill:
- `Infrastructure/templates/hooks.json.tmpl`
- rendered baseline: `Infrastructure/references/hooks.template.json`

Render / refresh:

```bash
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/render_plugin_builder_templates.py
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/check_plugin_builder_template_drift.py --update
```

Verify no drift:

```bash
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/Infrastructure/scripts/check_plugin_builder_template_drift.py
```

## Official source anchors
- Hooks config model: `codex-rs/config/src/hook_config.rs`
  - Defines `hooks` with events `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `SessionStart`, `UserPromptSubmit`, and `Stop`.
  - Each matcher group uses a `hooks` array; `handlers` is not a Codex hook field.
  - Defines handler types: `command`, `prompt`, `agent`.
  - Command supports `timeout` in seconds, `async`, and `statusMessage`. `timeoutSec` is not a Codex hook field.
- Plugin manifest hook loading: `codex-rs/core-plugins/src/manifest.rs` and `codex-rs/core-plugins/src/loader.rs`
  - Plugin manifests accept `hooks` as a path string, path string array, inline object, or object array.
  - If the manifest omits `hooks`, Codex discovers the plugin default `hooks/hooks.json`.
- Hook discovery/runtime support: `codex-rs/hooks/src/engine/discovery.rs`
  - Plugin hook commands receive `PLUGIN_ROOT`, `PLUGIN_DATA`, `CLAUDE_PLUGIN_ROOT`, and `CLAUDE_PLUGIN_DATA`.
  - `command` handlers run.
  - `prompt`, `agent`, and `async=true` are parsed but skipped with warnings.
- SessionStart output schema: `codex-rs/hooks/schema/generated/session-start.command.output.schema.json`
  - Supports `continue`, `stopReason`, `systemMessage`, `suppressOutput`.
  - `hookSpecificOutput.additionalContext` is available for `SessionStart`.
- Stop output schema: `codex-rs/hooks/schema/generated/stop.command.output.schema.json`
  - Supports `continue`, `stopReason`, `systemMessage`, `suppressOutput`.
  - Supports `decision: "block"` with `reason`.
- Stop behavior: `codex-rs/hooks/src/events/stop.rs`
  - `decision: "block"` requires non-empty `reason`.
  - Exit code `2` with stderr is treated as block feedback path.

## Stable conversion rules
- Emit plugin-bundled hooks at `hooks/hooks.json` unless a manifest path is explicitly required.
- Use explicit event buckets under the top-level `hooks` object.
- Prefer `type: "command"` handlers for working conversions.
- Keep `timeout` explicit in seconds for each command hook.
- Use `hooks`, not `handlers`, for matcher group command arrays.
- Use `matcher` only where runtime supports event matching semantics.
- For `Stop` hooks, include deterministic block rationale paths.

## Provisional/unsupported notes (recommended to flag)
- `type: "prompt"`: parsed, not executed.
- `type: "agent"`: parsed, not executed.
- `"async": true`: parsed, skipped.
- Any behavior not tied to the source anchors above should be marked as inferred.

## Output contract for plugin conversion reports
When `hooks/` are touched, it is recommended to include:
- `verified_hooks_behavior`: list with source anchors.
- `provisional_hooks_behavior`: list with reason and risk.
- `hook_conversion_assumptions`: concise assumptions requiring follow-up validation.

Caveat:
- Current `plugin-builder` and `plugin-installer` flows do not yet enforce handler-type/async execution semantics or require these report fields at validation time; treat this section as advisory reporting guidance.
- TODO: add explicit enforcement in plugin conversion/install validators and link the follow-up implementation issue when tracked.
