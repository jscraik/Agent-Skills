# Misuse-Resistant Interface Design

Secure code comes from interfaces that make the correct use natural and the
unsafe use hard to express. Prefer APIs that carry authority, ownership, and
invariants in their shape instead of relying on callers to remember process
rules.

## Principles

- Grant the narrowest capability that can do the job. If a caller only needs
  repository reads, expose a repository-scoped filesystem rather than a host
  path that can be reinterpreted.
- Keep unsafe adaptation behind a small boundary. Environment discovery, host
  paths, network fetches, and compatibility glue can exist, but should not
  become casual public APIs.
- Make invalid states unrepresentable where the domain permits it. Parse fixed
  configuration into named, typed fields at the boundary instead of handing
  callers strings or maps and asking them to remember invariants later.
- Put ownership in the API shape. Source declarations, generated artifacts, and
  tool-owned lockfiles have different owners; code should reflect which schemas
  the repository actually owns.
- Return errors with operation context. A bare error return pushes the burden of
  diagnosis onto the caller; wrapping at the boundary preserves the failing
  operation and the original cause.
- Add helpers only when they remove misuse or represent real domain behavior.
  Convenience that merely hides a read or a parse often makes ownership less
  clear.
- Tests should read like checks against policy. Reusable parsing, resolution,
  and comparison semantics belong in internal packages; exact current state
  belongs in checked configuration and tests, not prose.

## Examples

- A repository API can expose an `fs.FS` rooted at the repo while keeping host
  root discovery private.
- A fixed toolchain parser can decode required pins into typed version fields; a
  generic map is a better fit for genuinely open-ended data.
- A workflow loader can encode the workflow directory and step shape because
  those are repository policy surfaces. A lockfile reader usually should not
  exist unless the repository owns the lockfile schema.

## Review Rule

When review feedback identifies an interface misuse pattern, treat it as an API
design rule until proven local. Search adjacent public helpers, parsers,
loaders, validators, and command surfaces for the same authority, ownership,
or invariant leak before applying a line-local fix.

A named instance is only the starting evidence. If feedback says a
success/fail bool should become a contextual named error, inspect equivalent
APIs in the same package or layer before finishing the fix.

Classify each similar case as:

- fixed now;
- different semantics;
- public compatibility requires migration;
- outside current ownership boundary;
- intentionally open-ended data.

Do not create broad helper APIs merely to make code shorter. A helper is useful
when it carries authority, narrows capability, preserves ownership, or makes an
invalid state harder to express.
