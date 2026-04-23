# Extended guidance

## Anti-Patterns

- **Discovery mismatch**: description lacks trigger keywords or “use when …” contexts.
- **Monolith SKILL.md**: huge docs embedded directly instead of `Infrastructure/references/`.
- **Rigid template trap**: forces slot-filling and produces generic output.
- **Checklist without rationale**: steps with no principles, making the skill brittle.
- **Untested scripts**: scripts included but never executed to confirm behavior.

- **Workflow-in-description trap**: description becomes a step-by-step recipe, so the model shortcuts and never reads the body. Keep discovery keywords in the description; keep workflows in the body/references.
- **Absolute-path coupling**: hardcoded machine paths (`/home/...`, `~/.codex/...`) instead of portable, repo-relative paths.
- **Over-questioning**: asking broad or excessive clarifying questions instead of proceeding with reasonable defaults + a small number of targeted questions.
- **Unsafe automation**: scripts that assume network access, exfiltrate secrets, or run destructive commands without explicit approval.

## Variation

If a created skill produces repeated artifacts (reports, templates, PR descriptions), prevent “samey” output:
- Vary structure, depth, and examples based on context.
- Name 2–3 dimensions that must vary (tone, outline, level of detail).
- Link to `Infrastructure/references/variation-patterns.md` when needed.

## Examples

### Create a new skill (router style)

**User prompt:** "Create a Codex skill for reviewing API security changes in PRs."

**Expected outcome:** a `review-api-security/` skill folder with a trigger-rich description, a short core workflow in `SKILL.md`, deeper guidance in `Infrastructure/references/`, and `Infrastructure/references/evals.yaml` with pressure-test prompts.

## Codex Skill Compatibility

If targeting both systems:
- Prefer the portable subset (see `Infrastructure/references/portable-skills.md`).
- Avoid platform-specific tools/flags in the core workflow; isolate them behind scripts or per-platform references.
