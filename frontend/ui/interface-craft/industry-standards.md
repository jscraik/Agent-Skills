# Industry Standards

Benchmark interface quality against the implicit baseline users already carry from top products and platform defaults.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Core Principle](#core-principle)
- [Benchmark References](#benchmark-references)
- [Workflow](#workflow)
- [Benchmark Prompt Macros](#benchmark-prompt-macros)
- [Output Format](#output-format)

## When to Use

Use when users ask:
- “Is this good enough?”
- “Why does this feel amateur?”
- “How do we know where the bar is?”
- “What should we compare against?”

## Core Principle

Industry standard is the **floor**, not the goal.
Meet default platform/category expectations first, then innovate.

## Benchmark References

Use references in this order:

1. **Product/category peers** (closest direct comparison)
2. **Platform conventions** (web/iOS/Android desktop interaction norms)
3. **Component pattern libraries** for implementation grounding
   - include [component.gallery](https://component.gallery) when users ask for component-level benchmarks or inspiration

When using component galleries:
- borrow interaction patterns and quality bars, not visual cloning
- explain why a pattern matches the user’s context before recommending it

## Workflow

1. **Select comparison set**
   - pick relevant top products and platform defaults
   - add component-level references (for example component.gallery) when component architecture/polish is the focus
   - match category and device context

2. **Define baseline criteria**
   - clarity and hierarchy
   - interaction reliability/feedback
   - visual consistency
   - platform convention alignment

3. **Assess current interface**
   - where below baseline
   - where at baseline
   - where above baseline

4. **Recommend path**
   - fix below-baseline gaps first
   - then identify innovation opportunities

5. **Re-score after changes**
   - check if baseline is now met

## Benchmark Prompt Macros

Use these copy-ready prompts when component-level benchmarking is needed:

1. **Baseline benchmark prompt**
   - “Use interface-craft to benchmark this component against https://component.gallery. Identify where we are below baseline, at baseline, and above baseline. Recommend the top 3 adapted improvements for this codebase.”

2. **Pattern adaptation prompt**
   - “Find 2 relevant patterns on https://component.gallery for this interaction. Borrow behavior patterns only (not visual cloning), then map them to concrete React + CSS-variable implementation steps.”

3. **Range-to-depth benchmark prompt**
   - “Generate 3 structurally different directions inspired by component.gallery patterns, pick one to prototype first, and provide a repo-grounded implementation slice.”

4. **Quality gate prompt**
   - “Review this component against component.gallery-level quality and verify keyboard, ARIA, and prefers-reduced-motion behavior before suggesting polish tweaks.”

## Output Format

```md
## Baseline Context
[category + platform + reference set]

## Reference Notes
- [source + what pattern was borrowed]

## Current Gap Assessment
- Below baseline:
- At baseline:
- Above baseline:

## Priority Fixes to Reach Baseline
[ranked actions]

## Innovation Opportunities
[only after baseline items are covered]

## Re-evaluation Criteria
[how to verify improvement]
```
