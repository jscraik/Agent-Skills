# Resilience Patterns Reference

Detailed patterns for reliability review assessments. Use this reference during Phase 2 (resilience coverage) of `ce-reliability-review`.

## Table of Contents
- [Circuit Breaker](#circuit-breaker)
- [Bulkhead Isolation](#bulkhead-isolation)
- [Timeout Strategy](#timeout-strategy)
- [Retry with Backoff](#retry-with-backoff)
- [Graceful Degradation](#graceful-degradation)
- [Health Checks](#health-checks)
- [Rate Limiting and Back-pressure](#rate-limiting-and-back-pressure)
- [Fallback Strategies](#fallback-strategies)
- [Dead Letter Queues](#dead-letter-queues)
- [Idempotency](#idempotency)
- [Connection Pooling](#connection-pooling)
- [Cascading Failure Prevention](#cascading-failure-prevention)

## Circuit Breaker

**Purpose:** Fail fast when a dependency is unhealthy to prevent resource exhaustion and cascading failure.

**States:** Closed (normal) → Open (failing fast) → Half-Open (testing recovery)

**Review checkpoints:**
- Is a circuit breaker present at each remote call site?
- Are thresholds appropriate for traffic volume? (failure count, failure rate, sample window)
- Does the half-open state limit probe traffic?
- Is the open state observable? (metrics, logs, alerts)
- Does the circuit breaker have a fallback or does it just throw?
- Is the circuit breaker per-dependency or global? (per-dependency preferred)

**Common mistakes:**
- Circuit breaker wrapping idempotent reads but not state-mutating writes
- Threshold too high — breaker opens only after widespread damage
- No fallback in open state — fast failure with no user-visible degradation
- Shared circuit breaker across unrelated dependencies

## Bulkhead Isolation

**Purpose:** Isolate resources so one failing component cannot consume all capacity.

**Review checkpoints:**
- Are thread pools or connection pools isolated per dependency?
- Can one slow dependency exhaust the global worker pool?
- Are queue consumers isolated from request handlers?
- Is there per-tenant or per-operation resource isolation where appropriate?

**Common mistakes:**
- Single shared connection pool for all external services
- Background job worker competing with request threads
- No memory or CPU limits on batch processing

## Timeout Strategy

**Purpose:** Prevent indefinite waits at integration points.

**Review checkpoints:**
- Is a timeout set at every network call, database query, and external API invocation?
- Are timeouts tuned to the dependency's expected latency? (not default library values)
- Do timeouts compose? (total request timeout > sum of serial dependency timeouts is a bug)
- Is there a global request timeout as a safety net?
- Are timeout values documented and monitored?

**Common mistakes:**
- Default HTTP client timeout of 30s for a call that should complete in 200ms
- Missing timeout on database connection acquisition
- Serial dependency calls without a composing total timeout
- Timeout without a handling strategy (just swallowing the error)

## Retry with Backoff

**Purpose:** Recover from transient failures without amplifying load.

**Review checkpoints:**
- Is retry present for transient failure modes? (network errors, 503, connection reset)
- Is exponential backoff with jitter used? (not fixed-interval retry)
- Is there a max retry count? (unbounded retries are a resource leak)
- Are retried operations idempotent? (critical — retrying non-idempotent operations causes data duplication)
- Is the retry budget bounded? (e.g., 20% of total requests, not unbounded)
- Are non-transient errors excluded from retry? (400s, auth failures, validation errors)

**Common mistakes:**
- Retrying without backoff — amplifying load during outages
- Retrying non-idempotent POST requests without idempotency keys
- Retrying on non-transient errors (400 Bad Request)
- No jitter — synchronized retries from multiple clients create thundering herd

## Graceful Degradation

**Purpose:** Provide reduced but functional service when dependencies fail.

**Review checkpoints:**
- For each non-critical dependency: what happens to the user when it's down?
- Is there a defined degradation hierarchy? (critical vs. optional dependencies)
- Do error responses indicate degraded mode to the client?
- Is the degraded state time-bounded? (auto-recovery or manual intervention)
- Can the system serve stale data when the source is unavailable?

**Common mistakes:**
- Treating all dependencies as critical — one optional service failure takes down everything
- No user-visible indication that the service is in degraded mode
- Caching stale data indefinitely without staleness indicators

## Health Checks

**Purpose:** Enable infrastructure to detect and route around unhealthy instances.

**Review checkpoints:**
- Liveness probe: does the process respond? (should NOT check dependencies)
- Readiness probe: can the instance serve traffic? (should check critical dependencies)
- Startup probe: is initialization complete? (prevents premature traffic)
- Do health checks have their own timeout? (a health check blocked on a slow dependency is useless)
- Are health check results cached briefly to prevent probe storms?

**Common mistakes:**
- Liveness probe that checks database — healthy process killed because DB is slow
- No readiness probe — traffic routed to instance before warm-up
- Health check endpoint that does expensive computation

## Rate Limiting and Back-pressure

**Purpose:** Protect the service from overload, both external and internal.

**Review checkpoints:**
- Is there rate limiting at the API ingress? (per-client, per-endpoint, global)
- Are rate limits documented in the API contract?
- Does the system apply back-pressure to upstream producers when overwhelmed?
- Are rate limit responses clear? (429 with Retry-After header)
- Is there admission control for batch or background work?

**Common mistakes:**
- No rate limiting — a single bad client can take down the service
- Rate limiting without back-pressure — rejected requests queued somewhere upstream
- Missing Retry-After header — clients retry immediately

## Fallback Strategies

**Purpose:** Provide a reasonable response when the primary path fails.

**Review checkpoints:**
- Cache fallback: can stale cached data serve the request?
- Default fallback: is there a sensible default response?
- Alternative service: can a secondary service provide the data?
- Queue for later: can the request be deferred and processed when the dependency recovers?
- Partial response: can the core data be returned without optional enrichments?

## Dead Letter Queues

**Purpose:** Capture messages that cannot be processed for investigation and replay.

**Review checkpoints:**
- Do message consumers have a DLQ for poison messages?
- Is there monitoring and alerting on DLQ depth?
- Can DLQ messages be replayed after the root cause is fixed?
- Is there a retention policy for DLQ messages?
- Are DLQ messages enriched with failure context? (error, attempt count, timestamp)

## Idempotency

**Purpose:** Enable safe retries and replay without duplicate side effects.

**Review checkpoints:**
- Are state-mutating operations idempotent by design?
- Is there an idempotency key mechanism for external-facing APIs?
- Are database operations using upsert or conditional writes where appropriate?
- Can messages be safely replayed without creating duplicates?
- Is idempotency verified by tests?

**Common mistakes:**
- Auto-increment ID as idempotency key (every retry creates a new record)
- Idempotency at the API layer but not at the database layer
- Assuming "exactly once" delivery from message queues

## Connection Pooling

**Purpose:** Manage connection resources efficiently with failure containment.

**Review checkpoints:**
- Are connection pools bounded? (max size, not unlimited)
- Is there a connection acquisition timeout?
- Are idle connections evicted?
- Are connections validated before use? (stale connection detection)
- Is the pool size appropriate for the deployment topology?
- Are connection pool metrics exposed? (active, idle, waiting, total)

**Common mistakes:**
- Unbounded connection pool — resource exhaustion under load
- No acquisition timeout — threads blocked indefinitely waiting for connections
- Pool size calculated per instance but total exceeds dependency connection limit

## Cascading Failure Prevention

**Purpose:** Contain failures to prevent them from spreading across the system.

**Review patterns:**
1. **Dependency isolation**: Each dependency should fail independently
2. **Shed load early**: Reject excess traffic at the edge, not deep in the stack
3. **Fail static**: When in doubt, serve stale data or defaults
4. **Avoid retry amplification**: Retries at multiple layers compound exponentially
5. **Monitor queue depth**: Growing queues are early warnings of cascading failure
6. **Graceful shutdown**: Drain in-flight requests before terminating

**Red flags:**
- Synchronous calls to multiple dependencies in sequence with no total timeout
- Retry logic at multiple layers (client → gateway → service → downstream)
- Shared resource pools across unrelated dependencies
- No load shedding at the ingress
