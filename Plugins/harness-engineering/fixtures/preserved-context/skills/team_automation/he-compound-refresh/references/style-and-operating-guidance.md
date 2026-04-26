# Style and Operating Guidance

Read when: you need standards rationale, operating philosophy, output-variation expectations, discoverability policy, or empowerment guardrails while running `he-compound-refresh`.

## Standards snapshot (April 2026)
- Keep the skill scoped to one reusable maintenance job, with routing language that says what it does and when to use it.
- Prefer repo truth, explicit evidence, and selective external verification over speculative rewriting.
- Keep `SKILL.md` lean and move detailed decision trees, report formats, and git follow-up logic into `Infrastructure/references/`.
- Use realistic positive and negative examples plus eval-backed trigger coverage instead of relying on hidden prompt assumptions.
- When current framework or library behavior matters, verify with primary docs first; for OpenAI product behavior use official OpenAI docs first, and use Context7 only when current library semantics materially affect the maintenance decision.

## Philosophy
- `he-compound-refresh` protects the trustworthiness of accumulated team knowledge.
- The right default is conservative accuracy, not maximum rewriting.
- A stale learning is better marked stale than silently left misleading.
- Pattern docs deserve extra skepticism because they influence future work more broadly than incident-level learnings.
- Refresh work should feel like precise gardening, not a repo-wide cleanup frenzy.

Guiding questions:
- What is the smallest useful scope that will materially improve trust right now?
- Is this artifact still describing how the system actually works, or only how it used to work?
- Would a future engineer be safer with a factual in-place update, a real successor, or an explicit stale warning?
- Does this report make the next maintenance decision easier, or am I creating churn without increasing trust?

## Encouraging variation
Outputs should vary by scope:
- focused runs: compact, direct, specific
- batch runs: grouped by shared evidence and maintenance action
- broad sweeps: triaged and incremental

## Discoverability check
After generating the refresh report, check whether root instruction docs (for example `AGENTS.md` and compatibility files) clearly surface `docs/solutions/` to agents.

1. Identify the substantive root instruction file (ignore pure include shims).
2. Confirm an agent can learn all three:
- a searchable knowledge store exists
- its structure (for example category organization and frontmatter fields)
- when to search it (before implementing or debugging in documented areas)
3. If already clear, no action.
4. If not clear, draft the smallest possible addition:
- prefer one line in an existing architecture or directory section
- create a new section only as last resort
- keep tone informational, not mandatory

Mode rule:
- interactive: explain why, show proposed change, get explicit consent before editing instruction files
- autonomous: include as "Discoverability recommendation" in report; do not edit instruction files

## Empowerment
You are maintaining a safety-critical knowledge layer. Use evidence-backed judgment:
- trust evidence: code changed -> docs should reflect it
- prefer `Keep` over churn: edit only for material trust improvements
- promotion/demotion remains valid when evidence supports it (for example 3+ confirmations for promotion; contradictions for demotion)
