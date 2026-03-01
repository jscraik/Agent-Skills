---
name: recent-code-bugfix
description: "Diagnose and fix a bug introduced by the current author within the last week. Use when a user asks for a proactive bugfix from their recent commits, asks to triage/fix issues caused by their own changes, or leaves the prompt empty. Don’t use when failures are unrelated to the author’s recent edits or there is no local git history. Outputs: root-cause summary, minimal fix, and targeted verification evidence. Success: root cause maps directly to the author’s own recent changes."
knowledge_graph_profile: references/task-profile.json
---

# Recent Code Bugfix

## Table of Contents
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Reference map](#reference-map)
- [Constraints and safety](#constraints-and-safety)
- [Principles](#principles)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)

## When to use
- **Primary triggers:**
  - User asks for a proactive bugfix from their recent commits.
  - User asks to triage/fix an issue likely introduced by their own recent changes.
  - Prompt is empty and a default “find recent author bug + fix” pass is needed.
- **Non-triggers (route elsewhere):**
  - Requests for broad refactors, performance tuning, or feature work.
  - Failures that cannot be traced to the current author’s commits from the last week.
  - Repositories without usable local git history.

## Inputs
- A local git repository in the current working directory.
- Author identity from `git config user.name` / `git config user.email`.
- Commits from the last week, with changed files.
- Optional local failure signals (test logs, lint output, runtime errors).

## Outputs
- Root-cause statement tied directly to the author’s recent edits.
- Minimal code changes needed to fix the qualifying bug.
- Verification evidence from the smallest relevant check.
- Brief final report describing scope, fix, and validation status.

## Reference map
- Output contract (`schema_version: "1.0"`): `references/contract.yaml`
- Evaluation cases: `references/evals.yaml`
- Build plan artifact: `references/plan.md`

## Constraints and safety
- Redact secrets, tokens, credentials, and PII from output and artifacts.
- Keep scope narrow: only touch files required for the qualifying fix.
- Do not add unrelated refactors, defensive hardening, or compatibility shims unless explicitly requested.
- If no bug can be directly attributed to the author’s last-week changes, stop and report “no qualifying bug found.”

## Principles
- **Attribution first:** A fix only qualifies if the root cause maps directly to the author’s own recent edits.
- **Smallest repro first:** Prefer the fastest focused failure signal over full-suite runs.
- **Minimal patching:** Fix the defect with the smallest safe change aligned to local conventions.
- **Fail-fast honesty:** Stop quickly when evidence is insufficient or failures are unrelated.

## Workflow

### 1) Establish the recent-change scope
- Determine current author via git config:
  - `git config user.name`
  - `git config user.email`
- If both are unavailable, infer from environment once; if still unknown, ask once.
- Identify recent authored commits and touched files:
  - `git log --since=1.week --author=<author> --name-only --pretty=format:%H`
- Focus subsequent analysis on files changed in these commits.
- If prompt is empty, proceed with this default scope automatically.

### 2) Find a concrete failure tied to recent changes
- Prefer existing local evidence first (failing test output, lint output, runtime traces).
- If none exists, run the smallest relevant verification touching scoped files (single test, file-level lint, or direct repro).
- Confirm causality: the failure must stem from author-owned edits in the one-week window.
- If only unrelated legacy failures appear, stop and report no qualifying bug.

### 3) Implement the fix
- Apply a minimal, convention-aligned patch.
- Update only files required to resolve the verified root cause.
- Avoid speculative hardening or unrelated cleanup.

### 4) Verify
- Run the smallest targeted validation that proves the fix.
- Capture the exact command and result.
- If verification cannot run, document what should run and why it was blocked.

### 5) Report
- Summarize:
  - qualifying root cause,
  - fix implemented,
  - verification executed (or blocked reason).
- Explicitly state how root cause maps to the author’s recent commits.

## Validation
Fail fast: if any gate fails, stop and report instead of continuing.

- Gate 1: Author and last-week scope established.
- Gate 2: Defect reproduced or evidenced within scoped files.
- Gate 3: Root cause linked directly to author’s recent edits.
- Gate 4: Targeted verification passed, or blocking reason documented.

## Anti-patterns
- ❌ Fixing unrelated or pre-existing bugs just because they are nearby.
- ❌ Running broad full-repo checks before a scoped signal.
- ❌ Bundling refactors with the bugfix.
- ❌ Claiming success without explicit attribution evidence.

## Examples
- Triggering prompt: "Find a bug I introduced this week and fix it."
- Triggering prompt: "Can you proactively triage and patch an issue from my recent commits?"
- Triggering prompt: "" (empty prompt)
- Non-triggering prompt: "Refactor this subsystem for readability."
- Non-triggering prompt: "Fix all flaky tests in the repository."

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
