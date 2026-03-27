---
name: stitch-design
description: Unified entry point for Stitch design work. Use when the user wants to generate or edit UI screens via Stitch MCP — handles prompt enhancement, design system synthesis (.stitch/DESIGN.md), and high-fidelity screen generation/editing.
allowed-tools:
  - "StitchMCP"
  - "Read"
  - "Write"
metadata:
  skill-type: scaffolding_templates
---

# Stitch Design Expert

Unified entry point for all Stitch design work: prompt enhancement, design system synthesis, and screen generation or editing.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Workflow routing](#workflow-routing)
- [Prompt enhancement pipeline](#prompt-enhancement-pipeline)
- [References](#references)
- [See Also](#see-also)

## When to use
- The user wants to design a UI screen from a text description.
- The user wants to edit or refine an existing Stitch design.
- The user wants to create or update `.stitch/DESIGN.md`.
- You need a unified entry point combining prompt enhancement + Stitch MCP generation.

## Required inputs
- The user's design intent (text description, edit request, or design-md request).
- Access to Stitch MCP Server.
- Optional: existing `.stitch/DESIGN.md` for consistency.
- Optional: existing project ID (discoverable via `list_projects`).

## Deliverables
- Generated or edited Stitch screen assets in `.stitch/designs/`.
- Updated `.stitch/metadata.json` with screen IDs and project state.
- Optional: new or updated `.stitch/DESIGN.md`.

## Failure mode
- If Stitch MCP is unavailable, stop and report the tool failure.
- If project ID cannot be resolved, use `list_projects` before proceeding.
- If `.stitch/DESIGN.md` is missing, suggest running the `generate-design-md` workflow or the `design-md` skill.

## Workflow routing

Based on the user's request, select the appropriate workflow:

| User Intent | Workflow | Primary Tool |
|---|---|---|
| "Design a [page]..." | [`workflows/text-to-design.md`](workflows/text-to-design.md) | `generate_screen_from_text` |
| "Edit this [screen]..." | [`workflows/edit-design.md`](workflows/edit-design.md) | `edit_screens` |
| "Create/update .stitch/DESIGN.md" | [`workflows/generate-design-md.md`](workflows/generate-design-md.md) | `get_screen` + Write |

## Prompt enhancement pipeline

Before calling any Stitch generation or editing tool, enhance the user's prompt:

### 1. Analyze context
- **Project scope:** Maintain the current `projectId`. Use `list_projects` if unknown.
- **Design system:** Check for `.stitch/DESIGN.md`. If it exists, incorporate its tokens. If not, suggest the `generate-design-md` workflow.

### 2. Refine UI/UX terminology
See `references/design-mappings.md` to replace vague terms with precise design language.
- Vague: "Make a nice header"
- Professional: "Sticky navigation bar with glassmorphism effect and centered logo"

### 3. Structure the final prompt
```markdown
[Overall vibe, mood, and purpose of the page]

**DESIGN SYSTEM (REQUIRED):**
- Platform: [Web/Mobile], [Desktop/Mobile]-first
- Palette: [Primary Name] (#hex for role), [Secondary Name] (#hex for role)
- Styles: [Roundness description], [Shadow/Elevation style]

**PAGE STRUCTURE:**
1. **Header:** [Description of navigation and branding]
2. **Hero Section:** [Headline, subtext, and primary CTA]
3. **Primary Content Area:** [Detailed component breakdown]
4. **Footer:** [Links and copyright information]
```

### 4. Present AI insights
After any tool call, always surface the `outputComponents` (Text Description and Suggestions) to the user.

## References
- Tool schemas: `references/tool-schemas.md`
- Design mappings and vibe descriptors: `references/design-mappings.md`
- Prompting keywords: `references/prompt-keywords.md`
- Workflows: `workflows/text-to-design.md`, `workflows/edit-design.md`, `workflows/generate-design-md.md`

## See Also

| Skill | When to use together |
|---|---|
| [[design-md]] | Generate `.stitch/DESIGN.md` before iterative screen generation |
| [[enhance-prompt]] | Standalone prompt enhancement without screen generation |
| [[stitch-loop]] | Chain this skill's output into an autonomous multi-page build loop |
| [[stitch-react-components]] | Convert Stitch HTML output into React component files |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom → cause → do instead → check.
