---
name: apple-app-creator
description: Orchestrate iOS/macOS app scaffolding and optional subskill adoption for existing projects. Use when users need a guided wizard to scaffold with XcodeGen and optionally install xcode-makefiles and simple-tasks.
---

# App Creator

## Table of Contents
- [When to use](#when-to-use)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Procedure](#procedure)
- [Validation](#validation)
- [Constraints / Safety](#constraints--safety)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Resources](#resources)

## When to use
Use this skill when you want to:
- scaffold a new iOS/macOS app with XcodeGen templates;
- adopt tooling into an existing project without regenerating app code;
- install app-creator subskills (`xcode-makefiles`, `simple-tasks`) with explicit flags.

## Philosophy
- Prefer reproducible scaffolding over ad-hoc manual setup.
- Keep adoption non-destructive by default.
- Make next steps explicit with runnable commands.

## Inputs
- Project mode: `new` or `adopt`.
- App metadata in `new` mode: app name, bundle id, platform, UI framework, output directory.
- Optional subskill selection flags:
  - `--skip-xcode-makefiles`
  - `--skip-simple-tasks`
- Optional git onboarding flags:
  - `--git-init auto|never`
  - `--git-commit prompt|always|never`

## Outputs
- New scaffolded app project (new mode) or updated existing project (adopt mode).
- Optional subskill installs for makefile/task workflows.
- Printed next commands to build, run, and continue setup.

## Procedure
1. Collect required inputs for the selected mode.
2. Run doctor checks.
3. Choose mode:
   - `new`: scaffold templates + run XcodeGen;
   - `adopt`: skip scaffolding and only install selected subskills.
4. Install selected subskills (default is both unless skipped).
5. Optionally initialize git and create a baseline commit.
6. Print exact next commands.

Primary entrypoint:

```bash
skills/app-creator/scripts/init.sh --project-mode new
# or
skills/app-creator/scripts/init.sh --project-mode adopt
```

## Validation
- Run with `--dry-run` first when project state is uncertain.
- Confirm generated/updated files match the selected mode.
- If git onboarding is enabled, verify commit behavior matches flags.
- **Fail fast:** if required inputs are missing or doctor checks fail, stop and do not continue.

## Constraints / Safety
- Redact secrets, tokens, credentials, API keys, and PII in logs and shared output by default.
- Do not overwrite unrelated project files outside the selected workflow.
- Skip auto-commit if repository state is already dirty before execution.

## Anti-patterns
- Running `new` mode against an existing project expecting zero scaffolding changes.
- Skipping `--dry-run` for path-sensitive or destructive scenarios.
- Treating subskill installs as mandatory when project constraints require selective adoption.

## Examples
```bash
skills/app-creator/scripts/init.sh --project-mode new
skills/app-creator/scripts/init.sh --project-mode adopt --skip-simple-tasks
skills/app-creator/scripts/init.sh --project-mode new --dry-run
```

## Resources
- `references/workflow.md`
- `references/placeholders.md`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: decision (accepted|partial|rejected|deferred), outcome (good|neutral|bad|unknown), and confidence (high|medium|low).
- Persist feedback with python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "...".
<!-- /decision-feedback-protocol -->
