# Meta Modes

## Table of Contents
- [Goal](#goal)
- [Context compaction](#context-compaction)
- [Guardrail extract](#guardrail-extract)
- [Output checklist](#output-checklist)

## Goal
Handle workflow-support tasks that improve continuity or governance but are not backed by a prompt file in `codex/prompts/`.

## Context compaction
Choose this when:
- the conversation or execution state is bloated
- the next run needs a clean handoff
- the user wants a baton, continuation brief, or compact state summary

Output should include:
- current objective
- decisions already made
- active files or artifacts
- exact next step
- open risks or blockers
- explicit note that this is a meta-mode with no backing prompt file

## Guardrail extract
Choose this when:
- a failure, incident, or repeated confusion should become reusable guidance
- the user wants to turn a lesson into a prompt, agent, instruction, or rule update
- the main deliverable is a durable hardening recommendation

Output should include:
- source failure or lesson
- proposed durable change target, such as prompt, agent, AGENTS doc, or instruction file
- rationale for why the change belongs there
- validation or follow-up needed
- explicit note that this is a meta-mode with no backing prompt file

## Output checklist
Every meta-mode result should include:
- selected meta-mode
- rationale
- no-prompt-path note
- recommended files or systems to update next
- safeguards and validation gates
