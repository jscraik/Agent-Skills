# Design Critique

A systematic critique workflow for interface quality. Start with noticing, then diagnose structure/behavior/visuals, and end with actionable opportunities grounded in user impact.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Input Modes](#input-modes)
- [Critique Workflow](#critique-workflow)
- [What to Notice](#what-to-notice)
- [Facets of Quality Lens](#facets-of-quality-lens)
- [Output Format](#output-format)
- [Voice Rules](#voice-rules)
- [Severity Guide](#severity-guide)

## When to Use

Trigger on: `critique`, `review`, `feedback`, `audit`, `polish`, `redesign`, `what feels off`, or any screenshot/component/page quality review request.

Use this for **improving an existing interface**.
If the user needs fundamentally different concepts first, run [conceptual-range.md](conceptual-range.md) before deep critique.

## Input Modes

1. **Image / screenshot (primary)** — critique what is actually visible.
2. **File path (secondary)** — infer layout and interaction from code; mark all inferred points.
3. **Live URL (tertiary)** — critique captured content and any supplied screenshots.

## Critique Workflow

### Step 0 — Context Frame
Capture:
- what this screen is
- who it serves
- emotional context (stressful, routine, high-stakes, playful)
- whether the interface is being assessed with real/representative data

### Step 1 — Noticing Pass (no fixes yet)
Log observations only:
- where attention lands first
- where users might hesitate
- where expectations break
- where emotional tone shifts
- what appears missing

No prescriptions in this step.

### Step 2 — First Impressions
One direct paragraph on gut reaction. Be specific and decisive.

### Step 3 — Multi-Lens Audit
Audit in this order:
1. **Visual design** — color intent, typography, spacing/alignment, shadows/strokes, icon consistency
2. **Interface design** — focus mechanism, progressive disclosure, density, feedback, redundancy
3. **Consistency & conventions** — pattern reuse, platform conventions, cohesive design language
4. **User context** — does this reduce stress and build trust for this task?

For each issue:
> **[Issue]** — [specific observation]. [impact]. [better direction].

### Step 4 — Uncommon Care Scan
Identify details users remember:
- edge cases
- error states
- recovery states
- small moments where care can exceed expectation

Ask: “Where are we currently at good enough, and what would uncommon care look like?”

### Step 5 — Less, but Better Pass
Find unnecessary complexity:
- remove redundant UI elements
- reduce competing styles
- simplify copy and affordances

Prioritize fewer, clearer, better-executed elements over additional flourish.

### Step 6 — Recommendation Pack
Deliver ranked opportunities with rationale and expected user impact.

### Step 7 — Industry Standard Gap
Briefly classify current state:
- below baseline
- at baseline
- above baseline

Then specify what must change to reach baseline before innovation.

## What to Notice

Use these prompts:
- **Moments of hesitation** — uncertainty about what happens next
- **Expectation gaps** — mismatch between user mental model and UI response
- **Emotional shifts** — where confidence drops or delight appears
- **Missing elements** — what users look for but cannot find
- **Assumptions** — hidden expectations the interface places on users
- **Perceived craft** — cheap vs crafted visual/interaction signals
- **Felt quality** — fast vs sluggish, durable vs fragile

## Facets of Quality Lens

When useful, ask the user to define 3–5 facets (e.g., crafted, fidgetable, authentic, expansive, inventive), then:
1. score each facet (1–5 or 1–10)
2. identify weakest facet
3. focus next iteration on improving that facet

Use facets to make critique and planning explicit, not subjective.

## Output Format

```md
## Context
[screen purpose + user + emotional context]

## Noticing Log
[specific observations only]

## First Impressions
[one direct paragraph]

## Visual Design
[issue -> impact -> direction]

## Interface Design
[issue -> impact -> direction]

## Consistency & Conventions
[issue -> impact -> direction]

## User Context
[empathy + cognitive/emotional load]

## Uncommon Care Opportunities
[2-5 high-leverage edge/details improvements]

## Less, but Better Reductions
[what to remove/simplify]

## Top Opportunities
[ranked 3-5 with expected impact]

## Industry Standard Gap
[below/at/above baseline + required baseline fixes]
```

## Voice Rules

### Be
- specific and measurable
- factual before evaluative
- decisive and direct
- impact-aware and constructive

### Do not
- hedge (`maybe`, `perhaps`)
- give vague feedback
- prescribe without reasoning
- add empty praise padding

## Severity Guide

Prioritize findings:
1. **Structural** — information architecture, mental model, decision flow
2. **Behavioral** — feedback loops, transitions, response clarity
3. **Visual** — typography, spacing, color, shadows, polish

Structural and behavioral concerns outrank visual polish.
