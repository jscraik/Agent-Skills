---
source: https://docs.coderabbit.ai/tools/ast-grep
---

# ast-grep

ast-grep is an open-source static analysis tool that uses abstract syntax trees (AST) to find patterns in your codebase, helping identify security vulnerabilities and enforce code quality standards.

### Configuration Options

You can configure ast-grep in your `.coderabbit.yaml` file or through CodeRabbit's settings page under "Review -> Tools -> ast-grep". The following options are available:

- **`rule_dirs`**: List of directories containing your custom ast-grep rules (relative to repository root)
- **`util_dirs`**: List of directories containing utility configs to support rule management (relative to repository root)
- **`essential_rules`**: Enable the ast-grep essentials package (default: `true`)
- **`packages`**: List of GitHub packages to use (format: `owner/repo`)

### Example Configuration

```
reviews:
  tools:
    ast-grep:
      rule_dirs:
        - "rules/javascript"
        - "rules/python"
      util_dirs:
        - "utils"
      essential_rules: true
      packages:
        - "owner/custom-rules"
```

## Files

ast-grep will run on the following file types:

- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- CSS (.css)
- Elixir (.ex, .exs)
- Go (.go)
- Haskell (.hs)
- HTML (.html)
- Java (.java)
- JavaScript (.js, .jsx)
- JSON (.json)
- Kotlin (.kt)
- Lua (.lua)
- PHP (.php)
- Python (.py)
- Ruby (.rb)
- Rust (.rs)
- Scala (.scala)
- Shell (.sh, .bash)
- SQL (.sql)
- Swift (.swift)
- TypeScript (.ts, .tsx)
- YAML (.yaml, .yml)
