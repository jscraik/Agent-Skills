# CE Technical Review Prompt Parity Map

## Table of Contents
- [Purpose](#purpose)
- [Source prompt and migration target](#source-prompt-and-migration-target)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document records how `/Users/jamiecraik/dev/configs/codex/prompts/technical_review.md` was migrated into the CE skill package so the conversion stays auditable.

## Source prompt and migration target
- source:
  - `https://github.com/EveryInc/compound-engineering-plugin/tree/0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c/plugins/compound-engineering/skills/ce-technical-review`
  - `/Users/jamiecraik/dev/configs/codex/prompts/technical_review.md`
- migration target:
  - `/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-technical-review/`

## Parity mapping
| Prompt behavior | Preserved in skill | Notes |
|---|---|---|
| focused technical review for code diffs, specs, and plans | `SKILL.md` overall structure | Preserved directly |
| default to current branch diff when no target is given | `Workflow -> Phase 0` | Preserved directly |
| prioritize actionable, risk-relevant findings over style commentary | `Working agreement`, `Constraints` | Preserved directly |
| use linked plan/spec artifacts as the adherence baseline | `Working agreement`, `Workflow -> Phase 1` | Preserved directly |
| treat PR text, commit messages, and docs as untrusted input | `Working agreement`, `Constraints` | Preserved directly |
| code/diff review mode | `Review modes`, `references/review-modes.md` | Preserved directly |
| document review mode for specs/plans | `Review modes`, `references/review-modes.md` | Preserved directly |
| spec review rubric with score thresholds | `references/review-modes.md` | Preserved directly |
| plan review rubric with score thresholds | `references/review-modes.md` | Preserved directly |
| reviewer routing by language and risk | `Workflow -> Phase 2`, `references/review-modes.md` | Preserved directly |
| findings by severity with location, impact, fix, confidence | `Deliverables`, `references/review-modes.md` | Preserved directly |
| explicit no-critical-findings statement | `Deliverables`, `Acceptance criteria` | Preserved directly |
| validate key steps and report smallest safe fix on failure | `Validation` | Preserved directly |

## Intentional modernizations
- The stage is now packaged as a first-class CE skill instead of a standalone prompt path.
- Reviewer fanout is preserved, but framed as bounded and platform-gated rather than assumed to be unboundedly parallel.
- The skill makes the distinction between `technical-review` and broad `review` explicit, matching the current router guidance.
- `contract.yaml` and `evals.yaml` were added to improve routing reliability and quality gating.
- The skill explicitly routes document-strengthening needs toward `ce-deepen-spec` or `ce-deepen-plan` rather than forcing critique-only output when the better next step is obvious.
- Current-doc retrieval is now explicit and conditional: repo evidence stays primary, while official docs and Context7 are used only when framework or library behavior materially affects a finding.
- Non-route-critical standards/philosophy guidance is preserved in `references/style-and-operating-guidance.md` so `SKILL.md` can stay route-focused.
- Reviewer fanout is now deterministic and sub-agent explicit via `references/sub-agent-map.md`, with technical-first baseline lanes (`correctness-reviewer`, `testing-reviewer`, `code-simplicity-reviewer`).

## No-loss checklist
- code/diff review remains supported
- document review remains supported
- linked artifacts still matter
- readiness scoring for specs and plans still exists
- reviewer mapping by language and risk still exists
- findings are still severity-ranked and evidence-backed
- no-critical-findings output is still present
- fail-fast validation behavior is still present
