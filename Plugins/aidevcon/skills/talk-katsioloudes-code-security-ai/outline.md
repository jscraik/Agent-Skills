# Outline — Code Security Reinvented: Navigating the era of AI

## Speaker

**Joseph Katsioloudes** — Senior Developer Advocate at GitHub, working on the GitHub Security Lab team (a team of security experts whose mission is to secure the open source software we all rely on, via research, education, and other activities). He has spoken in 25+ countries, has 2.8M+ video views, and created the open-source security training game at `gh.io/scg` used by 10,000+ developers.

## Participants

- **Joseph Katsioloudes** — speaker.
- **Macy** — emcee for the room ("the tool room" / "tool called" per the garbled transcript), giving intro and outro and a workshop the next day.
- **Two audience members** during Q&A — unnamed:
  - **Q1** asks about false positives / hallucinations burning developer time.
  - **Q2** asks about "AI as judge" / dual-LLM patterns.

## Abstract (verbatim, as provided)

> While the process of building software has become easier and faster, the question remains: is it becoming more secure?
>
> With 1 security specialist for every 100 developers, AI can scale scarce security expertise and embed it into daily workflows. In this session, we will demonstrate how to leverage collective security knowledge through 12 practical demos. You will see how to use — and not use — AI to write safer code (3 demos), benefit from MCP servers, skills, and agentic workflows (3 demos), make informed supply chain decisions (2 demos), remediate security alerts faster (2 demos), and strengthen developer security education (2 demos).
>
> AI, however, is not perfect. We will examine its limitations, explain why they exist, and highlight the gaps that matter for responsible use.

## Thesis (synthesis)

There is one application security specialist for every 100 developers; AI can close that gap, but only if used responsibly. Hallucinations and non-determinism are real and persistent, so AI is best used as a **reasoning layer on top of deterministic detection tooling** rather than as a replacement for it. The combination of MCP servers (capability), skills (process/structure), and agentic workflows (tailored automation) — kept inside the PR where developers already work, with least-privilege boundaries — is what turns AI from a hallucinating assistant into a security force-multiplier. Education and SLOs that make security part of developers' performance objectives are the human half of the same equation.

## Section TOC

| # | Section | Summary | Approx. transcript lines |
|---|---|---|---|
| 1 | Emcee intro | Macy introduces Joseph and the "tool room" framing. | 1–35 |
| 2 | Opening + GitHub Security Lab context | Joseph's team, research examples (Ruby, zip buffer overflow), 1000+ vulns found and helped fix. | 36–70 |
| 3 | The 1-to-100 security gap | The core problem the talk addresses. | 70–95 |
| 4 | Writing safer code — start left, not shift left | 3 demos showing hallucinations and non-determinism in early Copilot. | 95–180 |
| 5 | AI as reasoning layer, not detection | "We don't have a detection problem — we have a fixing problem." | 180–215 |
| 6 | MCP — Model Context Protocol | What MCP is, security caveats, AI vs SAST tradeoffs. | 215–280 |
| 7 | Skills | Skills give structure to MCP capability. The MCP↔skills↔agents diagram. | 280–325 |
| 8 | Remediation in the PR — Copilot Autofix | Past dashboard view → present in-PR fixes; 3x faster, 600 vulns in 2 weeks. | 325–380 |
| 9 | Agentic workflows | Tailored security agents, agents.md split, online GitHub agent-workflows library. | 380–435 |
| 10 | Task flows for vulnerability finding | Codifying security-researcher knowledge; `gh.io/taskflows`. | 435–470 |
| 11 | Supply chain decisions | 4 free instruction files at `gh.io/sk`, Bootstrap example. | 470–520 |
| 12 | AI-assisted fuzzing | AI generates millions of inputs + harnesses, accelerating fuzzing. | 520–545 |
| 13 | Education — `gh.io/scg` playground | Hands-on sandbox: prompt-injection, multi-agent attacks, agentic workflows in a simulated internet. | 545–600 |
| 14 | Wrap-up | Summary of the five areas. | 600–625 |
| 15 | Q&A 1 — false positives burning dev time | Multi-model aggregation, multi-run, trust a vendor, education, **SLOs tied to performance**. | 625–700 |
| 16 | Q&A 2 — AI-as-judge / dual LLM | Useful but bypassable; "I attack your house to succeed once"; least privilege is the #1 thing. | 700–770 |
| 17 | Emcee outro | Wrap-up, coffee break. | 770–end |

## Terminology glossary (Joseph's framings)

