# Agentation Deep Workflows and Troubleshooting

## Table of Contents
- [Scope](#scope)
- [Layered verification matrix](#layered-verification-matrix)
- [Mode-specific execution notes](#mode-specific-execution-notes)
- [Troubleshooting decision tree](#troubleshooting-decision-tree)
- [Evidence checklist](#evidence-checklist)
- [Escalation rules](#escalation-rules)

## Scope

This guide holds deeper operational details that are intentionally omitted from `SKILL.md` to keep the skill concise.

Primary skill file:
- `../SKILL.md`

## Layered verification matrix

Run layers in sequence and stop at the first hard blocker.

1. Mount layer
- Confirm dependency exists in lockfile-managed install surface.
- Confirm root mount or provider wrapper exists in the app shell.
- Confirm dev-only posture unless user explicitly requests runtime exposure changes.

2. Endpoint layer
- Confirm endpoint configuration matches expected local service values.
- Confirm endpoint path/protocol is consistent with current environment.
- If endpoint is remote, explicitly report risk before edits.

3. MCP layer
- Confirm MCP registration exists and tooling is discoverable.
- Check MCP health independently from webhook delivery.
- Treat missing MCP tools as control-plane failure, not application-state failure.

4. Webhook layer
- Confirm webhook URL wiring and callback route ownership.
- Validate submit path and response handling independently.
- Do not infer webhook health solely from annotation UI behavior.

5. Mode readiness layer
- For `watch` and `critique`, confirm readiness transitions.
- For `self-driving`, confirm explicit user approval and stronger guardrails.

## Mode-specific execution notes

`manual`
- Prefer explicit step-by-step checks and deterministic evidence.
- Use this mode as baseline before any autonomous flow.

`watch`
- Verify observer loop startup and event capture boundaries.
- Record first-success evidence before claiming readiness.

`critique`
- Limit scope to review and bounded edits.
- Keep changes narrowly focused on observed blockers.

`self-driving`
- Require explicit confirmation before enabling autonomous execution.
- Maintain conservative rollback posture and clear intervention points.

## Troubleshooting decision tree

1. No annotations visible
- Check mount layer first.
- If mount passes, check endpoint and webhook separately.
- If endpoint fails, stop and repair endpoint before webhook work.

2. MCP tools missing
- Treat as control-plane issue.
- Do not proceed with workflow claims until MCP registration/health is confirmed.

3. Webhook failures with healthy MCP
- Focus on callback route and submit-path evidence.
- Report as data-plane failure; keep MCP status as pass.

4. Mixed signals across layers
- Return partial state with explicit per-layer evidence.
- Provide one next deterministic command, not a broad multi-edit plan.

## Evidence checklist

For each layer include:
- observed status (`pass|blocked|partial`)
- one concrete evidence item (command output, file location, or explicit non-run reason)
- immediate next action if blocked

For final summary include:
- mode used
- first blocker
- least-risk next step

## Escalation rules

- Escalate to the user when:
  - runtime entrypoint is ambiguous
  - scope must expand from verify-only to edits
  - mode must escalate to `self-driving`
  - behavior would change production posture

- Do not escalate when:
  - a deterministic blocker has one obvious minimal fix and user already allowed edits
  - evidence is sufficient to propose the next bounded command
