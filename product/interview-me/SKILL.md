---
name: interview-me
description: "Plan and review requirements with discovery/decision gating and approval. Use when requirements are unclear for a feature or refactor."
---

# interview-me (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Philosophy
- Default to clarity over speed: explicit decisions prevent rework.
- The interview exists to remove ambiguity, not to brainstorm.

## Anti-patterns
- Asking “nice to know” questions that don’t change scope.
- Skipping the approval gate after assumptions are captured.
- Letting the interview drift into brainstorming or implementation.
- Accepting vague goals without forcing a measurable success signal.
- Allowing scope changes without recording what was removed.
- Anti-pattern: treating interviews as validation instead of decision forcing.

## Variation
- Adapt question phrasing to the domain; do not reuse the same wording every time.
- Vary focus across scope, tradeoffs, and failure modes based on what is still unclear.

## Empowerment
- Present tradeoffs with defaults; let the user choose and own the scope.
- Offer a clear “stop and ship” option when scope is sufficient.
- Let the user pick the acceptance-criteria format and hold it fixed for the session.
- Empower the user to reject additional questions once the stop conditions are met.

## Default mode + intent

* Mode: `standard`
* Intent: start `DISCOVER`, switch to `DECIDE` when tradeoffs appear

## When to use

- Use when requirements are unclear for a new feature or refactor.
- Use when stakeholders disagree on scope or success criteria.
- Use when you need explicit tradeoffs before implementation.

## Example prompts

- "I want to add a new feature but I’m not sure what the scope should be."
- "We keep debating requirements — can you interview me first?"
- "Help me clarify success criteria for this refactor."

## Universal question spine (standard, 7 prompts)

Ask these in order, but skip any already answered by context.

1. **PAS: Amplify**

* “What’s the impact if we do nothing for 30 days?”

2. **Success signal**

* “What’s the success signal: metric, user-visible behavior, or both?”

3. **Done definition**

* “Pick acceptance criteria style: bullets vs Given/When/Then vs IO pairs.”

4. **Scope boundary**

* “What’s explicitly out-of-scope for this iteration?”

5. **Constraints**

* “Any hard constraints (compat, perf budget, security, deps)?”

6. **Edge / failure**

* “Name one failure mode we must handle well (or explicitly accept).”

7. **Tradeoff decision (DECIDE)**

* “Optimize for: speed-to-ship vs flexibility vs correctness?”

## Quick / Deep variants

* `:quick` uses questions 1–3 + 1 scope question
* `:deep` expands by adding:

  * data model invariants
  * observability
  * migration/rollback
  * testing strategy depth
  * security/privacy constraints

## Output

Use Kernel synthesis output verbatim.

---

## Optional patch to keep your ecosystem clean

If you keep `ask-questions-if-underspecified`, add this single escalation rule:

* If you need more than 5 questions → invoke the appropriate wrapper:

  * product-ish → `/pm-interview`
  * system design → `/architecture-interview`
  * failures → `/bug-interview`
  * otherwise → `/interview-me`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
