# Path Ownership Boundaries

## Table of Contents

- [Purpose](#purpose)
- [Four-plane model](#four-plane-model)
- [Canonical sources](#canonical-sources)
- [Derived and runtime surfaces](#derived-and-runtime-surfaces)
- [Edit policy](#edit-policy)
- [Validation](#validation)

## Purpose

Separate skill and plugin product content from factory mechanics and runtime projections so ownership is unambiguous.

## Four-plane model

1. Foundry source plane (`retained editable packages`)

- Curated skill and plugin packages held in `/Users/jamiecraik/dev/skills-foundry`.
- Owns retained editable package source, repairs, package-specific scripts,
  evaluation data, provenance, licences, documentation, and reference assets.
- Admission is copy-first. A Foundry admission does not install, enable, publish,
  promote, or transfer runtime authority.

2. SDK tooling plane (`reusable lifecycle behavior`)

- `/Users/jamiecraik/dev/skills-sdk` owns reusable creation, repair, validation,
  evaluation, judging, review, packaging, and handoff tooling.
- SDK inspection or transformation of a package does not transfer its canonical
  source from Foundry. Test fixtures and scratch candidates are not source owners.

3. Transitional migration plane (`remaining Agent-Skills dependencies`)

- Existing source, callers, and mechanics remain here only until their recorded
  transfer and consumer cutover. Agent-Skills is not a permanent third owner.
- Migrate necessary reusable behavior to SDK and package-specific content to
  Foundry. Keep host policy and credentials with their explicitly accepted owner.
- Retire old surfaces only after independent destination behavior, caller and
  recovery proof, and matching mutation authority. Complete separation before
  product refinement.

4. Runtime plane (`derived views and projections`)

- Flat/runtime projections and mirrored cache surfaces.
- Never hand-edit.

## Canonical sources

Every package has one canonical source determined by an explicit owner
decision. A runtime path is never canonical source. Foundry admission is a
copy-first retention step; move source authority only after direct consumers,
provenance, and the replacement path have been verified.

Skills Foundry retained source:

- `/Users/jamiecraik/dev/skills-foundry/**`
- Source-only means separate from runtime installation and publication, not
  read-only archival storage. Retained package authoring and repairs belong here.

Transitional package source paths in this repository:

- `Skills/agent-ops/**`
- `Skills/frontend-ui/**`
- `Skills/backend-platform/**`
- `Skills/product-strategy/**`
- `Skills/security-ops/**`
- `Skills/content-publishing/**`
- `Skills/mobile-native/**`

Transitional plugin source paths in this repository:

- `Plugins/<plugin>/skills/**`
- `Plugins/<plugin>/.codex-plugin/**`
- `Plugins/<plugin>/Infrastructure/references/**`

### Bulk-admission rule

Before admitting packages in bulk, record each package's explicit owner,
destination, disposition, rights, and consumers. Preserve unresolved and
rights-blocked entries; neither runtime availability nor a copy grants admission.
For a retained package still awaiting transfer:

1. Copy it into `/Users/jamiecraik/dev/skills-foundry` before changing an
   existing source or runtime surface.
2. Preserve the origin path or repository, licence, revision when known, and
   direct consumer notes with that Foundry copy.
3. Do not install, enable, publish, project, delete, or relink it as a side
   effect of the copy.
4. Record canonical source transfer and consumer cutover separately. SDK tooling
   may process the selected candidate without taking package source ownership.

The same named package can appear in Foundry, `agent-skills`, Tessl, and a
home runtime at once. Those locations describe different lanes; they do not
transfer ownership by proximity or by name.

Transitional factory and repository governance locations:

- `Infrastructure/scripts/**`
- `Docs/agents/**`
- `.harness/**`
- `.codex/environments/environment.toml`
- `harness.contract.json`

These paths describe current locations, not permanent destination ownership.
Classify reusable behavior, package-specific content, host policy, and temporary
migration evidence by their actual consumers before moving or retiring them.

## Derived and runtime surfaces

Runtime/projection surfaces (non-canonical):

- `.agents/skills/**`
- `.agents/plugins-runtime/cache/**`
- `.skillsets/**` (generated rooted manifest rows; current transitional inputs
  are `Skills/**`, `Plugins/**`, and generator code until recorded transfer.
  After transfer, use the package's accepted canonical owner and the generator's
  tooling owner, not the old Agent-Skills paths.)
- `skills-codex/**`
- `Plugins/cache/**`
- `runtime/**` (whenever introduced by migration phases)
- `~/.agents/skills/**`, `~/.codex/skills/**`, `~/.agents/plugins/**`, and
  `~/.codex/plugins/**` (curated or accepted runtime availability only)

Active agent-facing docs:

- `.agents/workflows/**` is tracked workflow documentation, not a runtime skill projection.

Generated index surface:

- `SKILL.md` (root index generated by sync workflow)

Workout and telemetry surfaces:

- `.workouts/**` is canonical workout harness source.
- `.skill-telemetry/**` is runtime evidence output and must not be committed.

## Edit policy

- Edit product content only in the canonical source path named by the explicit
  owner decision.
- Repair retained Foundry source in Foundry; an SDK handoff selects tooling work,
  not a new canonical package copy in Agent-Skills or SDK.
- Do not copy an external or runtime package into `agent-skills` merely to make
  it visible; preserve its provenance in Skills Foundry first.
- Do not hand-edit runtime/projection surfaces.
- Edit tracked `.agents/workflows/**` docs directly when the workflow itself changes.
- Do not hand-edit .skillsets/**; refresh current runtime projections with python3 bin/ask skills sync --scope workspace --projection flat and use the manifest generator only for legacy .skillsets/** compatibility metadata.
- Treat `Plugins/cache/**` as mirrored output. Edits are blocked by default and allowed only in explicit projection-refresh lanes.
- For explicit projection-refresh lanes, set `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1` and ensure matching canonical source or projection mechanics updates.
- Regenerate projections with repository wrappers (`python3 bin/ask skills sync`, `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`) rather than editing projections directly.
- Guard scope defaults:
  - local runs: staged diff only;
  - CI runs: base-ref diff (`origin/$GITHUB_BASE_REF...HEAD`);
  - override with `PATH_OWNERSHIP_GUARD_SCOPE=staged|working|base-ref`.

## Validation

- `bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validate_all.sh --ephemeral`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
