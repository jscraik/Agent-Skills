# Release Note Modes

Use this reference after the entrypoint selects `release-notes`.

## Mode selection

Choose exactly one primary mode:

| Mode | Use when | Output |
| --- | --- | --- |
| PR notes | A PR body needs `## Release notes`, or the user asks what changed in a branch | Markdown section suitable for the PR |
| Changelog update | A repository release-history file needs an entry | Patch-ready changelog text |
| Release-history lookup | The user asks when something shipped or what changed recently | Version-cited answer from GitHub releases |
| NPM handoff | An npm publish flow needs messaging and channel validation | `release-notes-handoff.v1` |

If two modes are requested, do them in dependency order: draft notes first, then changelog, then npm handoff.

## Evidence priority

Prefer evidence in this order:

1. Local diff or commit range supplied by the user.
2. PR metadata and linked issues.
3. Linear issue text or comments, when available.
4. Existing release notes and changelog entries.
5. GitHub releases queried with `scripts/list_releases.py`.

Record uncertainty instead of filling gaps with plausible marketing language.

## PR notes

Use this shape unless the repository has a stricter template:

```md
## Release notes

- Added ...
- Fixed ...
- Changed ...

## Notes

- Internal-only: ...
```

If no public note is needed, write:

```md
## Release notes

No user-facing release notes needed. Changes are internal-only: <brief evidence>.
```

## Changelog update

Preserve the repository's existing format. If there is no clear convention, use:

```md
## <version or Unreleased> - <YYYY-MM-DD>

### Added

- ...

### Fixed

- ...

### Changed

- ...

### Breaking Changes

- ...
```

Only include sections that have content. Keep implementation-only details out unless they explain user-facing behavior, operational risk, or compatibility.

## Release-history lookup

Use `scripts/list_releases.py`:

```bash
python3 scripts/list_releases.py --repo OWNER/REPO --tag-prefix TAG_PREFIX --limit 40
```

For a query:

- Search release tag, name, body, and linked PR numbers.
- Cite the matching version/tag and release URL.
- If a linked PR is needed for confidence, query it separately with `gh pr view`.
- If no match is found, say exactly that no matching release was found in the searched range.

## NPM handoff

Emit `release-notes-handoff.v1` before `npm-release` publishes. The handoff is a release communication artifact, not a publish command.

Required fields:

- `schema_version`
- `package`
- `version`
- `channel`
- `audience`
- `summary`
- `sections`
- `evidence`
- `publish_blockers`

Block or warn before handoff when:

- `publish_blockers` is non-empty.
- `breaking_changes` has entries but the version is not a major bump for stable releases.
- Release wording says prerelease, beta, alpha, canary, or rc while `channel` is `latest`.
- User-facing changes exist but all public sections are empty.
- Package/version/channel cannot be confirmed from `package.json`, user input, or release plan evidence.

## Linear evidence

Use Linear issue IDs, titles, and acceptance criteria as evidence when they are already available. Do not create ADRs from this workflow. For durable project decisions, update the appropriate Linear issue, project note, changelog, or release handoff.

## Security

Release notes are public or semi-public artifacts by default. Redact:

- secrets, tokens, and credentials
- private customer names or incidents
- undisclosed vulnerabilities before approval
- internal file paths when they reveal private system layout
