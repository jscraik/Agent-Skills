---
name: codex-ui-kit-installer
description: "Scaffold and install codex-ui-kit assets and optional prompts in a repo. Use when adding codex-ui-kit to a project."
---

# Codex UI Kit Installer

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Install the codex-ui-kit assets into a target repo and (optionally) copy the reusable prompts into the user’s Codex prompts directory.

## When to use
- Installing or updating the codex-ui-kit in a repo.
- Adding the ui-codex wrapper and schema files.
- Installing Codex UI prompts into the local prompts directory.

## Inputs
- Target repo root path.
- Whether prompts should be installed to `~/.codex/prompts`.

## Outputs
- Installed kit files in the repo.
- Optional prompts installed locally.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## When to use
- This skill applies to installing or updating codex-ui-kit. The current request is out of scope.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

## Philosophy
- Prefer least-privilege changes and explicit user consent.
- Preserve repo integrity; avoid overwriting unless instructed.
- Favor reproducible installs with clear verification steps.

## Guiding questions
- What is the exact repo root and desired install scope?
- Why is the kit needed (triage, wrapper, prompts, update)?
- Should prompts be installed locally, and is overwrite allowed?
- How will we verify the install (file checks, permissions)?

## Decision guide
- If the user wants the kit in a repo: run the installer with `--repo`.
- If the user wants prompts: add `--install-prompts` and confirm prompt location.
- If the user wants to validate without changes: use `--verify` or `--dry-run`.

## Workflow (recommended)
1) Confirm target repo root and whether prompts should be installed to `~/.codex/prompts`.
2) Run the installer script with least-privilege flags.
3) Verify files landed in the expected locations and permissions are set on `bin/ui-codex`.
4) If prompts were installed, remind user to restart Codex CLI to load them.
5) Clarify that custom prompts are local to the user’s machine and invoked explicitly (not shared via the repo).

## Quick start
Run from the skill directory or reference the script directly:

```bash
scripts/install_kit.sh --repo /path/to/repo
scripts/install_kit.sh --repo /path/to/repo --install-prompts
```

## Safety rules
- Ask before writing to `~/.codex/prompts` or any non-repo location.
- Avoid overwriting existing files unless the user explicitly approves `--force`.
- Do not add dependencies or modify package manager config.
- Prompts should be top-level Markdown files under the prompts directory; avoid subfolders.
- Redact secrets/sensitive data by default.

## Variation rules
- Vary install depth by request (repo-only vs prompts-only vs full).
- Use `--dry-run` for first-time installs or risky repos.
- Prefer `--verify` when the user wants confirmation only.
- Use different verification depth for updates vs fresh installs.

## Empowerment principles
- Empower users with a clear rollback path (delete added files).
- Empower reviewers with a checklist of installed artifacts.
- Empower maintainers with explicit notes on what changed and why.

## Anti-patterns to avoid
- Installing prompts without explicit consent.
- Overwriting custom repo files without user approval.
- Skipping executable permission checks on `bin/ui-codex`.

## Post-install checklist
- `AGENTS.md` present at repo root.
- `codex/ui_report.schema.json` present.
- `bin/ui-codex` present and executable.
- Optional: run `scripts/verify_ui_kit.sh <repo>` to confirm files and executables.
- Prompts visible after restarting Codex CLI (if installed).

## Resources

### scripts/
- `scripts/install_kit.sh`: Copies kit files into the repo, optionally installs prompts, supports `--dry-run` and `--force`.

### references/
- `references/usage.md`: Example install commands.

### assets/
- `assets/codex-ui-kit/`: Source files for AGENTS.md, schema, wrapper script, and prompts.

## Example prompts
- “Install the codex-ui-kit into this repo.”
- “Update the UI kit and install prompts locally.”
- “Verify the kit install without changing files.”

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

- Redact secrets/sensitive data by default.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
- Fail fast on first failed gate.

## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

- Redact secrets/sensitive data by default.
