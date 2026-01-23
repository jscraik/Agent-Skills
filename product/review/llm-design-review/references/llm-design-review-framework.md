# LLM Product Design Review Framework (Reference)

Use this file to expand the review into detailed checklists and standards mapping when needed. Keep outputs concise; do not copy this verbatim into responses.

## 1) UX and Interaction Design
- User need and value: confirm AI is appropriate and improves outcomes.
- Mental models: communicate capabilities, limits, and uncertainty.
- Prompt UX: examples, templates, and guardrails for input.
- Feedback and control: edit/retry/undo, multiple suggestions, user overrides.
- Transparency: disclose AI use, sources/citations, and why outputs appear.
- Error handling: friendly fallbacks, escalation paths, and recovery guidance.

## 2) System Architecture and Integration
- Modular services: LLM, retrieval, tools, UI, and orchestration separated.
- Tooling boundaries: structured tool calls, schema validation, least privilege.
- Scalability: batching, caching, horizontal scaling, rate limits.
- Context strategy: RAG, summarization, sliding windows, adaptive pruning.
- Graceful degradation: retries, queues, fallback models, user messaging.
- Agent control: bounded loops, step limits, timeouts, and audits.

## 3) Model, Prompt, and Data Strategy
- Model selection: quality vs. latency vs. cost; justify choice.
- Fine-tuning policy: prefer prompt/few-shot first; justify tuning with data.
- Prompt management: versioned templates, modular prompts, test suites.
- Context governance: what data is injected, why, and how it is filtered.
- Data ethics: consent, representativeness, bias checks, data sheets.
- Evaluation plan: golden sets, adversarial tests, pass/fail gates.

## 4) Safety, Security, and Ethics
- Moderation: input/output safety filters and domain-specific safeguards.
- Bias/fairness: demographic testing, mitigation strategy, monitoring.
- Privacy: consent, retention, minimization, encryption, RBAC.
- OWASP LLM Top 10: prompt injection, output handling, data poisoning,
  excessive agency, system prompt leakage, and model DoS.
- High-stakes: require human-in-the-loop approval and strong disclaimers.

## 5) Performance, MLOps, and Iteration
- Observability: latency, error rates, hallucination flags, feedback rates.
- Continuous evals: regression tests for prompts/models, scheduled evals.
- Rollbacks: feature flags and model/prompt rollback capability.
- Auditability: logs tied to model version, prompt version, and context.
- Update strategy: model upgrade plan and compatibility tests.

## 6) Governance and Compliance
- Ownership: AI component owners and review cadence.
- Risk register: tracked, prioritized, and mitigated.
- Standards mapping: NIST AI RMF, ISO/IEC 42001, OWASP LLM Top 10.
- Regulatory posture: EU AI Act risk tier, HIPAA/FERPA/PCI as applicable.

## Evidence Artifacts (preferred)
- Journey map and primary flow diagrams
- Architecture diagram and tool boundary map
- Prompt inventory + versioning approach
- Evaluation plan and baseline metrics
- Safety checklist and red-team findings
- Data handling policy summary

## Output Guidance
- Prioritize by severity and user impact.
- Call out assumptions separately from evidence-backed findings.
- Provide practical fixes with trade-offs when relevant.

## Reference Standards (names only)
- Google PAIR Guidebook
- Microsoft HAX Guidelines
- NIST AI RMF 1.0
- ISO/IEC 42001
- OWASP Top 10 for LLM Applications
- MITRE ATLAS
