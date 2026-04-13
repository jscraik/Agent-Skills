---
name: npm-release
description: "Create and validate npm package release workflows using semver bumping, dist-tags, provenance publishing, and 2FA-aware safeguards. Use when users need npm publish/version guidance in CI or local release lanes."
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

## Deliverables

- Release command sequence from version bump to publish.
- Dist-tag and channel guidance.
- 2FA/OTP handling notes.
- Post-release validation checks.
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

## Workflow

1. Confirm target version strategy and release channel.
2. Run version bump command and verify tag/commit policy (`git-tag-version`).
3. Dry-run package contents when needed (`npm pack --dry-run`).
4. Publish with explicit flags for access, provenance, and channel.
5. Apply/update dist-tags for rollout channels.
6. Verify published version and tags.

## Constraints

- Redact secrets, credentials, tokens, and OTP codes by default.
- Never expose private package credentials in logs or examples.
- Prefer one-time OTP entry methods that avoid persisting sensitive values in shell history.
- Do not publish live artifacts before at least one dry-run or equivalent verification when uncertainty exists.

## Validation

- `npm view <package-name> version`
- `npm dist-tag ls <package-name>`
- `npm publish --dry-run` or `npm pack --dry-run` before live publish when uncertain
- If OTP is required and missing, stop and report blocker clearly.

## Failure mode

- If publish fails with auth/OTP/provenance errors, stop and report exact npm error output without retry loops.
- If dist-tag mutation fails, keep current channel state unchanged and escalate with the failing command.

## Gotchas

- `npm publish --tag` does not retroactively move existing tags.
- Misconfigured `git-tag-version` can surprise release automation.
- 2FA blocks publish/dist-tag commands unless OTP is supplied.

## Anti-patterns

- Publishing without verifying intended dist-tag state.
- Assuming prerelease bump behavior without explicit `preid`.
- Mixing public/private access flags incorrectly on first publish.

## Examples

- "Release `@acme/widgets` `1.4.0` to `latest` with provenance and public access flags."
- "Publish a release candidate with `beta` tag while keeping `latest` on stable."
- "Our publish step fails because of OTP enforcement; provide the exact npm command flow."

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/context7-notes.md`
