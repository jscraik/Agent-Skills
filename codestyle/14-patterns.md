# Common Patterns Standards

## Table of Contents
- [Scope](#scope)
- [Core design principles](#core-design-principles)
- [Misuse-resistant interface design](#misuse-resistant-interface-design)
- [Structural patterns](#structural-patterns)
- [Boundary and response patterns](#boundary-and-response-patterns)
- [Enforcement](#enforcement)

## Scope
- This module defines reusable implementation patterns that improve maintainability and consistency.

## Core design principles
- Implementations SHOULD prioritize KISS, DRY, and YAGNI in that order.
- Production paths SHOULD favor immutable updates over in-place mutation.
- Functions SHOULD remain focused and deeply nested logic SHOULD be split into named helpers.

- Changed production `src/**` files MUST pass `pnpm run quality:size`; oversized legacy files MUST have an explicit allowlist entry and SHOULD be reduced opportunistically rather than expanded.

## Misuse-resistant interface design

Secure and maintainable code comes from interfaces that make the correct use natural and unsafe use hard to express. Prefer APIs that carry authority, ownership, and invariants in their shape instead of relying on callers to remember process rules.

- Grant the narrowest capability that can do the job. If a caller only needs repository reads, expose a repository-scoped filesystem or reader instead of a host path that can be reinterpreted.
- Keep unsafe adaptation behind a small boundary. Environment discovery, host paths, network fetches, and compatibility glue can exist, but SHOULD NOT become casual public APIs.
- Make invalid states unrepresentable where the domain permits it. Parse fixed configuration into named, typed fields at the boundary instead of handing callers strings or maps and asking them to remember invariants later.
- Put ownership in the API shape. Source declarations, generated artifacts, and tool-owned lockfiles have different owners; code SHOULD reflect which schemas the repository actually owns.
- Return errors with operation context. Bare errors push diagnosis onto callers; boundary code SHOULD preserve the failing operation and original cause.
- Add helpers only when they remove misuse or represent real domain behavior. Convenience that merely hides a read or parse often makes ownership less clear.
- Tests SHOULD read like checks against policy. Reusable parsing, resolution, and comparison semantics belong in internal packages; exact current state belongs in checked configuration and tests, not prose.
- Design corrections MUST be generalized before closeout when they imply a broader principle. If feedback says one boolean success/failure API should instead return a named sentinel error, search sibling APIs and tests in the same command core, adapter family, and affected docs/templates; then either update the shared pattern or record why each sibling is intentionally different.

Examples:

- A repository API can expose a filesystem rooted at the repo while keeping host root discovery private.
- A fixed toolchain parser can decode required pins into typed version fields; a generic map is a better fit for genuinely open-ended data.
- A workflow loader can encode the workflow directory and step shape because those are repository policy surfaces. A lockfile reader SHOULD NOT exist unless the repository owns the lockfile schema.


## Structural patterns
- Code SHOULD be organized by feature/domain boundaries instead of technology buckets when practical.
- Files MUST remain cohesive; shared logic SHOULD be extracted before copy-paste drift appears.
- Repository/service abstractions SHOULD be used when multiple storage backends or test doubles are required.
- A deterministic `quality-structure` fitness finding SHOULD be handled as a
  bounded structural repair: preserve public behavior, keep side effects at the
  same boundary, extract named helpers around validation or pure logic first,
  and prove the result with the finding's acceptance criteria.
- Repeated command prefixes, runtime setup, schema parsing, and path
  normalization SHOULD become small repo-owned helpers when two or more scripts
  need the same behavior.
- Do not add helpers that only rename a single call. A helper should remove
  real duplication, encode a domain invariant, or make unsafe states harder to
  express.

## Boundary and response patterns
- All external input MUST be validated at boundaries before domain logic.
- Error structures and API envelopes MUST remain consistent within a service surface.
- Named constants MUST be used for thresholds, limits, and policy values; magic numbers MUST be avoided.
- Prefer structured parsers and typed boundary objects over regex for JSON,
  YAML, TOML, URLs, paths, package metadata, command output, and schema-bearing
  artifacts.
- Regex is acceptable for local token validation and simple search, but brittle
  parsing regex SHOULD be replaced with `jq`, URL/path APIs, schema validators,
  or typed helper functions.

## Enforcement

- Changed production code MUST run `pnpm run quality:size` before handoff.
- When `harness fitness` reports a `quality-structure` finding, handoff MUST
  include the rerun command and whether the finding was cleared, still present,
  or intentionally deferred with a tracked reason.

- Pattern changes SHOULD be reviewed with targeted examples in PR notes.
- Any deliberate deviation from these defaults MUST include rationale and a tracker reference.
