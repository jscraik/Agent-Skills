# Understanding Hangs in Your App (Summary)

Last verified: 2026-01-01

Context: Apple guidance on identifying hangs caused by long-running main-thread
work and understanding the main run loop.

## Key concepts
- A hang is a noticeable delay in a discrete interaction (typically >100 ms).
- Hangs almost always come from long-running work on the main thread.
- The main run loop processes UI events, timers, and main-queue work sequentially.

## Main-thread work stages
- Event delivery to the correct view/handler.
- Your code: state updates, data fetch, UI changes.
- Core Animation commit to the render server.

## Why the main run loop matters
- Only the main thread can update UI safely.
- The run loop is the foundation that executes main-queue work.
- Busy run loops block new events and cause hangs.

## Diagnosing hangs
- Observe main run loop busy periods; healthy loops sleep most of the time.
- Hang detection often flags busy periods >250 ms (tunable in Instruments).

## Practical takeaways
- Keep main-thread work short; offload heavy work.
- Avoid long tasks on the main actor or main dispatch queue.
- Use run loop behavior as a proxy for user-perceived responsiveness.
