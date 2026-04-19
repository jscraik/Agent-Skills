# Install Flows

Read when: you need concrete output wording, install/list flow selection, or option behavior details that are too verbose for `SKILL.md`.

## Communication template

When listing skills, output approximately as follows, depending on the context of the user's request. If they ask about experimental skills, first verify the `.experimental` path exists; if it does not, state that it is unavailable and continue with `.curated` (or another explicit source):

```
Skills from {repo}:
1. skill-1
2. skill-2 (already installed)
3. ...
Which ones would you like installed?
```

After installing a skill, tell the user: `Restart Codex to pick up new skills.`

## Flow behavior and options

- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into repo-canonical `<category>/<skill-name>` under the canonical git source tree.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Boundary routing matrix

- Route to `skill-installer` when the user intent is list/install/visibility on already-authored skills.
- Route to `skill-creator` when the user asks to create, restructure, or rewrite skill package content.
- Route to `skill-builder` when the user asks to harden, benchmark, or gate-readiness-check an existing skill package.
- If a single request mixes install plus restructuring/hardening, split the response into phases and state the active phase explicitly before running commands.

## Boundary failure signatures

- Symptom: install flow starts rewriting contracts/evals before any source-resolution step.
  - Fix: route content restructuring to `skill-creator` or `skill-builder`, then return to install flow.
- Symptom: readiness claims are made without strict audit or benchmark evidence.
  - Fix: hand off to `skill-builder` before claiming release readiness.
- Symptom: user asks only "what can I install?" but response launches hardening commands.
  - Fix: stay in list/install mode and keep hardening out of scope unless explicitly requested.

## Trigger examples

- "Show me curated skills I can install right now, then install `linear`."
- "Check whether `skills/.experimental` exists, then list it if available."
- "Install this private repo skill from `https://github.com/acme/private-repo/tree/main/skills/my-skill`."

## Command examples

```bash
# List curated skills
python3 Infrastructure/scripts/list-skills.py

# List experimental skills
python3 Infrastructure/scripts/list-skills.py --path skills/.experimental

# Install one curated skill
python3 Infrastructure/scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/<skill-name>

# Install from GitHub URL
python3 Infrastructure/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>
```
