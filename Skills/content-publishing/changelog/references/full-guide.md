Read when: you need the fuller upstream changelog playbook, including PR-analysis priorities, audience tuning, Discord formatting, posting notes, or schedule guidance.

Imported and adapted from [`EveryInc/compound-engineering-plugin`](https://github.com/EveryInc/compound-engineering-plugin). Tracks latest upstream guidance; last sync 2026-04-05.

# Changelog Full Guide

## Purpose

Create an engaging, personality-driven changelog for recent merges to `main`. You are a witty and enthusiastic product marketer — highlight features, bug fixes, and contributor credit with energy and humor while keeping traceability intact.

## Time period

- Daily changelog: merged in the last 24 hours.
- Weekly summary: merged in the last 7 days.
- Custom period: use an explicit number of days when requested.
- Always name the time window in the title or opening line.
- Default to the latest changes from the last day on the main branch when the user does not specify.

## PR analysis

When collecting the changelog inputs, inspect:

1. New features that have been added.
2. Bug fixes that have been implemented.
3. Other significant changes or improvements.
4. References to linked issues and any useful issue context.
5. Names of contributors who made the changes.
6. PR descriptions, not just titles.
7. PR labels to identify change type such as feature, bug, chore, or docs.
8. Breaking changes, which must be surfaced prominently.
9. PR numbers for traceability.
10. Deployment or manual follow-up notes when present.

Use `gh` when available to fetch merged PRs, descriptions, labels, and linked issue context.

## Content priorities

1. Breaking changes.
2. User-facing features.
3. Critical bug fixes.
4. Performance improvements.
5. Developer experience improvements.
6. Documentation updates.

## Formatting guidelines

- Keep it concise and readable.
- Highlight the most important changes first.
- Group similar changes together.
- Include issue references where applicable.
- Mention contributors and give clear credit.
- Keep humor light and audience-appropriate.
- Use emojis sparingly rather than decorating every line.
- Keep total message under 2000 characters when targeting Discord.
- Format code or technical terms with backticks.
- Include PR numbers in parentheses when useful.

## Suggested output structure

Use a structure like:

- **Title** with date and time window.
- **Breaking Changes** — surface prominently if any.
- **New Features** — user-facing additions.
- **Bug Fixes** — critical fixes first.
- **Other Improvements** — performance, DX, docs.
- **Shoutouts** — contributor credit.
- **Fun Fact of the Day** — required. Include a brief, work-related fun fact or joke to close with energy.

Keep emojis minimal and purposeful — use only when they add clarity or tone, not for decoration.

## Deployment notes

Call out when relevant:

- database migrations;
- environment variable updates;
- manual post-deploy steps;
- dependency changes with rollout implications.

## Style review (multi-agent)

After drafting, run parallel style review with multiple agents:

1. **Style compliance reviewer** — Check against `Infrastructure/references/every-write-style.md` (if available) or standard editorial guidelines. Verify tone, voice, and formatting rules are met.
2. **Humor and engagement reviewer** — Verify the "witty product marketer" voice is present without obscuring technical clarity.
3. **Technical accuracy reviewer** — Verify PR numbers, issue references, and deployment notes are correct and traceable.

Run these reviews in parallel when the platform supports subagents. Synthesize findings and apply auto-fixes for minor issues; surface trade-offs for user decision on substantive changes.

Quick editorial pass checklist:
- remove filler;
- keep section ordering stable;
- ensure humor does not obscure the changes;
- ensure the audience can understand why the listed changes matter;
- verify Fun Fact is present and audience-appropriate.

## Discord posting

Posting is optional. If the user asks for it, keep the message length under Discord limits and preserve markdown compatibility.

Example webhook flow:

```bash
curl -H "Content-Type: application/json" \
  -d "{\"content\": \"...your changelog...\"}" \
  "$DISCORD_WEBHOOK_URL"
```

Only post when the user explicitly asks for delivery or provides the destination context.

## Error handling

- If there are no changes in the period, use a quiet-day message such as `Quiet day: no merged changes found in the selected window.`
- If PR details are incomplete, preserve the PR numbers and mark the missing context rather than guessing.
- Validate the final message length before posting to Discord.

## Schedule recommendations

- Daily run around the start of the workday for the previous day's changes.
- Weekly run at the start of the week for the previous week's merges.
- Additional runs after major releases or large deployment windows.

## Audience guidance

- Dev team channels: include technical detail, performance notes, and precise implementation context.
- Product channels: focus on visible user impact and roadmap-relevant movement.
- Leadership channels: emphasize progress, notable wins, and blockers or risk.

## Keep a Changelog compliance

Read when: the user wants output that follows the [Keep a Changelog](https://keepachangelog.com/) standard (v1.1) or needs a `CHANGELOG.md` file.

**Guiding principles:**
- Changelogs are **for humans, not machines** — don't dump git logs.
- **Group changes** by type: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- **Latest version comes first** (reverse chronological order).
- Include **release dates** in ISO 8601 format (`YYYY-MM-DD`).
- Keep an **`Unreleased`** section at the top to track upcoming changes.
- Mention whether you follow **Semantic Versioning**.

**CHANGELOG.md structure:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features

### Fixed
- Bug fixes

## [1.2.0] - 2026-04-05

### Added
- Feature description (#123) (Contributor Name)
```

**What to exclude:**
- Dotfile changes (`.gitignore`, `.github`)
- Development-only dependency bumps (unless they affect runtime)
- Minor code style or formatting changes
- Cosmetic documentation tweaks

**What to include:**
- Refactorings (may have side effects)
- Runtime environment changes
- New documentation for previously undocumented features
- Security fixes (always)

## GitHub-specific guidance

Read when: generating changelogs for GitHub Releases or GitHub-native workflows.

**GitHub Release integration:**
- GitHub Releases can auto-generate release notes from PRs — use this as a starting point, not the final output.
- Copy the GitHub-generated content into your changelog workflow for editorial refinement.
- Add the Fun Fact and personality that GitHub's auto-generator omits.
- Link PR numbers to full URLs for GitHub Release compatibility: `(#123)` → `([#123](https://github.com/owner/repo/pull/123))`.

**PR label conventions for GitHub:**
Standard labels that help categorize:
- `breaking` or `breaking-change` — must surface prominently
- `feature`, `enhancement` — user-facing additions
- `bug`, `fix` — corrections
- `docs` — documentation
- `chore`, `refactor` — consider omitting unless notable
- `security` — always include, prioritize

**GitHub CLI (`gh`) integration:**
```bash
# List recently merged PRs
gh pr list --state merged --limit 20 --json number,title,author,labels,mergedAt

# Get detailed PR info with linked issues
gh pr view <number> --json number,title,body,author,labels,closingIssuesReferences
```

**GitHub-native workflows:**
- Consider creating a `.github/workflows/changelog.yml` that runs this skill on a schedule.
- Store Discord webhook URLs in GitHub Secrets, not in the skill output.
- Use GitHub Releases as the source of truth, with the skill-generated changelog as the editorial layer.
