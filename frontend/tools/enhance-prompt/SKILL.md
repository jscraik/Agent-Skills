---
name: enhance-prompt
description: Transforms vague UI ideas into polished, Stitch-optimized prompts. Use when the user wants to improve a prompt before sending to Stitch — adding UI/UX keywords, design system context, and structured page sections for better generation results.
allowed-tools:
  - "Read"
  - "Write"
metadata:
  skill-type: scaffolding_templates
---

# Enhance Prompt for Stitch

Transform rough or vague UI generation ideas into polished, optimized prompts that produce better results from Stitch.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Enhancement pipeline](#enhancement-pipeline)
- [Output options](#output-options)
- [References](#references)
- [See Also](#see-also)

## When to use
- The user wants to polish a UI prompt before sending to Stitch.
- A prompt produced poor or inconsistent results.
- A simple idea needs design-system context added.
- A vague concept needs structuring into an actionable prompt.

## Required inputs
- The user's rough UI description or failing prompt.
- Optional: access to `.stitch/DESIGN.md` in the current project.
- Optional: target output file (`next-prompt.md` for `stitch-loop`, or custom).

## Deliverables
- An enhanced, structured Stitch prompt ready for generation.
- Optionally written to `next-prompt.md` or a user-specified file.

## Failure mode
- If the input is too ambiguous to infer platform or page type, ask one clarifying question before enhancing.
- Do not over-design: if the user wants simple, match that intent.

## Enhancement pipeline

### Step 1: Assess the input

| Element | Check for | If missing |
|---------|-----------|------------|
| **Platform** | "web", "mobile", "desktop" | Add based on context or ask |
| **Page type** | "landing page", "dashboard", "form" | Infer from description |
| **Structure** | Numbered sections/components | Create logical page structure |
| **Visual style** | Adjectives, mood, vibe | Add appropriate descriptors |
| **Colors** | Specific values or roles | Add design system or suggest |
| **Components** | UI-specific terms | Translate to proper keywords — see `references/KEYWORDS.md` |

### Step 2: Check for DESIGN.md

Look for `.stitch/DESIGN.md` in the current project.

**If DESIGN.md exists:** Read it and include the color palette, typography, and component styles as a "DESIGN SYSTEM (REQUIRED)" section.

**If DESIGN.md does not exist:** Append this note to the enhanced prompt:
```
---
💡 Tip: For consistent designs across multiple screens, create a DESIGN.md
file using the `design-md` skill. This ensures all pages share the same visual language.
```

### Step 3: Apply enhancements

**Add UI/UX keywords** — Replace vague terms with specific component names. See `references/KEYWORDS.md` for the full mapping table.

**Amplify the vibe** — Add descriptive adjectives: "modern" → "clean, minimal, with generous whitespace."

**Structure the page** — Organize into numbered sections:
```markdown
**Page Structure:**
1. **Header:** Navigation with logo and menu items
2. **Hero Section:** Headline, subtext, and primary CTA
3. **Content Area:** [Describe the main content]
4. **Footer:** Links, social icons, copyright
```

**Format colors** — Use: `Descriptive Name (#hexcode) for functional role`.

### Step 4: Format the output

```markdown
[One-line description of page purpose and vibe]

**DESIGN SYSTEM (REQUIRED):**
- Platform: [Web/Mobile], [Desktop/Mobile]-first
- Theme: [Light/Dark], [style descriptors]
- Background: [Color description] (#hex)
- Primary Accent: [Color description] (#hex) for [role]
- Text Primary: [Color description] (#hex)

**Page Structure:**
1. **[Section]:** [Description]
2. **[Section]:** [Description]
```

## Output options
- **Default:** Return the enhanced prompt as text for the user to copy.
- **`next-prompt.md`:** Write to `.stitch/next-prompt.md` for use with `stitch-loop`.
- **Custom file:** Write to the filename specified by the user.

## References
- Keywords and vibe descriptors: `references/KEYWORDS.md`
- Official Stitch prompting guide: https://stitch.withgoogle.com/docs/learn/prompting/

## See Also

| Skill | When to use together |
|---|---|
| [[design-md]] | Create `DESIGN.md` first so enhance-prompt can inject design tokens |
| [[stitch-loop]] | Pipe enhanced prompts into the baton loop for iterative page generation |
| [[stitch-design]] | Unified entry point that wraps enhance-prompt + screen generation |

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
