# CODESTYLE.md

## Purpose

This document defines **mandatory coding, documentation, UI, and configuration standards** for the agentic governance framework.  
All contributors and automation agents MUST follow these rules. CI enforces them via repo-defined tasks and checks.

**Enforced toolchain (as applicable per repo):**
- JS/TS: **Biome**, **ESLint v9 (flat config)**, **TypeScript typecheck**, **Vitest/Node test**
- Docs: **Vale**
- Python: **Ruff**, **Pyright**, **pytest**
- Rust: **rustfmt**, **Clippy**, **cargo test**
- Security/Policy: **Semgrep**, AST/pattern guards, supply-chain scanners, SBOM/provenance tooling

**Baselines (Jan 2026)**
- Node: **24 Active LTS** (pinned in `.mise.toml` and `brainwav/governance/90-infra/compat.json`)
- TypeScript: **>= 5.9** (when using TS)
- Rust: **2024 edition** (rustc >= 1.85)

> **Security advisories override baselines.** When a CVE/security advisory is published for any baseline framework, all affected projects MUST upgrade to the patched version immediately, regardless of stated baseline.

---

## Table of Contents

- [0. Gold Production Standards (Hard Prohibitions)](#0-gold-production-standards-hard-prohibitions)
- [1. General Principles](#1-general-principles)
- [2. Task Orchestration (Repo-Defined)](#2-task-orchestration-repo-defined)
- [3. Node.js Standards](#3-nodejs-standards)
- [4. JavaScript / TypeScript](#4-javascript--typescript)
- [5. React Standards](#5-react-standards)
- [6. Vite Standards](#6-vite-standards)
- [7. Tailwind Standards](#7-tailwind-standards)
- [8. Storybook Standards](#8-storybook-standards)
- [9. Rust & Tauri Standards](#9-rust--tauri-standards)
- [10. Documentation & Prose (Vale)](#10-documentation--prose-vale)
- [11. Data & Config Formats (YAML / TOML / JSON)](#11-data--config-formats-yaml--toml--json)
- [12. Naming Conventions](#12-naming-conventions)
- [13. Commits, Releases, ADRs](#13-commits-releases-adrs)
- [14. Toolchain & Lockfiles](#14-toolchain--lockfiles)
- [15. Quality Gates: Coverage, Mutation, TDD](#15-quality-gates-coverage-mutation-tdd)
- [16. Fast Tools (MANDATORY for agents)](#16-fast-tools-mandatory-for-agents)
- [17. Security, Supply Chain & Compliance](#17-security-supply-chain--compliance)
- [18. Accessibility](#18-accessibility)
- [19. Observability, Logging & Streaming](#19-observability-logging--streaming)
- [20. Resource Management & Memory Discipline](#20-resource-management--memory-discipline)
- [21. Repository Scripts & Reports](#21-repository-scripts--reports)
- [22. MCP & External Tools](#22-mcp--external-tools)
- [23. Config References (Authoritative)](#23-config-references-authoritative)
- [Appendix A — EU AI Act](#appendix-a--eu-ai-act-dates-for-governance)
- [Appendix B — Waivers (Uniform Model)](#appendix-b--waivers-uniform-model)
- [Project-Specific Style Rules](#project-specific-style-rules)

---

## 0. Gold Production Standards (Hard Prohibitions)

**ABSOLUTE PROHIBITION** — It is a policy violation to ship or describe anything as “production-ready”, “complete”, “operational”, or “fully implemented” if any of the following exist anywhere in a **production code path**:

- Fabricated data/entropy: `Math.random()` (or equivalent) used to fabricate data without injected seed
- Hard-coded mock responses in production paths
- `TODO`/`FIXME`/`HACK` comments in production paths
- Placeholder stubs (“will be wired later”, “not implemented”, etc.)
- Disabled features signaling gaps (`console.warn("not implemented")`, dead flags)
- Fake metrics or synthetic telemetry presented as real

**Production code path** = any code that:
- ships in release artifacts,
- executes in deployed services/CLIs/apps,
- is reachable in release builds (even behind runtime flags).

**Identity & truthfulness**
- Apps/binaries/services MUST include **service identity** in outputs, error messages, and logs (`service:"<service_name>"`).
- Shared libraries SHOULD avoid hard-coded identity; prefer injected structured fields.
- Status claims in UIs/logs/docs MUST be evidence-backed by code and passing checks.

**Detection**
- Pattern guards/AST-Grep/Semgrep/CI checks fail on violations.
- Exceptions require an ADR and a time-boxed waiver (see Appendix B).

---

## 1. General Principles

- **Functional-first**: prefer pure, composable functions.
- **Classes**: only when required by a framework or to encapsulate unavoidable state.
- **Functions**: SHOULD be <= 40 LOC; split if readability suffers.
- **Exports**: named exports only; no `export default`.
  - Exception: framework conventions that require default exports (e.g., certain Next.js special files).
- **Determinism**: no ambient randomness/time in core logic; inject seeds/clocks/IDs.
- **Errors**: never swallow errors; add context and route to logging layer.
- **Cancellation**: long-running work MUST accept cancellation (AbortSignal in JS/TS; cancellation tokens/channels in Rust).

---

## 2. Task Orchestration (Repo-Defined)

- Use the repo’s task runner and “smart” wrappers when provided.
- If the repo uses an affected-only execution strategy, apply it where possible.
- Heavy targets SHOULD be serialized where the repo defines resource discipline.

---

## 3. Node.js Standards

- Packages MUST target the repo baseline Node version (pinned).
- JS/TS packages MUST use ESM (`"type": "module"`); avoid CJS unless a pack explicitly permits it.
- Prefer Node standard capabilities where appropriate (test runner for small libs is allowed).
- JSON imports MUST use import attributes where runtime requires it:

  ```ts
  import data from "./foo.json" with { type: "json" };
  ```

---

## 4. JavaScript / TypeScript

### Type discipline

* Explicit types at all public API boundaries (functions, modules, React props).
* `strict: true` with:

  * `noUncheckedIndexedAccess`
  * `exactOptionalPropertyTypes`
  * `useUnknownInCatchVariables`
* `any` is forbidden everywhere. Use concrete types or `unknown` + narrowing.

### Banned patterns (CI errors)

| ❌ DON'T                                                  | ✅ DO                                     |
| -------------------------------------------------------- | ---------------------------------------- |
| `: any`, `as any`, `Promise<any>`, `Record<string, any>` | concrete types or `unknown` + validation |
| `value as unknown as T`                                  | type guards or schema validation         |
| `// @ts-ignore`, `// @ts-nocheck`                        | `// @ts-expect-error -- reason + ticket` |
| unsafe `as SomeType` without runtime guard               | guard function or schema validator       |
| eslint-disable without reason/expiry                     | disable with reason + ticket + expiry    |

### Type-checked linting (mandatory)

* ESLint MUST be type-aware for TS code.
* The following MUST be errors:

  * `@typescript-eslint/no-explicit-any`
  * `@typescript-eslint/no-unsafe-assignment`
  * `@typescript-eslint/no-unsafe-member-access`
  * `@typescript-eslint/no-unsafe-argument`
  * `@typescript-eslint/no-unsafe-return`
  * `@typescript-eslint/no-unsafe-type-assertion`
  * `@typescript-eslint/no-unnecessary-type-assertion`
  * `@typescript-eslint/ban-ts-comment`

### Known `any` sources

* `JSON.parse()` and `Response.json()` return `any` in TS.
* Boundary mitigation MUST use schema validation (Zod/Valibot) or a typed parser helper.

### Modules & imports

* ESM only (`module: "NodeNext"`, `moduleResolution: "NodeNext"`).
* `verbatimModuleSyntax: true`, `moduleDetection: "force"`.

### Async & cancellation

* Prefer `async/await`.
* Exported async APIs that perform I/O or long work MUST accept `AbortSignal`.

### Formatting & lint split

* **Biome** is the formatter and primary lint for style.
* **ESLint v9 flat config** is required for policy/architecture/security rules.
* Avoid duplicate coverage (Biome formats; ESLint governs policy).

### Testing

* Tests co-located (`__tests__` or `*.test.ts`).
* Vitest is default for browser/client.
* Node test runner allowed for small pure Node libs.
* Snapshots only for intentionally stable serialized outputs.

---

## 5. React Standards

* Components MUST be accessible-by-default (semantic elements first; ARIA only when needed).
* Public components MUST document props and behavior (doc comment or docs site entry).
* Hooks MUST follow the Rules of Hooks; side effects only in `useEffect`/`useLayoutEffect`.
* Prefer controlled components; uncontrolled only when justified.
* Avoid global mutable state; state should be local, passed, or via a chosen state layer.

**React exports**

* Prefer named exports for components/hooks.
* Index barrels MUST NOT cause circular dependencies.

**Testing**

* Component behavior tests MUST focus on user-visible behavior (labels/roles/text), not implementation details.
* Prefer interaction tests over DOM snapshots.

---

## 6. Vite Standards

* Environment variables MUST be explicit, typed, and documented.
* Only variables intended for client exposure may be prefixed for Vite client use; secrets MUST NOT enter client bundles.
* Build modes MUST be reproducible; avoid mode-dependent behavior that changes runtime semantics without tests.
* Prefer explicit `define`/`resolve.alias` governance rather than ad-hoc path hacks.

---

## 7. Tailwind Standards

* Tailwind usage MUST be consistent across the repo (single policy).
* Class ordering MUST be enforced by the chosen linter/formatter (repo-defined).
* Avoid “magic numbers” when theme tokens exist.
* Conditional class composition MUST be readable (prefer a utility like `clsx`/`cva` if adopted by the repo pack).
* Accessibility:

  * Focus states MUST be visible.
  * Color-only signaling is forbidden.

---

## 8. Storybook Standards

* Storybook SHOULD exist for reusable UI libraries and component packs.
* The a11y addon and interaction testing SHOULD be enabled where applicable.
* Stories MUST avoid hidden network calls; use deterministic fixtures.
* Visual regression (if used) MUST run in CI with stable baselines.

---

## 9. Rust & Tauri Standards

### Formatting (Required)

* **rustfmt** is the formatter of record.
* Formatting MUST be enforced in CI (`cargo fmt --check`).
* Formatting config is shared repo-wide.

### Linting (Required)

* **Clippy** is required.
* Allow-lists MUST include reason + ticket (+ expiry if temporary) per waiver model.

### Concurrency (Required)

* Prefer structured concurrency (async/await + explicit cancellation).
* Shared mutable state MUST be isolated (channels, actors, or controlled ownership).
* `unsafe` is forbidden unless:

  * ADR exists,
  * mitigation is documented,
  * concurrency test exists.

### Tauri

* Commands MUST validate inputs and return typed errors.
* UI-facing state MUST be deterministic and testable.
* Avoid blocking the main thread; spawn heavy work to worker tasks.

### Testing

* Unit tests MUST run in CI (`cargo test`).
* UI/desktop end-to-end tests SHOULD be separated from unit tests in CI.

---

## 10. Documentation & Prose (Vale)

All docs and long-form prose MUST be linted with **Vale**.

### Scope

* `**/*.md`, `**/*.mdx`, `**/*.adoc`, `**/*.rst`

### Configuration

* Repo root MUST include `.vale.ini`.
* CI MUST run `vale sync` before linting.

### Severity

* Vale **errors** MUST fail CI.
* Warnings/suggestions MAY be elevated repo-wide.

### Suppression / waivers (required discipline)

Markdown:

```md
<!-- vale off -- reason: legacy quote; ticket: GOV-123; expires: 2026-03-01 -->
...
<!-- vale on -->
```

MDX:

```mdx
{/* vale off -- reason: legal text; ticket: GOV-124; expires: 2026-03-01 */}
...
{/* vale on */}
```

---

## 11. Data & Config Formats (YAML / TOML / JSON)

### JSON

* JSON MUST be valid UTF-8.
* Prefer machine-generated JSON for large files; minimize hand-edited large JSON.
* Transformations MUST use `jq` (not regex).
* In JS/TS, JSON inputs at boundaries MUST be schema-validated.

### YAML

* YAML MUST be linted (repo-selected linter) and schema-validated where applicable.
* Indentation MUST be 2 spaces; tabs forbidden.
* Avoid ambiguous scalars; prefer explicit `true`/`false`.
* GitHub Actions YAML MUST avoid large inline scripts when a repo script exists.
* YAML suppressions (if supported by the linter) MUST follow the same waiver model.

### TOML

* TOML files MUST be syntactically valid and formatted consistently.
* Tool pinning files (e.g., `.mise.toml`) are authoritative and MUST be reviewed like code.
* Validation MUST occur via the consuming tool in CI (mise/ruff/etc.), plus a syntax check if available.

---

## 12. Naming Conventions

* Directories & files: `kebab-case`

  * Exception: constitutional governance docs may use `UPPER_SNAKE_CASE` or `PascalCase`.
* JS/TS vars/functions: `camelCase`
* Python/Rust vars/functions: `snake_case`
* Types/components: `PascalCase`
* Constants: `UPPER_SNAKE_CASE`

---

## 13. Commits, Releases, ADRs

* Commits MUST follow Conventional Commits.
* Commits/tags MUST be signed (GPG/SSH or Sigstore/Gitsign in CI).
* Releases SHOULD follow SemVer with generated changelogs.
* ADRs are REQUIRED for significant decisions; store under `docs/adr/` (MADR template).
* Public API changes SHOULD require an ADR where the repo enables the ADR gate.

---

## 14. Toolchain & Lockfiles

* Node: pinned (mise + compat file).
* Package manager (mise-managed tools):

  * Monorepos: **pnpm** (Corepack-managed).
  * Single-package repos: **bun**.
* Tool manager: **mise** for JS toolchains (including Bun).
* Lockfiles are authoritative:

  * Monorepos: `pnpm-lock.yaml` (root)
  * Single-package repos: `bun.lockb`
  * Python: `uv.lock` (per project)
  * Rust: `Cargo.lock` (per crate/workspace)
* Frozen installs MUST be used in CI:

  * Monorepos: `pnpm install --frozen-lockfile`
  * Single-package repos: `bun install --frozen-lockfile`
  * `uv sync --frozen`
  * `cargo build --locked`

---

## 15. Quality Gates: Coverage, Mutation, TDD

PR merge gate MUST pass:

* Branch coverage >= 65% (env override allowed)
* Mutation score >= 75% (env override allowed)

Repo MAY enforce higher thresholds per workflow.

---

## 16. Fast Tools (MANDATORY for agents)

* Use `rg` not `grep` for project-wide search.
* Prefer `fd` for file finding.
* Use `jq` for JSON parsing/transformations.
* Read limits: cap reads at ~250 lines; prefer targeted context flags.

---

## 17. Security, Supply Chain & Compliance

* No hard-coded secrets; use env injection/secret manager.
* Validate/sanitize all external inputs.
* Scanning per PR SHOULD include:

  * OSV / audits per ecosystem
  * Semgrep policy + OWASP
  * SBOM generation at release (CycloneDX)
  * provenance/signing (SLSA/in-toto + Sigstore) where applicable
* Containers (if used): minimal base, non-root, read-only FS, drop caps.

---

## 18. Accessibility

* Baseline: WCAG 2.2 AA.
* Full keyboard operation required.
* Screen reader compatibility required.
* CLI/TUI: `--plain` / `--no-color` modes required.

---

## 19. Observability, Logging & Streaming

* OpenTelemetry SHOULD be used where services/CLIs exist.
* Logs SHOULD be structured and include `service` at app boundaries.
* Streaming:

  * default token delta streaming for CLIs,
  * optional aggregated mode,
  * JSON event streaming optional if supported.

---

## 20. Resource Management & Memory Discipline

* Respect repo-defined concurrency limits for pnpm/CI tasks.
* Measure before increasing parallelism; attach before/after results to PR when changing.

---

## 21. Repository Scripts & Reports

* If codemap/report tooling exists, outputs MUST include service identity and be attachable to PRs.

---

## 22. MCP & External Tools

* Adapters/helpers MUST not hard-code user-specific paths.
* Health checks MUST be scriptable.
* Egress/network policies MUST be explicit where required.

---

## 23. Config References (Authoritative)

* ESLint: `eslint.config.mjs` (flat config)
* Biome: `biome.json` (or repo equivalent)
* Vale: `.vale.ini`
* Mise: `.mise.toml`
* Rustfmt: `rustfmt.toml`
* CI: `.github/workflows/*.yml`
* Rules of AI: `brainwav/governance/00-core/RULES_OF_AI.md`

---

## Appendix A — EU AI Act (dates for governance)

* Act in force: 1 Aug 2024
* GPAI/foundation-model obligations applicable: 2 Aug 2025
* Most provisions fully applicable: 2 Aug 2026

---

## Appendix B — Waivers (Uniform Model)

Any waiver across ESLint, Vale, Semgrep, Clippy, CI checks MUST include:

* Rule ID
* Reason
* Ticket/issue reference
* Expiry (date) OR ADR reference

Expired waivers MUST fail CI.

Example waiver file:

```yaml
id: WAIVER-001
rule: no-unsafe-type-assertion
reason: "Temporary migration of legacy API; runtime validator landing next"
ticket: GOV-999
expires: 2026-02-01
```

---

<!-- PROJECT-SPECIFIC: START -->

## Project-Specific Style Rules

> Add project-specific linting, formatting, or architectural rules here. This section is NOT overwritten when upgrading the governance pack.

### Additional Rules

```jsonc
{
  // Extend local eslint.config.mjs with project-specific rules
}
```

### Architectural Boundaries

<!-- Define project-specific import restrictions or layer rules -->

<!-- PROJECT-SPECIFIC: END -->
