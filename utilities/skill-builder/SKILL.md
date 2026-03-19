---
name: skill-builder
description: "Create, revise, benchmark, and quality-gate Codex skills (SKILL.md plus scripts, references, evals, and packaging). Use this skill when the user asks to build, audit, improve, compare, package, or safely install local/imported skill folders. Scope exclusions: unrelated app features, generic bug fixing, plugin package conversion, or session-log audits."
metadata:
  skill-type: code_quality_review
---

# Skill Builder
Design, improve, validate, and package high-quality Codex skills.
**Version**: 1.12.0 · **Last updated**: 2026-03-17

## Table of Contents
- [Working agreement](#working-agreement)
- [Scope and triggers](#scope-and-triggers)
- [OpenAI skill format and progressive disclosure](#openai-skill-format-and-progressive-disclosure)
- [Semantic tag governance](#semantic-tag-governance)
- [Modes](#modes)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Response format](#response-format)
- [Philosophy](#philosophy)
- [Examples](#examples)
- [Output contract](#output-contract)
- [Skill creation process](#skill-creation-process)
- [Execution guardrails](#execution-guardrails)
- [Validation](#validation)
- [Constraints and safety](#constraints-and-safety)
- [Install-distribute mode](#install-distribute-mode)

## Working agreement
- Follow the repo `AGENTS.md`; treat it as a map, not a megadoc.
- Keep the artifact boundary explicit: local Codex CLI -> `./artifacts/`, hosted shell -> `/mnt/data/`.
- Path confinement default: write inside approved repo roots and `./artifacts/`; `USER` scope is an explicit `install-distribute` opt-out with confirmation + allowlist.
- Keep `SKILL.md` concise with progressive disclosure:
  - target <= 320 lines
  - hard cap <= 360 lines
- Start with the smallest viable package boundary and 2-3 focused surfaces on first pass.
- Move deep policy into `references/`; move repeatable mechanics into `scripts/`.

## Scope and triggers
Use this skill when the user asks to:
- create a new skill;
- improve an existing skill's routing, workflow, safety, or portability;
- audit a skill against validators and evals;
- compare variants with shared evals;
- package a validated skill;
- refine skill-graph contracts tied to recursive workflow operations;
- list, install, update, or deconflict local/imported skill folders (`install-distribute` mode).

Keep this skill out of scope for: unrelated app feature coding; generic bug-fixing outside skill quality; routine non-skill docs edits; plugin conversion (`codex-plugin-builder`); session-scan coverage (`codex-sessions-skill-scan`).

## OpenAI skill format and progressive disclosure
Enforce OpenAI/Codex skill format by default:
- frontmatter uses official keys only:
  - required: `name`, `description`
  - optional: `license`, `allowed-tools`, `metadata`
- for this repository, use `metadata.skill-type` to classify skills for semantic indexing and governance checks
- keep `description` as routing logic (what + when), not a procedure dump;
- keep `SKILL.md` as the map:
  - route-critical boundaries, required inputs, output contract, and safety guardrails stay in `SKILL.md`
  - long examples, compatibility matrices, and operational runbooks move to `references/`
  - deterministic helpers stay in `scripts/`
- for non-trivial responses, include machine-checkable output contracts with `schema_version`.

## Semantic tag governance
Use semantic tags to complement directory categories without renaming folders.

Canonical `metadata.skill-type` values:
- `library_api_reference`
- `product_verification`
- `data_fetch_analysis`
- `team_automation`
- `scaffolding_templates`
- `code_quality_review`
- `ci_cd_deployment`
- `runbook`
- `infrastructure_ops`

Governance rules:
- for `create` mode in this repo, set `metadata.skill-type` on every new skill;
- for `improve` mode in this repo, preserve existing `metadata.skill-type` unless there is an explicit reason to retag;
- if no canonical value fits, choose the closest fit and add a short rationale in the change summary instead of inventing a new value;
- add new semantic-type values only with explicit user approval;
- keep folder taxonomy as-is; semantic tags are a second axis, not a replacement.

Lint and generation expectations:
- run `bash scripts/sync_skills.sh` after semantic-tag changes;
- run `bash scripts/lint_skill_types.sh` and require a clean pass (`Missing: 0`, `Invalid: 0`);
- treat `[WARN] Unrecognized metadata.skill-type ...` output as a governance failure to be fixed before claiming completion;
- confirm `docs/skills-by-type.md` regenerated successfully when tags change.

## Modes
Choose the smallest mode that fits:
- `create`
- `improve` (includes `upgrade`)
- `eval`
- `benchmark-lite`
- `graph`
- `package`
- `install-distribute`

Default to `create` or `improve`.

## Required inputs
- skill goal and boundary;
- 3-10 example prompts across happy, edge, and should-not-trigger cases;
- target environment: `codex`, `claude`, or `portable`;
- required tools, schemas, templates, and policy constraints;
- compatibility posture (`learn`, `guided`, `execute`);
- preferred fallback strategy (`strict`, `minimal`, `rollback-safe`) when requirements are partial.

If critical inputs are missing, ask only the minimum needed to proceed safely.

## Discovery interview
Run discovery for underspecified `create` or `improve` requests.
- Use `request_user_input` for 1-3 short prompts when it fits the round.
- If unavailable, ask 1-3 numbered chat questions and then continue.
- Ask one round at a time and wait before moving forward.
- Start each round with one plain-language question and briefly state why.
- Skip already-answered rounds.
- Stop when confidence is high enough to build safely.
- Before implementation, summarize:
  - confirmed facts
  - assumptions
  - approval checkpoint
- Use `references/discovery-interview.md` for reusable round templates.

## Deliverables
Produce only what the request needs, usually:
- `SKILL.md`
- optional `scripts/`, `references/`, `assets/`, `workflows/`
- `agents/openai.yaml` when UI/tool metadata is needed
- `references/contract.yaml` and `references/evals.yaml` for non-trivial skills
- validator and analyzer evidence
- packaged `.skill` when requested
- concise blocker summary if quality gates cannot be met in-turn

## Response format
For non-trivial responses, start exactly with `## Scope and triggers`, `## Required inputs`, `## Deliverables`, `## Failure mode`.
## Scope and triggers
- confirm when the skill applies.
## Required inputs
- list missing inputs or state what is already known.
## Deliverables
- list files, checks, and artifacts to produce.
## Failure mode
- if out of scope, say why and offer the nearest next step.

### Deterministic response details
Keep first response compact and install-focused:
- include deconflict-first ordering;
- include capability overlap matrix;
- include artifact-uplift scan plan before any write decision.

## Philosophy
- Build minimal, reversible skill updates first; avoid broad rewrites.
- Favor deterministic behavior and explicit guardrails over heuristics in critical paths.
- Always preserve existing contracts unless a change is necessary and validated.
- Offer an alternative strategy or fallback when assumptions are uncertain.
- Provide one backup plan when inputs or provenance are unclear.
- Vary the workflow by request context: use `strict` for risky scope, `minimal` for low-risk alignment, and `rollback-safe` when inputs are ambiguous.

## Anti-patterns
- Treat this skill as a workflow-quality agent, not a generic coding bug-fix helper.
- Avoid adding extra dependencies or benchmark tooling when a simpler check already resolves the issue.

## Examples
- When the user asks, "Can you improve this skill in `utilities/skill-creator` to add safer install checks for upstream artifacts?", run improve mode with deconflict-first mode and artifact checks before touching files.
- A release engineer asked, "I added a new benchmark in `utilities/skill-builder/references/evals.yaml` that keeps failing due to synthetic-looking prompts; can you audit and rewrite eval prompts so they read like real user requests?", then run required eval/security gates after updating `references/evals.yaml`.
- Product asks, "Please package `utilities/diagram-cli` from this PR with an immutable source ref and run `python3 utilities/skill-builder/scripts/quick_validate.py`, then report only the required validation outcomes."

## Output contract
For non-trivial `create`, `improve`, `eval`, or `benchmark-lite`, include:
- `schema_version`
- `mode`
- `skill_path`
- `findings`
- `validations`
- `security`
- `next_step`

## Skill creation process
Skip steps only with an explicit reason.

### 0) Confirm target and boundary
- confirm skill path and artifact boundary;
- enforce folder/name regex:
  - `^[a-z0-9](?:-?[a-z0-9]){0,63}$`
- enforce path confinement:
  - disallow absolute paths and `..` escapes by default;
  - allow `USER` scope only after explicit confirmation and destination allowlist check.
- mine thread context before asking the user to restate details.

### 1) Lock triggers early
- encode use-when, dont-use-when, outputs, and success criteria in `description`;
- create trigger coverage early in `references/evals.yaml`;
- minimum trigger coverage:
  - at least 4 should-trigger prompts
  - at least 4 should-not-trigger prompts
  - include paraphrases and near-neighbor collision prompts.

### 2) Choose structure
- single-file for one intent and one workflow;
- router-style for multi-intent or multi-contract skills.

Router layout:
```text
skill-name/
  SKILL.md
  workflows/
  references/
  scripts/
  assets/
  agents/openai.yaml
```

### 3) Scaffold
```bash
python3 utilities/skill-builder/scripts/init_skill.py <skill-name> --target codex --run-type instruction --category <category>
```

### 4) Author SKILL.md
- keep frontmatter parser-safe (no `<` or `>` in frontmatter fields);
- for this repository, include `metadata.skill-type` using one canonical value;
- keep route-critical guidance in `SKILL.md`;
- link deep context from `references/`.

### 5) Add resources only when they earn their keep
- `references/` for contracts, evals, deep docs
- `scripts/` for deterministic helpers
- `assets/` for templates/fixtures
- `agents/openai.yaml` for Codex UI metadata when needed

### 6) Validate and iterate
- fix first failing gate, then rerun;
- compare variants only when needed;
- package only after gates pass (use your repo-approved packaging helper).

## Execution guardrails
- Cap iterative fix loops at 3 rounds per failing gate.
- After loop cap, publish blocker report (`root_cause`, `attempts`, `next_options`) and wait for user decision.
- Avoid repeating the same unchanged command more than twice.
- Prefer deterministic scripts over repeated free-form retries.
- Keep reruns scoped while iterating; run broader checks before completion claims.

## Validation
Use two explicit phases.
Fail fast: fix the first failed gate before moving to later gates.

Phase A (`iterative_fail_fast`):
- run the first failing gate, fix, rerun until that gate passes.

Phase B (`pre-claim_full_sweep`):
- run all gold gates and required evals in one sweep before claiming completion.

Core validators (gold gates):
```bash
python3 utilities/skill-builder/scripts/quick_validate.py <path/to/skill-folder>
python3 utilities/skill-builder/scripts/skill_gate.py <path/to/skill-folder> --require-fail-fast --require-security-evals --pi-high-fail
python3 utilities/skill-builder/scripts/analyze_skill.py <path/to/skill-folder>
python3 utilities/skill-builder/scripts/openclaw_skill_guard.py <path/to/skill-folder> --mode both
```

Required eval runs:
```bash
python3 utilities/skill-builder/scripts/run_skill_evals.py <path/to/skill-folder>
```
Run required evals for:
- new skills (`create`), changed skills in `improve`/`upgrade`, and `install-distribute` writes (`install`, `update`, `deconflict`).

Reliability checks (required for `eval`, `benchmark-lite`, and install writes):
```bash
python3 utilities/skill-builder/scripts/run_skill_evals.py <path/to/skill-folder> --dual-run --capture-jsonl
python3 utilities/skill-builder/scripts/deterministic_trace_checks.py <path/to/codex-run.jsonl> --budgets-json '{"max_total_tokens":4000,"max_duplicate_command_ratio":0.35}'
```

Unified conformance rules:
- always run gold gates (`quick_validate`, `skill_gate`, `analyze_skill`, `openclaw_skill_guard`);
- for imported packages with upstream eval metadata, run upstream-grade checks and report both;
- Always run gold gates even when upstream checks pass;
- PI/security warnings are release-blocking in every mode.

## Constraints and safety
- Redact secrets, credentials, tokens, and PII by default.
- Default to offline behavior; gate network access with explicit allowlists.
- Keep destructive actions behind dry-run or explicit confirmation.
- Avoid inventing external facts; add verification when uncertain.
- For schema-bound outputs, include `schema_version`.
- `schema_version` policy:
  - major bump = breaking contract change;
  - minor bump = additive, backward-compatible fields;
  - unknown major versions must fail validation.

## Install-distribute mode
Required inputs:
- source (`name`, repo URL, or path), pinned source ref (`commit SHA` preferred), source hash (`sha256`), source trust (`allowlisted`)
- destination scope (`REPO` or `USER`) and destination path/category (`REPO` defaults to repo-local skill paths)
- overwrite consent
- operation type (`list`, `dry-run`, `install`, `update`, `deconflict`)

Operating rules:
- run deconflict-first before any write:
  - capability overlap matrix (`incoming` vs installed operational skills)
  - artifact-uplift scan (`references/`, `assets/`, `agents/`)
  - explicit decision (`merge|fold|improve-existing|install-new`)
- apply provenance gate before any install/update write:
  - verify allowlisted source, pinned source ref, and staged payload `sha256`
- stage in quarantine path, validate there, then perform atomic move/swap
- on any write failure, execute rollback and report restored paths
- preserve imported upstream eval contracts (`eval.yaml`, graders, rubric bundles)
- run validators on all touched skills with strict PI/security flags
- handoff:
  - plugin conversion/publishing -> `codex-plugin-builder`
  - session-scan coverage -> `codex-sessions-skill-scan`
