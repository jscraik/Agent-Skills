---
name: interview-kernel
description: "Core interview engine enforcing strict discovery/decision gating with externalized state, decisions, assumptions, and an approval gate. Use when building interview wrapper skills."
metadata:
  short-description: "Core interview engine for wrapper skills."
---

# Interview Kernel (v2)

A reusable “engine” for interviews. Wrappers (PM / Architecture / Bug / Deepen) provide only the domain spine; the kernel enforces consistent behavior, low drift, and a reliable output artifact.

## Philosophy (why this exists)

- **Interview first → spec second → execute last.** Interviews are a precursor to planning/execution, not a substitute. The goal is to decide cheaply before spending tokens/time implementing.
- **Slow down to speed up.** The interview narrows the solution space early so you don’t rework a pile of wrong assumptions later.
- Interviews fail when they drift. This kernel enforces discipline: **one decision at a time**, written down immediately.
- The fastest path to shipping is narrow scope + explicit tradeoffs, not more features or vague intent.

## Spec-driven workflow (recommended)

1) Interview to surface unknowns and force tradeoffs.
2) Produce/update a **spec artifact** (Decisions + Assumptions + Acceptance Criteria).
3) Only after approval, start a new implementation/planning phase (or a new agent session) using that spec as the source of truth.

## When to use

- Use as a shared kernel for any interview wrapper skill.
- Use when you need strict interviewing with approval gating.
- Use when assumptions and tradeoffs must be made explicit before work begins.
- Use when the user’s working memory is limited and you must keep interaction **single-threaded**.

## Anti-patterns (do not do)

- Asking soft or confirmatory questions that do not eliminate branches.
- Mixing discovery and implementation in the same turn.
- Proceeding without explicit approval when assumptions exist.
- Asking questions you can answer by quickly reading the provided source material (docs, config, code).

## Variation (avoid template lock-in)

- Vary question focus across scope, tradeoffs, and failure modes based on the wrapper’s intent.
- Prefer context-specific wording over generic templates.

## Empowerment (for the user)

- The user controls scope, tradeoffs, and approval. The kernel surfaces options, never assumes.
- Always include a safe escape hatch: **“Not sure — you decide”** (record as an assumption if it changes scope).

## User profile alignment (Jamie)

The interview must match `/Users/jamiecraik/.codex/USER_PROFILE.md`:

- Single-threaded, explicit, low cognitive load.
- Always use **multiple-choice** questions (3–5 options) with a clear recommended default.
- Prefer AskUserQuestion UI; otherwise use `a/b/c` options.
- If the user replies in free text, map to the closest option and confirm next turn.

## Kernel contract

### What the kernel guarantees

- Default: **one question at a time** (strict, low cognitive load).
- Continuous externalized state (**Interview Log**).
- Question quality gating (only high-leverage questions).
- Explicit decision forcing (tradeoffs must be chosen, not implied).
- Assumptions are first-class and must be approved.
- Standard synthesis format + approval gate before any work.

### What wrappers must provide

Wrappers MUST define:

- **Mode default**: `quick | standard | deep`
- **Interview intent**: `DISCOVER | DECIDE` starting intent
- **Question spine**: ordered list of question goals (domain-specific)
- **Domain additions**: extra log fields and required synthesis blocks

Wrappers MUST NOT rewrite kernel rules.

---

## Operating rules (non-negotiable)

1) **One question per turn.**
   - Optional override: if the user explicitly says `batch`, you may ask up to **3** questions in one AskUserQuestion call *for that turn only* and provide a reply key (e.g. `1a 2b 3c`). Default remains single-question.
2) **No implementation.** No code edits, no refactors, no “final plan” that depends on unknowns.
3) Allowed: **read-only discovery** (skim provided docs/configs/files) if it doesn’t commit to a direction.
4) After every answer: update the **Interview Log** + add a one-line **Captured answer**.
5) **Question budget**
   - `:quick` 3–5
   - `:standard` 5–10
   - `:deep` 15–20
6) **Approval gate**
   - Do not proceed until user explicitly approves:
     - `approve` (spec + decisions accepted)
     - or `approve assumptions` (assumptions accepted explicitly)
     - otherwise revise.

---

## Input handling (topic vs file vs existing spec)

Wrappers should pass through any source material. The kernel behavior should be:

- If the user provides a **file path** or a spec doc:
  - Read it first (discovery-only).
  - Pre-fill the Interview Log from what’s already stated.
  - Ask only about **gaps, contradictions, and risky assumptions**.
  - When done, update the doc by appending a clearly labeled section (see “File update rules”).
