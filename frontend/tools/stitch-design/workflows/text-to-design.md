---
description: Generate new screens from a text prompt using Stitch MCP.
---

# Workflow: Text-to-Design

Transform a text description into a high-fidelity design screen.

## Steps

### 1. Enhance the user prompt
Before calling any Stitch tool, apply the [Prompt Enhancement Pipeline](../SKILL.md#prompt-enhancement-pipeline):
- Identify platform (Web/Mobile) and page type.
- Incorporate existing `.stitch/DESIGN.md` tokens.
- Use specific design mappings from `references/design-mappings.md` and `references/prompt-keywords.md`.

### 2. Identify the project
Use `list_projects` to find the correct `projectId` if unknown.

### 3. Generate the screen
```json
{
  "projectId": "...",
  "prompt": "[Your Enhanced Prompt]",
  "deviceType": "DESKTOP"
}
```

### 4. Present AI feedback
Always show the text description and suggestions from `outputComponents` to the user.

### 5. Download design assets
Save to `.stitch/designs/`:
- `htmlCode.downloadUrl` → `.stitch/designs/{page}.html`
- `screenshot.downloadUrl` + `=w{width}` → `.stitch/designs/{page}.png`

See `references/tool-schemas.md` for the idempotency rule (check before overwriting).

### 6. Review and refine
- If the result needs adjustment, use the [edit-design](edit-design.md) workflow.
- Do NOT re-generate from scratch unless the fundamental layout is wrong.

## Tips
- Be structural: break pages into header, hero, features, footer.
- Specify colors with hex codes for precision.
- Set the tone explicitly: minimal, professional, vibrant.
