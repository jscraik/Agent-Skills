# Transcript -- Building AI agents in the browser, for the browser, of the browser

**Speaker:** Lars Trieloff (Adobe)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Lars-Triof.txt

## Source Status

The source transcript for this session contains a live technical demonstration with concrete runtime-control mechanics. This published transcript artifact is safety-redacted: it preserves the architecture, motivation, and product-design lessons while omitting setup commands, app-modification details, public runtime endpoints, credential/token paths, and other operational mechanics.

## Talk Substance

Lars Trieloff argues that browser-native agents are different from agents that merely have a web UI or remotely control a browser. The talk explores what happens when the browser itself becomes the agent's runtime context and containment boundary.

The central design question is how to give agents useful proximity to browser context without giving them unconstrained access to a user's machine, accounts, or third-party applications. The safe architectural takeaway is to build through documented integration surfaces, narrow permissions, visible user consent, and auditable event boundaries.

## Preserved Concepts

- Browser-native agents as a distinct product architecture.
- Browser-as-runtime and browser-as-container framing.
- Local execution versus remote sandbox tradeoffs.
- Harness design for constraining agent power.
- Product integration through explicit, documented APIs.
- Reviewable actions, narrow permissions, and credential isolation.

## Advisory Takeaway

The talk is useful as product architecture guidance: keep agent capabilities close enough to context to be useful, but constrained enough that actions remain visible, authorized, and reviewable.
