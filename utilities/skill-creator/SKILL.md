---
name: skill-creator
description: "Create, revise, benchmark, and quality-gate Codex skills (SKILL.md + resources + evals + packaging). Use when the user asks to build/audit/improve a skill or skill-graph contract; do not use for unrelated feature coding."
---

# Skill Creator

This skill helps you design, author, validate, and package high-quality skills.

**Version**: 1.8.0
**Last updated**: 2026-02-26

## Table of Contents
- [Working agreement (skills + shell + compaction)](#working-agreement-skills--shell--compaction)
- [Scope and triggers](#scope-and-triggers)
- [Modes (conservative)](#modes-conservative)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Response format (required)](#response-format-required)
- [Operating principles](#operating-principles)
- [Skill creation process (follow by default)](#skill-creation-process-follow-by-default)
- [Script-backed security rules (required)](#script-backed-security-rules-required)
- [What to avoid](#what-to-avoid)
- [Constraints](#constraints)
- [Validation](#validation)
- [Examples](#examples)
- [Skill test strategy by type](#skill-test-strategy-by-type)
- [Reference map (skill-creator internal)](#reference-map-skill-creator-internal)
- [Governance and style appendix](#governance-and-style-appendix)

## Working agreement (skills + shell + compaction)

- Follow the repo's `AGENTS.md` (treat it as a map, not a megadoc).
- For long-running work: also follow `~/.codex/instructions/shell-skills-compaction.md` (or a repo-local copy).
- Use an artifact boundary:
  - Local Codex CLI: write deliverables to `./artifacts/`
  - Hosted shell: write deliverables to `/mnt/data/`
- After major milestones, write a short status note to an artifact (e.g., `./artifacts/STATUS.md`) so the thread can be compacted safely.

## Scope and triggers

Use this skill to:

- Create a new skill (instruction-only, script-backed, or router-style).
- Revise an existing skill for better triggering, portability, or reliability.
- Audit/upgrade a skill to meet “gold standard” structure, progressive disclosure, and validation.
- Improve skill-knowledge graph contracts (schemas/workflows/telemetry) tied to recursive loop operations.
- Package a skill into a distributable `.skill` archive.

## Modes (conservative)

Select the smallest mode that matches user intent:

- **create**: scaffold and author a new skill.
- **improve**: revise an existing skill for routing quality, reliability, or safety.
- **eval**: run quality checks/evals and summarize findings.
- **benchmark-lite**: compare two variants with deterministic checks (`run_skill_evals.py --dual-run`) and report evidence.
- **graph**: improve skill-graph docs/contracts and runtime metadata for learn/promotion loops.
- **package**: produce a `.skill` archive once quality gates pass.

Default to `create`/`improve`; use `benchmark-lite` only when the user asks to compare variants.

## Required inputs

- Desired skill goal (what the user wants to accomplish).
- 3–10 example user prompts:
  - 2–5 happy-path prompts
  - 1–3 edge-cases
  - 1–3 “should NOT trigger” prompts (negative examples)
- Target environment(s): `codex`, `claude`, or `portable` subset.
- Any required assets, schemas, APIs, CLIs, or “house style” constraints.
- Compatibility posture (default: canonical-only for unreleased/greenfield projects; add backwards compatibility only when explicitly required).
- If graph work is requested: target profiles/scopes and desired graph outputs (schema/docs/runtime artifact updates).

If any of the above are missing, ask only the minimum questions required to proceed safely.

## Deliverables

Depending on the request, produce one or more of:

- A skill folder containing:
  - `SKILL.md` (required)
  - `agents/openai.yaml` (recommended for OpenAI/Codex UI + MCP dependencies)
  - `scripts/` (optional)
  - `references/` (optional but recommended for non-trivial skills)
  - `assets/` (optional)
  - `workflows/` (optional for router-style skills)
- `references/contract.yaml` (output contract) and `references/evals.yaml` (eval cases) when the skill is non-trivial.
- For schema-bound outputs, require a top-level `schema_version` in the output contract/artifact examples.
- `references/plan.md` (plan artifact) for non-trivial skill builds; store `$create-plan` output here when available.
- A validation report (what passed/failed and what to fix).
- An `analyze_skill.py` quality report for every validation run.
- An operational-readiness + security-risk report (OpenClaw-style summary: critical/warn/info).
- For graph-mode work: updated `docs/skill-graphs/*` contracts and any coupled runtime artifact/schema updates.
- A packaged `.skill` file (optional).
- Decision-feedback instrumentation in created/updated skills:
  - Include the `decision-feedback-protocol:v2` block in `SKILL.md`.
  - Ensure AskQuestion parity (`request_user_input`) is explicitly required for non-trivial outcomes.
  - Ensure feedback records can be written with `scripts/record_skill_feedback.py` including subject tags.

## Response format (required)

Always start responses with these headings (no text before them):

## Scope and triggers
- 1–3 bullets on when this skill applies (confirm scope).

## Required inputs
- List required inputs and ask targeted questions if needed.

## Deliverables
- List deliverables you will produce.

## Failure mode

If the request is out of scope:
- Use the headings above.
- Under **Required inputs**, explain what’s missing or why it’s out of scope.
- Under **Deliverables**, propose the closest appropriate next step or skill.

## Operating principles

### Humans steer. Agents execute.

Your goal is leverage: translate vague intent into a workflow the agent can execute repeatedly.
When something fails, the fix is almost never “try harder”—it’s usually missing scaffolding, missing constraints, or missing feedback loops.

### Keep SKILL.md short and treat it as a map

Context is scarce. Treat `SKILL.md` as the high-signal “table of contents,” and push depth into:
- `references/` (system of record)
- `scripts/` (deterministic helpers)
- `assets/` (templates/boilerplate)

This matches the “AGENTS.md as table of contents” approach: point to structured sources of truth instead of growing a single blob.

### Descriptions are routing logic

The `description` is effectively the model’s decision boundary. It should be concrete about:
- Use-when vs don’t-use-when
- Outputs/artifacts
- Success criteria

### Default compatibility posture

- For unreleased/greenfield projects, default to canonical implementations and guidance.
- Do not add compatibility shims, adapter layers, migration bridges, or dual-write flows unless explicitly requested or required by an existing released contract.

### Put templates/examples inside the skill

Do not cram templates into system prompts. Put them inside the skill so they load only when needed.

### Design for long runs

Plan for multi-step continuity:
- Reuse the same environment/container when you want stable deps and cached intermediate files.
- Use compaction as a default long-run primitive, not an emergency fallback.

### Treat skills + networking as high-risk

Default posture:
- Skills: allowed
- Shell: allowed
- Network: enabled only when required, behind strict allowlists, and never echo secrets.

### Environment compatibility notes (Codex-first)

- Keep canonical behavior Codex-first unless the user explicitly asks for Claude-specific features.
- Claude-only frontmatter fields (for example `disable-model-invocation`, `argument-hint`, `context: fork`) should be documented as optional compatibility notes, not default guidance.
- Do not assume slash-command semantics in Codex unless explicitly requested.

## Skill creation process (follow by default)

Skip steps only with a clear reason.

### 0) Confirm target + artifact boundary

- Confirm where the skill lives:
  - Repo: `.agents/skills/<skill-name>/`
  - User: `~/.agents/skills/<skill-name>/`
- Confirm artifact boundary (local `./artifacts/` vs hosted `/mnt/data/`).

### 1) Lock down triggers early (with negative examples)

- Collect 3–10 prompts (happy, edge, and negative).
- Ensure the `description` contains:
  - trigger keywords
  - explicit “don’t use when …” near-misses
  - output artifacts and success criteria
- Encode compatibility stance in the trigger boundary: default to canonical-only for unreleased work; require explicit language to trigger compatibility-preserving outputs.
- For non-trivial skills, write `references/evals.yaml` early (RED → GREEN → REFACTOR).

### 1.5) Immediate feedback loop (recommended)

Do not wait for a “perfect” spec before testing:
- Run 1–2 realistic prompts against the draft early.
- Show concrete outputs/artifacts quickly.
- Use observed failures to tighten triggers and constraints before expanding scope.
- Keep loops short and evidence-backed; avoid speculative rewrites.

### 2) Choose the skill structure

- **Single-file**: one intent, one workflow, < ~200 lines.
- **Router style**: multiple intents/workflows, heavy domain knowledge, or multiple output contracts.

Router layout:
```
skill-name/
  SKILL.md
  workflows/
  references/
  scripts/
  assets/
  agents/openai.yaml
```

### 3) Scaffold the folder

Use the initializer:

```bash
python scripts/init_skill.py <skill-name> --target codex --run-type instruction --path <output-dir>
```

Then delete any unused folders and example files.

### 4) Author SKILL.md

Frontmatter:
- `name`: kebab-case, matches folder name.
- `description`: **single line**; WHAT + WHEN + outputs + success criteria; include negative triggers.
- Prefer minimal frontmatter (default: only `name` + `description`).

Body:
- Include a short Principles section before the workflow.
- Keep the workflow minimal and reliable.
- Link to `references/` instead of pasting long docs (progressive disclosure).
- Store templates/examples in the skill bundle, not in prompts.
- Include the decision feedback protocol block (`decision-feedback-protocol:v2`) unless a stronger repo-specific equivalent already exists.

### 5) Add resources (as needed)

- `references/`: schemas, style guides, evals, contracts, deep docs.
- `scripts/`: deterministic helpers (token-efficient + repeatable).
- `assets/`: templates, boilerplate, fixtures.

Prefer relative paths so the skill works anywhere.

### 6) Validate (fail fast)

Stop at the first failed gate and fix it before proceeding.

```bash
~/.venvs/pyyaml/bin/python scripts/quick_validate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/skill_gate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/analyze_skill.py <path/to/skill-folder>
```

If the skill is **newly created** (mode `create`), evals are required before completion:

```bash
~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder>
```

Optional expansion:
- `scripts/run_skill_evals.py --dual-run --capture-jsonl` for cross-runner scorecards

### 6.5) Optional A/B compare loop (conservative)

Use this only when the user asks for optimization or variant comparison:
1. Create baseline (`v1`) and candidate (`v2`) skill variants.
2. Run shared eval prompts with `scripts/run_skill_evals.py --dual-run --capture-jsonl`.
3. Compare pass/fail evidence + failure modes, not style preferences alone.
4. Keep the better variant, then rerun core validators.

### 7) Package (optional)

```bash
python scripts/package_skill.py <path/to/skill-folder> dist/
```

## Script-backed security rules (required)

When a skill includes executable code (`scripts/` or containers):

- **Offline by default.** If network is required, gate behind `--allow-network` and document allowed domains.
- **Never echo secrets** (no `os.environ`, no token values).
- **Destructive actions require explicit confirmation**:
  - Prefer `--dry-run` by default
  - Require `--confirm` / `--force` to execute

## What to avoid

- Bloating `AGENTS.md` or `SKILL.md` with encyclopedic content—keep them as maps to deeper sources of truth.
- Writing marketing-style descriptions; treat them as routing logic.
- Putting templates/examples in system prompts; put them inside the skill.
- Assuming network access; keep allowlists tight and explicit.
- Printing logs that could contain secrets.
- Adding backward-compatibility work by default when the project is unreleased/greenfield.

## Constraints

- Redact secrets/credentials/PII by default. Never print raw tokens or environment values.
- Keep frontmatter valid and explicit (`name` + `description` as single-line scalars; use `agents/openai.yaml` for UI/dependency metadata).
- Do not invent external facts; if uncertain, add a verification step.
- For script-backed skills, default to offline behavior and require explicit confirmation for destructive actions.
- Default to canonical implementations for unreleased/greenfield projects; only include backwards-compatibility requirements when explicitly requested.

## Validation

Fail fast: stop at the first failed gate, fix it, and rerun.

```bash
~/.venvs/pyyaml/bin/python scripts/quick_validate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/skill_gate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/analyze_skill.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/openclaw_skill_guard.py <path/to/skill-folder> --mode both
```

Required for new skills:
- `~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder>`

Optional deep checks:
- `~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder> --dual-run --capture-jsonl`
- `python3 scripts/record_skill_feedback.py --skill-path <path/to/skill-folder>/SKILL.md --decision accepted --outcome good --confidence high --notes "validation sample" --workspace <workspace>`
- `python3 scripts/skill_subject_scoreboard.py --workspace <workspace> --format table`

## Examples

- “Create a new skill called `foo-bar` under `utilities/` with eval cases and an output contract.”
- “Audit this skill for trigger quality and tighten the description so it routes correctly.”
- “Fix validation failures (`quick_validate.py` / `skill_gate.py`) with the smallest safe patch and rerun gates.”

## Skill test strategy by type

Choose eval style by skill type:
- **Discipline skills** (rules/process): pressure prompts + negative prompts to catch rationalizations.
- **Technique skills** (how-to): application prompts that prove transfer to new scenarios.
- **Pattern skills** (mental model): recognition + “when NOT to use” prompts.
- **Reference skills** (docs/API): retrieval accuracy + correct application prompts.

For each type, include at least one explicit trigger case and one clear non-trigger case.

## Reference map (skill-creator internal)

Use these files when needed:

- `references/about-skills.md`: background on skills, intent, and structure.
- `references/portable-skills.md`: strict subset for cross-platform portability.
- `references/skill-structure.md`: router vs single-file patterns.
- `references/progressive-disclosure-patterns.md`: how to split SKILL.md into references/scripts.
- `references/quality-tools.md`: how to run validators/evals and interpret output.
- `references/iteration-and-testing.md`: eval-driven iteration patterns.
- `references/evals-v2-migration.md`: eval schema v2 fields, migration rules, and tiered gating.
- `references/tiered-gating-policy.md`: week-by-week rollout policy and promotion rules for tier 2.
- `references/security-hardening.md`: offline defaults, redaction, destructive action confirmations.
- `references/skill-knowledge-graph.md`: skill/graph mental model + Cockpit Rule delegation mapping.
- `references/examples.md`: calibrated examples for phrasing and structure.
- `references/anti-patterns.md`: common failure modes + remediation patterns.
- `references/governance-and-style.md`: deck alignment checklist, graph contract gap log, philosophy, anti-patterns, variation, and execution style.

## Runtime injection boundary (graph mode)

When a recursive run consumes injected lessons or external lesson suggestions:

- Keep **decisioning** in SKILL/description only:
  - `description` and SKILL body decide if graph mode runs and what boundaries apply.
- Keep **execution** in scripts/tools only after gates pass:
  - controls check passed,
  - delegation rationale present,
  - immutable IDs present.
- Required invocation envelope inputs before tool use:
  - `invocation_id`
  - `objective_hash`
  - `scope_skill`
  - `scope_profile`
  - `prompt_hash`
- Before any file/command execution, redact/validate:
  - strip secret-like tokens and credentials from `notes`, `feedback`, and notes,
  - require redaction for any user-supplied free text.
- Required artifact completeness before promotion review:
  - `run.json`
  - `capture_record.json` (if auto-capture enabled)
  - `evidence_packet.json` (if capture enabled)
  - `promotion_decision.json`

## Governance and style appendix

Keep SKILL.md concise and load deeper guidance only when needed:
- Deck alignment checklist, graph contract gap report, and governance controls: `references/governance-and-style.md`
- Philosophy/anti-patterns/variation/execution style: `references/governance-and-style.md`

When revising this skill, prefer updating the appendix reference first and only keep route-critical instructions in SKILL.md.
