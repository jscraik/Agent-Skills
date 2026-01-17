# Portable skills for Claude Code and Codex

Use this guide when authoring a single skill that must work in both Claude Code and OpenAI Codex. Follow the strict subset rules to avoid parser mismatches and loading failures.

## Portability contract (strict subset)

### File and YAML rules
- Name the file exactly `SKILL.md`.
- Start YAML frontmatter on line 1 and end with `---`.
- Use spaces in YAML (no tabs).
- Keep `name` and `description` on a single line.
- Use forward slashes in paths (for example, `references/guide.md`).

### Name and description limits
Use the tightest limits that all platforms accept:
- `name`: 1 to 64 characters, lowercase letters, digits, and hyphens only; no leading/trailing hyphen; no `--`; must match the parent folder name.
- `description`: 1 to 500 characters, single line. Include both what the skill does and when to use it.

### Frontmatter fields
- Codex requires only `name` and `description` and ignores extra keys.
- The open Agent Skills spec allows optional fields like `license`, `compatibility`, `metadata`, and `allowed-tools`.
- For portability, use only spec-defined optional fields and keep them minimal.

### Directory layout
```
<skill-name>/
  SKILL.md
  scripts/
  references/
  assets/
```
Keep `SKILL.md` concise and push depth into `references/`.

### Avoid symlinks
Codex ignores symlinked skill directories. Use a copy/sync step if you maintain a canonical source folder.

## Invocation and loading differences

### Progressive disclosure
Both ecosystems load only `name` and `description` at startup. The body of `SKILL.md` (and references) is loaded only when the skill is invoked.

### How skills get invoked
- Codex supports explicit invocation (`/skills` or `$skill-name`) and implicit invocation when the task matches the description.
- Claude Code is primarily model-invoked and asks for confirmation before loading and using the skill.

Author the skill body so it works in both explicit and implicit flows: start with required inputs and tell the agent to ask for missing data.

## Always-on guidance (rules vs skills)

- Codex uses `AGENTS.md` (and `AGENTS.override.md`) as always-on instructions.
- Claude Code uses `CLAUDE.md` as always-on instructions.

To avoid drift, keep shared rules in one canonical doc and mirror them into the other system's always-on file.
When documenting Claude Code environments, specify dependencies and commands in `CLAUDE.md`, and source `AGENTS.md` via `@AGENTS.md` to keep a single source of truth when both are present.

## Where skills live

- For this repo, the canonical location is `~/dev/agent-skills/skills` (symlinked view).
- Codex also loads skills from repo scopes (for example, `.codex/skills`) and user scope (`~/.codex/skills`), with higher precedence overriding lower scopes.
- Claude Code loads skills from `.claude/skills` (project) and `~/.claude/skills` (user).

If your team uses both tools, ensure the same skill exists in `~/dev/agent-skills/skills/<skill-name>` and `.claude/skills/<skill-name>`.

## Troubleshooting checklist

- If a skill does not appear in Codex, restart Codex after adding or editing skills.
- Confirm the file name is `SKILL.md` and the YAML is valid.
- Ensure `name` and `description` are within limits and single line.
- If using symlinked skill directories, ensure they resolve to real directories and that Codex can follow them.

## Trigger tests (portable)

Keep a small set of prompts to validate routing:
- Two prompts that should clearly trigger the skill.
- One prompt that should not trigger.
- One ambiguous prompt to test disambiguation.

## Disambiguation clause for overlapping skills

If multiple skills could match, pick the one whose description mentions the most specific artifacts (filetype, tool, or domain). Otherwise ask a single clarifying question before invoking a skill.

## Make outputs machine-checkable by default

Even for human-facing outputs, define:
- exact output filenames or paths
- schemas for JSON outputs
- validation steps

This improves determinism without adding scripts.

## Place quality gates before next steps

After any transformation step, add a "Validation loop" or "Quality gates" section before listing next steps. This reduces failures from moving on too early.

## Sources (verify for updates)
- OpenAI Codex skills docs: https://developers.openai.com/codex/skills/
- OpenAI Codex create-skill docs: https://developers.openai.com/codex/skills/create-skill/
- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md/
- Claude Code skills docs: https://code.claude.com/docs/en/skills
- Agent Skills spec: https://agentskills.io/specification
