# Project Brain Integration for ce-compound

When `.harness/` directory exists, use dual-write to both `docs/solutions/` and Project Brain.

## Dual Write Flow

1. **Primary write**: `docs/solutions/[category]/[filename].md` (canonical)
2. **Secondary write**: `.harness/knowledge/{domain}/knowledge.md`
3. **Memory sync**: Local Memory MCP via `observe()`

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
    "source:ce-compound"
  ],
  session_id: "project-brain:{repo}"
})
```

## Anti-Patterns

- **Project Brain Miss**: Writing only to docs/solutions/ when .harness/ exists
- **Duplicate Entries**: Creating multiple knowledge.md entries without checking
- **Missing MCP Sync**: Forgetting to sync to Local Memory
- **Premature Promotion**: Promoting to rules without 3+ confirmations

## See Also

- `learning-capture.md` - Detailed capture workflow
- `ce-compound-refresh/Infrastructure/references/project-brain-refresh.md` - Refresh guidance
