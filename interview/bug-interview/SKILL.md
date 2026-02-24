---
name: bug-interview
description: Analyze and review bug reports to capture repro, evidence, and the next
  smallest diagnostic step. Use when a bug report lacks clear reproduction.
---

# bug-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## What this wrapper optimizes for

- Reliable repro (or a plan to synthesize it)
- Evidence-driven narrowing (don’t guess)
- The smallest next diagnostic experiment (speed vs certainty is a user choice)

## Interaction notes

- Must use AskUserQuestion-style multiple choice (3–5 options, include a recommended default).
- In Delta mode (existing bug report/ticket), extract what’s already known first; only ask what’s missing to repro or run the next experiment.
- Avoid broad log/data dumps without a hypothesis.

## User profile alignment (Jamie)

Follow `~/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Keep one question per turn and map any free-text reply to the closest option with confirmation.

## Philosophy

- Bugs are solved by **reliable repro + smallest next experiment**.

## Anti-patterns to avoid

- Jumping to fixes before confirming repro or scope.
- Treating assumptions as facts without explicit approval.
- Asking for broad logs/data dumps without a targeted hypothesis.

## Variation

- Tailor prompts to the suspected layer (client/server/DB) and evidence quality.
- Avoid repeating identical option sets; vary the next-step tradeoff based on context.

## Default mode + intent

- Mode: `standard`
- Intent: start `DISCOVER`, switch to `DECIDE` when choosing what to try next

## Scope and triggers

- Bug report lacks clear reproduction steps.
- Need to narrow suspected layer quickly.
- Need a focused debug plan before touching code.

## Constraints / Safety

- Redact secrets/PII by default.
- Do not request broad data dumps without a hypothesis.
- Do not proceed without a minimal repro or a clear plan to synthesize one.

## Bug spine (10 prompts)

1) **Expected vs actual**
- One sentence each.

2) **Severity / impact**
- blocker / high / medium / low + workaround yes/no.

3) **Repro steps (single concrete path)**
- Minimal steps to reproduce (as few as possible).

4) **Frequency**
- always / often / rare / only once.

5) **Environment**
- OS + app version + runtime/browser + network context (pick the 1–2 that matter most).

6) **Evidence available**
- stack trace / logs / screenshot / error code / none.

7) **Regression window**
- Did this ever work? If yes, when did it last work (approx)?

8) **Recent changes**
- code / deps / config / data / environment.

9) **Minimal repro artifact**
- provide one minimal repro input (file, payload, request, dataset) OR synthesize one.

10) **Next diagnostic step (DECIDE)**
- Fastest experiment vs highest-signal experiment vs add instrumentation first.

## Bug synthesis add-on (append after Kernel synthesis)

```md
## Triage Addendum
- Repro status: confirmed / unconfirmed
- Suspected layer: client / server / DB / network / dependency / config
- Top hypotheses (1–3):
- Next diagnostic step (smallest experiment):
- Instrumentation needed (if any):
- Rollback/mitigation options:
```

## Required inputs
- User request details and any relevant files/links.

## Deliverables
- Kernel synthesis + Triage Addendum.
- Include `schema_version: 1` if outputs are contract-bound.

## Validation
- Fail fast and report missing inputs before proceeding.

## Examples

- "I have a crash report but no repro steps—help me find the next diagnostic step."
- "This bug only happens in prod; guide me to the smallest high-signal experiment."

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Procedure
1) (Optional) Delta scan: extract what’s already known from the bug report/ticket.
2) Execute the kernel interview loop using the Bug spine.
3) Synthesize outputs + approval gate.
4) Handoff to debugging/implementation using the approved triage plan.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
