# Conceptual Depth

Take one chosen concept and iterate it through progressive quality levels until it reaches its practical ceiling.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Depth Spectrum](#depth-spectrum)
- [Workflow](#workflow)
- [Depth Tactics](#depth-tactics)
- [Project-Backed Depth Moves](#project-backed-depth-moves)
- [Copy-Ready Repo Snippet](#copy-ready-repo-snippet)
- [Benchmark Rule](#benchmark-rule)
- [Output Format](#output-format)

## When to Use

Use when users ask to:
- push a concept further
- refine/polish an existing direction
- make something feel world-class
- move beyond “good enough”

Use this after conceptual-range selection.

## Depth Spectrum

Model quality on a 1→10 spectrum:
- **1–3**: baseline functional draft
- **4–6**: coherent quality and polish
- **7–10**: uncommon care, refined edge cases, distinctive craft

Goal: identify current level, then define concrete moves to the next level.

## Workflow

1. **State current level**
   - What level is this now, and what evidence supports that score?

2. **Define target level**
   - What “better” means here (clarity, responsiveness, durability, delight, trust).

3. **Plan iterative passes**
   - Pass A: fix obvious gaps
   - Pass B: improve consistency and interaction quality
   - Pass C: add uncommon-care details and edge-case excellence

4. **Run critique loop**
   - self-critique or external critique every pass
   - update level score after each pass

5. **Stop or pivot**
   - stop if marginal gain is low
   - pivot back to conceptual-range if core concept limits quality

## Depth Tactics

- **Zoom in** on one component and make it exceptional
- **Remove what is unessential** (“less, but better”)
- **Name what is not working** before solving
- **Reference exceptional examples** to expose gaps
- **Generate more variants** when stuck
- **Focus edge and error states** for uncommon care
- **Layer modalities** when relevant (visual + motion + sound/haptics)

## Project-Backed Depth Moves

When translating depth recommendations into implementation, use at least one concrete pattern family:

1. **DialKit depth moves** (`joshpuckett/dialkit`)
   - expose live tuning controls before finalizing constants
   - promote spring parameters (`visualDuration`, `bounce`) to named/tunable configuration
   - keep action callbacks explicit (`onAction`) for testable behavior changes

2. **Bloom depth moves** (`joshpuckett/bloom`)
   - upgrade to compound composition for clarity (`Root`, `Container`, `Trigger`, `Content`, `Item`)
   - harden controlled/uncontrolled parity (`open`, `onOpenChange`, `defaultOpen`)
   - refine morph geometry with explicit direction/anchor/offset reasoning

3. **Pasito depth moves** (`joshpuckett/pasito`)
   - move repeated timing/sequence logic into headless hooks
   - replace fixed style constants with CSS custom properties
   - enforce reduced-motion and keyboard semantics as depth-level quality gates

Reference index: `references/project-code-references.md`.

## Copy-Ready Repo Snippet

For implementation-oriented depth outputs, always include this compact block near the end:

```md
## Repo Pattern to Borrow
- Source: [DialKit|Bloom|Pasito] ([file-or-readme reference])
- Why now: [single sentence tied to quality level jump]
- Apply in next pass: [smallest concrete implementation step]
```

Keep this block to 3 bullets max.

## Benchmark Rule

Before claiming excellence:
1. confirm the concept meets platform/category baseline quality
2. then push beyond baseline with distinctive refinements

Baseline first, innovation second.

## Output Format

```md
## Current State
[current level score + evidence]

## Target State
[desired level + user-facing quality goals]

## Iteration Plan
- Pass A:
- Pass B:
- Pass C:

## Uncommon Care Opportunities
[specific moments/details to elevate]

## Less, but Better Reductions
[elements to remove or simplify]

## Industry Standard Check
[what baseline this now meets]

## Validation Signals
[how we know this reached the next level]

## Repo Pattern to Borrow
- Source: [DialKit|Bloom|Pasito] ([file-or-readme reference])
- Why now: [single sentence tied to quality level jump]
- Apply in next pass: [smallest concrete implementation step]
```
