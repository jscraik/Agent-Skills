---
source: https://docs.coderabbit.ai/tools/clang-tidy
---

# Clang-Tidy

## Files
Clang-Tidy will run on files with the following extensions:

- `**/*.cpp`

- `**/*.cxx`

- `**/*.cc`

- `**/*.c`

- `**/*.hpp`

- `**/*.hxx`

- `**/*.hh`

- `**/*.h`

## Configuration

- Enable or disable it with `reviews.tools.clang.enabled` or via **Reviews → Tools → Clang → Enabled** in CodeRabbit’s settings page.

- When present, your repository’s standard Clang-Tidy configuration (such as a `.clang-tidy` file) will be used to further customize checks and rule severities.

CodeRabbit will use the default settings based on the profile selected if no config file is found.
## Links

- Clang-Tidy Documentation

- Available Clang-Tidy Checks
