---
description: Analyze a Stitch project and synthesize its design system into a .stitch/DESIGN.md file.
---

# Workflow: Generate .stitch/DESIGN.md

Create a "source of truth" for your project's design language. See also: the dedicated `design-md` skill for a standalone version of this workflow.

## Retrieval

1. **Project lookup**: Use `list_projects` to find the target `projectId`.
2. **Screen lookup**: Use `list_screens` to find representative screens (e.g., "Home", "Main Dashboard").
3. **Metadata fetch**: Call `get_screen` for the target screen to get `screenshot.downloadUrl` and `htmlCode.downloadUrl`.
4. **Asset download**: Use `read_url_content` to fetch the HTML source.

See `references/tool-schemas.md` for exact call formats.

## Analysis & synthesis

1. **Identity** — Capture Project Title and numeric Project ID.
2. **Atmosphere** — Analyze HTML and screenshot for "vibe" (e.g., "Airy," "Professional," "Vibrant").
3. **Color palette** — Extract exact hex codes and assign functional roles.
4. **Geometry** — Convert Tailwind/CSS values into descriptions (e.g., `rounded-full` → "Pill-shaped").
5. **Depth** — Describe shadow styles and layering.

## Output: `.stitch/DESIGN.md`

```markdown
# Design System: [Project Title]
**Project ID:** [Insert Project ID Here]

## 1. Visual Theme & Atmosphere
(Description of mood and aesthetic philosophy)

## 2. Color Palette & Roles
(Descriptive Name + Hex Code + Role)

## 3. Typography Rules
(Font families, weights, and usage)

## 4. Component Stylings
* **Buttons:** Shape, color, behavior
* **Containers:** Roundness, elevation

## 5. Layout Principles
(Whitespace strategy and grid alignment)
```

## Best practices
- Always include hex codes in parentheses.
- Use natural language names ("Deep Ocean Blue") not just technical values.
- Explain *why* each element is used (functional role).
