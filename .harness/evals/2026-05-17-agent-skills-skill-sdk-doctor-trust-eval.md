---
schema_version: 1
artifact_id: agent-skills-skill-sdk-doctor-trust-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-skill-sdk-doctor-trust
title: Agent Skills Skill SDK Doctor Trust Eval
harness_stage: he-eval-report
status: blocked_runtime_contract
traceability_required: true
origin: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
linear_issue: JSC-329
date: 2026-05-20
---

# Agent Skills Skill SDK Doctor Trust Eval

## Executive Eval Summary

Status: blocked before readiness semantics. The current checkout does not expose
`skills doctor` or `skills package` as public `./bin/ask skills` actions, so
RF-1 cannot honestly start from a blocked-runtime doctor payload. The first RF-1
implementation proof is command registration plus a structured doctor JSON
contract for `context7`.

Linear Completion Recommendation: Do not complete JSC-329 until the invalid
choice baseline is replaced by a tested doctor payload.

Confidence: High for the command-surface blocker because it is based on live CLI
help and parser output in this checkout.

## Evaluated Slice

Linear Issue: `JSC-329`

Primary Artifacts:

- `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md`
- `.harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md`
- `.harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md`
- `.harness/README.md`
- `Infrastructure/references/skills-sdk-apparatus-lens.md`
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/command_metadata.py`

## Live Command Evidence

| Command | Outcome | Eval implication |
| --- | --- | --- |
| `./bin/ask skills --help` | pass: lists `list, budget, handles, resolve, parse, proof, prove, explain, route, goal, improve, starter, sync, audit, validate-skill-gate, validate-openai-format, validate-boundaries, install, fold, init`; does not list `doctor`, `package`, `profiles`, or `events`. | RF-1 must include command registration proof before field-level readiness assertions. |
| `./bin/ask skills doctor context7 --json --robot` | blocked: exits 2 with parser error `invalid choice: 'doctor'`. | The prior blocked-runtime baseline claim is false in this checkout. Preserve this as the pre-RF-1 snapshot. |
| `./bin/ask skills package context7 --json --robot` | blocked: exits 2 with parser error `invalid choice: 'package'`. | Package-readiness comparison is RF-2+ unless RF-1 deliberately introduces an unavailable/package-not-implemented field. |

## RF-1 Required Proof

RF-1 must prove these dimensions before broader SDK work starts:

| Dimension | Required RF-1 proof | Current status |
| --- | --- | --- |
| Command registration | `skills doctor` appears in `./bin/ask skills --help` and dispatches through `Infrastructure/bin/ask`. | missing |
| Command guidance parity | Parser actions, help output, command metadata, and unknown-action guidance expose the same `ask skills` action set. | missing |
| Structured outcome | `data.skill_doctor` validates against `Infrastructure/config/schemas/skill-doctor.v1.schema.json` and contains `schema_version`, `status`, `target_summary`, `checks`, `blockers`, `warnings`, `operation_context`, `contract_schemas`, `agent_summary`, and `next_command`. | missing |
| Status precedence | Focused test proves blockers outrank warnings, warnings outrank pass, and pass has no blockers or warnings. | missing |
| Current command comparison | Doctor output preserves or explains the current `skills proof`/`skills prove` reachability and outcome-proof signals for `context7`. | missing |
| Unavailable package seam | Doctor reports package readiness as `unavailable`, `not_implemented`, or a similarly explicit non-pass state until a real package command exists. | missing |
| Representative coverage | One additional non-`context7` skill-class fixture validates against the same schema and status semantics. | missing |
| Snapshot discipline | Eval stores the pre-RF-1 invalid-choice output and the post-RF-1 doctor output with tolerated dynamic fields. | missing |

## RF-2+ Proof Matrix

These are real SDK design inputs, but they should not expand JSC-329 unless RF-1
can expose a stable doctor surface first:

| Dimension | Route | Reason |
| --- | --- | --- |
| Package build/projection simulation | RF-2+ `skills package-doctor <skill>` | Requires package metadata, deterministic layout, archive inspection, projection target modeling, and additive upgrade policy. |
| Lifecycle events | RF-2+ events/schema lane | Requires tool, hook, package, projection, eval, and delegated-agent events that RF-1 can reference but should not invent. |
| Provenance | RF-2+ package/report lane | Needs stable skill/package/plugin/source identifiers that survive into eval and harness artifacts. |
| Namespace and permissions | RF-2+ SDK metadata lane | Needs package namespace, permission profile, required roots, deny semantics, and enablement states. |
| Harness consumer boundary | RF-4 after Agent Skills Kit owns schemas | Coding-harness should invoke and preserve evidence; it should not duplicate doctor/package logic. |
| Generated emitters | RF-2+ after schema registry exists | Skill package, docs, eval, Linear, plugin, and runtime projection emitters need a typed contract first. |

## Closure Gate

Do not close JSC-329 on prose, AI review, or source presence. Closure requires:

- pre-RF-1 parser-failure snapshot for `skills doctor context7`;
- `skills doctor` registered in help and dispatch;
- `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py::test_skills_action_metadata_matches_parser -q`;
- `artifacts/skill-doctor/context7.before.json`,
  `artifacts/skill-doctor/context7.after.json`, and
  `artifacts/skill-doctor/<second-skill>.after.json`;
- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py::test_skill_doctor_snapshots_validate_schema -q`;
- focused doctor contract test result;
- post-registration `skills doctor context7 --json --robot` output;
- second non-`context7` skill-class fixture result;
- `skills prove context7 --json --robot` comparison output;
- explicit coverage gaps for package/profile/event fields that remain RF-2+;
- changed-file validation evidence.

## Validation Commands Recorded In This Eval

Command: `./bin/ask skills --help` -> pass (confirmed current action list and missing doctor/package/profile/event actions).

Command: `./bin/ask skills doctor context7 --json --robot` -> blocked (exit 2, parser invalid choice for `doctor`).

Command: `./bin/ask skills package context7 --json --robot` -> blocked (exit 2, parser invalid choice for `package`).
