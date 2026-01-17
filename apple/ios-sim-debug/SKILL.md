---
name: ios-sim-debug
description: Use XcodeBuildMCP to build, run, launch, and debug the current iOS project on a booted simulator. Trigger when asked to run an iOS app, interact with the simulator UI, inspect on-screen state, capture logs/console output, or diagnose runtime behavior using XcodeBuildMCP tools.
metadata:
  short-description: Build/run iOS apps in simulator and inspect UI/logs
---
# iOS Debugger Agent

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview
Use XcodeBuildMCP to build and run the current project scheme on a booted iOS simulator, interact with the UI, and capture logs. Prefer the MCP tools for simulator control, logs, and view inspection.

## Philosophy
- Prefer deterministic, observable actions over guesswork.
- Minimize UI interaction; verify with logs and view hierarchy.
- Keep user consent explicit before launching or interacting.
- Explain the why behind each simulator action when results are ambiguous.

## Guiding questions
- What is the smallest action needed to answer the user’s question?
- Do we need build + run, or just launch/inspect?
- What evidence is required (logs, screenshot, UI tree)?
- Is the simulator already booted and correctly targeted?
- Why is this evidence sufficient to conclude the behavior?

## When to use
- When the user asks to run or debug an iOS app in a simulator.
- When the user needs UI inspection or interaction in the simulator.
- When the user requests logs or console output from a running app.

## Inputs
- Project path or workspace path for the iOS app.
- App scheme and target simulator ID.
- User approval to launch or interact with the app.

## Outputs
- Built/ran app in simulator with observed UI state.
- Logs, screenshots, or view hierarchy evidence as requested.
- A brief summary of findings and next steps.

## Core Workflow
Follow this sequence unless the user asks for a narrower action.

### 1) Discover the booted simulator
- Call `mcp__XcodeBuildMCP__list_sims` and select the simulator with state `Booted`.
- If none are booted, ask the user to boot one (do not boot automatically unless asked).

### 2) Set session defaults
- Call `mcp__XcodeBuildMCP__session-set-defaults` with:
  - `projectPath` or `workspacePath` (whichever the repo uses)
  - `scheme` for the current app
  - `simulatorId` from the booted device
  - Optional: `configuration: "Debug"`, `useLatestOS: true`

### 3) Build + run (when requested)
- Call `mcp__XcodeBuildMCP__build_run_sim`.
- If the app is already built and only launch is requested, use `mcp__XcodeBuildMCP__launch_app_sim`.
- If bundle id is unknown:
  1) `mcp__XcodeBuildMCP__get_sim_app_path`
  2) `mcp__XcodeBuildMCP__get_app_bundle_id`

## UI Interaction & Debugging
Use these when asked to inspect or interact with the running app.

- **Describe UI**: `mcp__XcodeBuildMCP__describe_ui` before tapping or swiping.
- **Tap**: `mcp__XcodeBuildMCP__tap` (prefer `id` or `label`; use coordinates only if needed).
- **Type**: `mcp__XcodeBuildMCP__type_text` after focusing a field.
- **Gestures**: `mcp__XcodeBuildMCP__gesture` for common scrolls and edge swipes.
- **Screenshot**: `mcp__XcodeBuildMCP__screenshot` for visual confirmation.

## Variation rules
- Vary depth based on task (quick inspect vs full debug session).
- Prefer different evidence types when results are ambiguous (UI tree + logs + screenshot).
- Use a different interaction path when the UI hierarchy changes between steps.

## Empowerment principles
- Empower the user to approve app launches and UI interactions.
- Empower reviewers with clear evidence references (screenshots, logs, UI nodes).
- Empower teammates with a short reproducible step list.

## Anti-patterns to avoid
- Tapping based on screenshots without `describe_ui`.
- Launching or installing without user request.
- Assuming bundle ids or schemes without verification.
- Treating a single UI snapshot as definitive without logs.

## Example prompts
- "Run the iOS app in the simulator and check the login screen."
- "Tap the Settings button and grab a screenshot."
- "Capture logs while reproducing the crash."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Logs & Console Output
- Start logs: `mcp__XcodeBuildMCP__start_sim_log_cap` with the app bundle id.
- Stop logs: `mcp__XcodeBuildMCP__stop_sim_log_cap` and summarize important lines.
- For console output, set `captureConsole: true` and relaunch if required.

## Troubleshooting
- If build fails, ask whether to retry with `preferXcodebuild: true`.
- If the wrong app launches, confirm the scheme and bundle id.
- If UI elements are not hittable, re-run `describe_ui` after layout changes.

