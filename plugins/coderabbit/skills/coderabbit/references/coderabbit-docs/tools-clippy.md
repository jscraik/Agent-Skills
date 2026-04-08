---
source: https://docs.coderabbit.ai/tools/clippy
---

# Clippy

## Supported files

Clippy runs on Rust files:

- `*.rs`

## Configuration

Clippy supports:

- `clippy.toml`
- `.clippy.toml`

Clippy does not require explicit configuration, but a `Cargo.toml` file must exist for the project.

## When CodeRabbit skips Clippy

CodeRabbit skips Clippy when:

- No Rust files (`.rs`) are present in the pull request.
- No `Cargo.toml` exists in the repository.
- Clippy is already running in GitHub workflows.

## Features

Clippy can detect:

- Style violations
- Common mistakes
- Performance issues
- Deprecated code patterns
- Other Rust-specific quality concerns

## Links

- [Clippy GitHub Repository](https://github.com/rust-lang/rust-clippy)
- [Clippy Documentation](https://doc.rust-lang.org/clippy/)
- [Clippy Lints](https://rust-lang.github.io/rust-clippy/master/)
