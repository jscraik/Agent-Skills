# Document Review Finding Tiers

Read when: strengthening a spec, plan, strategy artifact, Linear plan, refactor
program, or eval from review feedback.

## Purpose

Review output should improve HE artifacts without creating process noise. These
tiers classify what the agent may apply, what requires steering, and what should
stay informational.

## Tiers

`safe_auto`
: Evidence-backed correction that preserves the approved slice and improves
  clarity, traceability, validation, or artifact identity. The agent may apply
  it and record the change.

`gated_auto`
: Likely valid but it changes acceptance, sequencing, validation gates,
  ownership, Linear routing, or closure status. Apply the interactive steering
  contract before changing the artifact unless running headless; in headless
  mode record an autonomous assumption.

`manual`
: Requires human judgment, product authority, Linear authority, security
  approval, irreversible architectural choice, or interpretation of conflicting
  evidence. Do not silently apply.

`fyi`
: Useful observation with no immediate artifact change. Record only if it helps
  future traceability; do not create follow-up work by default.

## Required Fields

```yaml
finding_tier: safe_auto|gated_auto|manual|fyi
finding_evidence: "<file, command, artifact, Linear, or inspection method>"
affected_artifact: "<repo-relative path or not_applicable>"
action_taken: applied|asked|recorded|rejected|blocked
reason: "<why this tier applies>"
```

## Rules

- Do not turn every finding into a Linear issue.
- Do not use `safe_auto` when scope, acceptance, ownership, or closure state
  changes.
- `manual` and unresolved `gated_auto` findings may block downstream execution
  if they affect acceptance, validation, architecture invariants, or Linear
  completion.
