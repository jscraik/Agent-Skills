---
name: oak-api
description: Build or adapt Oak Curriculum API learning experiences, especially child-facing Apps SDK flows. Use when the user wants Oak endpoints or curriculum data turned into guided learning interactions with age-appropriate guardrails.
metadata:
  skill-type: library_api_reference

---

# Oak API

Turn Oak Curriculum API content into age-appropriate learning flows, endpoint maps, or implementation guidance without losing compliance and learner-safety constraints.

## Standards snapshot (March 2026)
- Prioritize learner safety, age fit, and clarity before clever product mechanics.
- Treat Oak content as a factual backbone, not something to dump verbatim into the chat.
- Keep compliance explicit: attribution, rate limits, API-key handling, and no implied endorsement.
- Default to recommendations and flows first; move into code only when the user asks for implementation.

## Philosophy
- Learner safety and clarity outrank novelty.
- Use Oak as structured curriculum evidence, not as copy to repeat wholesale.
- Keep outputs actionable for tutors, parents, teachers, or app builders.

## When to use
- Designing learner-facing experiences from Oak Curriculum content.
- Mapping Oak subjects, units, lessons, quizzes, or search results into a learning flow.
- Answering endpoint, content-coverage, licensing, or usage-limit questions about Oak API.
- Adapting Oak data for child-facing ChatGPT Apps or similar interactive experiences.

## When not to use
- Building generic educational content that does not depend on Oak data.
- Returning large chunks of Oak material verbatim.
- Discussing unrelated API design with no Oak endpoint or curriculum context.

## Required inputs
- Age range and learner context.
- Subject, key stage, year group, or learning goal.
- Desired interaction style such as explain, practice, quiz, or project.
- Constraints such as time, materials, accessibility needs, or implementation target.

## Deliverables
- A step-by-step learning flow or endpoint-backed content map.
- Selected Oak endpoint groupings and lesson or unit identifiers when relevant.
- A compliance checklist including attribution and usage reminders.
- If requested, code or Apps SDK integration guidance.

## Constraints
- Redact API keys, tokens, and any sensitive learner or classroom details by default.
- Keep network usage explicit and limited to Oak API hosts when `scripts/oak_api_fetch.py` is used.
- Do not imply endorsement by Oak or omit the required licensing and rate-limit reminders.

## Required output markers
- Include a line beginning with `Age range:`
- Include a section titled `Step-by-step flow:`
- Include a section titled `Compliance checklist:`
- Include the exact attribution line:
  - `Contains public sector information licensed under the Open Government Licence v3.0`
- For endpoint mapping requests, include:
  - `List endpoints:`
  - `Unit endpoints:`
  - `Pagination: offset, limit`
  - `Rate limit: 1000 requests per hour per user.`

## Failure mode
- If age range or subject context is missing, stop and say: `Missing inputs: age range, key stage, subject.`
- If endpoint details are unclear, load the relevant references before answering.
- If the task drifts into implementation without compliance or age context, restore those constraints before proceeding.

## Workflow
1. Collect age range, subject, key stage, goals, and constraints.
2. Confirm learner-safety and no-PII boundaries.
3. Use list and search references to identify the right content sequence.
4. Select units, lessons, or quiz structures and turn them into explain -> practice -> check flows.
5. Adapt tone and pacing for the age band.
6. End with compliance reminders and optional implementation next steps.

## Compliance checklist
- Include the required OGL attribution statement.
- Respect the rate limit: `1000 requests per hour per user.`
- Do not imply Oak endorsement.
- Use API keys via environment variables and never log them.

## Tooling and references
- Load only the Oak references needed for the current request:
  - `references/api-overview.md`
  - `references/endpoints-overview.md`
  - `references/lists.md`
  - `references/lesson-data.md`
  - `references/unit-curriculum-data.md`
  - `references/quiz-questions.md`
  - `references/search.md`
  - `references/api-limits.md`
  - `references/terms.md`
  - `references/apps-sdk.md`
- Use `scripts/oak_api_fetch.py` when authenticated fetches are required.
- Use assets only when the task needs packaged Oak-specific visuals or supporting materials from `assets/`.

## Validation
- Verify age range, subject, and key-stage context are present.
- Verify compliance statements and rate-limit reminders are included.
- Verify endpoint claims come from the Oak reference files rather than memory.
- Fail fast at the first missing educational or compliance prerequisite.

## Anti-patterns
- Dumping Oak lesson content verbatim.
- Skipping age-appropriate framing.
- Inventing undocumented endpoints or parameters.
- Treating Oak content like unrestricted generic curriculum text.

## Examples
- Create a KS2 maths session on fractions using Oak lessons.
- Find a Year 7 computing unit and turn it into a 20-minute interactive flow.
- Map Oak quiz questions into an adaptive KS4 science practice loop.

## See Also

| Skill | When to use together |
|---|---|
| [[chatgpt-apps]] | Build a ChatGPT App that surfaces Oak curriculum content |
| [[mcp-builder]] | Expose Oak API as MCP tools for agent workflows |
| [[product-spec]] | Spec the learning experience before implementing |
| [[fixing-accessibility]] | Ensure Oak-powered UI meets accessibility requirements |

**Topic map:** [[backend-platform]]

## Remember
The best Oak output is structured, age-aware, compliant, and easy to turn into a real learning session.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
