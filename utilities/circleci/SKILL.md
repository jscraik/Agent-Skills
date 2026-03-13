---
name: circleci
description: "Use this skill when the user asks for CircleCI migration, orchestration, testing, deployment, optimization, security/secrets, config policy, integration, or developer toolkit guidance."
---

# CircleCI

## Working agreement
- Follow the repo's `AGENTS.md` (map, not a megadoc).
- For long runs, follow `~/.codex/instructions/shell-skills-compaction.md` if present.
- Artifact boundary:
  - Local CLI: `./artifacts/`
  - Hosted shell: `/mnt/data/`
- Keep outputs tied to verifiable references, not assumptions.

## Table of Contents
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Inputs](#inputs)
- [Reference sources](#reference-sources)
- [Reference sources and crawl evidence](#reference-sources-and-crawl-evidence)
- [Reference workflow](#reference-workflow)
- [Outputs](#outputs)
- [Workflow](#workflow)
- [Decision quality standards](#decision-quality-standards)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)

## When to use
- Primary triggers:
  - User asks to migrate CI from GitHub Actions to CircleCI.
  - User asks for CircleCI migration planning, comparison, or risk controls.
  - User asks for workflow orchestration, testing strategy, deployment gates, policy, or security guidance.
  - User asks for CircleCI `/.circleci/config.yml` gold-standard patterns and review checklists.
  - User asks for CircleCI CLI/tooling guidance, including install and local validation.
- Non-triggers (route elsewhere):
  - Generic one-off troubleshooting of a single job or pipeline artifact with no strategy ask.
  - VCS-only questions not tied to CircleCI process design.
  - UI/browser automation requests (use `agent-browser`).

## Inputs
- Required:
  - Project context: repository shape, branch model, compliance expectations, deployment targets.
  - Scope: `migrate`, `orchestrate`, `testing`, `deploy`, `optimize`, `security`, `config_policy`, `integration`, `toolkit`, `howto`, or `gold_standard`.
  - Desired output mode: `advice`, `migration_plan`, `checklist`, or `reference_pack`.
- Optional:
  - Existing `/.circleci/config.yml`.
  - Evidence URLs already available in the repository.
  - CI provider constraints (parallelism, budget, approval requirements).
- Ask for clarifying input when missing:
  - environments and release ownership,
  - approval model,
  - rollback and incident response requirements.

## Reference sources
- `references/raw-docs-md/docs-guides-getting-started-first-steps.md` (bootstrap flow).
- `references/raw-docs-md/docs-guides-migrate-migrating-from-github.md` (migration path).
- `references/raw-docs-md/docs-guides-orchestrate-workflows.md` (orchestration).
- `references/raw-docs-md/docs-guides-toolkit-local-cli.md` (CircleCI CLI).
- `references/raw-docs-md/docs-guides-deploy-deploy-to-aws.md` (deployment examples).
- `references/raw-docs-md/docs-guides-security-contexts.md` (contexts and secret control).
- `references/raw-docs-md/docs-guides-security-security-overview.md` (security posture).
- `references/raw-docs-md/docs-reference-configuration-reference.md` (official config key reference).
- `references/raw-docs-md/docs-guides.md` (index anchor).

## Reference sources and crawl evidence
- This skill ships with CircleCI documentation snapshots under `references/raw-docs-md/`.
- Crawl artifacts:
  - `references/cf-crawl/job_status_raw.json`
  - `references/cf-crawl/job_status.txt`
  - `references/cf-crawl/manual-run/start-response.json`
  - `references/cf-crawl/manual-run/status-response.json`
- Use these for traceability if a recommendation references newly added or updated pages.
- Local env for running/refreshing crawl jobs: `~/.codex/.env` (not `~/.codex.env`).

## Reference workflow
1. Use local markdown references as primary source.
2. If a requested topic is missing or stale, run/refine via `$cf-crawl` with bounded scope.
3. Confirm source file, section, and publish timestamp before making normative guidance.
4. Produce recommendations using verifiable references and explicit caveats.
5. Preserve artifact trail in the `artifacts/` output.

## Outputs
- `artifacts/circleci-migration-plan.md`  
  Phase-by-phase migration plan from discovery to enforce.
- `artifacts/circleci-gold-standard.md`  
  Standards pack for jobs, workflows, security, policy, and rollout.
- `artifacts/circleci-decision-matrix.md`  
  Mapping for orchestrate/testing/deploy/security/policy decisions and owners.
- Always include:
  - source anchors,
  - risk and blast radius,
  - rollout gate criteria,
  - owner assignments and follow-up checks.

## Workflow
1. Parse scope (`migrate`, `orchestrate`, `testing`, `deploy`, `optimize`, `security`, `config_policy`, `integration`, `toolkit`, `howto`, `gold_standard`).
2. Build an evidence pack from local references and cite URL source + crawl status.
3. Produce one of these concrete outputs:
   - `migration_plan`: phase plan with validation gates.
   - `gold_standard`: reusable checklist for a project.
   - `reference_pack`: source index for immediate implementation use.
4. Enforce CircleCI best practices from references:
   - explicit workflow ordering and `requires`,
   - branch-based rollout controls,
   - approval/manual gate for release production,
   - contexts for secrets and sensitive vars,
   - deployment promotion with rollback path.
5. Return: artifact path, what changed, what remains blocked, and next action.

## Decision quality standards
- Default to behavior-preserving migration (reduce risk, not just config parity).
- Include at least one test gate and one deploy gate for every deployment proposal.
- Include contexts + restricted access patterns for secret and integration design.
- Flag optimization recommendations using concrete techniques (parallelism, caching, fan-in/out).
- Include config-policy checks and policy-as-code checks when policy is in scope.

## Discovery interview
- Ask one round at a time; do not move to the next step until the user answers the current question.
- Ask in plain-language questions, for example: “What should this skill help you do?”
- Explain why the round matters before the next question.
- Avoid dumping the whole interview plan at once.

## Validation
- If required inputs are missing, ask clarifying questions before producing a fabrication.
- Validate recommendations against local reference evidence (or refreshed `cf-crawl` output).
- For config topics, include at least one explicit recommendation to run:
  - `circleci config validate`
  - `circleci setup` (when onboarding a local shell)
  - `brew install circleci` (tooling bootstrap guidance when asked)
- If `CIRCLECI_API_TOKEN` is required for a live action, confirm safe handling and never print raw token.
- Fail-fast policy: stop at the first unresolved failed validation gate and do not proceed until it is fixed.

## Philosophy
- Prioritize safe migration over maximal optimization: keep existing release behavior stable while introducing stronger controls.
- Choose deterministic, auditable workflows over ad-hoc suggestions, and call out assumptions explicitly when evidence is missing.
- Never provide unsafe or policy-violating instructions; prefer a conservative recommendation when inputs are incomplete.

## Variation
- Favor multiple valid implementation options, chosen by project context instead of a one-size-fits-all template.
- Adapt workflow patterns based on branch model, team maturity, and risk appetite, and reject accidental template lock-in.
- When the same prompt arrives from different teams, choose options that reflect their actual constraints before finalizing a recommendation.

## Empowerment
- The agent should use judgment: if an explicit requirement is missing, ask one focused clarifying question, then proceed safely.
- These instructions are a guardrail for reliable outcomes, not a ceiling on solution quality—adapt and improve where the project context demands it.
- Help unlock the best migration path for each repo by enabling practical trade-offs and creative adaptation when evidence permits.
## Empowerment closing note
- You are capable and empowered to deliver strong, project-specific CircleCI migrations from this scaffold. Use these rules as a safe baseline, then enable practical judgment and local context to deliver the best path for the repo.

## Constraints
- This skill only scopes to CircleCI migration and pipeline-architecture guidance.
- It must not include browser automation, low-level host hardening, or vendor-agnostic infrastructure execution outside CircleCI workflow design.
- It must ask for missing deployment context (target environments, approval model, incident response, and rollback policy) before returning prescriptive production plans.
- It must use repository-local references and crawl artifacts from `references/raw-docs-md` / `references/cf-crawl` as the primary evidence source for recommendations.
- It must treat security-sensitive instructions as a hard-blocking concern unless explicit approval constraints are present.

## Anti-patterns
- ❌ Migrating without repository scope and approval model.
- ❌ Deploying to production without pre-merge verification gates.
- ❌ Hardcoding or committing secrets; avoid project-level plain env var leakage.
- ❌ Ignoring rollback and incident recovery in deployment guidance.
- ❌ Ignoring user safeguards by skipping required safety checks when asked to skip validation.

## Validation policy
- Fail fast on blocker: if required context is missing for deployment scope, policy, or security boundaries, stop and ask clarifying questions first.
- Validation checks are ordered for quick failure:
  1. required inputs present
  2. safety and policy constraints acknowledged
  3. migration/workflow recommendation with gates
  4. evidence-backed commands and artifact plan

## Examples
- "Migrate from GitHub Actions to CircleCI with release approvals and policy checks."
- "How should I set up orchestrate + test workflows for a monorepo?"
- "What is the CircleCI best-practice pattern for secure secrets and integration control?"
- "How do I install CircleCI CLI and run local validation?"
