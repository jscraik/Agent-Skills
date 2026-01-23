# Understanding and Improving SwiftUI Performance (Summary)

Last verified: 2026-01-01

Context: Apple guidance on diagnosing SwiftUI performance with Instruments and
reducing long or frequent updates.

## Core concepts
- SwiftUI is declarative; updates are driven by state, environment, and
  observable dependencies.
- View bodies must compute quickly to meet frame deadlines.
- Instruments is the primary tool to find long updates and excessive frequency.

## Instruments workflow
1. Profile via Product > Profile.
2. Choose the SwiftUI template and record.
3. Exercise the target interaction.
4. Stop recording and inspect SwiftUI track + Time Profiler.

## SwiftUI timeline lanes
- Update Groups: time spent calculating updates.
- Long View Body Updates: orange >500us, red >1000us.
- Long Platform View Updates: AppKit/UIKit hosting in SwiftUI.
- Other Long Updates: geometry/text/layout.
- Hitches: frame misses where UI wasn’t ready in time.

## Diagnose long view body updates
- Expand SwiftUI track; inspect module subtracks.
- Set Inspection Range and correlate with Time Profiler.
- Use call tree/flame graph to identify expensive frames.
- Repeat updates for enough samples.
- Filter to a specific update (Show Calls Made by `MySwiftUIView.body`).

## Diagnose frequent updates
- Use Update Groups for long active groups without long updates.
- Set inspection range and analyze update counts.
- Use Cause graph (Show Causes) to see triggers.
- Prioritize the highest-frequency causes.

## Remediation patterns
- Move expensive work out of `body` and cache results.
- Use `@Observable()` to scope dependencies to properties actually read.
- Avoid broad dependencies that fan out updates to many views.
- Reduce layout churn; isolate state-dependent subtrees.
- Avoid stored closures that capture parent state.
- Gate frequent updates (e.g., geometry) by thresholds.

## Verification
- Re-record after changes to confirm reduced updates and fewer hitches.
