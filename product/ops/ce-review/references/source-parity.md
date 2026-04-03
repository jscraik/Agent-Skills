# Source Parity Notes

## Table of Contents
- [Source inputs](#source-inputs)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)
- [Known constraints](#known-constraints)

## Source inputs
This package was synthesized from:
- `https://github.com/EveryInc/compound-engineering-plugin/tree/847ce3f156a5cdf75667d9802e95d68e6b3c53a4/plugins/compound-engineering/skills/ce-review`
- `config/codex/prompts/workflow-review.md`
- the longer legacy `ce:review` prompt that emphasized exhaustive multi-agent review, serial/parallel modes, conditional migration specialists, protected-artifact filtering, todo capture, and optional end-to-end follow-up

## Preserved behaviors
- PR, branch, current, latest, and artifact review targets
- upstream-style `mode:` parsing adapted into local broad-review semantics
- explicit `base:<ref>` diff-base override and `plan:<path>` context loading
- branch/worktree correctness before analysis
- optional review policy context from `compound-engineering.local.md`
- always-on `agent-native-reviewer` and `learnings-researcher`
- conditional exact-role reviewer fanout by language and risk
- protected-artifact cleanup filtering
- severity ranking using `P1 | P2 | P3`
- merge recommendation for code review and readiness recommendation for artifact review
- optional todo-follow-up after synthesis using the supplied `file-todos` naming and template rules
- `mode:autofix` residual findings landing as ready-to-execute todo work instead of fresh pending triage
- report-only and headless modes skipping todo creation and keeping the review boundary explicit
- optional browser / Xcode verification handoff
- `P1` findings treated as blocking progression

## Intentional modernizations
- kept `ce-review` distinct from `ce-technical-review` instead of letting the broad review stage swallow the focused technical one
- made reviewer fanout bounded by default, with serial fallback for long sessions or large reviewer sets
- treated missing `compound-engineering.local.md` as a compatibility gap, not a blocker
- encoded the supplied `file-todos` workflow into the package references so the review skill can preserve the original todo behavior even when the separate skill package is not yet installed locally
- preserved donor mode parsing while keeping local review read-oriented by default; only explicit `mode:autofix` or `mode:headless` unlock a small mutating follow-up
- adapted the donor's shared-checkout safety rule so browser or simulator verification is not run concurrently with a mutating review loop on the same checkout
- aligned external-doc usage to repo-first review, official OpenAI docs first for OpenAI-product behavior, and Context7 only when current framework/library behavior needs confirmation
- modernized institutional-knowledge lookup to prefer `.harness/memory/LEARNINGS.md`, then compatibility learnings files, then targeted `docs/solutions/`
- kept the stakeholder/scenario deep-dive as a high-risk escalation lane instead of forcing every review into maximal output

## Known constraints
- The legacy prompt assumed more aggressive fix-oriented follow-up automation than this package makes mandatory. In this skill, write-capable remediation remains a follow-up stage rather than a default part of review mode.
- Todo creation is still conditional on repo convention or explicit user request; the workflow is preserved, but not every review should automatically generate tracked work files.
