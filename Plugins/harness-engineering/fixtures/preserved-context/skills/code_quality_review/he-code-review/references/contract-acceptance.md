# Contract Acceptance Gate

Replace subjective "looks good" review with deterministic verification.

## Verification Checklist

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| **Contract compliance** | Implementation matches spec requirements | Compare code to spec requirements section |
| **Acceptance criteria** | All AC/UAC/VAC satisfied | Verify each criterion has implementation + test |
| **Test verification** | All tests pass, no regressions | Run full test suite, verify green |
| **Type checking** | No type errors | Run type checker (if applicable) |
| **Linting** | No lint violations | Run linter, zero errors |
| **Behavior preservation** | Changes don't break existing functionality | Regression tests pass |

## Scoring

### Pass
All checks ✅
- Approve for merge/progression
- Document any minor notes

### Conditional
Minor gaps only
- Approve with noted follow-ups
- Create todo items for gaps
- Ensure gaps are non-critical

### Fail
Any critical check ❌
- Return to he-work
- Document blocking issues
- Re-review after fixes

## Traceability Requirements

Record in review output:
- Verification evidence (test output, type check results)
- Test run summary (passed/failed counts)
- Any waivers with justification
- Link to spec/plan for requirements trace

## Contract Acceptance vs Style Review

**Contract acceptance first:**
1. Does it work? (contract acceptance)
2. Is it correct? (technical review)
3. Is it polished? (style)

**Never:**
- Review style when contract acceptance fails
- Approve without deterministic checks
- Skip verification because "it looks fine"

## Integration with Verification-First

The contract acceptance gate enforces the verification-first planning from he-plan:
- Tests must verify behavior (not implementation)
- Type checks catch interface mismatches
- Lint enforces patterns
- Self-check confirms spec alignment

See also:
- [[he-plan]] verification-first planning
- [[he-tdd]] behavior testing principles
- `he-anti-patterns.md` for style-over-substance anti-pattern
# Moved Traceability Lines

- Linked Linear issue, spec, plan, PR body, or branch identifier when the target is tracked delivery work
- Missing traceability is at least `go-with-conditions`; missing issue, missing validation, or mismatched scope is `no-go`.
