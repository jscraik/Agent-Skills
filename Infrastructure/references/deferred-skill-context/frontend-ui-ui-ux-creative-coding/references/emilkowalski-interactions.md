# Emil Kowalski — Interaction + Micro‑Motion Notes (2024–2026)

Use this when you need **interaction‑level** guidance (hover/press, overlays, drag, menus). Keep it actionable.

## Micro‑interaction heuristics
- Fix hover flicker by **listening on the parent** and animating a child element, keeping the hover target stable.
- Buttons feel more responsive with a **subtle press‑scale** (e.g., 0.98–0.99).
- **Avoid animating from `scale(0)`**—start around `0.9+` for a gentler feel.
- Keep **hover transitions snappy**; slow hovers read as lag.
- **Stagger multi‑element reveals** with tiny delays for smoother perception.
- **Sometimes the best animation is no animation**—don’t animate for its own sake.
- For touch devices, gate hover styles behind `@media (hover: hover) and (pointer: fine)` to avoid sticky tap-hover artifacts.

## Timing + easing
- Use **ease‑out** for enter/exit to feel faster and more natural.
- Keep animations **fast**; clarity beats flourish.
- If you see a **1px shift at animation end**, add `will-change: transform` to stabilize GPU/CPU handoffs.
- Prefer short custom curves over generic defaults when a motion system needs more intent.

## Overlays, toasts, drawers
- Prefer **drag‑to‑dismiss** for drawers/toasts; apply **momentum + damping** to avoid abrupt stops.
- Add a **subtle background blur** behind toasts to emphasize priority without blocking content.
- Use a short **drag vs scroll debounce** (≈100ms) to prevent accidental dismiss.
- On mobile keyboards, consider the **Visual Viewport API** to keep panels visible.
- Open adjacent tooltips instantly once one tooltip is already open; do not repay the full delay on every hover.
- For dismiss gestures, velocity can matter as much as distance; a quick flick should not require a huge drag.
- Capture pointer events after drag start and ignore extra touch points to prevent jumps or dropped gestures.

## Menus + dropdowns
- **Origin‑aware dropdowns** feel better; Radix/BaseUI support this with CSS vars.
- Animated navigation can be built with **Radix Navigation Menu** (Linear pattern).
- Use `@starting-style` or a mounted-state fallback for enter transitions rather than effect-driven setup when the platform can handle it cleanly.

## System polish / perceived speed
- For mutation UX, run **mutation + delay in parallel** (e.g., `Promise.all`) so waits don’t stack.
- A **short artificial delay** after a write can boost confidence that it “saved.”
- For theme bar color transitions, **precompute easing** and animate in small steps if CSS isn’t supported.
- Fast follow-up tooltips and short select/dropdown timings can change how fast the entire app feels, even when backend speed is unchanged.

## Motion primitives to pair with interactions
- **Clip‑path** is a powerful tool for distinctive UI motion (use sparingly, keep performant).
- **Blur** can help crossfades read as one state changing instead of two states overlapping, but keep it subtle and watch Safari cost.

## Performance notes
- Prefer direct `transform` updates on the moving element over inherited CSS variables that force recalculation through large subtrees.
- Use CSS or WAAPI for predetermined animation paths under load; keep JS motion for dynamic or interruptible cases.

## Sources (for attribution)
- https://x.com/emilkowalski/status/1762211373960900664
- https://x.com/emilkowalski/status/1772624579493605637
- https://x.com/emilkowalski/status/1952354760637505541
- https://x.com/emilkowalski/status/1954891053032755560
- https://x.com/emilkowalski/status/1959952049627365474
- https://x.com/emilkowalski/status/1970144111261868487
- https://x.com/emilkowalski/status/1956340129045352703
- https://x.com/emilkowalski/status/1957786835012214833
- https://x.com/emilkowalski/status/1981352193262256182
- https://x.com/emilkowalski/status/1937956517577134391
- https://x.com/emilkowalski/status/1949870041819730389
- https://x.com/emilkowalski/status/2003081351772479987
- https://x.com/emilkowalski/status/2003079978452431002
- https://x.com/emilkowalski/status/1928140156151775421
- https://x.com/emilkowalski/status/1850914125775315404
- https://x.com/emilkowalski/status/1810671775602098592
