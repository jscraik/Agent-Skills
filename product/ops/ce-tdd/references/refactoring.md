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
- If a refactor breaks tests but not behavior, the tests were wrong — fix the tests
- Keep refactors scoped to the current behavior area
