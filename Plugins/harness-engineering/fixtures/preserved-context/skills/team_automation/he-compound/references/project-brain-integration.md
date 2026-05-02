# Project Brain Integration for he-compound

When `.harness/` directory exists, keep `docs/solutions/` as the primary
`he-compound` artifact and run Project Brain sync as an explicit follow-up when
the user requests it or repo instructions require it.

## Follow-Up Flow

1. **Primary write**: `docs/solutions/[category]/[filename].md` (canonical)
2. **Project Brain follow-up**: `.harness/knowledge/{domain}/knowledge.md`
3. **Memory sync**: Local Memory MCP via `observe()` when available
4. **Status report**: `synced`, `not_needed`, or `blocked`

## Domain Mapping

| docs/solutions/ | .harness/knowledge/ |
|-----------------|---------------------|
| build-errors/ | build/ |
| test-failures/ | testing/ |
| runtime-errors/ | runtime/ |
| performance-issues/ | performance/ |
| security-issues/ | security/ |
| database-issues/ | data/ |
| integration-issues/ | integration/ |
| ui-bugs/ | ui/ |
| logic-errors/ | logic/ |

## Promotion Path

### First Capture
- Write to `knowledge.md`
- `observe(tags=["type:knowledge", ...])`

### Second Occurrence  
- Update existing knowledge.md
- Increment frequency counter

### Third Occurrence (Promotion)
- Promote to `rules.md`
- `observe(tags=["type:rule", ...])`
- Add header:

  ```markdown
  ---
  title: "{problem}"
  type: rule
  promoted: YYYY-MM-DD
  confirmed: 3
  ---
  ```

### Contradicted Guidance
- Demote to `hypotheses.md`
- `observe(tags=["type:hypothesis", ...])`
- Document contradiction reason

## Local Memory MCP Sync

```javascript
observe({
  content: "{problem} → {solution}",
  level: "learning",
  tags: [
    "project-brain:{repo}",
    "type:knowledge", // or "type:rule"
    "domain:{domain}",
    "source:he-compound"
  ],
  session_id: "project-brain:{repo}"
})
```

## Anti-Patterns

- **Project Brain Miss**: Writing only to chat when durable knowledge is required
- **Duplicate Entries**: Creating multiple knowledge.md entries without checking
- **Hidden Indexing Failure**: Hiding Local Memory indexing failure inside a successful docs/solutions result
- **Premature Promotion**: Promoting to rules without 3+ confirmations

## See Also

- `learning-capture.md` - Detailed capture workflow
- `he-compound-refresh/Infrastructure/references/project-brain-refresh.md` - Refresh guidance
