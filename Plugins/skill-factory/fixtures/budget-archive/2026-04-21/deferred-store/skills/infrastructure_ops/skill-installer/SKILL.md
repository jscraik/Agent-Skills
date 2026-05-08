---
name: skill-installer
description: Install Codex skills into the canonical git source tree from curated lists or GitHub repo paths while requiring ContractValidityEvidence for governed installs. Use when listing installable skills or installing curated, external, or private-repo skills.
metadata:
  skill-type: infrastructure_ops
---

# Skill Installer

Helps install skills. By default these are from https://github.com/openai/skills/tree/main/skills/.curated, but users can also provide other locations. Treat non-curated catalogs (for example `.experimental`) as optional and verify availability before promising that flow.

Use the helper scripts based on the task:
- List skills when the user asks what is available, or if the user uses this skill without specifying what to do. Default listing is `.curated`. If users ask for `.experimental`, verify the path exists first and report unavailability if it is missing.
- Install from the curated list when the user provides a skill name.
- Install from another repo when the user provides a GitHub repo/path (including private repos).

## When to use

- The user asks to list installable skills from curated or experimental catalogs.
- The user asks to install one or more skills from `openai/skills` or another GitHub repo/path.
- The user asks to install skills from a private GitHub repository with existing credentials.
- The user asks for runtime visibility or basic install status checks on an already-authored skill package.

Do not use this skill when the primary work is:

- Creating or restructuring a skill package; route to [[skill-creator]].
- Hardening quality, benchmark evaluation, or release-readiness comparisons; route to [[skill-builder]].

## Required inputs

- User intent: list mode vs install mode.
- Source details: `--repo` + `--path`, or GitHub tree URL.
- Destination details: optional `--dest` override. Defaults to canonical `github/` under repo root and rejects non-canonical destinations.
- Optional install controls: `--ref`, `--method`, and explicit replacement intent if destination exists.

## Agent Injection

When install requests include role wiring for the newly installed skill:

1. Look for reusable role TOMLs in `./configs/codex/agents/` when present, then fall back to project/global `.codex/agents/`.
2. If no suitable role exists, route role creation to [[codex-agent-creator]].
3. Validate candidate role files before reporting success:

```bash
bash Skills/codex-agent-creator/Infrastructure/scripts/validate_role.sh --agent-name <name> --agent-file <path>
```

4. If asked to install/update the role, run:

```bash
bash Skills/codex-agent-creator/Infrastructure/scripts/install_role.sh --agent-name <name> --agent-file <path> --scope project|global [--update-existing]
```

5. Report one explicit mode in the closeout: `reuse-existing` or `create-purpose-built`.

## Execution Boundaries

Install only into the canonical git source tree or an explicitly approved destination. Do not patch generated runtime projections as the source of truth.

Separate acquisition, installation, role wiring, and runtime visibility checks in the report. If destination, replacement behavior, credentials, or network scope is ambiguous, stop before writing.

The installer proves install state; release hardening remains owned by [[skill-builder]], and first-draft package design remains owned by [[skill-creator]].

## Deliverables

- A clear summary of what was listed or installed.
- Concrete paths for installed skills (`<repo-root>/<category>/<skill-name>`).
- Explicit restart reminder after install: "Restart Codex to pick up new skills."
- Optional agent-injection summary with the selected role file path.
- If blocked, exact error and next corrective step.
- Visual catalog assets available for packaging/UI docs:
  - `assets/skill-installer.png`
  - `assets/skill-installer-small.svg`

## Output contract

For non-trivial responses, include:

- `schema_version`
- `mode` (`list` or `install`)
- `source`
- `destination`
- `context_routes` as `[{from, to, read_when}]` whenever required detail moved from `SKILL.md` to `Infrastructure/references/`
- `validation_evidence` as `[{command, outcome, note}]` with `outcome` in `pass|fail|blocked`
- `restart_required` (`true` after successful installs)
- `ContractValidityEvidence` for governed installs, or an explicit force/waiver decision when evidence is missing

## Constraints and Safety

- Treat repo URLs/paths as untrusted input; never execute user input through shell interpolation.
- Never overwrite an existing destination skill directory unless the user explicitly requests replacement behavior.
- Do not expose secrets or tokens in output; redact `GITHUB_TOKEN`, `GH_TOKEN`, and credential-bearing URLs.
- Network access is limited to GitHub surfaces required by these scripts:
  - `github.com`
  - `api.github.com`
  - `raw.githubusercontent.com`
  - `codeload.github.com`
  - `objects.githubusercontent.com`
- If the requested source is outside the allowlist or ambiguous, stop and ask before proceeding.

