---
source: https://docs.coderabbit.ai/tools/opengrep
---

# OpenGrep

## Files
OpenGrep runs on files with the following extensions:

- **C/C++**: `.c`, `.cpp`, `.cc`, `.cxx`, `.c++`, `.h`, `.hpp`, `.hh`, `.hxx`, `.h++`

- **C#**: `.cs`

- **Go**: `.go`

- **Java**: `.java`

- **JavaScript/TypeScript**: `.js`, `.jsx`, `.ts`, `.tsx`

- **Kotlin**: `.kt`

- **Python**: `.py`

- **Ruby**: `.rb`

- **Rust**: `.rs`

- **PHP**: `.php`

- **Scala**: `.scala`

- **Swift**: `.swift`

- **Terraform**: `.tf`

- **JSON**: `.json`

## Configuration
OpenGrep is **Semgrep-compatible**. CodeRabbit looks for a config file in this order:

- `opengrep.yml`

- `opengrep.yaml`

- `opengrep.config.yml`

- `opengrep.config.yaml`

- `semgrep.yml`

- `semgrep.yaml`

- `semgrep.config.yml`

- `semgrep.config.yaml`

Search starts in the repository root and in PR-changed files, then falls back to a broader repository search. If no config file is found, OpenGrep is skipped.
## When we skip OpenGrep
CodeRabbit skips OpenGrep when:

- OpenGrep is disabled in your CodeRabbit configuration.

- No files in the pull request match the supported extensions.

- OpenGrep is already running in GitHub workflows.

- No OpenGrep or Semgrep config file is found.

## Links

- OpenGrep GitHub

- Semgrep rule syntax (OpenGrep is compatible)

OSV-ScannerOxlint
