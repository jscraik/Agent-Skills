# Quality, Security, and Operations Standards

## Table of Contents
- [Scope](#scope)
- [Detailed modules](#detailed-modules)
- [15. Quality Gates: Coverage, Mutation, TDD](#15-quality-gates-coverage-mutation-tdd)
- [16. Fast Tools (MANDATORY for agents)](#16-fast-tools-mandatory-for-agents)
- [17. Security, Supply Chain & Compliance](#17-security-supply-chain--compliance)
- [18. Accessibility](#18-accessibility)
- [19. Observability, Logging & Streaming](#19-observability-logging--streaming)
- [20. Resource Management & Memory Discipline](#20-resource-management--memory-discipline)
- [21. Repository Scripts & Reports](#21-repository-scripts--reports)
- [22. MCP & External Tools](#22-mcp--external-tools)
- [23. Config References (Authoritative)](#23-config-references-authoritative)

## Scope
- This module is a cross-cutting quality/security/operations umbrella.
- Topic-specific policy details are defined in dedicated modules listed below.

## Detailed modules
- Git workflow: [13-git-workflow.md](./13-git-workflow.md)
- Patterns: [14-patterns.md](./14-patterns.md)
- Performance: [15-performance.md](./15-performance.md)
- Security: [16-security.md](./16-security.md)
- Testing: [17-testing.md](./17-testing.md)
- Code review: [18-code-review.md](./18-code-review.md)
- Development workflow: [19-development-workflow.md](./19-development-workflow.md)

## 15. Quality Gates: Coverage, Mutation, TDD

PR merge gate MUST pass the repository contract commands:

* `pnpm lint`
* `pnpm typecheck`
* `pnpm test`
* `pnpm audit`
* `pnpm check`
* `bash scripts/validate-codestyle.sh`
* `bash scripts/verify-work.sh --fast`

Coverage and mutation thresholds MAY be enforced only when wired to executable repository validators.

---

## 16. Fast Tools (MANDATORY for agents)

* Use `rg` not `grep` for project-wide search.
* Prefer `fd` for file finding.
* Use `jq` for JSON parsing/transformations.
* Shell scripts that inspect JSON MUST use `jq` or a typed language helper;
  regex, `sed`, `awk`, or string slicing MUST NOT parse JSON.
* When `jq` is used in shell, pass shell values with `--arg` or
  `--argjson` and use `-e` when the filter result is the command success
  condition.
* Prefer repo-owned wrappers for toolchain setup. If several scripts need the
  same `uv`, Node, Semgrep, or package-manager environment, centralize that
  setup in the approved helper (for example `scripts/run-uv-python.sh`) and
  route package scripts through it.

* For TypeScript-family source, agents MUST run
  `bash scripts/harness-cli.sh source-outline <path> --json` before reading full
  file bodies; agents SHOULD unwrap implementation only for the needed symbol
  with `--symbol <name>`. Downstream repositories that consume the packaged CLI
  directly MAY use `harness source-outline <path> --json` instead.

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

* Biome: `biome.json`
* Vale: `.vale.ini`
* Markdownlint: `.markdownlint-cli2.yaml`
* Mise: `.mise.toml`
* TypeScript: `tsconfig.json`
* Vitest: `vitest.config.ts` and `e2e/vitest.e2e.config.ts`
* CircleCI: `.circleci/config.yml`
* GitHub Actions release workflows: `.github/workflows/*.yml`
* Semgrep/security policy: `semgrep*.yml` and repository security scripts where present
* ESLint/Rustfmt: downstream-only unless the repository includes `eslint.config.*` or `rustfmt.toml`

---
