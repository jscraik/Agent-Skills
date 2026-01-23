---
name: app-store-release-notes
description: "Generate a comprehensive, user-facing changelog from git history since the last tag, then translate commits into clear App Store release notes.. Use when Creating App Store “What’s New” text from git history.."
---

# App Store Changelog

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview
Generate a comprehensive, user-facing changelog from git history since the last tag, then translate commits into clear App Store release notes.

## When to use
- Creating App Store “What’s New” text from git history.
- Summarizing release changes between tags or refs.
- Preparing user-facing release notes for submission.

## Inputs
- Git tag or ref range (or default to last tag).
- Any store character limits or formatting constraints.

## Outputs
- User-facing bullet list release notes.
- Optional title (if requested).

## Philosophy
- Prioritize user value over internal detail.
- Be precise and truthful; only ship what happened.
- Optimize for scanability and trust.

## Guiding questions
- What changed for users since the last release?
- Why does each change matter to the user?
- Is this change verifiable in the commit range?
- Is anything ambiguous or internal-only?

## Workflow

### 1) Collect changes
- Run `scripts/collect_release_changes.sh` from the repo root to gather commits and touched files.
- If needed, pass a specific tag or ref: `scripts/collect_release_changes.sh v1.2.3 HEAD`.
- If no tags exist, the script falls back to full history.

### 2) Triage for user impact
- Scan commits and files to identify user-visible changes.
- Group changes by theme (New, Improved, Fixed) and deduplicate overlaps.
- Drop internal-only work (build scripts, refactors, dependency bumps, CI).

### 3) Draft App Store notes
- Write short, benefit-focused bullets for each user-facing change.
- Use clear verbs and plain language; avoid internal jargon.
- Prefer 5 to 10 bullets unless the user requests a different length.

### 4) Validate
- Ensure every bullet maps back to a real change in the range.
- Check for duplicates and overly technical wording.
- Ask for clarification if any change is ambiguous or possibly internal-only.

## Output Format
- Title (optional): "What’s New" or product name + version.
- Bullet list only; one sentence per bullet.
- Stick to storefront limits if the user provides one.

## Constraints / Safety
- Redact secrets/PII by default.
- Do not invent features or exaggerate impact.
- Do not include internal-only changes.
- Redact sensitive or internal identifiers if present in commit text.

## Variation rules
- Vary grouping by release size (small: 3–5 bullets; large: themed sections).
- Vary tone by audience (consumer vs enterprise) and platform.
- Use different phrasing patterns to avoid repetitive bullets.

## Empowerment principles
- Empower stakeholders with traceable bullets mapped to commits.
- Empower reviewers with a short rationale for each inclusion.

## Anti-patterns to avoid
- Listing internal-only work as user-facing changes.
- Using vague claims like “performance improvements” without evidence.
- Exceeding store limits or adding marketing fluff.

## Example prompts
- “Generate App Store release notes since v1.2.3.”
- “Create a What’s New list from the last tag.”
- “Summarize user-facing changes between v2.0.0 and HEAD.”

## Resources
- `scripts/collect_release_changes.sh`: Collect commits and touched files since last tag.
- `references/release-notes-guidelines.md`: Language, filtering, and QA rules for App Store notes.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
