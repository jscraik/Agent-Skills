---
name: interview-me
description: "Interactive, multiple-choice interview that turns an underspecified idea into a design-ready spec (decisions + assumptions + approval)."
---

# interview-me (interactive front door)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: single-question loop, question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## What this wrapper optimizes for

- **Low cognitive load**: one question, multiple-choice answers, safe defaults.
- **Design-ready output**: scope, acceptance criteria, decisions, assumptions, risks, rollout.
- **Works without prerequisite knowledge**: if the user is unsure, pick a default and record it as an assumption to approve.

## User interaction contract (UX)

The assistant MUST:

- Ask **one question** per turn (Kernel rule).
- Keep choices to **3–5 options** max, with **1-line “when to pick”** guidance per option.
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

## Default mode + intent

- Mode: `standard`
- Intent: start `DISCOVER`, switch to `DECIDE` as soon as tradeoffs appear

## When to use

- Use when requirements or scope are unclear for a feature/refactor.
- Use when you want to produce a design-ready spec with explicit decisions.
- Use when you need a beginner-friendly, guided path to a software design answer.

## Track selection (first question)

If the user’s intent is not obvious from context, start here.

1) **Choose the interview track**

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

## Spine A — Requirements-to-build (default)

Ask these in order, skipping anything already answered by context.

1) **Impact type (PAS: Amplify)**
- Options should classify impact: user pain / revenue risk / ops toil / compliance risk / other.

2) **Success signal**
- Options: user-visible behavior / metric / both.

3) **Acceptance criteria style**
- Options: bullets / Given-When-Then / IO pairs.

4) **Scope bias for v1**
- Options: smallest shippable / balanced / refactor-heavy.

5) **Primary constraint driver (choose 1)**
- Options: security / reliability / performance / cost / simplicity (or “other”).

6) **One failure mode we must handle well**
- Options: correctness/data loss / availability/downtime / latency/perf / security/privacy / UX breakage.

7) **Primary tradeoff decision (DECIDE)**
- Options: speed-to-ship / flexibility / correctness.

Optional (if still unclear or for `:deep`):

- rollout posture (flagged vs staged vs big-bang)
- observability expectations (logs/metrics/traces)
- migration/rollback constraints

## Spine B — System design answer (beginner-friendly)

Use this when the user wants to produce a system design answer but doesn’t have all the jargon or patterns memorized.

1) **What are we designing (in one sentence)?**
- Options should force a crisp framing: “Build X for Y measured by Z” vs “Improve X to reduce Y”.

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

## Output

Use Kernel synthesis output verbatim.

If Spine B was used, append a short **Design Addendum**:

- **Text C4-style sketch**: Context (actors) → Containers (services/data stores) → Key flows.
- **Core APIs / operations** (bullets).
- **Entities + invariants** (bullets; 3–7 items).
- **Quick cross-cutting checklist**: security, reliability, performance, cost.

If an architecture decision was made, optionally append an **ADR Draft** (status: Proposed) in Nygard format.

---

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
1) Clarify track + mode.
2) Run the single-question interview loop.
3) Synthesize + approval gate.

## Antipatterns
- Do not add features outside the agreed scope.
- Do not drift into implementation before approval.
