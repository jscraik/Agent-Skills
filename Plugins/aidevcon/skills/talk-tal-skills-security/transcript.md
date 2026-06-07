# Transcript -- Your AI Agent Installed Malware Because a SKILL.md Told It To

**Speaker:** Liran Tal (Snyk)
**Source:** /Users/baptistefernandez/Desktop/DevCon2026-Liran-Tal.txt

## Source Status

The source transcript for this session contains a live security demonstration. This published transcript artifact is intentionally safety-redacted: it preserves the defensive concepts, review model, and governance lessons while omitting concrete operational mechanics, payload details, secret-handling paths, and step-by-step misuse examples.

## Talk Substance

Liran Tal frames AI-agent skills as supply-chain artifacts. Because a skill can shape what an agent reads, how it reasons, and what actions it may attempt, teams need to review skills with the same seriousness they apply to third-party packages and automation scripts.

The talk contrasts superficial checks with semantic review. A file can look harmless at the naming or formatting level while still creating risky behavior through natural-language instructions, permission assumptions, or hidden context paths. The defensive response is layered review: provenance checks, ownership checks, permission review, sandboxing, behavioral analysis, and clear human approval boundaries.

## Preserved Concepts

- Skills as dependency-like artifacts.
- Provenance and ownership checks before adoption.
- Permission review for data access and action surfaces.
- Sandboxing and least-privilege execution for agent workflows.
- Semantic review that looks at what a skill causes an agent to do.
- Alert and approval design that reduces warning fatigue.

## Advisory Takeaway

The session's practical message is defensive: teams should build a skill intake process, inspect capability boundaries, and avoid treating natural-language skill files as harmless documentation.
