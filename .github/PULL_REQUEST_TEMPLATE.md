# Pull request checklist

Write for human maintainers first. Use `n.a.` with a concrete reason when a
field does not apply. Do not paste secrets, raw transcripts, bulky telemetry,
or local absolute paths.

## What Problem This Solves

- Motivation:
- Reasoning:
- Chosen approach:

## Why This Change Was Made

- Problem:
- Why now:
- Intended outcome:
- Out of scope:
- Reviewer focus:
- Risk and rollback:

## Behavior Proof

Complete this section when the PR changes runtime behavior, CLI behavior,
generated artifacts, validation behavior, agent workflow behavior, user-facing
docs, or any observable operator experience. Use `n.a.` with a concrete reason
for docs-only, metadata-only, or evidence-only changes where no behavior path
exists.

- Behavior before fix:
- Behavior or issue addressed:
- Real environment tested:
- Exact steps or command run after this patch:
- Evidence after fix:
- Observed result after fix:
- What was not tested:
- Proof limitations or environment constraints:

Behavior proof guidance: Behavior proof is separate from unit tests, lint,
typecheck, and CI. Use it to show the actual production path or nearest
meaningful operator path after the patch. If the exact path could not run,
state the blocker and the nearest fallback. Do not paste secrets, raw
transcripts, bulky telemetry, or local absolute paths.

## Work performed

- Plan IDs:
- Linear reference:
- Linked issue relationship:
- Phase / slice:
- Session IDs:
- Trace IDs:
- AI session / traceability:
<!-- Cite durable session/run/runtime-card references when available. Do not paste raw transcripts, prompts, secrets, or bulky telemetry. -->
- Completed work:
- Affected surfaces:
- Documentation impact:
- Documentation lifecycle impact:
- SemVer impact:
- Expected outcome alignment:
- Pattern scope inventory:
- Meta-behavior proof:
- Repeated-error research:
- Acceptance trace:
- Validation evidence: See Testing.
- Review artifacts: See Review artifacts.
- Durable evidence map:
- Runtime impact:
- CodeRabbit mode coverage:
- Closeout state:
<!-- Closeout state must classify PR state, merge or auto-merge state, branch/worktree state, Linear state, next-lane routing, and any remaining blocker or waiting owner. -->
- Learning / reinforcement:
- Deferred work:

## Checklist

- [ ] I did not push directly to `main`; this PR is from a dedicated branch.
- [ ] Branch name follows policy (`codex/*` for agent-created branches).
- [ ] Required local gates run: `bash scripts/validate-codestyle.sh`, `pnpm check`, `bash scripts/run-harness-gate.sh tooling-audit --path . --json`.
- [ ] `scripts/validate-codestyle.sh` was treated as the enforcement point for hook env sanitization (`GIT_DIR`, `GIT_WORK_TREE`, and related `GIT_*` values are untrusted and sanitized before `pnpm run`).
- [ ] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.
- [ ] North-star learning loop considered for changed files; relevant learning gate, review-context, promotion, or feedback evidence is listed below, or marked `n.a.` with a reason.
- [ ] This change is user-facing and I added a changelog entry.
- [ ] This change is not user-facing.
- [ ] Merge is blocked until all required checks pass.
- [ ] I will delete branch/worktree after merge.

## Testing

- regression_test_plan:
- verification_commands:
- verification_outcomes:
- blocked_steps_reason:
<!-- Add one or more evidence lines such as:
- Command: `bash scripts/validate-codestyle.sh` -> pass
- Command: `pnpm check` -> blocked (reason)
- Command: `bash scripts/run-harness-gate.sh tooling-audit --path . --json` -> n.a. (reason)
-->
- Any other command(s):

## Review artifacts

- Review status:
  - CodeRabbit review: pending completion and finding resolution or waiver.
  - Independent reviewer: pending confirmation that review was performed outside the coding agent.
  - Codex review: pending completion and finding resolution or waiver.
- CodeRabbit:
- Independent reviewer evidence:
- Codex:
- CodeRabbit Semgrep:
- Additional evidence (if any):

## Notes

<!-- Add one-paragraph merge rationale before requesting review. -->
