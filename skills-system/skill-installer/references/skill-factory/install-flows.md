# Install Flows

Read when: you need concrete output wording, install/list flow selection, or option behavior details that are too verbose for `SKILL.md`.

Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, inappropriate,
superseded, or low-signal text.

Local Skill Factory extension references live under
`skills-system/skill-installer/references/skill-factory/`.

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

- Treat install as an intake decision, not a copy operation.
- Before writing, inspect local candidates with `./bin/ask skills list --advanced --json` and targeted searches over `Skills/**`, `Plugins/**/skills/**`, and `skills-system/**`.
- Compare intent, trigger wording, scripts/assets, safety boundaries, and closeout contract against the closest local candidates.
- Report one intake outcome before writing:
  - `install_new`: no close match exists; create canonical source.
  - `blend_into_existing`: a local skill owns the behavior; copy only the useful external procedure, helper, eval, or reference into that owner.
  - `keep_separate`: overlap exists, but the external skill is a distinct primitive with its own trigger.
  - `reject_duplicate`: the external skill adds no durable capability.
  - `needs_human_choice`: ownership or visibility is ambiguous.
- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into repo-canonical `<category>/<skill-name>` under the canonical git source tree.
- In Agent Skills Kit, use `./bin/ask skills install <github-url> --json --robot`; this preserves upstream `.system` routing while writing to canonical source.
- Use the raw `scripts/install-skill-from-github.py` helper only for explicit runtime-only installs into `$CODEX_HOME/skills` or when outside the Agent Skills Kit repo.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Post-install hardening

Canonical installs must not stop at copied source. Before promoting a command handle or claiming readiness:

- Add or refresh `references/contract.yaml` and `references/evals.yaml`.
- Ensure the frontmatter description says what the skill does and when to use it.
- Add required local safety sections or references when strict audit requires them.
- Add prompt-injection expected-context config only for deliberate security/eval fixtures, not to suppress real helper risks.
- Run `./bin/ask skills audit <path> --level strict --json` and either fix failures or report the skill as installed but not gold-ready.
- Run workspace sync/proof only after the canonical source decision and hardening state are clear.

## Boundary routing matrix

- Route to `.system/skill-installer` when the user intent is list/install/visibility on already-authored skills.
- Route to `.system/skill-creator` when the user asks to create, restructure, or rewrite skill package content.
- Route to `skill-builder` when the user asks to harden, benchmark, or gate-readiness-check an existing skill package.
- If a single request mixes install plus restructuring/hardening, split the response into phases and state the active phase explicitly before running commands.

## Boundary failure signatures

- Symptom: an external skill is copied before checking for local overlap.
  - Fix: stop, run the intake comparison, and either blend, keep separate, reject, or ask for ownership choice.
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
- "Repair runtime visibility for this already-installed skill and tell me whether Codex needs a restart."

## Command examples

```bash
# Agent Skills Kit canonical install
./bin/ask skills install "https://github.com/<owner>/<repo>/tree/<ref>/<path>" --json --robot

# List curated skills
python3 skills-system/skill-installer/scripts/list-skills.py

# List experimental skills
python3 skills-system/skill-installer/scripts/list-skills.py --path skills/.experimental

# Install one curated skill
python3 skills-system/skill-installer/scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/<skill-name>

# Install from GitHub URL
python3 skills-system/skill-installer/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>
```
