# CLI Standards Baseline (Jan 2026)

Use these references to anchor CLI decisions and avoid drift.

## POSIX and GNU
- POSIX Utility Conventions:
  https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html
- GNU Coding Standards (CLI conventions):
  https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html

## Command Line Interface Guidelines
- CLI Guidelines (clig.dev):
  https://clig.dev/

## Heroku CLI Style Guide
- Heroku CLI Style Guide:
  https://devcenter.heroku.com/articles/cli-style-guide

## XDG Base Directory (config/cache/data)
- XDG Base Directory Spec:
  https://specifications.freedesktop.org/basedir/latest/

## Exit codes
- GNU Exit Status (portable semantics):
  https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html

## Shell script hygiene (if shipping scripts)
- ShellCheck:
  https://www.shellcheck.net/

## High-quality reference CLI
- GitHub CLI manual (flags, --json/--jq patterns):
  https://cli.github.com/manual/

## NO_COLOR spec
- NO_COLOR:
  https://no-color.org/

## Versioning notes
- POSIX + GNU define long-standing CLI expectations for flags, help, and output.
- 12-Factor CLI is a modern, widely-adopted best-practice rubric.
- NO_COLOR is the de-facto standard for color opt-out.
