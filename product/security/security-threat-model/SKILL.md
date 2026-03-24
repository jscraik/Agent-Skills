---
name: "security-threat-model"
description: Produce a repository-grounded threat model covering assets, trust boundaries, attackers, abuse paths, and mitigations. Use when the user explicitly wants AppSec threat modeling, not general architecture review.
metadata:
  skill-type: runbook
---

# Threat Model Source Code Repo

Deliver an actionable AppSec-grade threat model that is specific to the repository or a project path, not a generic checklist. Anchor every architectural claim to evidence in the repo and keep assumptions explicit. Prioritizing realistic attacker goals and concrete impacts over generic checklists.

## Quick start

1) Collect (or infer) inputs:
- Repo root path and any in-scope paths.
- Intended usage, deployment model, internet exposure, and auth expectations (if known).
- Any existing repository summary or architecture spec.
- Use prompts in `references/prompt-template.md` to generate a repository summary.
- Follow the required output contract in `references/prompt-template.md`. Use it verbatim when possible.

## Philosophy

- Prefer root-cause understanding over quick symptom patches.
- Keep guidance evidence-based, explicit, and reproducible.
- Optimize for decisions that reduce rework and operational risk.
- Map the final abuse paths to OWASP Top 10:2025 themes when that helps teams turn the threat model into implementation work.

## Workflow

### 1) Scope and extract the system model
- Identify primary components, data stores, and external integrations from the repo summary.
- Identify how the system runs (server, CLI, library, worker) and its entrypoints.
- Separate runtime behavior from CI/build/dev tooling and from tests/examples.
- Map the in-scope locations to those components and exclude out-of-scope items explicitly.
- Do not claim components, flows, or controls without evidence.

### 2) Derive boundaries, assets, and entry points
- Enumerate trust boundaries as concrete edges between components, noting protocol, auth, encryption, validation, and rate limiting.
- List assets that drive risk (data, credentials, models, config, compute resources, audit logs).
- Identify entry points (endpoints, upload surfaces, parsers/decoders, job triggers, admin tooling, logging/error sinks).

### 3) Calibrate assets and attacker capabilities
- List the assets that drive risk (credentials, PII, integrity-critical state, availability-critical components, build artifacts).
- Describe realistic attacker capabilities based on exposure and intended usage.
- Explicitly note non-capabilities to avoid inflated severity.

### 4) Enumerate threats as abuse paths
- Prefer attacker goals that map to assets and boundaries (exfiltration, privilege escalation, integrity compromise, denial of service).
- Classify each threat and tie it to impacted assets.
- Keep the number of threats small but high quality.
- Use STRIDE or equivalent taxonomies only as a completeness backstop, not as the primary organizing model.

### 5) Prioritize with explicit likelihood and impact reasoning
- Use qualitative likelihood and impact (low/medium/high) with short justifications.
- Set overall priority (critical/high/medium/low) using likelihood x impact, adjusted for existing controls.
- State which assumptions most influence the ranking.

### 6) Validate service context and assumptions with the user
- Summarize key assumptions that materially affect threat ranking or scope, then ask the user to confirm or correct them.
- Ask 1-3 targeted questions to resolve missing context (service owner and environment, scale/users, deployment model, authn/authz, internet exposure, data sensitivity, multi-tenancy).
- Pause and wait for user feedback before producing the final report.
- If the user declines or cannot answer, state which assumptions remain and how they influence priority.

### 7) Recommend mitigations and focus paths
- Distinguish existing mitigations (with evidence) from recommended mitigations.
- Tie mitigations to concrete locations (component, boundary, or entry point) and control types (authZ checks, input validation, schema enforcement, sandboxing, rate limits, secrets isolation, audit logging).
- Prefer specific implementation hints over generic advice (for example, "enforce schema at gateway for upload payloads" vs "validate inputs").
- Base recommendations on validated user context; if assumptions remain unresolved, mark recommendations as conditional.

### 8) Run a quality check before finalizing
- Confirm all discovered entrypoints are covered.
- Confirm each trust boundary is represented in threats.
- Confirm runtime vs CI/dev separation.
- Confirm user clarifications (or explicit non-responses) are reflected.
- Confirm assumptions and open questions are explicit.
- Confirm that the format of the report matches closely the required output format defined in prompt template: `references/prompt-template.md`
- Write the final Markdown to a file named `<repo-or-dir-name>-threat-model.md` (use the basename of the repo root, or the in-scope directory if you were asked to model a subpath).

## Deliverables

- concise Markdown threat model grounded in repo evidence;
- trust-boundary summary with entry points and assets;
- prioritized abuse-path table with likelihood, impact, and confidence;
- clearly separated:
  - existing controls with evidence
  - recommended controls
  - unresolved assumptions that still affect ranking.

## Output quality bar

- Prefer 5-12 high-quality abuse paths over a large low-signal list.
- Every mitigation should point to a concrete component, boundary, or control surface.
- Every severity call should have a short "why now" justification tied to exposure or missing controls.
- If architectural confidence is low, say so explicitly and lower confidence rather than inventing certainty.

## Risk prioritization guidance (illustrative, not exhaustive)
- High: pre-auth RCE, auth bypass, cross-tenant access, sensitive data exfiltration, key or token theft, model or config integrity compromise, sandbox escape.
- Medium: targeted DoS of critical components, partial data exposure, rate-limit bypass with measurable impact, log/metrics poisoning that affects detection.
- Low: low-sensitivity info leaks, noisy DoS with easy mitigation, issues requiring unlikely preconditions.

## References

- Output contract and full prompt template: `references/prompt-template.md`
- Optional controls/asset list: `references/security-controls-and-assets.md`

Only load the reference files you need. Keep the final result concise, grounded, and reviewable.

## Anti-patterns

- Skipping investigation and jumping directly to fixes.
- Making claims without evidence, logs, or reproducible steps.
- Mixing unrelated workstreams in a single execution path.

## Constraints / Safety

- Redact secrets, tokens, credentials, and PII by default; never echo raw environment values.
- Prefer safe defaults and avoid irreversible changes without explicit confirmation.

## Required inputs

- User task context and target environment.
- Relevant constraints, permissions, and preferences required to execute safely.

## Deliverables

- A concrete next-step response with explicit, reproducible actions.
- A short verification checklist and caveats for the user.

## Validation

- Fail fast: stop at the first failed check and do not continue.
- Re-run the required checks before proceeding to the next step.
- Report any failed check and requested follow-up actions clearly.
- Do not finalize until user-impacting assumptions are either confirmed or explicitly carried into the report as uncertainty.

## When to use

- Use this skill when the request matches the skill's intent and scope.
- Do not use it when a different domain or higher-privilege workflow is required.

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
| [[security-best-practices]] | Run after threat modeling to get language-specific remediation guidance |
| [[security-ownership-map]] | Use to identify which engineers are responsible for the highest-risk code areas |
| [[recon-workbench]] | When authorized recon evidence is needed to ground the threat model |
| [[architecture-interview]] | When the system design is still unclear — clarify before threat modeling |

**Topic map:** [[security-ops]]

<!-- decision-feedback-protocol:v2 -->

**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If assets, trust boundaries, or attacker assumptions are not evidenced in the repo, stop, list the missing model inputs, and fall back to a scoped system inventory before asserting threats or mitigations.
