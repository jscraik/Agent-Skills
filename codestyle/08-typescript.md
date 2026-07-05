# TypeScript Standards

## Table of Contents
- [Scope](#scope)
- [Type discipline](#type-discipline)
- [Banned patterns](#banned-patterns)
- [Linting and module rules](#linting-and-module-rules)
- [Async and cancellation](#async-and-cancellation)
- [Size and decomposition](#size-and-decomposition)
- [Testing](#testing)
- [Enforcement](#enforcement)

## Scope
- This module is the canonical TypeScript-specific standards reference for this codestyle pack.

## Type discipline
- Explicit types at public API boundaries (functions, modules, component props) are REQUIRED.
- Exported public API declarations in changed production `src/**` files MUST
  have JSDoc; touched function-like declarations in each changed production
  file MUST keep JSDoc coverage at or above 80%. `pnpm run
  quality:docstrings` enforces both changed-code ratchets.
- Use strict TypeScript configuration and keep boundary validation explicit.
- Repository TypeScript projects SHOULD keep `strict`,
  `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes` enabled unless
  a documented migration or waiver explains why a target cannot support them.
- `any` SHOULD be avoided in production paths; use concrete types or `unknown` plus narrowing. If a temporary `any` is unavoidable, keep it local, justified, and covered by tests or a follow-up waiver.

## Banned patterns
- Unjustified `: any`, `as any`, `Promise<any>`, and `Record<string, any>` in production code.
- `value as unknown as T` double assertions without runtime validation.
- `// @ts-ignore` and `// @ts-nocheck`; use `@ts-expect-error` with rationale only when unavoidable.
- Unsafe type assertions without guard functions or schema validation.

## Linting and module rules
- Biome handles formatting and style-level lint in this repository and MUST pass where enabled.
- Biome configuration lives in `biome.json`; when the Biome package version changes, keep the schema URL and lockfile in sync.
- TypeScript type safety MUST be enforced with `tsc --noEmit`.
- Downstream projects MAY use ESLint for additional policy checks when an `eslint.config.*` file exists; do not claim ESLint coverage where it is not configured.
- Prefer ESM and explicit module syntax for Node/TS packages.
- Local ESM imports MUST include `.js` extensions for emitted JavaScript compatibility.
- NodeNext TypeScript projects MUST keep `module` and `moduleResolution` aligned to `NodeNext` unless a documented runtime migration changes both together.
- Node-targeted TypeScript projects SHOULD keep the compiler target and lib
  aligned with the repository Node runtime baseline. When Node or TypeScript
  major versions move, update `tsconfig.json`, `.mise.toml`, package
  metadata, and generated scaffolds together.
- With `verbatimModuleSyntax` enabled, imports MUST reflect runtime semantics; use `import type` for type-only imports.
- JSON imports in NodeNext-style modules MUST use import attributes when the runtime/compiler requires them, for example `with { type: "json" }`.
- Keep imports acyclic; avoid barrels that create circular dependency chains.
- Node scripts that consume JSON, command output, environment variables, or
  filesystem state MUST validate and narrow those values at the boundary before
  domain logic uses them. Prefer small typed helpers over repeated ad hoc
  `JSON.parse`, `process.env`, or `RegExp` checks.
- Dynamic regular expressions MUST escape user- or file-derived fragments.
  Prefer exact path comparison, URL/path parsers, schema validation, or
  structured data checks before introducing regex.

## Async and cancellation
- Prefer `async/await` over nested Promise chains.
- Exported async APIs that do I/O or long work SHOULD accept `AbortSignal`.
- Surface cancellation as expected behavior, not as opaque failures.

## Size and decomposition
- `pnpm run quality:size` is the executable size gate for changed production
  source. Treat its failures as blockers.
- Changed production modules MUST stay at or below 400 logical lines, functions
  MUST stay at or below 80 logical lines, and function complexity MUST stay at or
  below 10.
- Changed test files MUST stay at or below 1,200 logical lines.
- `scripts/check-code-size.mjs` enforces these limits directly. Prefer extracting
  pure helpers, schema tables, or adapter-specific logic before raising a limit.
- `harness fitness` normalizes `pnpm run quality:size -- --json` artifacts into
  the deterministic `quality-structure` lane. Treat those findings as repair
  contracts with concrete metrics, required-fix constraints, and acceptance
  criteria; do not infer structure by parsing human-readable messages.
- Advisory AI review can suggest cohesion improvements, but it MUST NOT promote
  itself into blocking authority without a deterministic gate or explicit
  contract change.

## Testing
- Co-locate tests (`*.test.ts` / `__tests__`) and assert user-visible behavior where applicable.
- Keep snapshots limited to intentionally stable serialized outputs.
- Validate parsing boundaries (`JSON.parse`, `Response.json`) with schemas or typed helpers.

## Enforcement
- TypeScript changes MUST pass:
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm run quality:docstrings`

  - `pnpm run quality:size`
  - `pnpm run test:related`

  - `pnpm test`
  - `pnpm audit`
  - `pnpm check`
  - `bash scripts/validate-codestyle.sh`
  - `bash scripts/verify-work.sh --fast`
- Avoid soft bypasses for type/lint errors; temporary suppressions require waiver metadata with rule ID or section, reason, tracking ticket, and expiry or ADR reference.
- Validation evidence MUST be explicit:
  - `Command: <exact command> -> pass|fail|blocked (<reason>)`
