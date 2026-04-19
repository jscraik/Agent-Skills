---
name: vale
description: "Set up and verify Vale prose linting across local, pre-commit, and CI workflows. Use when users ask to install Vale, repair broken config or style sync, or enforce docs linting gates."
metadata:
  skill-type: runbook
  lifecycle_state: active
  maturity: validated
  owner: agent-ops
  review_cadence: quarterly
  last_reviewed: 2026-04-18
  metadata_source: frontmatter
---

# Vale

Use this skill to make Vale actually work end-to-end: install, `.vale.ini` setup, style package sync, local verification, and CI enforcement.

## When to use

- User asks to add Vale to a repository and make prose linting reproducible.
- User reports Vale is installed but failing due to missing config, styles, or packages.
- User asks to harden docs linting in CI or pre-commit with deterministic commands.
- User wants Vale troubleshooting with exact pass/fail blockers and minimal guesswork.

## Non-triggers
- Deep editorial policy design for an organization-wide style guide from scratch.
- General grammar proofreading requests without tool setup or automation needs.
- OpenAI API docs requests (route to `[[openai-docs]]`).

## Required inputs
- Repository root and target prose paths (for example `docs/`, `README.md`).
- Desired severity gate for enforcement (`suggestion`, `warning`, or `error`).
- Preferred execution surface (`local`, `pre-commit`, `CI`, or all three).
- Existing `.vale.ini` and styles directory status if already present.

## Discovery interview
- Ask one round at a time when setup scope is underspecified.
- Use a plain-language question for each discovery round.
- Explain why the round matters before asking for details.
- Avoid dumping the whole interview plan at once.

## Deliverables
- A working Vale command path with exact commands and outcomes.
- A valid `.vale.ini` with explicit `StylesPath`, alert level, and style bindings.
- Package synchronization guidance (`Packages` + `vale sync`) when external styles are used.
- CI and/or pre-commit gate commands with clear failure criteria.
- Troubleshooting notes tied to observed failures.
- Machine-readable response envelope including `schema_version` for automation consumers.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default in logs and examples.
- Keep setup non-destructive; do not delete style/config directories as a first step.
- When network access is needed (for package sync/download), use minimal required domains only.
- Prefer focused rollout (2-3 surfaces first: local CLI, pre-commit, CI) before broader expansion.

## Core principles
- Verify installation before editing config.
- Keep style assets in-repo and sync packages deterministically.
- Fail fast on the first broken gate and report exact blockers.
- Use machine-readable output (`line` or `JSON`) when integrating with automation.
- Prefer pinned integration revisions in repo config; avoid floating tags in production pipelines.

## Workflow
1. Discover current state:
   - Check `vale --version`.
   - Check config resolution with `vale ls-config`.
   - Confirm whether `.vale.ini` and `styles/` exist.
2. Install or upgrade Vale if missing:
   - macOS: `brew install vale`
   - Linux snap: `snap install vale`
   - Windows choco: `choco install vale`
3. Implement/repair config:
   - Create or update `.vale.ini` with `StylesPath`, `MinAlertLevel`, and style selection.
   - Keep file globs explicit (for example `[*.{md,adoc}]`).
4. Sync style packages when `Packages` are declared:
   - Run `vale sync` before linting.
5. Validate local behavior:
   - Run `vale --output=line --minAlertLevel=error <target>`.
   - For automation adapters, run `vale --output=JSON <target>`.
6. Wire automation:
   - Pre-commit lane: run `vale sync` hook before lint hook.
   - CI lane: run Vale on docs paths and fail on configured level.
7. Finalize with explicit evidence:
   - Record command outcomes as `pass|fail|blocked`.
   - Include exact blocker text for failed runs.

## Validation
- `vale --version`
- `vale ls-config`
- `vale sync` (when `.vale.ini` has `Packages = ...`)
- `vale --output=line --minAlertLevel=error docs/`
- `vale --output=JSON docs/`
- `bash Infrastructure/scripts/verify-vale-setup.sh docs/` (from this skill package)
- Stop on first failure and report the exact command and stderr.

## Gotchas
- `Packages` changes do nothing until `vale sync` is re-run.
- Missing or wrong `StylesPath` causes silent rule non-loading and confusing "style not found" failures.
- Running Vale from a subdirectory can change config discovery; verify via `vale ls-config`.
- CI failures often come from path-glob drift (`[*.md]` vs `[*.{md,adoc}]`) rather than rule quality.

## Anti-patterns
- Skipping `vale sync` after adding or changing packages.
- Committing CI checks that use default Vale output when machine parsing is required.
- Using broad, unscoped glob patterns that lint generated or vendored content unintentionally.
- Treating editor warnings as proof that CLI/CI integrations are configured correctly.

## Output contract

```yaml
schema_version: 1
status: complete|partial|blocked
summary: "<what was configured or fixed>"
commands:
  - command: "<exact command>"
    outcome: pass|fail|blocked
    note: "<optional stderr or blocker>"
artifacts:
  - path: "<config/workflow file path>"
    purpose: "<why it matters>"
residual_risks:
  - "<remaining risk or follow-up>"
```

## Failure mode
- If Vale is not installed and package manager install is blocked, return `blocked` with the exact install command and error.
- If `.vale.ini` exists but references missing styles, run `vale ls-config` and `vale ls-dirs`, then report the exact missing path mismatch.
- If `vale sync` fails due to network/auth restrictions, preserve current config, mark package sync as `blocked`, and provide minimal next command.
- If CI still fails after local pass, capture the CI command path and failing file glob before making additional config edits.

## Examples
- Triggering prompt: "GitHub Actions fails with `vale: command not found` but it works on my laptop. Wire this so local, pre-commit, and CI all run the same check."
- Triggering prompt: "After adding `Packages = Google, Microsoft` we now get `StylesPath does not exist`. Can you diagnose from `.vale.ini` and give the exact repair commands?"
- Triggering prompt: "Our PR bot needs parseable lint output for annotations. Show the exact Vale command and output mode we should standardize on."
- Non-triggering prompt: "Please rewrite this release note to sound friendlier."

## References
- `Infrastructure/references/context7-notes.md`
- `Infrastructure/references/contract.yaml`
- `Infrastructure/references/evals.yaml`
- `Infrastructure/references/discovery-interview.md`
- `Infrastructure/scripts/verify-vale-setup.sh`

## See Also

| Skill | When to use together |
|---|---|
| `[[context7]]` | Pull current Vale docs and integration guidance before changing commands or flags |
| `[[docs-expert]]` | Improve writing content after lint setup is stable |
| `[[npm-workflow-discipline]]` | Wire Vale checks into package scripts and CI script contracts |

**Topic map:** [[agent-ops]]