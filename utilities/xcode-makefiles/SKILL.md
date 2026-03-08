---
name: xcode-makefiles
description: Install strict Xcode Makefile tooling for iOS/macOS projects, including build/run/test scripts with AGENT_NAME-based per-agent isolation under build/. Use when a project needs reproducible local CLI builds without full app scaffolding.
---

# Xcode Makefiles

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
Use this skill when you need:
- deterministic Xcode CLI build/test/run targets;
- per-agent build isolation using `AGENT_NAME` under `build/`;
- makefile tooling added to an existing project without full scaffolding.

## Philosophy
- Keep builds reproducible and scriptable from CLI.
- Isolate agent artifacts to avoid cross-agent contamination.
- Prefer minimal install surface with explicit flags.

## Inputs
- `--project-dir PATH` (required)
- `--app-name NAME` (required)
- `--platform ios|macos` (required)
- `--mode install|upgrade` (default `install`)
- Optional:
  - `--sim-name NAME`
  - `--namespace NAME`
  - `--dry-run`

## Outputs
- Installed Makefile toolkit and scripts into target project.
- Standard build targets:
  - `make diagnose`, `make build`, `make test`, `make run`
  - `make build-and-run`, `make build-and-run-background`
  - `make clean`, `make agent-verify`
- Agent-isolated directories:
  - `build/DerivedData/<AGENT_NAME>`
  - `build/logs/<AGENT_NAME>`
  - `build/cache/<AGENT_NAME>`
  - `build/tmp/<AGENT_NAME>`

## Procedure
1. Confirm target project path and platform values.
2. Run installer in dry-run if this is a first-time setup.
3. Execute install or upgrade mode.
4. Validate make targets and script presence.
5. Run `make diagnose` and one build/test command.

Install command:

```bash
skills/xcode-makefiles/scripts/install.sh \
  --project-dir /path/to/project \
  --app-name WalkTrack \
  --platform ios
```

## Validation
- Verify required scripts were installed (`scripts/xcbuild.sh`, `scripts/diagnose.sh`, etc.).
- Run `make diagnose` and at least one of `make build` or `make test`.
- Confirm agent-specific paths resolve under `build/`.
- **Fail fast:** if required flags are missing or install validation fails, stop and do not proceed.

## Constraints / Safety
- Redact secrets, tokens, credentials, API keys, and PII from logs and shared output.
- Do not run destructive cleanup outside project-scoped `build/` directories.
- Use `--dry-run` before upgrade/install in sensitive repos.

## Anti-patterns
- Installing without confirming platform-specific settings.
- Mixing manual edits and installer output without re-running diagnostics.
- Treating `AGENT_NAME` as optional for shared multi-agent workflows.

## Variation
- Adapt install mode by context: first-time scaffold, upgrade-only, or diagnostics-only run.
- Use different validation depth for local prototyping versus CI-grade reproducibility.
- Customize platform targeting (iOS, macOS, or both) while preserving strict make-based guardrails.

## Examples
```bash
skills/xcode-makefiles/scripts/install.sh --project-dir /tmp/demo --app-name Demo --platform ios --dry-run
skills/xcode-makefiles/scripts/install.sh --project-dir /tmp/demo --app-name Demo --platform macos --mode upgrade
```

## Resources
- `references/contract.yaml`
- `references/evals.yaml`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: decision (accepted|partial|rejected|deferred), outcome (good|neutral|bad|unknown), and confidence (high|medium|low).
- Persist feedback with python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "...".
<!-- /decision-feedback-protocol -->

## Execution quality
- Philosophy: use a practical framework that balances speed, safety, and tradeoff clarity.
- Approach: choose context-specific variation rather than generic cookie-cutter steps; adapt output to repository constraints.
- Guiding question: Why is this the smallest safe change?
- Guiding question: What tradeoff are we making and why?
- Guiding question: How do we verify the result end-to-end?
- Anti-patterns: DO NOT skip validation, NEVER hide failed checks, and avoid repetitive template-only output.
- Empowerment: be capable, creative, and enable users to explore options with confidence.
