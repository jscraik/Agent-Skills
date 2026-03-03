# agent-skills Greptile rules

## Scope

Repository-specific review expectations for skills, governance docs, and automation scripts.

## Rule set

### 1) Independent validation is mandatory

- The coding agent must not act as approving reviewer on the same PR.
- Review artifacts must come from an independent validation pass.

### 2) Governance docs must remain aligned

If a PR changes any of the following, reviewers must verify consistency across touched files:

- `/AGENTS.md`
- `/README.md`
- `/harness.contract.json`
- `/CONTRIBUTING.md`
- `/.github/PULL_REQUEST_TEMPLATE.md`

### 3) Skill metadata contract

- Every `SKILL.md` must keep valid frontmatter with `name` and `description`.
- Skill docs must keep actionable, deterministic command examples.

### 4) Documentation hygiene

- Internal docs links must use full root paths (for example `/docs/agents/...`).
- Internal docs links should avoid trailing slashes.

### 5) Merge confidence threshold

- Confidence < 4/5 is merge-blocking.
- Confidence 4/5 may merge only when remaining comments are non-logic polish.
- Confidence 5/5 is merge-ready.
