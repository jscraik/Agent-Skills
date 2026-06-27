# Pull request checklist

Write for human maintainers first. Use `n.a.` with a concrete reason when a
field does not apply. Do not paste secrets, raw transcripts, bulky telemetry,
or local absolute paths.

## Motivation

- Motivation:
- Reasoning:
- Chosen approach:

## Summary

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

- Behavior or issue addressed:
- Real environment tested:
- Exact steps or command run after this patch:
- Evidence after fix:
- Observed result after fix:
- What was not tested:
- Proof limitations or environment constraints:
- Before evidence, if available:

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
- [ ] Required local gates run: `bash scripts/validate-codestyle.sh` plus the repo, package, or surface-scoped validation commands listed in Testing.
- [ ] `scripts/validate-codestyle.sh` was treated as the enforcement point for hook env sanitization (`GIT_DIR`, `GIT_WORK_TREE`, and related `GIT_*` values are untrusted and sanitized before delegated package scripts).
- [ ] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.
- [ ] North-star learning loop considered for changed files; relevant learning gate, review-context, promotion, or feedback evidence is listed below, or marked `n.a.` with a reason.
- [ ] Merge is blocked until all required checks pass.
- [ ] I will delete branch/worktree after merge.

## Testing

- verification_commands:
- verification_outcomes:
- blocked_steps_reason:
- Command: `bash scripts/validate-codestyle.sh` -> <replace with actual status and observed outcome or blocker>
- Command: `./bin/ask repo validate --json --robot` -> <replace with actual status and observed outcome, or n.a. with reason>
- Command: `./bin/ask repo closeout --changed --json --robot` -> <replace with actual status and observed outcome or blocker>
- Command: `<package-root package-manager command>` -> <replace with actual status and observed outcome, or n.a. with reason>; run package-manager gates only inside verified package roots
- Setup: `CHANGED_FILES="<comma-separated-changed-files>"` (set before running any file-scoped gates)
- Command: `<file-scoped learning/review-context gate from the owning surface>` -> <replace with actual status and observed outcome, or n.a. with reason>
- Command: `<north-star feedback or steering-uptake gate from the owning surface>` -> <replace with actual status and observed outcome, or n.a. with reason>
- Command: `harness pr-closeout --pr <number> --gates artifacts/pr-closeout/closeout-gates.json --json` -> <replace with actual status and observed outcome, or n.a. with reason>
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
