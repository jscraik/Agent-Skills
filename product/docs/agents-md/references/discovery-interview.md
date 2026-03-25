# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Scope and source of truth](#round-1-scope-and-source-of-truth)
- [Round 2: Refactor target](#round-2-refactor-target)
- [Round 3: Validation and handoff](#round-3-validation-and-handoff)
- [Round 6: Confirmation](#round-6-confirmation)

## When to use this reference

Use this when an `AGENTS.md` request is promising but underspecified:
- the user wants a new or updated AGENTS file but has not said which scope should change;
- the repo has multiple instruction files and precedence is unclear;
- the user wants progressive disclosure but the linked-doc layout is still fuzzy.

## How to run the interview

Default behavior:
- ask one round at a time;
- do not move to the next round until the current one is answered;
- start with one plain-language question;
- add one short `Why this matters:` line before the question;
- avoid dumping the full interview plan at once;
- stop when you can write the AGENTS update safely.

## Request user input mini-templates

### Round 1 template: scope

Chat intro:
- `Let’s start simple: what AGENTS scope are we changing?`

Good tool question shape:
- `Header:` `Scope`
- `Question:` `Which instruction scope should this update target?`
- `Options:`
  - `Repo root (Recommended)` — Best when the main AGENTS file sets the project-wide baseline.
  - `Nested area` — Best when only one subdirectory needs different rules.
  - `Global Codex home` — Best when the rule belongs in `~/.codex`.

Follow-up prompt if needed:
- `Which file is currently acting as the main source of truth here?`

### Round 2 template: refactor target

Chat intro:
- `Next, let’s separate auto-loaded instructions from linked reference docs.`

Good tool question shape:
- `Header:` `Refactor`
- `Question:` `What kind of AGENTS change do you want most?`
- `Options:`
  - `Trim root file (Recommended)` — Best when the root AGENTS file is too long or repetitive.
  - `Add linked docs` — Best when the root file is fine but depth needs a cleaner home.
  - `Fix precedence` — Best when overrides, fallback names, or conflicting files are the main problem.

Follow-up prompt if needed:
- `What should stay in the auto-loaded AGENTS scope, and what should move into linked docs?`

### Round 3 template: validation

Chat intro:
- `Last, let’s make sure the verification path is explicit.`

Good tool question shape:
- `Header:` `Checks`
- `Question:` `What should the handoff emphasize most?`
- `Options:`
  - `Verify active instructions (Recommended)` — Best when precedence and loaded files are the key risk.
  - `Preserve current layout` — Best when the repo has legacy filenames or a delicate doc structure.
  - `Flag cleanup work` — Best when deletion candidates and contradictions matter most.

Follow-up prompt if needed:
- `Do we need to preserve fallback filenames, custom byte limits, or specific verification commands?`

## Copy paste payload examples

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Scope",
      "id": "agents_scope",
      "question": "Which instruction scope should this update target?",
      "options": [
        {
          "label": "Repo root (Recommended)",
          "description": "Best when the main AGENTS file sets the project-wide baseline."
        },
        {
          "label": "Nested area",
          "description": "Best when only one subdirectory needs different rules."
        },
        {
          "label": "Global Codex home",
          "description": "Best when the rule belongs in ~/.codex."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- `What should this AGENTS update help keep clear every time?`

## Round 1: Scope and source of truth

**Why this matters:** AGENTS behavior depends on scope and precedence, so the wrong target file produces the wrong instructions.

Ask:
- Which scope should change: global, repo root, or a nested directory?
- Are there existing `AGENTS.override.md`, `AGENTS.md`, or fallback-named instruction files already in play?

Friendly opener:
- `Which instruction scope are we actually changing here?`
- Canonical round-1 wording fallback: `What should this skill help you do?`

## Round 2: Refactor target

**Why this matters:** progressive disclosure only helps if we separate auto-loaded instructions from linked reference material cleanly.

Ask:
- Should the root AGENTS file stay minimal and link outward?
- Which deeper guidance belongs in linked docs versus nested AGENTS scope files?
- Are there contradictions or duplicate rules that should be folded or deleted?

Friendly opener:
- `What should stay in the root AGENTS file, and what should move into linked docs or narrower overrides?`

## Round 3: Validation and handoff

**Why this matters:** AGENTS refactors are easy to get wrong if verification commands and expected behavior are not explicit.

Ask:
- Which commands should future operators run to confirm active instructions?
- Do we need to preserve fallback filenames or custom `project_doc_max_bytes` behavior?
- Should the handoff include deletion candidates or only safe edits?

Friendly opener:
- `How should someone verify this AGENTS setup after the refactor lands?`

## Round 6: Confirmation

**Why this matters:** instruction precedence mistakes are cheap to catch before editing and expensive to unwind later.

Summarize:
- target scope;
- files that should be auto-discovered;
- linked docs to add or keep;
- contradictions to resolve;
- validation commands to run.

Confirmation ask:
- summarize with the compact AGENTS update block;
- call out assumptions with an `Assumptions:` line when needed;
- end with one simple confirmation question:
  - `Does this capture it well enough for me to build?`
  - `Anything to add or change before I build it?`
