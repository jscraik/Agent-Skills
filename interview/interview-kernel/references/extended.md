# Extended guidance

## “Idea Legos” fallback (when you’re stuck)

Pick exactly **one** and ask a single question:

- **Example**: “Give one concrete example (input → output).”
- **Counterexample**: “Name one case this must NOT affect.”
- **Metric**: “What signal proves success?”
- **Reframe**: “Is this mainly UX vs correctness vs performance?”

---

## Interview loop (kernel algorithm)

1) Initialize Interview Log with blanks.
2) Read any provided materials (discovery-only), pre-fill the log.
3) Ask the next spine question (wrapper-provided) that passes the validity gate.
4) Record answer → update Interview Log → write “Captured answer”.
5) Check stop conditions:
   - If satisfied or budget exhausted → synthesize.
   - Else continue.

---

## Stop conditions

Stop and synthesize when you have:

- PAS snapshot (Problem/Impact/Success)
- Acceptance criteria format chosen + at least 3 criteria drafted
- Scope in/out
- Constraints
- Key edge cases / failure modes
- Integration points
- At least one explicit decision if tradeoffs exist
- Any assumptions clearly listed

Or when you hit question budget.

---

## Kernel synthesis output (standardized)

Wrappers can add extra sections, but the kernel always outputs:

### A) One-sentence pitch

“We are building **<X>** so that **<Y>** for **<Z>**, measured by **<metric>**.”

### B) Pyramid summary (answer-first)

1) Main decision (1 sentence)
2) 3 key reasons / drivers
3) Evidence/examples (scenarios, IO pairs, repro steps, constraints)

### C) Scope + non-goals

### D) Acceptance criteria (choose one)

- Bullet ACs, or
- Given/When/Then scenarios, or
- IO pairs

### E) Decisions table (required if any tradeoff exists)

```md
| Decision | Chosen | Alternatives | Sacrificed |
|---|---|---|---|
| | | | |
```

### F) Assumptions register (required if any assumption exists)

```md
| Assumption | Risk if wrong | How we’ll detect |
|---|---|---|
| | | |
```

### G) Risks / rollout / rollback / observability

### H) Open questions

### I) Next step (single action)

One concrete action that moves the work forward (e.g., “Run planning mode on this spec”, “Confirm option B with stakeholder X”, “Collect a repro artifact”).

### Approval gate (must end with)
“Reply `approve` to proceed, or say what to change. If assumptions exist, reply `approve assumptions` or correct them.”

## Operational notes
See `references/operations.md` for file update rules and defaults profile behavior.

## Core requirements
Required inputs: wrapper-provided request details + relevant source material. Deliverables: interview log + kernel synthesis + explicit approval gate (`approve` / `approve assumptions`). Constraints/validation: one question per turn, no implementation, explicit assumptions, and fail-fast gating. References: `references/contract.yaml`, `references/evals.yaml`.

## Procedure
1) Initialize Interview Log and read any provided source material.
2) Run the strict interview loop (DISCOVER ↔ DECIDE) within the question budget.
3) Produce kernel synthesis output.
4) Require explicit approval before any implementation/planning begins.

## Antipatterns
- Drifting into implementation or planning that depends on unknowns
- Asking obvious/inferable questions instead of reading the source material
- Proceeding without approval when assumptions exist

## Examples
See `references/examples.md`.

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
