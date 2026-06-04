# Architecture Skill Review: JSC-391 PU-002

## Findings

No blocking architecture findings.

The ADR selects repo-native paths before scaffold files are created, satisfying
the PU-002 ordering requirement. It preserves existing SDK owners instead of
creating parallel modules: `runtime_adapters.py`, `package_contracts.py`,
`package_verify.py`, `contracts.py`, and `conformance.py` remain the current
owners where behavior already exists.

The ownership map gives future work one primary module and collaborators for
each logical surface. The strongest architectural choice is rejecting
`.agents/**`, `.skillsets/**`, `Plugins/cache/**`, root `SKILL.md`, and
user runtime links as source in the ADR, which keeps generated surfaces out of
the scaffold.

## Residual Risk

PU-003 must turn the map into human-readable module contracts under
`Docs/reference/skills-sdk/**`. Until then, `Docs/reference/skills-sdk/modules.md`
is an intentional selected path, not an existing contract.

WROTE: artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor/pu-002/improve-codebase-architecture.md
