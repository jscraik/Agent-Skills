---
name: skillify
description: Capture a completed Codex workflow as a reusable SKILL.md package by analyzing session context plus optional session-collector evidence, interviewing the user with structured prompts, and writing a validated skill artifact. Use when the user asks to skillify or operationalize a repeatable process.
metadata:
  skill-type: scaffolding_templates
---

# Skillify

Codex-native workflow for converting a just-completed conversation into a reusable skill package.

## When to use
- User asks to "turn this workflow into a skill," "skillify this session," or "capture this process as a reusable skill."
- The session contains a repeatable process with stable steps, constraints, and success artifacts.
- The user wants structured follow-up questions before generating `SKILL.md`.

## Required inputs
- Optional short process description from the user.
- Current session context (messages, constraints, corrections, and outcomes).
- Optional `session-collector` JSON artifact path (example: `~/.config/codex/usage-data/session-collector.json` or `$SESSION_COLLECTOR_PATH`) when thread evidence needs corroboration.
- Preferred destination: canonical git-backed skill category path.
- Category confirmation (primary category 1-9 from the skill-builder matrix).
- Target environment (`codex`, `claude`, or `portable`) and compatibility posture (`learn`, `guided`, or `execute`).

## Deliverables
- A reviewed `SKILL.md` draft matching the process.
- Saved skill directory with at least `SKILL.md` and aligned `agents/openai.yaml`.
- Explicit invoke syntax (`/<skill-name> [arguments]`) and file path in final handoff.
- Structured summaries should include `schema_version` when machine-consumed output is requested.

## Philosophy
- Preserve user intent as an executable contract, not a loose summary.
- Start with the smallest viable package boundary and 2-3 focused surfaces, then expand only when needed.
- Prefer specific success artifacts over abstract completion statements.

## Constraints
- Prefer `request_user_input` for all user questions. If unavailable, use 1-3 numbered chat questions and continue.
- Keep interviews short for simple workflows; expand only where ambiguity remains.
- Preserve user corrections as hard rules in the generated skill.
- Treat `session-collector` evidence as optional support, never as a hard prerequisite.
- When `session-collector` data is stale or missing, continue with thread evidence and state assumptions explicitly.
- Do not claim validation unless commands were actually run.
- Redact secrets, tokens, credentials, and sensitive personal data by default in prompts, drafts, and summaries.

## Workflow
### 0) Confirm category, environment, and posture
- Start with one plain-language confirmation:
  - category (1-9);
  - target environment (`codex|claude|portable`);
  - compatibility posture (`learn|guided|execute`).
- Recommend defaults based on observed workflow before asking for overrides.

**Success criteria**:
- Category, environment, and posture are explicit before drafting.

### 1) Analyze session evidence before asking questions
- Extract:
  - repeatable process objective;
  - ordered steps;
  - inputs and parameters;
  - required tools and permissions;
  - success artifacts for each step;
  - user corrections and non-negotiables.
- If available, use `session-collector` artifact evidence to corroborate ordering, tool usage, and project scope. Read `references/session-collector-intake.md` when this path is used.
- Record evidence provenance as one of: `thread_only` or `thread_plus_session_collector`.
- If evidence is thin, mark assumptions explicitly before interview round 1.

**Success criteria**:
- Clear initial process outline exists with no unresolved contradictions.
- Evidence provenance is explicit, and stale/partial telemetry is called out before interview round 1.

### 2) Round 1 interview: name, scope, and success outcome
- Use `request_user_input` when available (fallback: 1-3 numbered chat questions) to confirm:
  - proposed skill name and one-line description;
  - top-level goal and completion criteria;
  - whether captured behavior should be strict or adaptable.
- Recommend a default name and description first, then let user override.

**Success criteria**:
- Name, description, and completion target are confirmed.

### 3) Round 2 interview: structure and destination
- Use `request_user_input` when available (fallback: 1-3 numbered chat questions) to confirm:
  - high-level ordered steps;
  - arguments needed for reuse;
  - execution style (`inline` vs `fork`);
  - whether to preserve telemetry-supported defaults discovered from `session-collector` evidence when present;
  - destination category path under canonical source tree:
    - example: `utilities/<name>/SKILL.md`
    - example: `github/<name>/SKILL.md`
- Default to canonical repository destination and do not propose personal-home destinations.

**Success criteria**:
- Step skeleton, argument set, execution style, and save location are confirmed.