## Stack-specific variants

### codex variant
Frontmatter:

```yaml
---
name: ios-sim-debug
description: Build, run, and debug iOS apps on simulator with UI interaction and log capture via XcodeBuildMCP. Not for non-interactive builds; use xcode-build.
metadata:
  short-description: Build/run iOS apps in simulator and inspect UI/logs
---
```
Body:

# iOS Debugger Agent

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview
Use XcodeBuildMCP to build and run the current project scheme on a booted iOS simulator, interact with the UI, and capture logs. Prefer the MCP tools for simulator control, logs, and view inspection.

## Philosophy
- Prefer deterministic, observable actions over guesswork.
- Minimize UI interaction; verify with logs and view hierarchy.
- Keep user consent explicit before launching or interacting.
- Explain the why behind each simulator action when results are ambiguous.

## Guiding questions
- What is the smallest action needed to answer the user’s question?
- Do we need build + run, or just launch/inspect?
- What evidence is required (logs, screenshot, UI tree)?
- Is the simulator already booted and correctly targeted?
- Why is this evidence sufficient to conclude the behavior?

## When to use
- When the user asks to run or debug an iOS app in a simulator.
- When the user needs UI inspection or interaction in the simulator.
- When the user requests logs or console output from a running app.

## Inputs
- Project path or workspace path for the iOS app.
- App scheme and target simulator ID.
- User approval to launch or interact with the app.

## Outputs
- Built/ran app in simulator with observed UI state.
- Logs, screenshots, or view hierarchy evidence as requested.
- A brief summary of findings and next steps.

## Core Workflow
Follow this sequence unless the user asks for a narrower action.

### 1) Discover the booted simulator
- Call `mcp__XcodeBuildMCP__list_sims` and select the simulator with state `Booted`.
- If none are booted, ask the user to boot one (do not boot automatically unless asked).

### 2) Set session defaults
- Call `mcp__XcodeBuildMCP__session-set-defaults` with:
  - `projectPath` or `workspacePath` (whichever the repo uses)
  - `scheme` for the current app
  - `simulatorId` from the booted device
  - Optional: `configuration: "Debug"`, `useLatestOS: true`

### 3) Build + run (when requested)
- Call `mcp__XcodeBuildMCP__build_run_sim`.
- If the app is already built and only launch is requested, use `mcp__XcodeBuildMCP__launch_app_sim`.
- If bundle id is unknown:
  1) `mcp__XcodeBuildMCP__get_sim_app_path`
  2) `mcp__XcodeBuildMCP__get_app_bundle_id`

## UI Interaction & Debugging
Use these when asked to inspect or interact with the running app.

- **Describe UI**: `mcp__XcodeBuildMCP__describe_ui` before tapping or swiping.
- **Tap**: `mcp__XcodeBuildMCP__tap` (prefer `id` or `label`; use coordinates only if needed).
- **Type**: `mcp__XcodeBuildMCP__type_text` after focusing a field.
- **Gestures**: `mcp__XcodeBuildMCP__gesture` for common scrolls and edge swipes.
- **Screenshot**: `mcp__XcodeBuildMCP__screenshot` for visual confirmation.

## Variation rules
- Vary depth based on task (quick inspect vs full debug session).
- Prefer different evidence types when results are ambiguous (UI tree + logs + screenshot).
- Use a different interaction path when the UI hierarchy changes between steps.

## Empowerment principles
- Empower the user to approve app launches and UI interactions.
- Empower reviewers with clear evidence references (screenshots, logs, UI nodes).
- Empower teammates with a short reproducible step list.

## Anti-patterns to avoid
- Tapping based on screenshots without `describe_ui`.
- Launching or installing without user request.
- Assuming bundle ids or schemes without verification.
- Treating a single UI snapshot as definitive without logs.

## Example prompts
- "Run the iOS app in the simulator and check the login screen."
- "Tap the Settings button and grab a screenshot."
- "Capture logs while reproducing the crash."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Logs & Console Output
- Start logs: `mcp__XcodeBuildMCP__start_sim_log_cap` with the app bundle id.
- Stop logs: `mcp__XcodeBuildMCP__stop_sim_log_cap` and summarize important lines.
- For console output, set `captureConsole: true` and relaunch if required.

## Troubleshooting
- If build fails, ask whether to retry with `preferXcodebuild: true`.
- If the wrong app launches, confirm the scheme and bundle id.
- If UI elements are not hittable, re-run `describe_ui` after layout changes.
