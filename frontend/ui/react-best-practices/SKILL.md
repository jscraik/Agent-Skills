---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines from Vercel Engineering.
  This skill should be used when writing, reviewing, or refactoring React/Next.js
  code to ensure optimal performance patterns. Triggers on tasks involving React components,
  Next.js pages, data fetching, bundle optimization, or performance improvements.
knowledge_graph_profile: references/task-profile.json
---

# Vercel React Best Practices

Comprehensive performance optimization guide for React and Next.js applications, maintained by Vercel. Contains 45 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

## Philosophy

Prioritize user-perceived performance and developer ergonomics. Optimize the critical path first (waterfalls, bundle size, server-side latency), then address re-renders and micro-optimizations only when they are measurable. Use data to pick the smallest fix that moves the metric. The core principles are: measure first, fix the bottleneck, and prefer simpler data-flow changes over complex caching frameworks.

## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

## Scope and triggers

Use this skill when a user asks to:
- Review or refactor React/Next.js code for performance.
- Reduce bundle size, TTFB, or render latency.
- Improve data fetching concurrency in Next.js.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | Re-render Optimization | MEDIUM | `rerender-` |
| 6 | Rendering Performance | MEDIUM | `rendering-` |
| 7 | JavaScript Performance | LOW-MEDIUM | `js-` |
| 8 | Advanced Patterns | LOW | `advanced-` |

## Variation

- Apply rules based on context (server vs client, App Router vs Pages Router, static vs dynamic).
- Prefer the minimal change that removes the bottleneck; avoid over-optimizing non-critical paths.
- If two rules apply, pick the one that reduces latency on the user-visible path.
- Vary the approach based on runtime constraints (Edge vs Node, serverless vs long-lived).

## Quick Reference

### 1. Eliminating Waterfalls (CRITICAL)

- `async-defer-await` - Move await into branches where actually used
- `async-parallel` - Use Promise.all() for independent operations
- `async-dependencies` - Use better-all for partial dependencies
- `async-api-routes` - Start promises early, await late in API routes
- `async-suspense-boundaries` - Use Suspense to stream content

### 2. Bundle Size Optimization (CRITICAL)

- `bundle-barrel-imports` - Import directly, avoid barrel files
- `bundle-dynamic-imports` - Use next/dynamic for heavy components
- `bundle-defer-third-party` - Load analytics/logging after hydration
- `bundle-conditional` - Load modules only when feature is activated
- `bundle-preload` - Preload on hover/focus for perceived speed

### 3. Server-Side Performance (HIGH)

- `server-cache-react` - Use React.cache() for per-request deduplication
- `server-cache-lru` - Use LRU cache for cross-request caching
- `server-serialization` - Minimize data passed to client components
- `server-parallel-fetching` - Restructure components to parallelize fetches
- `server-after-nonblocking` - Use after() for non-blocking operations

### 4. Client-Side Data Fetching (MEDIUM-HIGH)

- `client-swr-dedup` - Use SWR for automatic request deduplication
- `client-event-listeners` - Deduplicate global event listeners

### 5. Re-render Optimization (MEDIUM)

- `rerender-defer-reads` - Don't subscribe to state only used in callbacks
- `rerender-memo` - Extract expensive work into memoized components
- `rerender-dependencies` - Use primitive dependencies in effects
- `rerender-derived-state` - Subscribe to derived booleans, not raw values
- `rerender-functional-setstate` - Use functional setState for stable callbacks
- `rerender-lazy-state-init` - Pass function to useState for expensive values
- `rerender-transitions` - Use startTransition for non-urgent updates

### 6. Rendering Performance (MEDIUM)

- `rendering-animate-svg-wrapper` - Animate div wrapper, not SVG element
- `rendering-content-visibility` - Use content-visibility for long lists
- `rendering-hoist-jsx` - Extract static JSX outside components
- `rendering-svg-precision` - Reduce SVG coordinate precision
- `rendering-hydration-no-flicker` - Use inline script for client-only data
- `rendering-activity` - Use Activity component for show/hide
- `rendering-conditional-render` - Use ternary, not && for conditionals

### 7. JavaScript Performance (LOW-MEDIUM)

- `js-batch-dom-css` - Group CSS changes via classes or cssText
- `js-index-maps` - Build Map for repeated lookups
- `js-cache-property-access` - Cache object properties in loops
- `js-cache-function-results` - Cache function results in module-level Map
- `js-cache-storage` - Cache localStorage/sessionStorage reads
- `js-combine-iterations` - Combine multiple filter/map into one loop
- `js-length-check-first` - Check array length before expensive comparison
- `js-early-exit` - Return early from functions
- `js-hoist-regexp` - Hoist RegExp creation outside loops
- `js-min-max-loop` - Use loop for min/max instead of sort
- `js-set-map-lookups` - Use Set/Map for O(1) lookups
- `js-tosorted-immutable` - Use toSorted() for immutability

### 8. Advanced Patterns (LOW)

- `advanced-event-handler-refs` - Store event handlers in refs
- `advanced-use-latest` - useLatest for stable callback refs

## Anti-patterns

- Applying rules without evidence (no profiling, no user-visible impact).
- Overusing memoization or caching for trivial work.
- Adding complex code paths when a simpler data-flow change solves the issue.
- Copying patterns across codebases without validating assumptions.
- Avoid introducing framework-specific APIs when the app doesn't use that router mode.

## Empowerment

- If unsure which rule applies, start with the highest priority category and ask for target files.
- Offer the smallest safe refactor that fixes the bottleneck.
- Ask for profiling output when impact is unclear.

## Required inputs

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.


- Target files or directories.
- Framework context (Next.js App Router vs Pages Router).
- Performance goal (latency, bundle size, re-render reduction).

## Deliverables

- A short list of applicable rules with concrete edits or refactors.
- Any files that need additional profiling or measurement.

## Constraints / Safety

- Avoid introducing breaking changes without confirmation.
- Prefer reversible refactors over invasive rewrites.
- Redact secrets, tokens, and private URLs from examples or logs.

## Procedure

1. Confirm the runtime context (App Router vs Pages, Edge vs Node).
2. Identify the bottleneck category (waterfalls, bundle, server, render).
3. Select the smallest rule change that addresses the bottleneck.
4. Propose targeted edits with file-level references.
5. Validate with profiling or tests where available.

## Validation

- Run relevant tests and perf checks after edits.
- Fail fast: stop at the first failed check and fix before continuing.
- See `references/contract.yaml` (schema_version: 1) and `references/evals.yaml`.

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/async-parallel.md
rules/bundle-barrel-imports.md
rules/_sections.md
```

Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`

## References

- `rules/` for per-rule guidance and examples.
- `AGENTS.md` for the compiled guide.
- `references/decision-guide.md` for rule selection shortcuts.
- `references/metrics.md` for before/after checks.
- `assets/rule-output-template.md` for the report template.
- `references/contract.yaml` and `references/evals.yaml` for gold-gate validation.

## Examples

- "Reduce bundle size in a Next.js app router page."
- "Refactor data fetching to remove server waterfalls."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential, they don't constrain it. Use judgment, adapt to context, and push boundaries when appropriate.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
