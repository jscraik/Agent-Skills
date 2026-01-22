---
name: deep-interview
description: "Deep, gap-filling interview that enhances an existing doc/spec (preferred) or explores a topic. Use when deepening PRDs, ADRs, tickets, notes, or draft specs; if given a doc path, update it in-place with Delta/Interview Insights and an approval gate."
metadata:
  short-description: "Deepen existing docs/specs with a gap-filling interview."
---

# deep-interview (enhancer wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
This wrapper is optimized for **enhancing what already exists** (draft specs, PRDs, ADRs, tickets, notes) by forcing missing decisions and surfacing hidden risks.

## Spec-driven workflow (recommended)

Interview → update spec/doc → (after approval) run planning/execution as a separate step/session.

## User profile alignment (Jamie)

Follow `/Users/jamiecraik/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Always use multiple-choice questions (3–5 options, include a recommended default) and map any free-text reply to the closest option with confirmation.

## Philosophy + guiding questions

Deep interview = maximize decision quality with minimal churn. Focus on the gaps that can break the plan later.

Guiding questions:
- What decision will this answer unlock?
- What is the highest-risk unknown for v1?
- What would make this spec fail in the real world?
- What evidence would make us confident to proceed?

## When to use

- Use when a draft spec, PRD, ADR, ticket, or notes exist but gaps remain.
- Use when you need delta-mode enhancement rather than a greenfield interview.
- Use when a file path is provided and you must update the source artifact.

## Variation

- Vary prompts by artifact type (PRD vs ADR vs ticket vs notes) and maturity.
- Avoid repeating identical option sets; tailor tradeoffs to context.

## Detecting input type

Given `$ARGUMENTS`, determine what the user is trying to deepen:

1) **If `$ARGUMENTS` looks like a file path** (contains `/` or an extension like `.md`, `.txt`, `.rst`, `.adoc`):
   - Read the file (discovery-only).
   - Interview about its contents (Delta mode).
   - At the end, update the same file in-place:
     - Preserve structure.
     - Append a section: `## Delta Insights` (preferred) or `## Interview Insights`.
2) **If `$ARGUMENTS` is a topic/description**:
   - Interview about the concept.
   - At the end, produce a comprehensive summary + decisions + open questions.
   - Optionally propose a target file name for the spec (but do not create it unless asked).

### Safety for code files
If the input is a code file (`.ts/.js/.py/...`), treat it as **context-only** by default:
- Do not inject prose into code.
- Write insights into a sidecar doc (e.g. `docs/<topic>-insights.md`) unless the user explicitly requests code edits.

## Default mode + intent

- Mode: `deep`
- Intent: start `DISCOVER` (extract facts), then `DECIDE` aggressively (force tradeoffs)

## Interview focus (what “deep” means here)

Compared to `/interview-me`, this wrapper prioritizes:

- Missing scope boundaries and non-goals
- Hidden assumptions and contradictions
- Failure modes + “how we detect/roll back”
- Integration points and interface contracts
- Non-functional requirements (security, reliability, perf, cost)
- Rollout/migration/observability
- “What could go wrong?” and “what would make this fail?”

## Round-by-round process

Follow kernel rules (default: one question per turn). If the user says `batch`, you may ask up to 3 questions in one turn with a reply key.

Each round:
1) Summarize what the doc already claims (1–3 bullets).
2) Identify the top gap using the kernel prioritization rubric.
3) Ask the next high-leverage question using AskUserQuestion (preferred).
4) Update Interview Log + Captured answer.
5) Continue until stop conditions or user says `done`.

## Completion

When complete:

### For file input
- Summarize key decisions made during the interview.
- Update the original file:
  - Add `## Delta Insights` near the end.
  - Include: Decisions table, Assumptions register, Risks/rollout/observability, Open questions.
- Preserve original structure and intent.
- End with the kernel approval gate.

### For topic input
- Provide:
  - One-sentence pitch
  - Decisions table
  - Assumptions register
  - Draft acceptance criteria
  - Risks/rollout/observability
  - Open questions
  - Next step (single action)

---

## Inputs
- `$ARGUMENTS` (file path or topic) + any relevant links.

## Outputs
- Updated spec/doc (if file input) OR a structured summary artifact (if topic input).
- Include `schema_version: 1` if outputs are contract-bound.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md.

## Validation

- Fail fast: stop at the first failed gate and correct before proceeding.
- Ensure a Delta/Interview Insights section is added for file inputs.
- Ensure decisions + assumptions are captured before approval.

## Anti-patterns

- Do not inject prose into code files without explicit user approval.
- Do not overwrite the source doc’s structure; append insights instead.

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Examples

- "Deepen this draft PRD in docs/feature-spec.md."
- "Interrogate these notes and append Delta Insights to the same file."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Procedure
1) Detect input type (file vs topic).
2) Read source material (if file) and pre-fill Interview Log (Delta mode).
3) Run deep interview loop (kernel).
4) Synthesize outputs, update doc if applicable.
5) Approval gate + handoff to planning/execution.

Topic
$ARGUMENTS
---
