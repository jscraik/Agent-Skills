# Figma Make best practices (from transcripts)

- Design hygiene first: use Auto Layout, semantic layer names, and real components before pasting frames.
- Make only sees pasted frames; paste up to three frames per prompt and split complex flows into separate prompts.
- Be explicit with constraints (states, interactions, data, breakpoints) for more consistent results; Make is not deterministic.
- Use Point-and-Edit for fast scoped changes; use “Go to source” for precise code edits.
- Use templates to standardize high-quality prototypes across teams and riff without rebuilding.
- Use “Copy as design layers” to move a Make prototype into Figma Design for deep visual edits.
- Use guidelines in the code panel (`guidelines.mmd`) to lock in system rules and constraints.
- Use MCP connectors (e.g., Notion/GitHub/Linear) to pull PRDs/specs as prompt context; set tool permissions (ask/auto/never).
- Prefer internal preview links for team sharing (respects Figma permissions); publish only when public access is intended.
- If using device features (camera/mic) in prototypes, call out privacy and permission implications.
