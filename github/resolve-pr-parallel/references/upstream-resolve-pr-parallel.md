# Upstream Resolve PR Parallel

Pinned source:
- `https://github.com/EveryInc/compound-engineering-plugin/blob/0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b/plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md`
- `https://github.com/EveryInc/compound-engineering-plugin/tree/0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b/plugins/compound-engineering/skills/resolve-pr-parallel/scripts`

Read when:
- You need the full imported CE doctrine rather than the tighter local routing layer.
- You are checking whether a local simplification accidentally dropped useful operational detail.

## Preserved upstream frontmatter
- `name: resolve-pr-parallel`
- `description: Resolve all PR comments using parallel processing. Use when addressing PR review feedback, resolving review threads, or batch-fixing PR comments.`
- `argument-hint: "[optional: PR number or current PR]"`
- `disable-model-invocation: true`
- `allowed-tools: Bash(gh *), Bash(git *), Read`

## Preserved upstream workflow
1. Analyze
   - Fetch unresolved review threads with `scripts/get-pr-comments`.
   - Fallbacks:
     - `gh pr view PR_NUMBER --json reviews,comments`
     - `gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments`
2. Plan
   - Group unresolved work into code changes, questions, style fixes, and tests.
3. Implement in parallel
   - Spawn one resolver per unresolved item.
   - For 1-4 unresolved items, direct parallel returns are acceptable.
   - For 5+ unresolved items, batch at most 4 at a time.
   - For larger noisy runs, use a per-run scratch directory and keep child summaries short.
4. Commit and resolve
   - Commit changes with feedback-oriented messaging.
   - Resolve each review thread programmatically.
   - Push the branch.
5. Verify
   - Re-fetch unresolved review threads and expect `[]`.
   - Clean up scratch artifacts when they are no longer needed.

## Preserved upstream success criteria
- All unresolved review threads addressed
- Changes committed and pushed
- Threads resolved on GitHub
- Empty unresolved-thread result on verification

## Local adaptation notes
- The local skill adds explicit boundaries against `check-pr`, `gh-workflow`, `ce-review`, and `ce-technical-review`.
- The local scripts improve on the upstream helpers by adding pagination-safe thread fetching and a batch thread-resolution helper.
- The local skill uses Codex-native terminology for delegated remediation and blocked-state handling, but keeps the upstream execution shape intact.
