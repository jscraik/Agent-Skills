# Skills SDK PU-020 Route-Truth Declutter Spec

## Problem

The SDK status command is the intended operator route truth, but the static
HTML pipeline artifact can still introduce stale next-slice claims after the
capability matrix has moved on. PU-019 is now represented as an implemented
consumer lane in the capability matrix, while the HTML still advertises PU-019
as the next slice.

## Objective

Keep one authoritative route for Skills SDK capability truth:

- ./bin/ask sdk status --json --robot remains the operator entrypoint.
- Infrastructure/config/skills-sdk/capability-matrix.v1.json remains the
  structured source for capability status.
- artifacts/recommended-skills-sdk-pipeline.html remains a projection of those
  sources, not a second planning authority.

## Scope

- Declare the SDK status command and matrix source on the static HTML
  projection.
- Replace stale PU-019 next-slice language with the PU-020 route-truth
  declutter slice.
- Add tests that fail when completed PU notes reappear as next-slice claims in
  the HTML projection.
- Add tests that require declared source artifacts to exist and include the
  generated-from spec.

## Non-Goals

- Do not add a new dashboard, registry, or eval runner.
- Do not revive rooted projection mode.
- Do not claim hosted docs, CI, PR, review-thread, tracker, or merge-readiness
  truth from the local HTML projection.
- Do not broaden SDK execution behavior beyond status and projection truth.
- Do not model frontend, backend, engineering, legal, security, marketing,
  database, or agent-ops as Tessl workspaces by default. They are skill
  category facets unless a separate governance boundary is approved.
- Do not treat GitHub repository presence as skills distribution readiness.
  GitHub source provenance and Tessl distribution truth must stay separate.

## Tessl Workspace And GitHub Exit Boundary

The desired Tessl setup is a lifecycle and authority topology:

- `eval`: private workspace lane for project-linked eval runs, review runs,
  scenario quality, and release-decision evidence.
- `private_skills`: private workspace lane for internal skills that should be
  searchable, installable, reviewed, and governed without public publishing.
- `public_published`: public workspace lane for skills promoted through policy,
  review, evidence, and publish authority.

The first SDK slice in this direction should be a read-only Tessl workspace
snapshot/intake lane. It should collect catalog, project-link, eval-run,
review-run, inventory, member/role, and settings receipts before any install,
publish, archive, update, visibility, or workspace mutation is authorized.

Tessl Review evidence should not be modeled as a generic pass/fail blob. The
review snapshot must preserve the configured definition of "good": rubric or
criteria identity, threshold policy, reviewer/owner authority, reviewed target
identity, findings, fix recommendations, and promotion blockers.

Tessl Registry security should be treated as the primary Snyk-backed security
signal when a skill or tile already has a Tessl registry record. The registry
snapshot must preserve the security provider label when available, security
status such as `LOW`, `MEDIUM`, or passed/failed, known-issue summary, package
identity, registry source, and freshness evidence if Tessl exposes it.

Local Snyk Agent Scan is a fallback and pre-registry intake lane, not the
default security source once Tessl has registry security data. Use it only for
GitHub/source imports, private workspace candidates, or local skills that do
not yet have Tessl registry security. It must target explicit skill files or
directories directly, require `SNYK_TOKEN` without printing it, capture JSON
output, record that skill content and component metadata may be sent to Snyk
for analysis, and avoid broad MCP auto-discovery because Snyk's Agent Scan
documentation warns that scanning MCP configuration can execute the stdio
server commands declared in those configs.

## Acceptance

- The HTML projection explicitly points users back to ./bin/ask sdk status
  --json --robot and the capability matrix.
- No completed PU listed in implemented capability notes is advertised as
  Next or Next slice in the HTML projection.
- The matrix generated_from path is included in source_artifacts, and every
  source artifact exists.
- Focused SDK capability status tests pass.
