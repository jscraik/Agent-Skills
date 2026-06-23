# Skills SDK PU-020 Route-Truth Declutter Plan

## First-Principles Gate

- User outcome: a cold agent or operator can ask what is true and what is next
  for the Skills SDK without reconciling the CLI, matrix, and static HTML by
  hand.
- Copied assumption to avoid: a new dashboard, registry, or eval runner would
  make the SDK workflow clearer.
- Smallest durable mechanism: keep the existing SDK status command authoritative
  and make projections prove they are projections.
- Tessl topology principle: workspaces are lifecycle and authority lanes, not
  skill categories. Eval, private skills, and public published lanes are the
  target setup; frontend/backend/security/marketing-style groupings are facets.
- GitHub exit principle: GitHub can stay source/provenance during migration,
  but Tessl workspace/package receipts should become distribution, install,
  eval, review, inventory, and publish truth.

## Slice

1. Mark the HTML pipeline artifact with the source command and source matrix.
2. Replace stale PU-019 next-slice copy with PU-020 route-truth declutter copy.
3. Keep matrix generated_from pointed at the stable capability-truth contract
   and include this PU-020 spec and plan in source_artifacts.
4. Add deterministic tests for projection source declaration, source artifact
   existence, completed-PU next-slice drift, and static-doc projection-only
   behavior.
5. Carry the next Tessl slice as a read-only workspace snapshot/intake surface
   covering all plugins, projects, eval runs, review runs, inventories,
   members, and settings before any workspace mutation or publish flow exists.
6. Treat Tessl Review as configurable review policy: the snapshot should record
   what "good" means for the target through criteria/rubric identity,
   thresholds, reviewer authority, findings, fixes, and blockers.
7. Add a Tessl Registry security receipt lane that captures Tessl's Snyk-backed
   registry security signal when present, including provider label, status,
   known-issue summary, package identity, source, and freshness evidence.
8. Keep local Snyk Agent Scan as the fallback/pre-registry lane for explicit
   skill-path scans only. The lane should record scanner version, command,
   target paths, token presence without value, data-egress notice, JSON output
   path, issue counts, and blocked/error classification.

## Validation

- ./bin/ask sdk status --json --robot
- ./bin/skills-sdk status --json --robot
- uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q

## Follow-Up Boundary

After this declutter slice passes, the next SDK expansion can add no-network
fixture coverage and runtime projection proof for vendored capsule
discoverability. That follow-up should reuse the same status route instead of
creating a parallel planning surface.

The Tessl follow-up should first record workspace lane, workspace name, package
identity, category facets, source provenance, distribution truth, project
linkage, eval/review evidence, inventory coverage, member/role authority, and
workspace policy. It must remain read-only until install, publish, archive,
update, visibility, or workspace mutation authority is explicitly approved.
Review-run receipts should include the configured review criteria so a later
adoption decision can explain why the skill passed, failed, or needs revision.
The Tessl security follow-up should first consume registry-provided security
status rather than rescanning public registry entries locally. A local Snyk
Agent Scan follow-up is still useful for source imports and private candidates
with no Tessl registry security yet; it should use explicit skill roots such as
`Skills/` or selected plugin skill directories rather than whole-machine
discovery. Do not pass `--dangerously-run-mcp-servers`; use a sandbox or
disposable copy for untrusted inputs, and prefer a pinned scanner version once
the trial proves the shape.
