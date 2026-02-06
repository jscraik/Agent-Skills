# File update rules (when a wrapper targets a document)

When updating a document in-place:

- Preserve the original structure.
- Prefer **append** over rewrite.
- Add one clearly labeled section:
  - `## Interview Insights` (fresh mode), or
  - `## Delta Insights` (enhancement mode)
- Never inject prose into code files by default; write to a sidecar doc instead.

# Defaults Profile hook (recommended)

If `@DEFAULTS.md` or a user profile exists, treat it as default answers for:

- scope bias (minimal vs refactor)
- correctness vs speed
- testing expectations
- compatibility targets
- rollout posture

Only ask about these if the current task conflicts with defaults.
