# Audit Against Current Model Documentation

Read when the user asks to audit AGENTS.md and linked guidance for stale,
conflicting, or model-specific rules. This route extends the main skill workflow.

## Establish the evidence

1. Identify the requested model and product surface from the request and verified
   context. Distinguish model prompting advice from Codex instruction discovery,
   runtime configuration, tool behavior, and repository policy.
2. Inspect current local instructions, applicable parent and nested scopes,
   linked guidance, configuration, and command implementations. Preserve dirty
   work and judge the current files; do not report already-applied fixes as open.
3. Consult available current official model documentation. For OpenAI, use the
   available OpenAI Docs integration or skill; if unavailable, use official
   OpenAI documentation on the web when permitted. Record source URL, section,
   retrieval date, and the model or product it actually covers. If the user
   restricts the source route, respect that boundary and report missing access.
4. If exact-model documentation is unavailable, state that gap. Separate verified
   product-wide guidance from model-specific unknowns; do not transfer claims
   from a neighboring model or treat a UI model label as documentation.
5. Treat supplied memories and recordings as leads. Distinguish the user's
   actions from assistant status claims and completed results. Recheck suspected
   defects in current source. Keep private event content out of reusable guidance.

## Review meaning as well as links

A resolving link proves only that a target exists. Check its type, applicable
scope, trigger, and the behavior of the consumer that reads or executes it.

- Resolve apparent contradictions by authority, scope, and ownership first.
  Official recommendations inform proposals; they do not override binding
  repository rules or grant permission to change them.
- Check whether linked guidance reintroduces superseded rules for clarification,
  escalation, retries, formatting, delegation, or validation. Identify the actual
  conflicting clauses and consequence rather than labeling all strict rules stale.
- Verify dependencies and fallback targets in current source. A directory is not
  a readable-file fallback; an existing document can still name a removed tool.
- Inspect validation commands before running them. During an audit, avoid sync,
  regeneration, installation, or other mutations. Use a verified read-only check
  or report that behavior proof is blocked while continuing static inspection.
- Verify validation coverage: a diff-only check may omit committed instructions;
  pointer counts do not establish semantic correctness. State what was examined.

## Return findings and stop

For each actionable finding, give the local file and line, conflicting rule or
stale claim, supporting current source or official documentation, practical
impact, and smallest proposed correction. Distinguish confirmed defects,
recommendations, already-fixed items, and unresolved evidence gaps. Cite official
claims near the finding; avoid unsupported model-specific prescriptions.

Keep the Context ledger compact and inline unless an artifact is requested or
required by the active contract. Report checks as pass, fail, or blocked and
state coverage limits. Stop after the requested audit and proposed corrections;
apply changes only within an authorized edit scope. Missing model documentation
blocks model-specific conclusions, not independent local conflict review.
