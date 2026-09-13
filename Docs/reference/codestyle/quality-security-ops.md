# Quality Security And Operations Standards

Applies to the matching changed surface. Use repository commands and lockfiles
for the actual toolchain; unrelated technology sections do not add checks.

## 15. Quality Gates: Coverage, Mutation, TDD

The PR workflow runs the repository's typecheck, test, audit, and check scopes.
It does not enforce branch-coverage or mutation-score thresholds or consume
environment overrides for those scores. Do not report either as a passing
merge gate without an executable check and its recorded result.

### Program-design enforcement

The repository's `program-design` gate ratchets oversized public interfaces,
boolean default arguments, broad exception handlers, explicit `global`
statements, and module-level mutable state. In changed-files mode it compares
the patch with `HEAD` and fails only on new or worsened findings in those
categories. It does not measure coverage or mutation scores. Existing debt remains visible for a bounded
refactoring slice rather than making unrelated changes fail. This is a
low-noise baseline, not a claim that static analysis can decide every
abstraction or responsibility boundary.

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
* Rules of AI: applicable repository `AGENTS.md` files

---
