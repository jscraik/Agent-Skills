# Outline — Web MCP and the Agentic Web — Maximiliano Firtman

## Speaker

**Maximiliano Firtman** ("Maxi") — web developer from Buenos Aires, Argentina. ~30 years as an app developer, ~third decade as web developer, also mobile. Author of books and online courses across multiple providers. Self-describes as a "[Google] ambassador" (transcript says "colleagues ambassador", clearly a speech-to-text artifact for "Google"). The session was opened/closed by **Simon Maple** (Head of Developer Relations at Tessl; AI Native Dev co-host) — but Simon's framing words are minimal and the bulk of the transcript is Firtman.

## Abstract

Not provided by the user. **[inferred]** A practical introduction to Web MCP — a proposed W3C standard, entering origin trial in Chrome 149 — that lets web developers expose explicit tools from the frontend to AI agents, replacing today's slow, expensive, error-prone screenshot/DOM-inference techniques. Covers the agentic-web problem space, contrast with MCP, tool anatomy, imperative and declarative APIs, a live Doom-playing demo, the Chrome DevTools MCP bridge for using Web MCP today from Claude Code / Cursor / Codex, and a concrete adoption recipe.

## Thesis (synthesis)

Agents need to operate the web, but inference-based approaches (HTTP fetch, accessibility-tree reading, browser plugins, computer use) burn time, tokens, and context. Web MCP flips this: instead of the agent guessing the UI, the web developer **declares** typed tools the agent can call directly, with full access to the live browser context the backend doesn't have (DOM state, forms, sensors, session, client APIs). MCP and Web MCP are complementary — MCP for backend/server tools, Web MCP for anything that lives in the frontend.

## Section TOC

| Section | Summary | Approx. transcript lines |
|---|---|---|
| 1. Speaker intro | Maxi introduces himself: Argentina, 30 years dev, books/courses, Google ambassador | top ~10 lines |
| 2. The agentic web — three vectors | Agents want to build web apps; web apps want to host agents (incl. "MCP apps" inside Claude/ChatGPT); users want to browse via agentic browsers (Atlas, Gemini in Chrome) | next ~15 lines |
| 3. The problem: how agents access the web today | Connectors, CLIs (npx), HTTP fetch, browser-use plugins, computer use — all costly in time/tokens/context | middle section |
| 4. World Cup web-app running example | Following FIFA-style site to find Round of 16 / semifinals / final info takes the agent minutes | embedded in §3 |
| 5. From inference to contract — Web MCP intro | Web MCP exposes capabilities (not pixels) from the frontend; tool = name + description + JSON schema + execute fn | mid-talk |
| 6. Why not just MCP? | MCP connects agents to backend; Web MCP exposes frontend context (DOM, forms, sensors, web serial, session storage) | mid-talk |
| 7. "Inspired by MCP, not the same protocol" | The "X is to Java" analogy; W3C-tracked, separate spec | mid-talk |
| 8. Origin trial status | Chrome 149 origin trial starting "tomorrow"; flag-enabled today; API may still change | mid-talk |
| 9. Tool object anatomy (imperative API) | `name`, `description` (written for AI), `inputSchema` (JSON schema), `execute` (async fn) | later |
| 10. Declarative API for forms | `tool` name, `tool description`, optional `tool auto submit`, per-field `tool param description` on form elements / web components | later |
| 11. Web MCP Inspector + World Cup demo | List of tools (get matches by date, get team matches, list rules, search matches…); agent calls multiple tools to answer "can Argentina and England meet in the final?" | later |
| 12. Doom demo | Firtman added Web MCP to an open-source Doom port; agent plays Doom via `move`, `rotate`, screenshot + position tools | later |
| 13. Using Web MCP today via Chrome DevTools MCP | Chrome DevTools is itself exposed as an MCP server; agent → DevTools MCP → headed Chrome → Web MCP tools. Puppeteer alt. | later |
| 14. Tool design guidance | One purpose per tool; state-aware registration; plain-language descriptions; strict types + meaningful errors; small outputs | near end |
| 15. Adoption recipe | Pick one high-value page state → expose a read-only diagnostic tool → evaluate with calls/arguments → automate via Chrome DevTools MCP or Puppeteer | near end |
| 16. Wrap + host close | Experimental, expose frontend tools, full browser context, available in origin trial / DevTools MCP / Puppeteer; Simon closes the session | end |

