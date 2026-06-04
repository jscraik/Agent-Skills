# ADR: JSC-391 Skills SDK Path Map And Existing Source Inventory

## Status

Accepted for JSC-391 scaffold/refactor work.

## Context

JSC-391 is a scaffold/refactor gate for future Skills SDK work. It must create
agent-first landing zones without implementing new user-facing SDK behavior and
without treating generated runtime projections as editable source.

PU-001 captured the baseline in
`.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/pu-001-baseline.json`.
That baseline proves the repository is readable, the selected existing skill
handle is `ubiquitous-language`, and all tracked modules under
`Infrastructure/scripts/lib/ask/skills_sdk/**` currently import. It also records
isolated-worktree setup debt: `repo doctor`, `skills prove`, and changed-file
closeout block on missing generated runtime projection/command-handle surfaces.

Current path ownership guidance in `Docs/agents/14-path-ownership-boundaries.md`
defines `.agents/**`, `.skillsets/**`, `skills-codex/**`,
`Plugins/cache/**`, `runtime/**`, and root `SKILL.md` as derived or runtime
surfaces that must not be hand-edited. This ADR preserves that boundary.

## Decision

Use these physical paths for JSC-391:

| Logical landing zone | Selected physical path | Decision |
| --- | --- | --- |
| SDK core | `Infrastructure/scripts/lib/ask/skills_sdk/**` | Existing extractable service layer remains the SDK core while `./bin/ask` stays the control plane. |
| Deep module contracts | `Docs/reference/skills-sdk/modules.md` plus `.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json` | Human-readable contracts live in reference docs; machine-readable routing lives in the ownership map. |
| Schemas | `Infrastructure/config/schemas/skills-sdk/**` | Existing schema convention is under `Infrastructure/config/schemas`; a nested SDK folder avoids root schema ambiguity. |
| Runtime | `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py` for current behavior; future docs/shells may live under `Infrastructure/scripts/lib/ask/skills_sdk/runtime/**` only after PU-003 | Existing runtime reachability behavior is already owned by `runtime_adapters.py`; do not duplicate it. |
| Packaging | `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py` and `package_verify.py`; future docs/shells may live under `Infrastructure/scripts/lib/ask/skills_sdk/packaging/**` only after PU-003 | Existing package contracts and archive verification stay preserved. |
| Signing | `Infrastructure/config/schemas/skills-sdk/signing-placeholder.v1.schema.json` and `Docs/reference/skills-sdk/modules.md` | Placeholder contract only; no signing execution, key handling, trust-store writes, registry publication, or package upload. |
| Evals | `Infrastructure/scripts/lib/ask/skills_sdk/evals/**` for future contract helpers after PU-003; fixtures under `Infrastructure/tests/fixtures/skills_sdk/**` | Evals are contract/fixture-owned in JSC-391, not external Tessl requirements. |
| Fixtures | `Infrastructure/tests/fixtures/skills_sdk/**` | Matches existing `Infrastructure/tests/fixtures/**` convention. |
| Examples | `Docs/examples/skills-sdk/**` | Existing examples are under `Docs/examples`; avoid adding a new root-level examples tree. |
| Canon/reference docs | `Docs/reference/skills-sdk/**` | Repo already has `Docs/reference`; this is the canonical docs equivalent for SDK contracts. |
| Decisions | `.harness/decisions/**` | HE-scoped implementation decisions belong beside existing harness ADRs. |
| Receipts and evidence | `.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/**` | Keeps baseline, inventory, maps, post-change receipts, and crosswalk proof together. |

The parseable module ownership map is:

`.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json`

The tracked SDK inventory is:

`.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/sdk-inventory.json`

Changing these selected paths requires amending this ADR before implementation
writes to a rejected alternative.

## Existing SDK Source Inventory

The tracked source files under `Infrastructure/scripts/lib/ask/skills_sdk/**`
are inventoried in
`.harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/sdk-inventory.json`.
Generated `__pycache__/**` paths are excluded.

Classification summary:

| Source file | Classification | Rationale |
| --- | --- | --- |
| `__init__.py` | preserve | Package boundary marker with no public symbols. |
| `conformance.py` | preserve | Owns current codex-parity conformance fixtures and modeled/live status separation. |
| `contracts.py` | preserve | Owns shared doctor, validation command, frontmatter, and runtime failure vocabulary. |
| `package_contracts.py` | preserve | Owns package metadata/readiness contracts, schema paths, and skillflow/optimization contract helpers. |
| `package_verify.py` | preserve | Owns package/archive verification, provenance, manifest, and runtime mutation sentinel checks. |
| `runtime_adapters.py` | preserve | Owns current command-handle proof, runtime target, redaction, and runtime evidence emission. |

No existing tracked SDK source file is moved in PU-002. Future module shells
must wrap or collaborate with these files instead of duplicating their behavior.

## Rejected Alternatives

| Rejected path or approach | Reason |
| --- | --- |
| `.agents/**`, `.agents/skills/**` | Runtime Projection in this repository; generated command-handle surface, not canonical source. |
| `.skillsets/**` | Generated rooted manifest rows; source of truth is canonical skills/plugins and generator code. |
| `skills-codex/**` | Generated/runtime surface. |
| `Plugins/cache/**` | Mirrored output; not a scaffold source path. |
| `~/.agents/skills/**` and `~/.codex/skills/**` | User runtime links/projections, outside repo source ownership. |
| Root `SKILL.md` | Generated index surface, refreshed by sync rather than hand-edited. |
| Root `schemas/skills-sdk/**` | Would split schema convention from existing `Infrastructure/config/schemas/**`. |
| Root `examples/skills-sdk/**` | Repo examples convention is under `Docs/examples/**`; a new root adds ambiguity. |
| `Docs/canon/skills-sdk/**` | No current `Docs/canon` convention exists; `Docs/reference/**` is the repo-native canonical reference surface. |
| New CLI command files for JSC-391 | The slice is scaffold/refactor only and must not introduce user-facing feature behavior. |
| New signing, sandbox, eval execution, install, registry, or publish code | Out of scope for JSC-391; placeholders must be explicit and parseable. |

## Consequences

- PU-003 can add or update module contract docs and, only where justified, thin
  package markers or README files under selected SDK source paths.
- PU-004 can add fixtures/placeholders only under the selected paths and must
  parse or schema-check every placeholder.
- PU-005 tests must consume the module ownership map directly so future agents
  cannot bypass the path-map with prose-only claims.
- PU-006 post-change compatibility must compare against PU-001 receipts by
  structured fields, not narrative similarity.
- Feature implementation planning remains blocked until the parent V1 crosswalk
  has no unresolved `blocked_parent_acceptance` rows.