- If the user provides a **topic/idea**:
  - Start fresh, build the log from blanks.

### Delta / enhancement mode

If you detect existing decisions/spec text, switch to **delta mode**:

- Do **not** re-ask settled decisions.
- Ask only what is missing to make the artifact execution-ready:
  - scope boundaries
  - acceptance criteria
  - failure modes
  - constraints
  - integration points
  - rollout/rollback/observability

---

## State model

Maintain this block and keep it current:

```md
## Interview Log

### 0) Source material
- Inputs reviewed:
- Notes/constraints extracted:

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

Also maintain a running “Captured answer” line after each response:

```md
Captured answer: <1–2 lines, concrete, no fluff>
```

---

## What to ask next (prioritization rubric)

Pick the next question that best maximizes:

- **Impact**: changes architecture/UX/cost meaningfully
- **Irreversibility**: expensive to undo later
- **Uncertainty**: currently unknown or contradictory
- **Risk**: security, data loss, outages, runaway cost, compliance

If something can be answered by quick discovery (reading configs/spec), do that first.

---

## Interview intent switch (DISCOVER vs DECIDE)

Set and track the current intent:

- **DISCOVER**: gather missing facts  
  - Question types: “what is / what happens / give one example”
- **DECIDE**: force explicit choices where multiple viable paths exist  
  - Question types: multiple-choice tradeoffs, scope boundaries, acceptance criteria format

**Rule:** If multiple plausible implementations remain, switch to **DECIDE** until a path is chosen.

---

## Question validity gate (quality control)

A question is valid only if it does at least one:

- Eliminates a major interpretation branch
- Defines a boundary (in/out, must/must-not)
- Forces a tradeoff (what you’re sacrificing)
- Produces testable acceptance criteria
- Identifies an invariant / failure mode / rollback concern

Additionally, reject questions that are:

- Obvious (“Do you want tests?”)
- Inferable from the codebase/spec (“What language?” when it’s TypeScript)
- Pure validation (“Is this correct?”) unless it unblocks a high-risk path

---

## Question format (preferred: AskUserQuestion tool)

If the environment supports an AskUserQuestion-style UI, use it.

```yaml
AskUserQuestion:
  questions:
    - header: "<Category>"
      question: "<One thing>"
      options:
        - label: "<Option A> (Recommended)"
          description: "<When to pick this>"
        - label: "<Option B>"
          description: "<When to pick this>"
        - label: "<Option C>"
          description: "<When to pick this>"
        - label: "Not sure — you decide"
          description: "Let the assistant choose based on patterns; record as an assumption if it affects scope"
      multiSelect: false
Reply format: a / b / c / d (or "default")
```

### Fallback (plain text)

If AskUserQuestion UI is not available, use:

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

- “Give ONE example…”
- “Name ONE case where it must NOT…”

---

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

---

## File update rules (when a wrapper targets a document)

When updating a document in-place:

- Preserve the original structure.
- Prefer **append** over rewrite.
- Add one clearly labeled section:
  - `## Interview Insights` (fresh mode), or
  - `## Delta Insights` (enhancement mode)
- Never inject prose into code files by default; write to a sidecar doc instead.

---

## Optional: Defaults Profile hook (recommended)

If `@DEFAULTS.md` or a user profile exists, treat it as default answers for:

- scope bias (minimal vs refactor)
- correctness vs speed
- testing expectations
- compatibility targets
- rollout posture

Only ask about these if the current task conflicts with defaults.

## Remember

These guidelines prevent drift and make the work finishable.
---

## Inputs
- Wrapper-provided user request details
- Any relevant files/links/source material

## Outputs
- A structured interview log (state) maintained throughout
- Kernel synthesis output (pitch, scope, ACs, decisions, assumptions, risks, open questions)
- Approval gate (`approve` / `approve assumptions`)
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Default to low cognitive load: one question per turn.
- Prefer discovery over assumptions; record assumptions explicitly when unavoidable.
- No implementation/code changes during interview.
- Redact secrets/PII by default.
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md.

## Validation

- Fail fast: stop at the first failed gate and correct before proceeding.
- Confirm Interview Log is maintained and approvals are explicit.
- Confirm assumptions are listed before approval.

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

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

- "Build a concise interview spine for a payments refactor decision."
- "Use the kernel to interview for a migration plan before any code changes."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