## Terminology glossary (speaker's definitions)

- **Agentic web** — Firtman's umbrella for three intertwined trends: *"agents want to build for the web"*, *"the web wants to run agents"*, and *"users want to browse the web using agents."*
- **MCP apps** — Web-like surfaces that run inside agent hosts: *"MCB apps [MCP apps], that are actually running, for example, inside Cloth [Claude] or inside JNDPT [ChatGPT]."*
- **Computer use** — Last-resort approach where the agent drives mouse/keyboard at the OS level because no programmatic path exists: *"they're just using computer usage that is just using your computer. Like using a mouse, cursor..."*
- **Web MCP** — *"a proposed standard API... from the W3C"* that *"let[s] the front end expose capabilities and not just fix it [pixels]"*; *"we are passing from inference to a contract that we as web developer define."*
- **Tool** (in Web MCP) — *"It's just can be a new function. It can be any form that you have in your website."* Object with name, description, input schema (JSON), and execute function.
- **Tool description** — *"the description should be... for Asians [agents]. So we need to understand that our customer is an AI agent. Not the user."*
- **Imperative API** — Register tools as JavaScript functions with `execute`.
- **Declarative API** — Annotate HTML form elements / web components with `tool`, `tool description`, optional `tool auto submit`, and `tool param description`.
- **Origin trial** — *"meaning that you can start using it with real users out there"* — i.e. opt-in production use tied to a domain, while spec is unstable.
- **Chrome DevTools MCP** — *"Chrome now is offering DevTools as an MCP tool and through that MCP tool you can actually run Web MCP"* — the bridge that makes Web MCP usable from Claude Code / Cursor / Codex today.

## Named frameworks / concepts

### A. The three vectors of the agentic web
1. Agents building web apps (vibe-coded output is mostly web apps).
2. Web apps hosting agents (injected agents; MCP apps inside Claude/ChatGPT/Webex; web inside agent hosts).
3. Users (and agents) browsing the web via agentic browsers (Chrome, Gemini-in-Chrome, ChatGPT Atlas).

### B. Today's agent-to-web techniques (and their costs)
- Connectors (vendor-built integrations).
- CLI / `npx` commands the agent invokes in terminal.
- Raw HTTP fetch — fails on SPAs because no JS executes.
- Browser-use plugins (Chrome-based) reading DOM / accessibility tree / screenshots.
- Computer use — driving the OS like a human. *"agents are burning Belgians [billions]. When the browser is just a... guessing game."*

### C. Web MCP tool object (imperative)
```
{
  name: <string>,
  description: <string written for an AI agent>,
  inputSchema: <JSON schema>,
  execute: async (args) => result
}
```

### D. Web MCP declarative form annotations
- `tool` — tool name (mandatory)
- `tool description` — mandatory
- `tool auto submit` — boolean; permits agent-driven submission
- `tool param description` — per-field, on inputs / textareas / selects / form-element web components, when the label alone isn't enough for an agent

### E. Tool design guidance
1. One purpose per tool — don't overlap.
2. State-aware registration — register/unregister as app state changes (e.g. logged-in vs logged-out).
3. Plain-language descriptions — the consumer is a model.
4. Strict types; return meaningful errors so the agent can iterate without human help.
5. Small outputs — return exactly what was requested.

### F. Adoption recipe (Firtman's one suggestion)
> Pick **one high-value page state**, expose a **read-only diagnostic tool** from it, evaluate by calling it with arguments from Claude Code / Cursor / Opencode, then automate via **Chrome DevTools MCP** or **Puppeteer**. Native agent support expected "in a couple of months."

## Open questions / not covered

- Concrete auth / permission model for Web MCP tools (who can call what, consent prompts).
- Non-Chromium browser support timelines (Safari, Firefox) — only Chrome 149 origin trial discussed.
- How Web MCP composes with multiple iframes / cross-origin embeds.
- Performance benchmarks vs HTTP fetch / browser-use beyond the "minutes → seconds" hand-wave.
- Security model for the Doom-style "let the agent play while I sleep" use case.
- Detailed comparison to existing accessibility APIs (ARIA) for agent consumption.
- How `tool auto submit` interacts with CSRF / one-time tokens.
- Pricing/token measurements — talk asserts savings but does not quantify.
