---
name: skill-pr-delivery
description: Ship a Codex skill change from source edits through sync, audit, inspector review, commit, push, and PR evidence. Use when adding, hardening, skillifying, or making a skill available and the user wants the work delivered to a pull request.
metadata:
  skill-type: team_automation
---

# Skill PR Delivery

Use this skill when a skill package needs to become a real repository change, not just a draft instruction. It coordinates the skill source, runtime projection, reviewer feedback, and GitHub delivery evidence.

This skill owns skill lifecycle delivery. It does not replace the lower-level skill authoring guidance in `$skill-creator` or `$skill-factory`; use those for how to design the skill body, then use this skill to make the change shippable.

## When to use

- The user asks to add, harden, skillify, install, or make a skill available and also wants commit, push, PR, or reviewer validation.
- The work touches `Skills/**`, plugin-bundled skills, skill selection policy, runtime skill sync, or skill package metadata.
- The user asks to validate a skill with `skill-inspector`, CodeRabbit, CI, or PR checks.
- A completed workflow should be captured as a reusable skill and delivered on the active branch.

Do not use this skill for ordinary code changes that do not involve skill packages, or for one-off prompt advice that does not need repository delivery.

## Inputs

- Target skill name and canonical source path, if already known.
- Source workflow, existing skill, or user intent to capture.
- Desired visibility: default runtime skill, advanced repository skill, plugin lane skill, or local-only draft.
- Base branch and active branch or PR when the user names them.
- Required reviewers, such as `skill-inspector`, CodeRabbit, or a user-named agent.

## Outputs

- Updated canonical skill source under the repo-owned skill path.
- Supporting references such as `references/contract.yaml`, `references/evals.yaml`, and task-profile metadata when the repo expects them.
- Runtime sync evidence when the skill should be available to Codex.
- Inspector or reviewer findings, fixes, and re-review status when requested or risk warrants it.
- Commit, push, PR URL, and check status when the user asks for delivery.
- `schema_version` in any structured output contract that the skill package introduces.

## Philosophy

- A skill is not delivered until source, runtime projection, review state, git state, and PR state agree.
- Default visibility is an explicit product decision, not a side effect of creating a useful skill.
- Reviewer findings are part of the work, so blocking findings must be resolved before readiness claims.
- Preserve unrelated local work and prefer blocked status over cleanup shortcuts that would destroy user changes.

## Workflow

1. Resolve the operating lane.
   - Classify the request as create, harden, skillify, install, visibility change, or PR delivery.
   - If the request explicitly invokes `$skill-factory`, `$skill-creator`, or another skill-authoring skill, read that skill first and use it for the authoring portion.
   - Record the intended deliverable and stop early only when the destination or user intent is genuinely unsafe or unknowable.

2. Establish repository state.
   - Run `pwd` and `git status --short --branch`.
   - Check the active branch and upstream with `git branch -vv` when a push or PR is in scope.
   - If the branch is behind its upstream, use the user's preferred non-rebase pull strategy: `git pull --no-rebase`.
   - Preserve unrelated local changes. If unrelated edits conflict with the skill delivery, report the blocker instead of overwriting them.

3. Locate canonical skill ownership.
   - Prefer repo source under `Skills/**` or the plugin skill source that owns the package.
   - Do not edit generated runtime mirrors such as `.agents/**` as the source of truth.
   - If the skill already exists in another checkout or runtime cache, copy only the intentional package source into the current repository path and then validate it from there.

4. Author the skill package.
   - Keep `SKILL.md` focused on triggers, inputs, workflow, validation, failure modes, and see-also routing.
   - Move detailed contracts, examples, evals, or task-profile metadata into `references/**` or the repo's established reference location.
   - Include progressive-disclosure links in `SKILL.md` so future agents know when to read each reference.
   - Avoid duplicate task-profile files unless the repo's validators require both; when both are required, keep their content identical.

5. Decide runtime visibility deliberately.
   - If the user asks to use the skill in every project or make it available by default, update the repo's canonical selection policy and document why the default surface needs it.
   - If the skill is narrow, experimental, or project-specific, leave it discoverable through repository scan or advanced modes rather than adding it to the default flat runtime surface.
   - After any selection-policy change, run the focused lifecycle tests that cover sync and selection behavior.

6. Sync only from canonical source.
   - Use `./bin/ask skills sync --scope workspace --json` when workspace runtime projection is needed.
   - Use `./bin/ask skills sync --scope user --json` when the user-level Codex runtime should see the skill.
   - After sync, verify the projected skill path or skill list rather than assuming sync succeeded.

