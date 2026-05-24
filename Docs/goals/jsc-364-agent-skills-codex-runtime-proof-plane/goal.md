# JSC-364 Codex Runtime Proof Plane Governed Goal

## Mode

`GOVERNED_IMPLEMENTATION`

Jamie approved the switch from `PROMPT_REVIEW_ONLY` to
`GOVERNED_IMPLEMENTATION` on 2026-05-24. This board is now the repo-visible
control plane for the JSC-364 implementation lane.

## Objective

Implement JSC-364 by adding a Codex Runtime Proof Plane to Agent Skills Kit.
The implementation must make `./bin/ask` produce durable, machine-readable
runtime proof or durable `blocked_runtime` evidence for Codex-targeted
skill/runtime checks.

The trust boundary is strict: modeled Codex compatibility, generated projection
readiness, docs, plans, and local intent must never masquerade as live runtime
proof.

## Canonical Inputs

- Plan: `.harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md`
- Spec: `.harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md`
- Audit: `.harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md`
- Evidence extraction: `.harness/research/deep/2026-05-24-jamie-craik-evidence.md`
- Codex integration analysis: `/Users/jamiecraik/dev/codex/.harness/research/deep/2026-05-24-codex-skills-sdk-native-integration-analysis.md`
- Linear issue: `JSC-364`

## Native Prompt

```text
/goal Follow Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/goal.md
```

This is a prompt convention, not a native file binding.

## Completion Contract

JSC-364 is complete only when all P0 proof-plane units are implemented through
bounded slices and each slice has validation, review, delivery, and evidence
receipts.

Required outcomes:

- `./bin/ask` exposes a reachable Codex Runtime Proof Plane path.
- Runtime proof emits schema-valid proof or schema-valid `blocked_runtime`
  evidence.
- `repo doctor`, proof commands, conformance output, capability discovery, and
  closeout output do not confuse modeled conformance with live runtime parity.
- Agents can discover, invoke, validate, and hand off proof artifacts from the
  shared workspace without private session context.
- Documentation and agent-facing instructions are checked before cleanup is
  announced.

## Slice Lifecycle

Every implementation slice must follow this order:

1. Govern the slice boundary, allowed files, validations, and stop conditions.
2. Implement only the governed slice.
3. Run focused validation.
4. Run simplify, unslopify, HE code review, and testing review.
5. Fix accepted findings.
6. Run adversarial and agent-native reviews before marking done.
7. Update implementation notes and receipts.
8. Run final local validation for the slice.
9. Commit, push, open or update a GitHub PR, and launch PR green-sweep triage.
10. Continue only after the governor confirms the next slice is safe.

## Slice Map

| Slice | Purpose | First Proof |
|---|---|---|
| PU-001 | Command-handle drift repair and repo doctor baseline | Command-handle drift is reachable and blocking |
| PU-002 | P0 runtime evidence schemas and validator | RuntimeCard and EvidenceReceipt validation rejects malformed evidence |
| PU-003 | Codex parity conformance status split | Modeled conformance and live runtime parity are separate statuses |
| PU-004 | Capability discovery and public wrapper fixtures | Agents can discover proof-plane commands through public wrapper fixtures |
| PU-005 | Codex preview source identity and truncation hardening | Preview output names source identity and truncation basis |
| PU-006 | Runtime proof command and blocked runtime receipts | `skills proof --runtime-target codex` emits proof or blocked evidence |
| PU-007 | Shared workspace evidence and closeout integration | Closeout separates proof, tracker, PR, and documentation truth |
| PU-008 | Final validation, docs accuracy, and delivery sweep | Docs, AGENTS-facing guidance, PRs, CI, and receipts align |

## Mandatory Review Stack

Each slice must use:

- `$simplify`
- `$unslopify`
- `$he-code-review`
- `$testing`
- `@adversarial-reviewer`
- `@agent-native-reviewer`
- `$pr-green-sweep` after the PR exists

Review artifacts must be written or a blocker must be recorded. Mailbox text is
not completion evidence.

## Stop Conditions

Stop and classify the blocker if:

- The board validator fails.
- The planned slice requires files outside its allowed set.
- Runtime absence would be reported as success.
- Generated projections, plugin caches, global Codex config, or
  `/Users/jamiecraik/dev/codex` would need mutation.
- A proof surface exists only in docs or tests and is not reachable from a
  command path.
- PR, CI, review, Linear, or mergeability truth cannot be freshly verified for
  a delivery claim.

## Running Implementation Notes

Keep the live browser-readable ledger current at:

`.harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html`

Record decisions that were not in the plan or spec, implementation changes,
tradeoffs, validation results, blockers, and anything Jamie should know while
the work is in progress.

## First Action

Validate this board, then run the active scout task in `state.yaml` to record
the PU-001 implementation boundary before editing implementation code.
