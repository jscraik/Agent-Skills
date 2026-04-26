---
name: interview-me
description: Use this skill to analyze underspecified requests through a short interview and surface missing tradeoffs, assumptions, and approval gates before implementation when a prompt is underdefined and guessing would be risky.
metadata:
  skill-type: team_automation
---

# Interview Me

## When to use
- Use when requirements are underspecified and a decision-ready artifact is needed.
- Use to capture constraints, assumptions, and approval before heavy planning or implementation.

## Required inputs
- User intent and known constraints.
- Success metric or outcome target.
- Required tradeoff axis (time, quality, risk, release posture).
- Known unknowns that must remain explicit.

## Failure mode
- If request is already implementation-ready, recommend handoff to execution/plan skill instead of additional discovery.
- If the user declines follow-up questions, run with explicit assumptions and mark risk as open.

## Procedure
### 1) Start with one question
- Ask only one question with 3-5 clear choices and one recommended default.
- Keep momentum by choosing the choice that unlocks the next decision quickest.

### 2) Focused follow-up
- Ask the next question only when prior answers still block a meaningful decision.
- Map each answer to a visible decision and assumption entry.

### 3) Handoff
- Produce an approval-ready summary and stop at the decision gate.
- Keep route-critical guidance in this file and place expanded interview mechanics in `references/interview-playbook.md`.

## Deliverables
- A compact interview log with:
  - requested decisions,
  - assumptions,
  - constraints,
  - approval status.
- `schema_version` in output contract should be included when machine-readable outputs are requested.

## Validation
- Keep to one decision track per turn.
- Include schema-aware output structure (`schema_version`, decision id, status).
- Fail-fast on missing required inputs before implementation actions.
- Validation is fail-fast: if key inputs are missing, stop and ask exactly one follow-up question before proceeding.

## Anti-patterns
- Triggering implementation or plan steps before decision closure.
- Asking broad exploratory questions that do not reduce uncertainty.
- Ignoring unresolved risk when moving to execution.

## Examples
- "Can you inspect this draft and help me choose the right implementation scope before we proceed?"
- "I have a draft spec with gaps—ask me the three highest-impact questions before you proceed."
- "Please validate that we have enough assumptions captured before we move to execution."

## Philosophy
- Decisions first, implementation second.
- Keep interaction short, deterministic, and low cognitive load.
- Preserve explicit approval boundaries.

## Constraints
- Do not ask broad or leading questions that are not decision-relevant.
- Do not expose unsupported plan claims; ground outputs in confirmed inputs.
- Redact sensitive details by default.

## Variation
- Vary depth by context: keep the first pass to 1-2 highest-impact questions, then offer a focused add-on round only if assumptions remain unresolved.

## References
- Folded legacy modes: `references/folded-legacy-modes-core60.md`.
- Deep interview runbook and branch templates: `references/interview-playbook.md`.
- Include visual trace data from `assets/interview-me.png` when helpful for onboarding.

## Gotchas
- Symptom: Interview starts prescribing implementation before enough constraints exist.
  Cause: Discovery step was skipped.
  Do instead: Ask one high-impact decision question first, then confirm assumptions.
  Check: Summary includes confirmed constraints before any implementation recommendation.
- Symptom: Questions are too broad and stall the user.
  Cause: Prompt asks for open-ended brainstorming instead of a decision.
  Do instead: Ask 3-5 options with one recommended default.
  Check: User can answer in one short response and the next step is unblocked.
- Symptom: Scope drifts after follow-up questions.
  Cause: No scope restatement after new information.
  Do instead: Restate goal, constraints, and decision boundary after each pivot.
  Check: Deliverables still map directly to the original outcome target.
- Symptom: Approval boundary is implied but not explicit.
  Cause: Handoff omits decision status.
  Do instead: End with explicit approval state (`approved`, `needs-input`, or `declined`).
  Check: Output contract contains approval status before execution handoff.
- Symptom: Later answers silently override earlier decisions.
  Cause: Missing decision ledger.
  Do instead: Maintain a compact decision + assumption log and update entries intentionally.
  Check: Each recommendation traces to a visible decision record.

## See Also
| Skill | When to use |
|---|---|
| [[deep-interview]] | Deepen an existing draft doc or spec rather than running a lighter clarifying interview |
| [[architecture-interview]] | Structure a concrete architecture choice into a decision record |
| [[brainstorming]] | Explore multiple solution directions before narrowing into interview questions |
| [[he-plan]] | Turn the clarified outcome into an execution-ready implementation plan |

**Topic map:** [[product-strategy]]
