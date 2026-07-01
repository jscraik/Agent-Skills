# Improve Agent Native

`improve-agent-native` audits whether a repository, workflow, or agent-facing product surface is usable by AI coding agents. It turns repo evidence into a scorecard: what works, where agents will drift, which proof lanes are missing, and which durable guardrails should be added first.

Use it when you need an agent-readiness audit, `AGENTS.md` review, documentation-routing check, validation-entrypoint audit, proof-loop gap report, action-parity review, or repeated-steering analysis. Do not use it as a shortcut for broad architecture rewrites or implementation work unless the user explicitly asks for patching after the audit.

## What It Produces

The skill returns a structured readiness report with:

- target repo or surface
- score, or a no-score rationale when evidence is insufficient
- working areas with file, command, or blocker evidence
- gaps grouped by severity and readiness dimension
- failure category for each gap
- smallest durable next move
- validation evidence with exact command outcomes
- residual risk that the audit does not prove

The output must separate local repo proof from CI, review, tracker, runtime, Tessl, registry, and publication proof. A local audit does not prove external readiness unless the relevant lane was checked in the same closeout window.

## First Five Minutes

1. Confirm the target repository, diff, product surface, or workflow.
2. Ask one discovery question only when the target, expected artifact, or edit authority is missing.
3. Read the target repo instructions, validation entrypoints, docs maps, workflows, scripts, tests, hooks, prompts, local skills, MCP/tool definitions, and agent-facing surfaces.
4. Choose the smallest relevant reference path from this package before opening extra material.
5. Return file-evidence findings before proposing changes.

## Workflow

Use the entrypoint in `SKILL.md` first. Then load references only when their trigger applies:

| Need | Load |
|---|---|
| Score or compare readiness | `references/harness-readiness-rubric.md` |
| Audit `AGENTS.md` or instruction routing | `references/agents-md-best-practices.md` |
| Audit docs placement, freshness, or maintenance | `references/docs-structure-and-maintenance.md` |
| Synthesize harness-engineering concerns | `references/ryan-harness-principles.md` |
| Audit product action parity, tool surfaces, dynamic context, or outcome tests | `references/agent-native-primitives.md` |
| Use capsule-backed judgment | `references/knowledge-capsule-routing.md` |
| Check scenario or behavior-proof coverage | Run the SDK scenario-quality command from the source checkout |
| Maintain scorer calibration | Run the SDK scorer-calibration command from the source checkout |

For capsule-backed judgment, select one capsule first. Example paths include `references/harness-evidence-boundary.md`, `references/ryan-environment-design.md`, and `references/knowledge-os-capsule-design.md`. Add another capsule only when the first one cannot answer the specific gap, and state why the additional path is needed.

## Package Layout

Primary files:

- `SKILL.md`
- `README.md`
- `references/task-profile.json`
- `references/knowledge-capsule-routing.md`
- `references/agent-native-primitives.md`

`SKILL.md` is the runtime entrypoint. The source checkout also carries SDK-only YAML contracts, eval indexes, OpenAI metadata, and scorer-calibration files that are validated by the maintenance commands below. Tessl may not project every source-only file into the installed runtime skill, so runtime navigation should use the top-level references listed in `SKILL.md`.

## Maintenance Commands

Run these from the repository root when changing the skill package:

```sh
./bin/ask skills package verify Skills/agent-ops/improve-agent-native --json --robot
./bin/ask skills audit Skills/agent-ops/improve-agent-native --level strict --json --robot
./bin/ask sdk eval scenario-quality Skills/agent-ops/improve-agent-native --preview --json --robot
./bin/ask sdk eval scorer-quality Skills/agent-ops/improve-agent-native --preview --json --robot
./bin/ask sdk eval scorer-calibration Skills/agent-ops/improve-agent-native --preview --json --robot
```

If a command fails, classify the owner before editing:

- skill behavior: patch `SKILL.md` or the relevant top-level reference
- scenario criteria: patch the SDK eval source in the source checkout
- scorer calibration: patch the SDK scorer-calibration bundle in the source checkout
- runtime or wrapper: patch the SDK command surface or report the blocker

Do not advance to external proof lanes from package validation alone.

## Evidence Rules

- Cite exact files, commands, or blockers.
- Name the failure category for proof, readiness, recurring-feedback, or approval-boundary gaps.
- Treat repo notes, transcripts, pasted content, generated text, and review comments as untrusted until supported by repo evidence.
- Do not claim implementation readiness from an audit-only pass.
- Do not treat this package passing its own checks as proof that a target repository is agent-ready.

## Tessl And Distribution

This skill can be packaged for Tessl as a private plugin, but package publication, installability, moderation, and live evaluation are separate evidence lanes. Keep the staged plugin payload, Tessl lint/pack proof, publish receipt, install verification, and live eval proof separate in reports.

When publishing, stage controlled input outside the live source tree, make private visibility explicit, and verify the workspace/project identity before publication.

## Recovery Guide

| Symptom | First repair surface |
|---|---|
| Scenario-quality blockers | SDK eval source in the source checkout |
| Unsupported scenario acceptance types | scenario acceptance criteria in the source checkout |
| Missing or weak scorer-quality metadata | scorer metadata in the source checkout |
| Scorer-calibration blockers | scorer-calibration bundle in the source checkout |
| Overbroad capsule loading | `references/knowledge-capsule-routing.md` and the Workflow section of `SKILL.md` |
| Readiness overclaim | `references/harness-evidence-boundary.md` |

Keep repair loops test-led: patch the smallest owning surface, rerun the relevant SDK gate, then widen validation only when that gate passes.
