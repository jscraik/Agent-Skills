# Documentation Configuration And Release Standards

Applies to the matching changed surface. Use repository commands and lockfiles
for the actual toolchain; unrelated technology sections do not add checks.

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

### Lint failures

Do not suppress Vale findings. Rewrite, quote selectively, or move the owning
content to a form that the active lint contract can validate.

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
* YAML findings MUST be fixed in the owning source; suppression is not a supported policy path.

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

* Node: pinned by the current `.mise.toml` and applicable package manifests.
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
