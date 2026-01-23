---
name: product-design-review
description: "Deliver a complete, user-centered critique of a product or flow, identifying issues, risks, and improvements across the entire experience.. Use when When a user requests a UX/UI audit or heuristic review of a product.."
---

# Product Design Review

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Deliver a complete, user-centered critique of a product or flow, identifying issues, risks, and improvements across the entire experience.

## Philosophy
- Users optimize for progress, not features; reduce friction at decision points.
- Clarity beats cleverness; make the next action obvious.
- Trust is earned in small moments; avoid surprise and hidden costs.

## Pre-Review Questions
Ask only what is needed to avoid blocking:
- What is the product, target audience, and primary success metric?
- Which flow(s) should be reviewed (e.g., onboarding, purchase, search, settings)?
- What artifacts are available (screens, links, prototypes, analytics, support tickets)?
- Any constraints (platform, tech, brand, deadlines)?

## When to use
- When a user requests a UX/UI audit or heuristic review of a product.
- When the user wants onboarding, checkout, or core flow critique.
- When accessibility or content clarity reviews are requested.

## Platform Selection Rules
- If the experience runs in a browser, use the web reference.
- If the product is built in React or is OSS, also use the React/OSS reference.
- If multiple surfaces share a flow, evaluate each surface independently, then summarize cross-platform gaps.

## Review Workflow
1) Define scope and user segments
- Summarize the target users, environments, and constraints.
- Confirm the entry/exit points of the flow.

2) Map the user journey
- Outline each step the user takes and the system response.
- Note required inputs, decisions, and drop-off points.

3) Evaluate with a multi-lens audit
- Usability and clarity (labels, hierarchy, affordances, feedback)
- Accessibility and inclusivity (WCAG 2.2 AA expectations, platform conventions)
- Information architecture and navigation
- Content and microcopy (tone, clarity, error prevention)
- Visual design and consistency (spacing, color, typography, density)
- States and resilience (loading, empty, error, edge cases)
- Trust, privacy, and safety cues
- Performance and perceived speed (skeletons, progress, latency messaging)

4) Prioritize issues
- Rank by severity, frequency, and impact on goals.
- Call out quick wins vs. structural problems.

5) Provide solutions
- Suggest concrete fixes with rationale.
- Offer alternatives if trade-offs exist.

## Issue Taxonomy
Use consistent labels to keep the output actionable:
- Severity: blocker, high, medium, low
- Impact area: conversion, retention, task success, trust, accessibility, comprehension
- Evidence: screen reference, user step, heuristic violated, or data point (if provided)

## Output Format
- Brief context summary (1–3 bullets)
- Findings list (ordered by severity), each with:
  - Issue
  - Why it matters to users
  - Evidence (if available)
  - Recommendation
- Notable positives (optional, 1–3 items)
- Open questions / assumptions

## Usage Example (short)
Request: "Review the onboarding flow for our React web app; focus on usability and accessibility."
Output: Context summary, ordered findings with fixes, and a React component-focused summary for key screens.

## React Output Template (optional)
Use when the product is a React app and a concrete, component-focused summary is helpful:
- Route or page name
- Component or pattern
- Issue and user impact
- State handling (loading/empty/error)
- Accessibility note
- Recommendation

## OSS Output Template (optional)
Use when the product is open-source and adoption or contributor experience is critical:
- Entry point (README, install, first-run)
- Friction point
- User impact (drop-off, confusion, trust)
- Evidence (docs mismatch, setup steps, UX inconsistency)
- Recommendation

## Variation Rules
- Vary depth: quick scan for small flows, deeper pass for multi-step journeys.
- Vary output structure based on artifact type (screens vs. live product vs. analytics).
- Avoid repeating the same critique pattern across unrelated issues.

## Empowerment Principles
- Empower teams with multiple fix paths when trade-offs exist.
- Empower the team to choose the single next best action to unblock progress.
- Provide a learning question when evidence is missing so teams can validate.
- Surface team-owned decisions and empower them to pick the path forward.

## References
- For web reviews, use `references/heuristics-web.md`.
- For React or OSS context, use `references/react-and-oss.md`.
- For OSS adoption checks, use `references/oss-checklist.md`.

## Anti-Patterns to Avoid
- Generic advice not tied to specific UI or user steps
- Over-indexing on aesthetics while missing usability and accessibility
- Ignoring edge states, errors, and empty states
- Suggesting changes that violate stated constraints
- Treating opinions as facts without evidence
- Recommending large redesigns when small fixes solve the core issue
- Anti-pattern: proposing changes without validating user goals
- Anti-pattern: skipping accessibility and claiming usability success

## Quality Bar
- Tie every finding to a user outcome.
- Prefer concrete, implementable recommendations.
- Distinguish confirmed issues vs. assumptions when evidence is missing.

## Example prompts
- "Review our onboarding flow for usability and accessibility."
- "Audit the checkout experience and list top issues by severity."
- "Critique this OSS project’s first-run experience."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
