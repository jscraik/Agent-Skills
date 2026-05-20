# Generated Artifact Policy

Use this reference only when a Skill Factory task explicitly asks for generated media, visual assets, concrete artifact files, or persistence proof.

## Contract

- Do not call generated media complete from prompt text alone.
- Do not claim an artifact exists unless a file path was written and checked.
- Record artifact availability as `yes`, `no`, `blocked`, or `unknown` with evidence.
- If generation is available but persistence is blocked, report the exact tool, path, or approval boundary before claiming completion.
- Keep review-only media under `.harness/media/`; keep reusable skill assets under the skill package only when they are part of runtime behavior.

## Minimum Proof

Return the file path, generation tool or blocker, validation performed, and any residual risk. Avoid broad artifact bookkeeping for text-only skill edits.
