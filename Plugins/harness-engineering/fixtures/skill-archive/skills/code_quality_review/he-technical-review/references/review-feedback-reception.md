# Harness Engineering Review Feedback Reception

## Purpose
Apply technical rigor when receiving code-review feedback so implementation decisions are evidence-backed, not performative.

## Core principle
Verify before implementing. Ask before assuming.

## Response pattern

1. Read all feedback first.
2. Restate the technical requirement or ask for clarification.
3. Verify against codebase reality and existing tests.
4. Evaluate whether the suggestion is correct for this stack and architecture.
5. Respond with factual acknowledgment or evidence-backed pushback.
6. Implement validated items one at a time with targeted regression checks.

## Non-negotiable rules

- Do not implement unclear items.
- If any feedback item is unclear, stop and request clarification before implementation.
- Keep replies technical and direct; avoid performative gratitude/approval language.
- Treat external reviewer feedback as suggestions to test, not instructions to obey blindly.
- Escalate when feedback conflicts with user-approved architectural decisions.

## External reviewer verification checklist

- Is the suggestion technically correct for this codebase?
- Does it break existing behavior or compatibility requirements?
- Why does the current implementation exist?
- Does the suggestion hold across supported platforms and versions?
- Is there enough local evidence to verify, or should we investigate first?

If verification is incomplete, state the limitation and ask for direction.

## YAGNI check

When feedback asks for a "proper" or larger implementation:

1. Search for real usage.
2. If unused, propose removal or deferral.
3. If used, implement with minimal necessary scope.

## Pushback and correction protocol

Push back when suggestions are incorrect, unsafe, or out of scope. Use concrete evidence.

If pushback is wrong:
- state correction factually
- implement the validated fix
- avoid long apologies or defensive framing

## GitHub thread behavior

Reply to inline review comments in-thread, not as unrelated top-level comments.
