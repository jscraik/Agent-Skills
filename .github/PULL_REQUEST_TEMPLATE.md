# Pull request

Write for maintainers. Use `n.a.` with a reason when a field does not apply.
Do not include secrets, raw transcripts, bulky telemetry, or local absolute paths.

## Summary

- Problem:
- Change:
- Why this approach:
- Intended outcome:
- Out of scope:
- Reviewer focus:
- Risk and rollback:

## Release boundary

Select the release standard before you list proof. Use `n.a.` with a reason only
when the change has no release-stage meaning.

- Release mode: Prototype / Portfolio / Product / Harness / n.a. because reason
- Completion condition:
- Deferred work:
- Stronger-proof condition:

<!--
Prototype: Prove that the idea has value. The core path works. List known gaps.
Portfolio: Make the work credible, coherent, navigable, and explainable.
Product: Make the work reusable and maintainable. Include tests, documentation,
versioning, a release path, and a supportable architecture.
Harness: Protect a trust boundary or repeatable proof. Include deterministic
checks, receipts, failure behavior, and evidence boundaries.

Name the condition that would require a more serious mode or additional proof.
-->

## Behavior proof

Complete this section when the PR changes observable behavior. For a change
with no behavior path, write `n.a.` and explain why.

- Before:
- After:
- Environment or operator path:
- Verification steps:
- Evidence after fix:
- Untested paths and limitations:

Behavior proof is separate from unit tests, lint, typecheck, and CI. Show the
production path or nearest meaningful operator path. If that path could not
run, state the blocker and the nearest fallback.

## Change details

- Plan IDs:
- Linear reference:
- Linked issue relationship:
- Completed work:
- Affected surfaces:
- Documentation impact:
- SemVer impact:
- Acceptance trace:
- Runtime impact:
- Deferred work:

<!-- Complete the following fields only when their admission conditions apply. -->
- Validation evidence:
- Review artifacts:
- Pattern scope inventory:
- Meta-behavior proof:
- Repeated-error research:
- Durable evidence map:
<!-- For evidence-heavy PRs, use a compact index. Use repo-relative paths.

| Artifact | Durable reference | Schema / version | Producer command | Digest | Replay command | Authority |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | `source-of-truth` / `retained context` |
-->
- Learning / reinforcement:

## Checklist

- [ ] I did not push directly to `main`; this PR is from a dedicated branch.
- [ ] Branch name follows policy (`codex/*` for agent-created branches).
- [ ] I ran the required validation for the changed surfaces and recorded every outcome below.
- [ ] **(Pending)** CodeRabbit review completed and findings handled or explicitly waived.
- [ ] **(Pending)** An independent reviewer performed the review outside the coding agent.
- [ ] **(Pending)** Codex review completed and findings handled or explicitly waived.
- [ ] Any CodeRabbit Semgrep findings were fixed or explicitly justified.
- [ ] Merge is blocked until all required checks pass.
- [ ] I will delete the branch and worktree after merge.

## Validation

- Regression coverage:
<!-- Add one evidence line for each command:
- Command: `bash scripts/validate-codestyle.sh` -> pass
- Command: `pnpm check` -> blocked (reason)
- Command: `bash scripts/run-harness-gate.sh tooling-audit --path . --json` -> n.a. (reason)
-->
- Untested or blocked paths:

## Review and closeout

- CodeRabbit:
- Independent reviewer evidence:
- Codex:
- CodeRabbit Semgrep:
- User-facing impact: yes, with changelog / no / n.a. because reason
- Remaining findings or waivers:
- Current blockers:
