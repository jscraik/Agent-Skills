# Skills SDK Runtime Lane Contract

## Purpose

Use this contract whenever Skills SDK work needs runtime, judge, or Tessl proof.
It encodes the promotion pipeline for skill changes and separates lanes that
must not be substituted for one another:

- SDK mechanical validation
- oss-local flow
- oss-cloud flow
- Tessl local flow
- Tessl external flow

A skill moves forward only when the current lane passes or when the operator
explicitly accepts a blocker. If a command from one lane blocks, report that
lane as blocked. Do not replace it with a different lane and call the original
proof complete.

## Promotion Pipeline

1. SDK mechanical validation: prove the package shape, scenario metadata,
   scorer metadata, scorer calibration, docs projection, and strict audit.
2. oss-local flow: run the skill or A/B judge through `codex exec --profile
oss-local`; iterate until the sandboxed local OSS lane is valid, then move
   to the next model lane.
3. oss-cloud flow: run the same proof through `codex exec --profile oss-cloud`;
   iterate until the sandboxed cloud OSS lane is valid, then move to Tessl.
4. Tessl local flow: run internal/local Tessl staging and rubric checks;
   iterate until the rubric and scenario package are good enough for external
   workspace scoring.
5. Tessl external flow: project the foundry package into a durable private
   Tessl registry/workspace package, run the private Tessl Workspace eval, and
   score the preserved `tessl eval view --json` artifact before claiming
   handoff readiness.

## Lane Matrix

| Lane                      | Proves                                                                                                                                                                | Required command shape                                                                                                                                                                                                                                                                                                                                                                                                                                  | Authority boundary                                                                                                                                                                                                                                                                                              | Blocks that do not prove failure                                                                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SDK mechanical validation | Skill package shape and static SDK readiness before runtime model proof.                                                                                              | `./bin/ask skills package verify <skill-path> --json --robot`; `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`; `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`; `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`; `./bin/ask skills audit <skill-path>/SKILL.md --level strict --json --robot`.                                                                     | Repository schemas, package validators, static eval metadata, local files only.                                                                                                                                                                                                                                 | Live model quota, Tessl workspace quota, cloud auth, or model subscription failures.                                                                                        |
| oss-local flow            | Local OSS model behavior through the Codex control plane.                                                                                                             | `codex exec --profile oss-local` or an SDK command whose receipt shows `codex_exec_invoked=true` and `codex_profile=oss-local`.                                                                                                                                                                                                                                                                                                                         | Codex `oss-local.config.toml`; local profile sandbox and configured local model runtime.                                                                                                                                                                                                                        | Missing local model, Ollama local runtime unavailable, profile config missing, local sandbox denial, unsupported generic ChatGPT-account model.                             |
| oss-cloud flow            | Cloud OSS confirmation through the Codex control plane.                                                                                                               | `codex exec --profile oss-cloud` or an SDK command whose receipt shows `codex_exec_invoked=true` and `codex_profile=oss-cloud`.                                                                                                                                                                                                                                                                                                                         | Codex `oss-cloud.config.toml`; approved cloud auth stream such as the operator-approved env file or 1Password wrapper; cloud model access.                                                                                                                                                                      | Subscription missing, cloud provider 403, approved env stream unavailable, profile config missing.                                                                          |
| Tessl local flow          | Local Tessl package shape, scenario staging, native Tessl CLI compatibility, package archive creation, and temp `file:` install behavior without public distribution. | `./bin/ask evals run <skill-path> --mode smoke or release --json --robot` for the local ladder; `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --dry-run --json --robot` for scenario-generation staging; `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --preview\|--execute --json --robot` for Tessl plugin lint, pack, temp `file:` install, and optional review receipts. | Native installed `tessl` CLI, stable `/tmp/ask-tessl-*` staged input, temp install workspace under `/tmp/ask-tessl-local-install`, no `npx`, no publish, no registry upload, no live repo source install.                                                                                                       | Missing project link, local Tessl CLI auth blocker, staged package shape failure, generated scenario draft needing review, pack command failure, temp file-install failure. |
| Tessl external flow       | Durable private Tessl projection plus private Workspace scoring evidence.                                                                                             | `./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot`; use `--tessl-live-dry-run` before live service calls when proving shape.                                                                                                                                                                                                                                                                          | Foundry package id in `agent-skills`; private Tessl package id `<workspace>/<package-name>`; project repair/link/create before eval; preserved `tessl eval view --json` artifact; score receipt through `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot`. | Quota, workspace token/session failure, project link setup, live score below threshold, non-discriminative baseline, missing final view artifact.                           |

