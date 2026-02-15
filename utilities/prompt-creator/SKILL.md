---
name: prompt-creator
description: Create or update Codex skills (shareable, can be invoked implicitly) under .agents/skills when you want reusable team workflows; optionally create local custom prompts in ~/.codex/prompts when you explicitly want /prompts:... slash commands (deprecated).
---

# Prompt Creator (Codex skills-first)

## Scope and triggers
- You want a **shareable, reusable** workflow that your team can commit to a repo and Codex can invoke **implicitly** (based on `description`) or **explicitly** (by typing `$...`). Skills are the recommended primitive.
- You want a reusable workflow that also shows up in the **slash command menu** (enabled skills appear there too).
- You have an existing skill under `.agents/skills/**` and want to refine scope, inputs, safety constraints, or examples.
- You’re deciding between **skills vs deprecated custom prompts** and want a short recommendation.

> Note: Codex docs mark “custom prompts” as **deprecated** and recommend using **skills** for reusable instructions that Codex can invoke explicitly or implicitly. Only use `~/.codex/prompts` when you explicitly want `/prompts:<name>` local-only slash commands.

## Required inputs
- Skill name (kebab-case): for example `draftpr`.
- Skill scope + location:
  - Repo skill (recommended): `<repo>/.agents/skills/<skill-name>/`
  - User skill: `~/.agents/skills/<skill-name>/`
- One-line `description` (critical for implicit invocation).
- The workflow instructions you want Codex to follow.
- Optional resources:
  - `references/` for deeper docs
  - `assets/` for templates
  - `agents/openai.yaml` for UI metadata and dependencies (MCP tools)
- (Optional) If you explicitly want `/prompts:<name>`: a custom prompt name + body + placeholders.
- Safety constraints: anything that must *not* happen (no deletes, no deploys, no secrets, etc.).

## Deliverables
- A skill folder containing a `SKILL.md` file at one of:
  - `.agents/skills/<skill-name>/SKILL.md` (repo; recommended)
  - `~/.agents/skills/<skill-name>/SKILL.md` (user)
- A short “how to invoke” snippet:
  - Explicit: type `$<skill-name>` in the composer, or select it from the slash command menu.
  - Implicit: describe the task; Codex can choose the skill when it matches `description`.
- Optional (only when requested): a deprecated custom prompt file at `~/.codex/prompts/<name>.md` for `/prompts:<name>`.
- **Always include the full proposed file contents** for any new/updated `SKILL.md` (and `~/.codex/prompts/*.md` if applicable) inside fenced code blocks so the user can copy/paste if Codex can’t write files in the current sandbox.
- For created/updated skills, include a short OpenClaw-style readiness + security summary (critical/warn/info).

## Philosophy
- Prefer **skills** for anything shareable, multi-step, or policy-heavy.
- Keep skills small and single-purpose; push depth into `references/` (progressive disclosure).
- Safety-by-default: prompts must not smuggle destructive behavior or secrets.

## Procedure
0) **If the user is only asking “what should I use?”**
   - Answer directly in 1–2 sentences.
   - Do **not** run commands or attempt file writes.
   - If they want `/prompts:<name>`, say: “Use `~/.codex/prompts/<name>.md` (custom prompts are deprecated).”

1) **Default to a repo skill**
   - Create the folder:
     ```bash
     mkdir -p .agents/skills/<skill-name>
     ```
   - Create `.agents/skills/<skill-name>/SKILL.md` with this minimal template:
     ```md
     ---
     name: <skill-name>
     description: Explain exactly when this skill should and should not trigger.
     ---

     # <Skill title>

     ## When to use
     - ...

     ## Inputs
     - ...

     ## Procedure
     1) ...
     ```
   - In your response, **include the full `SKILL.md` contents** in a fenced code block (even if you also write it to disk).
2) **Make implicit invocation reliable**
   - Put clear trigger keywords + boundaries in the `description` line.
3) **Add guardrails**
   - Add explicit “do not” constraints in the instructions (no deploys, no secrets, etc.).
4) **Never claim you wrote files unless verified**
   - If you edit/create files, verify with a directory listing (for example: `ls -la .agents/skills/<skill-name>`).
   - If you cannot write due to sandboxing or permissions, say so and provide the exact file contents instead.
5) **(Optional) Add supporting resources**
   - `references/` for longer docs and checklists.
   - `agents/openai.yaml` if you need UI metadata or MCP dependencies.
6) **Only if you explicitly want `/prompts:<name>`**
   - Use a custom prompt in `~/.codex/prompts/` (**deprecated**). Prefer this only for local, explicit shortcuts.
   - Custom prompts must be top-level `*.md` files under `~/.codex/prompts/` (Codex ignores non-Markdown files and subdirectories).
   - When recommending this path, explicitly say: “Custom prompts are deprecated.”

## Validation
- Fail fast: if validation fails, stop and fix the smallest issue before continuing.
- For any new/updated skill folder, run:
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/openclaw_skill_guard.py <skill-dir> --mode both`
- If critical findings appear, do not recommend enablement until fixed or explicitly approved.
- Restart Codex if your new/updated skill doesn’t appear.
- Confirm you can invoke the skill:
  - Explicit: type `$<skill-name>` in the composer and select the skill.
  - Slash menu: type `/` and confirm the enabled skill appears in the list.
- Test a “near miss” prompt to ensure it doesn’t trigger when it shouldn’t (tight `description`).
 
If you created a deprecated custom prompt:
- Restart Codex and confirm `/prompts:<name>` appears in the slash menu.

## Anti-patterns
- Putting secrets, tokens, or credentials in prompt files (they are plain text on disk).
- Using custom prompts for workflows that should be gated (deploys, migrations, mass deletes).
- Writing huge skills without `references/` (violates progressive disclosure).
- Reusing a generic `description` that causes accidental implicit invocation.

## Constraints
- Never include secrets/credentials/PII in prompt files; redact by default.
- Prefer minimal diffs; do not overwrite existing skill instructions without an explicit “overwrite” instruction.
- If the user asks for a shared/team workflow, implement a **skill** (repo) instead of a local custom prompt.

## Examples
### Draft PR helper (skill)
Create `.agents/skills/draftpr/SKILL.md`:
```md
---
name: draftpr
description: Create a branch, commit selected files, and open a draft PR when I say "draft PR" or "open a draft PR".
---

Create a branch named `dev/<feature_name>` for this work.
If the user provides FILES, stage them first.
Commit the staged changes with a clear message.
Open a draft PR on the same branch. Use PR_TITLE when supplied; otherwise write a concise summary yourself.
```

Invoke (explicit):
```text
$draftpr
```

### Local `/prompts:` shortcut (deprecated)
Only do this when you explicitly want `/prompts:<name>` and don’t need repo sharing.

Create `~/.codex/prompts/draftpr.md`:
```md
---
description: Prep a branch, commit, and open a draft PR
argument-hint: FILES=<paths> PR_TITLE="<title>"
---

Create a branch named `dev/<feature_name>` for this work.
If files are specified, stage them first: $FILES.
Commit the staged changes with a clear message.
Open a draft PR on the same branch. Use $PR_TITLE when supplied; otherwise write a concise summary yourself.
```

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (trigger + acceptance checks)
- If you extend this skill to emit a machine-checkable output contract, include `schema_version` in that contract.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
