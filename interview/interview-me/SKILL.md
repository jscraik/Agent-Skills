---
name: interview-me
description: "Interactive, multiple-choice interview for requirements discovery and spec clarification; turns an underspecified idea (or draft spec) into an execution-ready spec with decisions, assumptions, acceptance criteria, and approval. Use when a user asks to 'interview me', clarify scope, or refine a draft spec."
metadata:
  short-description: "Front-door interview to clarify scope and produce a spec."
---

# interview-me (interactive front door)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: single-question loop, question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## What this wrapper optimizes for

- **Low cognitive load**: one question, multiple-choice answers, safe defaults.
- **Design-ready output**: scope, acceptance criteria, decisions, assumptions, risks, rollout.
- **Works from either starting point**:
  - **Fresh mode**: you have an idea but it’s underspecified.
  - **Delta mode**: you already have notes/spec; we deepen it by filling gaps and forcing decisions.

## Spec-driven workflow (recommended)

Interview → write/update spec → (after approval) run planning/execution as a separate step/session.

## User profile alignment (Jamie)

Follow `/Users/jamiecraik/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Always use multiple-choice questions (3–5 options, include a recommended default) and map any free-text reply to the closest option with confirmation.

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
- Prefer **AskUserQuestion** UI when available; otherwise use `a/b/c` options.
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

## When to use

- Use when requirements or scope are unclear for a feature/refactor.
- Use when you want to produce a spec with explicit decisions and an approval gate.
- Use when you want a beginner-friendly path to a system design answer.

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

## Inputs
- User request details and any relevant files/links.

## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md.

## Anti-patterns

- Asking multi-part questions in a single turn (unless user explicitly says `batch`).
- Skipping the approval gate when assumptions exist.

## Validation

- Fail fast: stop at the first failed gate and correct before proceeding.
- Ensure the approval gate is explicit before any execution/planning.

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Examples

- "Interview me to clarify a feature scope."
- "Refine this draft spec and surface the missing decisions."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
- Avoid destructive operations without explicit user direction.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

## Procedure
1) Clarify mode (Fresh vs Delta) + track + mode budget.
2) Run the single-question interview loop.
3) Synthesize + approval gate.
4) Handoff to planning/execution (separate step/session).

## Antipatterns
- Do not add features outside the agreed scope.
- Do not drift into implementation before approval.