## Non-Substitution Rules

- Do not skip SDK mechanical validation before runtime proof.
- Do not use generic `./bin/ask evals run --runner codex --model <model>` as
  oss-local proof unless the resulting receipt proves `codex_profile=oss-local`.
- Do not treat a ChatGPT-account model error as an oss-local blocker. The
  oss-local lane is the Codex `oss-local` profile lane.
- Do not treat an oss-local pass as oss-cloud proof. Cloud confirmation has its
  own auth, model, subscription, and profile boundary.
- Do not treat local Tessl package staging as external Tessl scoring proof.
- Do not treat external Tessl command completion as readiness until the final
  `tessl eval view --json` artifact is preserved and scored by the SDK Tessl
  score receipt.
- Do not treat a one-off Tessl upload as external proof unless the receipt also
  records the foundry package id, private Tessl package id, project link state,
  and staged package digest.
- Do not collapse local proof, runtime proof, hosted CI, review state, Tessl
  score state, and merge readiness into one status line.

## Required Reporting Shape

For each lane, report:

- `lane`: one of `sdk-mechanical`, `oss-local`, `oss-cloud`, `tessl-local`, or
  `tessl-external`.
- `command`: the exact command attempted.
- `authority_boundary`: profile, workspace, or staged package boundary.
- `foundry_package_id`: the canonical package identity in `agent-skills`.
- `tessl_private_package_id`: the private Tessl package identity, usually
  `<workspace>/<package-name>`.
- `status`: `pass`, `fail`, or `blocked`.
- `evidence`: receipt path, artifact path, command output summary, or blocker.
- `does_not_prove`: adjacent proof lanes that remain unproven.

## Recovery Rules

- If SDK mechanical validation blocks, fix the package, scenario, scorer,
  calibration, docs projection, or strict-audit issue before invoking model
  lanes.
- If oss-local blocks, inspect the Codex `oss-local` profile and local model
  runtime before switching lanes.
- If oss-cloud blocks on subscription or provider access, leave oss-cloud
  blocked and continue only with lanes that do not claim cloud confirmation.
- If Tessl local blocks, preserve the `/tmp/ask-tessl-*` staged evidence and
  fix package shape, project-link setup, plugin pack output, or temp file-install
  setup before live scoring.
- If Tessl external blocks, preserve the live staged package, private package
  identity, project-link state, and final view artifact when available; then
  classify quota, auth, project-link, score, or non-discriminative-baseline
  separately.

## Tessl External Identity Contract

The Tessl external lane is a projection from the foundry into a durable private
Tessl package:

- `agent-skills` is the foundry source of truth.
- `skills-sdk-lab` is the intended initial Tessl workspace for creation,
  scenario generation, internal review, and eval iteration before registry
  promotion.
- `jscraik-private` is the intended private Tessl registry workspace for
  promoted Skills SDK packages before public release.
- `jscraik` is the intended public-facing Tessl registry workspace for Skills
  SDK public skills after they pass private promotion.
- `foundry_package_id` identifies the canonical skill or plugin package in the
  repo.
- `tessl_private_package_id` identifies the private Tessl registry/workspace
  package, normally `<workspace>/<package-name>`.
- The CLI must repair, link, or create the Tessl project for that private
  package identity before running external evals.
- The receipt must record the staged package digest and the private package id
  so a future run can prove which foundry source produced which Tessl package.
- The private Tessl package can be persistent; the staged `/tmp/ask-tessl-*`
  copy remains the reproducible upload/eval evidence for the current run.

## First-Time Tessl Workspace Setup

Use the dedicated Tessl workspace checkout, not the live foundry repo, when
installing Tessl helper packages:

```bash
cd /Users/jamiecraik/Documents/tessl
tessl install tessl-labs/tile-creator sharaf/migrate-to-tessl --agent codex --agent agents
```

Do not use `pnpx tessl i ...` for SDK runtime lanes. `pnpx` is an ephemeral
package runner, and helper installation is a workspace setup mutation. The
native `tessl install` command must update the dedicated workspace
`tessl.json` with concrete plugin versions before those helper skills are
treated as available.

The helper split is:

- `tessl-labs/tile-creator`: use for first-time private tile/package shape,
  `plugin.json`, package docs, rules, skills, lint, and eval-scenario setup.
  Treat older `tile.json` examples as legacy naming unless the installed
  helper explicitly requires them.
- `sharaf/migrate-to-tessl`: use for migration and publish-oriented review
  loops, but keep its registry publish steps behind an explicit publish lane.

## Format Projection Rules

