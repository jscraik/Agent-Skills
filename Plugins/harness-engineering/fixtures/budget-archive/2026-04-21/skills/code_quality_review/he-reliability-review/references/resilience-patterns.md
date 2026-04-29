# Resilience Patterns Reference

Use this reference when `he-reliability-review` needs depth beyond the concise skill entrypoint. Keep review findings grounded in target evidence: code, config, architecture, logs, traces, metrics, incidents, QA reports, or documented operating assumptions.

## Review Frame

Start with the smallest set of critical user or system flows that can create real impact. For each flow, identify:

- User-visible success condition.
- Strong dependencies that must work for success.
- Weak dependencies that should degrade gracefully.
- State changes that must remain correct after timeout, retry, or partial failure.
- Saturation points such as queues, pools, workers, CPU, memory, database locks, file descriptors, or provider quotas.
- Detection path: health check, metric, trace, log, alert, SLO, error-budget burn, or customer symptom.
- Recovery path: rollback, retry after repair, reprocess, dead-letter replay, degraded mode, manual runbook, or incident escalation.

## Finding Requirements

Every substantive finding should include:

- Failure scenario.
- Evidence location or artifact.
- Blast radius and affected flow.
- Likelihood or trigger condition.
- Detection gap or existing signal.
- Mitigation.
- Validation step, such as a unit/integration test, fault-injection test, load test, replay, canary, alert check, or runbook exercise.

## SLO And Observability Readiness

Review user-facing reliability from user expectations, not only uptime.

- Are SLIs tied to meaningful symptoms such as successful request rate, latency, freshness, queue delay, or correctness?
- Is there an SLO or target threshold for the critical flow?
- Are alerts tied to user impact or error-budget burn rather than only infrastructure noise?
- Are traces, metrics, and logs sufficient to follow a failing request through dependencies?
- Do health checks distinguish process liveness from service readiness?
- Can operators identify saturation before it becomes an outage?

Common gaps:

- Dashboards show CPU or request count but not user-visible failure.
- Logs show errors but no correlation ID, dependency name, or retry attempt.
- Health check passes while a required dependency or queue is unhealthy.
- Alerts trigger after full outage instead of during burn-rate acceleration.

## Timeout Strategy

Timeouts prevent indefinite waits and protect shared resources.

Check:

- Network calls, database queries, lock acquisition, queue operations, and external APIs have explicit timeouts.
- Timeout values are tuned to the dependency and user flow, not just library defaults.
- Serial calls have a total request budget; the sum of dependency timeouts should not exceed the user-facing deadline.
- Timeout handling preserves correctness and emits useful telemetry.
- Timeouts are shorter than upstream caller deadlines where practical.

Common gaps:

- Missing timeout on connection acquisition or DNS/TLS setup.
- A long default timeout blocks request workers during dependency slowdown.
- Timeout is caught and swallowed, hiding degradation.
- Timeout triggers retry of a non-idempotent write.

## Retry, Backoff, Jitter, And Retry Budget

Retries can recover transient failures or amplify incidents.

Check:

- Retry only transient failures.
- Use bounded retry count and total elapsed time.
- Use exponential backoff with jitter for remote dependencies.
- Protect non-idempotent writes with idempotency keys or equivalent deduplication.
- Bound aggregate retry traffic with retry budgets, rate limits, or load shedding.
- Emit telemetry for retry count, final failure, and dependency identity.

Common gaps:

- Infinite retry loops.
- Fixed-interval retries across many clients.
- Retrying every HTTP status, including client or validation errors.
- Retrying writes without idempotency.
- Nested retries across client, SDK, proxy, and job runner.

## Circuit Breaker And Fallback

Circuit breakers fail fast when a dependency is unhealthy.

Check:

- Breakers are scoped per dependency or operation, not globally across unrelated services.
- Failure-rate and slow-call thresholds match traffic volume.
- Half-open probes are limited.
- Open-state behavior is observable.
- There is an intentional fallback, degraded mode, cached response, queueing path, or clear user-visible failure.

Common gaps:

- Breaker opens too late to prevent resource exhaustion.
- Breaker has no fallback and only changes the error shape.
- One shared breaker couples unrelated dependencies.
- Slow-call behavior is not counted, so brownouts continue indefinitely.

## Bulkhead, Pool, Queue, And Saturation Isolation

Bulkheads isolate resources so one failing path does not consume all capacity.

Check:

- Thread, worker, connection, and queue pools are isolated where dependency failure can spread.
- Background jobs cannot starve interactive requests.
- Queue workers have max concurrency, back-pressure, dead-letter handling, and replay strategy.
- Cache, database, and external-provider pools have sane limits and saturation telemetry.
- Per-tenant or per-operation isolation exists where noisy-neighbor risk matters.

Common gaps:

- One shared pool for all outbound dependencies.
- Queue retries fill the queue faster than workers drain it.
- Dead-letter queue exists but has no alert or replay path.
- Batch job uses the same database capacity as user-facing traffic.

## Rate Limiting, Back-pressure, And Load Shedding

Systems should protect themselves under overload.

Check:

- Incoming and outgoing request rates have bounded limits.
- Back-pressure is explicit, visible, and tested.
- Overload behavior prefers graceful degradation over total collapse.
- Clients receive actionable retry-after or failure semantics where appropriate.
- Load shedding protects critical flows before optional flows.

Common gaps:

- No admission control, so overload converts latency into full outage.
- Optional features consume capacity needed by checkout, auth, or other critical paths.
- Provider quota exhaustion is detected only after hard failures.

## Idempotency And State Correctness

Reliability includes correctness after partial failure.

Check:

- Retryable writes are idempotent.
- External side effects have correlation or idempotency keys.
- Partial success is recoverable or reconciled.
- Duplicate events, out-of-order messages, and replay are safe.
- Migrations and deploys preserve compatibility during rollout and rollback.

Common gaps:

- Payment, email, webhook, or order writes duplicate after timeout.
- Queue consumers assume exactly-once delivery.
- Rollback cannot process records written by the new version.

## Recovery And Operations

Review whether the system can recover, not just resist failure.

Check:

- Rollback path is defined and safe for data/schema changes.
- Runbook explains diagnosis, mitigation, and verification.
- Incident threshold or escalation path is clear.
- Canary, staged rollout, or feature flag exists for high-blast-radius changes.
- Recovery procedures are tested with drills, fault injection, load tests, or replay.

Common gaps:

- "Restart it" is the only recovery plan.
- Rollback is blocked by irreversible migration.
- Operators cannot tell whether recovery completed successfully.
