---
source: https://docs.coderabbit.ai/tools
---

CodeRabbit integrates with 40+ third-party linters and security analysis tools to enhance your code reviews. These tools run automatically in secure sandboxed environments, providing detailed feedback and 1-click fixes for common issues.

## Configuration methods

- YAML configuration
- Settings page

Add tools to your repository's `.coderabbit.yaml` file:

```
reviews:
  profile: assertive
  tools:
    eslint:
      enabled: true
    ruff:
      enabled: true
      config_file: "pyproject.toml"
    gitleaks:
      enabled: true
```

Configure tools through CodeRabbit's web interface:

1. Navigate to **Review -> Tools** in your settings
2. Toggle individual tools on/off
3. Set **Review -> Profile** to `Chill` or `Assertive`
4. Save changes to apply across all repositories

CodeRabbit offers two review profiles that control tool strictness:

- `Chill`: Focuses on critical issues and reduces noise from minor style violations
- `Assertive`: Provides comprehensive feedback including style and best practice suggestions

Each tool respects your existing configuration files (like `.eslintrc.js` or `pyproject.toml`) for maximum customization.

When tools detect issues, CodeRabbit displays structured output in the review comments:

```
ESLint
src/components/Button.tsx
12-12: 'React' must be in scope when using JSX

Add React import statement

(react/react-in-jsx-scope)
```

Many tools provide 1-click fixes that CodeRabbit can apply directly to your pull request.

## Language support

Popular languages and their supported tools:

- **JavaScript/TypeScript**: Biome, ESLint, oxlint
- **Python**: Ruff, Pylint, Flake8
- **Go**: golangci-lint
- **Rust**: Clippy
- **Ruby**: RuboCop, Brakeman
- **Swift**: SwiftLint
- **PHP**: PHPStan, PHPMD, PHPCS
