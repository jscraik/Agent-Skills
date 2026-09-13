# CODESTYLE.md

## Purpose

This is the codestyle front door for Agent Skills Kit. Apply standards for the
changed surface: read the common foundations, then only the matching modules.
The linked rules remain mandatory in their scope; this routing does not waive
security, validation, signing, accessibility, or evidence requirements.

## Toolchain Authority

Use the current repository `.mise.toml`, package manifests, lockfiles, and
applicable `AGENTS.md` files. The root has no package-manager install step.
Use `./bin/ask` and the locked Infrastructure Python wrapper as documented in
[AGENTS.md](/AGENTS.md). Technology-specific examples do not override those
executable command contracts. Security advisories override baseline versions.

## Choose The Relevant Standards

| Changed surface | Read |
| --- | --- |
| Any implementation or instruction change | [Common foundations](/codestyle/01-foundations.md) |
| JavaScript, React, Vite, Tailwind, or Storybook | [JavaScript and UI](/codestyle/02-javascript-ui.md) |
| Rust or Tauri | [Rust and Tauri](/codestyle/03-rust-tauri.md) |
| Documentation, YAML, TOML, JSON, naming, commits, releases, or lockfiles | [Docs, config, and release](/codestyle/04-docs-config-and-release.md) |
| Quality gates, accessibility, observability, resources, or external tools | [Quality, security, and operations](/codestyle/05-quality-security-ops.md) |
| Governance dates or project-specific overrides | [Appendices and overrides](/codestyle/06-appendices-and-project-overrides.md) |
| Python | [Python](/codestyle/07-python.md) |
| TypeScript | [TypeScript](/codestyle/08-typescript.md) |
| Web applications | [Web](/codestyle/09-web.md) |
| Shell, Bash, or Zsh | [Shell](/codestyle/10-shell-bash-zsh.md) |
| pnpm or npm packages | [Package managers](/codestyle/11-package-managers-pnpm-npm.md) |
| Swift | [Swift](/codestyle/12-swift.md) |
| Git operations | [Git workflow](/codestyle/13-git-workflow.md) |
| Design patterns or performance | [Patterns](/codestyle/14-patterns.md) and [performance](/codestyle/15-performance.md) |
| Security-sensitive changes | [Security](/codestyle/16-security.md) |
| Tests or review | [Testing](/codestyle/17-testing.md) and [code review](/codestyle/18-code-review.md) |
| Development workflow | [Development workflow](/codestyle/19-development-workflow.md) |
| Go | [Go](/codestyle/20-go.md) |

Use [the codestyle module index](/codestyle/README.md) for the complete human
map. Use `coding-policy:route` through the repository-defined package command
when machine-readable changed-file routing is needed.

## Validation Scope

Run the owning check for the changed surface before widening to the repository's
required aggregate gates. A documentation typo does not select unrelated
language or runtime checks. Preserve exact commands and pass, fail, or blocked
outcomes, and keep local, runtime, hosted, and release claims separate.
