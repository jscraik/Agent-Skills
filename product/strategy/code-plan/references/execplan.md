# ExecPlan Guidance (Reference)

Use this reference when a task is multi-hour, high-risk, or explicitly requests PLANS.md / ExecPlan usage. Treat any repo-provided PLANS.md as the source of truth and override this reference if it differs.

## Trigger Conditions
- The user asks for an ExecPlan or mentions PLANS.md
- The task is a large feature, significant refactor, or multi-hour effort
- The plan must serve as a living document for long execution

## Core Requirements (summary)
- Make the plan self-contained for a novice reader.
- Keep it as a living document with Progress, Surprises & Discoveries, Decision Log, Outcomes & Retrospective.
- Define all terms of art in plain language.
- Specify observable acceptance criteria and validation steps.
- Record decisions and updates as work proceeds.

## Output Shape (summary)
- Prefer prose-first sections with concrete file paths, commands, and expected outputs.
- Use checklists only in the Progress section.
- If the ExecPlan is the only content of a file, omit outer code fences.

## Skeleton (summary)
- Title
- Purpose / Big Picture
- Progress (checkbox list with timestamps)
- Surprises & Discoveries
- Decision Log
- Outcomes & Retrospective
- Context and Orientation
- Plan of Work
- Concrete Steps
- Validation and Acceptance
- Idempotence and Recovery
- Artifacts and Notes
- Interfaces and Dependencies

## Reminder
If the repo includes PLANS.md, follow it exactly. If missing, ask the user whether to proceed with this reference or to add a PLANS.md file first.
