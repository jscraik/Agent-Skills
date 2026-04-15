---
source: https://docs.coderabbit.ai/finishing-touches/unit-test-generation
---

# Unit Test Generation

## Platform support

AI coding tools accelerate implementation, but complete test coverage still requires deliberate review. CodeRabbit helps close that gap by generating tests based on your project's framework and patterns.

## How it works

CodeRabbit's test generation goes beyond templates. It analyzes your test conventions and generates tests intended to integrate into your existing suite.

## Output delivery options

- Separate PR
- Same PR commit

**Recommended for most teams:** generate tests in a separate PR. This keeps feature PR scope focused while enabling targeted review of generated tests.

CodeRabbit can often suggest CI/CD-related fixes (for example import or dependency issues) when test runs fail, but outcomes still depend on repository setup and available logs.

## Path-specific customization

Configure generation behavior in `.coderabbit.yaml`:

```yaml
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

These instructions become part of future generation context and can improve consistency over time.