### 4) Round 3 interview: deepen each step only as needed
- Iterate one step at a time with `request_user_input` when available (fallback: 1-3 numbered chat questions) when details are unclear.
- Capture for each major step:
  - downstream artifacts;
  - move-forward proof;
  - checkpoint needs;
  - hard constraints;
  - opportunities for safe parallelism.
- Keep this round minimal for short/simple processes.

**Success criteria**:
- Every major step has actionable instructions and explicit success criteria.

### 5) Round 4 interview: trigger language and gotchas
- Confirm invocation guidance:
  - when to use;
  - trigger phrases;
  - example user requests.
- Ask for final gotchas only if still uncertain.

**Success criteria**:
- Trigger section is precise enough for automatic routing.

### 6) Draft the skill package
- Build `SKILL.md` using the template in `references/skill-template.md`.
- Include:
  - frontmatter with official keys only (`name`, `description`, optional sanctioned keys);
  - routing language (`when to use`, trigger phrases, argument hints) in body sections rather than custom frontmatter keys;
  - `Success criteria` in every step;
  - optional annotations (`Execution`, `Artifacts`, `Human checkpoint`, `Rules`) only when useful.
- Keep body concise; place deep rationale in `references/` files when needed.

**Success criteria**:
- Draft has no TODO markers and is internally consistent.

### 7) Review and save
- Present full `SKILL.md` draft in a fenced `markdown` block.
- Ask for confirmation via `request_user_input` with a concise prompt (fallback: numbered chat confirmation).
- On approval, write files and report:
  - saved path;
  - invoke command;
  - any assumptions encoded.

**Success criteria**:
- Skill files are written to the confirmed location and invocation guidance is explicit.

## Output contract
For non-trivial `skillify` runs, include:
- `schema_version`
- `mode`
- `skill_path`
- `findings`
- `validations`
- `security`
- `next_step`

## Validation
- Run in two passes:
  - `iterative_fail_fast`: stop at first failing gate, fix, and rerun.
  - `pre-claim_full_sweep`: run all gates clean before completion claim.

- Gate commands:

```bash
python3 plugins/skill-factory/skills/skill-builder/scripts/quick_validate.py plugins/skill-factory/skills/skillify --mode compat
./bin/ask skills audit plugins/skill-factory/skills/skillify --level strict --robot
bash scripts/lint_openai_skill_format.sh --mode strict
bash scripts/lint_progressive_disclosure.sh --mode warn
python3 scripts/gotcha_pipeline.py validate
bash scripts/validate_skill_authoring_family.sh
```

- Fail fast and fix the first reported issue before final handoff.

## Anti-patterns
- Asking all interview questions at once for a simple 2-3 step process.
- Writing `SKILL.md` before confirming destination and trigger phrases.
- Copying a generic template without incorporating session-specific corrections.
- Blocking skill generation because `session-collector` data is unavailable.
- Using stale `session-collector` artifacts without calling out freshness limits.

## Examples
- "We just finished debugging a failing `pr-pipeline` check and posting the Linear update. Skillify exactly what we did so I can reuse it next week."
- "Convert this morning's review-to-merge flow into a reusable skill and save it in `utilities/pr-ready-flow`."
- "Capture my incident-triage handoff process as a reusable skill in `github/incident-triage-flow`, and keep the interview short."
- "Use `$HOME/path/to/configs/usage-data/session-collector.json` to confirm the tool sequence, then skillify this flow."

## Failure mode
- If `request_user_input` is unavailable, switch to 1-3 numbered chat questions and continue with the same interview rounds.
- If user confirmation cannot be obtained by either path, stop before saving and report the missing approval checkpoint.
- If validation fails after save, do not finalize; fix the failing check and re-run the same validation commands.

## Gotchas
- Keep `request_user_input` prompts short and mutually exclusive; long option labels reduce completion quality.
- Do not skip confirmation of destination path, or skills may be written to the wrong catalog and appear "missing."
- Confirm `session-collector` artifact freshness (`generated_at` and cutoff window) before using it to derive defaults.

## References
- `references/skill-template.md`
- `references/contract.yaml`
- `references/evals.yaml`
- `references/session-collector-intake.md`
- `assets/icon-small.png` and `assets/icon.png` (wired via `agents/openai.yaml`)

## See Also

| Skill | When to use |
|---|---|
| [[skill-creator]] | Create first-draft skill scaffolds before hardening |
| [[skill-factory:skill-installer]] | Install and surface a validated skill across Codex catalogs |


**Topic map:** [[agent-ops]]