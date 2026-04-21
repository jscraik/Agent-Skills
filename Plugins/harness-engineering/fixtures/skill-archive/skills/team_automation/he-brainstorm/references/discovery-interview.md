# HE Brainstorm Discovery Interview

Read when: the brainstorm request is underspecified and you need a concise, structured interview before requirements capture.

## Round model
- Keep rounds progressive and minimal.
- Ask one question, wait for one answer, then decide whether another round is needed.
- Keep each round tied to a concrete uncertainty that affects product requirements.

## Request user input mini-templates
- `Goal`: "What should this skill help you do?"
- `Primary user`: "Who is the main user for this change?"
- `Boundary`: "What should stay out of scope for this brainstorm?"
- `Success`: "What would make this outcome clearly successful?"

Use `request_user_input` when available and the round benefits from constrained options; otherwise ask one clear question in chat.

## Copy paste payload examples
Example `request_user_input` shape:

```json
{
  "questions": [
    {
      "header": "Primary goal",
      "id": "primary_goal",
      "question": "What should this skill help you do?",
      "options": [
        {
          "label": "Clarify feature scope (Recommended)",
          "description": "Define the product behavior before planning."
        },
        {
          "label": "Compare solution directions",
          "description": "Evaluate alternatives and pick one."
        }
      ]
    }
  ]
}
```

Example chat round:
- Question: "What should this skill help you do?"
- Why this matters: "This keeps us focused on the highest-leverage decision before writing requirements."

## Round 1: Goal and boundary
- Ask one intuitive starter question: "What should this skill help you do?"
- Follow with one boundary check only if needed: "What must remain out of scope?"

## Round 2: Users and outcomes
- Identify primary user and desired behavior change.
- Confirm what value the user should see if this succeeds.

## Round 3: Constraints and non-goals
- Capture hard constraints (timeline, policy, dependency, compliance).
- Capture explicit non-goals to prevent requirement drift.

## Round 4: Alternatives
- Confirm whether the user wants comparison mode.
- If yes, gather enough preference context to evaluate 2-3 approaches.

## Round 5: Success criteria
- Ask for concrete success checks and failure signals.
- Make sure criteria are measurable enough for later planning handoff.

## Round 6: Confirmation
- Use an explicit confirmation question before finalizing requirements:
  - "Does this capture the docs work well enough for me to implement?"
  - "Anything to add or change before I implement it?"
