# Required Agents

## Table of Contents
- [Purpose](#purpose)
- [Core Roles](#core-roles)
- [Checked-In Seeds](#checked-in-seeds)
- [Route Mapping](#route-mapping)
- [Validation Note](#validation-note)

## Purpose
This plugin packages the `compound-engineering-router` skill, which recommends existing Codex agent roles as bounded internal support for packaged CE routes. The plugin does not own those agent configs, so this file records role dependencies that should be validated against the active Codex config.

## Core Roles
- `repo-research-analyst`
- `learnings-researcher`
- `spec-flow-analyzer`
- `ui-ux-design`
- `design-implementation-reviewer`
- `julik-frontend-races-reviewer`
- `kieran-typescript-reviewer`

## Optional Roles
- `issue-intelligence-analyst` (used when configured and issue-tracker intent is active)

## Checked-In Seeds
To prevent future drift between the router package and the canonical Codex config, this package now carries a checked-in seed set for the helper bundle:

- `references/external-agent-seeds/repo-research-analyst.toml`
- `references/external-agent-seeds/learnings-researcher.toml`
- `references/external-agent-seeds/issue-intelligence-analyst.toml`
- `references/external-agent-seeds/spec-flow-analyzer.toml`
- `references/external-agent-seeds/ui-ux-design.toml`
- `references/external-agent-seeds/design-implementation-reviewer.toml`
- `references/external-agent-seeds/julik-frontend-races-reviewer.toml`
- `references/external-agent-seeds/kieran-typescript-reviewer.toml`

These seed files are recovery and sync artifacts, not plugin runtime surfaces. The canonical installed runtime paths remain under `/Users/jamiecraik/dev/configs/codex/agents/<role>/<role>.toml`.

## Route Mapping
- `ideate`: `repo-research-analyst`, `learnings-researcher`, and optional `issue-intelligence-analyst` when issue-tracker intent is active
- `brainstorm`: `repo-research-analyst`, `learnings-researcher`
- `spec`: `repo-research-analyst`, `learnings-researcher`
- `deepen-spec`: `repo-research-analyst`, `learnings-researcher`
- `plan`: `repo-research-analyst`, `learnings-researcher`, `spec-flow-analyzer`
- `deepen-plan`: `repo-research-analyst`, `learnings-researcher`
- UI-first requests: route to `spec` or `plan`; when UI-specific bounded support is warranted, use `ui-ux-design`, optional `design-implementation-reviewer`, `julik-frontend-races-reviewer`, and `kieran-typescript-reviewer`
- `review` and `technical-review`: additional specialist reviewers remain request-dependent and are validated at runtime against the configured agent catalog
- `compound`: usually `repo-research-analyst`, `learnings-researcher`, with optional specialized reviewers validated at runtime
- `compound-refresh`: usually none by default; bounded investigation support is optional when the refresh scope is broad

## Validation Note
These role names were checked against the active Codex config during plugin sync on `2026-03-23` (canonical runtime root: `/Users/jamiecraik/dev/configs/codex/`).
