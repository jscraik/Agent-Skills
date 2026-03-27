---
name: alignment-checkpoint
description: "Intent-alignment gate for ambiguous/high-stakes requests. Use this when you want to extract goal/assumptions/criteria and require an explicit /proceed approval gate before any tool use."
metadata:
  skill-type: team_automation

---

# Alignment Checkpoint

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Constraints](#constraints-safety)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Procedure](#procedure)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use
Use this skill when:
- You want to **prevent misunderstandings** before work begins.
- The request is ambiguous, multi-part, or high-risk.
- The user says: “alignment”, “checkpoint”, “confirm first”, “don’t start yet”, “before you run tools”, or similar.
- You are about to run tools (shell/web/filesystem/MCP) and want a clear go/no-go.

## Required inputs
- The user’s request text (treat as canonical; quote exactly in stasis mode).
- Any explicit constraints already stated by the user (time, scope, “do not implement”, etc.).

## Deliverables
Always produce (Phase 0):
1) A JSON extraction containing:
   - `explicit_goal`
   - `implicit_assumptions`
   - `success_criteria`
2) A formatted summary (goal/assumptions/criteria).
3) Three approach options: `minimal`, `balanced`, `comprehensive`.
4) An explicit gate requiring: `/proceed <option>` or `/clarify <question-or-answer>`.

Additionally, if stasis mode is triggered:
- A **STASIS_RECORD** containing the user request verbatim.
- Confirmation that **no tools will be used** and **no implementation will occur**.
- Optionally (only if explicitly requested) a **tool-free** plan outline.

## Standards snapshot (March 2026)
- This skill is a hard preflight gate: no tools, no edits, no hidden “quick checks” before approval.
- Make assumptions legible enough that the user can accept or reject them quickly.
- Prefer one sharp gate with three practical options over a sprawling plan dump.
- Preserve user wording accurately when stasis mode is active.

## Constraints (Safety)

Hard rule: before the user explicitly approves, you MUST NOT:
- run shell commands
- read/write repo files
- browse the web
- call MCP tools
- create/modify branches, issues, PRs

Secrets/PII hygiene:
- Never request or echo tokens/keys/credentials.
- Do not paste sensitive user data into examples; redact if needed.

Single-threading:
- Ask at most **one** clarifying question at a time.

## Philosophy

- **Align first, act second.** Output structure that the user can approve.
- **Assumptions are debts.** State them explicitly so the user can accept/reject.
- **No surprises.** Tools and implementation only after an explicit `/proceed`.

## Procedure

### 0) Detect stasis mode (preserve / do NOT implement)

If the user request includes either phrase (case-insensitive):
- `do NOT implement` / `do not implement`
- `preserve only`

Then:
1) Emit a **STASIS_RECORD** (verbatim request; no paraphrasing).
2) State: “Stasis mode is active: no tools will be used, and no implementation will occur.”
3) If the user explicitly asked for a plan, you MAY provide a **tool-free** plan outline.
4) Still present the approach options and require `/proceed <option>` before any tool use.

STASIS_RECORD format:
- `STASIS_RECORD`
- `timestamp: <ISO-8601 local time>`
- `verbatim_request:`
- `<paste the user request exactly as written>`

### 1) Produce the structured extraction (required)

Output a JSON object in a `json` code fence with EXACTLY these keys:

```json
{
  "explicit_goal": "",
  "implicit_assumptions": [],
  "success_criteria": []
}
```

Rules:
- Do not invent unknown specifics; express them as assumptions.
- If success criteria are missing, propose *testable* criteria and label them as assumptions.

### 2) Present the alignment summary (required)

Show:
- **Goal** (1 line)
- **Assumptions** (bullets)
- **Success criteria** (bullets)

### 3) Present 3 approach options (required)

Provide these options and what you would do *if approved*:
- **minimal**: smallest safe slice; minimal verification; no extras.
- **balanced**: normal engineering standard; lightweight tests/verification; minimal docs.
- **comprehensive**: thorough analysis; strongest verification; deeper docs/risk review.

### 4) Gate (required) — stop and wait

End with:
- “Reply with `/proceed minimal|balanced|comprehensive` to continue.”
- Or: ask **one** clarifying question and instruct: “Reply `/clarify <answer>`.”
- Additionally, the user may always ask their own clarification via: `/clarify <question>` (then re-run Phase 0 with the new info).

Then STOP. Do not continue into implementation or tool usage.

## Validation

Fail fast checks (if any fail, STOP and fix the first failure):
- Did I avoid all tool calls before approval?
- Did I output the JSON extraction with EXACTLY the 3 required keys?
- Did I present 3 options (minimal/balanced/comprehensive)?
- Did I end with an explicit gate and stop?
- If stasis mode triggered: did I include a STASIS_RECORD with the request verbatim?

Skill contract + evals:
- `references/contract.yaml` defines purpose/triggers/risks/non-goals.
- `references/evals.yaml` contains evaluation prompts + acceptance checks.

## Anti-patterns

- Starting implementation “just to get momentum” before `/proceed`.
- Running any tool “to confirm” before approval.
- Hiding assumptions or treating guesses as facts.
- Asking multiple clarifying questions at once.
- Ignoring “do NOT implement” / “preserve only” constraints.

## Examples

### Example A — ambiguous build request

User: “Add auth; make it secure; do it quickly.”

Assistant: outputs JSON → summary → 3 options → asks for `/proceed balanced`.

### Example B — stasis + plan-only

User: “Plan the migration—do NOT implement—preserve only.”

Assistant: STASIS_RECORD → JSON → options → gate (no tools).

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[interview-me]] | Follow with structured interview to clarify requirements |
| [[brainstorming]] | Explore approaches once intent is aligned |
| [[ce-plan]] | Move from approved intent to an execution-ready plan |
| [[product-spec]] | Produce a spec once ambiguity is resolved |
| [[decide-build-primitive]] | Decide the right primitive after intent is confirmed |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If goals, risks, or approval boundaries remain ambiguous, stop, restate the open assumptions, and fall back to explicit clarification rather than pretending alignment exists.
