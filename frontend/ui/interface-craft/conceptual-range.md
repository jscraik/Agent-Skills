# Conceptual Range

Generate broad, structurally different solution directions before committing to implementation depth.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Core Rule](#core-rule)
- [Workflow](#workflow)
- [Range Expansion Tactics](#range-expansion-tactics)
- [Project-Backed Range Moves](#project-backed-range-moves)
- [Copy-Ready Repo Snippet](#copy-ready-repo-snippet)
- [Output Format](#output-format)

## When to Use

Use when users ask for:
- alternatives or options
- concept exploration
- direction setting
- “we might be solving the wrong thing”

Use this before deep polish when confidence in the core concept is low.

## Core Rule

**Variants are not range.**
If all options are slight variations of one pattern, range has not been achieved.

Minimum bar: produce at least **3 structurally different concepts**.

## Workflow

1. **Frame the real job**
   - What outcome does the user actually need?
   - What assumption is driving the current approach?

2. **Capture the default instinct**
   - Document the first obvious solution.

3. **Expand breadth**
   - Generate 5–12 concepts rapidly.
   - Force structural variety (manual, automatic, guided, ambient, game-like, preset-driven, etc.).

4. **Select 3 distinct directions**
   - Keep directions that differ in interaction model, cognitive load, and user effort.

5. **Evaluate tradeoffs**
   - Pros/cons, risk, complexity, and user impact.

6. **Recommend next experiment**
   - Pick one direction to prototype first, with explicit reason.

## Range Expansion Tactics

- **Remove/add a constraint** — what if no screen? what if fully automatic?
- **Blend domains** — what if this behaved like a game/tool/appliance?
- **Invert the problem** — eliminate instead of choose; filter out instead of search in
- **Set arbitrary count** — force 5/10/20 ideas to break local minima
- **Optimize for a facet** — “what would a 10/10 crafted or inventive version look like?”

## Project-Backed Range Moves

When range exploration needs implementation realism, borrow at least one concrete pattern family:

1. **DialKit range moves** (`joshpuckett/dialkit`)
   - include one concept with live-tunable parameters as part of the interaction model
   - vary where controls live (embedded, floating, contextual) and how much agency users get

2. **Bloom range moves** (`joshpuckett/bloom`)
   - include one concept based on morphing trigger-to-content transitions
   - vary direction/anchor strategy to test different spatial mental models

3. **Pasito range moves** (`joshpuckett/pasito`)
   - include one concept that is tokenized via CSS variables and intentionally minimal in API
   - vary logic split between headless hooks and visual components

Reference index: `references/project-code-references.md`.

## Copy-Ready Repo Snippet

For implementation-oriented range outputs, include this compact block:

```md
## Repo Pattern to Borrow
- Source: [DialKit|Bloom|Pasito] ([file-or-readme reference])
- Why this direction: [single sentence tied to concept distinctiveness]
- Prototype first: [smallest concrete slice to test]
```

Keep this block to 3 bullets max.

## Output Format

```md
## Problem Frame
[job to be done + key assumptions]

## Default Path
[first obvious approach and why it is tempting]

## Concept Pool
[5-12 ideas in one-line form]

## Top 3 Structurally Different Directions
1) [direction] — [why distinct]
2) ...
3) ...

## Tradeoff Summary
[pros/cons, complexity, user impact]

## Recommended Next Prototype
[which direction to test first + success signal]

## Repo Pattern to Borrow
- Source: [DialKit|Bloom|Pasito] ([file-or-readme reference])
- Why this direction: [single sentence tied to concept distinctiveness]
- Prototype first: [smallest concrete slice to test]
```