- **The security gap** — "there is just one application security specialist for every 100 software developers."
- **Start left** (vs shift left) — "The problem when you shift left is that you keep having a gap on the left. The whole point and the opportunity here is to start left."
- **Fixing problem, not detection problem** — "in cyber security, we have a fixing problem. We have so much ways to find what's wrong. And we don't have the ways to minimize that gap by get up to the fixing speed."
- **AI as reasoning layer** — use deterministic tools for detection, AI to reason about how to fix.
- **Non-determinism** — same question + same code gives different vuln lists across runs; reducing context can make a real vuln disappear. "this is not determinism at its best."
- **Hallucinations** — Joseph's early-Copilot example flagged "passwords in plain text" that wasn't actually a real finding; "we will never get away with zero hallucinations."
- **MCP (Model Context Protocol)** — "designed by Anthropic… in order to help the AI models to go outside of their small and narrow training books. Help us access server[s], silo[s] from information."
- **Skills** — give structure/process on top of MCP capability. "if you have MCPs without skills that are going to give structure, your AI agents are just going to have capability but without… your process." Auditable, maintainable, extensible.
- **Agentic workflows** — schedule- or event-triggered agents running on the same VMs as GitHub Actions; "tailored" is the key advantage over SAST.
- **agents.md split** — Joseph notes that putting all rules into one script "bloats the AI context"; some things belong in `agents.md`, some in skill files, some in scripts.
- **Task flows** — codified knowledge of security researchers, used to steer models toward vulnerabilities; free at `gh.io/taskflows`.
- **Copilot Autofix** (transcript: "Copilot Topics") — fixes proposed directly in the PR, with explanations grounded in deterministic SAST findings; "they have fixed 600 vulnerabilities in two weeks bringing the fixed rate to the top."
- **Dual LLM / LLM-as-judge** (transcript: "Llamas… LLM jury") — second LLM judges the first's output. "it's working… it's a mitigation. If you don't [do] output filtering, input filtering, I'm not a big fan."
- **Least privilege for AI** — "AI shouldn't be touching anything sensitive because assume it's gonna take it" / "agents should have… boundaries."
- **Fuzzing (with AI)** — AI generates "this million of inputs and the boilerplates and also the hardness" to attack code in a safe way.
- **Security SLOs** — Joseph's recommendation: "this is your allowance for open security problems with that specific severity score and anything else is not accepted because you don't pass the service level objectives" — tied to developers' performance objectives.

## Named frameworks / concepts introduced

1. **The 1-to-100 gap** as the framing problem.
2. **Start left** rather than shift left.
3. **MCP × Skills × Agentic workflows** layering — capability + process + tailored automation.
4. **AI as reasoning layer on top of deterministic detection** — and the corresponding **MCP-vs-SAST comparison**: AI is good at systematic/contextual issues (crypto primitives, sensitive-data placement) but non-deterministic and expensive; SAST is deterministic and mature but pattern-matching.
5. **The five-area map of "AI for security" use cases** (matches the abstract's 12 demos):
   - Writing safer code (3 demos)
   - MCP servers, skills, agentic workflows (3 demos)
   - Supply chain decisions (2 demos)
   - Remediating alerts faster (2 demos)
   - Developer security education (2 demos)
6. **Free open-source resources**:
   - `gh.io/scg` — hands-on security-training playground / "secure code game"-style sandbox.
   - `gh.io/sk` — 4 supply-chain-decision instruction files.
   - `gh.io/taskflows` — task flows for vulnerability finding.
   - GitHub's online library of agent workflows (auto-review, triage).
7. **agents.md split** — separating context, skills, and scripts to avoid bloating the AI context.
8. **Dual-LLM / LLM-as-judge** with explicit acknowledgment of its limits.
9. **Security SLOs tied to performance objectives** as the organisational lever.
10. **AI-defense layers**: least-privilege first, then input/output filtering, then LLM-as-judge — in that priority order.

## Open questions / not covered

- Specific cost figures or token budgets for multi-model / multi-run aggregation strategies.
- Concrete numeric SLO targets ("allowance for open security problems") — Joseph describes the shape but not the numbers.
- Detailed comparison between specific commercial tools beyond name-checks (Semgrep, SonarQube, CodeQL).
- Compliance / regulatory frameworks (SOC2, ISO27001, etc.) — not discussed.
- How to evaluate or pick between models for security tasks — Joseph explicitly says "it's not about models, it's about the rest of things… you can cheat more when you have better scaffolding."
- Privacy/data-residency specifics beyond a brief mention that the GitHub Copilot Trust Center has Q&A on certificates and context leakage.
- IDE-specific guidance beyond "whatever I show you, you can do also in CodeX. Not just GitHub Copilot."
- Threat modeling methodologies.
- Red-teaming methodology beyond the brief fuzzing and prompt-injection examples.
