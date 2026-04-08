---
source: https://docs.coderabbit.ai/tools/shellcheck
---

# ShellCheck

## Files

ShellCheck runs on files with these extensions:

- `.sh`
- `.bash`
- `.ksh`
- `.dash`

## Configuration

CodeRabbit applies profile-specific severity filters:

### Chill

`--severity=warning`

### Assertive

`--severity=style`

## When CodeRabbit skips ShellCheck

CodeRabbit skips ShellCheck when:

- No shell script files are present in the pull request diff.
- ShellCheck is already running in GitHub workflows.

## Links

- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki)
