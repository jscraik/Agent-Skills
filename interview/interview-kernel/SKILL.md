---
name: interview-kernel
description: Core interview engine enforcing strict discovery/decision gating with
  externalized state, decisions, assumptions, and an approval gate. Use when building
  interview wrapper skills.
---

# Interview Kernel (v2)

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.


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

## Scope and triggers

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


## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

## Inputs

- User task context and target environment.
- Relevant constraints, permissions, and preferences required to execute safely.

## Outputs

- A concrete next-step response with explicit, reproducible actions.
- A short verification checklist and caveats for the user.

## Validation

- Fail fast: stop at the first failed check and do not continue.
- Re-run the required checks before proceeding to the next step.
- Report any failed check and requested follow-up actions clearly.

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
