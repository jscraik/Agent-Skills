---
id: lens.operator-evidence
title: Operator Evidence
type: expert_lens
version: 1.0.0
status: stable
triggers:
  keywords:
    - evidence
    - proof
    - receipt
    - closeout
    - handoff
    - validation gate
    - blocked
    - runtime truth
  task_intents:
    - validation_review
    - agent_workflow_design
    - sdk_contract_review
    - repo_hygiene
  file_signals:
    - .harness/
    - artifacts/
    - AGENTS.md
    - README.md
    - scripts/
strengths:
  - proof_lane_separation
  - handoff_quality
  - blocker_classification
  - runtime_evidence
avoid_when:
  - task_intent: pure_ui_copy
pairs_well_with:
  - lens.testing-confidence
  - lens.progressive-disclosure
output_categories:
  - missing_receipt
  - mixed_truth_lane
  - unverifiable_closeout
  - weak_handoff
priority: 88
---

# Operator Evidence

## Review Questions

1. Does the output separate local validation, runtime truth, CI truth, review truth, and merge readiness?
2. Are exact commands, artifacts, and blocker classes recorded?
3. Can another agent reproduce the evidence path without private chat context?
4. Does the handoff say what is proven and what remains unproven?
5. Are stale artifacts, summaries, and model confidence prevented from acting as proof?

## Failure Modes

- A passing local command is reported as CI or merge readiness.
- A review or subagent message is treated as artifact evidence.
- A blocker is described vaguely instead of classified.
- Handoff text omits the command or artifact needed for the next agent.
- Evidence exists only in a local scratch path that cannot support later review.

## Recommended Moves

- Emit structured receipts for selection, validation, and handoff decisions.
- Name truth lanes explicitly when reporting results.
- Keep missing evidence as a first-class blocked status.
- Prefer artifact-backed summaries over chat-only completion claims.
