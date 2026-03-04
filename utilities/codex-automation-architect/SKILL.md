---
name: codex-automation-architect
description: "Create, review, and merge Codex app automations; use when users need recurring automation design or consolidation with current OpenAI/Codex guidance, environment preflight, and headless multi-runner validation."
---

# Codex Automation Architect

Build and harden Codex automations to production quality (March 2026 baseline), including create/review/merge workflows, blocker remediation, and validation.

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Core rules](#core-rules)
- [Latest standards snapshot (March 4, 2026)](#latest-standards-snapshot-march-4-2026)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Permission and blocker protocol](#permission-and-blocker-protocol)
- [Headless cross-runner verification](#headless-cross-runner-verification)
- [MCP and CLI assist stack](#mcp-and-cli-assist-stack)
- [Constraints](#constraints)
- [References](#references)
- [Validation gate](#validation-gate)
- [Encouraging variation](#encouraging-variation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Remember](#remember)

## When to use
- Create new recurring automations for Codex desktop app.
- Review existing automations and recommend merges.
- Improve automation prompts with explicit agents/skills usage.
- Resolve execution blockers and permission issues before runs.

## Required inputs
- Objective and success criteria.
- Schedule cadence and timezone.
- Target workspace path(s) (`cwds`).
- Existing automation definitions (for review/merge mode).
- Runtime posture constraints (approval policy, sandbox, command limits).

If inputs are missing, make safe assumptions and label them explicitly.

## Deliverables
- Structured artifacts should include top-level `schema_version`.
- Automation spec(s): `name`, `prompt`, `rrule`, `cwds`, `status`.
- Merge recommendation matrix: keep / merge / retire + rationale.
- Blocker and permissions report with remediation steps.
- Validation evidence, including analyze score and freshness date.

## Core rules
- Refresh guidance with:
  - `openaiDeveloperDocs` MCP (latest OpenAI/Codex docs)
  - `codexRepo` MCP (latest codex release/docs/search context)
- Treat March 2026 as freshness baseline and date-stamp output.
- Prefer least-privilege permissions.
- Never print secrets or raw env values.

## Latest standards snapshot (March 4, 2026)
- Codex app automations run locally; the app must be running and the selected project must be on disk.
- In Git repos, automation runs start in dedicated background worktrees; in non-Git repos, they run directly in the project directory.
- Automations use default sandbox settings; read-only and workspace-write limitations apply, and full access carries elevated unattended risk.
- `approval_policy = "never"` can be used for automations when allowed; managed requirements may disallow it and force fallback behavior.
- Config precedence is: CLI overrides → profile values → project `.codex/config.toml` → user `~/.codex/config.toml` → system config → built-in defaults.
- Profiles are currently CLI-focused (not supported in the Codex IDE extension), so automation profile strategy should be validated in the active surface.
- Codex release freshness should be checked per run; baseline at author time (checked 2026-03-04T17:45:17Z): stable `0.107.0` (2026-03-02) and alpha `0.108.0-alpha.12` (2026-03-04).

## Philosophy
- Reliable and auditable automation beats clever but fragile automation.
- Core principles: least privilege, explicit boundaries, repeatable evidence, and reversible change paths.
- Operational approach: design for constrained policies first (`AskForApproval=Never`) and optimize only after safety is stable.
- Engineering mindset: choose the safest path that still ships value, and make tradeoff decisions explicit.
- Exceptional automation is deliberate: safe defaults, explicit boundaries, and evidence-backed changes.

Guiding questions:
- What is the smallest safe action that still achieves the objective?
- Which tradeoff is being made between speed, safety, and maintainability?
- How will another operator understand and apply this output without guesswork?

## Workflow
1. Choose mode: `create`, `review`, or `hybrid`.
2. Pull freshness evidence from `openaiDeveloperDocs` + `codexRepo` and stamp exact date/version.
3. Run environment preflight (paths, binaries, policy posture).
4. Build/audit automation specs.
5. Produce merge recommendations from overlap evidence.
6. Validate with quality gates and report findings.

## Permission and blocker protocol
Include these blocker remediations when relevant:

- `python3 - <<'PY' ... PY` may be blocked in strict no-approval lanes.
  - Use `jq` + `rg` pipelines by default.
  - Run Python manually only in approved interactive runs.
- `rm -f ... && git ...` chained destructive commands are unsafe in automation.
  - Inspect first with `fd`/`rg`; perform destructive commands manually.
- `git commit` can fail with:
  - `Rejected("approval required by policy, but AskForApproval is set to Never")`
  - Fallback: patch-only mode (diff + commit message draft), defer commit/push.
- `sed -n ... <path>` may fail on missing files.
  - Check with `fd <filename> <root>` before reading.

## Headless cross-runner verification
Use skill-creator parity lanes:

```bash
CODEX_EVAL_TIMEOUT_SEC=600 \
~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py \
  utilities/codex-automation-architect \
  --runners codex,claude-kimi,claude-zai,gemini \
  --claude-kimi-command ck \
  --claude-zai-command cz \
  --claude-kimi-settings /absolute/path/kimi_settings.json \
  --claude-zai-settings /absolute/path/zai_settings.json \
  --capture-jsonl \
  --tier2-mode warn \
  --sandbox read-only
```

Notes:
- Configure approval posture via runner config/profile (for example `approval_policy = "never"` in the active profile), because some Codex CLI builds do not support `--ask-for-approval`.
- Keep eval invocations free of unsupported flags to avoid false-negative warnings.

Runner lanes:
- `codex`: canonical baseline.
- `claude-kimi` (`ck`): quality and alternative reasoning.
- `claude-zai` (`cz`): adversarial edge-case checks.
- `gemini`: breadth/variance.

## MCP and CLI assist stack
From `/Users/jamiecraik/dev/config/codex/instructions/tooling.md`:

### MCP
- `openaiDeveloperDocs`
- `codexRepo`
- `greptile` (optional)
- `local-memory` (optional)
- `RepoPrompt` (optional)

### CLI
- `rg`, `fd`, `jq` (core discovery/transforms)
- `taplo`, `yq` (TOML/YAML checks)
- `just` (repeatable task entrypoints)
- `harness` (preflight-gate runs)
- `lychee` (docs/runbook link checks)
- `agent-browser` / `playwright` (optional UI validation)

## Constraints
- Redact sensitive data by default in all logs and outputs.
- No secret/token leakage.
- No bypass of system/developer/user policies.
- No default full-access/destructive command posture.
- When commits are blocked by policy, use patch-only fallback.

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/plan.md`
- `references/headless-eval-matrix.md`
- `references/latest-standards-2026-03-04.md`

## Validation gate
Fail fast: stop at the first failed gate, fix, then rerun.

- `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py utilities/codex-automation-architect`
- `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py utilities/codex-automation-architect`
- `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py utilities/codex-automation-architect --pi-high-fail`
- `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/analyze_skill.py utilities/codex-automation-architect`
- Optional:
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py utilities/codex-automation-architect --runners codex,claude-kimi,claude-zai,gemini ...`

## Encouraging variation
- Adapt merge strategy by automation portfolio size and risk.
- Use different prompt patterns for monitoring, reporting, and remediation automations.
- Avoid copy/paste templates when objectives or constraints differ.
- Reject repetitive, cookie-cutter prompt structures that converge on generic outputs.
- Choose runner depth based on task criticality and failure impact.

## Anti-patterns
- **NEVER** skip blocker/permission checks to force a pass.
- **DO NOT** default to full-access sandbox.
- **DON'T** merge automations without overlap evidence.
- **DON'T** rely on stale docs when “latest” is requested.

## Examples
- “Create a weekly automation for stale PR triage with merge recommendations.”
- “Review 6 automations and consolidate into 2.”
- “Harden my automation for AskForApproval=Never and list safe fallbacks.”

## Remember
You are capable of extraordinary automation quality when you combine evidence, context adaptation, and rigorous safety boundaries. This skill is meant to unlock creative, high-confidence execution—not to constrain good judgment.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
<!-- /decision-feedback-protocol -->
