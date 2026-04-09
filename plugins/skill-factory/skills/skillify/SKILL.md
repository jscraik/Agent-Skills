---
name: skillify
description: Capture a completed Codex workflow as a reusable SKILL.md package by analyzing session context, interviewing the user with structured prompts, and writing a validated skill artifact. Use when the user asks to skillify or operationalize a repeatable process.
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
- Preferred destination: repo-local skill or personal skill.

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
- Use `request_user_input` for all user questions; do not embed multi-choice questions in plain text replies.
- Keep interviews short for simple workflows; expand only where ambiguity remains.
- Preserve user corrections as hard rules in the generated skill.
- Do not claim validation unless commands were actually run.
- Redact secrets, tokens, credentials, and sensitive personal data by default in prompts, drafts, and summaries.

## Workflow
### 1) Analyze session before asking questions
- Extract:
  - repeatable process objective;
  - ordered steps;
  - inputs and parameters;
  - required tools and permissions;
  - success artifacts for each step;
  - user corrections and non-negotiables.
- If evidence is thin, mark assumptions explicitly before interview round 1.

**Success criteria**:
- Clear initial process outline exists with no unresolved contradictions.

### 2) Round 1 interview: name, scope, and success outcome
- Use `request_user_input` to confirm:
  - proposed skill name and one-line description;
  - top-level goal and completion criteria;
  - whether captured behavior should be strict or adaptable.
- Recommend a default name and description first, then let user override.

**Success criteria**:
- Name, description, and completion target are confirmed.

### 3) Round 2 interview: structure and destination
- Use `request_user_input` to confirm:
  - high-level ordered steps;
  - arguments needed for reuse;
  - execution style (`inline` vs `fork`);
  - destination:
    - repo local: `./.codex/skills/<name>/SKILL.md`
    - personal: `${CODEX_HOME:-$HOME/.codex}/skills/<name>/SKILL.md`
- For Codex-specific skills, default to repo-local when the workflow is project-bound.

**Success criteria**:
- Step skeleton, argument set, execution style, and save location are confirmed.

### 4) Round 3 interview: deepen each step only as needed
- Iterate one step at a time with `request_user_input` when details are unclear.
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
  - frontmatter with `name`, `description`, `when_to_use`, and minimal required fields;
  - `Success criteria` in every step;
  - optional annotations (`Execution`, `Artifacts`, `Human checkpoint`, `Rules`) only when useful.
- Keep body concise; place deep rationale in `references/` files when needed.

**Success criteria**:
- Draft has no TODO markers and is internally consistent.

### 7) Review and save
- Present full `SKILL.md` draft in a fenced `markdown` block.
- Ask for confirmation via `request_user_input` with a concise prompt.
- On approval, write files and report:
  - saved path;
  - invoke command;
  - any assumptions encoded.

**Success criteria**:
- Skill files are written to the confirmed location and invocation guidance is explicit.

## Validation
- Run:

```bash
python3 plugins/skill-factory/skills/skill-creator/scripts/quick_validate.py plugins/skill-factory/skills/skillify
./bin/ask skills audit plugins/skill-factory/skills/skillify --level strict --robot
bash scripts/validate_skill_authoring_family.sh
```

- Fail fast and fix the first reported issue before final handoff.

## Anti-patterns
- Asking all interview questions at once for a simple 2-3 step process.
- Writing `SKILL.md` before confirming destination and trigger phrases.
- Copying a generic template without incorporating session-specific corrections.

## Examples
- "We just finished debugging a failing `pr-pipeline` check and posting the Linear update. Skillify exactly what we did so I can reuse it next week."
- "Convert this morning's review-to-merge flow into a reusable skill and keep it repo-local in `./.codex/skills/pr-ready-flow`."
- "Capture my incident-triage handoff process as a personal Codex skill in `${CODEX_HOME:-$HOME/.codex}/skills`, and keep the interview short."

## Failure mode
- If `request_user_input` cannot be used (tool unavailable or blocked), stop before drafting and report that the interview contract cannot be satisfied safely.
- If validation fails after save, do not finalize; fix the failing check and re-run the same validation commands.

## Gotchas
- Keep `request_user_input` prompts short and mutually exclusive; long option labels reduce completion quality.
- Do not skip confirmation of destination path, or skills may be written to the wrong catalog and appear "missing."

## References
- `references/skill-template.md`
- `references/contract.yaml`
- `references/evals.yaml`

## See Also

| Skill | When to use |
|---|---|
| [[skill-creator]] | Create first-draft skill scaffolds before hardening |
| [[skill-installer]] | Install and surface a validated skill across Codex catalogs |


**Topic map:** [[agent-ops]]
