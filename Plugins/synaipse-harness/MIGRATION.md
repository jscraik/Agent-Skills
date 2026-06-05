# SynAIpse Harness Migration Notes

## Identity

- Plugin package name: `synaipse-harness`
- User-facing product name: `SynAIpse Harness`
- Skill prefix: `sy-`

## Prefix policy

Lifecycle stage names are plain domain terms: `strategy`, `reframe`, `brainstorm`, `trace-plan`, `tracker-plan`, `slice-spec`, `execution-plan`, `work`, `review`, `eval-report`, `reconcile`, `reinforce`.

Installable skill IDs keep the `sy-` prefix to avoid collisions with other skills and make routing grep-friendly.

## Split planning

- `sy-trace-plan`: decomposes intent into trace bullets.
- `sy-spec`: specifies one selected trace bullet.
- `sy-execution-plan`: sequences implementation for that specified slice.
