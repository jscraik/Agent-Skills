---
source: https://docs.coderabbit.ai/finishing-touches/simplify
---

# Simplify code

Automatically review changed code for opportunities to simplify, improve reuse, quality, and efficiency, then apply targeted improvements.

Open Beta
Pro Plan
Simplify reviews the files changed in your pull request and applies targeted code improvements: extracting reusable functions, simplifying conditionals, removing redundant code — while preserving existing behavior. Use it when you want a quick code-quality pass after writing a feature or fix.

## Platform support

### GitHub

Simplify is currently available on GitHub pull requests. You can trigger it by PR comment or from the Walkthrough checkboxes.

## Usage

Trigger Simplify using the **Simplify code** checkbox in the CodeRabbit PR Walkthrough (GitHub), or with a PR comment (any platform):

```
@coderabbitai simplify
```

## How it works

**1. Trigger Simplify**

Comment `@coderabbitai simplify` in your PR or check **Simplify code** in the CodeRabbit Walkthrough.

**2. Analyze changed files**

CodeRabbit clones your repository into a sandbox and diffs the PR branch against the base to identify all changed files.

**3. Apply improvements**

An AI agent reads each changed file, identifies simplification opportunities, and applies targeted edits: extracting reusable functions, simplifying conditionals, and removing redundant code without changing behavior.

**4. Verify with tests**

The agent runs your existing test suite to confirm no regressions were introduced by the changes.

**5. Deliver the result**

CodeRabbit either opens a new PR with the simplified code or commits the changes directly to your branch, depending on the option you select.

Simplify may take up to 20 minutes depending on the size of the pull request.

## Output options

### Create a PR with simplified code

CodeRabbit opens a new pull request against your branch with the simplified changes. Review and merge it like any other PR.

### Commit simplified code to branch

CodeRabbit commits the simplified code directly to your existing PR branch. Not available for fork PRs.

## Scope and limitations

- Simplify is a **Pro plan** feature.
- The agent preserves existing behavior — it will not change public APIs, rename exported symbols, or alter test assertions.
- If your test suite fails after simplification, CodeRabbit still delivers the changes so you can review and iterate.

## What's next

- **Autofix** - Automatically implement fixes for unresolved CodeRabbit review findings
- **Generate unit tests** - Generate comprehensive unit tests for your changed functions and methods
- **Generate docstrings** - Add documentation to functions that are missing it
