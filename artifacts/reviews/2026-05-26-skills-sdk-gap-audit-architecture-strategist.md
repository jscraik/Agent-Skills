# Review: architecture-strategist

## Findings

### High: Project manifest is consumed without schema validation, allowing silent boundary drift
- Evidence:
  - [skills_impl.py:2513](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2513) loads `skills-sdk.json` with `json.loads` and only checks `schema_version`.
  - [skills_impl.py:2527](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2527) only rejects duplicate normalized root paths; it does not validate required fields, trust policy, precedence policy, or root default flags.
  - [skills_impl.py:2541](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2541) uses this partially-validated manifest for ownership decisions.
- Why this matters architecturally:
  - Boundary ownership is a Type 1 control-plane concern. A malformed manifest can be silently treated as valid enough for routing/ownership checks, which undermines source/projection integrity at the point of policy enforcement.
- Miss in audit:
  - The audit labels project manifest support as schema-backed/partial, but misses that runtime consumption path bypasses schema validation entirely.

### High: Rename/productization blast radius is undercounted; identity is hardcoded in stable interfaces
- Evidence:
  - Schema IDs are anchored to `agent-skills.local` across core contracts, e.g. [skill-doctor.v1.schema.json:3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skill-doctor.v1.schema.json:3), [skill-package.v1.schema.json:3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skill-package.v1.schema.json:3), [skills-sdk.project.v1.schema.json:3](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:3).
  - Package provenance trust accepts brand-specific sources in [package_verify.py:20](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py:20).
  - Plugin/runtime identity also assumes `agent-skills-local`, e.g. [plugin_cache.py:232](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/services/plugin_cache.py:232), [plugin_state.py:172](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/plugin_state.py:172).
- Why this matters architecturally:
  - A future repo rename is not just branding; it is protocol identity migration. Without an aliasing/versioning plan, downstream validators, cached plugin selectors, and package trust checks can break.
- Miss in audit:
  - Audit flags rename timing, but not the concrete compatibility strategy needed for contract IDs/provenance names/runtime selectors.

### Medium: Command-surface authority is duplicated, creating drift risk for SDK namespace rollout
- Evidence:
  - Parser action surface is hardcoded in [Infrastructure/bin/ask:119](/Users/jamiecraik/dev/agent-skills/Infrastructure/bin/ask:119) onward via argparse subparsers.
  - A second action registry is hardcoded in [command_metadata.py:7](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/command_metadata.py:7) and [command_metadata.py:10](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/command_metadata.py:10).
- Why this matters architecturally:
  - Adding `skills sdk` requires touching at least two command authorities plus help/error flows. This is a coupling hotspot and raises regression risk for user guidance and robot-mode recovery.
- Miss in audit:
  - Audit identifies missing `skills sdk`, but not the structural command-metadata duplication that makes rollout brittle.

### Medium: Project manifest schema permits ambiguous lifecycle defaults; runtime loader does not guard them
- Evidence:
  - Schema requires booleans `default_for_create/install/update` per root but does not constrain cardinality (zero or many true values allowed): [skills-sdk.project.v1.schema.json:73](/Users/jamiecraik/dev/agent-skills/Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:73).
  - Runtime loader does not enforce uniqueness of default flags: [skills_impl.py:2527](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/skills_impl.py:2527).
- Why this matters architecturally:
  - As soon as create/install/update are productized, default target root selection can become nondeterministic or policy-dependent in ad hoc ways.
- Miss in audit:
  - Audit recommends sdk init/doctor but does not call out this latent ambiguity in declared root targeting.

## Missing Improvements
- Add a single canonical manifest-validation entrypoint used by all ownership/resolution/lifecycle codepaths, not just tests.
- Introduce a stable identity layer now:
  - keep current IDs as legacy aliases,
  - add neutral canonical IDs (e.g. `skills-sdk.local`),
  - version migration in contract docs and validators.
- Generate `VALID_ACTIONS` (or argparse definitions) from one source to remove parser/metadata drift.
- Add explicit cardinality rules for project-root defaults:
  - exactly one default for each lifecycle action, or explicit `none` with blocked status and remediation.

## Rename/Productization Risks
- Contract ID breakage risk:
  - External tools validating by `$id` may fail if IDs are renamed without alias support.
- Provenance trust regression:
  - Package verification currently trusts `agent-skills`-named sources; pure rename can break trust decisions unless dual acceptance is preserved.
- Runtime selector drift:
  - Plugin/runtime labels (`agent-skills-local`) are embedded in cache/state logic and config snippets; rename can orphan existing local runtime state.
- Human/operator confusion:
  - Project manifest filename `skills-sdk.json` vs repo control-plane file `Infrastructure/config/skills-sdk.json` creates same-name different-scope ambiguity unless docs and tooling consistently distinguish owner-manifest vs SDK-control manifest.

## Recommended Next Patch
- Smallest high-leverage patch:
  - Harden `_load_project_skills_sdk_manifest` to validate against `skills-sdk.project.v1` schema and enforce default-flag cardinality before returning any manifest used for ownership decisions.
- Validation command:
  - `python3 -m unittest Infrastructure.tests.test_ask_cli_impl Infrastructure.tests.test_jsc351_codex_abi_schema_contracts`

## Coverage Notes
- Inspected:
  - Updated audit file.
  - Skills CLI surface behavior (`./bin/ask skills --help`, `./bin/ask skills sdk --help`).
  - Command parser and metadata registries.
  - Skills SDK config and project manifest schema.
  - Manifest loader/ownership code path.
  - Package verification provenance controls.
- Did not inspect in depth:
  - Full lifecycle-and-sync script family behavior beyond contract references.
  - All downstream consumers of schema `$id` values outside this repo.
  - End-to-end plugin runtime cache migration behavior in external environments.

WROTE: artifacts/reviews/2026-05-26-skills-sdk-gap-audit-architecture-strategist.md

