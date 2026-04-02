---
source: https://docs.coderabbit.ai/tools/clippy
---

# Clippy

## Supported Files
Clippy will run on files with the following extensions:

- `*.rs`

## Configuration
Clippy supports the following configuration files:

- `clippy.toml`

- `.clippy.toml`

Clippy does not require configuration to run. If no configuration file is found, it will use default settings.A Cargo.toml is required.
## When we skip Clippy
CodeRabbit will skip running Clippy when:

- No Rust files (`.rs`) are found in the pull request.

- No `Cargo.toml` file is found in the repository.

- Clippy is already running in GitHub workflows.

## Features
Clippy can detect many code quality issues such as:

- Style violations

- Common mistakes

- Performance issues

- Deprecated code patterns

- And many more Rust-specific issues

## Links

- Clippy GitHub Repository

- Clippy Documentation

- Available Lints

CircleCIClang-Tidy
