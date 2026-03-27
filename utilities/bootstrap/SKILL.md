---
name: bootstrap
description: Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
metadata:
  skill-type: scaffolding_templates

---

# Environment Bootstrap

Create a working local dev environment from a repository with reproducible setup steps and verification output.

## Table of Contents
- [When to use](#when-to-use)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Philosophy](#philosophy)
- [Inputs](#inputs)
- [Procedure](#procedure)
- [Outputs](#outputs)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [Usage](#usage)
- [Example Output](#example-output)
- [Troubleshooting](#troubleshooting)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use

Use this skill when the user asks to quickly stand up a new repo locally, reproduce onboarding setup, or validate that a project can run from a clean environment.

## Standards snapshot (March 2026)
- Prefer deterministic bootstrap over one-off shell folklore.
- Detect the stack before installing dependencies or activating toolchains.
- Use repo-native setup and validation commands when they exist.
- Record what succeeded, what was skipped, and the first blocking step if bootstrap does not finish cleanly.

## Philosophy

- Prefer deterministic setup over ad-hoc shell steps.
- Detect and report blockers early so users can recover quickly.
- Keep generated setup notes actionable for the next contributor.

## Required inputs

- Repository URL (required).
- Optional target branch/tag/ref.
- Optional runtime/tooling constraints (Node/Python/Rust versions, package manager preference).

## Procedure

1. Clone the requested repository into a clean workspace.
2. Detect project type(s) and required toolchain.
3. Install or activate required tools via mise where applicable.
4. Install project dependencies with the detected package manager/workflow.
5. Prepare environment scaffolding (`.env`, service dependencies, startup prerequisites).
6. Run a minimal startup/health verification command.
7. Record outcomes and next steps in setup artifacts.

## Deliverables

- Bootstrapped local repository ready for development (or clear failure report).
- Concise setup summary (commands executed, detected stack, verification result).
- Follow-up artifact (`SETUP.md` or `SETUP_FAILED.md`) with reproducible instructions.

## Failure mode
If clone, toolchain activation, dependency install, or the first runnable health check fails, stop at that blocker, capture the exact outcome, and leave a documented partial state rather than claiming a successful bootstrap.

## Constraints

- Redact secrets and sensitive data by default in logs, setup artifacts, and copied config values.
- Do not silently bypass failing prerequisites; surface explicit remediation steps.
- Avoid destructive system changes outside the requested repo context without user approval.

## Validation

- Verify clone success and expected directory structure.
- Verify dependency install command exits successfully.
- Verify at least one project health check/start command outcome is recorded.
- Fail fast on unrecoverable setup gates and report first actionable blocker.

## Anti-patterns

- Running broad system modifications without clear user consent.
- Suppressing setup failures to produce a false "success" status.
- Hardcoding environment-specific assumptions without documenting them.

## Variation

- Adapt the workflow depth based on user intent: quick bootstrap, full developer setup, or audit-only verification.
- Use different validation strictness for exploratory setup versus handoff-ready environment preparation.
- Customize toolchain steps per detected project type while preserving the same preflight and safety gates.

## Usage

```bash
/bootstrap https://github.com/owner/repo
/bootstrap https://github.com/owner/repo --branch develop
```

## Example Output

- Bootstrap starts with repo URL and temp work directory.
- It clones, detects project type, installs tools/dependencies, verifies startup, and writes `SETUP.md`.
- Successful run ends with a clear completion marker and per-step status.

## Troubleshooting

If bootstrap fails:

1. Check `SETUP_FAILED.md` in the workspace.
2. Review first failing command and remediation notes.
3. Re-run with explicit toolchain versions if auto-detection was ambiguous.

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[fix-mise]] | Repair mise trust issues blocking the bootstrapped environment |
| [[cloudflare-deploy]] | Deploy the bootstrapped project to Cloudflare |
| [[gh-workflow]] | Set up GitHub PR workflow after bootstrap |
| [[verification-before-completion]] | Verify the bootstrap is working before continuing |

**Topic map:** [[backend-platform]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
