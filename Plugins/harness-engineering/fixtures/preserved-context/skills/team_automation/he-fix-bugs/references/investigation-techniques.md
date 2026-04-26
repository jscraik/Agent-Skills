# Investigation Techniques

Use this when standard tracing is insufficient, reproduction is intermittent, or environment/timing effects dominate.

## Root-Cause Tracing

When failures surface deep in the stack, trace backwards to the first invalid state.

Backward tracing loop:
1. Start at the symptom location.
2. Ask where each input value originated.
3. Walk upstream until valid state first became invalid.
4. Fix at origin, not only at observation point.

If manual tracing stalls, add targeted instrumentation immediately before risky operations.

## Regression Isolation With Git Bisect

For "worked before, fails now" bugs:

```bash
git bisect start
git bisect bad
git bisect good <known-good-ref>
# run reproduction check per step, mark good/bad
git bisect reset
```

Use `git bisect run <test-command>` when a deterministic command exists.

## Intermittent Bug Techniques

If the issue fails to reproduce consistently:
- add scoped logs around the suspected state transition,
- run repeated trials to estimate failure rate,
- compare serial vs parallel execution,
- vary input data and ordering to isolate trigger shape.

Example loop:

```bash
for i in $(seq 1 20); do
  echo "Run $i"
  <test-command> && echo PASS || echo FAIL
done
```

## Environment-Difference Checklist

When local and CI/prod diverge:
- runtime/tool versions,
- env vars and feature flags,
- dependency lock state,
- OS/filesystem behavior,
- data fixtures vs real data,
- timing and concurrency variance.

Treat differences as evidence, not noise.

## Race Condition Investigation

When timing is suspect:
- widen timing windows with deliberate delays in diagnostic branches,
- inspect shared mutable state and lock/ordering assumptions,
- verify async ordering assumptions around parallel operations.

## Browser Investigation

For UI regressions:
- reproduce through deterministic browser actions,
- capture console and network failures,
- save screenshots tied to each state transition,
- correlate front-end symptoms with backend/API behavior.
