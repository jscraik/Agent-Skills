---
source: https://docs.coderabbit.ai/finishing-touches
---

# CodeRabbit Documentation - Finishing Touches

Writing documentation for every function is time-consuming, but undocumented code creates bottlenecks during code reviews. You spend cycles explaining what functions do instead of focusing on business logic and architecture decisions.

CodeRabbit generates docstrings for functions missing documentation in your PRs. Comment `@coderabbitai generate docstrings` or check the box in your PR walkthrough to trigger generation.

The system scans your changes with ast-grep, identifies functions needing documentation, and generates docstrings that match your codebase's existing format. Generated docstrings are committed to a new branch and opened as a PR for your review.

This handles the initial documentation grunt work while keeping you in control through the standard PR review process.

## How it works

You review the generated PR like any other code change. CodeRabbit preserves existing docstrings and only documents functions that genuinely need it.

## Platform and integration support

## Configure per-directory styles

Customize documentation format using .coderabbit.yaml

Different parts of your codebase need different documentation approaches. Use path-based instructions to match your team's standards:

```yaml
code_generation:
  docstrings:
    path_instructions:
      - path: "src/**/*.ts"
        instructions: |
          Use TSDoc format with @param, @returns, and @example tags.
          Include code examples for public API functions.
          Focus on behavior and edge cases.
      - path: "**/*test*"
        instructions: |
          Describe test purpose and expected behavior.
          Keep docstrings concise - focus on what is being tested.
      - path: "Infrastructure/scripts/**/*.py"
        instructions: |
          Use Google-style docstrings with Args and Returns sections.
          Include usage examples for utility scripts.
      - path: "models/**/*.py"
        instructions: |
          Document database models with field descriptions and relationships.
          Include example queries and common usage patterns.
```

Path patterns use minimatch syntax to target specific directories, file types, or naming conventions.

### Common configuration examples

**Frontend components:**

```yaml
- path: "components/**/*.tsx"
  instructions: "Document props, usage examples, and accessibility considerations"
```

**API endpoints:**

```yaml
- path: "api/**/*.{js,ts}"
  instructions: "Document request/response formats, status codes, and error handling"
```

**Utility functions:**

```yaml
- path: "utils/**/*"
  instructions: "Focus on input validation, return types, and edge case behavior"
```

**Database models:**

```yaml
- path: "models/**/*.py"
  instructions: "Document fields, relationships, and include example queries"
```

## Reviewing generated docstrings

When CodeRabbit opens a docstring PR, focus your review on:

**Content accuracy:**

- Parameter descriptions match actual function behavior
- Return value documentation reflects real outputs
- Edge cases and error conditions are correctly described

**Format consistency:**

- Generated format matches your codebase conventions
- Examples use appropriate syntax for your language
- Terminology aligns with your project's vocabulary

**Completeness:**

- All parameters are documented with appropriate detail
- Complex functions include usage examples
- Error conditions and exceptions are covered

Most generated docstrings need minimal adjustment. Common tweaks include refining parameter descriptions or adding project-specific terminology.

## Technical implementation

CodeRabbit uses ast-grep for precise code parsing across different programming languages and coding styles. This enables accurate function detection while respecting your code structure and automatically detecting your preferred docstring format.

Language support depends on ast-grep capabilities. To request additional language support, contribute to the ast-grep language addition guide.

**Currently supported:** Bash, C, C++, C#, Elixir, Go, Java, JavaScript, Kotlin, Lua, PHP, Python, React TypeScript, Ruby, Rust, Swift, TypeScript.

## Next steps

Ready to enhance your development workflow? Explore these related features and resources.
