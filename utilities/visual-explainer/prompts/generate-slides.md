---
description: Generate a complete slide-deck HTML explainer and open it in the browser
skill: visual-explainer
---
Generate a slide deck for: $@

Follow the visual-explainer skill in **Slide Deck Mode**.

Required behavior:
- Treat this as explicit slide intent (`--slides` semantics).
- Before writing output, read:
  - `./references/slide-patterns.md`
  - `./templates/slide-deck.html`
  - `./references/css-patterns.md`
  - `./references/libraries.md`
- Build a coverage map first (source sections/decisions/spec points -> planned slides), then generate.
- Preserve content completeness: do not silently drop sections; add slides instead of over-compressing.
- Use slide-native structure (Title, Divider, Content, Split, Diagram, Dashboard, Table, Code, Quote, Full-Bleed) with varied composition and pacing.
- If `surf` is available (`which surf`), optionally generate 2-4 supporting images when they materially improve comprehension.

Output:
- Write a self-contained HTML deck to `~/.agent/diagrams/` with a `-slides.html` suffix.
- Open it in the browser.
- Report the final file path.
