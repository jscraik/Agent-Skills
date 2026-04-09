# Verification-First Planning

Every implementation unit must include verification strategy before execution.

## Verification Types

| Verification Type | When Required | How to Verify |
|-------------------|---------------|---------------|
| **Test oracle** | All code changes | Tests verify behavior through public interfaces |
| **Type checking** | TypeScript/Rust/Go | Static analysis catches interface mismatches |
| **Linting** | All repos | Enforce patterns and catch common mistakes |
| **Self-check** | AI-generated code | Agent compares output against spec requirements |

## Core Rules

1. **Tests describe behavior, not implementation**
   - Good: "user can checkout with valid cart"
   - Bad: "validateCart method is called with correct arguments"

2. **Tests must survive internal refactors**
   - If you rename an internal function, tests should still pass
   - Tests break only when behavior changes

3. **No horizontal slicing**
   - Don't write all tests first, then all implementation
   - Use vertical slices: one behavior → one test → one implementation → repeat
   - See `ce-anti-patterns.md` for horizontal slicing detection

4. **Include explicit verification gates**
   - Each implementation unit lists its verification method
   - Document test file paths
   - Specify expected test coverage

## Anti-Pattern: Horizontal Slicing

**WRONG:**
```
RED: Write tests 1-5
GREEN: Write implementations 1-5
```

**RIGHT (vertical slices):**
```
RED→GREEN: Test 1 → Impl 1
RED→GREEN: Test 2 → Impl 2
...
```

Horizontal slicing produces tests that verify imagined behavior, not actual behavior. Tests become coupled to implementation structure rather than behavior.

## Verification Checklist Per Unit

- [ ] Test describes behavior through public interface
- [ ] Test would survive internal refactor
- [ ] Verification method specified (test/type-check/lint)
- [ ] Test file paths documented
- [ ] No horizontal slicing planned

## Integration with TDD

For strict TDD workflow, see [[ce-tdd]].

Key difference:
- **ce-tdd**: Strict red-green-refactor with tracer bullets
- **verification-first planning**: Broader verification strategy including tests, types, lint, self-check
