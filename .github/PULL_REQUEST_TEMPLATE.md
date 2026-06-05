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

- Behavior or issue addressed: describe the observable behavior, issue, or n.a. reason
- Real environment tested: list the real environment, production path, or n.a. reason
- Exact steps or command run after this patch: list exact steps, command, or n.a. reason
- Evidence after fix: link artifact, copied output, screenshot, redacted log, runtime-card ref, or n.a. reason
- Observed result after fix: state the observed result, or n.a. reason
- What was not tested: list untested paths, or `none` with reason
- Proof limitations or environment constraints: state limitations, blockers, or `none`
- Before evidence, if available: link before evidence, summarize baseline, or `n.a.` with reason

Behavior proof guidance: Behavior proof is separate from unit tests, lint,
typecheck, and CI. Use it to show the actual production path or nearest
meaningful operator path after the patch. If the exact path could not run,
state the blocker and the nearest fallback. Do not paste secrets, raw
transcripts, bulky telemetry, or local absolute paths.

## Work performed

- Plan IDs: list Linear keys, spec paths, plan paths, or `n.a.` with reason
- Linear reference: list `Refs JSC-N`, `Fixes JSC-N`, `Closes JSC-N`, or `n.a.` with reason
- Linked issue relationship: classify the linked issue relationship as implementation closure, preparatory/enabling work, standalone/untracked work, or `n.a.` with reason; for parent-goal references, state completed acceptance IDs or `none`
- Phase / slice: list completed phase, implementation slice, or `n.a.` with reason
- Session IDs: list Codex thread/session IDs, session-collector artifact IDs or paths, harness run IDs, or `n.a.` with reason. For AI-assisted work, include at least one session reference or explain why no session artifact was captured.
- Trace IDs: list CI workflow/job URLs, harness/eval/runtime trace IDs, runtime-card/evidence bundle artifact paths, review trace IDs, or `n.a.` with reason. For traced or evaluated work, include the trace or artifact reference used to verify the claim.
- AI session / traceability: map the AI session or trace reference to the work it supports; do not paste raw transcripts, prompts, secrets, or bulky telemetry into the PR body.
- Completed work: list implementation units, docs/config changes, or evidence-only work completed in this PR
- Affected surfaces: list code, tests, docs, PR template, CLI reference, workflow config, generated artifacts, examples, or `n.a.` with reason
- Documentation impact: classify required docs as updated or `n.a.` with reason, including README.md, SECURITY.md, CONTRIBUTING.md, AGENTS.md, ARCHITECTURE.md, governance docs, and existing deep-module README files; list docs-expert or reviewer evidence for high-impact documentation changes
- Documentation lifecycle impact: classify created, updated, deprecated, superseded, archived, removed, or `n.a.` with reason; include canon class and distribution impact when docs changed
- SemVer impact: classify none, patch, minor, major, or `n.a.` with reason; explain downstream-template or packaged-skill impact when present
- Expected outcome alignment: state how this change preserves Coding Harness as a portable agent operating system for greenfield and brownfield repos, or mark `n.a.` with reason
- Pattern scope inventory: for any steering feedback, review comment, or line-level correction that implies a broader design/API principle, name the principle, list sibling implementations or similar misbehavior classes searched, and state which siblings were changed, intentionally left unchanged, or deferred with tracker/evidence
- Meta-behavior proof: for repeated steering or high-signal corrections, name the durable repo/system change plus concrete repo path, command, or issue ID that prevents recurrence, or `n.a.` with tracked exception reason
- Repeated-error research: when the same error occurs twice, use `Source: ...; Candidate 1: ...; Candidate 2: ...; Candidate 3: ...; Chosen: ...; Implemented: ...`; otherwise `n.a.` with reason
- Acceptance trace: map completed acceptance items to evidence refs, or `n.a.` with reason
- Validation evidence: list command outcomes, CI jobs, repo-relative artifact paths, or `n.a.` with reason; do not paste local absolute paths
- Review artifacts: list CodeRabbit, Codex, reviewer, or harness review artifacts, or `n.a.` with reason
- Durable evidence map: classify every local-only artifact reference as tracked receipt, PR comment, CI artifact URL, runtime-card/evidence-bundle ref, or `n.a.` with reason; use repo-relative paths only
- Runtime impact: state direct, transitive, dev-only, CI-only, runtime-facing, or `n.a.` with reason
- CodeRabbit mode coverage: list analysis, validation, gate, closeout, promotion, or `n.a.` with reason
- Closeout state: classify PR state, merge or auto-merge state, branch/worktree state, Linear state, next-lane routing, and any remaining blocker or waiting owner
- Learning / reinforcement: list promoted learnings, memory updates, or `none` with reason
- Deferred work: list follow-up work intentionally left out, or `none`

## Checklist

- [ ] I did not push directly to `main`; this PR is from a dedicated branch.
- [ ] Branch name follows policy (`codex/*` for agent-created branches).
- [ ] Required local gates run: `bash scripts/validate-codestyle.sh`, `pnpm check`, `bash scripts/run-harness-gate.sh tooling-audit --path . --json`.
- [ ] `scripts/validate-codestyle.sh` was treated as the enforcement point for hook env sanitization (`GIT_DIR`, `GIT_WORK_TREE`, and related `GIT_*` values are untrusted and sanitized before `pnpm run`).
- [ ] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.
- [ ] North-star learning loop considered for changed files; relevant learning gate, review-context, promotion, or feedback evidence is listed below, or marked `n.a.` with a reason.
- [ ] Merge is blocked until all required checks pass.
- [ ] I will delete branch/worktree after merge.

## Testing

- verification_commands: list exact commands run here
- verification_outcomes: record pass/fail/blocked for each command here
- blocked_steps_reason: none if all planned steps ran
- Command: `bash scripts/validate-codestyle.sh` -> pass/fail
- Command: `pnpm check` -> pass/fail
- Command: `bash scripts/run-harness-gate.sh tooling-audit --path . --json` -> pass/fail
- Setup: `CHANGED_FILES="<comma-separated-changed-files>"` (set before running file-scoped gates)
- Command: `bash scripts/run-harness-gate.sh learnings gate --source .harness/learnings/coderabbit.local.json --files "$CHANGED_FILES" --json` -> pass/fail/n.a.
- Command: `bash scripts/run-harness-gate.sh review-context --source .harness/learnings/coderabbit.local.json --files "$CHANGED_FILES" --json` -> pass/fail/n.a.
- Command: `bash scripts/run-harness-gate.sh north-star-feedback --source .harness/learnings/coderabbit.local.json --json` -> pass/fail/n.a.
- Command: `harness pr-closeout --pr <number> --gates artifacts/pr-closeout/closeout-gates.json --json` -> pass/fail/n.a.
- Any other command(s):

## Review artifacts

- Review status:
  - CodeRabbit review: pending completion and finding resolution or waiver.
  - Independent reviewer: pending confirmation that review was performed outside the coding agent.
  - Codex review: pending completion and finding resolution or waiver.
- CodeRabbit: <link / artifact path / comment ID>
- Independent reviewer evidence: <reviewer + link>
- Codex: <link / artifact path / comment ID>
- CodeRabbit Semgrep: fixed / waived with rationale / n.a.
- Additional evidence (if any):

## Notes

Add one-paragraph merge rationale here.
