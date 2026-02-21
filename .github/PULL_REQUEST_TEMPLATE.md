## Summary

[PROMPT: What does this PR do in 1–3 sentences?]

## Motivation / Context

[PROMPT: Why is this change needed? Link context, incidents, or user feedback.]

Closes #[PROMPT: #123] (or explain why none exists)

## What changed?

[PROMPT: Bullet list of key changes.]

## How to test

[PROMPT: Exact commands + expected outcomes.]

- [PROMPT: e.g. pnpm test]
- [PROMPT: e.g. pnpm lint]
- [PROMPT: e.g. pnpm build]

## Risk & rollback

Risk level: low / medium / high

Rollback plan: [PROMPT: Concrete rollback steps if needed.]

## Security / privacy impact

- [ ] No security impact
- [ ] Security impact (describe at high level; do NOT disclose vulnerabilities publicly)

Security/AI risk section:
[PROMPT: High-level description if security impact checked.]

## Governance evidence

### Threat model

- [ ] Threat model exists: [PROMPT: path or short summary]
- [ ] Threat model rationale: [PROMPT: why existing threat model still applies OR new threat changes are required]

### AI and data impact

- [ ] AI/tool execution impact: [PROMPT: new model calls, tool calls, prompt surfaces]
- [ ] Data handling impact: [PROMPT: what user data enters/leaves the system]
- [ ] Privacy / logging changes: [PROMPT: what is logged, masked, retained]

### Verification evidence

- [ ] Test evidence included (commands + results)
- [ ] Dependency / secret checks run where applicable
- [ ] PR body includes release artifact notes:
  - [ ] SBOM added (if release path changed)
  - [ ] Provenance/signature artifacts noted (if release path changed)

## Review of exception/incident updates

- [ ] New control bypasses documented in `GOVERNANCE/exceptions.md` (if any)
- [ ] Related incidents documented in `GOVERNANCE/incidents.md` (if any)

## AI assistance

- [ ] This PR was created with AI assistance (mark with `[AI]` in title if applicable)
- [ ] Testing level: untested / lightly tested / fully tested
- [ ] I understand what the code does and can explain it
- [ ] Prompts or session logs included (Optional, but helpful)

Prompt: `[PROMPT: artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml]`
Session: `[PROMPT: artifacts/ai/sessions/YYYY-MM-DD-<slug>.json]`

<details>
<summary>AI Session Log (click to expand)</summary>

[PROMPT: Short AI session summary]

- Log file: `[PROMPT: artifacts/ai/sessions/YYYY-MM-DD-<slug>.json]`
- Prompt file: `[PROMPT: artifacts/ai/prompts/YYYY-MM-DD-<slug>.yaml]`
- Files touched: [PROMPT: paths]
- Tests run: [PROMPT: commands]
- Human verification: [PROMPT: what you personally checked]

</details>

## Checklist

- [ ] Linked an issue or explained why none exists
- [ ] Added/updated tests or explained why not
- [ ] Updated docs where needed (Required for behavior/config/API/CLI changes)
- [ ] Internal docs links use full root paths (for example, `/docs/deployment`)
- [ ] Internal docs links do not use trailing slashes
- [ ] Ran docs lint: `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- [ ] Considered backward compatibility / migrations (Optional)
- [ ] Verified no secrets are committed (tokens, keys, passwords)
- [ ] Confirmed CI is green (or explained failures)

## Release notes

Release note: [PROMPT: user-facing note, or "None".]
