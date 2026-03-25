# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Role goal](#round-1-role-goal)
- [Round 2: Scope](#round-2-scope)
- [Round 3: Safety and runtime limits](#round-3-safety-and-runtime-limits)
- [Round 6: Confirmation](#round-6-confirmation)

## When to use this reference

Use this when a role request is promising but still underspecified:
- the user wants a new role but has not pinned down the job it should own;
- the user wants to tighten an existing role but the main failure mode is still fuzzy;
- the role could change project or global runtime behavior and you need a safer boundary first.

## How to run the interview

Default behavior:
- use `request_user_input` first when one short decision fits the round;
- if that tool is unavailable, ask the same round in chat;
- ask one round at a time;
- do not advance until the current round is answered;
- stop when you are confident the role can be created safely.

Interaction style:
- lead with one simple question, not a wall of bullets;
- explain the purpose of the round in plain language before asking it;
- use role language the user would naturally recognize;
- summarize what you learned before moving on.

## Request user input mini-templates

### Round 1 template: role goal

Chat intro:
- "Let’s start simple: what should this role help with?"

Good tool question shape:
- `Header:` `Goal`
- `Question:` `What kind of help should this role provide?`
- `Options:`
  - `Create new role (Recommended)` — Best when the role is mostly net-new.
  - `Improve current role` — Best when an existing role needs tightening.
  - `Package repeatable role` — Best when the role already works and needs safer reuse.

Follow-up prompt if needed:
- `In one sentence, what should this role reliably do every time?`
- Canonical round-1 wording fallback: `What should this skill help you do?`

### Round 2 template: scope

Chat intro:
- "Next, let’s make sure the scope is explicit."

Good tool question shape:
- `Header:` `Scope`
- `Question:` `Where should this role live?`
- `Options:`
  - `Project role (Recommended)` — Best when the role is specific to one repo.
  - `Global role` — Best when the role should be reusable across repos.
  - `Not sure yet` — Best when the user needs a quick tradeoff before deciding.

Follow-up prompt if needed:
- `Should this role be mostly read-only, or should it be able to edit files too?`

### Round 3 template: safety and limits

Chat intro:
- "Last, let’s make the boundaries explicit so the role behaves safely."

Good tool question shape:
- `Header:` `Guardrails`
- `Question:` `What should this role optimize for most?`
- `Options:`
  - `Safety and predictability (Recommended)` — Best when the role should avoid surprising behavior.
  - `Speed and low friction` — Best when fast progress matters more than exhaustive checks.
  - `Depth and completeness` — Best when richer output is worth more time or tokens.

Follow-up prompt if needed:
- `Should I set any thread, depth, runtime, nickname, or sandbox limits up front?`

## Round 6: Confirmation

Chat intro:
- "Here’s my understanding so far."

Confirmation ask:
- summarize with the standard role summary block;
- call out assumptions with an `Assumptions:` line when needed;
- end with one simple confirmation question:
  - `Does this capture it well enough for me to build?`
  - `Anything to add or change before I build it?`

## Copy paste payload examples

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Goal",
      "id": "role_goal",
      "question": "What kind of role are we shaping?",
      "options": [
        {
          "label": "New role (Recommended)",
          "description": "Use this when the role is mostly net-new."
        },
        {
          "label": "Improve role",
          "description": "Use this when an existing role needs tightening."
        },
        {
          "label": "Package role",
          "description": "Use this when the role already works and needs reuse."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- `What should this role help you do?`

### Round 2 example

```json
{
  "questions": [
    {
      "header": "Scope",
      "id": "role_scope",
      "question": "Where should this role usually live?",
      "options": [
        {
          "label": "Project (Recommended)",
          "description": "Best when the role is specific to one repo."
        },
        {
          "label": "Global",
          "description": "Best when the role should work across repos."
        },
        {
          "label": "Not sure",
          "description": "Use this when a quick tradeoff is still needed."
        }
      ]
    }
  ]
}
```
