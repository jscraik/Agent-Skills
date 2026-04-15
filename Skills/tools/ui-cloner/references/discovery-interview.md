# UI Cloner Discovery Interview

Use this only when key inputs are missing.

## Round 1: Core target
- Question: "Which URL should we replicate?"
- Why this matters: the audit cannot begin without a concrete source target.

## Round 2: Replication mode
- Question: "Do you want fast inspiration, high-fidelity replication, or brand adaptation?"
- Why this matters: output detail and verification depth change significantly by mode.

## Round 3: Build context
- Question: "What implementation stack should the plan target (for example React + Tailwind, or HTML/CSS)?"
- Why this matters: component and token recommendations must match the destination stack.

## Round 4: Brand constraints
- Question: "Should we keep your existing brand tokens, or can we mirror the source look closely first?"
- Why this matters: this decides whether source fidelity or brand consistency is the dominant constraint.

## Round 5: Scope
- Question: "Do you want full-site replication guidance or just specific sections/pages?"
- Why this matters: reduces over-analysis and keeps deliverables bounded.

## Intuitive round-1 question
- "Which exact URL should we use as the source for replication?"
- Generic fallback phrasing for shared discovery harnesses: "What should this skill help you do?"

## Request user input mini-templates
- Target template: "We can start as soon as you share the exact source URL."
- Mode template: "Pick one: fast inspiration, high fidelity, or brand adaptation."
- Stack template: "Which build stack should the plan target (for example React + Tailwind or HTML/CSS)?"

## Copy paste payload examples
- Minimal payload:
```json
{
  "target_url": "https://example.com",
  "mode": "adaptation",
  "target_stack": "React + Tailwind"
}
```

- Detailed payload:
```json
{
  "target_url": "https://example.com",
  "mode": "high_fidelity",
  "target_stack": "Next.js + Tailwind",
  "brand_constraints": {
    "preserve_colors": true,
    "accessibility_target": "WCAG AA"
  },
  "page_scope": ["home", "pricing"]
}
```
