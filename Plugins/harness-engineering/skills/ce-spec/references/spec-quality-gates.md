# Specification Quality Gates

Reference for required quality specifications in ce-spec work.

## Accessibility (a11y) Requirements for UI Specs

Every `dedicated-ui-spec` must specify:

| WCAG Principle | Requirements |
|----------------|--------------|
| **Perceivable** | Color contrast (4.5:1 normal, 3:1 large), text alternatives, captions/transcripts |
| **Operable** | Keyboard navigation, focus indicators, skip links, no keyboard traps |
| **Understandable** | Error prevention, correction guidance, consistent navigation |
| **Robust** | ARIA labels, semantic HTML, screen reader compatibility |

### Required UI Spec Elements
- `wcag_level` in frontmatter (default: `2.1-AA`)
- Keyboard interaction flows for interactive elements
- Focus order specification
- Screen reader announcements for dynamic content
- Color contrast verification criteria

Use Coderabbit CLI MCP for automated a11y review integration.

## Idempotency and Resilience Requirements

For services, APIs, background jobs, and state-changing operations:

| Concern | Specification Requirement |
|---------|--------------------------|
| **Idempotency** | Must operations be idempotent? What is the idempotency key? |
| **Retry behavior** | Max retries, backoff strategy, dead-letter handling |
| **Circuit breaker** | When to fail fast, recovery detection, half-open state |
| **Timeouts** | Per-operation and end-to-end timeout values |
| **State cleanup** | Orphaned state detection and cleanup procedures |

Read `Infrastructure/references/resilience-patterns.md` for detailed specification templates.

## Data Privacy and GDPR Checklist

For user-facing features collecting or processing personal data:

| Check | Requirement |
|-------|-------------|
| **Data minimization** | Only collect data strictly necessary for the feature |
| **Purpose limitation** | Document specific purpose for each data field |
| **Consent** | If required, specify consent mechanism and withdrawal process |
| **Retention** | Define data retention period and deletion trigger |
| **User rights** | Document how users access, rectify, or delete their data |
| **Security** | Encryption at rest/transit, access controls, audit logging |
| **DPO review** | Flag if Data Protection Officer review is required |
| **Cross-border** | Document if data leaves user's jurisdiction |

Read `Infrastructure/references/gdpr-specification-guide.md` for detailed privacy requirements and Data Protection Impact Assessment (DPIA) triggers.
