# Execution Workflow with Tracer Bullets

## Incremental Execution

For each task or implementation unit:
1. Mark task tracker `in_progress`
2. Mark plan/checklist `in_progress` (if artifact supports)
3. Read referenced files and patterns
4. Honor execution posture
5. Implement minimal slice
6. Run checks immediately
7. Record validation evidence
8. Update progress markers
9. Mark complete only after evidence exists

## Execution Postures

### test-first (TDD)
Use vertical tracer bullet slices per [[ce-tdd]]:

```
RED: Write one test for one behavior → confirm it fails
GREEN: Write minimal code to pass → confirm it passes
CHECK: Run all previous tests → confirm no regressions
REPEAT: Next behavior
```

### characterization-first
Capture current behavior before changing:
- Write test describing current behavior
- Verify test passes against existing code
- Now safe to refactor/change

### no special posture
Proceed pragmatically but validate continuously:
- Run relevant checks after each change
- Record evidence
- Don't batch validation

## When to Skip Test-First

Skip strict test-first only for:
- Pure config changes
- Trivial renames
- Purely cosmetic styling

**Always note the reason when skipping.**

## Verification Gates (Mandatory)

| Gate | When | Check |
|------|------|-------|
| After implementation | Every unit | Relevant tests pass |
| After TDD cycle | Using ce-tdd | All tests pass, no regressions |
| Type check | TypeScript/Go/Rust | No type errors |
| Lint | All repos | No lint errors |
| Integration | Cross-boundary work | Real chain exercised, not just mocks |
| Self-verify | AI-generated code | Output matches spec requirements |

## System-Wide Checks

Before calling a slice done, verify:
- What else fires: callbacks, middleware, observers, retries, jobs, handlers
- Whether tests exercise real chain vs mocked isolation
- Whether failure leaves orphaned/duplicated state
- Whether other interfaces need parity updates
- Whether error strategies align across layers

## Simplification

After every 2-3 related units:
- Simplify if repeated patterns emerging
- Keep scoped and behavior-preserving
- Run tests after each simplification
