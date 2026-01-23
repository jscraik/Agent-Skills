# SwiftUI Performance Audit

Last verified: 2026-01-01

Use when asked to diagnose slow rendering, janky scrolling, high CPU/memory,
excessive view updates, or layout thrash in SwiftUI apps.

## Workflow
1) Code-first review (if code provided)
- Identify unstable list identity, heavy work in `body`, broad dependencies,
  layout thrash, large images, over-animated hierarchies.
- Suggest fixes with minimal behavior changes.

2) Guide profiling (if code review is inconclusive)
- Use the SwiftUI template in Instruments (Release build).
- Reproduce the interaction and capture SwiftUI lanes + Time Profiler.
- Ask for trace export or screenshots.

3) Diagnose
- Prioritize view invalidation storms, unstable identity, heavy body work,
  layout thrash, large images, and over-animated trees.

4) Remediate
- Narrow state scope.
- Stabilize `ForEach` identities.
- Move heavy work out of `body`.
- Use `equatable()` for expensive subtrees.
- Downsample images off-main.

5) Verify
- Re-run the same trace and compare metrics.
