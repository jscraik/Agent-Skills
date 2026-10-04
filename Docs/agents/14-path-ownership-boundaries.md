# Path Ownership Boundaries

## Table of Contents

- [Purpose](#purpose)
- [Approved lifecycle](#approved-lifecycle)
- [Transitional selected skills](#transitional-selected-skills)
- [Four-plane model](#four-plane-model)
- [Canonical sources](#canonical-sources)
- [Derived and runtime surfaces](#derived-and-runtime-surfaces)
- [Edit policy](#edit-policy)
- [Validation](#validation)

## Purpose

Separate skill and plugin product content from factory mechanics and runtime projections so ownership is unambiguous.

## Approved lifecycle

Jamie approved these six rules on 2026-09-27. They supersede earlier guidance
that made Foundry the mandatory permanent source destination, stopped SDK
responsibility at handoff, or excluded registry/runtime proof from separation.

1. **Foundry holds candidates.** Skills Foundry stores permitted skills and
   plugins awaiting SDK processing, including blocked or rejected candidates
   with reasons. Holding is not SDK approval, distribution or installation.
   Preserve source history; processing does not authorise deletion or require
   permanent post-processing storage in Foundry.
2. **SDK owns the workflow.** Skills SDK owns the agent-facing `SKILL.md`,
   references and eval workflow plus executable create, update, external-intake,
   check and installation tooling. Required Tessl/Codex adapters belong to SDK;
   keep its Python core portable without disclaiming end-to-end integration.
3. **Tessl stores checked versions privately.** The `jscraik` private workspace
   is the distribution source for managed installations. Bind checks and
   registry readback to exact package identity and private visibility. Only
   Jamie decides which specific versions become public; passing checks is not
   publication authority.
4. **Codex runtimes contain installed copies.** Non-exempt managed packages in
   `~/.agents/skills` and `~/.codex/plugins` install from checked Tessl versions,
   not directly from Foundry or Agent-Skills. Updates require newly checked
   versions. Prove identity, discovery, required behaviour and recovery; do not
   silently author in installed copies.
5. **OpenAI-provided plugins are exempt.** Use their intended provider-managed
   route. Verify origin; a name, directory or compatible manifest is not proof.
6. **OpenAI system skills are exempt.** Preserve their provider-managed route
   and files during SDK discovery, migration and installation.

These are required outcomes, not claims that the destination implementation
already exists. Local source work does not authorise uploads, credentials,
provider spending or live runtime mutation. Select those actions explicitly
and retain missing proof as incomplete, not out of scope. Do not discard required
plugin hooks, assets or MCP components to make a skills-only journey pass.
Project-local skill proof alone does not prove home-level native plugin support.

## Transitional selected skills

Jamie's later decision on 2026-09-27 temporarily permits these existing custom
skills to run without prior SDK or Tessl processing: testing, evals-router,
sdk-scenario-generator, technical-writer, agents-md, simplify, unslopify,
improve-agent-native and improve-codebase-architecture. Keep complete resources,
provenance and recovery. Classify these copies as unchecked transitional skills,
not approved releases. This exception supersedes conflicting immediate admission
requirements for this set only; it does not cover new external intake or plugins.

Use `~/.agents/skills` as the sole user-managed custom skill collection; preserve
provider-managed system content and plugin locations. Reconcile existing aliases
before a separately authorised live cutover. Do not expose Foundry holding for
discovery or retain an operational dependency on Agent-Skills.

Move other permitted custom skills to Foundry holding with inventory and recovery,
not deletion. Preserve verified OpenAI system skills, including imagegen,
skill-creator and skill-installer. An explicit origin check, not a name, grants
the provider exemption. Retire the temporary exception only after SDK demonstrates
all required workflows and integrations, including accepted, rejected and recovery
behaviour. The eventual six-rule lifecycle remains the destination.

## Four-plane model

Agent-Skills user sync is retired. Both `./bin/ask skills sync --scope user`
and the shell sync's `--user` mode reject the operation before mutation,
including links-only and dry-run requests. Use workspace sync only for
repository projections. Preserve selected physical packages in
`~/.agents/skills` and provider-managed system skills; do not recreate a
`~/.codex/skills` alias. Jamie's temporary SDK/Tessl exception remains valid
for the selected custom skills until the required SDK workflows are ready.
This guard does not retire Configs' separate projection or plugin routes.

1. Foundry holding plane (`candidates awaiting processing`)

- Curated skill and plugin packages held in `/Users/jamiecraik/dev/skills-foundry`.
- Preserves complete candidate packages, provenance and rights information.
- A permitted holding copy or local catalog admission is not SDK clearance and
  does not install, enable, publish, promote or transfer source authority.

2. SDK tooling plane (`reusable lifecycle behavior`)

- `/Users/jamiecraik/dev/skills-sdk` owns the complete workflow in rule 2,
  including checked private-registry delivery and supported runtime adapters.
- Checking binds a selected candidate, not ownership of all editable source.
  Test fixtures and scratch candidates are not source owners.

3. Transitional migration plane (`remaining Agent-Skills dependencies`)

- Existing source, callers, and mechanics remain here only until their recorded
  transfer and consumer cutover. Agent-Skills is not a permanent third owner.
- Migrate necessary reusable behavior to SDK and permitted unprocessed packages
  to Foundry. Keep host policy and credentials with their explicit owner;
  SDK-owned adapters integrate with those owners.
- Retire old surfaces only after independent destination behavior, caller and
  recovery proof, and matching mutation authority. Complete separation before
  product refinement.

4. Runtime plane (`installed copies and transitional projections`)

- Target managed installations come from the checked private Tessl version;
  verified provider exemptions retain their intended loading route.
- Existing flat projections and mirrors are transitional dependencies. Preserve
  working consumers until authorised replacement; never hand-edit runtime output.

## Canonical sources

Every package has one canonical source determined by an explicit owner
decision. A runtime path is never canonical editable source. A Foundry holding
copy does not change that decision; move source authority only after direct
consumers, provenance and the replacement path have been verified. Tessl owns
the checked distribution version, not an inferred editable-source transfer.

Skills Foundry holding and retained provenance:

- `/Users/jamiecraik/dev/skills-foundry/**`
- Holding is separate from SDK approval and installation. Retained editable
  material may support updates where its explicit owner permits; Foundry is
  not a mandatory permanent post-processing authoring destination.

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
rights-blocked entries; neither runtime availability nor a holding copy grants
SDK approval. Full SDK review is not a prerequisite for permitted holding.
For a retained package still awaiting transfer:

1. Verify that recorded rights authorize the source copy. If rights are
   unresolved or blocked, retain only permitted inventory and provenance
   metadata; do not read or copy protected content. Retention intent is not
   transfer permission.
2. When rights and the selected transfer scope permit, copy the package into
   `/Users/jamiecraik/dev/skills-foundry` without changing the existing source
   or runtime surface. The copy alone is not canonical.
3. Preserve the origin path or repository, licence, revision when known, and
   direct consumer notes with that Foundry copy.
4. Do not install, enable, publish, project, delete, or relink it as a side
   effect of the copy.
5. Record canonical source transfer before switching the repair location to
   Foundry. Until then, authorized repairs stay in the explicit owner's
   canonical source; reconcile any changed source before accepting the copy.
   Record consumer cutover separately. SDK tooling may process the selected
   candidate without taking package source ownership.

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
- Repair the recorded editable source within authorised scope and rights;
  a permitted holding copy does not transfer ownership. Process updates through
  SDK checks before private registry delivery and runtime installation.
- Do not copy an external or runtime package into `agent-skills` merely to make
  it visible. Record provenance and permitted holding/intake before processing.
- Do not hand-edit runtime/projection surfaces.
- Edit tracked `.agents/workflows/**` docs directly when the workflow itself changes.
- Do not hand-edit .skillsets/**; refresh current runtime projections with python3 bin/ask skills sync --scope workspace --projection flat and use the manifest generator only for legacy .skillsets/** compatibility metadata.
- Treat `Plugins/cache/**` as mirrored output. Edits are blocked by default and allowed only in explicit projection-refresh lanes.
- For explicit projection-refresh lanes, set `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1` and ensure matching canonical source or projection mechanics updates.
- Where a transitional projection refresh is explicitly selected, use repository wrappers (`python3 bin/ask skills sync`, `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`) rather than hand edits. These legacy routes are not the target Tessl installation path or proof of lifecycle completion.
- Guard scope defaults:
  - local runs: staged diff only;
  - CI runs: base-ref diff (`origin/$GITHUB_BASE_REF...HEAD`);
  - override with `PATH_OWNERSHIP_GUARD_SCOPE=staged|working|base-ref`.

## Validation

- `bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
- `bash Infrastructure/scripts/validate_all.sh --ephemeral`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --project-governance`
