# PU-001 Ubiquitous Language Review

schema_version: 1
execution_mode: terminology_review

## Active Glossary Surface

`UBIQUITOUS_LANGUAGE.md`

## Terms Checked

- Agent Skills Kit
- `ask` CLI
- Runtime Projection
- Feature Worktree
- Release-Readiness Claim
- Owner Repo Skill Evidence
- Project Skill Lifecycle Gate

## Findings

No terminology changes required for PU-001.

## Language Checks

- The board uses `./bin/ask` as the repo control plane and `skills-sdk` as the product CLI facade, avoiding a misleading claim that the facade owns repo operations. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:12`.
- The board names runtime projections and global installs as forbidden source-edit surfaces, matching repository ownership language. Evidence: `docs/goals/skills-sdk-v1-0-product-implementation/goal.md:68`.
- The notes use `Feature Worktree`-compatible language by treating the dirty primary checkout as a reason to isolate work on a feature branch/worktree before implementation slices. Evidence: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html:193`.
- The tracker language separates `JSC-390` docs/explorer scope, `JSC-391` completed scaffold evidence, and the missing V1.0 parent implementation tracker. Evidence: `.harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html:216`.

## Ambiguities

- `waiver` is intentionally scoped to local implementation progress, not tracker completion. Do not call tracker state complete until a parent issue exists or Jamie explicitly waives the tracker action.

## Validation

- Active glossary exists and contains the relevant terms.
- Goal board validator passes.

## Next Step

Keep the same vocabulary in PR title/body and in PU-002 handoff.
