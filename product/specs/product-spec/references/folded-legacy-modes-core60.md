# Folded Legacy Modes (Core60)

Destination skill: `product/specs/product-spec`

This file captures legacy capabilities migrated from retired skills.

## `asymmetric-ideas`
- Source skill: `product/strategy/asymmetric-ideation-engine`
- Legacy description: Generate 10 launchable asymmetric ideas by excavating a repository for hidden patterns. Use when users ask for radical non-incremental ideation from repo context; don't use for roadmap optimization, bug fixing, or routine prioritization. Outputs: structured idea set + artifact file. Success: all novelty constraints satisfied.
- Fold rationale: High-novelty idea generation remains upstream of specification drafting.
- Legacy section map:
  - Working agreement
  - Scope and triggers
  - Required inputs
  - Constraints and safety
  - Principles
  - Empowerment

## `ideation-prep`
- Source skill: `product/strategy/brainstorming`
- Legacy description: This skill should be used before implementing features, building components, or making changes. It guides exploring user intent, approaches, and design decisions before planning. Triggers on "let's brainstorm", "help me think through", "what should we build", "explore approaches", ambiguous feature requests, or when the user's request has multiple valid interpretations that need clarification.
- Fold rationale: Most brainstorming sessions are pre-spec framing and should land in one pipeline.
- Legacy section map:
  - When to Use This Skill
  - Inputs
  - Outputs
  - Constraints
  - Core Process
  - What We're Building

## `improvement-batch`
- Source skill: `product/strategy/project-improvement-ideator`
- Legacy description: Use when asked to generate and prioritize product or repository improvements: privately explore 100 pragmatic ideas, run a premortem, and return the 10 strongest opportunities with current-source-backed best-practice notes, implementation slices, and risk controls; do not use for bug fixing or generic brainstorming.
- Fold rationale: Repository improvement proposals are pre-PRD artifacts.
- Legacy section map:
  - Table of Contents
  - Scope and triggers
  - Required inputs
  - Core workflow
  - Scoring rubric
  - Gold-standard lenses
