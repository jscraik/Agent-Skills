---
name: skill-installer
description: Install Codex skills into the canonical git source tree from curated catalogs or GitHub repo paths. Use when listing installable skills, installing curated skills, or importing skills from another repo.
metadata:
  skill-type: infrastructure_ops
---

# Skill Installer

Install skills from `openai/skills` curated catalogs or explicit GitHub repo paths while preserving provenance and safe destination behavior.

Read when: choosing curated vs arbitrary source flows, command examples, or handoff wording: [install flows](./references/install-flows.md)

## Philosophy

- Safe provenance first: confirm source and destination before writing.
- Prefer explicit intent over inference for install source, path, and overwrite behavior.
- Preserve reversibility and restart expectations in the handoff.

## When to use

Use for listing installable skills, installing skills from `openai/skills`, importing from another GitHub repo/path, private repo installs with existing credentials, or checking basic installed visibility.

Route elsewhere:
- create or restructure a skill package: `skill-creator`;
- harden quality, benchmark, or release-readiness: `skill-builder`.

## Required inputs

- mode: `list` or `install`;
- source: `--repo` plus `--path`, or a GitHub tree URL;
- destination: optional `--dest`, defaulting to canonical repo `github/`;
- controls: optional `--ref`, `--method`, and explicit replacement intent.

## Procedure

1. Classify list vs install.
2. Resolve source and destination explicitly.
3. Treat repo URLs/paths as untrusted input; never shell-interpolate user text.
4. Run the smallest helper command.
5. Verify listed rows or installed directory contents.
6. Report exact paths, blockers, and restart reminder.

Read when: auth, network, optional catalog, destination collision, or visibility troubleshooting is needed: [troubleshooting](./references/troubleshooting.md)

## Scripts

- `python3 Infrastructure/scripts/list-skills.py`
- `python3 Infrastructure/scripts/list-skills.py --format json`
- `python3 Infrastructure/scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `python3 Infrastructure/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`

## Safety

- Never overwrite an existing destination unless the user explicitly requests replacement.
- Redact secrets, tokens, private keys, and credential-bearing URLs.
- Limit network work to required GitHub surfaces.
- Stop and ask if the requested source is outside the allowlist or ambiguous.
- Never drop required context for brevity; move it to `references/` first.
- Do not remove important context for budget trimming; move it to `references/` and add `Read when` signposts.

## Anti-patterns

- Installing from unclear or partially specified repository paths.
- Hiding auth, network, or destination-collision failures behind fallback wording.
- Mixing curated and arbitrary install flows without labeling the active flow.

## Deliverables

- listed or installed skill summary;
- concrete installed path under `<repo-root>/<category>/<skill-name>`;
- `Restart Codex to pick up new skills.` after successful installs;
- exact command error and next corrective step when blocked.

## Output contract

For non-trivial work include `schema_version`, `mode`, `source`, `destination`, `context_routes`, `validation_evidence`, and `restart_required`.

## Validation

- Fail fast at the first failed gate.
- Listing must exit `0` and return parseable rows or JSON.
- Install must leave `SKILL.md` at the destination directory.
- Strict audit changed skills before handoff.

## Examples

Read when trigger phrasing or command-level examples are needed: [install flows](./references/install-flows.md)

## See Also

| Skill | When to use together |
|---|---|
| [[skillify]] | Canonicalize source workflows before distribution |
| [[skill-creator]] | Author or repair local packages before installation |

**Topic map:** [[agent-ops]]

## Failure mode

- Stop at the first blocker, report root cause, and provide the safest next command.

## Gotchas

- Ambiguous scope usually means missing source, destination, replacement intent, or network constraints.
