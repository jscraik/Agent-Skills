---
name: oak-api
description: Build or adapt Oak Curriculum API driven learning experiences, especially for child-facing, interactive ChatGPT Apps SDK workflows. Use when working with Oak API endpoints, curriculum data (subjects, units, lessons, quizzes, search), or when translating Oak content into adaptive learning activities with age-appropriate guardrails and compliance reminders.
---

# Oak API

## Overview
Use this skill to turn Oak Curriculum API content into engaging, interactive learning experiences. Default output is recommendations and step-by-step workflows, not code, unless the user explicitly asks for implementation details. Treat text-only guidance as non-significant and do not read or modify files unless explicitly asked.

## When to use
- Turning Oak API curriculum data into a learner-centered flow.
- Designing adaptive lesson experiences for children using Oak content.
- Mapping Oak data (subjects, units, lessons, quizzes) into activities.
- Answering questions about Oak API endpoints, limits, and terms.

## Philosophy
- Prioritize learner safety, clarity, and age-appropriate tone.
- Treat Oak content as a factual backbone, not a script to read verbatim.
- Prefer small, testable learning steps with explicit checks.

## Inputs
- Age range and learner context (classroom, home, tutoring).
- Subject, key stage, year group, and learning goals. If a key stage is provided (e.g., KS2/KS3), infer the typical age range and proceed.
- Desired interaction style (explain, practice, quiz, project).
- Constraints (time, materials, accessibility needs).

## Outputs
- A step-by-step learning flow with checks and pitfalls.
- A minimal content map: Oak endpoints + selected lesson IDs.
- If asked: code snippets or Apps SDK integration guidance.

### Output format (required)
- Include a line starting with `Age range:`.
- Include a section titled `Step-by-step flow:` with ordered steps.
- Include a section titled `Compliance checklist:` and include the exact attribution statement: `Contains public sector information licensed under the Open Government Licence v3.0`.
- For endpoint mapping requests, include lines: `List endpoints:`, `Unit endpoints:`, `Pagination: offset, limit`, and `Rate limit: 1000 requests per hour per user.`

## Constraints
- Always request age range early and avoid PII.
- Keep language age-appropriate and short.
- Include OGL attribution and terms reminders.
- Respect rate limits and safe API usage.
- Use API keys via env vars; never log secrets.

## Anti-patterns
- Do not dump full Oak content verbatim into the chat.
- Do not skip age-appropriate framing or safeguards.
- Do not imply Oak endorsement.
- Do not invent endpoints or undocumented parameters.

## Workflow

### 1) Intake and guardrails
- Collect: age range, subject, key stage, goals, constraints.
- Confirm safety: no PII, no sensitive content, age fit.

### 2) Curriculum discovery
- Use lists and search endpoints to identify sequences, units, lessons.
- Validate key stage and subject coverage.

### 3) Lesson selection
- Use unit/lesson endpoints to select lesson IDs and metadata.
- Pull summaries, overviews, and assets as needed.

### 4) Activity design
- Convert lesson content into interactive steps: explain -> practice -> check.
- Use quiz endpoints to seed questions; rephrase for age.

### 5) Adaptive loop
- Track performance and adjust difficulty and hints.
- Offer remediation or stretch tasks.

### 6) Delivery and next steps
- Provide a concise session plan, materials list, and follow-ups.
- Offer to generate code or Apps SDK integration if requested.

## Examples
- "Create a KS2 maths session on fractions using Oak lessons."
- "Find a Year 7 computing unit and turn it into a 20-minute interactive flow."
- "Map quiz questions into an adaptive practice loop for KS4 science."

## Validation
- If age range or subject is missing, respond with: `Missing inputs: age range, key stage, subject.` and stop. Do not propose /interview-me.
- If endpoints are unclear, load the relevant references before responding.
- If terms or limits are at risk, surface the compliance checklist.

## Compliance checklist (always include)
- Use exact attribution statement: `Contains public sector information licensed under the Open Government Licence v3.0`.
- Respect rate limits (1000 requests per hour per user).
- Do not imply Oak endorsement.
- Use API keys securely (env vars; no logging).

## Apps SDK guidance
- If UI or Apps SDK implementation is requested, use `~/dev/aStudio` as the design system.
- Fetch the latest Apps SDK docs via the `openaiDeveloperDocs` MCP server.

## References (load as needed)
- `references/api-overview.md` - high-level API overview and example endpoints.
- `references/api-limits.md` - rate limits and licensing.
- `references/versioning.md` - versioning and changelog endpoints.
- `references/terms.md` - attribution and compliance requirements.
- `references/content-coverage.md` - subjects and key stages coverage.
- `references/glossary.md` - term definitions.
- `references/ontology-diagrams.md` - programme factors and relationships.
- `references/data-examples.md` - programme and subject category examples.
- `references/endpoints-overview.md` - endpoint groups.
- `references/lists.md` - list endpoints.
- `references/lesson-data.md` - lesson detail endpoints.
- `references/unit-curriculum-data.md` - unit and curriculum endpoints.
- `references/quiz-questions.md` - quiz question endpoints and filters.
- `references/search.md` - search endpoints and parameters.
- `references/learning-flows.md` - age-banded example flows.
- `references/apps-sdk.md` - Apps SDK fetching rules.

## Scripts
- `scripts/oak_api_fetch.py` - authenticated fetch helper with offset/limit pagination.