The Skills SDK must not publish an OpenAI/Codex plugin directory directly as a
Tessl package. It must project a controlled Tessl package surface from the
foundry source and record what was included, translated, omitted, or blocked.

OpenAI/Codex package surfaces:

- `skills/**`: include as agent skill content after SDK validation.
- `references/**`: include only when safe, repo-local, non-symlinked, and
  referenced by the skill or package contract.
- `assets/**`: include only when referenced and safe.
- `agents/**`: preserve as OpenAI metadata; do not treat it as Tessl runtime
  input unless a Tessl mapping exists.
- `.codex-plugin/plugin.json`: translate selected identity, summary, display,
  and capability metadata into a Tessl `plugin.json`; do not publish this file
  directly as the Tessl manifest.
- `plugins/marketplace.json`: preserve as OpenAI marketplace/index metadata.
  There is no separate required OpenAI plugin marketplace JSON inside each
  plugin package in the current repo format; marketplace-facing metadata lives
  in `.codex-plugin/plugin.json` and the repo-level plugin index.
- `hooks/**`: omit or block unless the Tessl projection explicitly models and
  validates hook authority.
- `mcp/**` and `apps/**`: omit or block unless the Tessl projection explicitly
  models the server/app contract, auth boundary, and runtime authority.

Tessl package surfaces:

- `plugin.json`: required Tessl registry manifest with
  `workspace/package-name`, semantic version, summary, privacy, and the mapped
  skills/docs/rules entries.
- `README.md`: include for private and public registry promotion. Tessl docs
  treat it as Registry UI presentation and not as agent context; agent-facing
  context must live in skills, docs, rules, references, or generated scenarios.
- `skills/**`: include validated `SKILL.md` files and their declared safe
  support files.
- `references/**`: include safe knowledge capsules, docs, and evidence needed
  by the skill; reject raw local sources, absolute paths, symlinks, secrets,
  and unmodeled generated caches.
- `assets/**`: include only referenced safe files.
- `evals/**` or `scenarios/**`: generate from SDK eval metadata for local and
  external Tessl eval lanes.
- `tessl.json`: use as the workspace/project dependency manifest in the
  dedicated Tessl checkout or staged eval payload. Do not mutate the foundry
  repo root with Tessl workspace state unless a separate repo policy decision
  requires it.

The projection result must show this mapping in receipt evidence before any
private or public registry claim is made.

For a first private Tessl package projection:

1. Derive `foundry_package_id`, source commit, and staged package digest from
   the canonical `agent-skills` package.
2. Stage a clean private Tessl package under `/tmp/ask-tessl-*`; include
   `plugin.json`, `README.md` for registry presentation, skill content,
   references, and scenarios generated from SDK metadata.
3. Run local shape and install checks through
   `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --preview --json --robot`,
   then `--execute` when the operator wants the local native Tessl commands to
   run. This receipt stages the package, runs `tessl plugin lint`, runs
   `tessl plugin pack --output <temp-file>.tgz`, installs the staged package
   with `tessl install file:<staged-path> --agent codex --yes --strict` inside
   a temporary project workspace, and may run `tessl review run` only when
   `--include-review` is explicitly supplied.
4. Diagnose project identity from inside the staged package with
   `tessl project repair --json`.
5. If the project is unlinked, require an explicit setup action:
   `tessl project repair --relink --workspace <workspace> --project <name> --yes`
   for an existing private package, or
   `tessl project create <name> --workspace <workspace>` for a new private
   package.
6. Keep private registry publish/update separate from eval execution.
   Do not run `tessl plugin publish`, `tessl tile publish`, or related
   registry upload commands in runtime-lane proof unless the hard-boundary
   policy is explicitly revised and approved. Use staged-package lint,
   project-link evidence, and scored `tessl eval view --json` artifacts for
   readiness evidence.
7. Run the external eval only after the project identity is linked, then
   preserve `tessl eval view --json <run-id>` and score it through the SDK
   Tessl receipt lane.

The setup result must distinguish:

- workspace helper availability: installed helper plugins in
  `/Users/jamiecraik/Documents/tessl/tessl.json`;
- workspace selection: `skills-sdk-lab` for Skills SDK skill creation and eval,
  `jscraik-private` for private registry promotion, or `jscraik` for public
  registry publication;
- private package identity: `tessl_private_package_id`;
- project link state: linked, relinked, created, or blocked;
- publish readiness: not claimed from runtime-lane proof; registry publish or
  upload remains blocked unless a separate approved release lane provides
  evidence;
- eval readiness: final Tessl view artifact scored by the SDK receipt.
