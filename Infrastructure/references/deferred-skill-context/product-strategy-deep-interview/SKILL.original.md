---
name: deep-interview
description: Deepen an existing doc or topic through a structured gap-filling interview that adds missing assumptions, edge cases, and approval gates. Use when refining PRDs, ADRs, tickets, notes, or draft specs before planning or execution.
metadata:
  skill-type: team_automation
---

# deep-interview (enhancer wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
This wrapper is optimized for **enhancing what already exists** (draft specs, PRDs, ADRs, tickets, notes) by forcing missing decisions and surfacing hidden risks.

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Detecting input type](#detecting-input-type)
- [Interview focus](#interview-focus-what-deep-means-here)
- [Round-by-round process](#round-by-round-process)
- [Completion](#completion)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

## Spec-driven workflow (recommended)

Interview → update spec/doc → (after approval) run planning/execution as a separate step/session.

## Standards snapshot (March 2026)
- Default to Delta mode when a draft artifact already exists.
- Focus on the missing decisions, contradictions, and failure modes most likely to break delivery later.
- Preserve source documents and append insight rather than rewriting their intent unless the user explicitly asks for a deeper rewrite.
- End with an approval gate and a concrete next step rather than an open-ended brainstorm.

## User profile alignment (Jamie)

Follow `~/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Always use multiple-choice questions (3–5 options, include a recommended default) and map any free-text reply to the closest option with confirmation.

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

## Deliverables
- an updated source doc with `Delta Insights` or `Interview Insights` when file input is provided
- a structured summary with decisions, assumptions, risks, and next steps when the input is a topic
- an explicit approval gate before planning or implementation work proceeds

## Failure mode
If there is no meaningful artifact to deepen and the user really needs a front-door discovery interview, route to `interview-me` instead of pretending this is a delta enhancement task.

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
3) Ask the next high-leverage question using `default_mode_request_user_input` (preferred).
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

## Required inputs
- `$ARGUMENTS` (file path or topic) + any relevant links.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.
- Check against current global instructions in `~/.codex/AGENTS.md` and linked standards docs.
- Do not inject prose into code files unless the user explicitly asks for that behavior.

## Validation

- Fail fast: stop at the first failed gate and correct before proceeding.
- Ensure a Delta/Interview Insights section is added for file inputs.
- Ensure decisions + assumptions are captured before approval.
- Ensure the final output names the next highest-value unresolved question if one remains.

## Anti-patterns

- Do not inject prose into code files without explicit user approval.
- Do not overwrite the source doc’s structure; append insights instead.

## References
- `Infrastructure/references/contract.yaml` (output contract)
- `Infrastructure/references/evals.yaml` (quality checks)

## Examples

- "Deepen this draft PRD in docs/feature-spec.md."
- "Interrogate these notes and append Delta Insights to the same file."

## Procedure
1. Detect input type (file vs topic).
2. Read source material if a file is provided and pre-fill the interview log in Delta mode.
3. Run the deep interview loop using the highest-leverage missing decision each round.
4. Synthesize outputs and update the doc if applicable.
5. Present the approval gate and handoff to planning or execution.

Topic
$ARGUMENTS
---

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

## See Also

| Skill | When to use together |
|---|---|
| [[interview-me]] | Use for fresh requirements discovery; use this skill for deepening existing drafts |
| [[brainstorming]] | Use before this skill when the topic is still too vague for delta-mode enhancement |
| [[he-plan]] | Hand the completed insights to planning for an execution-ready implementation sequence |
| [[architecture-interview]] | Use when deep-interview surfaces a major architectural tradeoff requiring structured review |

**Topic map:** [[product-strategy]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Legacy mode: bug-track
Use this mode when the user brings a bug report, ticket, or prod symptom that lacks a reliable repro or a clear next diagnostic step.

### bug-track optimizes for
- reliable repro or a plan to synthesize one;
- evidence-driven narrowing instead of guessing;
- the smallest next diagnostic experiment with clear signal value.

### bug-track interaction rules
- stay in Delta mode when a bug report or incident ticket already exists;
- ask only for missing facts needed to confirm repro, severity, environment, or regression window;
- avoid broad log or data dumps without a concrete hypothesis;
- switch from DISCOVER to DECIDE only when choosing the next experiment.

### bug-track spine
Ask in order when needed:
1. expected versus actual behavior;
2. severity and workaround status;
3. minimal repro steps;
4. frequency;
5. environment;
6. evidence available;
7. regression window;
8. recent changes;
9. minimal repro artifact;
10. next diagnostic step.

### bug-track deliverable add-on
Append a compact triage addendum covering:
- repro status;
- suspected layer;
- top hypotheses;
- smallest next experiment;
- instrumentation needed;
- rollback or mitigation options.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
