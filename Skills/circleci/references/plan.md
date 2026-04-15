# CircleCI Skill Plan

## Objective
Build and validate a CircleCI skill that supports:
- migration from GitHub Actions to CircleCI,
- orchestration and test/deploy planning,
- security and secret-policy guidance,
- deployment, optimization, and developer toolkit support,
using current CircleCI documentation sources as of March 2026.

## Step 0 — Source evidence
- Confirmed CircleCI documentation references are present in:
  - `Infrastructure/references/raw-docs-md/docs-guides-getting-started-first-steps.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-migrate-migrating-from-github.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-orchestrate-workflows.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-toolkit-local-cli.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-deploy-deploy-to-aws.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-security-contexts.md`
  - `Infrastructure/references/raw-docs-md/docs-guides-security-security-overview.md`
  - `Infrastructure/references/raw-docs-md/docs-reference-configuration-reference.md`
- Confirmed crawl trace artifacts in:
  - `Infrastructure/references/cf-crawl/manual-run/start-response.json`
  - `Infrastructure/references/cf-crawl/manual-run/status-response.json`
  - `Infrastructure/references/cf-crawl/job_status_raw.json`
  - `Infrastructure/references/cf-crawl/job_status.txt`

## Step 1 — Skill instruction file
- Update `SKILL.md` to provide:
  - scope triggers,
  - input requirements,
  - evidence-backed workflow,
  - anti-patterns and validation expectations,
  - explicit `cf-crawl` and CLI usage guardrails.

## Step 2 — Behavioral contracts
- Replace placeholder `Infrastructure/references/contract.yaml` with concrete purpose, triggers, inputs, outputs, non-goals, risks, and examples.
- Replace placeholder `Infrastructure/references/evals.yaml` with at least:
  - explicit trigger,
  - implicit trigger,
  - contextual trigger,
  - negative controls,
  - edge-missing-inputs,
  - pressure bypass.

## Step 3 — Agent metadata
- Replace `agents/openai.yaml` with Codex OpenAI interface metadata for display and policy.
- Enable implicit invocation for natural-language migration questions.

## Step 4 — Verification and handoff
- Keep command verification optional unless explicitly requested by user in this task.
- Return concise completion summary with updated file list and rationale.
