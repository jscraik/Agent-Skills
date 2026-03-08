---
name: skill-installer
description: Plan and install skills into a Codex skills directory from curated or repo sources; use when a user asks to list available skills, install/update a skill, or validate a source before installation. Do not use for general app development, unrelated debugging, or docs-only rewrites.
---

# Skill Installer

## Table of Contents
- [Compliance](#compliance)
- [Philosophy](#philosophy)
- [Guiding questions](#guiding-questions)
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Output contract](#output-contract)
- [Constraints / Safety](#constraints--safety)
- [Communication](#communication)
- [Live feedback (AskQuestion)](#live-feedback-askquestion)
- [Variation rules](#variation-rules)
- [Empowerment principles](#empowerment-principles)
- [Anti-patterns to avoid](#anti-patterns-to-avoid)
- [Scripts](#scripts)
- [Behavior and Options](#behavior-and-options)
- [Notes](#notes)
- [Example prompts](#example-prompts)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)
- [Procedure](#procedure)

## Compliance
- Check against GOLD Industry Standards guidance in `~/.codex/AGENTS.md`.

## Philosophy
- Prefer curated sources; verify before installing.
- Minimize changes and avoid overwriting without consent.
- Keep installs reproducible and auditable.

## Guiding questions
- What is the exact skill source (curated vs repo path)?
- Why is this skill needed (new capability vs update)?
- Is overwrite permitted if the skill exists?
- How will we verify installation success?

## Scope and triggers
- When the user asks to list installable skills.
- When the user asks to install a curated skill by name.
- When the user provides a GitHub repo/path for skill installation.
- For workflow safety checks: when intent is unclear, run a dry-run first.

## Required inputs
- Skill source (curated list, repo URL, or repo/path).
- Installation scope (`REPO` or `USER`).
- Destination path or `AGENT_SKILLS_HOME`/`CODEX_HOME` custom location.
- User confirmation for overwrites or updates.
- For curated installs, accept a single skill name (`--skill`) when path is omitted.

### Codex ask-questions collection (required)
- In Codex Plan and Default modes, use `request_user_input` for missing install decisions (source, destination, overwrite/update consent) whenever it is available and the prompt fits in 1-3 short questions.
- If `request_user_input` is unavailable, ask direct numbered questions in chat and wait for explicit confirmation before writes.
- Do not install or overwrite until required decisions are explicitly confirmed.
- Before any write action, confirm installation scope explicitly (`REPO` path vs `USER` path).

## Deliverables
- Installed skill directory under a category folder (e.g., `~/dev/agent-skills/utilities/<skill-name>`) or a custom path.
- A summary of what was installed and from where.
- An `analyze_skill.py` quality report for each installed target.
- An OpenClaw-style readiness + security report (critical/warn/info) for each installed skill.
- A reminder to restart Codex to pick up new skills.
- Post-install decision-feedback readiness check:
  - Verify installed `SKILL.md` contains `decision-feedback-protocol:v2` (or a stronger equivalent).
  - If missing, patch it and report that AskQuestion parity feedback capture was enabled.
  - Verify the workspace can run subject analytics via `python3 utilities/skill-builder/scripts/skill_subject_scoreboard.py --workspace <workspace>`.
- For `--dry-run`, provide a compact plan summary instead of filesystem changes.

## Output contract
For non-trivial install/deconflict/dry-run outcomes, append a deterministic JSON block after prose:

```json
{
  "schema_version": "1.0",
  "mode": "list|install|update|dry-run|deconflict",
  "source": "<repo-or-url-or-curated-name>",
  "destination": "<resolved-path>",
  "scope": "REPO|USER",
  "staging_path": "<tmp-or-mnt-data-path>",
  "actions": [{"type":"copy|merge|skip|warn","summary":"<one line>"}],
  "risks": [{"severity":"critical|warn|info","summary":"<one line>"}],
  "validations": [{"name":"quick_validate|skill_gate|analyze_skill|openclaw_skill_guard","result":"pass|warn|fail"}],
  "repo_clean": true,
  "retry_rounds": 0,
  "next_step": "<single next action>"
}
```

## Constraints / Safety
- Redact secrets/PII by default.
- Do not overwrite existing skills without explicit consent.
- Use network access only when required; request escalation in restricted sandboxes.
- Avoid installing from untrusted or ambiguous sources.
- Warn on prompt-injection or risky command patterns before installing; default to interactive prompt (investigate / continue / stop).
- High-severity risk findings are blocked by default; require explicit `--force-unsafe` consent to continue.
- Prompt patterns are configurable via `references/prompt-injection-patterns.json` (supports `severity`; this skill’s config, not the target skill).
- Investigate option runs a read-only summary (file counts, largest files, binary attachments, warning matches).
- Investigate output includes a macOS `open` helper and triage labels (docs-context / code-context / unknown).
- Local allow/block config (not in repo) can customize matches: `~/.codex/skill-security/allow-block.json` or `CODEX_SKILL_SECURITY_CONFIG`.
- Network allowlist policy: installer scripts may access only `api.github.com`, `github.com`, `raw.githubusercontent.com`, `codeload.github.com`, and `objects.githubusercontent.com` unless the user explicitly approves expansion.
- Stage external fetches in an isolated temp boundary (`/tmp` or `/mnt/data`) and promote into the final skill destination only after security + validation checks pass.
- Optional visual and fixture resources live in `assets/`; reference them when they materially improve install guidance.

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations.

Use the helper scripts based on the task:
- List curated skills when the user asks what is available, or if the user uses this skill without specifying what to do.
- Install from the curated list when the user provides a skill name.
- For direct curated installs, prefer `--skill <name>`.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

Install skills with the helper scripts.

## Communication

When listing curated skills, output approximately as follows, depending on the context of the user's request:
"""
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
"""

After installing a skill, tell the user: "Restart Codex to pick up new skills."

## Live feedback (AskQuestion)

- Use AskQuestion parity (`request_user_input`) for live user decisions at each non-trivial gate:
  - before overwrite/replace/update of an existing skill directory;
  - after deconflict analysis when overlap is high (default threshold: 20%);
  - when same-job intent detection flags an existing skill as functionally equivalent;
  - when risk scan reports warnings and more than one safe action exists;
  - after install/merge to capture outcome quality feedback.
- Required response fields for decision capture:
  - `decision`: `accepted|partial|rejected|deferred`
  - `outcome`: `good|neutral|bad|unknown`
  - `confidence`: `high|medium|low`
- Persist feedback with `record_skill_feedback.py` using concise notes and selected subject tags.
- Do not close the run before collecting post-action feedback for non-trivial installs/merges.

## Variation rules
- Vary install method by auth context (download vs git).
- Vary output detail by user intent (listing vs install vs update).
- Prefer `--dry-run` or listing when intent is unclear.
- Use different verification depth for updates vs first installs.
- Cap repeated retries at 3 rounds per failing step; on round 4, halt and return blockers.

## Empowerment principles
- Empower users to confirm overwrite decisions.
- Empower reviewers with a clear source + ref summary.
- Empower maintainers with a rollback note (remove installed folder).

## Anti-patterns to avoid
- Installing from an unverified or ambiguous source.
- Overwriting existing skills without explicit consent.
- Skipping the restart reminder after install.

## Scripts

Some script flows use network. Start with least-privilege sandbox execution and only request escalation if the sandbox blocks required network/filesystem operations.

- `scripts/list-skills.py` (canonical curated listing with installed annotations)
- `scripts/list-skills.py --format json`
- `scripts/list-curated-skills.py` (backward-compatible wrapper to `list-skills.py`)
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...] --category <category>`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path> --category <category>`
- `scripts/install-skill-from-github.py --skill <name> --category <category>`
- `scripts/install-skill-from-github.py --dry-run --skill <name> --category <category>`
- `scripts/install-skill-from-github.py --deconflict --deconflict-threshold 0.2 --skill <name> --category <category>`
- `scripts/install-skill-from-github.py --deconflict --deconflict-block-threshold 0.45 --deconflict-engine auto --skill <name> --category <category>`
- `scripts/install-skill-from-github.py --deconflict --merge-proposal --skill <name> --category <category>`
- `scripts/install-skill-from-github.py --run-deconflict-benchmark`

## Behavior and Options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- `--dry-run` performs source resolution + risk scan only and does not mutate destination.
- `--deconflict` performs advisory overlap analysis against installed skills before install.
- `--deconflict-threshold <0..1>` sets overlap cutoff (default `0.2`) for merge-vs-install decisioning.
- `--deconflict-block-threshold <0..1>` sets hard-stop cutoff (default `0.45`) for likely duplicates.
- Same-job detection uses intent coverage + command overlap to flag skills aiming at the same outcome, even when wording differs.
- Same-job detection also applies name-alignment heuristics (for example `skill-installer` variants across categories/repos) to catch near-duplicates early.
- Deconflict scoring uses section-aware intent weighting and a negative-overlap guard to reduce false positives.
- When a same-job match is detected, include concrete improvement ideas (missing commands, sections, or protocol markers) for merge-first decisions.
- `--deconflict-engine auto|harness|lexical` controls overlap signals (`auto` prefers local `harness search` and falls back to `pnpm dlx --allow-build=better-sqlite3 @brainwav/coding-harness search`).
- `--deconflict-cache-path` enables reusable profile cache across repeated runs.
- `--deconflict-artifact-path` writes a structured overlap artifact with knowledge-graph nodes/edges.
- Knowledge-graph artifacts include `candidate_skill`/`installed_skill` nodes with `overlaps_with` and `same_job_candidate` edges for downstream analysis.
- `--merge-proposal` writes markdown patch plans under `artifacts/deconflict/proposals` (or `--merge-proposal-dir`).
- `--run-deconflict-benchmark` runs labeled benchmark pairs from `references/deconflict-benchmarks.json`.
- `--skill <name>` installs from `openai/skills/skills/.curated/<name>`.
- Requires a category when `--dest` is not provided.
- Installs into `~/dev/agent-skills/<category>/<skill-name>` by default.
- Destination precedence: `AGENT_SKILLS_HOME`, then `CODEX_HOME`, then `--dest`.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--category <category>`, `--method auto|download|git`, `--dry-run`, `--deconflict`, `--deconflict-threshold`, `--deconflict-block-threshold`, `--deconflict-engine`, `--deconflict-cache-path`, `--deconflict-artifact-path`, `--merge-proposal`, `--merge-proposal-dir`, `--run-deconflict-benchmark`, `--benchmark-file`.
- Security consent flag: `--force-unsafe` allows continuation when high-severity findings are detected.

## Notes

- Curated listing is fetched from `https://github.com/openai/skills/tree/main/skills/.curated` via the GitHub API. If it is unavailable, explain the error and exit.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- The skills at https://github.com/openai/skills/tree/main/skills/.system are preinstalled, so no need to help users install those. If they ask, just explain this. If they insist, you can download and overwrite.
- Installed annotations come from the destination folder (category or selected destination root).

## Example prompts
- "List the curated skills I can install."
- "Install the `frontend-design` skill from the curated list."
- "Install a skill from this GitHub repo path."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Validation
- Fail fast and report errors before proceeding.
- Confirm AskQuestion checkpoints were executed for overwrite/deconflict/warning decisions.
- For `--dry-run`, report source/risk summary and skip destination mutations/validation checks.
- Run required checks on each installed target:
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py <installed-skill-dir>`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <installed-skill-dir>`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <installed-skill-dir>`
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <installed-skill-dir> --mode both`
- For installs that actually write files (non-dry-run):
  - If the skill is **new** (not an overwrite/update), run evals:
  - `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py <installed-skill-dir>`
- Run deconflict benchmark before changing scoring logic:
  - `~/.venvs/pyyaml/bin/python utilities/skill-installer/scripts/install-skill-from-github.py --run-deconflict-benchmark`
- If critical findings exist, stop and ask for approval before enabling/using the skill.
- Keep `references/evals.yaml` security coverage: include at least one `category: negative`, one `category: pressure`, and deterministic forbidden-command checks for risky download, destructive shell, and exfiltration command families.
- For write flows, validate repository cleanliness after install plan execution:
  - `git status --porcelain` should be empty or match the expected installed-skill path allowlist.
- Confirm staged-to-final promotion details are reported:
  - include the staging directory path and whether staging validations passed before copy/move to destination.
- Verify decision-feedback protocol presence in each installed `SKILL.md`:
  - `rg -n \"decision-feedback-protocol:v2|Decision Quality Feedback|request_user_input\" <installed-skill-dir>/SKILL.md`

## Troubleshooting
- Error: destination already exists. Recovery: stop and request explicit overwrite confirmation before any mutation.
- Error: same failing step repeats 3 times. Recovery: stop retries, capture exact failing command/output, and present one safe fallback path.

## Procedure
1) Clarify scope and inputs.
2) Resolve staging boundary and run discovery + optional deconflict scan.
3) Use AskQuestion (`request_user_input`) for live decision gates.
4) Execute the selected install/merge workflow (stage -> validate -> promote).
5) Summarize outputs, ask for outcome feedback, and record it.

## Antipatterns
- Do not add features outside the agreed scope.
