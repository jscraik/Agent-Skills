# Upstream Frontend Design Reference

Read when:
- you want the full imported compound-engineering `frontend-design` doctrine rather than the deconflicted local wrapper;
- you need the original module structure, anti-pattern list, or visual verification cascade;
- you are reviewing whether the local wrapper preserved the upstream intent faithfully.

Source:
- Upstream path: `Plugins/compound-engineering/skills/frontend-design/SKILL.md`
- Pinned ref: `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`
- URL: `https://github.com/EveryInc/compound-engineering-plugin/blob/0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b/Plugins/compound-engineering/skills/frontend-design/SKILL.md`

Preservation note:
- This reference intentionally keeps the high-value upstream guidance that would be too duplicative inside the installed wrapper skill.
- The local `frontend-design` skill is a routing layer over this reference plus the stronger local frontend skill graph.

## Preserved upstream content

### Frontmatter

```yaml
name: frontend-design
description: Build web interfaces with genuine design quality, not AI slop. Use for any frontend work - landing pages, web apps, dashboards, admin panels, components, interactive experiences. Activates for both greenfield builds and modifications to existing applications. Detects existing design systems and respects them. Covers composition, typography, color, motion, and copy. Verifies results via screenshots before declaring done.
```

### Core lifecycle

```text
Detect context -> Plan the design -> Build -> Verify visually
```

### Authority hierarchy

1. Existing design system or codebase patterns
2. User's explicit instructions
3. Skill defaults

### Layer 0: Context detection

Look for:
- design tokens and CSS variables
- component libraries
- CSS frameworks
- typography imports
- color palette and theme files
- animation libraries
- spacing and layout patterns

Mode classification:
- existing system
- partial system
- greenfield
- ambiguous

### Layer 1: Pre-build planning

Write three short statements before coding:
1. visual thesis
2. content plan
3. interaction plan

### Layer 2: Design guidance core

Covered upstream themes:
- typography defaults
- color and theme defaults
- composition defaults
- motion defaults
- accessibility defaults
- imagery defaults

### Context modules

The upstream skill defines:
- Module A: Landing Pages and Marketing
- Module B: Apps and Dashboards
- Module C: Components and Features

### Hard rules and anti-patterns

Default against:
- generic SaaS card-grid first impressions
- purple-on-white bias
- overused default fonts in greenfield work
- cluttered heroes
- repetitive mood copy
- decorative gradients substituting for real visual content

Always avoid:
- prompt language leaking into UI
- broken contrast
- missing focus states
- semantic div soup

### Litmus checks

Examples preserved from upstream:
- Is the brand or product unmistakable in the first screen?
- Is there one strong visual anchor?
- Can the page be understood by scanning headlines only?
- Are cards actually necessary where they are used?
- Does motion improve hierarchy or atmosphere?
- Does the new work match the existing design system?

### Visual verification

Preferred cascade:
1. existing project browser tooling
2. browser MCP tools
3. `agent-browser`
4. mental review fallback with an explicit note

### Creative energy

The upstream skill explicitly encourages a bold aesthetic commitment for greenfield work and warns against generic AI output.

## Local adaptation summary

The local wrapper preserves the upstream intent while changing the routing behavior:
- use local frontend skills for execution depth and deconfliction;
- keep this reference as the full doctrine source;
- preserve screenshot-first verification and context detection as non-negotiable quality bars.
