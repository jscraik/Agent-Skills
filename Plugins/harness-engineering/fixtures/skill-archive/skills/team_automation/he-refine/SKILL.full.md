---
name: he-refine
description: "[BETA] Run browser-first refinement loops by starting the dev server, opening the feature, and iterating improvements with the user."
metadata:
  skill-type: team_automation
---

# Harness Engineering Refine

**Note: The current year is 2026.** Use this when comparing recency-sensitive dependencies, framework docs, and dev-server behavior.

`he-plan` decides what to build. `he-refine` polishes what already exists through tight browser-feedback loops. `he-work` applies larger implementation tasks and shipping changes after refinement decisions are locked.

This stage is for iterative polish on an existing feature, not blank-slate implementation.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow)
- [Subagent policy](#subagent-policy)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [References](#references)

## Working agreement
- Treat this as a Harness Engineering refinement stage with fast feedback.
- Start from the right branch and never polish directly on `main`/`master`.
- Favor small, reversible edits; keep each cycle focused on one user-noted issue.
- Keep the dev server loop stable so user feedback maps directly to current code.
- If server startup fails, surface logs quickly and ask one focused unblock question.

## When to use
Use this stage when:
- the user wants to polish or tighten an in-progress feature,
- the fastest path is browser feedback plus hot-reload iteration,
- implementation exists but quality, clarity, or UX still needs refinement,
- the user wants collaborative fix-check-repeat loops before review or ship.

Route elsewhere when:
- the feature direction is still undecided (`he-ideate`, `he-brainstorm`),
- requirements/spec/plan artifacts are incomplete (`he-spec`, `he-plan`, `he-deepen-*`),
- the user needs broad implementation across many files (`he-work`),
- the request is an optimization experiment with metric loops (`he-improve`).

## Required inputs
- target branch/PR context (or explicit confirmation to use the current branch),
- project path and server startup constraints,
- user-reported improvement goals,
- acceptable polish scope (UI-only, behavior-only, or both),
- stop condition (for example "done after N fixes" or "done when visuals are approved").

If critical inputs are missing, ask one blocking clarification before modifying files.

## Deliverables
- verified execution branch,
- running dev server URL and resolved startup method,
- iterative refinement changelog tied to user feedback,
- applied code updates with quick validation evidence,
- explicit stage handoff recommendation (`continue`, `he-work`, `he-code-review`, or `stop`),
- `schema_version: 1` in any machine-readable summary.

## Workflow
1. **Branch guard**
Run branch checks first. If input references PR number or branch name, switch safely. If no input is given, stay on current branch but block if it is `main`/`master`.

2. **Launch config check**
Run `bash scripts/read-launch-json.sh` to inspect `.claude/launch.json`. If a valid config exists, use it as source of truth for command, cwd, env, and port.

3. **Framework fallback detection**
When launch config is absent or invalid:
- run `bash scripts/detect-project-type.sh`;
- map detected type to `references/dev-server-*.md`;
- resolve package manager via `bash scripts/resolve-package-manager.sh`;
- resolve port via `bash scripts/resolve-port.sh --type <type>`.

4. **Start and probe dev server**
Start the server in the background with logs captured to a temp file. Probe `http://localhost:<port>` for up to 30 seconds.
- If probe fails, show the last 20 log lines and ask one unblock question.
- If probe succeeds, share the URL and begin refinement loop.

5. **Browser-first refinement loop**
Use `references/ide-detection.md` to pick best-effort handoff behavior and keep the user in loop:
- user points to what feels off,
- implement one focused fix,
- re-check quickly (browser or agent-browser when inspection is requested),
- repeat until the user confirms refinement is complete.

6. **Close loop**
Summarize what was refined, what remains, and route to next stage:
- `he-work` for larger follow-on implementation,
- `he-code-review` for readiness gating,
- `stop` when user confirms done.

## Subagent policy
- Stage policy is defined in `../../../../../references/routing-map.json` under `he-refine`.
- Resolve available roles from `~/.codex/agents/manifest.json` before delegation.
- If auto-spawn is unavailable, continue inline and provide manual role guidance.
- If required roles are missing, route role creation/install to `[[codex-agent-creator]]`.

## Validation
- Verify branch is not `main`/`master` before edits.
- Verify launch config sentinel handling is correct (`__NO_LAUNCH_JSON__`, `__INVALID_LAUNCH_JSON__`, etc.).
- Verify project-type detection output is one of supported types or an explicit unknown/multiple signal.
- Verify resolved port is numeric and probe reached localhost successfully.
- Verify refinement edits map to explicit user feedback.
- Verify fallback guidance includes manual role list and `codex-agent-creator` path when roles are unavailable.

## Anti-patterns
- polishing on protected default branches,
- skipping server health probe before claiming readiness,
- running broad refactors under a refinement request,
- making multiple unrelated fixes in one iteration without user confirmation,
- blocking workflow solely because subagents cannot auto-spawn.

## References
- `references/launch-json-schema.md`
- `references/ide-detection.md`
- `references/dev-server-detection.md`
- `references/dev-server-rails.md`
- `references/dev-server-next.md`
- `references/dev-server-vite.md`
- `references/dev-server-nuxt.md`
- `references/dev-server-astro.md`
- `references/dev-server-remix.md`
- `references/dev-server-sveltekit.md`
- `references/dev-server-procfile.md`
- `references/source-parity.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/sub-agent-map.md`
- `scripts/read-launch-json.sh`
- `scripts/detect-project-type.sh`
- `scripts/resolve-package-manager.sh`
- `scripts/resolve-port.sh`

## See Also
| Skill | When to use |
|---|---|
| [[he-improve]] | Run measurable optimization experiments instead of browser-led polish |
| [[he-work]] | Execute larger implementation changes after refinement choices are settled |
| [[he-code-review]] | Run readiness review before merge |
