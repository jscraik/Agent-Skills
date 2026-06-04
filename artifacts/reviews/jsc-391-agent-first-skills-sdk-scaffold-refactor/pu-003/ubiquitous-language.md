# Ubiquitous Language Review: JSC-391 PU-003

schema_version: 1
scope: Skills SDK module contract vocabulary

## Findings

No terminology blockers.

The PU-003 contract uses repo-native language from `UBIQUITOUS_LANGUAGE.md`
and the PU-002 ADR:

- Canonical source remains separate from Runtime Projection.
- Generated handles, plugin caches, and user/global runtime mirrors remain
  forbidden source surfaces.
- Deep module terms are stable: manifest, receipts, risk, install, sandbox,
  refs, evals, signing, runtime, and packaging.
- Placeholder status terms are explicit: not_run, skipped_optional, and blocked.
- Work-mode terms are explicit: inferential, computational, and hybrid.

## Prompt Translations

- "Do the swarm review later" maps to: agent-native and architecture-strategist
  review are separate follow-up lanes, not PU slice closure evidence.
- "Module is ready" must mean: the contract is documented and parseable for this
  scaffold slice, not that feature execution exists.

## Skipped

- Did not update root `UBIQUITOUS_LANGUAGE.md`; PU-003 did not introduce a new
  project-wide term, only applied existing terms to the SDK reference surface.

WROTE: artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor/pu-003/ubiquitous-language.md
