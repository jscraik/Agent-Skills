# Emil Kowalski — Interaction + Micro‑Motion Notes (2024–2026)

Use this when you need **interaction‑level** guidance (hover/press, overlays, drag, menus). Keep it actionable.

## Micro‑interaction heuristics
- Fix hover flicker by **listening on the parent** and animating a child element, keeping the hover target stable.
- Buttons feel more responsive with a **subtle press‑scale** (e.g., 0.98–0.99).
- **Avoid animating from `scale(0)`**—start around `0.9+` for a gentler feel.
- Keep **hover transitions snappy**; slow hovers read as lag.
- **Stagger multi‑element reveals** with tiny delays for smoother perception.
- **Sometimes the best animation is no animation**—don’t animate for its own sake.

## Timing + easing
- Use **ease‑out** for enter/exit to feel faster and more natural.
- Keep animations **fast**; clarity beats flourish.
- If you see a **1px shift at animation end**, add `will-change: transform` to stabilize GPU/CPU handoffs.

## Overlays, toasts, drawers
- Prefer **drag‑to‑dismiss** for drawers/toasts; apply **momentum + damping** to avoid abrupt stops.
- Add a **subtle background blur** behind toasts to emphasize priority without blocking content.
- Use a short **drag vs scroll debounce** (≈100ms) to prevent accidental dismiss.
- On mobile keyboards, consider the **Visual Viewport API** to keep panels visible.

## Menus + dropdowns
- **Origin‑aware dropdowns** feel better; Radix/BaseUI support this with CSS vars.
- Animated navigation can be built with **Radix Navigation Menu** (Linear pattern).

## System polish / perceived speed
- For mutation UX, run **mutation + delay in parallel** (e.g., `Promise.all`) so waits don’t stack.
- A **short artificial delay** after a write can boost confidence that it “saved.”
- For theme bar color transitions, **precompute easing** and animate in small steps if CSS isn’t supported.

## Motion primitives to pair with interactions
- **Clip‑path** is a powerful tool for distinctive UI motion (use sparingly, keep performant).

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
