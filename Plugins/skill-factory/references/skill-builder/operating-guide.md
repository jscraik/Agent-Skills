# Skill Builder Operating Guide

Use this reference when the skill-builder work is non-trivial, touches release readiness, or requires preserving detailed governance while keeping `SKILL.md` small.

## Working Agreement

- Follow the repo `AGENTS.md`; treat it as a routing map.
- Keep artifact boundaries explicit: local Codex CLI writes to `./Infrastructure/artifacts/`; hosted shell writes to `/mnt/data/`.
- Path confinement default: write inside approved repo roots and `./Infrastructure/artifacts/`.
- `USER` scope is an explicit `install-distribute` opt-out that requires confirmation and an allowlist.
- Start with the smallest viable package boundary and 2-3 focused surfaces on the first pass.
- Move deep policy into `references/`; move repeatable mechanics into `scripts/`.
- Preserve valuable context by relocating it with explicit signposting, not by deleting or flattening nuanced guidance.
- Treat graph-readiness as source quality: add `## See Also`, topic-map signposts, and `references/task-profile.json` for operational graph skills.

## Boundary Triage

Use `skill-creator` for first-draft creation or large reshaping from nothing.
Use `skill-builder` for hardening and readiness gates.
Use `skill-installer` for acquisition, install, and runtime visibility after the skill is valid.
Use `plugin-builder` for plugin conversion.
Use `skill-refactor` for session-scan coverage and keep/merge/prune/retire analysis.

## Iteration Round Contract

For non-trivial lifecycle work:

1. Prepare realistic prompts from the creator handoff package.
2. Freeze comparison inputs for candidate and baseline parity.
3. Select baseline type: `no_skill`, `prior_skill_snapshot`, or explicitly approved `neutral_repo_baseline`.
4. Run candidate and baseline in the same round window.
5. Capture quantitative evidence, qualitative evidence, and metric-availability status.
6. Assess route and description quality every round; edit only when evidence shows weakness or ambiguity.
7. Record the round decision: `iterate_again`, `widen_eval_set`, `ready_for_install_handoff`, `ready_for_plugin_handoff`, or `stop_blocked`.

Round state values: `prepared`, `running`, `evidence_captured`, `reviewed`, `decision_recorded`, `blocked`.

## Evidence Ownership

Use an additive artifact model:

- `result.json`: per-case comparison details, round-state fields, metric availability, and optional qualitative review path.
- `summary.json`: run-level readiness rollup and blocked-state visibility.
- `scorecard.json`: CI-facing pass/fail surface.
- `release_manifest.json`: release-facing snapshot that points to richer artifacts.
- `comparison_review.md`: optional run-scoped qualitative review.

Keep readiness states distinct: `starter_valid`, `comparison_incomplete`, `comparison_blocked`, `downstream_ready`.
`skill-installer` and `plugin-builder` are downstream-only; hand off only when contract evidence exists and lifecycle judgment is complete.

## Category Confirmation

For create/improve-style reshaping, confirm the primary category before drafting:

- Library & API Reference
- Product Verification
- Data Fetching & Analysis
- Team Automation
- Code Scaffolding & Templates
- Code Quality & Review
- CI/CD & Deployment
- Runbooks
- Infrastructure Operations

Start with: "Based on what you described, this sounds like a [Category X] skill. Does that match your intent, or is it something different?"

## OpenAI Format and Progressive Disclosure

- Frontmatter uses official keys: `name`, `description`, and optional repo `metadata`.
- Keep optional runtime metadata in `agents/openai.yaml`.
- Use `metadata.skill-type` for semantic indexing and governance checks.
- Keep `description` as routing logic, not a procedure dump.
- Keep `SKILL.md` as the map: boundaries, required inputs, output contract, and safety guardrails.
- Move long examples, compatibility matrices, and operational runbooks to `references/`.
- Add explicit read-when signposts for relocated context.
- Keep deterministic helpers in `scripts/`.
- For non-trivial responses, include machine-checkable output contracts with `schema_version`.

## Semantic Tag Governance

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

For create mode, set `metadata.skill-type` on every new skill.
For improve mode, preserve existing `metadata.skill-type` unless there is an explicit reason to retag.
If no canonical value fits, choose the closest fit and explain the tradeoff in the change summary.
Add new semantic-type values only with explicit user approval.

After semantic-tag changes, run sandbox-safe sync or full sync, then require clean skill-type, OpenAI-format, progressive-disclosure, and gotcha-pipeline validation.

## Governance Gates

Before completion claims for create/improve mode, run the applicable gates:

- `bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh --mode strict`
- `bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode warn`
- `python3 Infrastructure/scripts/lifecycle-and-sync/gotcha_pipeline.py validate`
- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh`
- `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh`
- full `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh` when runtime paths are writable

Use "Do X because Y" style in procedure sections.
Progressive disclosure means signposted relocation, not information loss.
Use `__all__` only when module-style scripts are intended for import reuse.

## Discovery Interview

Run discovery for underspecified create/improve requests:

- Use `request_user_input` for 1-3 short prompts when it fits the round.
- Ask one plain-language question at a time and explain why it matters.
- Skip already-answered rounds.
- Stop when confidence is high enough to build safely.
- Before implementation, summarize confirmed facts, assumptions, and the approval checkpoint.

## Agent Injection

When skill-linked subagent support is requested:

1. Check `/Users/jamiecraik/dev/configs/codex/agents/` first.
2. Treat `.codex/agents/` as compatibility projection, not the default write target.
3. If no role fits, hand off role creation to `codex-agent-creator`.
4. Validate candidate role files with `bash Skills/codex-agent-creator/Infrastructure/scripts/validate_role.sh --agent-name <name> --agent-file <path>`.
5. Install/update only when requested with `install_role.sh`.
6. Record route as `reuse-existing` or `create-purpose-built`.

## Deterministic First Response

For non-trivial first responses in `create`, `improve`, `eval`, or `benchmark-lite`, use these headings:

- `## Scope and triggers`
- `## Required inputs`
- `## Deliverables`
- `## Failure mode`
- `## Examples`

Keep the first response compact and install-focused. Include deconflict-first ordering, capability overlap matrix when relevant, and artifact-uplift scan plan before write decisions.
For ambiguous packaging, explicitly ask whether the output should stay a standalone skill or become a plugin.

## Skill Creation Process

1. Confirm target boundary and scoped writes.
2. Confirm category and missing inputs in one round.
3. Set trigger logic first and add trigger/non-trigger coverage in `references/evals.yaml`.
4. Scaffold with minimal structure, moving deep policy to `references/` and deterministic mechanics to `scripts/`.
5. For repo skills, wire graph navigation with `## See Also`, topic maps, and task profiles.
6. If recursive evidence exists, consume lesson artifacts and promote only repeated, rubric-bound lessons.
7. Iterate gate-by-gate.
8. Run description optimization before handoff.

Path-safe names should be short lowercase slugs with optional single hyphens; avoid regex-heavy prose in `SKILL.md` because markdown link parsers can misread it.

## Gotchas

- Missing required headings: promote aliases to exact top-level headings and rerun progressive-disclosure lint.
- Runtime sync timeout or permission error: use sandbox-safe sync, then note runtime paths were not writable.
- Stale type index after tag edits: run sandbox-safe sync, then `lint_skill_types.sh`.
- Valuable context disappeared during cleanup: restore it to `references/` and add direct signposts from `SKILL.md`.
