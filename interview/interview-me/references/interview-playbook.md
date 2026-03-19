# Interview Me Playbook

## Table of Contents
- [Purpose](#purpose)
- [Decision-first sequence](#decision-first-sequence)
- [Question templates](#question-templates)
- [Branch logic](#branch-logic)
- [Approval gate contract](#approval-gate-contract)
- [Quality checklist](#quality-checklist)

## Purpose
This runbook holds deep mechanics for `interview-me` so `SKILL.md` stays concise and routing-focused.

## Decision-first sequence
1. Frame the target decision in one sentence.
2. Ask one highest-leverage question with bounded options.
3. Record chosen option and assumptions.
4. Ask one follow-up only if a blocking uncertainty remains.
5. Stop at the approval gate and provide the handoff summary.

## Question templates
Use one template per turn.

`Scope template`
- "Which scope is right for this iteration?"
- Option A: smallest safe slice (recommended)
- Option B: medium scope with known tradeoffs
- Option C: broad scope with higher delivery risk

`Risk template`
- "Which risk posture should govern this change?"
- Option A: conservative rollout (recommended)
- Option B: balanced rollout
- Option C: aggressive rollout

`Validation template`
- "What validation depth do you want before handoff?"
- Option A: smoke checks only
- Option B: focused verification (recommended)
- Option C: full verification suite

## Branch logic
- If user picks the recommended option, proceed directly to handoff summary.
- If user picks a higher-risk option, add one mitigation question before handoff.
- If user response is ambiguous, restate options and ask for a single explicit choice.
- If user declines follow-up questions, proceed with explicit assumptions and label open risks.

## Approval gate contract
Use this minimal shape when machine-readable output is requested.

```yaml
schema_version: 1
decision_id: interview-me/<timestamp-or-seq>
status: approved | needs-input | declined
decision:
  prompt: <one sentence>
  selected_option: <label>
assumptions:
  - <assumption>
constraints:
  - <constraint>
open_risks:
  - <risk or empty>
next_handoff:
  skill: <target execution skill>
  summary: <concise handoff sentence>
```

## Quality checklist
- One decision track per turn.
- One primary question at a time.
- Options are concrete and mutually exclusive.
- Assumptions and constraints are visible before recommendations.
- Approval status is explicit before any execution handoff.
