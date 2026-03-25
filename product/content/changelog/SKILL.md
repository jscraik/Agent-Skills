---
name: changelog
description: Draft concise changelogs from recently merged pull requests, grouped by user-facing impact and contributor credit. Use when the user wants a daily or weekly engineering summary, release-note style update, or Discord-ready changelog based on GitHub activity.
metadata:
  skill-type: team_automation
---

# Changelog

Preserves upstream changelog guidance from `EveryInc/compound-engineering-plugin` at pinned ref `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`; see [`artifacts/changelog-import-2026-03-23.txt`](../../../artifacts/changelog-import-2026-03-23.txt) for provenance and hashes. The richer operating guide lives in `references/full-guide.md`.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Workflow](#workflow)
- [Reference guide](#reference-guide)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Gotchas](#gotchas)

## When to use
- Use when the user wants a changelog, release-note summary, or daily or weekly engineering update from merged PRs.
- Use when the output needs grouping by features, fixes, and improvements with contributor credit.
- Use when the destination is chat-friendly, such as Discord, Slack, or an internal update post.

Do not use this skill when:
- the user needs to cut or publish a release; use `release`;
- the task is a full PR review or merge-readiness check; use `check-pr` or `gh-workflow`;
- the user wants a marketing launch post rather than an engineering changelog.

## Required inputs
- repository or GitHub scope to inspect;
- time window such as daily, weekly, or explicit number of days;
- audience, if known, such as dev team, product, or leadership;
- posting target or format constraint, especially Discord length limits.

## Deliverables
- a concise changelog grouped by change type and impact;
- PR-number traceability and contributor credit where evidence exists;
- breaking changes or deployment notes called out clearly when relevant;
- a quieter fallback summary when no merged changes are found.

## Failure mode
- If the repository or time window is unclear, stop and narrow the scope first.
- If GitHub details are partially unavailable, produce a bounded changelog with the evidence you have and mark the missing detail explicitly.
- If the user actually needs release execution or PR triage instead of a summary artifact, switch to the more specific skill.

## Standards snapshot (March 2026)
- Prefer evidence from merged PRs, labels, linked issues, and descriptions over guesswork.
- Keep the summary readable first, but never at the cost of losing breaking-change visibility or PR traceability.
- Match tone to the audience: technical for dev channels, clearer business framing for broader org updates.
- Preserve nuanced formatting and posting guidance in `references/full-guide.md` instead of inflating this wrapper.

## Workflow
1. Define the repo scope and time window.
2. Gather merged PRs from the target branch, then inspect PR titles, descriptions, labels, linked issues, and contributors.
3. Classify changes into breaking changes, features, bug fixes, and other improvements.
4. Pull deployment notes, migrations, env var changes, or manual steps into a dedicated callout when relevant.
5. Draft the changelog for the intended audience and respect the target length limit.
6. If the output is for Discord or another short-form channel, tighten the summary without removing the highest-signal changes.

## Reference guide
- Read `references/full-guide.md` when you need the preserved upstream playbook for:
  - PR-analysis details and prioritization;
  - Discord-ready formatting and posting notes;
  - audience-specific tone adjustments;
  - quiet-day fallbacks, deployment notes, and schedule guidance.
- Treat this `SKILL.md` as the routing layer and preserve the more specific changelog doctrine in the reference file.

## Validation
- Verify the time window and branch scope used for the changelog.
- Verify every highlighted item maps back to an actual PR, issue, or release note input.
- Verify breaking changes and deploy notes are surfaced before routine improvements.
- Verify the final output respects the requested channel or length constraints.

## Anti-patterns
- Inventing impact, urgency, or contributor credit not supported by the PR evidence.
- Treating PR titles alone as sufficient without checking descriptions, labels, or linked issues when available.
- Burying breaking changes under routine improvements.
- Compressing the output so aggressively that the changelog loses traceability or useful deployment context.

## Gotchas
- No merged PRs in scope -> changelog reads empty or confused -> use a quiet-day summary and say the window was checked.
- PR metadata is incomplete -> summary overreaches -> keep traceability explicit and mark missing issue or label context.
- Discord output exceeds limits -> summary becomes unreadable after trimming -> shorten routine items first and preserve breaking changes, major features, and deploy notes.

## See Also

| Skill | When to use together |
|---|---|
| [[gh-workflow]] | Inspect PRs, branches, and merge state before drafting the summary |
| [[release]] | Cut the release after the changelog content is ready |
| [[every-style-editor]] | Polish the final changelog for a branded external audience |
| [[feature-video]] | Pair a release-note summary with a visual walkthrough artifact |

**Topic map:** [[content-publishing]]
