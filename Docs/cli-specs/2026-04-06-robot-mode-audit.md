---
title: Robot-Mode Interface Consistency Audit
status: completed
date: 2026-04-06
---

# Robot-Mode Interface Consistency Audit

## Executive Summary

The robot-mode interface provides a solid foundation for AI agent interaction but has several consistency issues that should be addressed for a polished, predictable experience.

**Grade: B+** (Good foundation, minor inconsistencies, one critical bug)

## 1. Command Taxonomy Assessment

### Current Structure

| Topic | Actions | Consistency |
|-------|---------|-------------|
| repo | status, validate, check-stability | ✅ Good |
| skills | list, sync, audit, install, fold, init | ✅ Good |
| plugins | init | ⚠️ Incomplete (no list, audit) |
| evals | run, benchmark, dashboard | ⚠️ "run" is vague |
| graph | related, find, info, chain, list, topics | ⚠️ "list" conflicts with skills |
| mcp | sync | ⚠️ Single action topic |

### Issues Found

1. **Inconsistent naming**: `graph list` and `skills list` have same name but different semantics
   - `skills list` = list all skills
   - `graph list` = list skills in graph (with filters)
   - **Recommendation**: Rename `graph list` to `graph skills` or `graph nodes`

2. **Vague action**: `evals run` doesn't specify what it runs
   - **Recommendation**: Rename to `evals test-skill` or `evals run-tests`

3. **Incomplete topics**: `plugins` only has `init`, missing `list`, `audit` like skills
   - **Recommendation**: Add `plugins list` for consistency

4. **Single-action topics**: `mcp` only has `sync`
   - Acceptable for now, but consider if this should be a subcommand of another topic

## 2. Output Schema Stability

### Schema Consistency: ✅ EXCELLENT

All commands return consistent `CallResult` envelope:

```json
{
  "status": "success|error|partial",
  "trace_id": "uuid-v4",
  "metadata": {
    "version": "0.1.0",
    "command": "string",
    "next_steps": ["string"],
    "correction_note": "string (robot mode only)"
  },
  "data": { /* command-specific */ },
  "telemetry": {
    "latency_ms": integer
  },
  "errors": [
    {
      "code": "ERR_*",
      "message": "string",
      "fix_suggestion": "string",
      "help_url": "string"
    }
  ]
}
```

### Observations

- ✅ All 6 top-level fields always present
- ✅ metadata.version is static "0.1.0" - should match CLI version from `--version`
- ✅ correction_note properly included in metadata when robot mode corrects
- ✅ trace_id is valid UUID v4

### Recommendation

Add `metadata.schema_version` to track envelope schema changes independently from CLI version.

## 3. Intent Handling Behavior

### Fuzzy Matching: ✅ GOOD

**Working corrections:**
- `skill` → `skills` ✅
- `ls` → `list` ✅
- `search` → `find` ✅
- `aud` → `audit` ✅

### Bug Found: 🐛 CRITICAL

When argparse fails but fuzzy matching succeeds, an error message leaks before JSON output:

```
ask: error: argument topic: invalid choice: 'skill' (choose from ...)
{ "status": "success", ... }  ← JSON follows error message
```

This breaks JSON parsing for agents that capture both stdout and stderr.

**Root cause**: argparse prints to stderr before fuzzy matching kicks in.

**Fix**: Capture argparse errors and only display if fuzzy matching also fails.

### Missing Feature: Contextual Examples

Error messages include examples, but they're hardcoded rather than contextual to the specific error.

**Current**:
```
Valid actions: list, sync, audit, install, fold, init
📚 Examples:
   • ask skills list
   • ask skills audit backend/cli-spec --level strict
```

**Better**:
```
Unknown action 'foo' for topic 'skills'
💡 Did you mean 'ask skills fold'?
   Similar commands: fold, init
📚 For 'fold' usage:
   ask skills fold source-skill target-skill
   ask skills fold skill-creator skill-builder --sensitivity 0.3
```

