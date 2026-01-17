---
name: codex-ui-kit-installer
description: Install or update codex-ui-kit in a repo and optional Codex UI prompts. Not for general skill installation; use skill-installer or clawdhub.
metadata:
  short-description: Install Codex UI kit
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

## Browser handling (macOS)
- If Safari is not the default macOS browser and you need to open URLs in Safari, use `open -a Safari "<url>"`.

## Post-install checklist
- `AGENTS.md` present at repo root.
- `codex/ui_report.schema.json` present.
- `bin/ui-codex` present and executable.
- `bin/ios-web` present and executable; default profile opens iPad 13" Safari.
- `bin/ios-web-storybook` and `bin/ios-web-openai` present for Storybook/OpenAI widget presets.
- Optional: run `scripts/verify_ui_kit.sh <repo>` to confirm files, executables, and simctl availability.
- Prompts visible after restarting Codex CLI (if installed).

## iOS simulator defaults (web UI preview)
- `bin/ios-web` now defaults to an iPad 13" profile (iPad Air 13-inch (M2)) and always uses Safari via simctl openurl.
- Fallback order: target device name → any available iPad → any available iPhone.
- Example (React/Vite/OpenAI widgets): start your dev server on port 5173, then run  
  `bin/ios-web --path / --port 5173 --profile ipad_13 --snap ./artifacts/ios-ipad13.png`
- Example (Storybook): `bin/ios-web --port 6006 --profile ipad_13`
- Presets: `bin/ios-web-storybook` (port 6006, iPad 13), `bin/ios-web-openai` (port 5173, iPad 13).
- Xcode-beta: if you need the beta toolchain, pass `--developer-dir /Applications/Xcode-beta.app/Contents/Developer` to `ios-web` (presets inherit it via extra args).
- For native SwiftUI/SwiftPM apps, use the ios-debugger-agent/xcode-build skills to run the app; use `ios-web` only for web surfaces.

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

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: codex-ui-kit-installer
description: Install or update the codex-ui-kit into a repository (AGENTS.md, codex/ui_report.schema.json, bin/ui-codex) and optionally install Codex UI prompts into ~/.codex/prompts. Use when asked to set up the Codex UI triage/fix workflow, add the ui-codex wrapper, refresh a repo with the kit contents, or install codex-ui-kit.zip.
metadata:
  short-description: Install Codex UI kit
---
```
Body:

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

## Browser handling (macOS)
- If Safari is not the default macOS browser and you need to open URLs in Safari, use `open -a Safari "<url>"`.

## Post-install checklist
- `AGENTS.md` present at repo root.
- `codex/ui_report.schema.json` present.
- `bin/ui-codex` present and executable.
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

### copilot variant
Frontmatter:

```yaml
---
name: codex-ui-kit-installer
description: Install or update the codex-ui-kit into a repository (AGENTS.md, codex/ui_report.schema.json, bin/ui-codex) and optionally install Codex UI prompts into ~/.codex/prompts. Use when asked to set up the Codex UI triage/fix workflow, add the ui-codex wrapper, refresh a repo with the kit contents, or install codex-ui-kit.zip.
metadata:
  short-description: Install Codex UI kit
---
```
Body:

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

## Browser handling (macOS)
- If Safari is not the default macOS browser and you need to open URLs in Safari, use `open -a Safari "<url>"`.

## Post-install checklist
- `AGENTS.md` present at repo root.
- `codex/ui_report.schema.json` present.
- `bin/ui-codex` present and executable.
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
