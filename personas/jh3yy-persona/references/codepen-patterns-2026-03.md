# Jhey CodePen Pattern Pack (March 2026)

## Table of Contents
- [Purpose](#purpose)
- [Provenance](#provenance)
- [Pattern index](#pattern-index)
- [Code-backed references](#code-backed-references)
- [How to use in persona responses](#how-to-use-in-persona-responses)

## Purpose
Capture a concrete, code-backed set of recent Jhey demos that can be cited when users ask for “real examples” in `jh3yy-persona` responses.

## Provenance
- Canonical pen URLs come from user-provided references.
- Code snippets were validated from each pen’s debug source endpoint (`https://cdpn.io/jh3y/debug/<slug>`) on **2026-03-06**.
- Note: direct `codepen.io` page fetches were Cloudflare-blocked in this CLI context; `cdpn.io` debug pages provided accessible compiled HTML/CSS/JS.

## Pattern index

| Slug | Title | Primary primitives |
|---|---|---|
| `qEbVOMm` | progressive anchor pagination | Anchor Positioning, `:has()`, reduced-motion gates, JS readiness fallback |
| `MYgaaem` | you can scroll. | Scroll-driven animation timelines, `@property`, `oklch`, GSAP fallback |
| `wvLvYWo` | Cuisine Selector with :has() | `:has()`, `linear()` easing curve tuning, intent/active state composition |
| `LYNZwGm` | Impossible Checkbox v2 🐻 | React + GSAP interaction orchestration, audio cues, playful state escalation |
| `PwzeRwy` | "noise" webgl button for web | WebGL shaders + GSAP-driven parameter modulation |
| `azZbyRe` | destination slider w/ svg + gsap 🧑‍🍳 | SVG path recomputation + GSAP interpolation + pointer activation |
| `vEGobqb` | quantity picker w/ [type=number] 👨‍🍳 | Custom element wrapping native `type="number"` with accessibility states |
| `raebqbQ` | CSS scroll-triggered pop out images [Chrome 145+] | CSS timeline/trigger APIs for layered pop-out transitions |
| `pvyZZmO` | image pixelation w/ svg 🤙 | SVG filter pipeline (`feMorphology`, `feComposite`, `feFlood`) + GSAP controls |
| `XJdLrZV` | subtle css border pulse effect | Layered pseudo-element pulse feedback on interaction states |
| `WbwyGBb` | masked inset border shine ☀️ | Pointer-angle-driven CSS masking + runtime pointer tracking |
| `WbwZaNa` | context aware :hover cards w/ blur 👨‍🍳 | Container-query sizing + pointer-aware CSS variable parallax |

## Code-backed references

### 1) `qEbVOMm` — progressive anchor pagination
- Pen: <https://codepen.io/jh3y/pen/qEbVOMm>
- Debug source: <https://cdpn.io/jh3y/debug/qEbVOMm>
- Evidence:
```css
@supports (anchor-name: --pagination) { ... }
position-anchor: --pagination-active;
```
```js
requestAnimationFrame(() => {
  pagination.dataset.ready = true;
});
```

### 2) `MYgaaem` — you can scroll.
- Pen: <https://codepen.io/jh3y/pen/MYgaaem>
- Debug source: <https://cdpn.io/jh3y/debug/MYgaaem>
- Evidence:
```css
@supports (animation-timeline: scroll()) and (animation-range: 0% 100%) { ... }
animation-timeline: --list;
view-timeline: --list;
```
```js
if (!CSS.supports('(animation-timeline: scroll()) and (animation-range: 0% 100%)')) {
  gsap.registerPlugin(ScrollTrigger);
}
```

### 3) `wvLvYWo` — Cuisine Selector with :has()
- Pen: <https://codepen.io/jh3y/pen/wvLvYWo>
- Debug source: <https://cdpn.io/jh3y/debug/wvLvYWo>
- Evidence:
```css
--ease: linear(0 0%, ... , 1 100%);
label:has(:focus-visible),
label:hover { ... }
```

### 4) `LYNZwGm` — Impossible Checkbox v2 🐻
- Pen: <https://codepen.io/jh3y/pen/LYNZwGm>
- Debug source: <https://cdpn.io/jh3y/debug/LYNZwGm>
- Evidence:
```js
const { React: { useState, useRef, useEffect }, gsap: { to, timeline } } = window;
const SOUNDS = { ON: new Audio(...), OFF: new Audio(...), GROAN: new Audio(...) };
const [checked, setChecked] = useState(false);
```

### 5) `PwzeRwy` — "noise" webgl button for web
- Pen: <https://codepen.io/jh3y/pen/PwzeRwy>
- Debug source: <https://cdpn.io/jh3y/debug/PwzeRwy>
- Evidence:
```js
const vertexShaderSource = `...`;
const fragmentShaderSource = `... uniform float u_noiseType; ...`;
const gl = this.canvas.getContext('webgl', { alpha: false, antialias: true });
```

### 6) `azZbyRe` — destination slider w/ svg + gsap 🧑‍🍳
- Pen: <https://codepen.io/jh3y/pen/azZbyRe>
- Debug source: <https://cdpn.io/jh3y/debug/azZbyRe>
- Evidence:
```js
const updatePath = (value = undefined, bumpHeightParam = undefined) => { ... };
const pathData = `M ${pathStartX} ${baselineY} ...`;
gsap.to(pathElement, { attr: { d: pathData } });
```

### 7) `vEGobqb` — quantity picker w/ [type=number] 👨‍🍳
- Pen: <https://codepen.io/jh3y/pen/vEGobqb>
- Debug source: <https://cdpn.io/jh3y/debug/vEGobqb>
- Evidence:
```js
class QuantityPicker extends HTMLElement { ... }
static get observedAttributes() { return ['min', 'max', 'step', 'value', ...]; }
customElements.define('quantity-picker', QuantityPicker);
```
```html
<input type="number" min="..." max="..." step="..." />
```

### 8) `raebqbQ` — CSS scroll-triggered pop out images [Chrome 145+]
- Pen: <https://codepen.io/jh3y/pen/raebqbQ>
- Debug source: <https://cdpn.io/jh3y/debug/raebqbQ>
- Evidence:
```css
timeline-trigger: var(--trigger-name) view() cover 40% exit 200%;
animation-trigger: var(--trigger-name) play-forwards play-backwards;
```

### 9) `pvyZZmO` — image pixelation w/ svg 🤙
- Pen: <https://codepen.io/jh3y/pen/pvyZZmO>
- Debug source: <https://cdpn.io/jh3y/debug/pvyZZmO>
- Evidence:
```js
gsap.set('feMorphology', { attr: { operator: config.operator, radius: config.radius } });
document.startViewTransition(() => update());
```

### 10) `XJdLrZV` — subtle css border pulse effect
- Pen: <https://codepen.io/jh3y/pen/XJdLrZV>
- Debug source: <https://cdpn.io/jh3y/debug/XJdLrZV>
- Evidence:
```css
[data-border-pulse] { ... }
&:is(:hover, :focus-visible)::before { opacity: 0.26; }
```

### 11) `WbwyGBb` — masked inset border shine ☀️
- Pen: <https://codepen.io/jh3y/pen/WbwyGBb>
- Debug source: <https://cdpn.io/jh3y/debug/WbwyGBb>
- Evidence:
```css
mask: linear-gradient(calc(var(--pointer-angle) * 1deg), ...);
```
```js
const calculateAngle = event => { ... };
iconButton.style.setProperty('--pointer-angle', angleDegrees.toFixed(2));
```

### 12) `WbwZaNa` — context aware :hover cards w/ blur 👨‍🍳
- Pen: <https://codepen.io/jh3y/pen/WbwZaNa>
- Debug source: <https://cdpn.io/jh3y/debug/WbwZaNa>
- Evidence:
```css
article { container-type: size; ... }
translate: calc(var(--pointer-x, -10) * 50cqi) calc(var(--pointer-y, -10) * 50cqh);
```
```js
document.addEventListener('pointermove', event => {
  article.style.setProperty('--pointer-x', x.toFixed(3));
});
```

## How to use in persona responses
1. If the user asks for “real code” or “references,” cite **1-3 pens** from this pack by slug/title.
2. Name the exact primitive(s) the user should transfer (for example `animation-timeline`, Anchor Positioning, native custom elements, SVG filters).
3. Include one adaptation step that fits the user’s stack (React, Vue, vanilla, design-system tokens, etc.).
4. Preserve the persona’s platform-first stance: CSS/native first, JS layered in only when it adds measurable value.
