# QA Intake Routing

Use this reference when a user reports bugs, starts a QA session, wants conversational issue intake, or asks to turn feedback into Linear issues. The Harness Engineering adaptation is Linear-first: do not create GitHub issues or ADRs from this workflow unless the user explicitly overrides the repo convention.

## Core Loop

1. Listen to the report in the user's words.
2. Ask at most 2-3 short clarifying questions focused only on expected behavior, actual behavior, reproduction steps, and whether the failure is consistent or intermittent.
3. Explore the repo lightly for domain language and behavior boundaries. The goal is context for durable issue wording, not a fix.
4. Read `CONTEXT-MAP.md` or `CONTEXT.md` when project terms shape the report, and prefer canonical terms in the Linear issue.
5. Decide whether the report is one Linear issue or several thin issues.
6. File Linear issue(s) in dependency order. If Linear creation is blocked, stop with `linear_status: linear_blocked`, exact missing fields, and the ready-to-create issue payload; do not treat the payload as equivalent to a filed issue.
7. Ask: "Next issue, or are we done?"

## Single Issue vs Breakdown

Keep one Linear issue when the report describes one wrong behavior in one user-facing area, even if several symptoms come from the same behavior.

Break down into multiple Linear issues when:

- the report spans independent areas that can be fixed separately;
- symptoms have different failure modes or verification steps;
- different agents or engineers could work in parallel;
- one issue genuinely blocks testing another.

Create blockers first so later Linear issues can reference real issue IDs. If blocker creation is blocked, return the ordered ready-to-create payloads and missing metadata instead of creating downstream placeholder links. Mark independent issues as "None - can start immediately" rather than inventing dependencies.

## Linear Issue Template

```md
## What happened
[Plain-language actual behavior from the user's perspective.]

## What I expected
[Expected behavior in project domain terms.]

## Steps to reproduce
1. [Concrete user action or command.]
2. [Relevant input, configuration, role, state, or environment.]
3. [Observed result.]

## Blocked by
[Linear issue ID or "None - can start immediately".]

## Additional context
[Useful observations from the user or light repo exploration, phrased as behavior. Do not include file paths or line numbers.]
```

## Rules

- Use Linear issues or comments for durable tracker state.
- Do not cite file paths, line numbers, function names, or internal module details in issue bodies.
- Describe behavior, not implementation.
- Reproduction steps are mandatory; ask if they are missing.
- Keep each issue readable in about 30 seconds.
- If expected behavior is unclear, route to `he-brainstorm` or `he-spec` before filing an implementation issue; once the ambiguity is resolved, the Linear tracker gate is still mandatory before handoff.
- If the Linear app is disconnected or team/project/priority metadata is missing, stop with `linear_status: linear_blocked` and a complete issue payload.
- If the issue is already filed and ready for diagnosis, route to `he-fix-bugs`.
- If multiple Linear issues need sequencing, route to `he-plan`.
- If a repro should become a failing test first, route to `he-work` with `test-first` posture.
