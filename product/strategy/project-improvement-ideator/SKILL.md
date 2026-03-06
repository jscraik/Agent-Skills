---
name: project-improvement-ideator
description: "Use when asked to generate and prioritize product or repository improvements: privately explore 100 pragmatic ideas, run a premortem, and return the 10 strongest opportunities with current-source-backed best-practice notes, implementation slices, and risk controls; do not use for bug fixing or generic brainstorming."
---

# Project Improvement Ideator

Use this skill to do wide-net, evidence-backed ideation that still lands on shippable recommendations.

- Check the GOLD industry standards guide in `~/.codex/AGENTS.override.md` when it exists; if it is missing, continue and note that assumption.
- When the user asks for “latest”, “current”, “best practice”, or an as-of date, verify current primary sources before final ranking.
- Keep outputs decision-oriented; do the expansive thinking internally and present only the strongest recommendations unless the user asks for the full pool.

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Core workflow](#core-workflow)
- [Scoring rubric](#scoring-rubric)
- [Gold-standard lenses](#gold-standard-lenses)
- [Output format](#output-format)
- [Guardrails](#guardrails)
- [References](#references)

## Scope and triggers
- Use when the user wants roadmap ideas, improvement prioritization, strategic feature proposals, or “what should we build next?” guidance for a product, repo, developer tool, AI app, or workflow.
- Use when the user wants breadth first, then disciplined convergence on the best opportunities.
- Do not use for bug triage, implementation execution, incident response, or open-ended brainstorming with no need to rank or narrow.

## Required inputs
- User request, repo/product context, and any relevant files/links.
- Intended audience: developers, operators, end users, buyers, or internal teams.
- Constraints: timeline, staffing, risk tolerance, platform boundaries, and whether “latest/current” verification is required.
- If context is missing, assume current repo state, keep assumptions explicit, and avoid pretending to know unretrieved external facts.

## Core workflow
1. **Frame the opportunity**
   - Clarify the system under review, target users, success criteria, and constraints.
   - If repo context exists, inspect it before ideating so proposals are grounded in actual architecture, workflows, and gaps.

2. **Run a freshness pass when needed**
   - If the user asks for “latest”, “best practice”, “modern”, or an as-of date, verify current primary sources first.
   - Prefer official docs, changelogs, standards bodies, and first-party product guidance over secondary commentary.
   - Stamp the exact check date in the output and separate sourced facts from inference.

3. **Do the premortem before ideation output**
   - Imagine the plan failed six months from now.
   - Identify what went wrong: false assumptions, adoption failures, integration friction, safety gaps, novelty theater, cost/latency blowups, weak differentiation, poor discoverability, brittle workflows, or missing feedback loops.
   - Convert the most plausible failure modes into selection filters so weak ideas are removed early.

4. **Generate 100 candidate ideas privately**
   - Generate a broad internal pool of 100 ideas before picking winners.
   - Cover multiple buckets, not just feature ideas: onboarding, UX, DX, automation, agentic workflows, security, observability, reliability, performance, governance, integrations, collaboration, monetization, and operational robustness.
   - Include both “small sharp wins” and “strategic wedges”, but reject moonshots with poor effort-to-value.
   - Do **not** dump all 100 ideas by default; use them as the divergence set for later ranking.

5. **Cluster, dedupe, and sharpen**
   - Merge overlapping ideas into clearer wedges.
   - Prefer ideas that create compounding leverage, not one-off novelty.
   - Rewrite vague ideas into concrete user-facing opportunities with a believable MVP slice.

6. **Score the best candidates**
   - Score each shortlisted idea on the rubric below.
   - Penalize ideas that require high coordination cost, fragile integrations, unclear ownership, or speculative user demand.
   - Use the premortem filters as a hard reality check before final ranking.

7. **Select the top 10**
   - Return the 10 strongest ideas, not 5.
   - Optimize for a mix of: user value, differentiation, feasibility, speed to first value, and long-term defensibility.
   - Prefer ideas that feel powerful to users while remaining pragmatic for a small team to pilot.

8. **Make the recommendations actionable**
   - For each winning idea, describe the user-visible magic, the enabling mechanism, the smallest credible implementation slice, and the main risk with mitigation.
   - Call out dependencies on current platform capabilities, approvals, unpublished assets, or policy constraints.

## Scoring rubric
Score shortlisted ideas from 1-5 on:
- **User value** — Does it materially improve the product for a clear user?
- **Strategic leverage** — Does it unlock compounding advantage, not just a one-off feature?
- **Feasibility** — Can a team plausibly deliver a meaningful slice without excessive complexity?
- **Time-to-value** — How quickly could users feel the benefit?
- **Reliability/safety uplift** — Does it improve trust, control, predictability, or robustness?
- **Differentiation** — Is it meaningfully more compelling than the obvious default competitors would build?
- **Confidence** — How grounded is the idea in repo evidence and current best practices?

Tie-breakers:
1. Lower complexity burden.
2. Better fit with the premortem-adjusted failure filters.
3. Clearer MVP path.

## Gold-standard lenses
Use these as idea filters, especially for AI, coding, apps, software, and developer workflows:
- **Eval-driven iteration** — Prefer ideas that can be measured with explicit success criteria, edge cases, and regression checks.
- **Start simple before going multi-agent** — Prefer single-agent or workflow designs first; only recommend multi-agent complexity when evals justify it.
- **Structured, typed system design** — Favor structured outputs, typed tool contracts, and narrow interfaces over freeform, brittle flows.
- **Human control for risky actions** — Ideas that perform writes, side effects, or sensitive access should preserve review/approval points.
- **Conversation-native UX** — Favor atomic actions, conversational entry, concise outputs, and discoverable prompts over dashboard bloat.
- **Production realism** — Prefer ideas that account for staging vs production, rate limits, tracing, latency, caching, cost, and failure handling.
- **Security posture** — Assume prompt injection, data leakage, and over-broad context/tool access are real risks; reward ideas that reduce attack surface.
- **Pragmatic delight** — Look for ideas that feel magical to users without requiring heroic engineering or brittle orchestration.

## Output format
Use this structure unless the user asks for a different format:

### `## Assumptions`
- Explicit assumptions about repo context, user goals, constraints, and missing inputs.

### `## Freshness check`
- Include only when current/modern/latest guidance matters.
- State exact verification date and list the primary sources checked.
- Separate sourced facts from inferences.

### `## Premortem`
- 5-10 concise bullets on why this plan could fail in six months.

### `## Premortem-adjusted selection filters`
- Short bullets describing how the failure analysis changed the ranking criteria.

### `## Top 10 (ranked)`
For each idea include:
1. **Title**
2. **Why it wins** — 1-2 sentences.
3. **User-visible magic** — what feels compelling or unusually valuable.
4. **Implementation slice** — 2-4 concrete bullets for an MVP or pilot.
5. **Key risk + mitigation** — one concise bullet.
6. **Score snapshot** — compact rubric summary.

### `## Score summary`
- Table or compact bullets with the final ranked ideas and scores.

### `## Reserve bench themes`
- Do not print all 100 ideas.
- Instead, show the major discarded clusters or near-miss themes so the user can see the breadth that was considered.

## Outputs
- A structured ranked response tailored to the request.
- Include `schema_version: 1` when the output is contract-bound or artifact-bound.
- Keep the internal 100-idea divergence private unless the user explicitly asks to inspect the full pool.

## Guardrails
- No new dependencies unless explicitly justified and low risk.
- Prefer incremental or staged rollouts; label large initiatives clearly.
- Avoid generic “add AI” or “add chatbot” ideas unless the mechanism and user value are unusually strong.
- Do not invent repo facts, market facts, or current platform capabilities.
- If “latest” matters, do not rely on memory alone; verify.
- Keep assumptions explicit, especially for dates, environments, platforms, and available integrations.
- Redact secrets, PII, and sensitive operational details.

## Constraints
- Avoid destructive operations and implementation work unless the user explicitly changes scope.
- Do not present unsourced “industry standard” claims as facts when freshness has not been checked.
- Prefer ideas with a believable MVP or pilot path over visionary but high-fragility concepts.
- Redact secrets, credentials, PII, and sensitive operational details by default.

## Validation
- Run relevant checks when updating this skill:
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/quick_validate.py product/strategy/project-improvement-ideator`
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/skill_gate.py product/strategy/project-improvement-ideator`
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/analyze_skill.py product/strategy/project-improvement-ideator`
  - `~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/openclaw_skill_guard.py product/strategy/project-improvement-ideator --mode both`
- Run evals when behavior or output structure changes materially.
- Fail fast and report validation errors before proceeding.

## Philosophy
- Think expansively in private and converge ruthlessly in public.
- Reward ideas that combine user-visible power with operational realism.
- Prefer evidence, tradeoffs, and selection discipline over novelty theater.

## Anti-patterns
- Do not stop after the first 10 ideas; always diverge broadly before ranking.
- Do not fill the list with vague “AI copilot”, “chatbot”, or dashboard ideas unless the mechanism and value are unusually concrete.
- Do not recommend multi-agent complexity, new dependencies, or heavy integrations without a strong ROI case.
- Do not confuse “interesting” with “worth shipping”.

## Examples
- “Give me the 10 best improvements for this developer tool, but only after you’ve considered a much broader idea pool.”
- “Do a six-month premortem on this roadmap and then give me the strongest product wedges grounded in current best practices.”
- “Rank the most compelling, pragmatic March 2026 upgrades for this AI app.”

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Asset preview: `assets/project-improvement-ideator.png`

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they do not constrain it. Use judgment, adapt to context, and push boundaries when appropriate.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
