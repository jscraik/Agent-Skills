# Linear Decision Capture

Jamie's projects use Linear, not ADRs, as the default durable memory for architecture decisions.

## When To Capture

Capture a decision only when all three are true:

- **Hard to reverse**: changing later has meaningful cost.
- **Surprising without context**: a future reader would wonder why the code is shaped this way.
- **Real trade-off**: there were plausible alternatives and one was chosen for specific reasons.

Skip capture for obvious, reversible, or purely mechanical choices.

## Where To Capture

1. Update the current Linear issue or workpad when one exists.
2. Create a small Linear follow-up issue when the decision is durable but no current issue exists.
3. If Linear is unavailable, include the note in chat and mark it as not persisted.

Do not create ADR files from this skill unless the user explicitly asks or a binding repo instruction requires ADRs.

## Linear Note Template

```md
## Architecture decision

Decision: {one sentence}
Context: {why this came up now}
Why: {main reason}
Trade-off: {what we accepted}
Rejected options: {only the options worth remembering}
Impacted context/modules: {paths or CONTEXT.md terms}
Review trigger: {when this should be revisited, or "none known"}
```

## Rejected Candidate Template

Use this when the user rejects an architecture candidate for a load-bearing reason.

```md
## Rejected architecture option

Option: {short name}
Rejected because: {one sentence}
Do not re-suggest unless: {new condition that would change the decision}
Related files/context: {paths or terms}
```

## Closeout Requirements

Report one of:

- `Linear decision note: updated {issue id or link}`
- `Linear decision note: created {issue id or link}`
- `Linear decision note: not needed`
- `Linear decision note: not persisted - {reason}`
