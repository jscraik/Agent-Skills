---
name: interview-kernel
description: "Core interview engine enforcing single-question discovery/decision gating. Use when building interview wrapper skills."
---

# Interview Kernel

A reusable “engine” for interviews. Wrappers (PM / Architecture / Bug / Refactor) provide only the domain spine; the kernel enforces consistent behavior and outputs.

## Philosophy (why this exists)

- Interviews fail when they drift. This kernel enforces discipline: one question, one decision, one recorded answer.
- The fastest path to shipping is narrow scope + explicit tradeoffs, not more features or vague intent.

## When to use

- Use as a shared kernel for any interview wrapper skill.
- Use when you need strict single-question interviewing with approval gating.
- Use when assumptions and tradeoffs must be made explicit before work begins.

## Anti-patterns (do not do)

- Asking soft or confirmatory questions that do not eliminate branches.
- Mixing discovery and implementation in the same turn.
- Proceeding without explicit approval when assumptions exist.

## Variation (avoid template lock-in)

- Vary question focus across scope, tradeoffs, and failure modes based on the wrapper’s intent.
- Prefer context-specific wording over generic templates.

## Empowerment (for the user)

- The user controls scope, tradeoffs, and approval. The kernel surfaces options, never assumes.

## Kernel contract

### What the kernel guarantees

* One question at a time (strict).
* Continuous externalized state. (Interview Log)
* Question quality gating (only high-leverage questions).
* Explicit decision forcing (tradeoffs must be chosen, not implied).
* Assumptions are first-class and must be approved.
* Standard synthesis format + approval gate before any work.

### What wrappers must provide

Wrappers MUST define:

* **Mode default**: `quick | standard | deep`
* **Interview intent**: `DISCOVER | DECIDE` starting intent
* **Question spine**: ordered list of question goals (domain-specific)
* **Domain additions**: extra log fields and required synthesis blocks

Wrappers MUST NOT rewrite kernel rules.

---

## Operating rules (non-negotiable)

1. **Single question only.**
2. **No implementation.** No code edits, no refactors, no “final plan” that depends on unknowns.
3. Allowed: **read-only discovery** (skim provided docs/configs) if it doesn’t commit to a direction.
4. After every answer: update the **Interview Log** + add a one-line **Captured answer**.
5. **Question budget**

   * `:quick` 3–5
   * `:standard` 5–10
   * `:deep` 15–20
6. **Approval gate**

   * Do not proceed until user explicitly approves:

     * `approve` (spec + decisions accepted)
     * or `approve assumptions` (assumptions accepted explicitly)
     * otherwise revise.

---

## State model

Maintain this block and keep it current:

```md
## Interview Log

### 1) PAS Snapshot
- Problem (observable):
- Amplify (impact if unsolved):
- Success (what “good” looks like; not implementation):

### 2) Goal / Success
- Primary goal:
- Success metric / signal:
- Acceptance criteria (draft):

### 3) Scope
- In:
- Out / non-goals:

### 4) Constraints
- Hard constraints:
- Preferences:

### 5) Edge cases / failure modes
- List:

### 6) Integration / dependencies
- Touchpoints:
- Compatibility targets:

### 7) Decisions
- Decisions made so far:

### 8) Assumptions
- Assumptions stated so far:

### 9) Risks / rollout / observability
- Risks:
- Rollout/rollback:
- Observability/alerts/logs:

### 10) Open questions
- [ ] ...
```

### Display mode (UX)

Default to **compact** output to keep the interview usable with minimal cognitive load:

- Keep the **full Interview Log** as the source of truth.
- In normal turns, show a **compact log view**: only sections that changed this turn and any still-blocking blanks (1–2 lines each).
- If the user replies `log` or asks to see state, render the **full Interview Log** block verbatim.

Always include a lightweight progress header:

`Progress: <mode> Q<n>/<budget> · Intent: DISCOVER|DECIDE`

(Progress is informational; do not ask extra questions about it.)

Also maintain a running “Captured answer” line after each response:

```md
Captured answer: <1–2 lines, concrete, no fluff>
```

---

## Interview intent switch (DISCOVER vs DECIDE)

Set and track the current intent:

* **DISCOVER**: gather missing facts

  * Question types: “what is / what happens / give one example”
* **DECIDE**: force explicit choices where multiple viable paths exist

  * Question types: multiple-choice tradeoffs, scope boundaries, acceptance criteria format

**Rule:** If multiple plausible implementations remain, switch to **DECIDE** until a path is chosen.

---

## Question validity gate (quality control)

A question is valid only if it does at least one:

* Eliminates a major interpretation branch
* Defines a boundary (in/out, yes/no, must/must-not)
* Forces a tradeoff (what you’re sacrificing)
* Produces testable acceptance criteria
* Identifies an invariant / failure mode / rollback concern

If a candidate question does none of these, do not ask it.

---

## Question format (every question must look like this)

```text
Question: <one thing>

Options (3–5 max):
a) ... — when to pick this
b) ... — when to pick this
c) ... — when to pick this
d) Not sure — use default (record as an assumption if it affects scope)

Default: a)
Reply: a / b / c / d (or "default")
```

If free-text is required (rare), constrain it:

* “Give ONE example…”
* “Name ONE case where it must NOT…”

---

## “Idea Legos” fallback (when you’re stuck)

Pick exactly **one** and ask a single question:

* **Example**: “Give one concrete example (input → output).”
* **Counterexample**: “Name one case this must NOT affect.”
* **Metric**: “What signal proves success?”
* **Reframe**: “Is this mainly UX vs correctness vs performance?”

---

## Interview loop (kernel algorithm)

1. Initialize Interview Log with blanks.
2. Ask the next spine question (wrapper-provided) that passes validity gate.
3. Record answer → update Interview Log → write “Captured answer”.
4. Check stop conditions:

   * If satisfied or budget exhausted → synthesize.
   * Else continue.

---

## Stop conditions

Stop and synthesize when you have:

* PAS snapshot (Problem/Impact/Success)
* Acceptance criteria format chosen + at least 3 criteria drafted
* Scope in/out
* Constraints
* Key edge cases / failure modes
* Integration points
* At least one explicit decision if tradeoffs exist
* Any assumptions clearly listed

Or when you hit question budget.

---

## Kernel synthesis output (standardized)

Wrappers can add extra sections, but the kernel always outputs:

### A) One-sentence pitch

“We are building **<X>** so that **<Y>** for **<Z>**, measured by **<metric>**.”

### B) Pyramid summary (answer-first)

1. Main decision (1 sentence)
2. 3 key reasons / drivers
3. Evidence/examples (scenarios, IO pairs, repro steps, constraints)

### C) Scope + non-goals

### D) Acceptance criteria (choose one)

* Bullet ACs, or
* Given/When/Then scenarios, or
* IO pairs

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

### Approval gate (must end with)

“Reply `approve` to proceed, or say what to change. If assumptions exist, reply `approve assumptions` or correct them.”

---

## Optional: Defaults Profile hook (strongly recommended)

If `@DEFAULTS.md` exists, treat it as default answers for:

* scope bias (minimal vs refactor)
* correctness vs speed
* testing expectations
* compatibility targets
* rollout posture

Only ask about these if the current task conflicts with defaults.

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
