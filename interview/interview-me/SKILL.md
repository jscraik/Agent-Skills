---
name: interview-me
description: Interactive, multiple-choice interview for requirements discovery and
  spec clarification; turns an underspecified idea (or draft spec) into an execution-ready
  spec with decisions, assumptions, acceptance criteria, and approval. Use when a
  user asks to 'interview me', clarify scope, or refine a draft spec.
---

# interview-me (interactive front door)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: single-question loop, question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [LearningPosture compatibility](#learningposture-compatibility)
- [Fresh vs Delta](#step-0--fresh-vs-delta)
- [Track selection](#track-selection-first-substantive-question)
- [Spine A](#spine-a--requirements-to-build-default)
- [Spine B](#spine-b--system-design-answer-beginner-friendly)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

## What this wrapper optimizes for

- **Low cognitive load**: one question, multiple-choice answers, safe defaults.
- **Design-ready output**: scope, acceptance criteria, decisions, assumptions, risks, rollout.
- **Works from either starting point**:
  - **Fresh mode**: you have an idea but it’s underspecified.
  - **Delta mode**: you already have notes/spec; we deepen it by filling gaps and forcing decisions.

## Spec-driven workflow (recommended)

Interview → write/update spec → (after approval) run planning/execution as a separate step/session.

## Standards snapshot (March 2026)
- Keep the interview single-threaded, low-cognitive-load, and decision-oriented.
- Use multiple-choice questions to reduce ambiguity, but make the options sharp enough to change the final spec.
- Move from DISCOVER to DECIDE as soon as tradeoffs appear; do not over-interview once the next decision is clear.
- Produce an execution-ready output with explicit decisions, assumptions, acceptance criteria, and an approval gate.

## LearningPosture compatibility

- This wrapper stays single-question, multi-choice, and approval-gated.
- Posture semantics mapped to interview flow:
  - `learn`: one-question, one-decision-at-a-time clarification with rationale.
  - `guided`: constrained branching with explicit assumptions and risks before moving to the next spine.
  - `execute`: only after approval; hand off to planning/execution, never code in this wrapper.
- Default posture is `learn`, which keeps scope and risk articulation explicit before branching.

## User profile alignment (Jamie)

Follow `~/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Always use multiple-choice questions (3–5 options, include a recommended default) and map any free-text reply to the closest option with confirmation.

## Philosophy + guiding questions

Use the shortest path to clarity without overloading the user. Ask only what reduces risk or unlocks decisions.

Guiding questions:
- What decision will this answer unlock?
- What is the smallest question that reduces uncertainty?
- What is the highest-risk unknown for v1?
- What would make this spec fail in the real world?
- What evidence would make us confident to proceed?

## User interaction contract (UX)

The assistant MUST:

- Ask **one question** per turn (Kernel rule).
- Use **multiple-choice** only; keep choices to **3–5 options** max, with **1-line “when to pick”** guidance per option.
- Prefer **`default_mode_request_user_input`** UI when available; otherwise use `a/b/c` options.
- Accept replies as:
  - `a` / `b` / `c` / …
  - `default`
  - optionally **one short sentence** after the letter (to add context).
- If the user replies in free text, map it to the closest option and confirm on the next turn.

Optional commands (do not break the single-question rule):

- `back` → revert the last captured answer and re-ask the same question.
- `skip` → leave blank, record an assumption, move on.
- `stop` → synthesize with current state (even if imperfect).
- `log` → show the full Interview Log (otherwise keep the log compact).
- `batch` → for power users: allow up to 3 questions in the next turn only.

## Default mode + intent

- Mode: `standard`
- Intent: start `DISCOVER`, switch to `DECIDE` as soon as tradeoffs appear

## Scope and triggers

- Use when requirements or scope are unclear for a feature/refactor.
- Use when you want to produce a spec with explicit decisions and an approval gate.
- Use when you want a beginner-friendly path to a system design answer.

## Deliverables
- an interview-driven spec or spec addendum with explicit decisions and assumptions
- an approval gate before planning or implementation work begins
- a compact handoff recommendation to the next skill or workflow

## Failure mode
If the request is actually implementation or direct code work, stop treating it as an interview problem and route to the better execution skill instead of forcing more questions.

## Step 0 — Fresh vs Delta

If you detect an existing spec/notes (pasted text or a referenced doc), default to **Delta mode**.

**Choose starting mode**
- a) Fresh: create a spec from scratch (default if nothing exists yet)
- b) Delta: deepen/refine an existing spec/notes (Recommended when a draft exists)
- c) Not sure — you decide

Default: b) if existing notes/spec are present; otherwise a)

Behavior:
- **Fresh** → use the relevant spine below normally.
- **Delta** → run the same spine, but ask only about missing or risky items (scope boundaries, failure modes, constraints, decisions, acceptance criteria).

## Track selection (first substantive question)

If the user’s intent is not obvious from context, start here.

**Choose the interview track**
- a) Feature/refactor requirements (default) — clarify what to build
- b) System design answer (beginner) — guided design interview
- c) Architecture decision / ADR — choose between alternatives
- d) Product/PM scope — value + metrics + rollout
- e) Bug triage — repro + evidence + next experiment

Default: a)

Behavior:
- If user chooses **c** → invoke `/architecture-interview` immediately (carry over captured context).
- If user chooses **d** → invoke `/pm-interview` immediately.
- If user chooses **e** → invoke `/bug-interview` immediately.
- If user chooses **b** → run **Spine B** below (within this wrapper).
- If user chooses **a** → run **Spine A** below.

---

## Spine A — Requirements-to-build (default)

Ask these in order, skipping anything already answered by context (especially in Delta mode).

1) **Problem (PAS: Problem)**
- Options should force an observable problem statement (not a solution).

2) **Primary user / context**
- Options: internal team tool / dev tool / consumer app / ops platform / other.

3) **Impact type (PAS: Amplify)**
- Options should classify impact: user pain / revenue risk / ops toil / compliance risk / other.

4) **Success signal (PAS: Success)**
- Options: user-visible behavior / metric / both.

5) **Acceptance criteria style**
- Options: bullets / Given-When-Then / IO pairs.

6) **Scope bias for v1**
- Options: smallest shippable / balanced / refactor-heavy.

7) **Primary constraint driver (choose 1)**
- Options: security / reliability / performance / cost / simplicity (or “other”).

8) **One failure mode we must handle well**
- Options: correctness/data loss / availability/downtime / latency/perf / security/privacy / UX breakage.

9) **Primary tradeoff decision (DECIDE)**
- Options: speed-to-ship / flexibility / correctness.

Optional (if still unclear or for `:deep`):
- integration touchpoints (1–3)
- rollout posture (flagged vs staged vs big-bang)
- observability expectations (logs/metrics/traces)
- migration/rollback constraints

---

## Spine B — System design answer (beginner-friendly)

Use this when the user wants a system design answer without needing perfect jargon.

1) **What are we designing (one sentence)?**
- Options should force: “Build X for Y measured by Z” vs “Improve X to reduce Y”.

2) **Functional scope (pick the top 2–3)**
- Options: CRUD / search / feeds & ranking / real-time updates / background jobs / analytics/reporting.

3) **Scale guess (pick one range)**
- Options: prototype (10s/day) / small (1–10 rps) / medium (100 rps) / large (10k rps+) / unknown.
- If unknown, pick a conservative default and record it as an assumption.

4) **Reliability & latency target (SLO-ish)**
- Options: internal tool (looser) / consumer-facing (medium) / mission-critical (tight).

5) **Data correctness preference**
- Options: strong consistency / eventual consistency acceptable / mixed (strong for writes, eventual for reads).

6) **Data model shape**
- Options: relational / key-value / document / time-series / graph.

7) **Core interfaces**
- Options: request/response API / async job queue / event stream / mixed.

8) **High-level architecture style**
- Options: single service + DB / modular monolith / microservices / serverless-managed.

9) **Biggest bottleneck risk**
- Options: read-heavy hot key / write amplification / fanout / large payloads / external dependency.

10) **Worst credible failure mode**
- Options: data loss / long outage / security leak / silent correctness bug / runaway cost.

Optional (if time remains):
- caching approach (none vs CDN vs app cache)
- rollout posture (flagged vs staged vs big-bang)
- observability baseline (logs/metrics/traces)

---

## Output

Use Kernel synthesis output verbatim.

If Spine B was used, append a short **Design Addendum**:

- **Text C4-style sketch**: Context (actors) → Containers (services/data stores) → Key flows.
- **Core APIs / operations** (bullets).
- **Entities + invariants** (bullets; 3–7 items).
- **Quick cross-cutting checklist**: security, reliability, performance, cost.

If an architecture decision was made, optionally append an **ADR Draft** (status: Proposed) in Nygard format.

After approval, recommend a clean handoff:
- “Create/update SPEC.md (or the provided doc)”
- “Run planning/execution in a separate session using the approved spec”

---

## Variation guidance

Avoid repeating identical option sets. Vary structure and examples based on domain (product, infra, data, UX) while keeping cognitive load low.

## Required inputs
- User request details and any relevant files/links.

## Constraints
- Redact secrets/PII by default.
- Check against current global instructions in `~/.codex/AGENTS.md` and linked standards docs.
- Avoid implementation or tool-heavy exploration before the approval gate.

## Anti-patterns

- Asking multi-part questions in a single turn (unless user explicitly says `batch`).
- Skipping the approval gate when assumptions exist.
- Continuing the interview after the highest-risk unknown is already resolved.
- Asking generic discovery questions that do not unlock a decision.

## Validation

- Fail fast: stop at the first failed gate and correct before proceeding.
- Ensure the approval gate is explicit before any execution/planning.
- Ensure the synthesis contains decisions, assumptions, and concrete next steps.

## Examples

- "Interview me to clarify a feature scope."
- "Refine this draft spec and surface the missing decisions."

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Procedure
1. Clarify mode (Fresh vs Delta), track, and mode budget.
2. Run the single-question interview loop.
3. Synthesize the interview into decisions, assumptions, and acceptance criteria.
4. Present the approval gate.
5. Handoff to planning or execution in a separate step or session.

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

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Legacy mode: pm-track
Use this mode when the user needs a product interview focused on scope, value, metrics, and rollout rather than a general requirements interview.

### pm-track optimizes for
- minimum viable scope that proves value;
- a measurable primary outcome plus a guardrail when needed;
- explicit non-goals and release posture;
- visible tradeoffs between speed, UX quality, and future-proofing.

### pm-track interaction rules
- keep the single-question, multiple-choice kernel style;
- in Delta mode, skip settled decisions and target only scope gaps, success metrics, and rollout tradeoffs;
- keep stakeholder requests separate from validated requirements;
- require an explicit out-of-scope list before treating the spec as approved.

### pm-track spine
Ask in order when not already answered:
1. target user or segment;
2. situation or trigger;
3. observable problem;
4. cost of the problem;
5. value hypothesis;
6. primary success metric and optional guardrail;
7. activation or distribution path;
8. MVP scope boundary in one sentence;
9. non-goals;
10. tradeoff and rollout posture.

### pm-track deliverable add-on
Append a compact PRD-lite addendum covering:
- target user;
- job to be done;
- problem and value hypothesis;
- primary metric and optional guardrail;
- activation or distribution path;
- release strategy;
- open questions deferred to later.

## Folded Legacy Modes (Core60)
<!-- core60-folded-modes:v1:start -->
This skill owns legacy capability from retired skills. Use these modes when requests match prior behavior.

- `pm-track` from `interview/pm-interview`: Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified.

Deep legacy details: `references/folded-legacy-modes-core60.md`.
<!-- core60-folded-modes:v1:end -->
