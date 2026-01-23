---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
  short-description: UI review against Web Interface Guidelines
  tags: [ux, ui, accessibility, guidelines]
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## When to use

Use this skill when a user asks to:
- Review UI/UX for accessibility or design issues.
- Audit a site against best practices.
- Check a specific feature or flow for UI guidelines.

## Philosophy

Aim for accessible, predictable interfaces that reduce user error and cognitive load. Prefer clarity over novelty, and fix issues in order of user impact (accessibility → usability → visual polish). Use evidence from the UI and user flows, not personal taste. The guiding principle is to reduce friction in the primary user journey. Core principles: measure real friction, prioritize user safety, and avoid subjective aesthetic bias.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Variation

- Scope the review to the user’s target surfaces (checkout, onboarding, settings).
- If the repo uses a design system, map findings to existing tokens/components.
- If the UI is marketing-only, weight visual hierarchy and content clarity more heavily.
- Adapt findings to the product maturity (MVP vs enterprise) and adjust severity accordingly.
- Vary strictness based on compliance risk (public accessibility requirements vs internal tools).

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## Inputs

- Files or glob patterns to review.
- Any known UI surfaces to prioritize.
- Existing design system or token references, if any.

## Outputs

- Findings in the `file:line` format required by the guidelines.
- A short summary of top issues by impact.
- A note when rules require user confirmation or product context.

## Constraints / Safety

- Do not change source files without explicit approval.
- Avoid reporting unverified issues as violations.
- Redact secrets, tokens, and private URLs from outputs.

## Procedure

1. Fetch the latest guidelines from the source URL.
2. Read the target files or ask for file patterns.
3. Apply all guideline rules and capture file:line findings.
4. Summarize top issues by impact.

## Validation

- Confirm guidelines were fetched before analysis.
- Fail fast: stop at the first failed check and fix before continuing.
- See `references/contract.yaml` (schema_version: 1) and `references/evals.yaml`.

## Anti-patterns

- Avoid skipping accessibility checks.
- Avoid reporting findings without file/line references.
- Avoid treating stylistic preferences as violations.
- Avoid proposing changes that conflict with the repo design system.
- Avoid blocking delivery for low-impact cosmetic issues.
- Avoid recommending UI changes that add net complexity without user benefit.

## Empowerment

- Ask for missing files/patterns before proceeding.
- Offer a focused review pass when scope is large.
- Suggest a phased review (critical issues first, polish later).

## References

- `references/checklist.md` for review order and reporting format.
- `references/sources.md` for guideline sources.
- `references/anti-patterns.md` for expanded pitfalls.
- `assets/review-output-template.md` for the reporting template.
- `references/contract.yaml` and `references/evals.yaml` for gold-gate validation.

## Example prompts

- "Review my checkout UI for accessibility."
- "Audit this page against UX best practices."
- "Check the settings screen for guideline issues."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential, they don't constrain it. Use judgment, adapt to context, and push boundaries when appropriate.
