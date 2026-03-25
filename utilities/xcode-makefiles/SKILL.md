---
name: xcode-makefiles
description: Install strict Xcode Makefile tooling for iOS/macOS projects, including build/run/test scripts with AGENT_NAME-based per-agent isolation under build/. Use when a project needs reproducible local CLI builds without full app scaffolding.
metadata:
  skill-type: scaffolding_templates
---

# Xcode Makefiles

Install strict CLI-first Xcode build tooling with per-agent isolation for iOS and macOS projects.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Keep builds deterministic and scriptable from the command line.
- Isolate agent artifacts under `build/<...>/<AGENT_NAME>` to avoid cross-agent contamination.
- Prefer installer-driven setup over manual file copying.
- Validate with `make diagnose` before trusting the toolchain.

## When to use
- A project needs reproducible CLI build and test targets for Xcode work.
- The user wants strict Makefile tooling without full app scaffolding.
- Multiple agents or contributors need isolated build state in the same repo.

## Required inputs
- `--project-dir PATH`
- `--app-name NAME`
- `--platform ios|macos`
- Optional:
  - `--mode install|upgrade`
  - `--sim-name NAME`
  - `--namespace NAME`
  - `--dry-run`

## Deliverables
- Installed Makefile toolkit and scripts.
- Standard build and test targets such as `make diagnose`, `make build`, `make test`, and `make run`.
- Agent-isolated directories under `build/`.

## Philosophy
- Xcode automation should be reproducible enough to trust in both solo and multi-agent workflows.
- Isolation beats convenience when build state can leak across runs.
- Diagnostics belong before build optimism.

## Failure mode
- If the project needs full app scaffolding, use a scaffold-oriented Apple build skill instead.
- If the platform or app name is missing, stop before install.
- If the repo has custom Xcode automation that would conflict with this toolkit, make that collision explicit first.

## Constraints
- Redact secrets, tokens, credentials, API keys, and PII from logs and shared output.
- Do not run destructive cleanup outside project-scoped `build/` directories.
- Prefer `--dry-run` before install or upgrade in sensitive repos.

## Workflow
1. Confirm project path, app name, and platform.
2. Run dry-run if the repo is new to this tooling or already has build scripts.
3. Execute install or upgrade mode.
4. Verify required scripts and Makefile targets are present.
5. Run `make diagnose` and at least one build or test command.

## Anti-patterns
- Installing without confirming iOS versus macOS targeting.
- Mixing manual edits with installer output and skipping diagnostics.
- Treating `AGENT_NAME` isolation as optional in shared agent workflows.

## Validation
- Fail fast: stop at the first missing required flag or failed diagnose step.
- Verify required scripts were installed.
- Run `make diagnose` and at least one of `make build` or `make test`.
- Confirm agent-specific paths resolve under `build/`.

## Examples
```bash
skills/xcode-makefiles/scripts/install.sh --project-dir /tmp/demo --app-name Demo --platform ios --dry-run
skills/xcode-makefiles/scripts/install.sh --project-dir /tmp/demo --app-name Demo --platform macos --mode upgrade
```

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[apple-app-creator]] | Install xcode-makefiles after scaffolding with apple-app-creator |
| [[circleci]] | Integrate Make targets into CircleCI pipeline |
| [[verification-before-completion]] | Verify Make targets build cleanly before completing |
| [[recon-workbench]] | Audit Makefile build outputs for security |

**Topic map:** [[mobile-native]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
