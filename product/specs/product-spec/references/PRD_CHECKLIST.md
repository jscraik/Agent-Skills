# PRD Checklist (Quality Gate)

> Rule: If a section is not applicable, mark it `N/A` and explain why in 1–2 lines.
> Evidence rule: Every paragraph must end with an `Evidence:` line or `Evidence gap:` line.

## 0) Evidence Coverage (Required)
- [ ] Every paragraph ends with `Evidence:` or `Evidence gap:`
- [ ] Evidence Gaps section lists all missing sources
- [ ] Evidence Map table lists all citations

## 1) Executive Summary
- [ ] One-liner describes what we’re building and for whom
- [ ] “Why now” is explicit
- [ ] Expected outcome is stated (not implementation)

## 2) Template Metadata (Required for template-driven deliverables)
- [ ] name is unique and present
- [ ] description is human-readable
- [ ] title_template includes {variable} placeholders where applicable
- [ ] acceptance_criteria list exists
- [ ] priority is set (defaults to "medium" if not specified)
- [ ] variables list exists (can be empty)
- [ ] metadata object exists (can be empty)
- [ ] template metadata exported to `<spec>.template.json`

## 3) Problem Statement / Opportunity
- [ ] Problem is clearly defined
- [ ] Evidence exists (numbers, links, user quotes, support tickets)
- [ ] “If we do nothing” impact is explained
- [ ] Opportunity is framed as a user/business outcome

## 4) Target Users / Personas
- [ ] Personas are specific (role + context)
- [ ] Each persona has concrete pain points (not generic)
- [ ] Primary vs secondary users are identified (if relevant)

## 5) User Stories / Use Cases
- [ ] Every story uses: As a…, I want…, so that…
- [ ] Each story has acceptance criteria (observable + testable)
- [ ] Priority is explicit (Must/Should/Could)
- [ ] Key user journeys are written as short narratives

## 6) Acceptance Criteria (Top-level)
- [ ] Top-level acceptance criteria section exists
- [ ] Criteria are observable, testable, and not duplicates of story-level criteria

## 7) Decision Log / ADRs
- [ ] Decision log exists with rationale, alternatives, and ADR links

## 8) Data Lifecycle & Retention
- [ ] Data created/sources documented
- [ ] Retention and deletion policies documented
- [ ] DSAR/export handling documented or N/A

## 9) Functional Requirements
- [ ] Requirements are grouped by user journey
- [ ] Edge cases are explicitly listed
- [ ] Failure UX is described (what user sees/does)

## 10) Non-Functional Requirements
- [ ] Performance expectations are stated (only at a high level)
- [ ] Reliability expectations are stated (availability/degraded mode)
- [ ] Privacy/security expectations are stated (data sensitivity)
- [ ] Accessibility expectations are stated (minimum bar)

## 11) Success Metrics / KPIs
- [ ] Each KPI has a numeric target
- [ ] Each KPI includes measurement method and data source
- [ ] Guardrails exist (what must not regress)
- [ ] Time window for measurement is defined

## 12) Scope
- [ ] In-scope list is explicit
- [ ] Out-of-scope list is explicit
- [ ] Non-goals are stated (if applicable)

## 13) Feature Creep Guardrails
- [ ] Guardrail questions answered with evidence
- [ ] Trade-offs documented for any scope additions
- [ ] 48-hour rule applied or explicitly waived with reason

## 14) Scope Decision Log
- [ ] Log exists with date, decision, rationale, and trade-off
- [ ] Agent/stakeholder requests captured

## 15) Dependencies
- [ ] Internal dependencies listed
- [ ] External dependencies listed
- [ ] Assumptions about dependencies written

## 16) Risks and Mitigations
- [ ] Top risks listed with likelihood and impact
- [ ] Each risk has a mitigation or fallback
- [ ] Unknowns are captured as open questions

## 17) Timeline / Milestones (Optional)
- [ ] Milestones exist or marked N/A with explanation
- [ ] Critical path dependencies are reflected

## 18) PRD Diagram & Clarity Checks (Recommended)
- [ ] User journey flow diagram exists (Mermaid preferred)
- [ ] State model exists for user-facing lifecycles with multiple states (if applicable)
- [ ] Terminology is consistent (glossary if needed)

## 19) Launch & Rollback Guardrails
- [ ] Go/No-Go metrics are defined
- [ ] Rollback triggers and owners are defined
- [ ] Post-deploy verification steps are listed

## 20) Post-Launch Monitoring Plan
- [ ] Monitoring window is defined
- [ ] Dashboards and owners are listed
- [ ] Alert thresholds are specified

## 21) Support / Ops Impact
- [ ] Runbook links are included
- [ ] Escalation path and manual ops are documented

## 22) Compliance & Regulatory Review Triggers
- [ ] Triggers are listed
- [ ] Required reviews and status are documented

## 23) Ownership & RACI
- [ ] RACI table exists with accountable owners
- [ ] Security/Privacy and Support/Ops ownership included

## 24) Security & Privacy Classification
- [ ] Data sensitivity tier stated
- [ ] PII/PHI/PCI presence documented
- [ ] Required controls listed

## 25) Dependency SLAs & Vendor Risk
- [ ] Third-party dependencies listed
- [ ] SLA/SLO expectations captured
- [ ] Vendor-down fallback documented

## 26) Cost Model & Budget Guardrails
- [ ] Cost drivers listed
- [ ] Budget cap defined
- [ ] Cost alerts and owners defined

## 27) Localization & Internationalization
- [ ] Locales in scope documented or N/A
- [ ] Translation workflow documented
- [ ] Formatting rules documented where relevant

## 28) Backward Compatibility & Deprecation
- [ ] Compatibility constraints documented
- [ ] Deprecation plan and comms documented
- [ ] Migration aids documented

## 29) Experimentation & Feature Flags
- [ ] Experiment plan documented (if applicable)
- [ ] Flag ownership and kill switch documented

## 30) Kill Criteria
- [ ] Stop conditions documented
- [ ] Decision owner documented
- [ ] Communication plan documented

## 31) Evidence Gaps & Map (Required)
- [ ] Evidence Gaps section present with owners/impact
- [ ] Evidence Map table present with sources and confidence

## 32) PRD Integrity Rule (Required)
- [ ] No technical implementation details (databases, frameworks, service topology)
- [ ] The PRD describes WHAT/WHY/WHO, not HOW
