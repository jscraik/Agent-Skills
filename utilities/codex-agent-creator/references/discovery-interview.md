# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Agent goal](#round-1-agent-goal)
- [Round 2: Scope](#round-2-scope)
- [Round 3: Safety and runtime limits](#round-3-safety-and-runtime-limits)
- [Round 6: Confirmation](#round-6-confirmation)

## When to use this reference

Use this when a custom-agent request is promising but underspecified:
- the user wants a new custom agent but has not pinned down the exact job;
- the user wants to tighten an existing custom agent but the failure mode is still fuzzy;
- the request could change project or global runtime behavior and needs safer boundaries first.

## How to run the interview

Default behavior:
- use `request_user_input` first when one short decision fits the round;
- if that tool is unavailable, ask the same round in chat;
- ask one round at a time;
- do not advance until the current round is answered;
- stop when confidence is high enough to build safely.

Interaction style:
- lead with one simple question, not a wall of bullets;
- explain the purpose of the round in plain language before asking it;
- use language the user would naturally recognize;
- summarize what you learned before moving on.

## Request user input mini-templates

### Round 1 template: agent goal

Chat intro:
- "Let’s start simple: what should this custom agent help with?"

Good tool question shape:
- `Header:` `Goal`
- `Question:` `What kind of help should this custom agent provide?`
- `Options:`
  - `Create new custom agent (Recommended)` — Best when capability is mostly net-new.
  - `Improve current custom agent` — Best when an existing custom agent needs tightening.
  - `Package repeatable custom agent` — Best when the agent already works and needs safer reuse.

Follow-up prompt if needed:
- `In one sentence, what should this custom agent reliably do every time?`

### Round 2 template: scope

Chat intro:
- "Next, let’s make sure scope and install location are explicit."

Good tool question shape:
- `Header:` `Scope`
- `Question:` `Where should this custom agent live?`
- `Options:`
  - `Project custom agent (Recommended)` — Best when behavior is specific to one repo.
  - `Global custom agent` — Best when behavior should be reusable across repos.
  - `Not sure yet` — Best when a quick tradeoff is still needed.

Follow-up prompt if needed:
- `Should this custom agent be mostly read-only, or should it be able to edit files too?`

### Round 3 template: safety and limits

Chat intro:
- "Last, let’s make the boundaries explicit so the custom agent behaves safely."

Good tool question shape:
- `Header:` `Guardrails`
- `Question:` `What should this custom agent optimize for most?`
- `Options:`
  - `Safety and predictability (Recommended)` — Best when behavior should avoid surprises.
  - `Speed and low friction` — Best when fast progress matters more than exhaustive checks.
  - `Depth and completeness` — Best when richer output is worth more time or tokens.

Follow-up prompt if needed:
- `Should I set any thread, depth, runtime, nickname, or sandbox limits up front?`

## Round 6: Confirmation

Chat intro:
- "Here’s my understanding so far."

Confirmation ask:
- summarize with the standard custom-agent summary block;
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
      "id": "agent_goal",
      "question": "What kind of custom agent are we shaping?",
      "options": [
        {
          "label": "New custom agent (Recommended)",
          "description": "Use this when the capability is mostly net-new."
        },
        {
          "label": "Improve custom agent",
          "description": "Use this when an existing custom agent needs tightening."
        },
        {
          "label": "Package custom agent",
          "description": "Use this when the custom agent already works and needs safer reuse."
        }
      ]
    }
  ]
}
```

Suggested follow-up in chat:
- `What should this custom agent help you do?`

### Round 2 example

```json
{
  "questions": [
    {
      "header": "Scope",
      "id": "agent_scope",
      "question": "Where should this custom agent usually live?",
      "options": [
        {
          "label": "Project (Recommended)",
          "description": "Best when the behavior is specific to one repo."
        },
        {
          "label": "Global",
          "description": "Best when the behavior should work across repos."
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
