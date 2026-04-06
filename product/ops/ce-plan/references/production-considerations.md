# Production Planning Considerations

Production readiness guidance for implementation planning.

## Feature Flag and Rollout Planning

For work requiring gradual rollout or risk mitigation:

| Rollout Pattern | When to Use |
|----------------|-------------|
| **Feature flag** | Toggle functionality without deployment |
| **Gradual rollout** | Percentage-based traffic shifting |
| **Canary release** | Small subset before full rollout |
| **Dark launch** | Test in production without user impact |
| **Blue-green** | Zero-downtime cutover |

### Feature Flag Requirements
- Define feature flag strategy using `references/rollout-strategies.md`
- All feature flags must have removal criteria (e.g., "remove flag when 100% rollout stable for 7 days")
- Plan monitoring and rollback procedures for each phase
- Document flag naming convention and ownership

Use Cloudflare MCP for edge config/feature flag management if applicable.

## Cost and Resource Controls

For plans involving significant resource usage:

| Cost Control | When to Specify |
|--------------|-----------------|
| **Token budget** | LLM-heavy implementations (specify per-operation limits) |
| **Compute budget** | Background jobs, data processing (max CPU/memory/time) |
| **Storage limits** | File uploads, data retention (max size, cleanup policy) |
| **API rate limits** | External API calls (throttling, quota management) |
| **Cloud costs** | Infrastructure changes (estimated monthly cost, budget alerts) |

### Documentation Requirements
Document in implementation units:
- Estimated resource usage per operation
- Cost monitoring approach
- Alert thresholds
- Optimization milestones

## Observability and Monitoring Planning

Every plan must specify how the work will be observed in production:

| Component | Planning Requirement |
|-----------|---------------------|
| **Logging** | Log levels, structured logging fields, sensitive data redaction |
| **Metrics** | Key metrics to track (latency, throughput, errors), dashboard needs |
| **Alerting** | Alert conditions, severity levels, on-call routing |
| **Tracing** | Distributed tracing for cross-service work, trace sampling rate |
| **Health checks** | Liveness/readiness probes, dependency health validation |
| **SLOs/SLIs** | Service level objectives, error budgets (user-facing services) |

### Implementation Unit Requirements
- What to monitor
- Alert thresholds
- Runbook references
- Incident response triggers

Use CircleCI MCP for CI/CD observability if applicable.

## Testing Pyramid

Every implementation unit must specify test coverage across all three layers:

```
    ┌─────────────┐
    │   E2E Tests │  ← Critical user journeys, smoke tests
    │  (Browser)  │    Few tests, high confidence
    ├─────────────┤
    │Integration  │  ← Service boundaries, API contracts
    │   Tests     │    Real chains, mocked externals
    ├─────────────┤
    │  Unit Tests │  ← Business logic, edge cases
    │             │    Fast, isolated, many tests
    └─────────────┘
```

### Coverage Requirements

| Layer | Target Coverage | What to Test |
|-------|----------------|--------------|
| **Unit** | 70%+ | Business logic, utilities, pure functions |
| **Integration** | Critical paths | Database queries, API clients, service calls |
| **E2E** | User journeys | Critical flows, auth, payments, core features |

### Documentation
Per implementation unit, document:
- Test scope for each layer
- Mocking strategy for external dependencies
- Test data requirements
- CI execution time budget

## Reliability Modeling

For backend services, APIs, background jobs, or multi-component work, model failure scenarios:

### Failure Domain Questions

| Domain | Questions to Answer |
|--------|---------------------|
| **Failure modes** | What can fail? (network, disk, dependency, timeout, corruption) |
| **Cascading risk** | Can this failure cascade to other systems? How to contain? |
| **Graceful degradation** | What functionality remains when dependencies fail? |
| **Recovery path** | How does the system recover? Auto or manual? Time to recover? |
| **Retry safety** | Are operations idempotent? Can retries cause harm? |
| **Resource exhaustion** | What happens under load? Circuit breaker needed? |

### Resilience Checklist

- [ ] **Circuit breakers**: Fail fast when dependencies unhealthy
- [ ] **Bulkheads**: Isolate resources to prevent one failure consuming all
- [ ] **Timeouts**: Set at every integration point
- [ ] **Retries**: Exponential backoff with jitter, idempotent operations only
- [ ] **Graceful degradation**: Core functionality works without non-critical deps
- [ ] **Health checks**: Liveness and readiness probes
- [ ] **Rate limiting**: Protect from overload
- [ ] **Fallbacks**: Default behavior when services fail

### Documentation Requirements
Per implementation unit, document:
- Expected failure modes and their likelihood
- Mitigation strategy per failure mode
- Fallback behavior when partial degradation occurs
- Monitoring/alerting for failure detection

See `../ce-reliability-review/references/resilience-patterns.md` for detailed patterns (circuit breaker, bulkhead, retry, etc.).

### When to Route to ce-reliability-review

Route to `[[ce-reliability-review]]` if:
- The work involves new services or significant service changes
- There are multiple external dependencies
- The blast radius of failure is high (user-facing, financial, data integrity)
- The user explicitly asks for reliability analysis
