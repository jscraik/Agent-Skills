# Pull request checklist

## Summary

- What changed (brief):
- Why this change was needed:
- Risk and rollback plan:

## Checklist

- [ ] I did not push directly to `main`; this PR is from a dedicated branch.
- [ ] Branch name follows policy (`codex/*` for agent-created branches).
- [ ] Required local gates run: `bash scripts/validate-codestyle.sh`, `npm run check`, `test -f memory.json && jq -e '.meta.version == "1.0" and (.preamble.bootstrap | type == "boolean") and (.preamble.search | type == "boolean") and (.entries | type == "array")' memory.json >/dev/null`.
- [ ] CodeRabbit review completed and findings handled (or explicitly waived).
- [ ] CodeRabbit review was performed by an independent reviewer (not the coding agent).
- [ ] Codex review completed and findings handled (or explicitly waived).
- [ ] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.
- [ ] Merge is blocked until all required checks pass.
- [ ] I will delete branch/worktree after merge.

## Testing

- verification_commands: list exact commands run here
- verification_outcomes: record pass/fail/blocked for each command here
- blocked_steps_reason: none if all planned steps ran
- Command: `bash scripts/validate-codestyle.sh` -> pass/fail
- Command: `npm run check` -> pass/fail
- Command: `test -f memory.json && jq -e '.meta.version == "1.0" and (.preamble.bootstrap | type == "boolean") and (.preamble.search | type == "boolean") and (.entries | type == "array")' memory.json >/dev/null` -> pass/fail
- Any other command(s):

## Review artifacts

- CodeRabbit: <link / artifact path / comment ID>
- Independent reviewer evidence: <reviewer + link>
- Codex: <link / artifact path / comment ID>
- CodeRabbit Semgrep: fixed / waived with rationale / n.a.
- Additional evidence (if any):

## Notes

Add one-paragraph merge rationale here.
