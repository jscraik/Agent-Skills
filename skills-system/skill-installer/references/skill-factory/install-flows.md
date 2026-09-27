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

### Approved transitional runtime installation

Jamie approved a temporary cutover on 2026-09-27: install only the explicitly
selected existing custom skills into `~/.agents/skills`, without requiring prior
Skills SDK processing or Tessl delivery until SDK can run its required workflows.
Keep them classified as unchecked transitional installations, not SDK-cleared
or release-ready packages. This exception does not apply to new external intake
or implicitly extend to plugins.

Preserve complete packages, supporting resources, provenance and recovery.
Check external file and command dependencies separately from discovery; a copied
folder does not prove an independent working workflow. Keep remaining custom
skills in Foundry holding outside active discovery. Preserve provider-managed
system skills and plugin state. Do not expose the entire holding collection or
retain a second custom collection through `~/.codex/skills`.

For a selected GitHub-backed runtime install, pass `--dest "$HOME/.agents/skills"`
explicitly to the upstream installer. Its default destination and installed-list
annotations may still refer to `$CODEX_HOME/skills`; do not use that default or
those annotations as proof of the selected destination. Inspect existing aliases
before writing, preserve recovery, and verify discovery after installation.

This is a local Skill Factory policy extension, not an upstream system-skill
patch. Maintain it here during bridge refreshes; leave the upstream installer
and provider-managed system files unchanged. Retire the temporary exception only
after the required SDK workflows and integrations have been proved.

### External intake and managed promotion

The following intake and hardening procedures apply to their selected lanes;
they do not reinstate SDK/Tessl prerequisites for the temporary cutover above.

- Treat install as **External Skill Intake**, not a copy operation.
- Before writing, inspect local candidates with `./bin/ask skills list --advanced --json` and targeted searches over `Skills/**`, `Plugins/**/skills/**`, and `skills-system/**`.
- Compare intent, trigger wording, scripts/assets, safety boundaries, and closeout contract against the closest local candidates.
- The repo-owned install command returns `data.intake_decision` in dry-run and real install paths. Review this **Intake Decision** before writing canonical source.
- Report one intake outcome before writing:
  - `install_new`: no close match exists; create canonical source.
  - `blend_into_existing`: a local skill owns the behavior; copy only the useful external procedure, helper, eval, or reference into that owner.
  - `keep_separate`: overlap exists, but the external skill is a distinct primitive with its own trigger.
  - `reject_duplicate`: the external skill adds no durable capability.
  - `needs_human_choice`: ownership or visibility is ambiguous.
- Stop before writing when the intake outcome is `reject_duplicate` or `needs_human_choice`; the operator must choose whether to blend, keep separate, reject, or install as a new primitive.
- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- Aborts if the destination skill directory already exists.
- Installs into repo-canonical `<category>/<skill-name>` under the canonical git source tree.
- In Agent Skills Kit, use `./bin/ask skills install <github-url> --json --robot`; this preserves upstream `.system` routing while writing to canonical source.
- Use the raw `scripts/install-skill-from-github.py` helper for an explicitly selected runtime-only install with `--dest "$HOME/.agents/skills"`; do not rely on its legacy destination default.
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Post-install hardening

Canonical installs must not stop at copied source. Before promoting a command handle or claiming readiness:

- Run `./bin/ask sdk start <path> --json --robot`; the start receipt is the
  shared authority for install, update, skillify, refactor, and builder lanes.
- Add or refresh `references/contract.yaml` and `references/evals.yaml`.
- Ensure the frontmatter description says what the skill does and when to use it.
- Add required local safety sections or references when strict audit requires them.
- Add prompt-injection expected-context config only for deliberate security/eval fixtures, not to suppress real helper risks.
- Run `./bin/ask skills audit <path> --level strict --json --robot` and either fix failures or report the skill as installed but not release-ready.
- Run SDK deterministic proof before Tessl or promotion claims:
  `./bin/ask sdk security risk-modes <path> --preview --json --robot`,
  `./bin/ask sdk eval scenario-quality <path> --preview --json --robot`,
  `./bin/ask sdk eval scorer-quality <path> --preview --json --robot`, and
  `./bin/ask sdk eval scorer-calibration <path> --preview --json --robot`.
