---
name: design-md
description: Analyze Stitch projects and synthesize a semantic design system into DESIGN.md files. Use when the user wants to capture an existing Stitch project's visual language into a reusable design system document.
allowed-tools:
  - "stitch*:*"
  - "Read"
  - "Write"
  - "web_fetch"
metadata:
  skill-type: scaffolding_templates
---

# Stitch DESIGN.md

Analyze a Stitch project and synthesize its visual language into a `.stitch/DESIGN.md` source-of-truth document.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Retrieval workflow](#retrieval-workflow)
- [Analysis and synthesis](#analysis-and-synthesis)
- [Output format](#output-format)
- [Best practices](#best-practices)
- [References](#references)
- [See Also](#see-also)

## When to use
- The user wants to capture an existing Stitch project's design language.
- A multi-screen project needs consistent generation prompts.
- You need a `.stitch/DESIGN.md` before running `stitch-loop`.

## Required inputs
- A Stitch project with at least one designed screen.
- Access to the Stitch MCP Server.
- Project ID (optional — can be discovered via `list_projects`).

## Deliverables
- `.stitch/DESIGN.md` following the prescribed output format.
- Exact color hex codes, component shape descriptions, and typography rules.

## Failure mode
- If no Stitch project exists, stop and guide the user to create one first.
- If the screen HTML cannot be fetched, report the exact tool failure and stop.
- If the project lacks meaningful design data, note this and produce a minimal template.

## Retrieval workflow

1. **Namespace discovery** — Run `list_tools` to find the Stitch MCP prefix (e.g., `mcp_stitch:`).
2. **Project lookup** — Call `[prefix]:list_projects` with `filter: "view=owned"` if Project ID is unknown. Extract the numeric ID from the `name` field (e.g., `projects/13534454087919359824`).
3. **Screen lookup** — Call `[prefix]:list_screens` with the numeric `projectId`. Identify the most representative screen (e.g., "Home", "Landing Page").
4. **Metadata fetch** — Call `[prefix]:get_screen` with `projectId` and `screenId` to get `screenshot.downloadUrl`, `htmlCode.downloadUrl`, width, height, `deviceType`, and `designTheme`.
5. **Asset download** — Use `web_fetch` or `read_url_content` to download the HTML source from `htmlCode.downloadUrl`. Parse Tailwind classes, custom CSS, and component patterns.
6. **Project theme** — Call `[prefix]:get_project` with the full resource name (`projects/{id}`) to get the `designTheme` object (color mode, fonts, roundness, custom colors).

## Analysis and synthesis

### 1. Extract project identity
Capture Project Title and the numeric Project ID.

### 2. Define atmosphere
Evaluate the screenshot and HTML structure for overall "vibe." Use evocative adjectives (e.g., "Airy," "Dense," "Minimalist," "Utilitarian").

### 3. Map color palette
For each key color:
- A descriptive natural-language name (e.g., "Deep Muted Teal-Navy")
- The exact hex code in parentheses (e.g., "#294056")
- Its functional role (e.g., "Used for primary actions")

### 4. Translate geometry
Convert CSS values into physical descriptions:
- `rounded-full` → "Pill-shaped"
- `rounded-lg` → "Subtly rounded corners"
- `rounded-none` → "Sharp, squared-off edges"

### 5. Describe depth
Explain shadow presence and quality: "Flat," "Whisper-soft diffused shadows," "Heavy, high-contrast drop shadows."

## Output format

```markdown
# Design System: [Project Title]
**Project ID:** [Insert Project ID Here]

## 1. Visual Theme & Atmosphere
(Description of mood, density, and aesthetic philosophy.)

## 2. Color Palette & Roles
(List colors by Descriptive Name + Hex Code + Functional Role.)

## 3. Typography Rules
(Font family, weight usage for headers vs. body, letter-spacing character.)

## 4. Component Stylings
* **Buttons:** (Shape description, color assignment, behavior).
* **Cards/Containers:** (Corner roundness description, background color, shadow depth).
* **Inputs/Forms:** (Stroke style, background).

## 5. Layout Principles
(Whitespace strategy, margins, and grid alignment.)
```

## Best practices
- **Be descriptive:** Avoid "blue." Use "Ocean-deep Cerulean (#0077B6)."
- **Be functional:** Explain what each design element is used for.
- **Be precise:** Include exact hex codes and pixel values in parentheses.
- **Be consistent:** Same terminology throughout.
- **Reference the guide:** Use language from the Stitch Effective Prompting Guide.

## References
- See Also: `stitch-loop`, `enhance-prompt`, `stitch-design`

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-loop]] | Run iterative page generation after `DESIGN.md` is established |
| [[enhance-prompt]] | Enhance generation prompts using the tokens from `DESIGN.md` |
| [[stitch-design]] | Unified entry point combining design-md, enhance-prompt, and screen generation |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom → cause → do instead → check.
