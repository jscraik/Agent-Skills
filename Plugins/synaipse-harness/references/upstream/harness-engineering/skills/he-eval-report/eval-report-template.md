---
schema_version: 1
artifact_id: <canonical-slug>-eval
artifact_type: he-eval-report
canonical_slug: <canonical-slug>
title: <Title Matching First H1>
harness_stage: he-eval-report
status: draft
date: YYYY-MM-DD
traceability_required: true
origin: <repo-relative plan or PR artifact>
linear_issue: <issue key when tracked>
linear_milestone: <milestone when tracked>
---

<!-- markdownlint-disable MD025 -->

# Title Matching Frontmatter

## Command Summary
BLUF: <one substantive paragraph explaining this report's job, the evaluated work, why closure matters, the closure recommendation, proof state, major blocker or risk, and exact next action>
Decision Needed: <accept | challenge | rework | none>
Top Risks: <one to three risks with consequences>
Next Action: <exact next action>

## Executive Eval Summary
Summary: <overall closure state in one sentence>
Status:
Linear Completion Recommendation:
Primary Blockers:
Confidence:

## Evaluated Slice
Summary: <the exact slice being evaluated>
Linear Project:
Linear Milestone:
Linear Parent Issue:
Linear Sub-Issues:
Reframe Program:
Plugin Harness Engineering Spec:
Affected Files/Modules:
Affected Workflows:
Related ADRs:
Related Core Invariants:

## Linear Definition of Done Status
Summary: <whether the Linear definition of done is satisfied>
Artifact Path:
Definition of Done Status:
Closure Safety:

## Linear Backlink Map
Summary: <whether Linear traceability is complete>
Linear Project:
Linear Milestone:
Linear Parent Issue:
Linear Sub-Issues:
Linear Status Recommendation:
Proof Artifact Links:
Missing Identifiers:
Traceability Repair:

## Source Artifact Trace
Summary: <whether source artifacts support the closure claim>
Linear Plan:
Reframe Program:
Plugin HE Spec:
ADRs:
Core Invariants:
Other Source Artifacts:

## Planned Proof Check
Summary: <whether promised proof was produced>
Promised Proof From Source Artifacts:
Proof Planned Before Implementation: yes | no | unknown
Proof Produced:
Proof Missing:
Interpretation:
Blocks Closure: yes | no

## Functional Validation Results
Summary: <whether functional validation supports closure>
Command or Method:
Result:
Evidence:
Confidence:
Blocks Closure:

## Eval Gate Matrix
Summary: <whether eval gates block completion>
Gate:
Expected:
Actual:
Status: pass | fail | partial | not-run
Evidence:
Confidence:
Blocks Closure: yes | no
Required Action:

## Agentic Eval Validity
Summary: <whether the agentic eval proves the intended capability>
Evaluated Capability / Task:
Task Validity:
Outcome Validity:
Trajectory / Transcript Evidence:
Grader Coverage:
Trial Policy:
Pass@k / Pass^k Reporting:
Authorization Validator:
Saturation / Maintenance Signal:
Blocks Completion: yes | no
Required Action:

## Side-Effect Authorization
Summary: <whether protected actions were authorized>
Protected Action: [REQUIRED: action name or not_applicable with reason]
User Authorization Evidence: [REQUIRED: user approval evidence or not_applicable]
Agent Justification: [REQUIRED: agent claim or not_applicable]
External Party Influence: [REQUIRED: evidence or not_applicable]
Validator Decision: not-run
Validator Confidence: not-run
Suggested Next Step: [REQUIRED: approve, block, or repair step]
Blocks Completion: yes

## Domain Model Integrity Check
Summary: <whether domain invariants remain intact>
Conclusion:
Bounded Context:
Aggregate Invariants:
Translation Evidence:
Scenario or Test Evidence:
Confidence:
Blocks Completion:

## Drift Validation
Summary: <whether drift blocks closure>
Architecture Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]
Routing Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]
Context Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]
Governance Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]
Agent-Native Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]
Moat Drift: [REQUIRED: Improved | Neutral | Regressed | Unknown with evidence]

## Architecture Integrity Check
Summary: <whether architecture integrity is acceptable>
Conclusion:
Evidence:
Blocks Completion:

## Routing Determinism Check
Summary: <whether routing remains deterministic>
Conclusion:
Evidence:
Blocks Completion:

## Context Load Check
Summary: <whether context loading remains bounded>
Conclusion:
Evidence:
Blocks Completion:

## Agent-Native Check
Summary: <whether agents can operate the workflow safely>
Conclusion:
Evidence:
Blocks Completion:

## Governance Simplicity Check
Summary: <whether governance stayed simple enough>
Conclusion:
Evidence:
Blocks Completion:

## Moat Protection Check
Summary: <whether the work preserves the HE moat>
Conclusion:
Evidence:
Blocks Completion:

## Proof Artifacts
Summary: <whether required proof artifacts exist>
Produced:
Required:
Missing:
Planned Before Implementation:
Generated Media Cache Source:
Repository Media Path:
Prompt Metadata Path:
Media Sidecar Path:
Repository Media Exists:
Blocks Completion:
Attach or Link Back to Linear:

## Runtime Persistence and Closure Boundary
Summary: <whether runtime state and closure proof are fresh enough>
Runtime Invocation Receipt: [REQUIRED: run_id/resolved_skill/session evidence or blocked]
Resumption Key: [REQUIRED: artifact path plus issue/PR/branch when relevant]
Live State Refresh: [REQUIRED: repo/tracker/PR/check/runtime refresh or blocked]
Session Evidence Status: [REQUIRED: fresh | historical | stale | not_used | blocked]
Closure Proof Boundary: [REQUIRED: exact evidence that can prove closure]
Coding Lens Status: [REQUIRED: pass | fail | blocked | not_applicable with evidence]
Testing Lens Status: [REQUIRED: pass | fail | blocked | not_applicable with evidence]
Blocks Completion: yes

## Failures / Regressions
Summary: <whether failures or regressions block closure>
Failure or Regression:
Evidence:
Required Corrective Action:
Follow-Up Justified:
Blocks Closure:

## Linear Completion Recommendation
Summary: <the Linear closure recommendation>
Classification: Blocked
Recommended Linear Status:
Required Linear Comment/Update:
Issues to Close:
Issues to Reopen:
Issues to Leave Open:
New Follow-Up Issues:
Labels to Add/Remove:
Milestone Completion:
Project Status Change:
Status Update Needed:
Proof Artifacts to Attach or Link:

## Follow-Up Work
Summary: <whether follow-up work is required>
Classification: [REQUIRED: Do Not Create | Create Follow-Up | Blocked]
Target Linear Project:
Parent Issue or Milestone:
Reason:
Agent-Safe or Human Review Required:

## Core / ADR Update Recommendation
Summary: <whether core or ADR updates are required>
Core Update:
ADR Update:
Reason:

## Evidence & Traceability Matrix
Summary: <whether evidence supports each material claim>
Conclusion:
Fact:
Interpretation:
Assumption:
Evidence:
Affected Files/Modules:
Command or Inspection Method:
Confidence:
Operational Impact:
Blocks Completion:
