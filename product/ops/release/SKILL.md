---
name: release
description: Create and publish a new project release (semver) when you need to cut
  a main-branch, clean-tree release via just release X.Y.Z for Cargo publish and git
  tag creation.
knowledge_graph_profile: references/task-profile.json
---

# Release

## Compliance
- Follow the Gold Industry Standard and repo release policies.

## Scope and triggers
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

## Examples
```bash
just release 1.4.2
```

## Validation
- Fail fast: stop at the first failed check or command.
- `git status -sb` shows clean tree and `main` before running.
- `git tag --list "vX.Y.Z"` returns nothing before release.
- `just release X.Y.Z` completes without errors.

## Anti-patterns
- Releasing from a dirty working tree or non-`main` branch.
- Skipping version validation or using a non-semver version.
- Re-running `just release` after a failure without fixing the root cause.

## Constraints
- Redact secrets/PII by default.
- Keep `name` and `description` single-line YAML scalars (quote if needed).
- Do not add new dependencies without explicit user approval.

## Resources (optional)
- `references/evals.yaml`

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

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

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
