---
name: gh-address-comments
description: Address GitHub PR review or issue comments with gh CLI. Not for CI failures or full issue workflows; use gh-actions-fix or gh-issue-fix.
metadata:
  short-description: Address comments in a GitHub PR review
---
# PR Comment Handler

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy
- Respect reviewer intent; clarify before changing behavior.
- Prefer minimal, verifiable fixes over sweeping refactors.
- Keep changes traceable to specific comments and evidence.
- Explain the why in responses, not just the what.
- Optimize for reviewer trust and project continuity.

## Guiding questions
- What is the reviewer’s intent and expected outcome?
- Why is this comment raised now (correctness, design, consistency, or risk)?
- What is the smallest change that resolves the issue?
- How will this change be verified (tests, lint, evidence)?

## When to use
- When the user asks to address review comments on an open GitHub PR.
- When the user wants to respond to reviewer feedback using `gh` CLI.
- When the user needs a summary of PR review threads before fixing.
- When the user asks to verify `gh` auth or fetch PR comments.

## Inputs
- Current git branch and repository context.
- `gh` CLI authenticated session and repo access.
- User-selected comment numbers to address.

## Outputs
- A numbered summary of review threads and proposed fixes.
- Code changes addressing selected comments.
- A response plan for each addressed comment (path + rationale + verification).

## Constraints / Safety
- Do not change unrelated code while addressing specific comments.
- Do not run `gh` commands without auth; prompt to authenticate first.
- Avoid destructive git operations; ask before any risky action.

## Example prompts
- "Address the open PR comments on my current branch."
- "Summarize reviewer feedback and fix comments 2 and 4."
- "Use gh to fetch PR review threads and propose fixes."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Variation rules
- Vary depth of fixes based on comment severity (nit vs correctness vs design).
- Vary response style by reviewer role (maintainer vs peer) and repo norms.
- Vary evidence depth by change risk (simple edits vs behavior changes).
- Prefer different approaches when prior fixes failed or feedback repeats.

## Empowerment principles
- Empower the user to pick which comments to address first.
- Empower reviewers with concise evidence of the change (path + rationale).
- Empower maintainers with clear trade-offs and rollback options.
- Empower teams to defer non-blocking comments explicitly.

## Anti-patterns to avoid
- Changing unrelated code while addressing a single comment.
- Responding without confirming ambiguous intent.
- Hiding trade-offs or breaking tests to “satisfy” a comment.
- Anti-pattern: replying before verifying CI status or local tests.
- Anti-pattern: bundling multiple comment fixes without labeling them.

## 1) Inspect comments needing attention
- Run scripts/fetch_comments.py which will print out all the comments and review threads on the PR

## 2) Ask the user for clarification
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for it
- Ask the user which numbered comments should be addressed

## 3) If user chooses comments
- Apply fixes for the selected comments

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.

## Stack-specific variants

### claude variant
Frontmatter:

```yaml
---
name: gh-address-comments
description: Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and prompt the user to authenticate if not logged in.
metadata:
  short-description: Address comments in a GitHub PR review
---
```
Body:

# PR Comment Handler

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Philosophy
- Respect reviewer intent; clarify before changing behavior.
- Prefer minimal, verifiable fixes over sweeping refactors.
- Keep changes traceable to specific comments and evidence.
- Explain the why in responses, not just the what.
- Optimize for reviewer trust and project continuity.

## Guiding questions
- What is the reviewer’s intent and expected outcome?
- Why is this comment raised now (correctness, design, consistency, or risk)?
- What is the smallest change that resolves the issue?
- How will this change be verified (tests, lint, evidence)?

## When to use
- When the user asks to address review comments on an open GitHub PR.
- When the user wants to respond to reviewer feedback using `gh` CLI.
- When the user needs a summary of PR review threads before fixing.
- When the user asks to verify `gh` auth or fetch PR comments.

## Inputs
- Current git branch and repository context.
- `gh` CLI authenticated session and repo access.
- User-selected comment numbers to address.

## Outputs
- A numbered summary of review threads and proposed fixes.
- Code changes addressing selected comments.
- A response plan for each addressed comment (path + rationale + verification).

## Constraints / Safety
- Do not change unrelated code while addressing specific comments.
- Do not run `gh` commands without auth; prompt to authenticate first.
- Avoid destructive git operations; ask before any risky action.

## Example prompts
- "Address the open PR comments on my current branch."
- "Summarize reviewer feedback and fix comments 2 and 4."
- "Use gh to fetch PR review threads and propose fixes."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Variation rules
- Vary depth of fixes based on comment severity (nit vs correctness vs design).
- Vary response style by reviewer role (maintainer vs peer) and repo norms.
- Vary evidence depth by change risk (simple edits vs behavior changes).
- Prefer different approaches when prior fixes failed or feedback repeats.

## Empowerment principles
- Empower the user to pick which comments to address first.
- Empower reviewers with concise evidence of the change (path + rationale).
- Empower maintainers with clear trade-offs and rollback options.
- Empower teams to defer non-blocking comments explicitly.

## Anti-patterns to avoid
- Changing unrelated code while addressing a single comment.
- Responding without confirming ambiguous intent.
- Hiding trade-offs or breaking tests to “satisfy” a comment.
- Anti-pattern: replying before verifying CI status or local tests.
- Anti-pattern: bundling multiple comment fixes without labeling them.

## 1) Inspect comments needing attention
- Run scripts/fetch_comments.py which will print out all the comments and review threads on the PR

## 2) Ask the user for clarification
- Number all the review threads and comments and provide a short summary of what would be required to apply a fix for it
- Ask the user which numbered comments should be addressed

## 3) If user chooses comments
- Apply fixes for the selected comments

Notes:
- If gh hits auth/rate issues mid-run, prompt the user to re-authenticate with `gh auth login`, then retry.
