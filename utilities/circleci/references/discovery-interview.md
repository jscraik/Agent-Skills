# Discovery interview

## Table of Contents
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Goal and name](#round-1-goal-and-name)

## How to run the interview

Use one round at a time. Ask one plain-language question, confirm the answer, then move on.

- Explain why the round matters before asking the question.
- Do not dump the entire interview plan in one turn.
- Continue until you are about 95% confident the next execution step is safe.

## Request user input mini-templates

Use `request_user_input` for concise round-by-round discovery.

### Round 1 template: goal and name

Header: `Goal`

Question: `What kind of help should this skill provide?`

Options:
- `Create new workflow` (Recommended)
- `Improve existing workflow`
- `Package existing workflow`

## Copy paste payload examples

```json
{
  "questions": [
    {
      "header": "Goal",
      "id": "goal_mode",
      "question": "What should this skill reliably help with?",
      "options": [
        {
          "label": "Improve existing workflow",
          "description": "Use this when a current flow is already in use."
        }
      ]
    }
  ]
}
```

## Round 1: Goal and name

Ask this only:

- "What should this skill help you do?"

Then summarize assumptions and confirm before moving to the next round.
