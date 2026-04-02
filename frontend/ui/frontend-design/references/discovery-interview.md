# Discovery interview

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [How to run the interview](#how-to-run-the-interview)
- [Request user input mini-templates](#request-user-input-mini-templates)
- [Copy paste payload examples](#copy-paste-payload-examples)
- [Round 1: Goal and context](#round-1-goal-and-context)
- [Round 2: Existing system signal](#round-2-existing-system-signal)
- [Round 3: Routing boundary](#round-3-routing-boundary)
- [Round 4: Constraints](#round-4-constraints)
- [Round 5: Success criteria](#round-5-success-criteria)
- [Round 6: Confirmation](#round-6-confirmation)

## When to use this reference

Use this reference when a broad frontend design ask does not yet include enough context to route safely:
- the user asks for "frontend design" but the best owner skill is still unclear;
- the intended audience, job to be done, or visual direction is missing;
- the request could route to `frontend-ui-design`, `design-system`, or `ui-ux-creative-coding` depending on one missing decision.

## How to run the interview

- Ask one round at a time.
- Use one plain-language question first, then a short `Why this matters:` line.
- Keep each round to one main decision; ask one small follow-up only if needed.
- Skip already-answered rounds.
- Avoid dumping the whole interview plan at once.
- Stop once the routing decision is clear and safe.

## Request user input mini-templates

### Round 1 template
- Intro: "Let’s start with the core goal."
- Question: "What should this skill help you do?"
- Why this matters: "This keeps us from routing to the wrong owner skill."

### Round 2 template
- Intro: "Now I want to confirm what already exists."
- Question: "Should this follow an existing design system, or are we setting a new direction?"
- Why this matters: "This determines whether we route to implementation or system governance."

### Round 3 template
- Intro: "Next, let’s pick the right downstream owner."
- Question: "Do you want production UI build guidance, design-system structure, or motion/polish refinement?"
- Why this matters: "The wrong owner can waste cycles and create conflicting guidance."

### Round 4 template
- Intro: "Let’s lock constraints before handoff."
- Question: "What constraints are non-negotiable: accessibility, brand voice, timelines, or performance?"
- Why this matters: "Handoff quality depends on constraint clarity."

### Round 5 template
- Intro: "I’ll define what good looks like."
- Question: "How will we know this route is successful for your immediate goal?"
- Why this matters: "Success criteria prevent ambiguous completion."

### Round 6 template
- Intro: "Here is my understanding before execution."
- Question: "Does this capture it well enough for me to build?"
- Why this matters: "Explicit confirmation avoids accidental misalignment."

## Copy paste payload examples

### Round 1 example

```json
{
  "questions": [
    {
      "header": "Goal",
      "id": "goal_mode",
      "question": "What should this skill help you do?",
      "options": [
        {
          "label": "Route broad ask (Recommended)",
          "description": "Use when we need to choose the right UI owner skill first."
        },
        {
          "label": "Implement UI now",
          "description": "Use when the request is already concrete enough for direct UI implementation."
        },
        {
          "label": "System-level design",
          "description": "Use when tokens, spacing, typography, or theme structure are the core request."
        }
      ]
    }
  ]
}
```

### Round 6 example

```json
{
  "questions": [
    {
      "header": "Confirm",
      "id": "confirm_route",
      "question": "Does this capture it well enough for me to build?",
      "options": [
        {
          "label": "Yes, proceed (Recommended)",
          "description": "Proceed with the selected owner skill and execution plan."
        },
        {
          "label": "Needs edits",
          "description": "Adjust assumptions before implementation starts."
        },
        {
          "label": "Change route",
          "description": "Pick a different owner skill before executing."
        }
      ]
    }
  ]
}
```

Follow-up confirmation prompt:
- "Anything to add or change before I build it?"

## Round 1: Goal and context
- Capture outcome in one sentence.
- Confirm target surface and user type.

## Round 2: Existing system signal
- Decide existing-system, partial-system, or greenfield.
- Confirm whether existing tokens and components are mandatory.

## Round 3: Routing boundary
- Decide the primary owner:
  - `frontend-ui-design` for production UI structure and implementation planning;
  - `design-system` for token architecture and governance;
  - `ui-ux-creative-coding` for motion/polish once direction is set.

## Round 4: Constraints
- Capture required accessibility baseline, timeline pressure, and platform constraints.

## Round 5: Success criteria
- Define measurable checks for the immediate handoff.

## Round 6: Confirmation
- Summarize confirmed facts.
- List assumptions.
- Ask:
  - "Does this capture it well enough for me to build?"
  - "Anything to add or change before I build it?"