## 4. Error Explanation Quality

### Error Code Consistency: ✅ GOOD

| Code | Used | Quality |
|------|------|---------|
| ERR_RUNTIME | ✅ | Good |
| ERR_VALIDATION | ✅ | Good |
| ERR_PATH_TRAVERSAL | ✅ | Excellent (with fix suggestion) |
| ERR_DEPENDENCY | ✅ | Good |
| ERR_CONFLICT | ✅ | Good |
| ERR_REDUNDANCY | ✅ | Good |
| ERR_AUTH | ⚠️ | Defined but not used |

### Bug Found: 🐛 CRITICAL

**UnboundLocalError** when fuzzy matching fails to parse unknown commands:

```python
python3 bin/ask invalid-topic --robot
# ... argparse error ...
UnboundLocalError: cannot access local variable 'args'
```

**Location**: bin/ask line 456 - `args` referenced before assignment when both argparse and fuzzy matching fail.

### Fix Suggestion Coverage

- ✅ ERR_PATH_TRAVERSAL: "Use a relative path within the repository."
- ⚠️ ERR_VALIDATION: Often lacks fix_suggestion
- ⚠️ ERR_RUNTIME: Generic message without specific fix

**Recommendation**: Require fix_suggestion for all error codes in ErrorObject.

## 5. Quick-Start Teaching Efficiency

### Help Message: ⚠️ FAIR

**Current issues**:
1. Examples are on one line and hard to read:
   ```
   Examples: ask repo status # Check... ask skills list --json # List...
   ```

2. No explicit mention of `--agent-mode` or `-r` aliases in description

3. Missing quick-reference for robot mode capabilities

### AGENTS.md Documentation: ✅ EXCELLENT

- Clear robot mode philosophy
- Good before/after examples
- Addresses agent pain points
- Best practices section

### Suggested Improvements

**Help message**:
```
Agent Skills Kit CLI

🤖 Robot Mode (--robot, --agent-mode, -r):
   Fuzzy command matching, auto-corrections, detailed guidance
   Example: "ask skill list" → auto-corrected to "ask skills list"

📚 Quick Start:
   ask repo status              Check repository health
   ask skills list --json       List skills as JSON
   ask graph find security      Search for security skills

Topics: repo, skills, plugins, evals, graph, mcp
Use --help TOPIC for detailed command help
```

## Recommendations Summary

### Critical (Fix Immediately)

1. **Fix UnboundLocalError** when fuzzy matching fails (bin/ask:456)
2. **Suppress argparse errors** when robot mode successfully corrects

### High Priority

3. Rename `graph list` to `graph skills` to avoid semantic collision
4. Rename `evals run` to `evals test-skill` for clarity
5. Fix help message formatting (newlines in examples)
6. Add `plugins list` for topic consistency

### Medium Priority

7. Add `metadata.schema_version` to envelope
8. Make fix_suggestion required in ErrorObject
9. Add contextual "Did you mean?" with similarity scoring
10. Use actual CLI version in metadata.version

### Low Priority

11. Consider merging `mcp` into `config` or `tools` topic
12. Add `ask --version` flag
13. Create interactive `ask tutorial` command

## Verification Checklist

After fixes, verify:
- [ ] `ask invalid --robot --json` returns valid JSON only (no stderr noise)
- [ ] `ask skill list --robot` works without error messages
- [ ] All error codes include fix_suggestion
- [ ] Help message examples are readable
- [ ] Command taxonomy is internally consistent

## Appendix: Test Commands

```bash
# Taxonomy consistency
ask graph list --json | jq '.data.skills'  # Should be nodes, not skills

# Schema stability
ask repo status --json | jq 'keys'  # Should always be same 6 keys

# Intent handling
ask skill list --robot --json  # Should not have stderr noise

# Error quality
ask skills audit /etc/passwd --json | jq '.errors[0].fix_suggestion'  # Should exist

# Bug check
ask invalid-topic --robot  # Should not crash
```