- Run scenario behavior proof through the read-only Codex profile lanes in order:
  `./bin/ask sdk eval run <path> --runner internal --mode smoke --codex-profile oss-local --json --robot`
  then `./bin/ask sdk eval run <path> --runner internal --mode smoke --codex-profile oss-cloud --json --robot`.
- Run Tessl local proof with execute evidence before dry-run or live scoring:
  `./bin/ask sdk eval tessl-local-proof --skill <path> --workspace jscraik --execute --json --robot`.
- Run Tessl live-private dry-run only after the prior gates pass, using controlled staged input:
  `./bin/ask evals run <path> --mode smoke --runner discovery-smoke --tessl-live-private --tessl-workspace jscraik --tessl-live-dry-run --json --robot`.
- Run `./bin/ask sdk eval handoff-readiness --skill <path> --preview --json --robot` before live Tessl scoring or any release-readiness claim.
- Treat oss-local as the 70-75 internal discovery band, oss-cloud as the path
  to >=90 internal confidence, and Tessl live-private as confirmation at >=90
  and >= baseline. If Tessl finds basic skill-behavior or fixture failures,
  patch the SDK validator, scenario, rubric, reference, or judge contract and
  rerun from oss-local before spending another live confirmation run.
- Run `./bin/ask skills external-review <path> --json --robot` as the **Second-Review Lane** for Plugin Eval and Tessl local review before claiming quality.
- Run release evals only after the SDK handoff gates are current; blocked SDK gates stop command-handle promotion, canonical routing, blending into an existing skill, or release-readiness claims.
- Include Snyk in the release/security lane for manifest-backed candidates. Pure `SKILL.md`-first instruction-only candidates without supported dependency manifests should be reported as `not_applicable` for Snyk.
- Run workspace sync/proof only after the canonical source decision and hardening state are clear.

## Boundary routing matrix

- Route to `.system/skill-installer` when the user intent is list/install/visibility on already-authored skills.
- Route to `.system/skill-creator` when the user asks to create, restructure, or rewrite skill package content.
- Route to `skill-builder` when the user asks to audit, harden, benchmark, or
  check an existing skill package. Use `skill-factory-router` only when the
  downstream owner is ambiguous or routing itself is requested.
- If a single request mixes install plus restructuring/hardening, split the response into phases and state the active phase explicitly before running commands.

## Boundary failure signatures

- Symptom: an external skill is copied before checking for local overlap.
  - Fix: stop, run the intake comparison, and either blend, keep separate, reject, or ask for ownership choice.
- Symptom: install flow starts rewriting contracts/evals before any source-resolution step.
  - Fix: route new content scaffolding to `.system/skill-creator` and existing
    package hardening to `skill-builder`, then return to install flow.
- Symptom: readiness claims are made without strict audit or benchmark evidence.
  - Fix: hand off to `skill-builder` in the explicitly selected validation or
    promotion mode before making the corresponding readiness claim.
- Symptom: user asks only "what can I install?" but response launches hardening commands.
  - Fix: stay in list/install mode and keep hardening out of scope unless explicitly requested.

## Trigger examples

- "Show me curated skills I can install right now, then install `linear`."
- "Check whether `skills/.experimental` exists, then list it if available."
- "Install this private repo skill from `https://github.com/acme/private-repo/tree/main/skills/my-skill`."
- "Repair runtime visibility for this already-installed skill and tell me whether Codex needs a restart."

## Command examples

The raw helper examples below require an explicitly authorised runtime install;
they do not bypass intake or SDK checks outside the transitional exception.
Listing annotations describe the helper's default location, not verified
installation in `~/.agents/skills`.

```bash
# Agent Skills Kit canonical install
./bin/ask skills install "https://github.com/<owner>/<repo>/tree/<ref>/<path>" --json --robot

# List curated skills
python3 skills-system/skill-installer/scripts/list-skills.py

# List experimental skills
python3 skills-system/skill-installer/scripts/list-skills.py --path skills/.experimental

# Explicit runtime destination for an authorised curated install
python3 skills-system/skill-installer/scripts/install-skill-from-github.py --repo openai/skills --path skills/.curated/<skill-name> --dest "$HOME/.agents/skills"

# Explicit runtime destination for an authorised GitHub install
python3 skills-system/skill-installer/scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path> --dest "$HOME/.agents/skills"
```