7. Validate the skill package.
   - Run `./bin/ask skills audit <skill-path> --level strict --json`.
   - Run `git diff --check` before committing.
   - Run focused unit tests when sync, selection policy, package shape, or lifecycle validation changed.
   - Capture exact pass, fail, skipped, or blocked outcomes.

8. Use reviewer validation when requested or high-risk.
   - Spawn `skill-inspector` as a no-edit reviewer for new, default-visible, or substantially changed skills.
   - Ask for severity-ranked findings with exact file and line evidence.
   - Fix blocking findings and run a follow-up inspection when the first review found blockers.
   - Do not treat a mailbox update as review evidence; use the reviewer's actual findings or artifact output.

9. Deliver through git and GitHub when requested.
   - Stage only intended files.
   - Commit with the required repository trailer.
   - Push the active branch.
   - Create or update the PR with a concise scope, validation evidence, and risk notes.
   - Run `gh pr checks <number> --watch=false` and report the current check state.

## Validation

Use the smallest set that proves the touched surface:

- `./bin/ask skills audit Skills/agent-ops/<skill-name> --level strict --json`
- `git diff --check`

When skill sync or selection policy changed, add:

- `./bin/ask skills sync --scope workspace --json`
- `./bin/ask skills sync --scope user --json`
- `uv run --python 3.12 -m unittest Infrastructure.tests.test_ask_skills_sync_security Infrastructure.scripts.testing.test_skill_lifecycle_validation`

When PR delivery is in scope, add:

- `gh pr checks <number> --watch=false`

Fail fast at the first failed required gate. Do not commit, push, or mark the PR ready until the failed gate is resolved or explicitly documented as blocked.

## Constraints

- Redact secrets, tokens, credentials, private transcript details, and sensitive repository data by default.
- Do not copy raw private logs into skill package files; summarize evidence when history matters.
- Do not use destructive git cleanup such as `git reset --hard`, `git checkout --`, or force push unless the user explicitly requests that exact operation and the repo state is understood.
- Do not overwrite unrelated local changes while staging or syncing skill files.
- Do not broaden the default runtime surface without a recorded visibility decision.
- Keep generated runtime projections out of the commit unless the repository explicitly tracks them.

## Failure mode

- If the repo has conflicting instructions about skill ownership or validation, stop and resolve the contradiction before editing.
- If runtime sync succeeds but the projected skill is missing, treat it as a delivery blocker and inspect selection policy before committing.
- If the reviewer returns blockers, fix them before claiming the skill is ready.
- If GitHub auth, network, or branch protection blocks PR delivery, leave the branch and commit state clear and report the exact blocker.

## Anti-patterns

- Editing `.agents/**` directly and calling it the canonical skill change.
- Adding every new skill to the default runtime surface without a visibility decision.
- Committing after an inspector review with unresolved high-severity findings.
- Reporting "PR ready" without fresh `gh pr checks` or equivalent check evidence.
- Re-running broad validation repeatedly when a focused failing gate already identifies the blocker.

## Examples

- "Create this skill, sync it for Codex, validate with skill-inspector, then push it to the PR."
- "We just proved out this workflow. Skillify it and deliver it on the current branch."
- "Make this skill default-visible in every project, but validate the selection policy and runtime sync."
- "The inspector found blockers on the skill package. Fix them and rerun the review before pushing."

## References

Read these only when the task needs the extra contract detail:

| Reference | Read when |
| --- | --- |
| [references/contract.yaml](./references/contract.yaml) | Checking expected triggers, outputs, risks, observability, or rollback behavior. |
| [references/evals.yaml](./references/evals.yaml) | Updating routing examples, eval prompts, or expected skill-selection behavior. |
| [Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml) | Inspecting the security-gate eval mirror consumed by lifecycle diagnostics; keep it in parity with `references/evals.yaml`. |
| [Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json) | Inspecting machine-readable task-profile metadata used by lifecycle diagnostics. |
| [references/task-profile.json](./references/task-profile.json) | Inspecting the compatibility task profile required by family benchmark tooling; parity with `Infrastructure/references/task-profile.json` is enforced by centralized validators. |

## See Also

| Skill | Why |
| --- | --- |
| [[skill-creator]] | Use for general guidance on creating a well-formed skill body. |
| [[skill-factory:skill-factory-router]] | Use when the user asks for Skill Factory lane routing before authoring or hardening. |
| [[gh-workflow]] | Use for deeper GitHub issue, review, CI, or merge lifecycle operations. |
| [[verification-before-completion]] | Pair when the user asks for strict completion evidence beyond the skill package itself. |

**Topic map:** [[agent-ops]]
