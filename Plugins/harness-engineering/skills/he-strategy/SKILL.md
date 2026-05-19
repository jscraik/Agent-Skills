---
name: he-strategy
description: "Creates engineering strategy documents, decision records, confidence assessments, and repo direction summaries from evidence. Use when architecture choices, execution direction, or future-agent guidance need facts, tradeoffs, and authority limits before implementation."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Harness Engineering Strategy

## Philosophy
Write bounded strategy from verified evidence. Strategy can guide future work, but it does not authorize implementation, tracker mutation, or enforcement changes.

## When to Use
Use for one strategy mode: repo intent, architecture review, triage, repo cognition pipeline, ADR/core compression, moat/drift analysis, source-prompt equivalence, or future-agent guidance.

## When Not to Use
Do not write specs, implementation plans, code review, Linear payloads, or refactors. Route admitted execution to `he-spec`, `he-plan`, `he-work`, `he-reframe`, or `he-linear-plan`.

## Inputs
Selected mode, repo files, relevant `.harness/**` artifacts, source prompt family when applicable, date/context for naming, and any live issue/PR evidence.

## Outputs
Write one selected artifact under `.harness/features/`, `.harness/review/`, `.harness/triage/`, `.harness/strategy/`, `.harness/decisions/`, or `.harness/core/`; otherwise return `Do Not Create`.

## Procedure
Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, superseded, or
low-signal text.

1. Select one mode. If the user asks for the full repo cognition pipeline, produce separate intent, architecture review, and triage artifacts.
2. Start with 2-3 focused surfaces. If they do not prove the claim, read one more. Stop at five unless the user asks for deeper research.
3. For each conclusion, split `fact` from `interpretation`:
   - fact: has file, command, issue, PR, or artifact evidence.
   - interpretation: has confidence and authority limits.
4. Add one stop condition: what new evidence would make the strategy wrong.
5. Validate naming, sources, evidence matrix, confidence, authority limits, stop condition, and BLUF shape before handoff.

## Validation
Fail fast: stop at the first failed gate and do not proceed until it is fixed, waived by an authorized gate, or reported as blocked. For generated artifacts, run or block:

~~~bash
rg -n "<strategy-keyword>" .harness Plugins Skills Docs
git log --oneline -- <relevant-path>
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <strategy-path> --json
~~~

If a gate fails, fix the artifact and re-run the same command once. If it still fails, return `blocked` with the exact failure.

## Failure Handling
If evidence is missing, write `Unknown`. If the artifact would add low-value governance, return `Do Not Create`. If the strategy becomes implementation by stealth, stop and route to the execution skill only after a selected slice exists.

## Safety Boundaries
Redact secrets. External mutation, broad repo edits, destructive commands, credential use, installs, and deployment require explicit approval. Do not edit runtime projections as source.

## Handoff Rules
Hand off only when the strategy exposes a selected execution slice. Humans keep authority for ADRs, core invariant changes, strategic deletion, and unresolved instruction conflicts.

## Gotchas
- Prompt similarity is not source-prompt equivalence; compare coverage and uninspected surfaces.
- Process volume is not moat unless it is tied to a verified feedback loop.
- Narrow evidence can still produce a useful strategy if authority limits are explicit.

## Output Format
Use this shape:

~~~yaml
schema_version: 1
selected_mode: architecture_review
artifact_path: .harness/strategy/2026-05-16-local-review-loop.md
facts:
  - evidence: "Infrastructure/scripts/lib/ask/skill_review_dashboard.py"
    claim: "Dashboard HTML is generated from local review JSON."
interpretations:
  - claim: "A shared score vocabulary should prevent runner/dashboard drift."
    confidence: medium
authority_limits:
  - "No live Tessl registry publish path was inspected or changed."
stop_condition: "Runner stops emitting score categories."
validation:
  - command: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
    outcome: pass
future_agent_guidance:
  - "Prefer local external-review artifacts over registry state for private skills."
~~~

## Examples
- When the user asks, "Review whether the local skill-review dashboard should share signal names with the runner," inspect the runner and dashboard files, validate the focused pytest gate, then write one bounded architecture-review artifact.
- When the user asks, "Compress this ADR set into future-agent guidance," inspect the ADRs and source files, validate BLUF structure, and do not create Linear issues.

## References
- Mode contracts: `../../references/skills/he-strategy/strategy-output-contract.md`
- Repo cognition pipeline: `../../references/skills/he-strategy/repo-cognition-pipeline.md`
- Architecture lenses: `../../references/skills/he-strategy/architecture-lens-canon.md`
- Source-prompt comparison: `../../references/skills/he-strategy/source-prompt-preservation.md`
- Shared HE gates: `../../references/subagent-call-contract.md`, `../../references/deferred-context-index.md`
- Software-literature strategy lenses: `../../../../Infrastructure/references/software-literature-expert-lens-pack.md`, `../../../../Infrastructure/references/software-literature-skill-expertise-map.md`
