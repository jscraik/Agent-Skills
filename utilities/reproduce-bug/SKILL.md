---
name: reproduce-bug
description: Reproduce or investigate a bug from a Linear issue or GitHub issue, preserving tracker context, symptoms, and repro steps. Use when the user wants issue-driven debugging rather than a freeform root-cause review.
metadata:
  skill-type: product_verification
---

# Reproduce Bug

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Tracker intake](#tracker-intake)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Gotchas](#gotchas)

## Standards snapshot
- Route tracker-driven bug reproduction and investigation here.
- Prefer Linear as the default issue source in this repo.
- Keep GitHub issue intake supported because some bug reports still arrive there.
- Reproduce before theorizing about fixes.
- Preserve richer upstream issue-driven doctrine in references instead of compressing it away.

## When to use
- The user provides a Linear issue or GitHub issue and wants the bug reproduced.
- The user wants an investigation report tied back to a tracker issue.
- The team needs verified reproduction steps, evidence, and a root-cause hypothesis before fixing.
- A bug report needs structured follow-up after reproduction, including optional tracker updates.

## When not to use
- Generic debugging with no tracker context; use `systematic-debugging` instead.
- Issue triage or tracker field updates with no reproduction work; use `linear` or `gh-workflow`.
- Direct implementation of a known fix when reproduction is already complete.

## Required inputs
- A tracker issue reference:
  - Linear issue ID or URL, preferred
  - GitHub issue number or URL, still supported
- If no tracker issue exists, at least observable symptoms plus enough context to create a manual reproduction plan.
- Environment hints when known:
  - route or feature area
  - browser or OS
  - data conditions
  - frequency or intermittence

## Deliverables
- A chosen issue source: `linear | github | manual-context`.
- Confirmed or attempted reproduction steps.
- Evidence gathered during reproduction and investigation.
- A ranked root-cause hypothesis summary.
- A suggested next action:
  - post findings to Linear
  - post findings to GitHub
  - start working on a fix
  - continue investigation

## Failure mode
- If the tracker issue cannot be resolved, stop and ask for the smallest missing identifier.
- If the report is too vague to reproduce, stop after documenting the missing conditions and investigation gaps.
- If the task is really issue management or generic debugging rather than reproduction, route to `linear`, `gh-workflow`, or `systematic-debugging`.

## Output contract
Use this shape when the user asks for structured output:

```json
{
  "schema_version": 1,
  "issue_source": "linear|github|manual-context",
  "issue_ref": "string|null",
  "reproduction_status": "confirmed|not_reproduced|blocked|partial",
  "root_cause_summary": "string|null",
  "evidence": ["string"],
  "next_step": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Use `issue_ref: null` only for manual-context mode.
- Keep `evidence` concise and path-oriented when possible.

## Tracker intake
- Prefer Linear issue intake first in this repo. Use the `linear` skill or Linear MCP reads to fetch the issue ID, description, comments, link attachments, and linked context when a Linear identifier or URL is provided.
- Keep GitHub issue intake fully supported. Use `gh`-based intake or `gh-workflow` context when a GitHub issue number or URL is provided.
- If the user gives only a prose bug report, treat it as `manual-context` mode and say that tracker-linked follow-up can be added later.
- Use `references/tracker-intake-and-reporting.md` for the preserved upstream issue-driven workflow, adapted to Linear-first intake with GitHub parity.

## Workflow
1. Resolve the issue source: Linear, GitHub, or manual context.
2. Read the issue before touching code or the browser:
   - symptoms
   - expected behavior
   - reproduction steps
   - environment clues
   - comments or follow-up discussion
3. Search the repo for likely code paths and form 2-3 ranked hypotheses.
4. Choose the narrowest reproduction route:
   - test-based reproduction for logic, backend, or data bugs
   - browser-based reproduction for UI or interaction bugs
   - manual or environment-specific reproduction when automation is not realistic
5. Capture evidence when the bug reproduces:
   - screenshots
   - failing tests
   - logs
   - console errors
6. Investigate the likely root cause and document where behavior diverges from expectation.
7. Present findings before any external mutation.
8. If the user wants tracker follow-up, prefer posting findings to Linear in this repo, while still offering GitHub issue comments when that is the actual source or the requested destination.

## Validation
- Verify the issue source is resolved before investigation begins.
- Verify reproduction status is stated explicitly as confirmed, not reproduced, blocked, or partial.
- Verify evidence is attached to the claimed hypothesis.
- Verify no tracker comment is posted without explicit user direction.
- Verify GitHub support remains available even though Linear is the preferred intake path.

## Constraints
- Redact secrets, tokens, credentials, and personal data from evidence.
- Do not claim reproduction success without concrete evidence.
- Do not post to Linear or GitHub automatically.
- Do not treat issue comments as truth without verifying them against the codebase or runtime behavior.

## Anti-patterns
- Jumping to fixes before reproduction.
- Treating GitHub-only assumptions as canonical in a Linear-first repo.
- Posting speculative findings back to a tracker.
- Stretching this skill into generic issue triage or code fixing.

## Examples
- "Reproduce the bug in Linear issue ENG-123 and tell me what is actually happening."
- "Investigate GitHub issue #482 and verify whether the reported crash still reproduces."
- "I have a bug report in Linear with screenshots and comments; can you turn it into confirmed repro steps?"
- "Use this issue thread to reproduce the UI bug before we touch the code."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/tracker-intake-and-reporting.md`

## Gotchas
- Symptom: Investigation starts from code guesses instead of the report.
  Cause: Tracker intake was skipped.
  Do instead: Read the issue and extract the symptom, expectation, repro steps, and environment clues first.
  Check: Issue-source summary exists before hypothesis work begins.
- Symptom: Tracker follow-up path assumes GitHub only.
  Cause: Upstream workflow was imported without adapting the local issue system.
  Do instead: Prefer Linear updates in this repo, but keep GitHub comment flow available.
  Check: Final next-step options mention the right tracker destination.

## See Also

| Skill | When to use together |
|---|---|
| [[systematic-debugging]] | Move from reproduction evidence into a deeper root-cause analysis |
| [[test-browser]] | Reproduce or verify browser-facing regressions with route-level evidence |
| [[gh-workflow]] | Follow up on GitHub issues or PR state after the bug is understood |

**Topic map:** [[agent-ops]]
