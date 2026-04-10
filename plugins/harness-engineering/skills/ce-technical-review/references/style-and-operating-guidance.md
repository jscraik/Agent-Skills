# Style and Operating Guidance

## Table of Contents
- [Purpose](#purpose)
- [Standards snapshot (April 2026)](#standards-snapshot-april-2026)
- [Technical review philosophy](#technical-review-philosophy)
- [Depth variation model](#depth-variation-model)

## Purpose
This reference preserves higher-context guidance for technical-review quality without bloating route-critical instructions in `SKILL.md`.

## Standards snapshot (April 2026)
- Keep skill routing explicit: what it does and when to use it.
- Keep review output findings-first, evidence-backed, and minimal-ambiguity.
- Resolve mode and target deterministically before analysis.
- Prefer repo-grounded evidence; escalate to external docs only when behavior claims depend on current framework/library semantics.
- Preserve high-value reasoning context via references instead of deleting it during compaction.

## Technical review philosophy
- Correctness and regression risk come before style.
- Findings should be specific enough that implementers can act without guessing.
- Reviewer fanout is a tool, not a quality metric; use the smallest set that materially improves confidence.
- Technical review should reveal the highest-leverage engineering risks early to reduce downstream churn.

## Depth variation model
Adapt technical-review depth to risk and target shape.

Risk level:
- High risk: prioritize correctness, persistence, security, reliability, and rollback safety.
- Medium risk: balanced coverage with targeted specialist lanes.
- Low risk: concise baseline with explicit unknowns where evidence is limited.

Target type:
- Code/diff: bug risk, regressions, adherence, security/perf/data hazards.
- Spec/plan: ambiguity, sequence correctness, validation realism, rollout and failure handling.

Time pressure:
- Time-boxed: focus on P0/P1 first and capture unresolved verification as open questions.
- Full pass: include maintainability and medium-term operational concerns after blocker-class risks.
