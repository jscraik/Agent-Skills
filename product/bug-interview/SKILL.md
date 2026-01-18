---
name: bug-interview
description: "Analyze and review bug reports to capture repro, evidence, and next diagnostic step. Use when a bug report lacks clear reproduction."
---

# bug-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Philosophy
- Bugs are solved by reliable repro + smallest next experiment.

## Anti-patterns to avoid
- Avoid jumping to fixes before confirming repro or scope.
- Avoid treating assumptions as facts without explicit approval.
- Avoid asking for broad logs or data dumps without a targeted hypothesis.

## Variation
- Vary questions by failure type (perf, crash, data loss, UX).

## Empowerment
- Let the user choose diagnostic tradeoffs (speed vs certainty).

## Default mode + intent

* Mode: `standard`
* Intent: start `DISCOVER` (bugs are information-heavy), switch to `DECIDE` when choosing what to try next

## When to use

- Use when a bug report lacks clear reproduction steps.
- Use when you need to narrow the suspected layer quickly.
- Use when you must choose the smallest diagnostic experiment.

## Constraints / Safety
- Redact secrets/PII by default.

- Do not request broad data dumps without a hypothesis.
- Do not proceed without a minimal repro or a clear plan to synthesize one.

## Example prompts

- "The app crashes sometimes — help me diagnose it."
- "Users report errors but we can’t reproduce."
- "I need a focused debug plan before touching code."

## Bug spine (9 prompts)

1. **Expected vs actual**

* “What did you expect, and what actually happened? (One sentence each.)”

2. **Repro steps (single concrete path)**

* “Give the exact minimal steps to reproduce (as few steps as possible).”

3. **Frequency**

* “How often: always / often / rare / only once?”

4. **Environment**

* “Where: OS + app version + runtime/browser + network context (pick the 1–2 that matter most).”

5. **Error evidence**

* “What evidence do we have: stack trace / logs / screenshot / error code / none?”

6. **Regression window**

* “Did this ever work? If yes, when did it last work (approx)?”

7. **Recent changes**

* “What changed near the start: code / deps / config / data / environment?”

8. **Minimal repro artifact**

* “Can you provide one minimal repro input (file, payload, request, dataset) or should we synthesize one?”

9. **Impact + workaround**

* “Severity: blocker / high / medium / low — and is there a workaround?”

## Bug synthesis add-on (append after Kernel synthesis)

```md
## Triage Addendum
- Repro status: confirmed / unconfirmed
- Suspected layer: client / server / DB / network / dependency / config
- Top hypotheses (1–3):
- Next diagnostic step (smallest experiment):
- Rollback/mitigation options:
```

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
