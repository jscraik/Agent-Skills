# Notes from reverse_engineering_techniques.pdf (summary)

## Scope covered in the PDF
- Web apps (React/SPAs)
- Open-source codebase analysis

## Web/React (high-level tools and themes)
- Browser DevTools as the primary inspection surface (Elements, Sources, Network).
- Bundled/minified JS can be pretty-printed for structure, but names are often obfuscated.
- Source maps (when present) can restore original file structure; treat availability and permissions carefully.
- Network traffic (REST/GraphQL/WebSocket) is a key source of evidence.

## OSS (high-level tools and themes)
- Start with docs, build/test, and use the software to understand intent.
- Use entry points, tests, and repo structure to build a mental model.
- Leverage git history to identify hotspots and evolution.
- Follow license and contribution guidance.

## Safety framing
- The PDF highlights legal/ethical constraints; use insights for education, security improvement, or interoperability, not IP misuse.
- This skill enforces non-circumvention and evidence-only outputs.
