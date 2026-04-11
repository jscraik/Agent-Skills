# CE Reliability Review Compaction Context

Read when: you need the expanded variation guidance, extended examples, and full gotcha set that were moved out of `SKILL.md` for line-budget governance.

## Encouraging variation (expanded)
- Vary review depth by service criticality: user-facing payment services need more depth than internal batch jobs.
- Adapt resilience recommendations to the actual scale and traffic patterns.
- Customize failure scenarios to the specific technology stack and cloud platform.
- Use different emphasis for greenfield services (design patterns) versus mature services (gap analysis).
- Monoliths have different failure domains than microservices; adjust accordingly.
- Do not apply a cookie-cutter resilience checklist when context-specific analysis is safer.

## Additional examples
- "Check whether circuit breaker and timeout coverage is complete for the checkout dependency chain."
- "Review `docs/specs/2026-04-01-event-pipeline-spec.md` for reliability gaps before I move to planning."
- "We split into three microservices; map cascading-failure risk across the dependency chain."

## Gotchas (expanded)
- Circuit breakers without health checks just delay failure discovery.
- "Graceful degradation" in the spec must match what actually happens in code.
- Cloud provider SLAs are not your SLOs; application reliability compounds on top.
