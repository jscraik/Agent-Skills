# PRD Checklist (Quality Gate)

> Rule: If a section is not applicable, mark it `N/A` and explain why in 1–2 lines.

## 1) Executive Summary
- [ ] One-liner describes what we’re building and for whom
- [ ] “Why now” is explicit
- [ ] Expected outcome is stated (not implementation)

## 2) Problem Statement / Opportunity
- [ ] Problem is clearly defined
- [ ] Evidence exists (numbers, links, user quotes, support tickets)
- [ ] “If we do nothing” impact is explained
- [ ] Opportunity is framed as a user/business outcome

## 3) Target Users / Personas
- [ ] Personas are specific (role + context)
- [ ] Each persona has concrete pain points (not generic)
- [ ] Primary vs secondary users are identified (if relevant)

## 4) User Stories / Use Cases
- [ ] Every story uses: As a…, I want…, so that…
- [ ] Each story has acceptance criteria (observable + testable)
- [ ] Priority is explicit (Must/Should/Could)
- [ ] Key user journeys are written as short narratives

## 5) Functional Requirements
- [ ] Requirements are grouped by user journey
- [ ] Edge cases are explicitly listed
- [ ] Failure UX is described (what user sees/does)

## 6) Non-Functional Requirements
- [ ] Performance expectations are stated (only at a high level)
- [ ] Reliability expectations are stated (availability/degraded mode)
- [ ] Privacy/security expectations are stated (data sensitivity)
- [ ] Accessibility expectations are stated (minimum bar)

## 7) Success Metrics / KPIs
- [ ] Each KPI has a numeric target
- [ ] Each KPI includes measurement method and data source
- [ ] Guardrails exist (what must not regress)
- [ ] Time window for measurement is defined

## 8) Scope
- [ ] In-scope list is explicit
- [ ] Out-of-scope list is explicit
- [ ] Non-goals are stated (if applicable)

## 9) Dependencies
- [ ] Internal dependencies listed
- [ ] External dependencies listed
- [ ] Assumptions about dependencies written

## 10) Risks and Mitigations
- [ ] Top risks listed with likelihood and impact
- [ ] Each risk has a mitigation or fallback
- [ ] Unknowns are captured as open questions

## 11) Timeline / Milestones (Optional)
- [ ] Milestones exist or marked N/A with explanation
- [ ] Critical path dependencies are reflected

## 12) PRD Diagram & Clarity Checks (Recommended)
- [ ] User journey flow diagram exists (Mermaid preferred)
- [ ] State model exists for user-facing lifecycles with multiple states (if applicable)
- [ ] Terminology is consistent (glossary if needed)

## 13) PRD Integrity Rule (Required)
- [ ] No technical implementation details (databases, frameworks, service topology)
- [ ] The PRD describes WHAT/WHY/WHO, not HOW
