---
source: https://docs.coderabbit.ai/finishing-touches/unit-test-generation
---

## Platform support

AI coding tools let you write code 10x faster, but comprehensive testing still happens manually. CodeRabbit bridges this gap by analyzing your code changes and generating sophisticated unit tests that understand your project's patterns, testing frameworks, and edge cases.

## How it works

CodeRabbit's test generation goes beyond basic templates. It understands your project's testing patterns and generates tests that actually integrate with your existing test suite.

## Output delivery options

- Separate PR
- Same PR commit

**Recommended for most teams** CodeRabbit creates a new pull request
containing all generated tests. This approach keeps your feature PR focused
while allowing independent review of test code. **Key advantage**:
CodeRabbit automatically fixes CI/CD integration issues. If tests fail due
to missing dependencies, import errors, or configuration problems,
CodeRabbit analyzes your GitHub Actions logs and pushes fixes. This means
you get working tests, not just test code that looks right.

## Path-specific customization

Configure test generation for different parts of your codebase using `.coderabbit.yaml`:

```
code_generation:
  unit_tests:
    path_instructions:
      - path: "**/*.ts"
        instructions: |
          Use vitest for testing framework.
          Generate comprehensive test cases including edge cases and error conditions.
          Include proper TypeScript types in test expectations.
      - path: "**/api/**"
        instructions: |
          Focus on request/response validation and error handling.
          Mock external API calls using MSW.
          Test authentication middleware and rate limiting.
      - path: "**/components/**"
        instructions: |
          Use React Testing Library for component tests.
          Test user interactions, accessibility, and error boundaries.
          Mock complex props and verify state changes.
```

These instructions become part of CodeRabbit's context for future test generation, continuously improving test quality and consistency across your codebase.
Unit test generation is part of CodeRabbit's finishing touches - adding the comprehensive test coverage that ensures code quality and maintainability.
