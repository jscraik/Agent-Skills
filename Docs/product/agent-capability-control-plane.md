---
title: Agent Capability Control Plane
status: active
date: 2026-05-01
agent_compatible: true
schema_version: 1
linear_issue: JSC-246
governing_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
governing_plan: Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md
---

# Agent Capability Control Plane

This repository is the canonical source for skills and plugins. Its local
Skills SDK journey helps an author answer four practical questions about one
existing skill without requiring knowledge of the underlying implementation:

1. Is this the skill I meant?
2. Is its source structurally sound?
3. Can it be packaged without changing the runtime?
4. What has actually been proved locally?

## Default Local Journey

Start with one canonical skill and run only the command that advances the
current result. The default journey is:

```bash
./bin/ask sdk start <skill> --json --robot
./bin/ask sdk check <skill> --json --robot
./bin/ask skills package verify <skill> --strict --json --robot
./bin/ask skills prove <skill> --json --robot
```

When strict package verification passes, its one next action is the same
target's `skills prove` command. A passing package gate establishes source
readiness; proof separately establishes runtime reachability and task outcome.

| Job | Result |
| --- | --- |
| Start | Resolves the target and reports its current local state. |
| Check | Gives a compact structural and contract verdict with actionable failures. |
| Verify package | Reports a target-bound strict package verdict without installing anything. |
| Prove | Separates structural validity, runtime reachability, and local task outcome. |

Each result is target-bound, compact, and contains at most one next action. A
passing structural or runtime check does not establish a successful task
outcome; an outcome result does not establish installation, activation,
publication, review acceptance, or release readiness.

### SDK Check Contract

The compact `data.skills_sdk_check` result conforms to
[`skills-sdk-check.v1`](/Infrastructure/config/schemas/skills-sdk/sdk-check.v1.schema.json).
It reports the requested `query`, one facade `status`, the canonical replay and
next commands, and the nested
[`skills-sdk.check-receipt.v1`](/Infrastructure/config/schemas/skills-sdk/check-receipt.v1.schema.json).

`canonical_source_path` identifies the canonical `SKILL.md` used for the
result, or is `null` when the target cannot resolve to one. `claims_boundary`
states the local truth the check establishes and explicitly excludes package
readiness, runtime reachability, task outcome, publication, and release
readiness. Consumers must retain those fields rather than inferring broader
readiness from a passing check.

## Ownership And Boundaries

Skill Factory owns creating, importing, refactoring, and retiring skill source.
Skills SDK owns the local resolve, check, package, and proof journey. Runtime
projection, cloud evaluation, Tessl distribution, publication, and versioned
installation are explicit later boundaries; none is a default dependency of
these four local commands.

Canonical source remains under `Skills/**` and `Plugins/*/skills/**`. Generated
projections under `.agents/**` and user-runtime links are derived surfaces, not
alternative source authorities.

## Expert And Repository Operations

The repository retains lower-level diagnostic, maintenance, and lifecycle
operations for their named maintainers and integrations. They are deliberately
not the default author journey. Use the owning runbook or command help when a
specific investigation requires one, rather than treating a broad diagnostic
report as a prerequisite for ordinary local skill work.

The underlying command contracts and implementation history remain available in
[Product Golden Path Command Contracts](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md)
and the linked specifications. They document expert mechanisms; they do not
expand the four-command local journey.

## Local Proof

Local proof is useful only when it distinguishes its constituent truths:

- structural quality: the source and declared contracts validate;
- runtime reachability: the selected runtime can discover the skill; and
- outcome proof: a bounded real task or evaluation has the claimed result.

Keep these facts separate in command output and in human conclusions. When any
one is unavailable, report that boundary and the smallest target-bound next
action rather than inferring a broader readiness claim.
