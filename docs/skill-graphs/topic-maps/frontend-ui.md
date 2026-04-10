---
type: moc
name: frontend-ui
description: "Skills for building, designing, and testing frontend interfaces — UI systems, components, animations, accessibility, and visual tooling."
covers:
  - frontend-design
  - component-systems
  - visual-tooling
  - browser-automation
  - graphics-and-assets
---

# Frontend & UI

> Skills for building, designing, and testing frontend interfaces: UI systems, components, animations, accessibility, and visual tooling.

## Table of Contents
- [Design & Component Systems](#design--component-systems)
- [Visual & Creative Coding](#visual--creative-coding)
- [Browser Automation & Testing](#browser-automation--testing)
- [Graphics & Asset Generation](#graphics--asset-generation)
- [Accessibility & Metadata](#accessibility--metadata)

---

## Design & Component Systems

- [[design-system]] — Token-layer styling system: brand → alias → mapped; theme variables for monorepo UI work.
- [[frontend-ui-design]] — Production-ready UI systems and components with tokens and accessibility standards.
- [[react-ui-patterns]] — React UI composition patterns for TypeScript + Tailwind + Radix: state, routing, structure.
- [[baseline-ui]] — Validates animation durations, typography scale, component accessibility, and layout patterns in Tailwind CSS projects.
- [[shadcn-ui]] — Set up, add, adapt, and troubleshoot shadcn/ui components and registry items.
- [[stitch-react-components]] — Convert Stitch screens into modular Vite/React components with validated structure and style-system alignment.
- [[agentation]] — Install, verify, or troubleshoot Agentation in React/Next.js/Vite/Tauri apps.

## Visual & Creative Coding

- [[ui-ux-creative-coding]] — Polished motion + implementation artifacts in React/Tauri (Tailwind v4, Radix, optional Three.js).
- [[threejs-builder]] — Build and validate simple, performant Three.js web apps using modern ES module patterns.
- [[remotion]] — Best-practice guidance for Remotion (React video): compositions, timing, assets, audio, captions, rendering.
- [[stitch-remotion]] — Generate Stitch-to-Remotion walkthrough videos from screen assets.
- [[slides]] — Create, edit, and validate presentation decks (.pptx) with PptxGenJS and overflow checks.
- [[visual-explainer]] — Generate beautiful, self-contained HTML pages to visually explain systems, code changes, plans, or data.
- [[beautiful-mermaid]] — Render Mermaid diagrams to SVG and PNG.

## Browser Automation & Testing

- [[agent-browser]] — Deterministic browser automation via the agent-browser CLI using accessibility snapshots and ref-based interaction.
- [[playwright-interactive]] — Persistent Playwright session for iterative UI automation, visual QA, or Electron inspection.
- [[ui-visual-regression]] — Review and validate UI visual regression diffs (Storybook + Playwright + Argos).
- [[stitch-loop]] — Iterative autonomous website building with Stitch using a baton file for multi-pass page generation.

## Graphics & Asset Generation

- [[imagegen]] — Generate or edit images via the OpenAI Image API: text-to-image, inpaint/mask, background removal, product shots.
- [[nano-banana-builder]] — Web applications using Google Nano Banana image APIs for generation and iterative editing.
- [[sora]] — Generate, remix, poll, list, download, or delete Sora videos via the OpenAI video API.
- [[favicon-generator]] — Generate complete favicon/app icon suites with templates and assets.
- [[og-image-creator]] — Generate brand-aligned Open Graph images for existing routes via Playwright.
- [[better-icons]] — Search and extract SVG icons via the better-icons CLI or MCP from Iconify collections.
- [[agent-browser]] + [[frontend-ui-design]] — Capture hosted design references/screenshots and translate them into production-ready UI implementation guidance.

## Accessibility & Metadata

- [[fixing-accessibility]] — Audit and fix HTML accessibility issues: ARIA labels, keyboard navigation, focus management, color contrast.
- [[fixing-metadata]] — Audit and fix HTML metadata: titles, descriptions, canonical URLs, Open Graph tags, JSON-LD, robots directives.

---

## Cross-links

- Planning a new UI? Start with [[brainstorming]] → [[product-spec]] → [[frontend-ui-design]].
- Need icons or assets? [[better-icons]] and [[imagegen]] can supply raw materials for [[design-system]].
- Writing tests? Pair [[playwright-interactive]] with [[ui-visual-regression]].
- Topic maps: [[product-strategy]] | [[backend-platform]] | [[agent-ops]]
