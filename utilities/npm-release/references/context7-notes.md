# Context7 Notes: NPM Release

- Retrieval path: `cli_primary`
- Auth wrapper: `op run --env-file ~/.codex/.env -- ...`
- Library id: `/websites/npmjs`

## Queried commands

```bash
op run --env-file ~/.codex/.env -- ctx7 library npm "package release publish dist-tag version workflow" --json
op run --env-file ~/.codex/.env -- ctx7 docs /websites/npmjs "npm publish version dist-tag provenance access two-factor otp" --json
op run --env-file ~/.codex/.env -- ctx7 docs /websites/npmjs "npm version git-tag-version from-git preid pre-release workflow" --json
```

## Grounding highlights

- `npm version patch|minor|major|prerelease|from-git` for semver bumping.
- `npm publish --provenance --access public` for first public release with provenance.
- `npm publish --tag <tag>` for non-latest channels.
- `npm dist-tag add <pkg@version> <tag> --otp <code>` for channel control.
- `npm profile enable-2fa auth-and-writes` for write protection.
