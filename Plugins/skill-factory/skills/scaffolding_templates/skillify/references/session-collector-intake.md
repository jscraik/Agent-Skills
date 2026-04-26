# Session Collector Intake

Read when: `skillify` is converting a completed conversation, run, or repeated agent workflow into a reusable skill package.

Use this intake to turn session evidence into stable skill behavior without copying raw transcripts into public skill files.

## Intake Boundary

- Use `skillify` to convert a selected, repeatable workflow into a skill.
- Use `skill-refactor` first when the user asks what happened across many sessions, which sessions matter, or whether a workflow should be merged, pruned, improved, or skillified.
- Do not make `skillify` responsible for broad session-history inventory.

## Evidence To Consume

Prefer bounded extracted evidence:

- user goal and repeated trigger language
- assistant procedure that actually worked
- commands or tools that are essential to the workflow
- validation gates that proved the result
- blockers and failure boundaries that future agents must respect
- examples of should-trigger and should-not-trigger user wording

Avoid:

- raw full transcripts
- private file trees in examples
- secrets, tokens, account identifiers, or personal content
- one-off debugging chatter that is not part of the reusable process

## Extraction Handoff

When another skill or collector provides session evidence, ask for or create a compact handoff:

```text
schema_version: 1
source: session-evidence
workflow_name: <plain-language workflow>
repeatability: <high|medium|low>
trigger_phrases:
  - <phrase>
required_inputs:
  - <input>
procedure:
  - <step>
validation:
  - <gate>
failure_boundaries:
  - <condition that should stop or redirect>
redactions:
  - <what was removed>
```

Proceed only when repeatability is at least medium and the reusable behavior is clearer than the incidental details of the session.

## Skill Drafting Rules

- Generalize from the extracted workflow, not from a single timestamp, branch name, or machine path.
- Preserve validation and safety gates that prevented failures.
- Move long examples or nuanced caveats into references and signpost them from `SKILL.md`.
- Add eval cases for happy, edge, failure, and pressure behavior based on the extracted evidence.
