---
source: https://docs.coderabbit.ai/pr-reviews/custom-checks
---

## How Custom Checks Work

Custom checks run in a secure, **read-only** environment against your PR.
**The agent has access to:**

- Changed files, code snippets, and relevant git history
- PR title, description, linked issues, and review discussion
- Pattern and code search tools (ast-grep, ripgrep)
- Sandboxed shell commands to inspect the repo
- Web lookups for public documentation
- Connected MCP tools for internal systems

**Process:**

## Limitations

Custom checks cannot:

- **Run your test suite** — dependencies are not installed in the sandbox
- **Access `node_modules`, `dist`, or build artifacts** — build steps are not executed
- **Execute arbitrary repository code** — security restriction
- **Post inline comments on specific lines** — results appear in the summary table only
- **Check PR approval status or reviewer assignments** — not available to the agent
- **Modify the CodeRabbit review** — use Path Instructions instead

## Writing Effective Instructions

Think of instructions as guidance for a smart teammate who needs explicit criteria, not subjective judgment.

**Avoid these anti-patterns:**

| Anti-pattern | Example | Why it fails |
| --- | --- | --- |
| Vague instructions | "Verify best practices" | No concrete pass/fail criteria |
| Unavailable information | "Ensure PR is approved by @security-team" | Agent cannot check approval status |
| Speculation | "Assess if there are obvious performance optimizations" | No definitive criteria; relies on subjective judgment |
| Review modifications | "Keep review comments concise" | Use Path Instructions instead |

## Examples

Custom checks can enforce a wide range of guardrails tailored to your team's needs. Here are a few examples to get you started.

Sensitive Data in Logs

```
Fail if any log statement may include passwords, API keys, tokens,
SSNs, or payment card data. Check print(), console.log, logger.*,
System.out.println, and fmt.Print variants.
```

Hardcoded Credentials

```
Scan for hardcoded credentials matching: sk_live_*, AKIA[A-Z0-9]{16},
ghp_[a-zA-Z0-9]{36}, or variables named *_SECRET, *_KEY, *_PASSWORD.
Exclude test files and .example files.
```

Database Migrations

```
For files in db/migrations/: verify both up() and down() methods exist.
Flag migrations dropping tables without restoration in down().
```

Breaking Changes

```
All breaking changes to public APIs, CLI flags, environment variables,
or database schemas must be documented in the "Breaking Change" section
of the PR description and in CHANGELOG.md.
```

Language Migration Policy

```
Disallow creation of new Java source files. Java may be modified,
but new code should be written in Kotlin.

Pass: PR modifies existing .java files or adds no new .java files.
Fail: A new *.java file is added to source control.
```
