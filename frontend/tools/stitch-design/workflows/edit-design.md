---
description: Edit an existing design screen using Stitch MCP.
---

# Workflow: Edit-Design

Make targeted changes to an already generated design.

## Steps

### 1. Identify the screen
Use `list_screens` or `get_screen` to find the correct `projectId` and `screenId`. See `references/tool-schemas.md`.

### 2. Formulate the edit prompt
Be specific about what to change:
- **Location**: "Change the color of the [primary button] in the [hero section]..."
- **Visuals**: "...to a darker blue (#004080) and add a subtle shadow."
- **Structure**: "Add a secondary button next to the primary one with the text 'Learn More'."

### 3. Apply the edit
```json
{
  "projectId": "...",
  "selectedScreenIds": ["..."],
  "prompt": "[Your target edit prompt]"
}
```

### 4. Present AI feedback
Always show `outputComponents` text description and suggestions to the user.

### 5. Download updated assets
Download the updated HTML and screenshot to `.stitch/designs/`, overwriting previous versions.

### 6. Verify and repeat
If more polish is needed, repeat with a new specific prompt.

## Tips
- One edit at a time is often better than a long list of changes.
- Reference components with professional terms: "navigation bar", "hero section", "card grid".
- Use hex codes for precise color matching.
