---
name: llm-design-review
description: "Structure a multidisciplinary design review for LLM-powered products, producing actionable risks, fixes, and evidence gaps across UX, architecture, AI safety, and operations.. Use when Use this skill when the task matches its description and triggers.."
---

# LLM Design Review

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Structure a multidisciplinary design review for LLM-powered products, producing actionable risks, fixes, and evidence gaps across UX, architecture, AI safety, and operations.

## Guiding Questions (pre-review)
- What user segments, environments, and success metrics define “good”?
- What domain risks exist (high-stakes, regulated, minors, sensitive data)?
- What artifacts are available (flows, wireframes, system diagrams, prompts, evals)?
- What model(s), data sources, and tools are in scope?
- What launch timeline and constraints matter?

## Review Workflow (use in order)
1) Scope and risk tier
- Define surface (web, API), scope boundaries, and risk classification.
- Identify data types (PII, PHI, PCI) and policies that apply.

2) UX and interaction integrity
- Check user intent fit, mental models, transparency, feedback/control, errors.
- Validate trust cues, confidence messaging, and safe fallback paths.

3) System architecture and integration
- Verify modularity, tool boundaries, least privilege, and graceful degradation.
- Review latency, caching, context management, and scaling plans.

4) Model, prompt, and data strategy
- Confirm model choice vs. latency/cost/quality; avoid over-tuning.
- Ensure prompt/version control, structured tool calls, and context window plan.
- Require eval plan (gold sets, edge cases, red-team prompts).

5) Safety, security, privacy, compliance
- Apply OWASP LLM Top 10 mitigations (prompt injection, output handling).
- Check moderation, abuse handling, data retention, consent, RBAC, encryption.
- Map to NIST AI RMF/ISO 42001 where relevant.

6) MLOps and lifecycle governance
- Monitoring KPIs, logging/auditability, rollback strategy, and feedback loops.
- Define model update path and regression gates.

## Evidence Expectations
- Clear artifacts: journey map, architecture diagram, prompt inventory, eval plan.
- Explicit assumptions vs. confirmed findings.
- Risk register entries and owner/mitigation for high-severity issues.

## Output Format
- Context summary (1-3 bullets)
- Findings (ordered by severity): issue, user impact, evidence, recommendation
- Risks and mitigation plan (if applicable)
- Open questions / missing evidence
- Notable strengths (optional, 1-3 items)

## Trigger Examples
- Create a design review checklist for our LLM-powered support chatbot.
- Audit the UX and safety of our LLM feature that drafts legal emails.
- Run a multidisciplinary design review for an AI assistant: UX, architecture, prompts, safety, and MLOps.
- Evaluate our LLM product’s tool-calling design and prompt governance.

## Variation Rules
- Vary depth by scope (single flow vs. full product).
- Use stricter safety/detail for high-stakes domains.
- Avoid generic advice; anchor each finding to a user or system outcome.

## Anti-Patterns to Avoid
- Do not give generic AI advice without tying it to a specific user goal or system risk.
- Do not skip safety, privacy, or abuse considerations for “simple” features.
- Do not treat LLM outputs as trusted; require validation and safe handling.
- Do not recommend architecture changes without a migration or rollback path.

## Empowerment Principles
- Provide at least one low-effort fix and one strategic fix for high-severity items.
- Offer a clear “next best action” that unblocks the team.
- Ask for missing evidence or artifacts instead of guessing.

## References
- For detailed checklists, standards mapping, and extended guidance, open:
  `references/llm-design-review-framework.md`

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
