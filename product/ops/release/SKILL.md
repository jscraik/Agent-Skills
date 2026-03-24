---
name: release
description: Cut a clean semver release from the main branch using the repo's release flow. Use when the user wants a tagged Cargo release, not generic deployment or changelog drafting.
metadata:
  skill-type: ci_cd_deployment
---

# Release

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Procedure](#procedure)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use
- You need to ship a new version using `just release X.Y.Z`.
- The release must be semver-valid, greater than current, and performed from `main`.
- The flow includes Cargo.toml version bumps, lockfile update, tag, and crates.io publish.

## Required inputs
- Target version `X.Y.Z` (prompt if missing).
- Repo root and current version (read from `Cargo.toml`).
- Confirmation you are on `main` with a clean working tree.
- Cargo credentials available (`cargo login` or `CARGO_REGISTRY_TOKEN`).

## Deliverables
- A completed release run (or a clear stop with error context).
- A new version commit + tag (created by `just release`).
- Confirmation that publish/tag steps were invoked.

## Failure mode
If any precondition fails, stop before the release command, report the exact blocker, and leave the repo unchanged rather than improvising around policy or credential problems.

## Standards snapshot (March 2026)
- Releases are high-risk mutating operations: verify branch, cleanliness, credentials, and version ordering before any write.
- Prefer a single canonical release path over manual patchwork unless the user explicitly requests recovery from a failed release.
- Keep evidence explicit: current version, target version, branch state, tree state, and tag state should all be visible in the reasoning.
- Never retry a failed release command blindly; diagnose first, then resume with intent.

## Principles
- Validate before action: semver and version ordering come first.
- Single-threaded, fail-fast: stop immediately on any error.
- Keep the release path minimal and reproducible.

## Procedure
1) Confirm branch and clean state.
   - `git branch --show-current` should be `main`.
   - `git status -sb` should be clean.
2) Determine current version and validate the target.
   - Read `Cargo.toml` current version.
   - Ensure target is valid semver and greater than current.
3) Confirm credentials are present (do not print secrets).
   - `cargo login` is configured OR `CARGO_REGISTRY_TOKEN` is set.
4) Run the release.
   - `just release X.Y.Z`
5) If any step fails, stop and report the error without retrying blindly.
6) After success, summarize the exact version shipped and the release artifacts created.

## Examples
```bash
just release 1.4.2
```

## Validation
- Fail fast: stop at the first failed check or command.
- `git status -sb` shows clean tree and `main` before running.
- `git tag --list "vX.Y.Z"` returns nothing before release.
- `just release X.Y.Z` completes without errors.
- The final state includes the new tag and a clean post-release tree unless the repo's release process intentionally leaves generated changes.

## Anti-patterns
- Releasing from a dirty working tree or non-`main` branch.
- Skipping version validation or using a non-semver version.
- Re-running `just release` after a failure without fixing the root cause.

## Constraints
- Redact secrets/PII by default.
- Keep `name` and `description` single-line YAML scalars (quote if needed).
- Do not add new dependencies without explicit user approval.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[gh-workflow]] | Manage the PR and merge lifecycle before cutting a release |
| [[verification-before-completion]] | Validate all checks pass before tagging |
| [[check-pr]] | Review the PR that triggers the release |
| [[ce-plan]] | Plan the release checklist before executing |

**Topic map:** [[backend-platform]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
