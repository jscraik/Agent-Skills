# Common Codestyle Foundations

Applies to the matching changed surface. Use repository commands and lockfiles
for the actual toolchain; unrelated technology sections do not add checks.

## Toolchain Baselines

- JS/TS: Biome, ESLint v9 flat config, TypeScript typecheck, and Vitest/Node test.
- Docs: Vale.
- Python: Ruff, Pyright, and pytest.
- Rust: rustfmt, Clippy, and cargo test.
- Security/policy: Semgrep, AST/pattern guards, supply-chain scanners, and
  SBOM/provenance tooling where selected by the repository contract.
- Baseline versions: Node 24, TypeScript >= 5.9, Rust 2024 edition with
  rustc >= 1.85. Resolve actual versions from the current `.mise.toml`,
  manifests, and lockfiles rather than an absent compatibility file.
- Security advisories override baselines; affected projects must adopt the
  patched version through the authorized dependency-change workflow.

## 0. Gold Production Standards (Hard Prohibitions)

**ABSOLUTE PROHIBITION** — It is a policy violation to ship or describe anything as “production-ready”, “complete”, “operational”, or “fully implemented” if any of the following exist anywhere in a **production code path**:

- Fabricated data/entropy: `Math.random()` (or equivalent) used to fabricate data without injected seed
- Hard-coded mock responses in production paths
- `TODO`/`FIXME`/`HACK` comments in production paths
- Incomplete stub paths or future-only behavior
- Disabled features signaling gaps (warning-only paths, dead flags)
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
- Violations must be fixed or the owning surface must be retired; no waiver path exists.

---

## 1. General Principles

- **Functional-first**: prefer pure, composable functions.
- **Classes**: only when required by a framework or to encapsulate unavoidable state.
- **Functions**: SHOULD be <= 40 LOC; split if readability suffers.
- **Program design**: architecture diagrams describe component boundaries; every implementation change MUST also be reviewed for function responsibility, abstraction level, data flow, side effects, failure paths, and caller knowledge.
- **Small interfaces**: public Python functions SHOULD keep at most five parameters. Group cohesive data in a named value object when the interface would otherwise grow.
- **Flag arguments**: public functions MUST NOT add boolean default arguments to select materially different behavior. Split the commands or use an explicit policy/value object instead.
- **State and errors**: changed Python production code MUST NOT add module-level mutable state, explicit `global` statements, or broad `except Exception`/`except BaseException`/bare handlers.
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

## 16. Fast Tools (MANDATORY for agents)

* Use `rg` not `grep` for project-wide search.
* Prefer `fd` for file finding.
* Use `jq` for JSON parsing/transformations.
* Read limits: cap reads at ~250 lines; prefer targeted context flags.

---
