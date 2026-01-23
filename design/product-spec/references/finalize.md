### 8) Finalize
- **Quality gate:** completeness (all sections substantive), consistency, clarity, actionability.
- **Foundation Spec specifics:** one-sentence summary; core problem with anti-goal; target user + context + job-to-be-done; success (primary metric, guardrails, activation); MVP scope (must-have vs out-of-scope); user stories (top 5–10 with AC and edge cases); primary journey (happy path); positioning constraints; evidence discipline applied.
- **UX Spec specifics:** mental model alignment; information architecture (entities, relationships, navigation); affordances & actions per screen/component; system feedback states per key view; UX acceptance criteria in Gherkin format; evidence discipline applied.
- **Build Plan specifics:** outcome → opportunities → solution (with rejected alternatives); top 3–5 assumptions/risks; epics sequenced; stories per epic with AC, telemetry/events, tests; data + contracts (lightweight); test strategy (unit/integration/E2E/failure-mode); release & measurement plan (feature flags, rollout, monitoring, measurement window); evidence discipline applied.
- **PRD specifics (decision-first, default):**
  - One-sentence summary
  - Problem & Job (JTBD-lite) + anti-goal
  - Target user + context + workaround
  - Success criteria (primary metric, activation, guardrails)
  - Scope (in/out) + primary journey (happy path only)
  - Top user stories with acceptance criteria
  - Optional (only if decision-impacting): assumptions/risks, rollout/measurement, or compliance notes
  - If deeper analyses exist (SWOT, market, value prop, pre-mortem), link and summarize the decision only
- **Tech specifics:** architecture diagram/description covers all components; every API endpoint has method/path/schemas/errors; data models detail fields + constraints + indexes; security covers authN/Z + encryption + input validation; performance includes latency/throughput/availability; deployment repeatable & rollback-able; observability plan; SLOs/error budget + policy; top-level `Acceptance Criteria` section present and populated; decision log/ADRs referenced; data lifecycle/retention/deletion addressed; feature creep guardrails answered with evidence; scope decision log populated; launch/rollback guardrails and go/no-go metrics defined; post-launch monitoring plan with owners and window; support/ops impact and runbook links; compliance/regulatory review triggers stated; ownership/RACI defined; security/privacy classification completed; dependency SLAs/vendor risk covered; cost model with guardrails; localization/i18n stance; backward compatibility/deprecation policy; experimentation/feature flag plan; explicit kill criteria.
- **Review mode specifics:** Project Review Report produced; checklist passed; Recovery Plan section (stop/continue/start + top actions + "done when"); follow-ups to update PRD/Tech Spec/ADRs noted (only if explicitly requested after audit). Every paragraph includes `Evidence:` or `Evidence gap:`; include `Evidence Gaps` + `Evidence Map` sections.
- **Review artifact vs. new process (default):** The adversarial review document is evidence of the audit (like a transcript), not a new ongoing project process. Keep it, but do not introduce new mandatory processes unless the user explicitly asks.
- Run production gates before `[AGREE]` when shipping: ORR checklist, Launch checklist, SLO template (or N/A with reason).
- When satisfied and all models said `[AGREE]`, write the final documents:
  - `.spec/foundation-YYYY-MM-DD-<slug>.md`
  - `.spec/ux-YYYY-MM-DD-<slug>.md`
  - `.spec/build-plan-YYYY-MM-DD-<slug>.md`
  - (Optionally) `.spec/spec-YYYY-MM-DD-<slug>.md` for backward compatibility
  - Print all documents with debate summary.
- Add final summary block:
```
=== Debate Complete ===
Documents: Foundation Spec, UX Spec, Build Plan (or [PRD | Technical Specification])
Rounds: <N> (or include cycles if >1)
Models: <list>
Key refinements: - <bullets>
```
- For template-driven deliverables, run `python3 scripts/spec-export.py <spec>.md --out <spec>.template.json` and include the JSON in deliverables.
- **Validation guidance:** For each story and top-level acceptance criteria, include a validation method (tests, lint, build, manual check) and prefer repo scripts. If no repo scripts are known, recommend tools from `~/.codex/instructions/tooling.md` (e.g., `biome`, `pnpm test`, `uv run pytest`) as appropriate to the stack.
