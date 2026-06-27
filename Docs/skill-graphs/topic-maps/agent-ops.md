---
type: moc
name: agent-ops
description: "Skills for building, operating, and evolving the Agent-Skills system itself — skill authoring, agent configs, automations, plugin packaging, and Codex-native tooling."
covers:
  - skill-authoring
  - agent-configuration
  - automations
  - plugin-packaging
  - codex-tooling
  - debugging
  - task-management
---

# Agent Ops

> Skills for building, operating, and evolving the Agent-Skills system: skill authoring, agent configs, automations, plugin packaging, and Codex-native primitives.

## Table of Contents
- [Skill & Agent Authoring](#skill--agent-authoring)
- [Codex Tooling & Home](#codex-tooling--home)
- [Debugging & Verification](#debugging--verification)
- [Task & Session Management](#task--session-management)
- [Workflow Planning & Routing](#workflow-planning--routing)
- [Documentation & Context](#documentation--context)

---

## Skill & Agent Authoring

- [[skill-builder]] — Create, revise, benchmark, and quality-gate Codex skills (SKILL.md + scripts + evals + packaging).
- [[codex-agent-creator]] — Create and install Codex custom multi-agent roles under `agents/` with a role definition and `openai.yaml` metadata.
- [[plugin-builder]] — Create, convert, and validate Codex plugin packages: skills, prompts, hooks, agents, and MCP metadata.
- [[decide-build-primitive]] — Analyze and decide the right Codex primitive: Skill, Custom Prompt, or Agent automation.
- [[codex-automation-architect]] — Create, review, and merge Codex app automations with environment preflight and multi-runner validation.
- [[agents-md]] — Refactor or create AGENTS.md using progressive disclosure: minimal root, linked docs, contradiction tracking.

## Codex Tooling & Home

- [[codex-home-audit]] — Audit and improve a Codex home directory (AGENTS.md, USER_PROFILE, instructions, rules, config.toml).
- [[skill-refactor]] — Daily skill health scan: analyze `~/.codex/sessions` and per-repo session logs for invocations and failures.
- [[insight-report]] — Generate a high-fidelity Codex usage insights HTML report from local session data.
- [[fix-mise]] — Diagnose and repair mise trust/runtime failures.

## Debugging & Verification

- [[he-fix-bugs]] — Root-cause-first debugging workflow for bugs, test failures, regressions, and unexpected behavior.
- [[verification-before-completion]] — Validate completion claims with fresh command evidence before marking work done.
- [[he-tdd]] — Build behavior-safe code changes with RED/GREEN evidence.
- [[evals-router]] — Design, audit, debug, and scale LLM evaluation workflows: error analysis, judge prompts, synthetic eval data.
- [[process-watch]] — Analyze system processes and resource usage to diagnose runaway CPU/memory/IO.
- [[recon-workbench]] — Authorized, evidence-backed Recon Workbench (rwb) workflows on macOS/iOS, web/React, or OSS targets.

## Task & Session Management

- [[gh-workflow]] — Manage GitHub issues and PRs through the repository’s tracker workflow.
- [[alignment-checkpoint]] — Intent-alignment gate for ambiguous/high-stakes requests; requires explicit `/proceed` approval before tool use.

## Workflow Planning & Routing

- [[he-plan]] — Create execution-ready implementation plans with sequencing, validation, and rollout guidance.
- [[he-brainstorm]] — Pre-planning exploration for ambiguous requests: clarify, compare 2-3 approaches, recommend a direction.
- [[interview-me]] — Interactive, multiple-choice interview for requirements discovery; turns ideas into execution-ready specs.
- [[deep-interview]] — Deep, gap-filling interview to enhance existing docs/specs or explore a topic.
- [[architecture-interview]] — Plan and review architecture decisions via structured interview and ADR output.

## Documentation & Context

- [[technical-writer]] — Audit or rewrite repository docs (README, runbooks, community-health files) and in-code documentation.
- [[context7]] — Extract current library documentation via Context7 for up-to-date API details and version checks.
- [[openai-docs]] — Up-to-date official OpenAI documentation with citations via the OpenAI docs MCP.
- [[diagram-cli]] — Generate, validate, and refresh architecture artifacts (.mmd/.svg/.diagram manifest + context packs).
- [[markdown-converter]] — Convert source files into Markdown outputs using the bundled converter workflow.
- [[llm-wiki]] — Build and maintain a local markdown wiki for persistent, queryable project knowledge.

---

## Cross-links

- Building a new skill? [[he-brainstorm]] → [[skill-builder]] → [[decide-build-primitive]] → [[plugin-builder]].
- Debugging a failing automation? [[he-fix-bugs]] → [[evals-router]] → [[verification-before-completion]].
- Session health check? [[skill-refactor]] → [[insight-report]].
- Topic maps: [[backend-platform]] | [[product-strategy]] | [[security-ops]]
