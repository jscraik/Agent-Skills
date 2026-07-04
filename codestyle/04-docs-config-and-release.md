# Docs, Config, and Release Standards

## Table of Contents
- [10. Documentation & Prose (Vale)](#10-documentation--prose-vale)
- [11. Data & Config Formats (YAML / TOML / JSON)](#11-data--config-formats-yaml--toml--json)
- [12. Naming Conventions](#12-naming-conventions)
- [13. Commits, Releases, ADRs](#13-commits-releases-adrs)
- [14. Toolchain & Lockfiles](#14-toolchain--lockfiles)

## 10. Documentation & Prose (Vale)

Authoritative repository docs MUST pass the configured documentation gates.

### Scope

* `pnpm docs:lint` runs markdownlint over Markdown files selected by `.markdownlint-cli2.yaml`.
* `scripts/check-doc-style.sh` runs Vale on staged authoritative docs: `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, and `docs/**/*.md`.
* Other prose formats (MDX, AsciiDoc, reStructuredText) MUST declare their formatter/linter contract before becoming review-critical surfaces.

### Configuration

* Repo root MUST include `.vale.ini` when Vale is enabled.
* CI or local validation SHOULD run `vale sync` before Vale linting when Vale packages are configured.
* Markdown style MUST stay compatible with the repo markdownlint configuration.

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
* Tool pinning files (for example `.mise.toml`) are authoritative and MUST be reviewed like code.
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

### Commit format (enforced)

* Commits MUST be concise and atomic.
* Prefer Conventional Commits: `feat|fix|refactor|docs|test|chore`.
* Subject MUST follow `<type>(optional-scope): <imperative summary>`.
* Subject MUST be specific and <= 72 characters.
* One logical change per commit; split unrelated edits.

### Commit body requirements

* Include `Why`, `What`, and `Impact/Risk` sections when helpful.
* Include `Behavior Proof` when a commit changes runtime behavior, CLI
  behavior, generated artifacts, validation behavior, agent workflow behavior,
  user-facing docs, or any observable operator experience.
* `Behavior Proof` SHOULD state the behavior or issue addressed, real
  environment or production path tested, exact post-patch steps or command,
  evidence after fix, observed result, untested paths, proof limitations, and
  before evidence when available.
* `Validation` section MUST include only commands actually run.
* Validation lines MUST use this format:
  * `Command: <exact command> -> pass|fail|blocked (<reason>)`
* Never invent validation.
* If no validation was run, state:
  * `Validation: not run (<reason>)`

### Commit trailer requirement

* Preserve existing trailers.
* Include this trailer exactly once as the final trailer line:
  * `Co-authored-by: Codex <noreply@openai.com>`

### Pull request template contract (enforced)

* Follow the repository PR template exactly.
* Do not add, remove, rename, or reorder template sections.
* Keep checklist item text exactly as written.
* Fill required fields with concrete, non-placeholder content.

### PR prep requirements

* Before generating PR title/description, read:
  * `AGENTS.md`
  * `CONTRIBUTING.md`
  * `.github/PULL_REQUEST_TEMPLATE.md`
* Use repo-defined command contracts from scripts/docs; do not assume `npm`.
* Prefer repository wrapper gates when defined (for example `bash scripts/verify-work.sh`) over ad hoc equivalents.

### PR testing and artifacts

* Populate required structured testing fields exactly as the template defines.
* Record exact commands and explicit outcomes using:
  * `Command: <exact command> -> pass|fail|blocked (<reason>)`
* If a planned step cannot run, mark it `blocked` with the concrete blocker.
* Never hardcode `npm test`; use the repository canonical command contract.
* Run aggregate/deep gates when defined and required by change scope.
* Keep `CodeRabbit` and `Codex` review artifact fields non-empty when present in template.
* Preserve independent review requirements; the coding agent cannot self-approve.

### Release and architecture records

* Commits/tags MUST be signed (GPG/SSH or Sigstore/Gitsign in CI).
* Releases SHOULD follow SemVer with generated changelogs.
* ADRs are REQUIRED for significant decisions; store under `docs/adr/` (MADR template).
* Public API changes SHOULD require an ADR where the repo enables the ADR gate.

---

## 14. Toolchain & Lockfiles

* Node and package-manager contract is defined in [11-package-managers-pnpm-npm.md](./11-package-managers-pnpm-npm.md).
* `.mise.toml`, `docs/agents/tooling.md`, `scripts/check-environment.sh`, and `harness.contract.json` MUST stay aligned when a managed CLI is added, removed, or renamed.
* Global npm CLIs used by agents SHOULD be pinned through mise as `npm:<package>` tools instead of installed manually with `npm install -g`.
* If mise lockfile support is adopted for this repository, commit the lockfile and document the update workflow in the tooling policy before requiring it in CI.
* Python dependency locks should remain deterministic and validated in CI.
* Rust lockfiles should remain deterministic and validated in CI.
* Frozen or locked install/build modes SHOULD be used for CI reproducibility.
