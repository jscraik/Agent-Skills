# Bounded Subagent Support for ce-brainstorm

## Table of Contents

- [Approval gate](#approval-gate)
- [Research roles](#research-roles)
- [Fallback](#fallback)
- [Constraints](#constraints)

Read when: spawning internal research subagents during Phase 1.1 (Standard or Deep scope)

## Approval gate
Ask a short blocking approval question via the platform's blocking question tool (`AskUserQuestion`, `request_user_input`, or `ask_user`) before spawning subagents, unless the user has already explicitly approved delegation.

## Research roles

If approved, run these bounded internal subagents in parallel:

### repo-research-analyst

```text
"Find similar features, conventions, or patterns relevant to: <topic>
- Max 20 files, max 4 MB total read
- Return a <=400 word summary with file:line refs"
```

### learnings-researcher

```text
"Find prior learnings relevant to: <topic>
- Check .harness/memory/LEARNINGS.md first when it exists
- Then docs/solutions/ for directly relevant entries
- Return only directly relevant findings, <=200 words total"
```

## Fallback
If approval is not granted, the tool is unavailable, or subagents are unnecessary, perform the equivalent grounding serially in the main thread.

## Constraints
- Do not spawn subagents without user approval
- Keep research bounded to prevent context pressure
- Synthesize findings into the main thread before proceeding
