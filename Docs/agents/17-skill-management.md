# Skill Management

## Purpose

Keep skill authoring and lifecycle details out of the always-loaded root
instructions while preserving the commands agents need when working on skills.

Before changing skills, sync policy, runtime projections, or agent-facing docs,
read [UBIQUITOUS_LANGUAGE.md](/UBIQUITOUS_LANGUAGE.md).

## User Runtime Links

Home-directory skill links are live runtime surfaces, not disposable local
shortcuts. Before deleting a worktree, pruning a branch checkout, or moving a
projection directory, verify that `~/.agents/skills` and `~/.codex/skills` do
not point into the removed tree. If they do, repair the link or run the owning
sync command first, then prove visibility with:

```bash
./bin/ask skills load-preview --json --robot
./bin/ask skills proof unslopify --runtime-target codex --json --robot
find -L ~/.agents/skills -maxdepth 4 -name SKILL.md
find -L ~/.codex/skills -maxdepth 4 -name SKILL.md
```

Treat a dangling runtime link as a runtime outage even when the git cleanup was
otherwise correct. The repo is clean only in the git lane; picker readiness is a
separate runtime-projection lane.

### Curated transition set

`~/.codex/skills`, `~/.codex/plugins`, and their `~/.agents` counterparts may
temporarily expose a curated transition set while packages await SDK admission.
That availability is neither a source-of-truth decision nor an admission into
the active SDK workspace. Preserve an unmanaged package copy-first in
`/Users/jamiecraik/dev/skills-foundry`, retain its provenance there, and start
active SDK work only after an explicit owner decision names the candidate source
and bounded task. Do not remove, relink, install, publish, or promote a runtime
package merely because its source is being retained or reviewed.

## Runtime Proof Before Skill Use

Canonical skill source existence is not runtime authorization. When a user,
workflow, or handoff asks an agent to use `$<skill>`, a failed runtime proof,
route check, or user-runtime-link check blocks active use of that skill.

Reading `SKILL.md` directly is allowed only for source inspection, repair,
audit, or package hardening. In that mode, report the claim boundary plainly:
the canonical source was inspected, but the runtime skill was not available.
Do not apply the skill procedure as if the runtime invocation succeeded, and
do not claim the skill was used until the runtime surface is repaired and
proved.

## Install Failure Recovery

```bash
./bin/ask skills install <url> --remediate --robot
./bin/ask skills audit <path> --level strict --robot
```

Use `--remediate` to scaffold missing files during install recovery, then run a
strict audit before treating the skill as ready.

Skill setup must follow the [Zero-Setup Agent Workspace](/Docs/agents/21-zero-setup-agent-workspace.md)
product rule. A skill is not professionally ready if it requires the customer
to manually stitch together install, projection, runtime, and validation steps
before an agent can discover and report readiness.

High-level workflow skills whose truth lives in UI or app state need
[CTF Workflow Evals](/Docs/agents/23-ctf-workflow-evals.md) before a
release-readiness claim. Examples include login, upload-and-chat, access grants,
and other workflows where capturing a planted flag is the practical proof of
success.

## Plugin Desktop Readiness

Plugin install success is not the same as Codex Desktop loadability. Before
claiming a local plugin is usable in the GUI, verify the
`plugin-desktop-readiness.v1` contract exposed by:

```bash
./bin/ask plugins status <plugin> --json --robot
```

Use `data.desktop_readiness_state.desktop_loadable` as the claim boundary. A
plugin is not GUI-ready until the contract proves all of these lanes:

- repo plugin cache content is ready;
- the active Codex config enables the plugin id and has no stale enabled plugin
  ids outside the active marketplace;
- the official personal marketplace at `~/.agents/plugins/marketplace.json`
  resolves the plugin source path to `~/.codex/plugins/<plugin-name>`;
- the Codex profile compatibility marketplace resolves the plugin source path
  to a symlink alias of the same canonical plugin payload, or to a case-only
  samefile path on case-insensitive filesystems;
- the resolved plugin root has `.codex-plugin/plugin.json` and any
  manifest-declared skills contain `*/SKILL.md`.

