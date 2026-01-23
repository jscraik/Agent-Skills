# Optimizing SwiftUI Performance with Instruments (Summary)

Last verified: 2026-01-01

Context: WWDC session on the SwiftUI Instrument in Instruments 26 and how to
find SwiftUI-specific bottlenecks.

## Key takeaways
- Profile with the SwiftUI template (SwiftUI + Time Profiler + Hangs/Hitches).
- Long view body updates are common; use "Long View Body Updates".
- Set inspection range on long updates and correlate with Time Profiler.
- Keep work out of `body`: move formatting/sorting/decoding into cached paths.
- Use the Cause & Effect Graph to diagnose *why* updates occur.
- Avoid broad dependencies that trigger many updates.
- Environment updates still cost; avoid fast-changing values in environment.
- Profile early during feature development.

## Suggested workflow
1. Record a trace in Release mode with the SwiftUI template.
2. Inspect "Long View Body Updates" and "Other Long Updates".
3. Zoom into a long update and check Time Profiler for hot frames.
4. Fix slow body work by moving heavy logic to cached paths.
5. Use Cause & Effect Graph for unintended update fan-out.
6. Re-record and compare update counts and hitch frequency.

## Example patterns
- Cache formatted distance strings in a manager instead of computing in `body`.
- Replace global arrays with per-item state to reduce update fan-out.
