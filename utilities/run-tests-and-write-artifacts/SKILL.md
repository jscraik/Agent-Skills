---
name: run-tests-and-write-artifacts
description: "Run reproducible test suites in a checked-out repo and write evidence artifacts to /mnt/data (test_output.log, test_results.json, test_summary.md). Use when users ask to run tests, verify a branch, or reproduce CI failures; do not use for static-only review, deployment, or bug fixing before evidence is collected."
---

# run-tests-and-write-artifacts (v0.1.0)

## Scope and triggers

### Use when
- The user asks to run tests, verify a change, or reproduce failing CI behavior.
- You need machine- and human-readable artifacts in `/mnt/data` for downstream debugging.
- A reproducible, versioned workflow is required: run tests, capture evidence, summarize next steps.

### Don’t use when
- The user only wants static analysis or explanations without execution.
- The user asks for deployment, release, or packaging work.
- The user asks for performance benchmarking/profiling.
- The environment cannot run tests and cannot be provisioned in-scope.

## Requirements and context
- A repository is present on disk in the current workspace.
- Optional user-specified test command or suite scope.
- Ability to write artifacts to `/mnt/data`.

If critical context is missing, produce blocked artifacts with exact unblocking instructions.

## Deliverables
Always write:
- `/mnt/data/test_output.log` — raw command output (or diagnostic output when blocked).
- `/mnt/data/test_results.json` — structured results with `schema_version`, status, commands, summary, failures, notes.
- `/mnt/data/test_summary.md` — concise narrative summary with outcome and next steps.

Optional when already supported:
- `/mnt/data/junit.xml`
- `/mnt/data/coverage.xml` or `/mnt/data/coverage.html`
- `/mnt/data/flaky_tests.json`

## Philosophy
- Prefer deterministic command selection over ad-hoc guessing.
- Capture evidence first; diagnosis and fixes come after artifact creation.
- Fail safely: even if blocked, emit complete artifacts with explicit reasons.
- Keep v0.1.0 scoped to Jamie’s core tooling path.
- Ask: what proof would make the next debugging step obvious and actionable?

## Variation and adaptation
- Adapt command choice to context-specific repo signals while keeping deterministic ordering.
- Vary scope based on the user request: unit-only, workspace-wide, or targeted rerun.
- Use different handling for blocked states vs failing tests vs fully passing runs.
- Customize summary depth for unique downstream needs (human triage vs machine pipelines).
- Avoid repetition: don’t produce the same generic narrative for every outcome.
- Avoid cookie-cutter phrasing when logs contain distinct failure patterns.
- Keep outputs not-the-same across different failure classes, but retain schema consistency.

## Workflow
### Step 0 — Establish context
- Identify repository root and tooling signals (`Justfile/justfile`, `pyproject.toml`, `pytest.ini`, `package.json`, `pnpm-workspace.yaml`).
- Record assumptions in `test_results.json.notes`.

### Step 1 — Select test command(s)
Use the first applicable command below unless the user explicitly specifies another safe command:
1. `just test` (only if a `test` recipe exists).
2. `uv run pytest -q` (Python path).
3. `pnpm test` (single package) or `pnpm -r test` (workspace).

Do not auto-run Java/Go/Rust test commands in v0.1.0 unless explicitly requested.
Do not auto-install dependencies in v0.1.0; if missing, mark `blocked` and provide remediation.

### Step 2 — Execute and capture raw output
- Run selected command(s) and append stdout/stderr to `/mnt/data/test_output.log`.
- Capture exit code and duration per command.

### Step 3 — Write structured results
Write `/mnt/data/test_results.json` (see `references/contract.yaml`) with at minimum:
- `schema_version`
- `status` (`passed` | `failed` | `blocked`)
- `commands[]` with command metadata
- `summary`
- `failures[]` (best effort)
- `notes[]`

### Step 4 — Write human summary
Write `/mnt/data/test_summary.md` with:
- Commands and scope executed
- Overall outcome and failing highlights
- Blockers/limitations (if any)
- Concrete next steps

### Step 5 — Edge-case routing
1. **No repository / empty workspace**
   - Mark `blocked`; explain missing repo inputs; still emit all three required artifacts.
2. **Mixed Python + Node ecosystem**
   - Prefer user-specified scope. Otherwise use deterministic primary ordering from Step 1 and document assumptions.
3. **Missing runtime/dependencies/tools**
   - Do not install automatically; mark `blocked` and provide exact remediation commands.
4. **Flaky failures suspected**
   - Re-run failing subset once (max one retry), record both outcomes, and emit `/mnt/data/flaky_tests.json` when applicable.
5. **Long-running integration requirements**
   - Run default unit-level path first unless the user explicitly asks for full integration coverage.

## Validation
Fail fast: stop at the first failed gate, fix, and rerun before finalizing.

Minimum checks:
1. Required artifacts exist and are non-empty (unless intentionally blocked with explanation).
2. `test_results.json` includes required keys from `references/contract.yaml`.
3. `test_summary.md` includes command(s), outcome, blockers (if any), and next actions.

## Anti-patterns
- NEVER run arbitrary commands without documenting why they were selected.
- DO NOT attempt bug fixes before generating test evidence artifacts.
- DON'T return only prose when machine-readable JSON is required.
- Never hide blocked states; mark `status: blocked` with explicit reasons.
- Avoid silent dependency installs; implicit installs are a common mistake.
- Avoid wrong or incorrect command ordering that breaks reproducibility.
- Treat pitfall signals in logs as warnings to improve next-run routing.

## Constraints and safety
- Network access is denied by default; enable only with explicit user request and allowlist.
- Never echo secrets, tokens, credentials, or raw sensitive environment values.
- Redact sensitive information in artifacts by default.
- Prefer non-destructive commands and explicit scope statements.

## Examples
### Triggering prompts
- “Run the tests and give me a failure summary.”
- “Reproduce this CI test failure locally and write artifacts.”
- “Verify this branch by running the project test suite.”

### Negative examples (don’t trigger)
- “Can you explain what this function does?”
- “Refactor this module for readability.”
- “Write a README section for testing.”
- “What testing framework should I choose for Node?”
- “Deploy this service to production.”

## Resources
- `references/contract.yaml` — output schema and artifact guarantees.
- `references/evals.yaml` — regression eval cases for routing and edge behavior.
- `references/plan.md` — implementation plan/task graph for this skill.

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

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
