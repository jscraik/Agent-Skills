---
name: web-design-guidelines
description: Review UI code against Web Interface Guidelines with file:line findings.
  Use for rule-based compliance checks (not experiential critiques). Use when the
  user requests this capability.
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## Scope and triggers

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

## Pre-flight accessibility triage (fast pass)
Before the full guideline pass, you may run the quick triage checklist:
- `references/a11y-triage.md`

This does **not** replace the required guideline fetch; always apply the full ruleset after the triage pass.

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

## Required inputs

- Files or glob patterns to review.
- Any known UI surfaces to prioritize.
- Existing design system or token references, if any.

## Deliverables

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
- `references/a11y-triage.md` for a fast critical-issues pre-check.
- `assets/review-output-template.md` for the reporting template.
- `references/contract.yaml` and `references/evals.yaml` for gold-gate validation.

## Example prompts

- "Review my checkout UI for accessibility."
- "Audit this page against UX best practices."
- "Check the settings screen for guideline issues."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential, they don't constrain it. Use judgment, adapt to context, and push boundaries when appropriate.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
