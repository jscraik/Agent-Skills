# Session Evidence Workflow

Read when: a skill-refactor run needs past-session evidence before recommending skill installs, improvements, merges, or pruning.

This workflow folds the useful session-history pattern into `skill-refactor` without creating a separate user-facing session router. It keeps raw transcripts out of context and treats session evidence as input to skill reliability analysis, not as the final answer.

## Ownership

- `skill-refactor` owns session inventory, bounded extraction, correlation, and recommendations about skill health.
- `skillify` may consume extracted workflow evidence when converting a completed run into a reusable skill.
- Harness Engineering may reference `skill-refactor` or `skillify` when past sessions are useful, but it should not own generic session-history plumbing.

## Flow

1. Define the evidence question.
   - Skill reliability: "Which skills failed, undertriggered, or duplicated work?"
   - Skill creation: "Which repeated workflow should be captured by `skillify`?"
   - Harness Engineering: "Which past solved evidence helps route or document this lifecycle stage?"
2. Inventory before extraction when more than one session may matter.
   - Prefer existing local collectors or deterministic scripts.
   - Capture metadata such as platform, session id, timestamp, repo/cwd, branch when available, size, and last activity.
   - Keep absolute file paths in local artifacts only; user-facing summaries should cite artifact labels or redacted basenames unless the user asks for exact local paths.
3. Select a small deep-dive set.
   - Choose sessions by repo/cwd, branch, recency, repeated skill names, or explicit error signals.
   - Avoid opening every large JSONL file directly.
4. Extract bounded evidence from selected sessions.
   - Use skeleton mode for user intent, assistant decisions, and compact tool-call summaries.
   - Use errors mode for non-zero exits, stderr, missing files, frontmatter failures, validation failures, and permission blockers.
   - Preserve raw extracted snippets in local artifacts when useful, but redact secrets and private account identifiers before summaries.
5. Correlate and decide.
   - Map evidence to one root cause class: coverage gap, instruction drift, routing mismatch, quality regression, missing validation, or environment blocker.
   - Prefer one root-cause fix when it explains multiple session symptoms.
   - Separate "improve existing skill" from "skillify a repeated workflow" and "Harness Engineering lifecycle evidence."

## Output Shape

Use this concise structure for recommendations:

```text
schema_version: 1
mode: session-evidence
scope: <single-skill|category|full-inventory|workflow-capture>
evidence:
  - label: <redacted artifact/session label>
    signal: <skeleton|errors|metadata|collector-summary>
    summary: <one sentence>
findings:
  - severity: <high|medium|low>
    root_cause: <coverage-gap|instruction-drift|routing-mismatch|quality-regression|missing-validation|environment-blocker>
    recommendation: <keep|improve|merge|retire|skillify|route-to-he>
    evidence_labels: [...]
validation_evidence:
  - <command or artifact checked>
```

## Privacy Rules

- Do not paste raw transcripts, full tool outputs, API keys, tokens, secrets, private account identifiers, or unrelated personal content into skill artifacts.
- Do not encode the user's local file tree into public skill examples.
- When a local path is required for operator action, keep it in the run summary or local artifact, not in reusable public guidance.
- If extraction would send local session excerpts to an external model or service, stop and ask for explicit approval.

## Hand Offs

- Hand off to `skillify` when the evidence shows a repeated workflow that should become a reusable `SKILL.md` package.
- Hand off to Harness Engineering only when the evidence is about lifecycle stage routing or verified solved-problem capture.
- Stay in `skill-refactor` when the question is skill reliability, coverage, merge/prune decisions, or routing quality.
