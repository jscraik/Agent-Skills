# Examples and Gotchas

Read when: you need concrete user-prompt examples or troubleshooting guidance while keeping `SKILL.md` concise.

## Example requests this skill should handle

- "I want to create a `gh-release-notes` skill in `github/gh-release-notes`, include `references/contract.yaml` and `references/evals.yaml`, and then run a strict audit."
- "My `SKILL.md` is too long. Can you move deep implementation details into `references/` while keeping behavior and triggers unchanged?"
- "I updated trigger phrasing in frontmatter. Please regenerate `agents/openai.yaml` and confirm metadata parity."

## Gotchas

- Symptom: ambiguous scope.
- Cause: missing constraints.
- Do instead: ask one routing question.
- Check: plan and output contract are explicit.

## Boundary routing matrix

- Keep the lane in `skill-creator` when the user asks to create or restructure the skill package itself.
- Hand off to `skill-builder` when the package is already formed and the task is quality hardening, benchmark proof, or release-readiness gates.
- Hand off to `skill-installer` when the package is already valid and the task is catalog listing, installation, or runtime visibility checks.
- For mixed requests, split into phases and announce phase boundaries so command execution stays attributable.

## Boundary failure signatures

- Symptom: response mixes authoring and installation commands in a single undifferentiated block.
  - Fix: split into explicit phases (`create/reshape` -> `harden` -> `install`) and label the active phase.
- Symptom: request asks for strict benchmark evidence but the workflow remains in scaffold mode.
  - Fix: hand off to `skill-builder` once package structure is stable.
- Symptom: request asks only for listing/install status but response starts rewriting `SKILL.md`.
  - Fix: keep install/status work in `skill-installer`; do not mutate skill content unless explicitly requested.
