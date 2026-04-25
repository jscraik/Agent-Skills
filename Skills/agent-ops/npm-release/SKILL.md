---
name: npm-release
description: "Create and validate npm package release workflows with deterministic installs, semver, dist-tags, provenance, and 2FA safeguards. Use when preparing or publishing npm releases."
metadata:
  skill-type: runbook
---

# NPM Release

Use this skill for npm package release operations: version bumping, publish strategy, dist-tag controls, provenance flags, and post-publish verification.

## When to use

- Publishing packages to npm registry.
- Setting release channels (`latest`, `beta`, `next`, custom tags).
- Preparing semver bumps and git-tag behavior.
- Handling 2FA/OTP for release operations.
- Enforcing deterministic npm install/lockfile behavior as part of release readiness.
- Validating release scripts/contracts in `package.json` before publish.

## Non-triggers

- Dependency install/lockfile workflow asks without publish intent.
- Registry-agnostic release plans that do not use npm CLI.

## Philosophy

- Make release channels explicit through tags and post-publish checks.
- Treat publish as a controlled pipeline, not a single command.
- Fail fast when OTP/provenance/access requirements are unmet.

## Required inputs

- Package name and intended next version or bump type.
- Desired release channel (`latest` or custom dist-tag).
- Access/provenance requirements (`--access public`, `--provenance`).
- Account security posture (2FA, OTP requirement).
- `release-notes-handoff.v1` from `[[release-notes]]` when the release has user-facing behavior, CLI/API changes, generated artifacts, or compatibility impact.

## Deliverables

- Release command sequence from version bump to publish.
- Dependency/install discipline checks required before publish.
- Dist-tag and channel guidance.
- 2FA/OTP handling notes.
- Post-release validation checks.
- Handoff validation result showing whether release notes, version, channel, and breaking-change messaging are aligned.
- Structured outputs should include `schema_version` when a schema-bound contract is requested.

## Rules

**Use explicit version bump semantics**:

```bash
npm version patch
npm version minor
npm version major
npm version prerelease --preid=rc
npm version from-git
```

**Publish with explicit channel and provenance when required**:

```bash
npm publish --provenance --access public
npm publish --tag beta
```

**Manage channels with dist-tags**:

```bash
npm dist-tag add my-pkg@1.0.0 beta --otp <OTP_CODE>
```

**Respect 2FA requirements**:

```bash
npm profile enable-2fa auth-and-writes
```

**Consume release-note handoff before publish**:

If `release-notes-handoff.v1` is present, validate `package`, `version`, `channel`, `sections.breaking_changes`, and `publish_blockers` before any publish command. If user-facing changes exist but no handoff is present, stop and run `[[release-notes]]` first.

## Workflow

1. Confirm target version strategy and release channel.
2. Confirm release communication readiness: consume `release-notes-handoff.v1`, or ask `[[release-notes]]` to create it when public notes are needed.
3. Confirm lockfile/install discipline at the target package root (`npm --prefix <package-path> ci`, lockfile in sync, required release script contract present). Validate that `package.json` scripts include release-critical hooks used by the workflow, such as `prepare`, `prepublishOnly` (or `prepublish`), and a release entrypoint like `release` or `publish`, and that they align with `references/contract.yaml`.
4. Run version bump command and verify tag/commit policy (confirm `git-tag-version` npm config is set correctly before `npm version`).
5. Dry-run package contents when needed (`npm pack --dry-run`).
6. Publish with explicit flags for access, provenance, and channel.
7. Apply/update dist-tags for rollout channels.
8. Verify published version and tags.

## Constraints

- Redact secrets, credentials, tokens, and OTP codes by default.
- Never expose private package credentials in logs or examples.
- Prefer one-time OTP entry methods that avoid persisting sensitive values in shell history.
- Do not publish live artifacts before at least one dry-run or equivalent verification when uncertainty exists.
- Do not publish when `release-notes-handoff.v1` has `publish_blockers`, mismatched package/version/channel, hidden breaking changes, or prerelease wording aimed at `latest`.

## Validation

- `npm view <package-name> version`
- `npm dist-tag ls <package-name>`
- `npm publish --dry-run` or `npm pack --dry-run` before live publish when uncertain
- `release-notes-handoff.v1` matches package, version, channel, and breaking-change expectations before publish
- If OTP is required and missing, stop and report blocker clearly.

## Failure mode

- If publish fails with auth/OTP/provenance errors, stop and report exact npm error output without retry loops.
- If dist-tag mutation fails, keep current channel state unchanged and escalate with the failing command.

## Gotchas

- `npm publish --tag` does not retroactively move existing tags.
- Misconfigured `git-tag-version` can surprise release automation.
- 2FA blocks publish/dist-tag commands unless OTP is supplied.
- Release notes that say beta/rc/canary while publishing to `latest` are a channel mismatch, not a wording issue.

## Anti-patterns

- Publishing without verifying intended dist-tag state.
- Publishing user-facing changes without a release-note handoff or explicit no-notes-needed decision.
- Assuming prerelease bump behavior without explicit `preid`.
- Mixing public/private access flags incorrectly on first publish.

## Examples

- "Release `@acme/widgets` `1.4.0` to `latest` with provenance and public access flags."
- "Publish a release candidate with `beta` tag while keeping `latest` on stable."
- "Our publish step fails because of OTP enforcement; provide the exact npm command flow."
- "Validate this `release-notes-handoff.v1` before publishing `@brainwav/coding-harness`."

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/context7-notes.md`

## See Also

| Skill | When to use together |
|---|---|
| [[pnpm-manager]] | Coordinate monorepo package prep before npm publish |
| [[release-notes]] | Draft public release notes and produce the npm handoff before publish |
| [[fix-mise]] | Pin and verify runtime/tool versions before release commands |
| [[gh-workflow]] | Coordinate release PR/branch workflows and checks |