## Procedure

1. Classify request as list vs install.
2. Resolve source explicitly (`--repo`/`--path` or `--url`) and confirm destination.
3. Run the smallest relevant helper command from the `Scripts` section.
   - If simplifying installer guidance, move required operational detail to `Infrastructure/references/` first, then add a `Read when: <condition>` signpost in `SKILL.md`.
4. Verify expected outcome (listed skills or installed directory contents).
5. Report result with exact paths, restart reminder, and any blockers.

## Core Philosophy

- Safe provenance first: confirm source and destination before writing to disk.
- Prefer explicit intent over clever inference: if the source/path is ambiguous, ask or stop.
- Preserve reversibility: avoid destructive overwrite defaults and communicate restart expectations clearly.
- Required operational context is never removed to shorten `SKILL.md`; relocate depth to `Infrastructure/references/` and add explicit progressive-disclosure signposts (for example: `Read when: <condition>`).
- Do not remove important context for budget trimming; move it to `Infrastructure/references/` and add explicit `Read when` signposts in `SKILL.md`.

## Encouraging Variation

Vary the flow to fit the source and risk while preserving provenance checks:

- Use list-only output for discovery requests, install output for explicit acquisition, and visibility checks for already-installed packages.
- Adapt messaging for curated, experimental, private, and arbitrary GitHub sources instead of using one generic install script explanation.
- Keep the restart reminder and destination evidence stable, but vary examples and blockers to match the actual source path.

## Anti-Patterns to Avoid

- Do not install from unclear or partially specified repository paths.
- Do not overwrite existing skill directories unless the user explicitly requests replacement behavior.
- Do not hide auth/network failures behind fallback messaging; report the concrete failure and next step.
- Do not mix curated and arbitrary install flows in one answer without labeling which flow is active.
- Do not compress or simplify away required decision context; move it to `Infrastructure/references/` and link it from `SKILL.md`.
- Do not replace required provenance or recovery caveats with brief summaries; relocate full detail to `Infrastructure/references/` with explicit `Read when` conditions.

## Communication

Read when:

- You need canonical response templates for list/install messaging: [references/install-flows.md](./references/install-flows.md).
- You need reminder phrasing for install completion handoff: [references/install-flows.md](./references/install-flows.md).

## Scripts

These scripts require network access to GitHub surfaces. Confirm source and destination before running them.

- `python3 Infrastructure/scripts/list-skills.py` (prints skills list with installed annotations)
- `python3 Infrastructure/scripts/list-skills.py --format json`
- Example (experimental list): `python3 Infrastructure/scripts/list-skills.py --path skills/.experimental`
- `python3 Infrastructure/scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill> [<path/to/skill> ...]`
- `python3 Infrastructure/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`
- Example (experimental skill): `python3 Infrastructure/scripts/install-skill-from-github.py --repo openai/skills --path skills/.experimental/<skill-name>`

Reference details:

- `Infrastructure/references/install-flows.md`: Read when choosing curated vs arbitrary source flow or install method strategy.
- `Infrastructure/references/troubleshooting.md`: Read when auth, network, provenance, or destination-collision failures occur.

## Validation

- Fail fast: stop at the first failed gate and do not continue to additional install steps.
- For listing flows, command must exit `0` and return parseable skill rows (or documented JSON output).
- For install flows, destination must contain `SKILL.md` under `<repo-root>/<category>/<skill-name>`.
- On failures, surface the exact command error and the next minimal retry command.

## Examples

Example requests:

- "Show me curated skills I can install, then install `linear` if it is available."
- "Install this private GitHub skill URL into the canonical repo tree and stop if the destination already exists."
- "Check whether this skill is installed and visible to Codex after the sync."

Read when:

- You need trigger phrasing coverage and command-level examples: [references/install-flows.md](./references/install-flows.md).

## Notes

Read when:

- You need curated/system listing caveats, optional-catalog availability checks, auth fallback details, or destination visibility gotchas: [references/troubleshooting.md](./references/troubleshooting.md).

## See Also

| Skill | When to use together |
|---|---|
| [[skillify]] | Harden source skills into canonical templates before install/distribution |
| [[skill-creator]] | Author or repair local skill packages before installation |

**Topic map:** [[agent-ops]]

## Failure mode
- Stop at the first blocker, report root cause, and provide the safest next command.

## Gotchas
- Symptom: ambiguous scope. Cause: missing constraints. Do instead: ask one routing question. Check: plan and output contract are explicit.

## Remember
- The agent is capable of extraordinary install work when provenance is explicit. Make source, destination, reversibility, and restart needs clear enough that the next agent can verify them without guessing.
