# Operational Readiness Review (ORR) Checklist

> Rule: RNIA — if N/A, state why in 1–2 lines and who accepted the risk.

## Service health & ownership
- [ ] Service/component owner documented
- [ ] On-call path defined (who is paged, escalation policy)
- [ ] Runbook link exists for common failures

## Monitoring & alerting
- [ ] Key SLIs/SLOs defined (or marked N/A with reason)
- [ ] Dashboards exist for core metrics
- [ ] Alerts cover: availability, latency, error rate, saturation (or N/A with reason)
- [ ] Alert thresholds + paging rules documented

## Logging & tracing
- [ ] Structured logging fields: request_id/trace_id, user/tenant (if applicable), component, error_code
- [ ] Trace propagation plan documented (or N/A)

## Reliability & failure handling
- [ ] Timeouts defined per dependency
- [ ] Retries/backoff policies defined (or explicitly avoided)
- [ ] Circuit breaker or fallback strategy (or N/A with reason)
- [ ] Degraded mode behavior documented
- [ ] Data durability expectations stated (e.g., at-least-once/at-most-once)

## Security & privacy
- [ ] AuthN/AuthZ model documented
- [ ] Secrets storage/rotation documented
- [ ] Sensitive data flows and logging redaction documented
- [ ] Abuse/misuse considerations captured (or N/A)

## Rollout / rollback
- [ ] Rollout plan (flag/canary/phased) with success/abort criteria
- [ ] Rollback/kill-switch documented and tested (or dry-run plan)
- [ ] Backward compatibility plan (API/db) documented

## Capacity & performance
- [ ] Current load assumptions + 12–24 month projection
- [ ] Known bottlenecks and mitigations
- [ ] Load/perf test plan or rationale for N/A

## Dependencies
- [ ] Upstream/downstream dependencies listed with expected SLAs
- [ ] Ownership/contact for dependencies recorded

## Data management
- [ ] Schema/migration plan risks called out
- [ ] Retention/backfill/archive approach (or N/A)

## Residual risk
- [ ] Residual risks listed with owners and review date
