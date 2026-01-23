# Anti-patterns (expanded)

Avoid these mistakes even when they seem to help performance.

- Premature memoization without measured re-render costs.
- Adding caches that grow unbounded or violate data freshness.
- Mixing client and server data-fetching patterns in the same path.
- Introducing concurrency without error handling or cancellation.
- Hiding waterfalls by moving work into effects instead of parallelizing.
