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
BLUF: <closure recommendation and reason>
Decision Needed: <accept | challenge | rework | none>
Top Risks: <one to three risks with consequences>
Next Action: <exact next action>

## BLUF-Only Summary
1. <Executive Eval Summary BLUF>
2. <Functional Validation Results BLUF>
3. <Linear Completion Recommendation BLUF>

## Executive Eval Summary
BLUF: <overall closure state in one sentence>
Status:
Linear Completion Recommendation:
Primary Blockers:
Confidence:

## Evaluated Slice
BLUF: <the exact slice being evaluated>
Linear Project:
Linear Milestone:
Linear Parent Issue:
Linear Sub-Issues:
Refactor Program:
Plugin Harness Engineering Spec:
Affected Files/Modules:
Affected Workflows:
Related ADRs:
Related Core Invariants:

## Linear Definition of Done Status
BLUF: <whether the Linear definition of done is satisfied>
Artifact Path:
Definition of Done Status:
Closure Safety:

## Linear Backlink Map
BLUF: <whether Linear traceability is complete>
Linear Project:
Linear Milestone:
Linear Parent Issue:
Linear Sub-Issues:
Linear Status Recommendation:
Proof Artifact Links:
Missing Identifiers:
Traceability Repair:

## Source Artifact Trace
BLUF: <whether source artifacts support the closure claim>
Linear Plan:
Refactor Program:
Plugin HE Spec:
ADRs:
Core Invariants:
Other Source Artifacts:

## Planned Proof Check
BLUF: <whether promised proof was produced>
Promised Proof From Source Artifacts:
Proof Planned Before Implementation: yes | no | unknown
Proof Produced:
Proof Missing:
Interpretation:
Blocks Closure: yes | no

## Functional Validation Results
BLUF: <whether functional validation supports closure>
Command or Method:
Result:
Evidence:
Confidence:
Blocks Closure:

## Eval Gate Matrix
BLUF: <whether eval gates block completion>
Gate:
Expected:
Actual:
Status: pass | fail | partial | not-run
Evidence:
Confidence:
Blocks Closure: yes | no
Required Action:

## Agentic Eval Validity
BLUF: <whether the agentic eval proves the intended capability>
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
BLUF: <whether protected actions were authorized>
Protected Action:
User Authorization Evidence:
Agent Justification:
External Party Influence:
Validator Decision: exempt
Validator Confidence: high
Suggested Next Step:
Blocks Completion: no

## Domain Model Integrity Check
BLUF: <whether domain invariants remain intact>
Conclusion:
Bounded Context:
Aggregate Invariants:
Translation Evidence:
Scenario or Test Evidence:
Confidence:
Blocks Completion:

## Drift Validation
BLUF: <whether drift blocks closure>
Architecture Drift: Unknown
Routing Drift: Unknown
Context Drift: Unknown
Governance Drift: Unknown
Agent-Native Drift: Unknown
Moat Drift: Unknown

## Architecture Integrity Check
BLUF: <whether architecture integrity is acceptable>
Conclusion:
Evidence:
Blocks Completion:

## Routing Determinism Check
BLUF: <whether routing remains deterministic>
Conclusion:
Evidence:
Blocks Completion:

## Context Load Check
BLUF: <whether context loading remains bounded>
Conclusion:
Evidence:
Blocks Completion:

## Agent-Native Check
BLUF: <whether agents can operate the workflow safely>
Conclusion:
Evidence:
Blocks Completion:

## Governance Simplicity Check
BLUF: <whether governance stayed simple enough>
Conclusion:
Evidence:
Blocks Completion:

## Moat Protection Check
BLUF: <whether the work preserves the HE moat>
Conclusion:
Evidence:
Blocks Completion:

## Proof Artifacts
BLUF: <whether required proof artifacts exist>
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

## Failures / Regressions
BLUF: <whether failures or regressions block closure>
Failure or Regression:
Evidence:
Required Corrective Action:
Follow-Up Justified:
Blocks Closure:

## Linear Completion Recommendation
BLUF: <the Linear closure recommendation>
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
BLUF: <whether follow-up work is required>
Classification: Do Not Create
Target Linear Project:
Parent Issue or Milestone:
Reason:
Agent-Safe or Human Review Required:

## Core / ADR Update Recommendation
BLUF: <whether core or ADR updates are required>
Core Update:
ADR Update:
Reason:

## Evidence & Traceability Matrix
BLUF: <whether evidence supports each material claim>
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
