# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Target and audience](#round-1-target-and-audience)
- [Round 2: Source of truth and constraints](#round-2-source-of-truth-and-constraints)
- [Round 3: Validation and handoff](#round-3-validation-and-handoff)
- [Round 6: Confirmation](#round-6-confirmation)

## When to use this reference

Use this when a docs request is promising but underspecified:
- the user wants a rewrite or audit but has not said which doc surface should change;
- the audience or job-to-be-done is unclear;
- brand authority, compliance constraints, or validation expectations are still fuzzy.

## How to run the interview

Default behavior:
- ask one round at a time;
- start with one plain-language question;
- add one short `Why this matters:` line;
- avoid dumping the full interview plan at once;
- stop once target, audience, source of truth, and validation path are clear enough to draft safely.

## Request user input mini-templates

Intuitive round-1 question:
- `Which documentation surface should we improve first?`

### Round 1 template: target

Chat intro:
- `Let’s start simple: which documentation surface should we improve first?`

Good tool question shape:
- `Header:` `Target`
- `Question:` `Which documentation surface should this update target first?`
- `Options:`
  - `README (Recommended)` — Best when onboarding, repo trust, or first-run experience is the main problem.
  - `Docs section` — Best when deeper guides or references need cleanup.
  - `Runbook or code docs` — Best when operational or in-code documentation is the main gap.

Follow-up prompt if needed:
- `Who is the primary reader for this page?`

### Round 3 template: validation

Chat intro:
- `Last, let’s make the handoff and validation path explicit.`

Good tool question shape:
- `Header:` `Checks`
- `Question:` `What should the handoff emphasize most?`
- `Options:`
  - `PR-ready edits (Recommended)` — Best when you want a concrete doc patch with a clear next step.
  - `Audit only` — Best when you need gaps, risks, and questions before rewriting.
  - `Full QA bundle` — Best when lint, readability, brand, and manual GitHub checks should all be recorded.

Follow-up prompt if needed:
- `Which checks do we need to record explicitly: lint, links, readability, brand, or GitHub UI review?`

## Copy paste payload examples

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Target",
      "id": "doc_surface",
      "question": "Which documentation surface should this update target first?",
      "options": [
        {
          "label": "README (Recommended)",
          "description": "Best when onboarding, repo trust, or first-run experience is the main problem."
        },
        {
          "label": "Docs section",
          "description": "Best when deeper guides or references need cleanup."
        },
        {
          "label": "Runbook or code docs",
          "description": "Best when operational or in-code documentation is the main gap."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- `What should this docs work help the reader do every time?`

## Round 1: Target and audience

**Why this matters:** documentation quality depends on serving the right reader on the right page.

Ask:
- Which doc surface should change first: README, `/docs`, runbook, or in-code docs?
- Who is the primary reader?
- What should the reader be able to do after reading it?

Friendly opener:
- `Which documentation surface should we improve first, and who is it for?`
- Canonical round-1 wording fallback: `What should this docs work help you do?`

## Round 2: Source of truth and constraints

**Why this matters:** doc rewrites go wrong when brand rules, platform limits, or policy owners are discovered too late.

Ask:
- What is the governing source of truth for commands, versions, and brand guidance?
- Are there compliance, rollout, or platform constraints?
- Is this public-repo work, private internal docs, or both?

Friendly opener:
- `What source of truth should I trust for commands, brand rules, and constraints here?`

## Round 3: Validation and handoff

**Why this matters:** docs are easy to make prettier and easy to leave unverifiable.

Ask:
- Which checks should the handoff include: readability, lint, links, brand, or manual GitHub UI checks?
- Should the deliverable include an audit only, a draft, or PR-ready edits?
- Do we need to record unknowns and follow-up questions explicitly?

Friendly opener:
- `How do you want the handoff verified: fast audit, full QA pass, or PR-ready edit bundle?`

## Round 6: Confirmation

**Why this matters:** summarizing before edits catches wrong assumptions cheaply.

Summarize:
- target surface;
- primary audience and job-to-be-done;
- governing sources of truth;
- validation plan;
- open assumptions.

End with one compact confirmation question:
- `Does this capture the docs work well enough for me to implement?`
- `Anything to add or change before I implement it?`

Explicit confirmation question guidance:
- Use `Does this capture...` for the primary confirmation prompt.
- Use `Anything to add or change before I implement it?` for the final check before edits begin.
