---
name: skill-builder
description: "Create, revise, benchmark, and quality-gate Codex skills (SKILL.md plus scripts, references, evals, and packaging). Use this skill when the user asks to build, audit, improve, compare, or package a Codex skill or skill-graph contract; do not use it for unrelated app features, generic bug fixing, or routine docs edits."
---

# Skill Builder
This skill designs, improves, validates, and packages high-quality Codex skills.
**Version**: 1.10.0 · **Last updated**: 2026-03-07

## Table of Contents
- [Working agreement](#working-agreement)
- [Scope and triggers](#scope-and-triggers)
- [Modes](#modes)
- [Needed inputs](#needed-inputs)
- [Discovery interview](#discovery-interview)
- [LearningPosture compatibility](#learningposture-compatibility)
- [Deliverables](#deliverables)
- [Response format](#response-format)
- [Output contract](#output-contract)
- [Operating principles](#operating-principles)
- [Skill creation process](#skill-creation-process)
- [Execution guardrails](#execution-guardrails)
- [Script-backed security rules](#script-backed-security-rules)
- [What to avoid](#what-to-avoid)
- [Constraints](#constraints)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Reference map](#reference-map)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Empowering execution style](#empowering-execution-style)

## Working agreement
- Follow the repo `AGENTS.md`; treat it as a map, not a megadoc.
- Keep the artifact boundary explicit:
  - local Codex CLI -> `./artifacts/`
  - hosted shell -> `/mnt/data/`
- Keep `SKILL.md` within a strict line budget (target <= 320 lines). If new depth is needed, move it to `references/` and link it.
- For long runs, write short status notes so compaction is safe.
- For advisory or intake-only turns, do bounded preflight first; do not broad-scan the repo tree unless editing or repo-wide analysis is actually needed.

## Standards snapshot (March 2026)
- Build skills as routing assets plus durable support files, not megadocs.
- Prefer repo-validated workflow and benchmark evidence over aspirational wording.
- Treat evals, contracts, and validator output as part of the product, not optional polish.
- Keep the result implementable by another agent without hidden context.
- Start with the smallest package boundary and 2-3 focused surfaces on a first pass.
- Avoid sprawling scope by keeping first-pass plans narrow until evidence justifies expansion.

## Scope and triggers
Use this skill to:
- create a new skill;
- improve an existing skill’s routing, workflow, or reliability;
- audit a skill against repo standards and validators;
- compare two skill variants;
- package a validated skill for reuse;
- improve skill-graph contracts tied to recursive workflow operations.

Do not use this skill for unrelated application features, generic debugging, or ordinary documentation tasks that do not create or improve a skill.

## LearningPosture compatibility

This skill must preserve existing `delegation.mode` semantics while supporting posture-aware guidance via `learning_posture` metadata.

- Supported posture modes:
  - `learn`: explain alternatives, assumptions, and risks first before proposing edits.
  - `guided`: propose concrete improvements, keep the user in the loop, and require explicit progression checkpoints.
  - `execute`: apply agreed changes only after scope, inputs, and safety gates are present.
- Default posture for this skill is `guided`.
- Explicit `learn` posture requests should delay output-only behavior and increase explanation depth.
- For execution requests, the skill should still preserve the advisory safety bar and never remove existing human checkpoint gates from the spec.

## Modes
Choose the smallest mode that fits:
- **create**: scaffold and author a new skill;
- **improve**: tighten routing, workflow, safety, or portability;
- **eval**: run validators and summarize findings;
- **benchmark-lite**: compare variants with shared evals;
- **graph**: refine skill-graph docs, contracts, or runtime metadata;
- **package**: produce a distributable `.skill` archive.

Default to `create` or `improve`.

## Needed inputs
- skill goal;
- 3-10 example prompts:
  - 2-5 happy path,
  - 1-3 edge cases,
  - 1-3 should-not-trigger negatives;
- target environment: `codex`, `claude`, or `portable`;
- any needed tools, APIs, schemas, templates, or style rules;
- compatibility posture;
- if graph work is in scope, the profile/scope and intended graph outputs.

If key details are missing, ask only the minimum questions needed to proceed safely.

## Discovery interview
When `create` or `improve` work is underspecified, run a round-based discovery interview before building.

- Use Codex `request_user_input` first when a round fits into 1-3 short prompts.
- Ask one round at a time and wait for the answer before moving on.
- Skip rounds already answered by the thread; do not make the user restate known context.
- Stop when you are about 95 percent confident you can build the skill safely.
- Keep each round intuitive:
  - start with one plain-language question,
  - prefer concrete options over jargon,
  - explain why the round matters in one short sentence,
  - avoid dumping the whole interview plan at once.
- Prefer the reusable `request_user_input` mini-templates and payload examples in `references/discovery-interview.md` unless the thread already suggests a better phrasing.
- If discovery needs more than one round, prefer isolated discovery in a forked subagent context so the main thread stays compact.
- Before building, summarize the skill back to the user and ask for confirmation.
- Use `references/discovery-interview.md` for the six-round default flow.

## Deliverables
Produce what the request actually needs, usually from this set:
- a skill folder with `SKILL.md`;
- `scripts/`, `references/`, `assets/`, or `workflows/` when they materially help;
- `agents/openai.yaml` when OpenAI or Codex UI or tool metadata is needed;
- `references/contract.yaml` and `references/evals.yaml` for non-trivial skills;
- `references/plan.md` for multi-step builds;
- validator output, analyzer output, and an OpenClaw-style readiness summary;
- a packaged `.skill` file when packaging is requested.
- a concise blocker summary when a skill cannot meet the quality bar in the current turn

For created or revised skills, keep decision-feedback instrumentation in scope:
- include the `decision-feedback-protocol:v2` block in the skill when post-run feedback is relevant;
- make feedback runtime-owned: if capture is enabled, emit a non-blocking `post_run_feedback` event after result delivery via Codex `request_user_input`;
- keep feedback recordable with `scripts/record_skill_feedback.py`.

## Response format
Start with these headings and no text before them:

## Scope and triggers
- confirm when the skill applies.

## Required inputs
- list missing inputs or state what is already known.

## Deliverables
- list the files, checks, or artifacts you will produce.

## Failure mode
- if the request is out of scope, say why and suggest the closest next step.

On the first response, stay compact: no deep implementation, no file scaffolding, and no validator dump unless the user asked for it or the inputs are already complete.

## Output contract
For non-trivial `improve`, `eval`, or `benchmark-lite` responses, include a deterministic summary block after prose:

```json
{
  "schema_version": "1.0",
  "mode": "improve|eval|benchmark-lite",
  "skill_path": "<path>",
  "findings": [{"id":"<short-id>","priority":"P0|P1|P2","status":"open|fixed","summary":"<one line>"}],
  "validations": [{"name":"<validator>","result":"pass|warn|fail"}],
  "next_step": "<single next action>"
}
```

## Operating principles
### Humans steer. Agents execute.
Translate vague intent into a repeatable workflow. When results are weak, fix the scaffolding, constraints, or feedback loop instead of pushing harder on the same draft.

### Keep SKILL.md as a map
Keep route-critical guidance in `SKILL.md` and move depth into:
- `references/` for the system of record,
- `scripts/` for deterministic helpers,
- `assets/` for templates and fixtures.

### Descriptions are routing logic
The frontmatter `description` is the decision boundary. Make it concrete about:
- when to use the skill;
- when not to use it;
- outputs and success criteria.

Use `references/description-optimization.md` when routing quality is the main issue.

### Calibrate language to the user
Use terms like `eval`, `assertion`, `benchmark`, and `JSON` only as freely as the user’s fluency supports. Briefly define specialized terms when needed.

### Think in tradeoffs
Ask three questions before you lock the design:
- Why does this skill exist?
- What evidence would change the workflow?
- What should stay out of scope?

Vary examples, adapt the structure, and choose context-specific guidance. Avoid repetitive, generic, cookie-cutter instructions; converge only after evidence review.

## Skill creation process
Skip steps only with a clear reason.

### 0) Confirm target and boundary
- confirm where the skill lives;
- confirm the artifact boundary;
- confirm `name` follows `^[a-z0-9](?:-?[a-z0-9]){0,63}$` and exactly matches the target folder name;
- mine the current thread for demonstrated tools, steps, constraints, output shapes, and corrections before asking the user to restate them.

### 1) Lock down triggers early
- collect happy, edge, and negative prompts;
- encode use-when, don’t-use-when, outputs, and success criteria in the `description`;
- keep compatibility boundaries explicit;
- for non-trivial skills, write `references/evals.yaml` early;
- enforce trigger coverage minimums in evals: at least 3 should-trigger prompts and 3 should-not-trigger prompts;
- for trigger-tuning work, use `references/description-optimization.md`.

### 2) Choose the structure
- **single-file** for one intent and one workflow;
- **router-style** for multiple intents, heavy domain knowledge, or multiple output contracts.

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

Keep support files one-level deep inside standard folders (`references/<file>`, `scripts/<file>`, `assets/<file>`). Avoid nested trees unless a validator requires them.

### 3) Scaffold the folder
Use:
```bash
python scripts/init_skill.py <skill-name> --target codex --run-type instruction --path <output-dir>
```

Delete unused starter files immediately.

### 4) Author SKILL.md
- keep frontmatter minimal: `name` plus `description`;
- make `description` a single line with trigger boundary and success criteria;
- keep frontmatter parser-safe: avoid XML-style angle brackets (`<` or `>`) in `name`/`description`;
- keep the workflow lean and reliable;
- link to references instead of pasting deep docs;
- keep templates and examples inside the skill bundle, not in prompts.

### 5) Add resources only when they earn their keep
- use `references/` for deep docs, schemas, contracts, and evals;
- use `scripts/` for repeatable helpers;
- use `assets/` for templates and fixtures.
- for Codex-native UX or tool wiring, add `agents/openai.yaml` with at least `display_name`, `short_description`, and policy-aware tool metadata.

If repeated eval runs recreate the same helper script, bundle it once in `scripts/` and reuse it.

### 6) Validate
Run the core validators, fix the first failing gate, then rerun.

### 6.5) Compare variants only when needed
- run shared evals for baseline and candidate;
- compare evidence and failure modes, not style alone;
- when quality is subjective, prefer blind comparison before declaring a winner.

### 7) Package only after quality gates pass
```bash
python scripts/package_skill.py <path/to/skill-folder> dist/
```

## Execution guardrails
- Cap iterative fix loops at 3 rounds per failing gate; after round 3, stop and report blockers plus the smallest safe next step.
- Do not repeat the same command unchanged more than twice; if it fails twice, change approach or halt.
- Prefer deterministic helper scripts over free-form retries when the same failure repeats.
- Keep benchmark and validation reruns scoped while iterating, then rerun repo-wide gates before claiming the portfolio is clean.

## Script-backed security rules
When the skill includes executable code:
- default to offline behavior;
- gate network use behind explicit flags and an allowed domains or host allowlist policy;
- keep destructive actions behind dry-run or explicit confirmation;
- never echo secrets or raw environment values.

## What to avoid
- NEVER pad `SKILL.md` with theory that belongs in `references/`.
- DO NOT broaden the `description` until it overlaps with adjacent skills.
- DON'T add scripts, network calls, or compatibility branches unless the workflow truly needs them.
- Avoid marketing copy; treat the description as routing logic.
- Avoid absolute paths and hidden environment assumptions when a relative path or explicit prerequisite will do.

## Constraints
- Redact secrets, credentials, tokens, and PII by default.
- Keep frontmatter valid and minimal.
- Do not invent external facts; add a verification step when uncertain.
- Default to canonical implementations for unreleased or greenfield work.
- For schema-bound outputs, include `schema_version` in the contract or artifact example.
- Keep generated skill names and folder names aligned; do not finalize with a mismatch.
- Use `docs/skill-graphs/question-lifecycle.md` for question timing and `docs/skill-graphs/knowledge-graph-operating-model.md` for graph-mode runtime boundaries instead of expanding them inline here.

## Validation
Fail fast: stop at the first failed gate, fix it, and rerun before continuing.
Core validators:
```bash
~/.venvs/pyyaml/bin/python scripts/quick_validate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/skill_gate.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/analyze_skill.py <path/to/skill-folder>
~/.venvs/pyyaml/bin/python scripts/openclaw_skill_guard.py <path/to/skill-folder> --mode both
```

For new skills:
```bash
~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder>
```

Optional deep checks:
- `~/.venvs/pyyaml/bin/python scripts/run_skill_evals.py <path/to/skill-folder> --dual-run --capture-jsonl`
- `python utilities/skill-builder/scripts/benchmark_skill_portfolio.py --root . --config utilities/skill-builder/references/benchmark-policy.json --mode warn --format text --output-json artifacts/industry-benchmark-latest.json`
- `python utilities/skill-builder/scripts/refresh_benchmark_policy.py --root . --policy utilities/skill-builder/references/benchmark-policy.json --benchmark-json artifacts/industry-benchmark-latest.json --schedule-days 7 --report-json artifacts/benchmark-policy-refresh-report.json`
- `python utilities/skill-builder/scripts/run_repo_skill_quality.py --root . --baseline-file utilities/skill-builder/references/skill-quality-baseline.json --benchmark-mode warn --benchmark-config utilities/skill-builder/references/benchmark-policy.json --benchmark-output-json artifacts/industry-benchmark-latest.json --format text`
- `~/.venvs/pyyaml/bin/python scripts/deterministic_trace_checks.py <path/to/codex-run.jsonl> --budgets-json '{"max_total_tokens":4000,"max_duplicate_command_ratio":0.35}'`
- `python3 scripts/record_skill_feedback.py --skill-path <path/to/skill-folder>/SKILL.md --decision accepted --outcome good --confidence high --notes "validation sample" --workspace <workspace>`
- `python3 scripts/skill_subject_scoreboard.py --workspace <workspace> --format table`
- `python3 - <<'PY'\nimport pathlib,re,sys\np=pathlib.Path(\"<path/to/skill-folder>\").resolve(); name=p.name\nok=bool(re.fullmatch(r\"[a-z0-9](?:-?[a-z0-9]){0,63}\", name))\nprint(\"OK\" if ok else \"FAIL\", name)\nsys.exit(0 if ok else 1)\nPY`

## Troubleshooting
- Error: folder/name mismatch. Recovery: rename folder to match frontmatter `name`, then rerun validators.
- Error: frontmatter contains `<` or `>` and fails parser safety. Recovery: replace angle brackets with plain-language wording, then rerun validators.
- Error: repeated validator failure after 3 rounds. Recovery: halt, summarize failing gate output verbatim, and ask for a scoped decision.

## Examples
- “When the user asks to create a new release-note helper skill under `utilities/`, scaffold it with evals, contract, and an output contract.”
- “Can you audit this skill’s trigger quality and tighten the description so it routes cleanly?”
- “Help me compare two skill variants with the same eval suite and keep the higher-signal version.”

## Reference map
Use these files when needed:
- `references/discovery-interview.md` for round-by-round clarification;
- `references/description-optimization.md` for trigger tuning;
- `references/iteration-and-testing.md` for eval-driven refinement;
- `references/quality-tools.md` for validator and eval interpretation;
- `references/skill-structure.md` and `references/progressive-disclosure-patterns.md` for layout choices;
- `references/security-hardening.md` for offline defaults and destructive-action gates;
- `docs/skill-graphs/question-lifecycle.md` for question timing and post-run feedback behavior;
- `docs/skill-graphs/knowledge-graph-operating-model.md` for graph-mode boundaries;
- `references/examples.md`, `references/anti-patterns.md`, and `references/governance-and-style.md` for calibrated examples and deeper guidance.
- `../codex-plugin-builder/references/plugin-contract.md` and `../codex-plugin-builder/scripts/plugin_builder.py` when validating plugin-owned skills or enforcing plugin manifest and marketplace contracts.

## See Also

| Skill | When to use together |
|---|---|
| [[codex-plugin-builder]] | Package a validated skill into a distributable plugin; runs after quality gates pass |
| [[decide-build-primitive]] | Use before building to confirm a Skill is the right primitive vs a Prompt or Automation |
| [[verification-before-completion]] | Gate any "skill is done" claim with fresh validator evidence |
| [[evals-router]] | When the skill is an LLM eval workflow — use to design or audit the eval layer |
| [[agents-md]] | When the new skill needs a corresponding AGENTS.md entry or routing update |

**Topic map:** [[agent-ops]]

## Decision feedback protocol

<!-- decision-feedback-protocol:v2 -->
- Question timing is runtime-owned. Do not make the skill itself decide when feedback is asked.
- If post-run feedback capture is enabled, emit a non-blocking `post_run_feedback` event via Codex `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 scripts/record_skill_feedback.py`.

## Empowering execution style
Be capable, creative, and willing to explore better options when evidence supports them. Enable the user to make safe choices by explaining tradeoffs clearly, then keep the implementation disciplined and auditable.

## Legacy mode: install-distribute
Use this mode when the request is about listing, installing, updating, or validating skills from curated registries or GitHub sources rather than authoring the skill itself.

### Install-distribute triggers
- list curated skills or compare what is already installed;
- install a skill from a curated registry, GitHub repo, or repo path;
- update an installed skill safely with overwrite and deconflict checks;
- dry-run a proposed install before writing files.

### Install-distribute required inputs
- source: curated skill name, repo URL, or repo path;
- destination scope: `REPO` or `USER`;
- target destination path or category;
- overwrite/update consent when the destination already exists;
- whether the user wants listing, dry-run, install, update, or deconflict analysis.

Use `request_user_input` for missing install decisions when the turn fits in 1-3 short questions. Do not overwrite or promote files until the scope and overwrite decision are explicit.

### Install-distribute operating rules
- Prefer curated or verified sources and stage external fetches in `/tmp` or `/mnt/data`.
- Keep installs auditable: source, ref, staging path, validations, and final destination should all be reported.
- Run a risk scan before promotion and stop on high-severity findings unless the user explicitly approves continuation.
- Run deconflict analysis for every install/update request before any write. Do not rely on "looks overlapping" heuristics.
- Deconflict scope must review all installed operational skills in the chosen destination scope (`REPO` or `USER`) and then decide: merge, fold, improve-existing, or install-new.
- Exclude system/meta skills from default deconflict comparisons unless the user explicitly asks for system-skill work. Default exclusions include `.system` slices and creator/meta scaffolding skills such as `skill-creator`.
- For plugin installs or Claude-to-Codex plugin conversions, run local plugin deconflict analysis first:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py inspect-local <plugin-name> --path plugins`
  - prefer merge, fold, or improvement work when an existing local plugin already covers the intended job.
- For unclear requests, default to `list` or `dry-run` instead of mutating the workspace.
- For Claude-to-Codex plugin conversion during install runs, enforce terminology mapping:
  - `.claude-plugin/plugin.json` -> `.codex-plugin/plugin.json`
  - `commands/` and slash-command wording -> `prompts/`
  - reject legacy Claude runtime markers in final Codex package paths.

### Install-distribute deliverables
- installed or updated skill folder, or a dry-run plan if no writes occurred;
- source summary, staging boundary, and any deconflict or risk findings;
- explicit deconflict decision record (`merge`, `fold`, `improve-existing`, or `install-new`) and why;
- validator results for each installed target;
- restart reminder after successful install/update;
- verification that the installed `SKILL.md` includes decision feedback instrumentation when relevant.

### Install-distribute validation
- run the installed skill through quick validation, skill gate, analyzer, and OpenClaw-style guard checks;
- run evals for newly installed skills after write completion;
- confirm the repo diff only contains expected skill-install paths;
- stop and report blockers if a failing step repeats 3 times.
- for plugin installs/conversions, run:
  - `python3 utilities/codex-plugin-builder/scripts/plugin_builder.py validate <path/to/plugin> --require-marketplace --marketplace-path .agents/plugins/marketplace.json`

## Folded Legacy Modes (Core60)
<!-- core60-folded-modes:v1:start -->
This skill owns legacy capability from retired skills. Use these modes when requests match prior behavior.

- `install-distribute` from `utilities/skill-installer`: Plan and install skills into a Codex skills directory from curated or repo sources; use when a user asks to list available skills, install or update a skill, or validate a source before installation.
- `prompt-packaging` from `utilities/codex-prompt-creator`: Create or update reusable Codex skills under .agents/skills and optionally local ~/.codex/prompts shortcuts. Use when a user asks to buil...

Deep legacy details: `references/folded-legacy-modes-core60.md`.
<!-- core60-folded-modes:v1:end -->
