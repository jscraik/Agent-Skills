---
name: skill-builder
description: "Create, revise, benchmark, and quality-gate Codex skills (SKILL.md plus scripts, references, evals, and packaging). Use this skill when the user asks to build, audit, improve, compare, package, or safely install local/imported skill folders. Scope exclusions: unrelated app features, generic bug fixing, plugin package conversion, or session-log audits."
metadata:
  skill-type: code_quality_review
---

# Skill Builder
Design, improve, validate, and package high-quality Codex skills.
## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Category confirmation](#category-confirmation)
- [OpenAI skill format and progressive disclosure](#openai-skill-format-and-progressive-disclosure)
- [Semantic tag governance](#semantic-tag-governance)
- [Compact governance contract](#compact-governance-contract)
- [Modes](#modes)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Gotchas](#gotchas)
- [Response format](#response-format)
- [Philosophy](#philosophy)
- [Examples](#examples)
- [Output contract](#output-contract)
- [Skill creation process](#skill-creation-process)
- [Execution guardrails](#execution-guardrails)
- [Validation](#validation)
- [Constraints and safety](#constraints-and-safety)
- [Install-distribute mode](#install-distribute-mode)
- [Antipatterns](#antipatterns)

## Working agreement
- Follow the repo `AGENTS.md`; treat it as a map, not a megadoc.
- Keep the artifact boundary explicit: local Codex CLI -> `./artifacts/`, hosted shell -> `/mnt/data/`.
- Path confinement default: write inside approved repo roots and `./artifacts/`; `USER` scope is an explicit `install-distribute` opt-out with confirmation + allowlist.
- Start with the smallest viable package boundary and 2-3 focused surfaces on first pass.
- Move deep policy into `references/`; move repeatable mechanics into `scripts/`.

## When to use
Use this skill when the user asks to:
- create a new skill;
- improve an existing skill's routing, workflow, safety, or portability;
- audit a skill against validators and evals;
- compare variants with shared evals;
- package a validated skill;
- refine skill-graph contracts tied to recursive workflow operations;
- list, install, update, or deconflict local/imported skill folders (`install-distribute` mode).

Keep this skill out of scope for: unrelated app feature coding; generic bug-fixing outside skill quality; routine non-skill docs edits; plugin conversion (`codex-plugin-builder`); session-scan coverage (`codex-sessions-skill-scan`).

## Category confirmation
For `create` and `improve` mode, confirm the primary category before drafting:

1. Library & API Reference
2. Product Verification
3. Data Fetching & Analysis
4. Business Process & Automation
5. Code Scaffolding & Templates
6. Code Quality & Review
7. CI/CD & Deployment
8. Runbooks
9. Infrastructure Operations

Start with:
- “Based on what you described, this sounds like a [Category X] skill. Does that match your intent, or is it something different?”

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
- in this sandboxed environment, run `bash scripts/sync_skills_sandbox_safe.sh` after semantic-tag changes;
- run full `bash scripts/sync_skills.sh` only when runtime skill paths are writable;
- run `bash scripts/lint_skill_types.sh` and require a clean pass (`Missing: 0`, `Invalid: 0`);
- run `bash scripts/lint_openai_skill_format.sh --mode strict` and require a clean pass;
- run `bash scripts/lint_progressive_disclosure.sh --mode warn` and remediate warnings over time;
- run `python3 scripts/gotcha_pipeline.py validate` to ensure candidate-governance artifacts stay contract-safe;
- treat `[WARN] Unrecognized metadata.skill-type ...` output as a governance failure to be fixed before claiming completion;
- confirm `docs/skills-by-type.md` regenerated successfully when tags change.

## Compact governance contract
Use this contract for `create` and `improve` mode in this repository.

Source of truth:
- `references/governance-contract.md`

Required gates before completion claim:
- `bash scripts/lint_openai_skill_format.sh --mode strict`
- `bash scripts/lint_progressive_disclosure.sh --mode warn`
- `python3 scripts/gotcha_pipeline.py validate`
- `bash scripts/sync_skills_sandbox_safe.sh` and `bash scripts/lint_skill_types.sh` when semantic tags changed in this environment
- full `bash scripts/sync_skills.sh` when runtime skill paths are writable

Core policies:
- use `Do X because Y` style in `SKILL.md` procedure sections;
- keep `description` routing-first (`what + when`), never a checklist;
- progressive-disclosure triggers must live in `references/` (`Read when: <condition>`);
- `__all__` only when module-style scripts are intended for import reuse; not required for CLI entrypoints.

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
- 2-3 concrete use cases, plus 8-10 should-trigger and 8-10 should-not-trigger queries;
- target environment: `codex`, `claude`, or `portable`;
- required tools, schemas, templates, and policy constraints;
- compatibility posture (`learn`, `guided`, `execute`);
- category confirmation (for create/improve) with rationale for any category tradeoff.

If critical inputs are missing, ask only the minimum needed to proceed safely.
- When inputs are missing, phrase each critical item as a direct question ending in `?`; do not only list field names or placeholders.

## Discovery interview
Run discovery for underspecified `create` or `improve` requests.
- Use `request_user_input` for 1-3 short prompts when it fits the round.
- If unavailable, ask 1-3 numbered chat questions and then continue.
- Ask one round at a time and wait before moving forward.
- Start each round with one plain-language question and explain why the round matters with a short `Why this matters:` line.
- Avoid dumping the whole interview plan at once; keep the first turn to the current round only.
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

## Examples
- User says: “I want you to improve `utilities/diagram-cli` so it can safely install from PRs and still pass our schema gates.” Run `improve` mode, confirm category, then run required validation and package only after gates pass.
- User says: “This skill keeps failing on imports when we add a new repo path; can you tighten its workflow and add a concrete trigger test plan?” Run `improve` mode, add discovery, then produce 8+ realistic trigger and non-trigger query tests before delivery.
- User says: “Can you take `frontend/tools/agentation`, figure out why the skill feels bloated and undertriggers, rewrite it to current OpenAI skill format, and show me the exact gates you ran before we ship it?” Run `improve` mode, confirm category, tighten `description`, split heavy guidance into `references/`, and report validator outcomes with the final diff.

## Gotchas
- Missing required headings -> nested/alias headings used -> promote to exact top-level `##` names -> rerun `bash scripts/lint_progressive_disclosure.sh --mode warn`.
- `sync_skills` timeout with `Operation not permitted` -> runtime paths are read-only in sandbox -> run `bash scripts/sync_skills_sandbox_safe.sh`.
- Stale type index after tag edits -> semantic sync skipped -> run sandbox-safe sync, then `bash scripts/lint_skill_types.sh`.

## Response format
For non-trivial first responses in `create`, `improve`, `eval`, or `benchmark-lite`, start with these exact top-level headings in this order:
- `## Scope and triggers`
- `## Required inputs`
- `## Deliverables`
- `## Failure mode`
- `## Examples`

Heading contract:
- use the exact heading text above; do not substitute aliases such as `## When to use`;
- keep each section short if the user asked for a concise first response, but still include the heading;
- under `## Scope and triggers`, briefly confirm whether this skill applies, the likely category, and the boundary of the work;
- under `## Required inputs`, ask the minimum missing items as direct questions with `?`;
- under `## Failure mode`, say what happens if the request is out of scope or critical inputs remain missing.
### Deterministic response details
Keep first response compact and install-focused:
- include deconflict-first ordering;
- include capability overlap matrix;
- include artifact-uplift scan plan before any write decision.

## Philosophy
- Build minimal, reversible updates first; prefer deterministic guardrails.
- Apply controlled variation in output depth, phrasing, and check ordering based on user context (team, risk, or scope), while preserving safety guarantees.
- Keep the user unblocked: when inputs are incomplete but risk is low, make the safest reasonable assumption, state it, and keep momentum.

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

Use the compact flow below, then follow the linked references for full detail.

1. Confirm target boundary and enforce scoped writes.
   - Keep names path-safe (`^[a-z0-9](?:-?[a-z0-9]){0,63}$`).
   - Default to repo scope; require explicit allowlist confirmation for `USER` scope.
2. Confirm category and missing inputs in one round.
3. Set trigger logic first (`description`) and add 8+/8+ trigger coverage in `references/evals.yaml`.
4. Scaffold and draft with minimal structure, moving deep policy to `references/` and deterministic mechanics to `scripts/`.
5. When recursive run evidence exists, consume `lesson_observations.json`, `lesson_candidates.json`, and `promotion_decision.json` and promote only repeated, rubric-bound lessons.
6. Iterate gate-by-gate: fix one failure, rerun, then continue.
7. Run description optimization before handoff and deliver only when gates are clear or triaged.

Reference files:
- `references/governance-contract.md`
- `references/quality-tools.md`
- `references/workflows-and-validation.md`
- `references/iteration-and-testing.md`
- `references/discovery-interview.md`

## Execution guardrails
- Cap iterative fix loops at 3 rounds per failing gate, then publish a blocker report and wait for user direction.
- Avoid repeating unchanged commands more than twice; prefer deterministic scripts.
- Keep reruns scoped during iteration; run broader checks before completion claims.

## Validation
- Fail-fast is mandatory: stop at first failing gate, fix, rerun, then continue.
- Use two passes: `iterative_fail_fast` then `pre-claim_full_sweep`.
- Use `references/quality-tools.md` for gate command matrix and strict PI/security expectations.
- During iteration prefer `run_skill_evals.py --eval-mode smoke`; before promotion or packaging run `--eval-mode release` and keep the generated `release_manifest.json` with the scorecard artifacts.

## Constraints and safety
- Redact secrets, credentials, tokens, and PII by default.
- Keep destructive actions behind dry-run or explicit confirmation.
- Include `schema_version` for schema-bound outputs and follow versioning policy in `references/governance-contract.md`.
- Default to offline execution; allow network only with explicit permission and allowlist in scope.

## Install-distribute mode
- Confirm provenance (`allowlist` + pinned ref + staged `sha256`) before writes.
- Run deconflict-first (`overlap matrix` + `artifact-uplift scan` + explicit decision).
- Validate in quarantine before atomic move/swap; rollback on write failure.
- Hand off plugin conversion to `codex-plugin-builder` and session coverage scans to `codex-sessions-skill-scan`.
- Use `references/advanced-workflow.md` for full install-distribute mechanics and checklists.

## Failure mode
- If out of scope, say why and offer the nearest next skill-appropriate next step.

## Anti-patterns
- Overfitted routing language -> description only matches one phrasing -> expand to realistic paraphrases and near-neighbor cases, then recheck `references/evals.yaml`.
- Checklist dump in frontmatter -> `description` becomes procedure-heavy and undertriggers -> move process detail to `SKILL.md` or `references/` and keep frontmatter routing-first.