Use the official personal marketplace as the canonical user-facing shape:
`~/.agents/plugins/marketplace.json` should contain one marketplace payload for
all local plugins, with each local `source.path` starting with `./` and staying
inside the marketplace root. For project-local plugins materialized at
`~/.codex/plugins/<plugin-name>`, write `./.codex/plugins/<plugin-name>`.
The sync wrapper may also create `~/.agents/plugins/<plugin-name>` symlinks to
the materialized plugin directory for operator discoverability. The
`~/.agents/plugins` root itself must stay a real directory on each macOS host,
not a symlink to a repo, feature worktree, or profile mirror. On
case-insensitive filesystems, `plugins` and `Plugins` can resolve to the
same directory, so pointing the official personal marketplace at the repo
source tree can overwrite `Plugins/marketplace.json` with personal
`./.codex/plugins/<plugin-name>` paths. On multi-machine setups, a root symlink
can also point at a checkout that only exists on one Intel or Apple Silicon Mac,
making the Desktop picker drop local plugins after sync, prune, or worktree
cleanup.

Keep `~/.codex/.agents/plugins/marketplace.json` as a compatibility mirror
while Desktop/runtime compatibility requires it. That mirror must point to
`./.agents/plugins/<plugin-name>`, and that path must be an alias to
`~/.codex/plugins/<plugin-name>` rather than an independent copy. Repository
source marketplaces can still use `./Plugins/<plugin-name>` because their
marketplace root is the repo root. Plugin runtime/package caches must preserve
manifest-declared skill content; duplicate suppression belongs in
picker/projection surfaces, not in the loader package cache.

For one-command install flows, prefer:

```bash
./bin/ask plugins install <url> --path <plugin-path> --sync-profile --require-desktop-loadable --json --robot
```

If this command is blocked by profile write permissions, report the blocker and
rerun the profile sync with explicit write access rather than claiming the
plugin is installed for Desktop:

```bash
./bin/ask plugins sync-local-runtime --json --robot
```

If `data.desktop_readiness_state.stale_enabled_plugin_ids` is non-empty, do not
keep hand-editing the config. Use the wrapper repair command so the stale IDs
come from the readiness contract and the result is rechecked across the
post-prune stability window:

```bash
./bin/ask plugins prune-stale-config --json --robot
```

If Codex Desktop or another config writer keeps restoring the stale ID after the
default watch window, rerun with a longer explicit window and treat a failed
stability check as evidence that the external writer must be stopped or
refreshed before closeout:

```bash
./bin/ask plugins prune-stale-config --stability-seconds 30 --json --robot
```

When the config is already clean but a stale ID has repeatedly reappeared, prove
the clean state is stable before closeout:

```bash
./bin/ask plugins prune-stale-config --verify-stable-when-clean --stability-seconds 30 --json --robot
```

## Folding Strategy

If `./bin/ask skills fold source target --robot` returns confidence `>= 0.2`, fold
rather than duplicate unless the user explicitly wants a separate skill.

## Line Budget

Keep `SKILL.md` bodies at or below the 360-line split budget. When a skill
exceeds that budget, move bulk detail to a focused reference file and leave a
clear link in the `SKILL.md`.

Do not delete important, still-valid context just to reduce line count. Preserve
that context by relocation, not by leaving it in the entrypoint.

Removed context must have a disposition:

- `moved-to-reference`: still valid, reusable, and too bulky for `SKILL.md`.
- `superseded`: replaced by a newer compressed rule or reference.
- `intentionally-discarded`: stale, duplicated, unsafe, inappropriate,
  contradicted by newer guidance, or no longer part of the skill contract.
- `not-context`: formatting, navigation, repetition, or low-signal prose.

Do not create context landfills. Deferred references should protect useful
knowledge, not preserve stale or inappropriate text for its own sake.

## Reference Quality

References are part of the Skills SDK package contract, not spare notes. Treat
them like scripts: if a skill uses `references/**`, those files must work for
future agents at package-readiness time.

The SDK package contract reports `values.reference_quality` and
`./bin/ask skills package verify <skill> --json --robot` blocks broken reference
sets. The minimum enforced floor is:

- every file under `references/` is readable and non-empty;
- structured references (`.json`, `.yaml`, `.yml`) parse successfully;
- `references/contract.yaml`, when present, declares purpose, inputs, and
  outputs;
- `references/evals.yaml`, when present, declares claims and cases.

Passing this floor does not prove that a reference is great; it prevents known
low-quality reference packages from being promoted as ready. When a reference
drives execution, evals, rollback, validation, or policy, keep it specific,
current, and runnable enough that an agent can use it without re-deriving the
contract from chat history.

See [Tooling and Command Policy](/Docs/agents/02-tooling-policy.md#skill-line-budget-policy)
for the detailed policy.
