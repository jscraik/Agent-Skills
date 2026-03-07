# Jhey Tompkins Persona Evidence (2013-2026)

## Table of Contents
- [Identity and disambiguation](#identity-and-disambiguation)
- [Primary source map](#primary-source-map)
- [Timeline highlights](#timeline-highlights)
- [Technique highlights: Building a Drawer: The Versatility of Popover (2024-10-30)](#technique-highlights-building-a-drawer-the-versatility-of-popover-2024-10-30)
- [Technique highlights: Time Travel with JavaScript (2025-04-12)](#technique-highlights-time-travel-with-javascript-2025-04-12)
- [Technique highlights: You can scroll things (2025-01-10)](#technique-highlights-you-can-scroll-things-2025-01-10)
- [Technique highlights: Muddling your words (2024-12-12)](#technique-highlights-muddling-your-words-2024-12-12)
- [Technique highlights: Sliders: Range Inputs in Disguise (2024-11-14)](#technique-highlights-sliders-range-inputs-in-disguise-2024-11-14)
- [Technique highlights: The Path To Awesome CSS Easing With linear() (2023-09-22)](#technique-highlights-the-path-to-awesome-css-easing-with-linear-2023-09-22)
- [Technique highlights: 3D CSS Flippy Snaps With React And GreenSock (2021-11-29)](#technique-highlights-3d-css-flippy-snaps-with-react-and-greensock-2021-11-29)
- [CodePen pattern refresh (2026-03-06)](#codepen-pattern-refresh-2026-03-06)
- [Skill evidence matrix](#skill-evidence-matrix)
- [Notable code artifacts](#notable-code-artifacts)
- [Code artifact catalog (C-series)](#code-artifact-catalog-c-series)
- [Talk highlights](#talk-highlights)
- [Gaps and assumptions](#gaps-and-assumptions)
- [Suggested metadata schema](#suggested-metadata-schema)

## Identity and disambiguation
- Canonical identity for this persona: **Jhey Tompkins** (`jh3y`, `@jh3yy`).
- Common misspellings in user prompts: **Jhey Thomkins**, **Jhey Tomkins**.
- Keep persona routing resilient to misspellings, while preserving canonical naming in outputs.

## Primary source map
- Official site: <https://www.jhey.dev/>
- GitHub: <https://github.com/jh3y>
- Smashing author page: <https://www.smashingmagazine.com/author/jhey-tompkins/>
- DEV profile: <https://dev.to/jh3y>
- Medium profile: <https://jh3y.medium.com/>
- The Craft of UI (Substack): <https://craftofui.substack.com/>
- Slide decks hub: <https://jhey-presents.netlify.app/>
- Pixel Pioneers schedule/interview: <https://pixelpioneers.co/events/bristol-2022>
- Hey! Presents talk page: <https://heypresents.com/talks/take-your-skills-to-the-moon-with-creative-coding>

## Timeline highlights

### Early era (2014-2016)
- 2014-04-16 — Medium: Parsing config for custom builds with gulp.
- 2014-09-29 — `whirl` release (MIT): CSS loading animation library.
- 2014 — `sike` (MIT): Node CLI wellbeing/reminder tool.
- 2015-10-08 — Medium: caret/cursor XY positioning article.

### Growth era (2020-2023)
- 2020-07-17 — Smashing: creative wellness article.
- 2020-11-25 — Smashing: playfulness as learning strategy.
- 2021-10-04 — Kent C. Dodds chat transcript on building demos.
- 2021-11-29 — Smashing: 3D CSS Flippy Snaps with React and GreenSock.
- 2022-06-10 — Pixel Pioneers talk: creative coding skill growth.
- 2023-09-22 — Smashing: CSS `linear()` easing deep dive.

### Current era (2024-2026)
- 2024-10-30 — Craft of UI starts (Popover drawer post).
- 2025-04-12 — Craft of UI: “Time Travel with JavaScript”.

## Technique highlights: Building a Drawer: The Versatility of Popover (2024-10-30)
- Centers the Popover API as a native primitive (`top layer`, light dismiss, `::backdrop`) and layers enhancements instead of rebuilding disclosure mechanics from scratch.
- Uses discrete transitions with `@starting-style` and avoids brittle timeout-based choreography.
- Implements gesture-like drawer interaction with CSS `scroll-snap` plus `scrollsnapchange` (or IntersectionObserver fallback) to close when snapped out.
- Adds scroll-driven polish (backdrop scaling/custom properties), and addresses mobile keyboard/viewports via `visualViewport` and `interactive-widget` behavior.

## Technique highlights: Time Travel with JavaScript (2025-04-12)
- Uses a split-flap board build to teach a general animation pattern: animate a timeline playhead (`totalTime`) rather than directly animating every state transition.
- Demonstrates a forward-only “time scrub” approach with modulo wrapping to avoid reverse/DOM duplication tricks when looping characters.
- Contrasts GSAP and WAAPI implementations: GSAP for concise timeline control and easing; WAAPI as dependency-free alternative with more manual orchestration.
- Re-emphasizes platform-first thinking (CSS clipping/3D/perspective for visual mechanics) with JavaScript used as the control layer where it adds leverage.

## Technique highlights: You can scroll things (2025-01-10)
- Uses semantic markup (heading + list) and calls out screen-reader implications early, reinforcing accessibility-first framing for visual effects.
- Combines `position: sticky` with `scroll-snap` (`proximity`, not `mandatory`) for controlled yet natural scrolling behavior.
- Shows CSS-first scroll animation via `view()` timeline and `animation-range`, then provides a JavaScript fallback (GSAP + ScrollTrigger) only when feature support is absent.
- Uses custom properties for indexed color ramps in `oklch` and progressive enhancement touches like dynamic `scrollbar-color`/`@property` where supported.

## Technique highlights: Muddling your words (2024-12-12)
- Frames text scrambling with accessibility constraints first (for example `aria-label` or screen-reader-only fallback content).
- Demonstrates both JavaScript and CSS implementations, explicitly discussing tradeoffs in randomness, interaction ergonomics, and compositing behavior.
- Shows progressive enhancement and motion preference gating (`prefers-reduced-motion`) for hover/focus-driven effects.
- Covers multiple implementation patterns: imperative `requestAnimationFrame`, GSAP plugin approach, pseudo-element keyframes, and composited track-translation with `steps()`.

## Technique highlights: Sliders: Range Inputs in Disguise (2024-11-14)
- Re-centers implementation on native range input primitives instead of rebuilding controls with `div`-heavy interaction layers.
- Uses CSS scroll/view timeline APIs to derive a normalized slider progress custom property, with JavaScript synchronization as a capability fallback.
- Demonstrates platform-aware details: Safari `tabindex` considerations, vertical slider orientation via `writing-mode`, and preserving native touch/keyboard behavior.
- Emphasizes styling from a value pipeline (`--slider-complete`) so advanced visuals (counters, color, 3D/overscroll effects) remain tied to accessible native input mechanics.

## Technique highlights: The Path To Awesome CSS Easing With linear() (2023-09-22)
- Establishes easing literacy as a UX quality lever and positions `linear()` (CSS Easing Level 2) as a way to approximate spring/bounce-like motion directly in CSS.
- Bridges ecosystem workflows by converting GSAP-style ease functions into CSS `linear()` curves, reinforcing a practical platform-first migration path.
- Includes progressive enhancement guidance (`@supports`) so advanced timing functions degrade safely.
- Shows implementation breadth (raw CSS variables, generated eases, and Tailwind extension patterns) focused on production usability, not just demos.

## Technique highlights: 3D CSS Flippy Snaps With React And GreenSock (2021-11-29)
- Shows a demo-first learning workflow: break the effect into mechanics (grid, card faces, transforms) before framework concerns.
- Uses CSS custom properties as a bridge between declarative styling and JS/React state (`--count`, `--x`, `--y`, image URLs), keeping visual logic mostly in CSS.
- Applies GSAP `distribute` utilities for burst-like staggered motion and interaction polish, with explicit anti-spam interaction gating.
- Calls out practical constraints (grid-size performance, browser differences), reinforcing “playful but production-aware” experimentation.

## CodePen pattern refresh (2026-03-06)
- Added a **12-demo reference bundle** from current CodePen work in:
  `references/codepen-patterns-2026-03.md`.
- This refresh strengthens “real-life code” coverage for:
  - Anchor Positioning and `:has()` interaction patterns (`qEbVOMm`, `wvLvYWo`)
  - Scroll-linked progressive enhancement with JS fallback (`MYgaaem`, `raebqbQ`)
  - Native-control-first component work (`vEGobqb`)
  - SVG/WebGL interaction craft (`PwzeRwy`, `azZbyRe`, `pvyZZmO`)
  - Pointer-reactive CSS variable systems (`WbwyGBb`, `WbwZaNa`)
- Retrieval note: in this environment, direct `codepen.io` fetches were Cloudflare-blocked; debug endpoints (`cdpn.io`) were used for code validation.

## Skill evidence matrix
| Skill | Evidence |
|---|---|
| CSS animation systems | `whirl` (MIT), move-things-with-css, Smashing easing + playfulness |
| Advanced CSS / modern APIs | Craft of UI Popover drawer, CSS anchoring-related deck coverage, DEV clipping paths |
| Creative UI prototyping | Pixel Pioneers + Hey! Presents talks, Craft of UI posts |
| JavaScript + GSAP | Smashing audio visualization/sliders, DEV meta GSAP infinite scrolling, `gsap-eases.css` gist |
| React | Smashing Whac-A-Mole, 3D Flippy Snaps, audio visualization series |
| Node tooling | `sike` CLI, Medium Node CLI/task-runner/npm scripts articles |
| Teaching / speaking | SmashingConf workshop, Pixel Pioneers, State of the Browser segments, Config session |

## Notable code artifacts
- `whirl`: <https://github.com/jh3y/whirl>
- `move-things-with-css`: <https://github.com/jh3y/move-things-with-css>
- `gsap-eases.css` gist: <https://gist.github.com/jh3y/1b3afdfa7af3ebc5668bf169cea17d09>
- `getCursorXY.js` gist: <https://gist.github.com/jh3y/6c066cea00216e3ac860d905733e65c7>

## Code artifact catalog (C-series)
| ID | Date (evidence) | Project | Type | URL | Summary | Skills demonstrated | License | Copyright status | Relevance |
|---|---|---|---|---|---|---|---|---|---|
| C-01 | 2014-09-29 (release tag) | whirl | Repo | <https://github.com/jh3y/whirl> | CSS loading animations packaged for easy use; high adoption signals practical craftsmanship. | CSS animation library design, packaging, docs | MIT | Open source | 5 |
| C-02 | 2014 (copyright line) | sike | Repo | <https://github.com/jh3y/sike> | Node CLI that reminds users to move at intervals; shows empathy + tooling. | Node CLI, scheduling, terminal UX | MIT | Open source | 4 |
| C-03 | 2016 (README sign-off year) | stationery-cabinet | Repo | <https://github.com/jh3y/stationery-cabinet> | Local boilerplate/workflow for building and deploying many CodePen creations. | Tooling, templating, build pipelines, creative practice | Unknown (verify per repo) | Open source (assumed) | 5 |
| C-04 | 2020 (repo statement) | move-things-with-css | Repo | <https://github.com/jh3y/move-things-with-css> | Companion code for an ebook on CSS animations/transitions. | Curriculum-driven code, CSS motion | MIT | Open source | 5 |
| C-05 | Pinned (date not extracted) | vincent-van-git | Repo | <https://github.com/jh3y/vincent-van-git> | Turns GitHub commit history into a “canvas”; emblematic playful tooling artifact. | Data visualization, automation, creative tooling | Unknown (verify per repo) | Open source (verify) | 5 |
| C-06 | 2016-10-05 (last active) | carousel.css | Gist | <https://gist.github.com/jh3y/1f6029449ccaf1993e7ceba991772119> | Pure CSS carousel exploration; early CSS-first experimentation. | CSS-only interaction patterns | Not specified | Code snippet; copyright unclear | 4 |
| C-07 | 2023-02-26 (last active) | getCursorXY.js | Gist | <https://gist.github.com/jh3y/6c066cea00216e3ac860d905733e65c7> | Cursor coordinate utility tied to earlier caret-position writing. | DOM measurement, UI detail problem-solving | Not specified | Code snippet; copyright unclear | 4 |
| C-08 | 2023-07-12 (created) | theme-toggle.js | Gist | <https://gist.github.com/jh3y/0ef81d0f62c2bd2eef5bc99e0852a74e> | Netlify Edge function sketch for theme toggling. | Edge/serverless, theming, performance | Not specified | Code snippet; copyright unclear | 3 |
| C-09 | 2025-01-27 (last active) | magnify-this.js | Gist | <https://gist.github.com/jh3y/50b175c2a7bd48fbb7117053c3f3ce1e> | Bookmarklet-style magnifier utility with playful framing. | JS utilities, browser APIs | Not specified | Code snippet; copyright unclear | 3 |
| C-10 | 2025-12-10 (last active) | gsap-eases.css | Gist | <https://gist.github.com/jh3y/1b3afdfa7af3ebc5668bf169cea17d09> | Maps GreenSock-style easing to CSS `linear()` output. | CSS motion, tooling translation, animation literacy | Not specified | Code snippet; copyright unclear | 5 |

## Talk highlights
- 2022 — “Take your skills to the moon with creative coding” (Hey! Presents).
- 2022 — “Supercharge Your Skills with Creative Coding” (Pixel Pioneers).
- 2024 — “Design engineering — from design to engineer” (Config session listing).

## Gaps and assumptions
- Some sources are difficult to crawl fully (CSS-Tricks, CodePen, full X/Twitter corpus).
- Treat timeline as high-confidence but not exhaustive.
- Prefer primary links above for any future verification refresh.

## Suggested metadata schema
Use this metadata shape for future additions:

- `id`: (e.g., `W-07`)
- `title`
- `date`: `YYYY-MM-DD`
- `type`: `article | repo | gist | talk | interview | podcast`
- `url`
- `tags`: `[]`
- `skills`: `[]`
- `excerpt`: `<= 1-2 sentences`
- `license`: `MIT | Apache-2.0 | proprietary | unknown`
- `copyright`: `copyrighted | open-source | unclear`
- `relevance`: `1-5`
- `related_code`: `[]`
