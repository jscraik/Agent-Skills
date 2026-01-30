# UI/UX Creative Coding — Canonical Examples (Jan 2026)

These examples are **format‑correct** and intentionally short. Use them to keep outputs consistent.

---

## Example 1 — General UI direction (no persona)

**Prompt:**
Design a settings screen for a Tauri app. Keep it concise and include the standard headings.

**Response (canonical):**

```
## When to use
- For desktop settings screens that need clear hierarchy and light motion feedback.

## Inputs
- Audience: desktop users, keyboard‑first
- Required: reduced‑motion support
- Components: toggles, segmented control, account panel

## Outputs
- **Hierarchy:** Account → Preferences → System; section labels + helper text.
- **Motion:** 120–180ms ease‑out on toggle/segment change; no layout shifts.
- **Accessibility:** focus states, semantic groups, reduced‑motion parity.
- **Polish:** soft card radius, low‑contrast dividers, strong CTA hierarchy.
- **Next step:** confirm which preferences require confirmation modals.
```

---

## Example 2 — @jh3yy persona (CSS‑first micro‑interaction)

**Prompt:**
Use the ui-ux-creative-coding skill to design a table‑of‑contents marker. Apply @jh3yy’s persona.

**Response (canonical):**

```
## When to use
- For content pages that need a lightweight, CSS‑first active‑section marker.

## Inputs
- TOC structure + anchor links
- Must be CSS‑only with progressive enhancement

## Outputs
- **@jh3yy — references/jhey-tompkins-persona.md** 🧑‍🍳
- **CSS‑only anchor marker (no JS):**
  ```css
  .toc { scroll-target-group: auto; }
  a:target-current { anchor-name: --active; }
  .toc::after { position-anchor: --active; top: anchor(top); }
  ```
- **States:** focus + active styles; visible indicator width ≥ 2px.
- **Performance:** transforms only; no layout thrash.
- **Next step:** confirm reduced‑motion fallback styling.
```

---

## Example 3 — @kubadesign persona (landing page refresh)

**Prompt:**
Use the ui-ux-creative-coding skill to outline a landing page refresh. Apply @kubadesign’s persona.

**Response (canonical):**

```
## When to use
- For product landing pages that need sharper visual hierarchy and conversion focus.

## Inputs
- Current hero + CTA copy
- Target conversion action

## Outputs
- **@kubadesign — references/kubadesign-persona.md**
- **Layout:** hero → proof strip → feature grid → CTA band.
- **Visual levers:** try 2–3 Midjourney prompt tweaks (e.g., `--sref`, `--stylize`) for gradients.
- **Polish:** rounded cards + soft shadows + bold hero headline.
- **Next step:** pick 2 hero variants for A/B testing.
```

---

## Example 4 — @benjitaylor persona (developer tool refinement)

**Prompt:**
Use the ui-ux-creative-coding skill to refine a developer tool UI. Apply @benjitaylor’s persona.

**Response (canonical):**

```
## When to use
- For developer tools that need clearer feedback loops and interaction polish.

## Inputs
- Current UI states (idle/loading/error)
- Target workflows: inspect → adjust → export

## Outputs
- **@benjitaylor — references/benjitaylor-persona.md**
- **Feedback loops:** inline status row + success toast + retry on failure.
- **Interaction polish:** hover/focus states on icon grid; 120ms ease‑out.
- **Developer UX:** keyboard shortcuts + copy‑to‑clipboard affordance.
- **Next step:** confirm the top 3 workflows to prioritize in v1.
```

---

## Example 5 — @emilkowalski persona (motion system)

**Prompt:**
Use the ui-ux-creative-coding skill to outline a motion system for a dashboard. Apply @emilkowalski’s persona.

**Response (canonical):**

```
## When to use
- For dashboards that need subtle, readable motion to communicate state.

## Inputs
- Core states: loading → ready → error
- Components: cards, charts, alerts

## Outputs
- **@emilkowalski — references/emilkowalski-persona.md**
- **Motion rules:** 140–200ms ease‑out for state transitions; 240ms for modal entry.
- **State clarity:** animate opacity/transform only; no layout reflow.
- **Education:** document the 3 primary easing curves with usage notes.
- **Next step:** confirm reduced‑motion fallback (fade‑only).
```
