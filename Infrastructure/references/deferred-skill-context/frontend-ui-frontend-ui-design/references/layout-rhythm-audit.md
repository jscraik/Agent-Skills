# Layout Rhythm Audit

## Table of Contents
- [Purpose](#purpose)
- [Use this when](#use-this-when)
- [Audit pass](#audit-pass)
- [Improvement playbook](#improvement-playbook)
- [Anti-pattern guardrails](#anti-pattern-guardrails)
- [Verification checks](#verification-checks)

## Purpose
Provide a deterministic layout and spacing review path when a UI feels crowded, monotonous, or structurally weak.

## Use this when
- The user reports spacing inconsistency, weak hierarchy, or alignment problems.
- A page looks generic despite acceptable color/typography choices.
- Card grids are repetitive and scanning feels slow.
- Density feels too cramped or too sparse for the content type.

## Audit pass
### 1) Spacing consistency
- Check whether spacing uses a defined scale or arbitrary values.
- Confirm related elements are grouped tightly while section groups are clearly separated.
- Flag repeated equal spacing that removes rhythm.

### 2) Hierarchy clarity
- Run a squint test: with reduced visual detail, is the primary action still obvious?
- Verify whitespace and proximity communicate priority before adding extra styling.
- Confirm the most important content is identifiable within a short scan.

### 3) Structural composition
- Confirm there is a clear layout system (grid/flex patterns) instead of ad hoc placement.
- Check alignment coherence across headings, actions, and supporting content.
- Detect repetitive card templates that flatten hierarchy.

### 4) Rhythm and density
- Identify where spacing should be tight versus generous.
- Match density to content intent:
  - data-dense product surfaces: tighter, systematic spacing;
  - narrative or marketing surfaces: more breathing room.

## Improvement playbook
- Use a consistent spacing scale and token-referenced values.
- Prefer `gap` for sibling spacing in modern layout containers.
- Use flexbox for 1D arrangements and grid for 2D coordination.
- Break monotony by varying section composition and content emphasis.
- Treat cards as optional containers, not default layout units.
- Build hierarchy with space and weight first; use ornament only when needed.

## Anti-pattern guardrails
- Avoid arbitrary spacing values outside the chosen scale.
- Avoid equal spacing everywhere; rhythm requires contrast.
- Avoid stacking nested cards for hierarchy.
- Avoid forcing CSS grid where a simpler flex pattern is clearer.

## Verification checks
- Squint test passes with clear primary and secondary grouping.
- Spacing and alignment are consistent across similar elements.
- Rhythm alternates deliberately between tight and generous zones.
- Density fits the task and does not harm readability.
