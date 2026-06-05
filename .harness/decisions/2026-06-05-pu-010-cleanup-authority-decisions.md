---
schema_version: 1
decision_id: pu-010-cleanup-authority-decisions
title: "PU-010 Cleanup Authority Decisions"
date: 2026-06-05
status: accepted_for_implementation
source_execution_plan: .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-execution-plan.md
---

# PU-010 Cleanup Authority Decisions

## Scope

These decisions unblock the PU-010 implementation slices for receipt-proven
rollback and uninstall. They apply only to project-local cleanup in explicit
project roots. They do not authorize global cleanup, workspace cleanup,
registry mutation, publishing, trust-store mutation, signing, sandbox cleanup,
or cleanup of the live agent-skills repository.

## cleanup receipt schema

Use one discriminated schema:

    Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json

The receipt operation field distinguishes rollback from uninstall. A single
schema keeps action buckets, journal fields, source receipt binding, lockfile
changes, mutation truth, manual actions, and acceptance trace consistent across
both commands.

Separate rollback and uninstall schemas are deferred unless the shared schema
becomes ambiguous during implementation.

## before-state policy

Automatic restoration is allowed only when the install receipt contains
machine-checkable before-state evidence:

- inline before-content with digest proof, or
- an approved before-state reference whose content digest can be verified.

If before-state proof is missing, stale, unreadable, or digest-mismatched, the
file is not restored automatically. The cleanup receipt records a manual action
instead.

## receipt identity

Use the source install receipt digest as the minimum immutable cleanup
authority for PU-010. A receipt path is never sufficient authority by itself.

The cleanup planner records:

- source receipt path
- source receipt digest
- source receipt schema version
- resolved target root
- lockfile reference when the operation uses lockfile state

Adding a first-class receipt id is deferred unless compatibility with existing
PU-009 install receipts can be preserved without weakening digest authority.

## duplicate install policy

Refuse duplicate active lockfile entries for the same skill id in PU-010.

Uninstall by skill id is safe only when the lockfile resolves to exactly one
active entry. Install-instance targeting is deferred to a later slice unless it
can be added compatibly and proven by tests without widening the PU-010 scope.

## journal path

Use a project-local cleanup journal path under:

    .harness/state/skills-sdk/cleanup/

Journal records are written before the first filesystem or lockfile mutation.
They are scoped by operation, project-root identity, source receipt digest, and
skill id when present. Cleanup must never write journal state outside the
resolved project root.

Cleanup receipts remain under:

    .harness/receipts/skills-sdk/cleanup/

The journal is staged state for recovery or blocking. The receipt is the final
operator evidence artifact.

## Implementation Notes

- Preview mode must not write journals or receipts.
- Apply mode must write the journal before destructive mutation.
- If an unresolved journal is detected on rerun, the command either resumes
  safely from verified completed actions or blocks with a recovery payload.
- Capability truth stays deferred or partial until executable temp-project
  proof supports a stronger label.
