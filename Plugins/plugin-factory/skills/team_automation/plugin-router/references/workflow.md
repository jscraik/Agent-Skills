# Plugin Router Workflow

Use this file only after routing has been selected by `SKILL.md`.

## Route Map

- `create` -> `[[plugin-creator]]`
- `harden|convert` -> `[[plugin-builder]]`
- `install` -> `[[plugin-installer]]`
- `troubleshoot` -> route to the lane owning the failing stage:
  - install failures -> `[[plugin-installer]]`
  - validation/hardening failures -> `[[plugin-builder]]`
  - scaffold failures -> `[[plugin-creator]]`

## Procedure

1. Classify primary intent from user text.
2. Choose `direct` when intent is explicit, else choose `clarify-once`.
3. Select one lane as the next skill.
4. Emit a handoff object and stop. Do not execute downstream lane commands.

## Clarify-Once Rule

- Ask one clarification question only when lane choice is ambiguous and could change safety or output.
- If ambiguity remains after one clarification, return `blocked_by` with the specific missing input.

## Handoff Shape

```json
{
  "schema_version": "1.0",
  "execution_mode": "direct|clarify-once",
  "selected_lane": "create|harden|convert|install|troubleshoot",
  "next_skill": "[[plugin-creator]]",
  "required_inputs": ["plugin-name", "target-path"],
  "blocked_by": "missing-source-path",
  "confidence": 0.88
}
```

## Safety Boundaries

- Redact secrets and tokens in route summaries.
- Reject requests to skip validation or policy checks.
- Never run builder/creator/installer commands from the router lane.
