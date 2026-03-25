Read when: you need the fuller upstream changelog playbook, including PR-analysis priorities, audience tuning, Discord formatting, posting notes, or schedule guidance.

Imported and adapted from `EveryInc/compound-engineering-plugin` at pinned ref `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`. This file preserves the richer single-file source guidance for the local `changelog` wrapper.

# Changelog Full Guide

## Purpose

Create an engaging changelog for recent merges to `main`, highlighting features, bug fixes, contributor credit, and operational notes without losing traceability.

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

- Title with date and time window.
- Breaking changes.
- New features.
- Bug fixes.
- Other improvements.
- Shoutouts.
- Optional closing note or fun fact when the audience and channel fit.

## Deployment notes

Call out when relevant:

- database migrations;
- environment variable updates;
- manual post-deploy steps;
- dependency changes with rollout implications.

## Style review

After drafting, do a quick editorial pass:

- remove filler;
- keep section ordering stable;
- ensure humor does not obscure the changes;
- ensure the audience can understand why the listed changes matter.

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
