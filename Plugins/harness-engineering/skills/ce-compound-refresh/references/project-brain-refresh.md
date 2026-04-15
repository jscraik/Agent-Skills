# Project Brain Integration for ce-compound-refresh

When `.harness/` exists, refresh applies to both locations.

## Dual Refresh Flow

1. **Primary refresh**: `docs/solutions/[category]/[file].md`
2. **Secondary refresh**: `.harness/knowledge/{domain}/knowledge.md`
3. **Memory update**: Local Memory MCP via `observe()` if content changed

## Promotion Review During Refresh

### Check for Promotion
During refresh, check if knowledge should promote to rules:

**Criteria for promotion to rules.md:**
- Same pattern confirmed 3+ times
- Stable over time (no contradictions)
- Widely applicable

**Action:**
- Move content to `rules.md`
- Add promotion header:
  ```yaml
  ---
  title: "{pattern}"
  type: rule
  status: Active
  promoted: YYYY-MM-DD
  origin: knowledge.md (3+ confirmations)
  ---
  ```
- Update `observe()` tags: `"type:rule"`

### Check for Demotion

**Criteria for demotion to hypotheses.md:**
- New evidence contradicts guidance
- Partially correct but incomplete
- Needs more validation

**Action:**
- Move content to `hypotheses.md`
- Add demotion header:
  ```yaml
  ---
  title: "{pattern}"
  type: hypothesis
  status: Under review
  demoted: YYYY-MM-DD
  reason: {contradiction}
  ---
  ```
- Update `observe()` tags: `"type:hypothesis"`

## Local Memory MCP Update

After refresh:

```javascript
observe({
  content: "Refreshed: {problem} → {updated solution}",
  level: "learning",
  tags: [
    "project-brain:{repo}",
    "type:{knowledge|rule|hypothesis}",
    "domain:{domain}",
    "source:ce-compound-refresh",
    "action:refresh"
  ],
  session_id: "repo:{repo}:task:{task_id}"
})
```

## Anti-Patterns

- **Partial Refresh**: Updating docs/solutions/ but not .harness/
- **Missing MCP Update**: Content changed but memory not synced
- **Promotion Without Evidence**: Promoting without 3+ confirmations
- **Orphaned Rules**: Not demoting rules when contradicted

## See Also

- `../../ce-compound/Infrastructure/references/project-brain-integration.md` - Initial capture
- `../../ce-compound/Infrastructure/references/learning-capture.md` - Capture workflow
