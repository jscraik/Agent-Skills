# Token Governance (Lifecycle)

Last verified: 2026-01-01

Use this when adding or changing tokens.

## Add
- Add new tokens only after confirming no existing token fits the need.
- Add semantic tokens first; map to raw values in themes.
- Update bridge mappings for web surfaces.

## Deprecate
- Mark deprecated tokens in token metadata and docs.
- Provide a replacement token and migration note.
- Keep deprecated tokens for at least one release cycle.

## Version
- Bump token package version on any token change.
- Include a concise CHANGELOG entry with additions/removals/renames.
- Note breaking changes explicitly and provide migration steps.

## Migrate
- Provide a codemod or search/replace guidance if a rename is required.
- Update Storybook docs and component usage examples.
