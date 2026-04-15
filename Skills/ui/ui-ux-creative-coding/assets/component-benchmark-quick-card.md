# Component Benchmark Quick Card

## Table of Contents
- [When to use](#when-to-use)
- [60-second flow](#60-second-flow)
- [Capture block (copy/paste)](#capture-block-copypaste)
- [Decision rules](#decision-rules)
- [Output line template](#output-line-template)

## When to use
Use this card when component choices are ambiguous and you need a fast, evidence-backed pattern decision.

## 60-second flow
1. Pick component (drawer/modal/popover/etc.).
2. Review at least 3 comparable systems in `component.gallery`.
3. Record baseline states + accessibility expectations.
4. Pick one default + one fallback.
5. State one explicit tradeoff and why.

## Capture block (copy/paste)
```md
Component:
Systems compared (>=3):
Shared baseline behaviors:
Accessibility expectations:
Motion expectations:
Stack-fit notes:
Recommended pattern:
Fallback pattern:
Tradeoff:
Why this choice:
```

## Decision rules
- Prefer composable patterns with strong a11y/state coverage.
- Prefer stack-fit (React/Tailwind/Radix/Tauri) over novelty.
- Prefer reduced-motion + keyboard parity by default.
- Reject patterns that increase complexity without measurable UX benefit.

## Output line template
`Chosen pattern: <x> over <y> because <stack-fit + a11y + tradeoff rationale>.`
