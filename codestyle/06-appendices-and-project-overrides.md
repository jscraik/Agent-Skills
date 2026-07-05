# Appendices and Project Overrides

## Table of Contents
- [Appendix A — EU AI Act (dates for governance)](#appendix-a--eu-ai-act-dates-for-governance)
- [Appendix B — Waivers (Uniform Model)](#appendix-b--waivers-uniform-model)
- [Project-Specific Style Rules](#project-specific-style-rules)

## Appendix A — EU AI Act (dates for governance)

* Act in force: 1 Aug 2024
* GPAI/foundation-model obligations applicable: 2 Aug 2025
* Most provisions fully applicable: 2 Aug 2026

---

## Appendix B — Waivers (Uniform Model)

Any waiver across ESLint, Vale, Semgrep, Clippy, and CI checks MUST include these fields unless a command contract defines a tool-specific override schema:

* Rule ID or section
* Reason
* Tracking ticket
* Expiry or ADR reference

Expired waivers MUST fail CI.

For diff-budget overrides (runtime-enforced shape):

* `approvedBy`: person approving the override
* `reason`: reason for the override
* `timestamp`: timestamp of approval

Example waiver file:

```yaml
# .codestyle-waiver.yml
waivers:
  - ruleId: "eslint:no-console"
    reason: "CLI tool requires console output for user feedback"
    trackingTicket: "JSC-123"
    expiry: "2026-06-30"

  - ruleId: "vale:Google.FirstPerson"
    reason: "User-facing docs require first-person voice per product guidelines"
    trackingTicket: "JSC-456"
    adrReference: "docs/adr/0042-documentation-voice.md"

diffBudgetOverrides:
  - approvedBy: "tech-lead@example.com"
    reason: "Emergency hotfix for production incident INC-789"
    timestamp: "2026-04-19T10:30:00Z"
```

---

<!-- PROJECT-SPECIFIC: START -->

## Project-Specific Style Rules

> Add project-specific linting, formatting, or architectural rules here. This section is NOT overwritten when upgrading the governance pack.

### Additional Rules

```jsonc
{
  // Extend local eslint.config.mjs with project-specific rules
}
```

### Architectural Boundaries

<!-- Define project-specific import restrictions or layer rules -->

<!-- PROJECT-SPECIFIC: END -->
