# SQL Deep Guidance

Read when: Query plans regress, schema changes are risky, or migration safety is a concern.

## Query planning
- Verify index usage via explain plans.
- Keep filter predicates compatible with index access.

## Migration safety
- Design reversible migrations where feasible.
- Prefer phased rollouts for high-traffic tables.
