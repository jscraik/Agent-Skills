# Product-Factory-Runtime Separation Plan

## Table of Contents
- [Goal](#goal)
- [Scope](#scope)
- [Current constraints](#current-constraints)
- [Target layout](#target-layout)
- [Task graph](#task-graph)
- [Canonical identity contract](#canonical-identity-contract)
- [Migration mechanism contract](#migration-mechanism-contract)
- [Forwarder type contract](#forwarder-type-contract)
- [Compatibility state machine](#compatibility-state-machine)
- [Path contract compatibility](#path-contract-compatibility)
- [Plugin activation contract](#plugin-activation-contract)
- [Derived artifact lifecycle contract](#derived-artifact-lifecycle-contract)
- [Writer and Reader Authority Contract](#writer-and-reader-authority-contract)
- [Promotion Evidence Contract](#promotion-evidence-contract)
- [Parity artifact contract](#parity-artifact-contract)
- [Slice contract](#slice-contract)
- [Phases](#phases)
- [Compatibility mapping](#compatibility-mapping)
- [User-facing acceptance matrix](#user-facing-acceptance-matrix)
- [Validation ladder](#validation-ladder)
- [Risks and rollback](#risks-and-rollback)
- [Definition of done](#definition-of-done)

## Goal

Separate canonical product content from mechanics and runtime projections without disrupting existing skill and plugin workflows.

## Scope

In scope:
- establish one canonical authoring root for first-party skills and plugin-owned skills;
- isolate factory mechanics into an explicit implementation lane;
- isolate runtime/projection surfaces as derived outputs;
- preserve command contracts during migration;
- define measurable phase gates and rollback conditions.

Out of scope:
- plugin marketplace protocol changes;
- skill content rewrites not required for path migration;
- one-shot path moves without compatibility and validation gates.

## Current constraints

These are hard constraints from the current repo state and scripts:
- `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` rejects a symlinked `skills-antigravity` path. Any plan requiring that symlink is invalid.
- local marketplace runtime cache authoritative derived location is `.agents/plugins-runtime/cache/**`.
- legacy visible local marketplace cache `Plugins/cache/agent-skills-local/**` must stay removed and must not be reintroduced as compatibility output.
- runtime/projection surfaces (`.agents/**`, `.agents/skills/**`, `skills-antigravity/**`, `Plugins/cache/**`, `runtime/**`) are governed by path-ownership checks and must remain derived.
- governance ownership docs use the existing uppercase root `GOVERNANCE/**` for control-plane policy content.

## Target layout

Planned topology:
- `Infrastructure/catalog/skills/<category>/<skill>/SKILL.md` for first-party canonical skill sources.
- `Infrastructure/catalog/Plugins/<plugin>/.codex-plugin/plugin.json` as canonical plugin package manifest, with plugin skill content under `Infrastructure/catalog/Plugins/<plugin>/skills/<category>/<skill>/SKILL.md`.
- `Infrastructure/factory/**` for sync, graph, install, validation, and projection mechanics.
- `runtime/**` for repository-local derived projections only.
- `GOVERNANCE/**` for policy contracts, ownership rules, and CI-check parity docs.

During migration, legacy canonical paths are retained only through explicitly selected compatibility mechanisms (see migration mechanism contract).

## Task graph

```yaml
tasks:
  - id: P0
    title: "Phase 0: control-plane abstraction prerequisite"
    depends_on: []
  - id: PA
    title: "Phase A: ownership enforcement and projection contract freeze"
    depends_on: [P0]
  - id: PB
    title: "Phase B: mechanics extraction"
    depends_on: [PA]
  - id: PC
    title: "Phase C: first-party canonical relocation"
    depends_on: [PB]
  - id: PD
    title: "Phase D: plugin canonical relocation"
    depends_on: [PC]
  - id: PE
    title: "Phase E: runtime lane consolidation"
    depends_on: [PD]
  - id: PF
    title: "Phase F: compatibility cleanup"
    depends_on: [PE]
```

## Canonical identity contract

Duplicate detection and runtime precedence are keyed by this identity:
- `owner_kind`: `first_party` or `plugin`
- `owner_name`: `repo` for first-party, `<plugin>` for plugin-owned paths
- `category_name`: canonical category segment for category-addressed skills
- `runtime_name`: directory basename; this is the blocking uniqueness key for discovery, `ask skills list`, and plugin-shadowing checks during migration
- `metadata_name`: frontmatter `name` when present; this must equal `runtime_name` unless an explicit compatibility alias is declared and tested
- `discovery_surface`: `skills_default`, `skills_category`, `plugins_status`, or other explicitly named discovery surface exported by policy
- `lane_role`: `default_visible`, `advanced_visible`, `hidden_flat`, `plugin_hidden`, or `system_bridge`
- `overlap_class`: `none` by default; non-`none` values require explicit allowlist policy and tests

Identity string format:
- `<owner_kind>:<owner_name>:<runtime_name>`

Rules:
- no two canonical or compatibility artifacts may expose the same `runtime_name` in the same `discovery_surface`, unless the overlap is explicitly allowlisted and tested;
- no two canonical skills may share the same `<category_name>/<runtime_name>` tuple unless explicitly allowlisted and tested;
- lane semantics must remain parity-stable: migration cannot move a skill between `lane_role` classes without explicit planned delta approval;
- `metadata_name` drift is a validation failure, not a separate identity namespace;
- duplicate, freshness, and shadowing validators must import one shared identity helper before any content move;
- allowlisted overlap classes must be declared in policy exports and validated by shadowing tests.

## Migration mechanism contract

Per slice, compatibility is modeled on two independent axes:
- `discovery_compatibility`: `catalog_only` or `dual_read`.
- `path_compatibility`: `resolver_only`, `filesystem_forwarder`, or `combined`.

Rules:
- `dual_read` is allowed only while `activation_state` is one of `pre_activation` or `rollback_pending`;
- `filesystem_forwarder` entries are compatibility artifacts and never discoverable roots;
- the commit that flips `activation_state` from `pre_activation` to `migrated` must simultaneously remove the legacy canonical source or replace it with a declared forwarder;
- no post-activation commit may leave both legacy and catalog canonical sources readable;
- slices with unresolved path consumers cannot use `path_compatibility=resolver_only`;
- default for phases C and D:
  - pre-activation: `discovery_compatibility=dual_read`, `path_compatibility=combined`;
  - migrated before cleanup: `discovery_compatibility=catalog_only`, `path_compatibility=filesystem_forwarder` unless resolver coverage is complete;
  - post-cleanup (cleanup-eligible slices): `discovery_compatibility=catalog_only`, `path_compatibility=resolver_only`;
- plugin package-root slices that must preserve `source.path=./Plugins/<plugin>` are not cleanup-eligible in this plan and remain `path_compatibility=filesystem_forwarder` in `migrated` state until a separate marketplace-contract migration;
- if a lane requires `filesystem_forwarder`, record forwarder type and validator coverage in the slice manifest before promotion.

## Forwarder type contract

`filesystem_forwarder` is a closed taxonomy. Allowed `forwarder_type` values:
- `resolver_alias`: no on-disk mirror; resolver maps legacy path requests to canonical targets.
- `directory_projection`: generated directory mirror for legacy read compatibility; generated artifacts only.
- `package_root_projection`: generated compatibility package root at `Plugins/<plugin>` for marketplace `source.path` compatibility while canonical package content lives at `Infrastructure/catalog/Plugins/<plugin>`.
- `wrapper_index`: wrapper/index indirection for command/path compatibility without legacy content ownership.

Rules:
- every slice using `path_compatibility` containing `filesystem_forwarder` must declare exactly one allowed `forwarder_type`;
- each `forwarder_type` must have explicit validator coverage in slice checks;
- unlisted forwarder implementations are forbidden;
- symlink-based forwarders are forbidden unless explicitly allowlisted by policy for antigravity sync-source compatibility.

## Compatibility state machine

Each slice must use this lifecycle:
- `declared`: slice defined in manifest; no path behavior changes.
- `pre_activation`: dual-read and path compatibility are enabled by declared compatibility fields.
- `migrated`: catalog canonical source active; legacy canonical source removed or forwarded.
- `rollback_pending`: activation failed or regression found; rollback commands required.
- `rolled_back`: slice restored to previous state and validated.
- `cleanup_complete`: cleanup-eligible slice forwarders removed after resolver coverage and exit checks are complete.

Allowed transitions:
- `declared -> pre_activation -> migrated -> cleanup_complete`
- `declared -> pre_activation -> migrated` for plugin package-root slices that retain compatibility package roots in this plan
- `migrated -> rollback_pending -> rolled_back`
- `rolled_back -> pre_activation` only after root cause is documented.

Activation execution model:
- `activating` is an execution substep inside the `pre_activation -> migrated` transition and is not persisted as an `activation_state` value in `slices.yaml`.

State transition gate:
- every transition is advanced by one reviewed migration state change in a PR and must include transition-specific validation evidence.
- one reviewed migration state change may advance at most one `activation_state` step for a given slice.
- transition semantics are strict:
  - `pre_activation`: `discovery_compatibility=dual_read` is required.
  - `migrated`: same commit must set `discovery_compatibility=catalog_only` and complete source-to-forwarder cutover.
  - `rollback_pending`: `dual_read` may be temporarily restored only through declared `rollback_commands`.
  - once a slice enters `pre_activation`, all write flows for that slice must resolve to `authoritative_write_root`; legacy paths may remain readable/forwarded but are not directly writable except declared forwarder generation.

## Path contract compatibility

Command compatibility includes path-addressed workflows:
- category-relative skill paths accepted or emitted today must continue to resolve through Phase F;
- canonical category path schema is `Infrastructure/catalog/skills/<category>/<skill>/SKILL.md` (and plugin-owned `Infrastructure/catalog/Plugins/<plugin>/skills/<category>/<skill>/SKILL.md`);
- each migrated slice must provide path compatibility via `filesystem_forwarder` or `combined` until all path consumers use a shared resolver contract;
- resolver-only mode is allowed only after explicit resolver-coverage evidence for path-accepting commands;
- phase promotion must test both legacy and catalog paths for at least one migrated slice while compatibility artifacts exist.

Terminal state:
- category-relative `<category>/<skill>` CLI compatibility remains supported via shared resolver contract after Phase F;
- filesystem forwarders are removed only after resolver migration is complete and all slice exit checks remain green.

## Plugin activation contract

Plugin canonical relocation must preserve plugin activation semantics during and after Phase D:
- plugin discovery readers must be migrated from `Plugins/*` canonical-root assumptions to policy-backed roots that include `Infrastructure/catalog/Plugins/**`;
- marketplace `source.path` resolution must remain valid for `bin/ask plugins status` and `bin/ask plugins doctor`;
- workspace/profile projection generation and plugin runtime cache generation must read from the same policy-exported canonical roots;
- canonical plugin package ownership migrates to `Infrastructure/catalog/Plugins/<plugin>/.codex-plugin/plugin.json`;
- until marketplace contract version changes, marketplace `source.path` remains `./Plugins/<plugin>`;
- `Plugins/<plugin>` remains a compatibility package root (never an authoritative source root) for repo and profile-home sync;
- during compatibility mode, all manifest-declared package-relative assets must resolve identically from `Plugins/<plugin>` and `Infrastructure/catalog/Plugins/<plugin>` (`.codex-plugin/plugin.json`, `skills/**`, `agents/**`, `hooks/**`, MCP metadata, templates, install scripts, and manifest-referenced docs);
- no command may treat `Plugins/<plugin>` as an authoritative write root;
- legacy `Plugins/<plugin>` paths are compatibility directories only and may not remain canonical package sources;
- phase promotion is blocked if baseline comparator output reports plugin activation/status parity regressions for unchanged plugins, including package-relative asset resolution parity.

Package-root resolution contract:
- canonical package root is `Infrastructure/catalog/Plugins/<plugin>`;
- `Plugins/<plugin>` is a generated `forwarder_type=package_root_projection` compatibility root and never an authoritative source root;
- marketplace `source.path=./Plugins/<plugin>` resolves to the generated projection during compatibility mode;
- manifest-relative asset resolution is defined against canonical package content and must remain parity-equivalent in the generated projection for all manifest-declared relative assets (`skills/**`, `agents/**`, `hooks/**`, MCP metadata, templates, install scripts, and manifest-referenced docs);
- direct edits under `Plugins/<plugin>` are forbidden except declared projection generation writers.

## Derived artifact lifecycle contract

Derived surfaces (`runtime/**`, `.agents/**`, `.agents/skills/**`, `skills-antigravity/**`, `.agents/plugins-runtime/cache/**`) require deterministic lifecycle handling:
- before slice activation or rollback validation, purge stale derived artifacts for affected slices;
- regenerate projections/caches from declared canonical roots;
- run validation only after clean reprojection; previous artifacts are not considered valid evidence;
- slice manifests must record required purge/regenerate commands in `entry_checks`, `exit_checks`, and `rollback_commands`.

## Writer and Reader Authority Contract

Reader routing and writer routing must both be explicit and single-owner during migration:
- readers: all selection/discovery readers consume only manifest-derived policy exports;
- writers: each runtime/projection surface has exactly one authoritative writer at any point in slice lifecycle;
- non-authoritative writers are blocked by ownership guards except for declared forwarder generation.

Required per-surface authority table fields in governance docs:
- `surface`, `authoritative_writer`, `authoritative_reader`, `input_roots`, `purge_rule`, `forwarder_allowed`, `rollback_owner`.

Required per-slice manifest fields:
- `authoritative_write_root`
- `inventory_selector`
- `path_consumer_inventory_ref`
- `path_consumer_inventory_digest`
- `reader_inventory_ref`
- `reader_inventory_digest`
- `policy_export_version`

Digest semantics:
- `path_consumer_inventory_digest` and `reader_inventory_digest` are computed over selector-scoped rows identified by `inventory_selector`, not whole-file inventory content.

## Promotion Evidence Contract

Promotion and rollback decisions are machine-checkable baseline diffs, not prose comparisons.

Phase 0 must produce baseline artifacts:
- `GOVERNANCE/runtime-separation/baseline.json`
- `GOVERNANCE/runtime-separation/baseline.schema.json`

Required comparator:
- `python3 Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current <artifact>`
- current artifact producer: `python3 Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py --output GOVERNANCE/runtime-separation/current.json`

Comparator output must provide:
- stable blocker ids;
- drift class;
- severity mapping;
- command source;
- allowed delta decision.
- planned delta application result.

Comparator input contract:
- `current.json` stores normalized migration-owned invariants only: reader root set, writer authority map, plugin activation parity, visible-cache absence, duplicate/shadow drift classes, and selected command-level blocker summaries;
- aggregate command outputs (`repo validate`, `plugins doctor`, and related flows) are normalized before comparison and do not compare full volatile envelopes.

## Parity artifact contract

Parity gates must compare deterministic fields emitted by the same build paths in both repo-local and profile-home lanes:
- `python3 Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py --output GOVERNANCE/runtime-separation/current.json` must emit:
  - `policy_identity` at `summary.policy_identity`;
  - `discovery_identity` at `summary.discovery_identity`;
  - `canonical_root_digest` at `summary.canonical_root_digest`.
- `bash Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh` must emit the same fields for profile-home evaluation under the same JSON paths.
- `policy_identity` is the deterministic hash over exported canonical root sets, discovery precedence, overlap allowlists, and writer-authority assignments after manifest expansion.
- `discovery_identity` is the deterministic hash over discovery-surface exports: visible runtime identities per surface, precedence order, and overlap-class allowlists after manifest expansion.
- `canonical_root_digest` is `sha256` over sorted lane-independent logical canonical root identities exported by policy (root ids/templates), not absolute filesystem paths.
- promotion and rollback parity checks compare those emitted fields only; prose summaries are non-authoritative.
- absolute-path and symlink-resolution checks remain local invariants and are validated separately from cross-lane parity identity.

Promotion rule:
- no new blocker ids/classes/severity regressions;
- allowlisted baseline blockers may remain only if unchanged and explicitly listed in baseline artifact.
- `baseline.json` is immutable after Phase 0 except for:
  - explicit per-slice `planned_deltas` entries reviewed in migration PRs; and
  - explicit phase-level control-plane baseline deltas reviewed in phase-promotion PRs (`phase_baseline_deltas`).
- each slice must declare `planned_deltas` with: `command`, `json_paths`, `allowed_old_to_new`, and `expiry_condition`.

## Inventory completeness contract

Inventory completeness is machine-checked before slice activation:
- generated `readers.yaml` and `path-consumers.yaml` come from repo-wide executable-consumer scanning plus explicit checked-in overrides;
- executable-consumer scope includes Python, shell, JS/TS, and tests that execute those consumers; markdown is blocking only when explicitly declared as normative machine-read input;
- informational plans/docs are non-blocking unless explicitly listed as normative input;
- completeness means zero unexplained executable direct-root matches;
- every remaining match must be allowlisted with `owner`, `slice_id`, `rationale`, and `expiry_condition`;
- each slice `inventory_selector` defines the subset rows from generated inventories used for that slice's digest checks;
- promotion is blocked when selected inventory rows for targeted slices drift and corresponding per-slice digests in `slices.yaml` are stale.

## Slice contract

All moves run by bounded, declared slices tracked in `GOVERNANCE/runtime-separation/slices.yaml`.
- Phase 0 must create `GOVERNANCE/runtime-separation/slices.yaml` before any path move.
- `GOVERNANCE/runtime-separation/slices.yaml` is the single mutable migration-state source for per-slice compatibility axes, precedence, and activation state.
- manifest top-level schema includes `schema_version`, `reader_min_version`, and `policy_export_version`.
- minimum per-slice schema: `id`, `phase`, `owner_lane`, `activation_state`, `discovery_compatibility`, `path_compatibility`, `discovery_precedence`, `forwarder_type`, `overlap_class`, `authoritative_write_root`, `inventory_selector`, `path_consumer_inventory_ref`, `path_consumer_inventory_digest`, `reader_inventory_ref`, `reader_inventory_digest`, `policy_export_version`, `canonical_paths`, `legacy_paths`, `planned_deltas`, `representative_commands`, `plugin_lifecycle_checks`, `entry_checks`, `exit_checks`, `rollback_commands`.
- each slice is atomic for rollback only when canonical-content move, manifest update, and slice-specific compatibility wiring are committed together.
- each slice is capped to one ownership lane at a time (`skills` or `plugins`, never mixed).
- a PR may advance only slices already declared in the manifest.
- no phase promotion until all slice exit checks are green.
- schema compatibility requirement: every reader with `consumes_manifest_schema=true` in `GOVERNANCE/runtime-separation/readers.yaml` must prove `N` and `N-1` compatibility before phase promotion, where `N` is the current `schema_version` value in `slices.yaml`.
- every reader inventory entry must declare `consumes_manifest_schema`, `supported_schema_versions`, and `compat_test_command`.
- `representative_commands` entries are structured tuples: `command`, `comparison_mode` (`both|legacy_only|canonical_only`), `args_legacy`, `args_canonical`, `expected_exit_code`, `normalized_assertions`, `expected_result_ref`.
- `plugin_lifecycle_checks` entries are structured tuples: `id`, `command`, `args`, `expected_exit_code`, `normalized_assertions`, `applies_to_phase`, `applies_to_rollback`.
- `plugin_lifecycle_checks.applies_to_phase` is a set of phase keys (`phase_a`..`phase_f`) or `all`; consuming gates must filter checks by active phase key.
- `plugin_lifecycle_checks.applies_to_rollback` is boolean; rollback gates select only entries with `applies_to_rollback=true`.
- all selected `plugin_lifecycle_checks` must be evaluated against their full tuple contract: execute `command`+`args`, assert `expected_exit_code`, and verify `normalized_assertions`.

Control-plane ownership rules:
- `slices.yaml` is the only mutable migration-state source;
- `selection_policy.py` owns invariant policy schema and export shape only;
- policy exports are generated/derived from `slices.yaml` and cannot be edited directly;
- `GOVERNANCE/runtime-separation/readers.yaml` and `GOVERNANCE/runtime-separation/path-consumers.yaml` are generated authoritative audit inventories for reader/consumer completeness gates;
- governance authority tables are generated documentation only and cannot alter activation behavior;
- no static root list in code may affect runtime root selection after Phase 0 exit.

## Phases

0. Phase 0: control-plane abstraction prerequisite
- Entry criteria:
  - record a Phase 0 baseline artifact before migration work, capturing outputs of:
    - `bin/ask repo status`
    - `bin/ask skills list --json`
    - targeted baseline plugin status checks from declared slices: `bin/ask plugins status <plugin> --json`
    - `bin/ask plugins doctor --json`
    - `bin/ask repo validate`
    - `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
    - `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
    - `bash Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh`
    - `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`
    - `bin/ask repo doctor-catalog --strict`
  - baseline must include `accepted_preexisting_blockers` entries with blocker id, source command, owner, drift class, and rationale.
  - baseline policy is explicit: either `bin/ask repo doctor-catalog --strict` is green, or only allowlisted baseline drift classes are present and no new/worse drift is allowed.
- Actions:
  - create `GOVERNANCE/runtime-separation/slices.yaml`, `GOVERNANCE/runtime-separation/slices.schema.json`, and `Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py`;
  - create generated authoritative inventory outputs `GOVERNANCE/runtime-separation/readers.yaml` and `GOVERNANCE/runtime-separation/path-consumers.yaml`;
  - create `GOVERNANCE/runtime-separation/baseline.json`, `GOVERNANCE/runtime-separation/baseline.schema.json`, `Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py`, and `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py`;
  - create `Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py` with fixture-driven `N`/`N-1` coverage;
  - create `Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh --strict` for authoritative-writer enforcement;
  - create `Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh` for ephemeral profile-home projection validation;
  - create `Infrastructure/scripts/runtime-separation/scan_runtime_separation_consumers.py --emit-readers --emit-path-consumers --emit-digests` and gate stale digest drift;
  - create `Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh --runtime-separation` with fixture set for argv, exit codes, output markers, and JSON schema expectations;
  - make scan roots and identity canonical in shared policy (`selection_policy.py`) and ensure loaders consume policy exports rather than hard-coded root sets;
  - add `Infrastructure/catalog/**` root support behind migration flags; flags only enable manifest-aware behavior and may not encode per-slice migration state;
  - codify canonical identity checks in freshness validation;
  - audit repo consumers for direct reads of legacy canonical roots and route them through policy-backed discovery APIs using generated inventories as the authoritative allowlist source;
  - wire manifest validation into `bash Infrastructure/scripts/validate_all.sh` and `bin/ask repo validate`;
  - add required policy/discovery identity parity tests and wrapper contract tests.
  - run Phase 0 in two sub-gates:
    - `phase_0a_control_plane`: baseline/inventory/schema/comparator/wrapper-contract machinery;
    - `phase_0b_pilot_slice`: one declared pilot slice must prove `pre_activation -> migrated` cutover and rollback evidence via slice representative commands and lifecycle checks.
- Exit criteria:
  - policy identity and discovery identity remain aligned against the baseline artifact;
  - duplicate, freshness, and shadowing validators all import the shared identity helper and reject `runtime_name`/`metadata_name` drift;
  - manifest validator is required and green for current `schema_version`, and reader compatibility for `N`/`N-1` is proven;
  - no direct canonical-root readers remain outside modules listed in `GOVERNANCE/runtime-separation/readers.yaml`;
  - inventory scan is complete with zero unexplained executable matches and fresh selector-scoped digest parity against manifest refs;
  - compatibility harness proves `N`/`N-1` reader compatibility from pinned fixtures;
  - current/baseline artifact build and comparator pass against schema contract.
  - wrapper fixture contract checks are green.
  - no content path moves yet.

1. Phase A: ownership enforcement and projection contract freeze
- Actions:
  - enforce boundaries via `Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`;
  - publish ownership and projection-read-only policy in docs under `GOVERNANCE/**` and agent docs;
  - freeze external compatibility invariants only for `.agents/**`, `.agents/skills/**`, `runtime/**`, `skills-antigravity/**`, and plugin runtime cache surfaces (allowed writers, discovery/precedence, visibility, and negative tests).
  - defer internal projection-generation behavior freeze until Phase B wrapper/mechanics extraction evidence is green.
- Exit criteria:
  - path-ownership gates block direct runtime/projection edits, including alias-path writes.
  - governance authority docs are generated and validated from manifest inventories.
  - projection contract tests exist for writer ownership, precedence, and negative-path behavior.

2. Phase B: mechanics extraction
- Actions:
  - move mechanics internals into `Infrastructure/factory/**`;
  - keep wrapper contracts stable until Phase F cleanup: entrypoint path, supported flags, exit-code semantics, and machine-readable output markers for:
    - `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
    - `bash Infrastructure/scripts/validate_all.sh`
    - `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
    - `bin/ask repo status`
    - `bin/ask repo validate`
  - migrate writer surfaces (skill/plugin create/install/import/harden flows) to manifest-derived root selection and enforce authoritative writer contract.
  - declare at least one pilot slice in `pre_activation` and run writer routing proof for that slice before Phase B promotion.
- Exit criteria:
  - wrappers remain contract-compatible and mechanics tests pass from wrapper entrypoints;
  - wrapper fixture contract checks pass with unchanged argv/exit/output behavior.
  - writer surfaces cannot write legacy canonical roots for slices in `pre_activation` or `migrated`.
  - writer mutation suite passes with writes constrained to `authoritative_write_root`.

3. Phase C: first-party canonical relocation (`Infrastructure/catalog/skills/**`)
- Entry criteria:
  - consumer audit is green for targeted first-party slices in this PR.
  - path-consumer inventory for targeted slices is complete in `GOVERNANCE/runtime-separation/path-consumers.yaml`.
- Actions:
  - move first-party sources slice-by-slice;
  - require `discovery_compatibility=dual_read` in `pre_activation`, and set `discovery_compatibility=catalog_only` in the same commit that sets `activation_state=migrated`;
  - on activation commit, switch to `activation_state=migrated` and remove legacy canonical source or replace it with declared forwarder in the same change;
  - update discovery precedence for migrated slices according to manifest `discovery_precedence`;
  - enforce duplicate identity checks keyed by runtime identity contract.
- Exit criteria:
  - all migrated first-party slices pass duplicate checks and acceptance matrix.

4. Phase D: plugin canonical relocation (`Infrastructure/catalog/Plugins/**`)
- Entry criteria:
  - consumer audit is green for targeted plugin slices in this PR.
  - path-consumer inventory for targeted plugin slices is complete in `GOVERNANCE/runtime-separation/path-consumers.yaml`.
- Actions:
  - move plugin canonical sources plugin-by-plugin;
  - migrate canonical plugin manifests to `Infrastructure/catalog/Plugins/<plugin>/.codex-plugin/plugin.json` and keep `Plugins/<plugin>` as compatibility directory until marketplace contract version update;
  - migrate plugin discovery/activation readers to policy-backed canonical roots that include `Infrastructure/catalog/Plugins/**`, while preserving `source.path=./Plugins/<plugin>` compatibility contract;
  - preserve plugin activation semantics for unchanged plugins through targeted `plugin_lifecycle_checks`, including `bin/ask plugins status <plugin> --json` checks for affected plugin slices;
  - execute targeted-slice `plugin_lifecycle_checks` where `applies_to_phase` contains `phase_d` or `all`; evaluate each selected check against `expected_exit_code` and `normalized_assertions` (install/sync/cache/profile-home reprojection and related lifecycle checks);
  - ensure workspace/profile projection and plugin runtime cache generation use policy-exported roots only;
  - preserve hidden runtime cache contract (`.agents/plugins-runtime/cache/**`);
  - keep visible local cache legacy path removed.
- Exit criteria:
  - plugin slice checks pass, shadowing checks pass, and no local marketplace cache regression appears;
  - all targeted-slice `plugin_lifecycle_checks` with `applies_to_phase` containing `phase_d` or `all` pass full tuple evaluation (`expected_exit_code` + `normalized_assertions`).

5. Phase E: runtime lane consolidation
- Actions:
  - formalize `runtime/**` as derived-only repo lane;
  - keep `skills-antigravity` as a real directory (not symlink), per sync guard;
  - if compatibility is needed, implement it as `filesystem_forwarder` via wrapper/index indirection only;
  - symlink allowances are closed by default outside antigravity sync-source lanes;
  - any non-antigravity alias symlink must be explicitly declared in governance policy with `source`, `target`, `owner`, and `justification`;
  - each declared alias symlink must have ownership-guard and projection-integrity coverage before promotion.
- Exit criteria:
  - runtime lane is read-only by policy and negative tests;
  - no compatibility rule contradicts `sync_skills.sh` path guards;
  - consolidation changes no projection semantics frozen in Phase A.

6. Phase F: compatibility cleanup
- Actions:
  - remove remaining legacy readers/forwarders slice-by-slice only after green exit checks;
  - plugin compatibility package roots at `Plugins/<plugin>` are explicitly out of scope for cleanup in this plan and remain required while `source.path=./Plugins/<plugin>` is contract-required;
  - plugin slices may not remove `Plugins/<plugin>` compatibility directories in this plan; plugin package-root cleanup requires a separate versioned marketplace-contract migration plan;
  - keep category-relative CLI path compatibility through shared resolver contract after forwarder removal;
  - freeze final ownership map and update contributor docs.
- Exit criteria:
  - discovery no longer depends on legacy canonical roots;
  - plugin compatibility package roots remain intact and parity-validated where contract-required;
  - command contracts remain compatible and category-relative CLI paths continue to resolve via shared resolver contract.

## Compatibility mapping

| Surface | Canonical target | Transitional mechanism | Hard guard |
| --- | --- | --- | --- |
| First-party skill sources | `Infrastructure/catalog/skills/<category>/<skill>/SKILL.md` | `discovery_compatibility: dual_read -> catalog_only`; `path_compatibility: combined -> filesystem_forwarder -> resolver_only` | runtime-identity duplicate checks + freshness strict |
| Plugin skill sources | `Infrastructure/catalog/Plugins/<plugin>/skills/<category>/<skill>/SKILL.md` | `discovery_compatibility: dual_read -> catalog_only`; `path_compatibility: combined -> filesystem_forwarder` (resolver-only deferred until marketplace-contract migration) | plugin shadowing + runtime-identity duplicate checks + activation/status parity |
| Plugin package manifest | `Infrastructure/catalog/Plugins/<plugin>/.codex-plugin/plugin.json` | generated compatibility package-root projection at `Plugins/<plugin>` while `source.path=./Plugins/<plugin>` remains contract-required | targeted `plugin_lifecycle_checks` (`plugins status <plugin> --json`) + marketplace `source.path` parity + manifest-asset parity |
| Mechanics commands | `Infrastructure/factory/**` internals + `Infrastructure/scripts/*` wrappers | wrapper delegation only | command-contract compatibility gates |
| Runtime projection tree | `runtime/**`, `.agents/**`, and `.agents/skills/**` derived outputs | no direct compatibility writes | path-ownership guard blocks source edits |
| Local marketplace cache | `.agents/plugins-runtime/cache/**` | canonical hidden cache only | block reintroduction of `Plugins/cache/agent-skills-local/**` |
| Antigravity projection lane | `skills-antigravity/**` real directory | `filesystem_forwarder` via wrapper/index only | reject symlinked `skills-antigravity` sync-source paths |

## User-facing acceptance matrix

Every phase promotion requires these user-visible flows to pass against the recorded Phase 0 baseline:
- comparator output from `Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py` reports no new blocker ids/classes/severity regressions.
- comparator enforces slice-scoped `planned_deltas` only (no undeclared field/value changes permitted).
- `bin/ask repo status --json` remains baseline-compatible for comparator fields.
- `bin/ask skills list --json` remains baseline-compatible for comparator fields.
- `bin/ask plugins doctor --json` remains baseline-compatible for comparator fields.
- targeted `plugin_lifecycle_checks` provide baseline-compatible `bin/ask plugins status <plugin> --json` evidence for promoted plugin slices.
- slice `representative_commands` in `slices.yaml` pass for each promoted slice using the full structured tuple (`command`, `comparison_mode`, `args_legacy`, `args_canonical`, `expected_exit_code`, `normalized_assertions`, `expected_result_ref`) while compatibility artifacts exist.
- `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh` reports no projection-integrity regressions.
- `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home .agents --cache-rel plugins-runtime/cache --strict --show-overlap` reports no local-marketplace-cache regressions.
- `bash Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh` reports no profile-home parity regressions for plugin status/doctor/cache behavior.
- targeted-slice `plugin_lifecycle_checks` selected by active phase key (`applies_to_phase` contains promoted phase key or `all`) pass full tuple evaluation (`expected_exit_code` + `normalized_assertions`) and report parity.
- repo-local and profile-home lanes emit identical `policy_identity`, `discovery_identity`, and `canonical_root_digest`.
- `bash Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh --strict` reports no non-authoritative writes.
- `bin/ask repo doctor-catalog --strict` is baseline-compatible with no new/worse drift classes.
- `bin/ask repo validate` is baseline-compatible with no new required failures.

If any acceptance flow fails, phase promotion is blocked.

## Validation ladder

Phase 0 bootstrap ladder (before new validators exist):
- `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
- `vale **/*.md **/*.mdx **/*.adoc **/*.rst` (required for documentation linting)
- `bin/ask skills list --json`
- `bin/ask plugins doctor --json`
- targeted baseline plugin status checks from declared slices: `bin/ask plugins status <plugin> --json`
- `bin/ask repo validate`
- `bin/ask repo doctor-catalog --strict`
- `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
- `bash Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh`
- `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --quiet`
- `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`

Phase A-F per-PR mandatory lane (after Phase 0 deliverables land):
- core lane (all migration PRs):
- `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
- `vale **/*.md **/*.mdx **/*.adoc **/*.rst` (required for documentation linting)
- purge stale derived artifacts for affected slices.
- regenerate projections/caches for affected slices before any comparator or plugin parity checks.
- `bin/ask repo validate`
- `python3 Infrastructure/scripts/runtime-separation/validate_runtime_separation_manifest.py --strict`
- `python3 Infrastructure/scripts/validation-and-linting/verify_selection_contract.py`
- `python3 Infrastructure/scripts/runtime-separation/scan_runtime_separation_consumers.py --emit-readers --emit-path-consumers --emit-digests --strict`
- `python3 Infrastructure/scripts/runtime-separation/verify_runtime_separation_reader_compat.py --schema-current GOVERNANCE/runtime-separation/slices.yaml --schema-prev GOVERNANCE/runtime-separation/fixtures/schema-prev.yaml`
- `python3 Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py --output GOVERNANCE/runtime-separation/current.json`
- `bash Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.sh --runtime-separation`
- `python3 Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current GOVERNANCE/runtime-separation/current.json`
- `bash Infrastructure/scripts/runtime-separation/verify_runtime_separation_writer_mutations.sh --strict`
- plugin lane (required when affected slices include plugins or plugin projections):
- `bin/ask plugins doctor --json`
- targeted-slice `plugin_lifecycle_checks` selected by active phase key (`applies_to_phase` contains promoted phase key or `all`) with full tuple evaluation (`expected_exit_code` + `normalized_assertions`), including `bin/ask plugins status <plugin> --json` where declared.
- `bash Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh`
- runtime/cache lane (required when affected slices touch runtime or cache projections):
- `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home .agents --cache-rel plugins-runtime/cache --strict --show-overlap`

Phase A-F phase-promotion exhaustive lane:
- `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
- `vale **/*.md **/*.mdx **/*.adoc **/*.rst` (required for documentation linting)
- `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh` (rerun after verify-work to catch generated-path drift)
- purge stale derived artifacts for all promoted slices.
- regenerate projections/caches for all promoted slices before exhaustive checks.
- `bin/ask repo validate`
- `bin/ask repo doctor-catalog --strict`
- `python3 Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py --strict`
- `bash Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh`
- `python3 Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py --quiet`
- `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`
- `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home .agents --cache-rel plugins-runtime/cache --strict --show-overlap`
- full-slice `representative_commands` sweep for all promoted slices using `comparison_mode` and asserting `expected_exit_code` plus `normalized_assertions` against `expected_result_ref`.
- targeted-slice `plugin_lifecycle_checks` selected by active phase key (`applies_to_phase` contains promoted phase key or `all`) with full tuple evaluation (`expected_exit_code` + `normalized_assertions`).

Additional negative ownership checks for migration PRs:
- direct edits to `.agents/**`, `skills-antigravity/**`, or `runtime/**` must fail `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh` unless the slice is explicitly marked as projection mechanics;
- direct edits to `.agents/skills/**` must fail the same ownership guard unless the slice is explicitly marked as projection mechanics;
- cache-path edits must fail without explicit intent and may run only with `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 PATH_OWNERSHIP_GUARD_SCOPE=working`;
- alias-path and realpath projection behavior must be verified via `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`; do not infer alias safety from git diff output alone;
- manifest schema and lane constraints are required gates for every migration PR.

## Risks and rollback

Primary risks:
- duplicate canonical identity introduced by mixed roots;
- hidden reader assumptions on legacy paths;
- runtime overlap regressions between flat skills and plugin cache skills;
- accidental reintroduction of visible local marketplace cache;
- slice rollback that does not restore phase-wide shared policy/mechanics baseline.

Rollback model:
- rollback at slice granularity first (revert slice commit range, rerun full ladder);
- phase-wide policy/mechanics commits are rollback domains separate from content slices;
- validated rollback checkpoints are required after Phase 0 and after Phase B before any slice promotions;
- before phases C, D, and E, record a validated baseline tag/snapshot;
- rollback must restore compatible manifest state (`schema_version` + `reader_min_version` + `policy_export_version`) or revert policy/mechanics to the matching baseline before rerunning validations;
- rollback validation requires clean derived-artifact purge/regeneration before acceptance checks;
- if slice rollback does not restore green acceptance matrix, revert to phase baseline and freeze next slices until root cause is documented.

Mandatory rollback validation:
- execute slice `rollback_commands` from manifest;
- run purge/regenerate steps for affected derived surfaces;
- `PATH_OWNERSHIP_GUARD_SCOPE=working bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
- `vale **/*.md **/*.mdx **/*.adoc **/*.rst` (required for documentation linting)
- `bin/ask repo validate`
- `bin/ask repo doctor-catalog --strict`
- `bash Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`
- `bin/ask plugins doctor --json`
- affected-slice `plugin_lifecycle_checks` with `applies_to_rollback=true`, each with full tuple evaluation (`expected_exit_code` + `normalized_assertions`), including `bin/ask plugins status <plugin> --json` where declared
- full `representative_commands` sweep for affected slices using `comparison_mode`, `expected_exit_code`, and `normalized_assertions`.
- `bash Infrastructure/scripts/validation-and-linting/check_codex_home_skill_overlap.sh --codex-home .agents --cache-rel plugins-runtime/cache --strict --show-overlap`
- `bash Infrastructure/scripts/runtime-separation/validate_runtime_separation_profile_home.sh`
- `python3 Infrastructure/scripts/runtime-separation/build_runtime_separation_current.py --output GOVERNANCE/runtime-separation/current.json`
- `python3 Infrastructure/scripts/runtime-separation/compare_runtime_separation_baseline.py --baseline GOVERNANCE/runtime-separation/baseline.json --current GOVERNANCE/runtime-separation/current.json`
- policy identity, discovery identity, and canonical root digest parity across repo-local/profile-home lanes

## Definition of done

- canonical skill/plugin authoring paths are unambiguous and runtime-identity validated.
- mechanics (`Infrastructure/factory/**`) and runtime (`runtime/**` + projections) are physically separated.
- runtime/projection surfaces are enforced read-only, including realpath/alias paths.
- plugin activation/discovery contracts remain stable after canonical relocation to `Infrastructure/catalog/Plugins/**`.
- plugin package manifests are canonical at `Infrastructure/catalog/Plugins/<plugin>/.codex-plugin/plugin.json`, while compatibility directory behavior at `Plugins/<plugin>` remains valid for `source.path=./Plugins/<plugin>` until a versioned marketplace contract change.
- legacy visible local marketplace cache remains absent from repo canonical runtime paths.
- manifest contract is versioned, validated, and reader-compatible for `N`/`N-1` via fixture-driven harness.
- category-relative CLI path compatibility is preserved through shared resolver contract after forwarder cleanup.
- control-plane ownership is singular: mutable migration state in manifest only; policy exports are derived.
- baseline artifact ownership is defined in governance docs and baselines are evidence snapshots, never live policy inputs.
- planned migration output changes are declared via slice-scoped `planned_deltas`; undeclared comparator drift is blocked.
- promotion/rollback validation includes both repo-local and profile-home lanes for plugin status/doctor/cache parity.
- command contracts remain compatible at closeout: entrypoint path, supported flags, exit-code semantics, and output schema/text markers for:
  - `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
  - `bash Infrastructure/scripts/validate_all.sh`
  - `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
  - `bin/ask repo status`
  - `bin/ask repo validate`
