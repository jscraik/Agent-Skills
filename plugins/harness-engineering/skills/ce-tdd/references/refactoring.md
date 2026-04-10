# Refactor Candidates

After TDD cycle, look for:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on public interface)
- **Shallow modules** → Combine or deepen
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic

## Rules

- Never refactor while RED — get to GREEN first
- Run tests after each refactor step
- After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate to determine whether behavior regressed or assertions are brittle, and only modify tests after confirming no regression.
- Keep refactors scoped to the current behavior area
