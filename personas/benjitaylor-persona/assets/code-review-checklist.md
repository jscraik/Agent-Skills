# Benji-Style Interaction Review Checklist

## Context
- Surface/component under review:
- User goal for this interaction:
- Constraints (platform, timeline, performance, accessibility):

## Continuity and motion
- Does the user keep spatial context between states (fly vs teleport)?
- Are state transitions structural (morph/persist) instead of opacity-only crossfades?
- Are persistent elements traveling naturally instead of being destroyed/recreated?

## Precision for AI collaboration
- Is feedback mapped to exact selector or component identity?
- Is the target state explicit (before/after behavior)?
- Is intent written as executable guidance rather than vague taste language?

## Performance and resilience
- For high-frequency updates, is rendering strategy appropriate (for example canvas loop/interpolation)?
- Are loading, empty, paused, and error states handled without abrupt UX degradation?

## Tradeoffs and decision
- Chosen path + why now:
- Alternative path + why deferred:

## Immediate next step
- One concrete implementation action for the next commit/review cycle.
