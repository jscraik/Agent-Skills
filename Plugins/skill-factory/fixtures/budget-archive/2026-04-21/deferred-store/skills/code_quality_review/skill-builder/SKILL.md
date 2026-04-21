---
name: skill-builder
description: Analyze and harden Codex skills and plugin packages for contract quality, eval coverage, and safety compliance. Use this skill when an existing package is approaching release and needs evidence-backed validation.
metadata:
  skill-type: code_quality_review
  lifecycle_state: active
  maturity: canonical
  owner: Agent Skills Team
  review_cadence: quarterly
  last_reviewed: 2026-04-12
  metadata_source: frontmatter
---

# Skill Builder
Design, improve, validate, and package high-quality Codex skills.
## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Iteration Round Contract](#iteration-round-contract)
- [Evidence Ownership and Readiness](#evidence-ownership-and-readiness)
- [Category confirmation](#category-confirmation)
- [OpenAI skill format and progressive disclosure](#openai-skill-format-and-progressive-disclosure)
- [Semantic tag governance](#semantic-tag-governance)
- [Compact governance contract](#compact-governance-contract)
- [Modes](#modes)
- [Required inputs](#required-inputs)
- [Agent injection](#agent-injection)
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
- Keep the artifact boundary explicit: local Codex CLI -> `./Infrastructure/artifacts/`, hosted shell -> `/mnt/data/`.
- Path confinement default: write inside approved repo roots and `./Infrastructure/artifacts/`; `USER` scope is an explicit `install-distribute` opt-out with confirmation + allowlist.
- Start with the smallest viable package boundary and 2-3 focused surfaces on first pass.
- Move deep policy into `Infrastructure/references/`; move repeatable mechanics into `Infrastructure/scripts/`.
- Preserve valuable context by relocating it with explicit signposting, not by deleting or flattening nuanced guidance just to make `SKILL.md` shorter.
- Do not remove important context for budget trimming; move it to `Infrastructure/references/` and add explicit `Read when` signposts in `SKILL.md`.
- Treat graph-readiness as source quality, not cleanup work after the fact:
  - add a `## See Also` table with at least 2 real related skills,
  - include a topic-map signpost such as `**Topic map:** [[agent-ops]]` when the skill belongs in the graph,
  - create or preserve `Infrastructure/references/task-profile.json` for in-scope operational skills.

## When to use
Use this skill when the user asks to:
- improve an existing skill's routing, workflow, safety, portability, or eval posture;
- audit a skill against validators and evals;
- compare variants or fold overlapping skill approaches into one governed surface;
- package a validated standalone skill;
- refine skill-graph contracts tied to recursive workflow operations;
- prepare a contract-valid skill for install/distribute handoff or finish bounded distribution work when lifecycle judgment is already settled.

Keep this skill out of scope for: first-draft skill scaffolding (`skill-creator`); pure install/import or runtime-visibility work once the skill is already valid (`skill-installer`); unrelated app feature coding; generic bug-fixing outside skill quality; routine non-skill docs edits; plugin conversion (`plugin-builder`); session-scan coverage (`skill-refactor`).
Boundary triage for ambiguous requests: use `skill-creator` for create/reshape work, `skill-builder` for hardening and readiness gates, and `skill-installer` for acquisition/install/runtime-visibility tasks.

## Iteration Round Contract
For non-trivial lifecycle work, use one explicit round model:
1. Prepare realistic prompts from the creator handoff package.
2. Freeze comparison inputs for candidate and baseline parity.
3. Select baseline type:
   - `no_skill` for new skills by default
   - `prior_skill_snapshot` for existing skills
   - `neutral_repo_baseline` only when planning explicitly approved it
4. Run candidate and baseline in the same round window.
5. Capture evidence (quantitative, qualitative, and metric-availability status).
6. Assess route and description quality every round; edit only when evidence shows weakness or ambiguity.
7. Record round decision (`iterate_again`, `widen_eval_set`, `ready_for_install_handoff`, `ready_for_plugin_handoff`, or `stop_blocked`).
Round state must remain explicit in artifacts: `prepared`, `running`, `evidence_captured`, `reviewed`, `decision_recorded`, `blocked`.

## Evidence Ownership and Readiness
Use one additive artifact model:
- `result.json`: per-case comparison details, round-state fields, metric availability, and optional qualitative review path.
- `summary.json`: run-level readiness rollup and blocked-state visibility.
- `scorecard.json`: CI-facing pass/fail surface; additive metadata only.
- `release_manifest.json`: thin release-facing snapshot that points to richer artifacts.
- `comparison_review.md` (optional, run-scoped): qualitative review notes when JSON alone is not enough.
Readiness states must stay distinct: `starter_valid`, `comparison_incomplete`, `comparison_blocked`, `downstream_ready`.
Downstream handoff guardrail: `skill-installer` and `plugin-builder` are downstream-only. Hand off only when `ContractValidityEvidence` exists and lifecycle judgment is complete.

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
  - optional: `metadata` in `SKILL.md` frontmatter when repo governance needs classification tags
- keep optional runtime metadata in `agents/openai.yaml` (for interface details, invocation policy, and tool dependencies) instead of overloading frontmatter
- for this repository, use `metadata.skill-type` to classify skills for semantic indexing and governance checks
- keep `description` as routing logic (what + when), not a procedure dump;
- keep `SKILL.md` as the map:
  - route-critical boundaries, required inputs, output contract, and safety guardrails stay in `SKILL.md`
  - long examples, compatibility matrices, and operational runbooks move to `Infrastructure/references/`
  - when relocating material, preserve high-value nuance, caveats, and doctrine in `Infrastructure/references/` instead of summarizing them away
  - add explicit signposts so `SKILL.md` tells the reader which reference to open and when
  - deterministic helpers stay in `Infrastructure/scripts/`
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
- in this sandboxed environment, run `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh` after semantic-tag changes;
- run full `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` only when runtime skill paths are writable;
- run `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh` and require a clean pass (`Missing: 0`, `Invalid: 0`);
- run `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict` and require a clean pass;
- run `bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn` and remediate warnings over time;
- run `python3 Infrastructure/scripts/lifecycle-and-sync/gotcha_pipeline.py validate` to ensure candidate-governance artifacts stay contract-safe;
- treat `[WARN] Unrecognized metadata.skill-type ...` output as a governance failure to be fixed before claiming completion;
- confirm `docs/skills-by-type.md` regenerated successfully when tags change.

## Compact governance contract
Use this contract for `create` and `improve` mode in this repository.

Source of truth:
- [Infrastructure/references/governance-contract.md](./references/governance-contract.md)

Required gates before completion claim:
- `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict`
- `bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn`
- `python3 Infrastructure/scripts/lifecycle-and-sync/gotcha_pipeline.py validate`
- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh` and `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh` when semantic tags changed in this environment
- full `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` when runtime skill paths are writable

Core policies:
- use `Do X because Y` style in `SKILL.md` procedure sections;
- keep `description` routing-first (`what + when`), never a checklist;
- progressive-disclosure triggers must live in `Infrastructure/references/` (`Read when: <condition>`);
- progressive disclosure means signposted relocation, not information loss; if detail matters for correct behavior, preserve it in `Infrastructure/references/` and route to it explicitly;
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

## Agent injection
When the request includes skill-linked subagent support, wire it explicitly during `create`, `improve`, or `install-distribute`:

1. Reuse-first discovery: check `/Users/jamiecraik/dev/configs/codex/agents/` first; treat `.codex/agents/` as a compatibility projection, not the default write target.
2. If no suitable role exists, hand off role creation to [[codex-agent-creator]] and request a purpose-built agent with explicit `model`, `model_reasoning_effort`, and canonical global targets.
3. Validate candidate role files: `bash Skills/codex-agent-creator/Infrastructure/scripts/validate_role.sh --agent-name <name> --agent-file <path>`.
4. Install/update role files only when requested: `bash Skills/codex-agent-creator/Infrastructure/scripts/install_role.sh --agent-name <name> --agent-file <path> --scope global --canonical-root ~/dev/configs/codex --config ~/dev/configs/codex/config.toml [--update-existing]`.
5. Record route as `reuse-existing` or `create-purpose-built` in the handoff summary.

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
- Use `Infrastructure/references/discovery-interview.md` for reusable round templates.

## Deliverables
Produce only what the request needs, usually:
- `SKILL.md`
- optional `Infrastructure/scripts/`, `Infrastructure/references/`, `assets/`, `workflows/`
- `agents/openai.yaml` when UI/tool metadata is needed
- `Infrastructure/references/contract.yaml` and `Infrastructure/references/evals.yaml` for non-trivial skills
- `## See Also` plus a topic-map signpost for graph-visible skills in this repository
- `Infrastructure/references/task-profile.json` for active/in-scope skills that participate in the recursive skill graph
- preserved reference context with clear signposts when content is being condensed or imported from a richer source
- validator and analyzer evidence
- packaged `.skill` when requested
- concise blocker summary if quality gates cannot be met in-turn

## Examples
- User says: “I want you to improve `Skills/diagram-cli` so it can safely install from PRs and still pass our schema gates.” Run `improve` mode, confirm category, then run required validation and package only after gates pass.
- User says: “This skill keeps failing on imports when we add a new repo path; can you tighten its workflow and add a concrete trigger test plan?” Run `improve` mode, add discovery, then produce 8+ realistic trigger and non-trigger query tests before delivery.
- User says: “Can you take `frontend/tools/agentation`, figure out why the skill feels bloated and undertriggers, rewrite it to current OpenAI skill format, and show me the exact gates you ran before we ship it?” Run `improve` mode, confirm category, tighten `description`, split heavy guidance into `Infrastructure/references/`, and report validator outcomes with the final diff.

## Gotchas
- Missing required headings -> nested/alias headings used -> promote to exact top-level `##` names -> rerun `bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn`.
- `sync_skills` timeout with `Operation not permitted` -> runtime paths are read-only in sandbox -> run `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh`.
- Stale type index after tag edits -> semantic sync skipped -> run sandbox-safe sync, then `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh`.
- Valuable source context disappears during cleanup -> progressive disclosure was treated as compression -> restore the nuance into `Infrastructure/references/` and add direct signposts from `SKILL.md`.

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
- when a packaging request leaves the standalone-skill vs plugin boundary undecided, treat that as route clarification, say so explicitly under `## Scope and triggers`, and ask one direct deliverable-boundary question under `## Required inputs` such as `Should this stay a standalone skill, or do you want the output packaged as a plugin?`
### Deterministic response details
Keep first response compact and install-focused:
- include deconflict-first ordering;
- include capability overlap matrix;
- include artifact-uplift scan plan before any write decision.
- for ambiguous packaging requests, include the word `clarification` or `route clarification` plus both deliverable terms `standalone skill` and `plugin` in the first response.

## Philosophy
- Build minimal, reversible updates first; prefer deterministic guardrails.
- Apply controlled variation in output depth, phrasing, and check ordering based on user context (team, risk, or scope), while preserving safety guarantees.
- Keep the user unblocked: when inputs are incomplete but risk is low, make the safest reasonable assumption, state it, and keep momentum.

## Output contract
For non-trivial `create`, `improve`, `eval`, or `benchmark-lite`, include:
- `schema_version`
- `mode`
- `skill_path`
- `context_routes` as `[{from, to, read_when}]` whenever required detail moved from `SKILL.md` to `Infrastructure/references/`
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
3. Set trigger logic first (`description`) and add 8+/8+ trigger coverage in `Infrastructure/references/evals.yaml`.
4. Scaffold and draft with minimal structure, moving deep policy to `Infrastructure/references/` and deterministic mechanics to `Infrastructure/scripts/`.
   - When slimming `SKILL.md`, preserve high-impact context in `Infrastructure/references/` and add explicit read-when signposts instead of collapsing the source material into a weaker summary.
   - For repo skills, wire graph navigation while drafting:
     - add `## See Also` with 2+ real related skills,
     - add a topic-map signpost,
     - create or preserve `Infrastructure/references/task-profile.json` when the skill is in the operational graph.
5. When recursive run evidence exists, consume `lesson_observations.json`, `lesson_candidates.json`, and `promotion_decision.json` and promote only repeated, rubric-bound lessons.
6. Iterate gate-by-gate: fix one failure, rerun, then continue.
7. Run description optimization before handoff and deliver only when gates are clear or triaged.

Reference files:
- `Infrastructure/references/governance-contract.md`
- `Infrastructure/references/quality-tools.md`
- `Infrastructure/references/workflows-and-validation.md`
- `Infrastructure/references/iteration-and-testing.md`
- `Infrastructure/references/discovery-interview.md`

## Execution guardrails
- Cap iterative fix loops at 3 rounds per failing gate, then publish a blocker report and wait for user direction.
- Avoid repeating unchanged commands more than twice; prefer deterministic scripts.
- Keep reruns scoped during iteration; run broader checks before completion claims.

## Validation
- Fail-fast is mandatory: stop at first failing gate, fix, rerun, then continue.
- Use two passes: `iterative_fail_fast` then `pre-claim_full_sweep`.
- Use `Infrastructure/references/quality-tools.md` for gate command matrix and strict PI/security expectations.
- During iteration prefer `run_skill_evals.py --eval-mode smoke`; before promotion or packaging run `--eval-mode release` and keep the generated `release_manifest.json` with the scorecard artifacts.
- Treat graph-readiness as part of the default repo gate set for `create` and `improve` work:
  - `python3 Infrastructure/scripts/validation-and-linting/check-see-also.py . --changed-files <skill>/SKILL.md`
  - `python3 Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py --repo-root . --expected-count 0`
- When graph-facing skills changed materially, refresh adjacency evidence:
  - `python3 Infrastructure/scripts/skill-graph/build-adjacency-yaml.py`
  - `python3 Infrastructure/scripts/skill-graph/validate-adjacency.py`

## Constraints and safety
- Redact secrets, credentials, tokens, and PII by default.
- Keep destructive actions behind dry-run or explicit confirmation.
- Include `schema_version` for schema-bound outputs and follow versioning policy in `Infrastructure/references/governance-contract.md`.
- Default to offline execution; allow network only with explicit permission and allowlist in scope.

## Install-distribute mode
- Confirm provenance (`allowlist` + pinned ref + staged `sha256`) before writes.
- Run deconflict-first (`overlap matrix` + `artifact-uplift scan` + explicit decision).
- Preserve relevant upstream context when importing: keep high-value references, examples, and caveat docs unless they are clearly redundant or out of scope, and signpost them from the wrapper skill.
- Validate in quarantine before atomic move/swap; rollback on write failure.
- Hand off pure installation or runtime-visibility work on an already-valid skill to `skill-installer`.
- Hand off plugin conversion to `plugin-builder` once the standalone skill is contract-valid and the deliverable boundary becomes a plugin.
- Hand off session coverage scans to `skill-refactor`.
- Use `Infrastructure/references/advanced-workflow.md` for full install-distribute mechanics and checklists.

## See Also

| Skill | When to use |
|---|---|
| [[decide-build-primitive]] | Decide whether the capability should be a skill, prompt, or agent before authoring it |
| [[skill-refactor]] | Audit skill coverage, failures, and overlap using real session evidence instead of authoring doctrine alone |
| [[codex-agent-creator]] | Reuse existing agent TOMLs or create role-specific custom agents for skill-linked delegation flows |

**Topic map:** [[agent-ops]]

## Failure mode
- If out of scope, say why and offer the nearest next skill-appropriate next step.

## Anti-patterns
- Overfitted routing language -> description only matches one phrasing -> expand to realistic paraphrases and near-neighbor cases, then recheck `Infrastructure/references/evals.yaml`.
- Checklist dump in frontmatter -> `description` becomes procedure-heavy and undertriggers -> move process detail to `SKILL.md` or `Infrastructure/references/` and keep frontmatter routing-first.
- Over-compression during cleanup -> valuable context gets deleted to satisfy disclosure rules -> preserve nuance in `Infrastructure/references/` and make `SKILL.md` a stronger signpost instead of a thinner substitute.
