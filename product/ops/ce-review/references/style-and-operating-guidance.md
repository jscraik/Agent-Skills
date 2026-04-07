# Style and Operating Guidance

## Table of Contents
- [Purpose](#purpose)
- [Standards snapshot (April 2026)](#standards-snapshot-april-2026)
- [Core review philosophy](#core-review-philosophy)
- [Depth variation model](#depth-variation-model)
- [Reviewer fanout posture](#reviewer-fanout-posture)

## Purpose
This reference preserves higher-context guidance that improves review quality without bloating `SKILL.md`.

Open this when you need:
- rationale behind the workflow constraints,
- guidance for adapting review depth to risk and time,
- decision support for reviewer fanout and synthesis quality.

## Standards snapshot (April 2026)
- Keep each skill scoped to one reusable job, with routing-first description (`what` + `when`).
- Prefer explicit routing, realistic examples, and validation over implicit prompt assumptions.
- Use repo guidance and prior institutional learnings before external research.
- Keep one current step in focus and make mode/target resolution deterministic before analysis.
- Preserve valuable nuance through references instead of deleting context during compaction.

## Core review philosophy
- Broad review exists to improve decision quality, not to maximize output volume.
- Prioritize concrete blockers and evidence-backed risk over exhaustive commentary.
- Synthesis quality matters as much as issue discovery: dedupe, prioritize, and route next action clearly.
- Verdict quality is part of the deliverable: `Pass`, `Conditional`, or `Fail` should be defensible from evidence.

## Depth variation model
Adapt review depth to context while preserving severity and safety standards.

Risk level:
- High risk: deeper contract, rollout, security, and failure-mode checks.
- Medium risk: balanced coverage with selective specialist fanout.
- Low risk: concise baseline coverage with focused validation.

Artifact type:
- Code/package: correctness, regression, persistence, operational risk.
- Spec/plan/solution: consistency, constraints, traceability, stage readiness.

Time pressure:
- Time-boxed: prioritize P0/P1/P2 signal and explicit unknowns.
- Full pass: include broader maintainability and medium-term reliability considerations.

## Reviewer fanout posture
- Start with the smallest reviewer set that materially improves confidence.
- Increase fanout when language mix, architecture spread, or risk profile justifies it.
- Prefer bounded parallelism; switch to serial when session or result handling constraints increase failure risk.
- Never treat fanout size as a quality proxy; synthesis clarity is the quality bar.
