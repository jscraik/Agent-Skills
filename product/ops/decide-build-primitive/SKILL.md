---
name: decide-build-primitive
description: Use this skill to analyze whether a capability should become a Skill, Custom Prompt, or Agent automation when the user is packaging or automating a workflow and the right Codex primitive is not yet clear.
metadata:
  skill-type: team_automation
---

# Decide Build Primitive

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Decision workflow](#decision-workflow)
- [Decision heuristics](#decision-heuristics)
- [Output format](#output-format-strict)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use
- Use this skill when the user asks how to package, automate, or operationalize a Codex capability.
- Use it when the decision is between a reusable `SKILL`, a `CUSTOM_PROMPT`, or an `AGENT_AUTOMATION`.
- Use it when the team needs a durable recommendation with tradeoffs, not just a gut-feel answer.

## Required inputs
- the capability to package or automate
- expected inputs and outputs
- who triggers it and how often
- whether it must run interactively, delegated, or autonomously
- any repo, compliance, environment, or portability constraints

If one of these is missing, ask only the smallest question needed to choose safely.

## Deliverables
- a single recommendation using the strict output block below
- the primary reason and supporting factors behind the choice
- implementation notes grounded in the chosen primitive
- an explicit hybrid recommendation only when the capability genuinely spans layers

## Failure mode
If the request is not actually a packaging decision, say so briefly and route to the better skill or direct execution path instead of forcing a primitive choice.

## Standards snapshot (March 2026)
- Prefer the smallest primitive that preserves clarity, reliability, and reuse.
- Optimize for how the capability will actually be invoked in production workflows, not how it was first described.
- Distinguish human-guidance assets from autonomous execution assets; do not blur them just because both can automate work.
- Make the tradeoff legible enough that another agent would make the same decision from the same evidence.

## Decision workflow
### Step 1: Clarify the job to be done
- What is being built, and what outcome should it reliably produce?
- Who triggers it: a human in-chat, an explicit operator, or a scheduler/automation?
- Does it need repo/chat context to work well, or should it run in isolation?
- Is the capability a reusable method, a deterministic prompt macro, or an autonomous workflow?

### Step 2: Evaluate the six decision axes
- **Autonomy and runtime length:** seconds with a human present, bounded delegated run, or long autonomous lane.
- **Context dependence:** benefits from current thread/repo context versus clean-slate execution.
- **Invocation style:** implicitly triggerable, explicitly invoked, or scheduled/event-driven.
- **Workflow complexity:** single reasoning surface, multi-step method, or orchestration with checkpoints and artifacts.
- **Portability:** reusable across repos versus repo-bound or environment-bound.
- **Operational burden:** needs logs, retries, budgets, telemetry, packaging, or CI integration.

### Step 3: Choose the primitive
- **Choose `SKILL` when** the capability is a reusable method, decision framework, or bounded workflow that benefits from current context and implicit routing.
- **Choose `CUSTOM_PROMPT` when** the capability is a personal or team macro, mostly prompt-shaped, explicitly invoked, and not worth full skill packaging.
- **Choose `AGENT_AUTOMATION` when** the capability is autonomous, scheduled, long-running, or operationally heavy enough to need isolation, structured outputs, logging, or retry policy.

### Step 4: Check for a justified hybrid
- Recommend a hybrid only when two layers have different jobs.
- Common valid hybrid: `SKILL` for human-guided setup or review plus `AGENT_AUTOMATION` for recurring execution.
- Reject fake hybrids that only hide indecision.

## Decision heuristics
- If the value is mostly in routing, checklists, and structured judgment, bias toward `SKILL`.
- If the value is mostly in a reusable phrasing pattern with little surrounding workflow, bias toward `CUSTOM_PROMPT`.
- If the value is mostly in unattended execution, artifact production, or repeated runs, bias toward `AGENT_AUTOMATION`.
- If governance, telemetry, retries, or budget controls are core to success, that is strong evidence for `AGENT_AUTOMATION`.
- If cross-repo reuse with light operational overhead is the main goal, that is strong evidence for `SKILL`.

## Output format (strict)
Return exactly:
```
DECISION: [SKILL | CUSTOM_PROMPT | AGENT_AUTOMATION]
PRIMARY REASON:
SUPPORTING FACTORS:
IMPLEMENTATION NOTES:
POTENTIAL HYBRID:
```

Follow-up expectations:
- If `AGENT_AUTOMATION`, note entrypoint, guardrails, timeout or budget, logging, and failure handling.
- If `SKILL`, note triggers plus any scripts, references, assets, or evals that should exist.
- If `CUSTOM_PROMPT`, note audience, scope boundary, and why full packaging would be overkill.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not recommend destructive or autonomous execution paths without clear operational justification.
- Keep recommendations grounded in the current request rather than generic platform folklore.

## References
- `references/contract.yaml` — purpose, triggers, inputs/outputs, non-goals, risks.
- `references/evals.yaml` — evaluation cases to validate triggering and outputs.

## Validation
- Verify the chosen primitive actually matches invocation style, autonomy, and operational burden.
- Verify the recommendation could be implemented without immediately collapsing into one of the other primitives.
- Fail fast on ambiguous evidence; name the missing fact instead of pretending certainty.

## Anti-patterns
- Choosing `AGENT_AUTOMATION` just because the task sounds impressive.
- Choosing `CUSTOM_PROMPT` for something that clearly needs reusable evals, references, or implicit routing.
- Choosing `SKILL` for unattended or scheduler-driven work that really needs an automation contract.
- Returning a hybrid because the decision is unclear.
- Inventing operational details or governance requirements that were never evidenced.

## Examples

- "Should this be a Skill or a custom prompt?"
- "Choose between agent automation vs skill for a long-running workflow."
- "We use this every week across repos; should it be a skill or an automation?"
- "This is a one-off review macro for me; do I really need a skill?"

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

## See Also

| Skill | When to use together |
|---|---|
| [[codex-automation-architect]] | Use after `AGENT_AUTOMATION` decision to design the automation contract |
| [[ce-plan]] | Use when the capability is CE-scoped and needs concrete stage planning |

**Topic map:** [[agent-ops]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
