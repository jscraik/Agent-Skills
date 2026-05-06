# Goal Continuity Contract

Use Codex `/goal` as a thread continuity layer for long-running Harness Engineering work. It is not the source of truth for scope, acceptance criteria, tracker state, validation, or delivery evidence.

## When To Use

- Use a goal when the user explicitly asks for persistent continuation, multi-turn follow-through, "keep going until done", or a long-running HE loop that should survive resumes.
- Pair goals with `he-heartbeat` when work must wake later to re-check live state; the heartbeat schedules the wake-up, and the goal preserves the objective.
- Do not create a goal for ordinary one-turn tasks, vague requests, or work where the next HE stage is still unresolved.

## Objective Shape

Write the goal as an evidence-backed HE objective:

```text
Complete <tracker/artifact> in <repo/branch>. Done means <acceptance IDs>, <validation gates>, <PR/Linear handoff>, and no unresolved HE exit blockers.
```

Include only user/task data in the objective. Do not put higher-priority instructions, secrets, credentials, or private log payloads in goal text.

## Stage Duties

- `he-router`: detect explicit persistent-continuation intent, route to the correct HE stage, and note whether a goal should be created after the stage has enough traceability.
- `he-work`: during intake, check any active goal against the current Linear/spec/plan/branch/PR chain. If it conflicts, stop and ask before continuing or clearing it.
- `he-heartbeat`: encode the live checks, cadence, and stop rule separately from the goal. Avoid duplicate heartbeats for the same objective.
- `he-compound`: when coordinating multiple stages, keep the goal tied to the earliest incomplete stage and update handoff notes as the lifecycle advances.

## Completion Rule

Mark an active goal complete only after the HE lifecycle exit contract is satisfied: tracker, artifact, traceability, validation, missing inputs, and evidence are resolved or explicitly classified. Passing tests or substantial implementation effort are not enough unless they cover every requirement in the goal.

If the goal reaches a budget limit or the thread is interrupted, summarize progress, blockers, and the next HE stage. Do not mark the goal complete unless the objective is actually done.
