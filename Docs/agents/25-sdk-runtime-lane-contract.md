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

Use the
[Skills SDK Gold Standard Rubric](/Docs/reference/skills-sdk-gold-standard-rubric.md)
as the top-level scoring standard before Tessl live eval or registry release
claims. Numeric scores from Plugin Eval or Tessl do not replace the rubric's
automatic failure conditions, lane separation, or command-evidence requirements.

## Promotion Pipeline

1. SDK mechanical validation: prove the package shape, gold-standard rubric
   floor, scenario metadata, scorer metadata, scorer calibration, docs
   projection, and strict audit.
2. oss-local flow: run the skill scenario proof or A/B judge through
   `codex exec --profile oss-local` in the read-only Codex profile sandbox;
   iterate until the sandboxed local OSS lane is valid, then move to the next
   model lane.
3. oss-cloud flow: run the same proof through the Configs-owned
   `run-auth-backed.sh → run-codex-exec.sh` chain for `oss-cloud` in the
   read-only, strict, ephemeral Codex profile sandbox;
   iterate until the sandboxed cloud OSS lane is valid, then move to Tessl.
4. Tessl local flow: run internal/local Tessl staging and rubric checks;
   iterate until the rubric and scenario package are good enough for external
   workspace scoring.
5. Tessl external flow: project the foundry package into a durable private
   Tessl registry/workspace package, run the private Tessl Workspace eval, and
   score the preserved `tessl eval view --json` artifact before claiming
   handoff readiness.

### Disposable SDK judge workspaces

An SDK A/B judge may execute from a fresh workspace under
`/private/tmp/ask-sdk-ab-variant-workspaces/` rather than a checked-out Git
directory. The command must keep that workspace path contained and
candidate-bound, then pass `--skip-git-repo-check` to the strict Configs
executor. This flag only permits Codex startup in that SDK-created disposable
workspace; it does not widen the filesystem root, change the read-only
sandbox, or permit a dirty/current checkout. Keep `--output-last-message`
repo-relative, copy the resulting receipt into the evidence root, and retain
the exact command argv in the judge receipt.

## Lane Matrix

| Lane                      | Proves                                                                                                                                                                | Required command shape                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Authority boundary                                                                                                                                                                                                                                                                                                        | Blocks that do not prove failure                                                                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SDK mechanical validation | Skill package shape and static SDK readiness before runtime model proof.                                                                                              | `./bin/ask skills package verify <skill-path> --json --robot`; `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`; `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`; `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`; `./bin/ask skills audit <skill-path>/SKILL.md --level strict --json --robot`.                                                                                                                                                                                                                                                                                                                                                                                                                           | Repository schemas, package validators, static eval metadata, local files only.                                                                                                                                                                                                                                           | Live model quota, Tessl workspace quota, cloud auth, or model subscription failures.                                                                                        |
| oss-local flow            | Local OSS model behavior through the Codex control plane.                                                                                                             | `codex exec --profile oss-local` or an SDK command whose receipt shows `codex_exec_invoked=true` and `codex_profile=oss-local`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Codex `oss-local.config.toml`; local profile sandbox and configured local model runtime.                                                                                                                                                                                                                                  | Missing local model, Ollama local runtime unavailable, profile config missing, local sandbox denial, unsupported generic ChatGPT-account model.                             |
| oss-cloud flow            | Cloud OSS confirmation through the Codex control plane.                                                                                                               | `python3 Infrastructure/scripts/validation-and-linting/run_oss_cloud_smoke.py --json`, which validates the projected profile and 1Password Desktop FIFO before it invokes `bash run-auth-backed.sh --env-file ~/.codex/.env --require-env OLLAMA_API_KEY -- bash run-codex-exec.sh --profile oss-cloud --model deepseek-v4-flash:cloud --strict-config --sandbox read-only --ephemeral`; or an SDK receipt whose `execution_argv` proves that same wrapper chain and `codex_profile=oss-cloud`.                                                                                                                                                                                                                                                                                                                                                                         | Codex `oss-cloud.config.toml`; Desktop-owned `~/.codex/.env` FIFO; reviewed Configs wrappers; cloud model access.                                                                                                                                                                                                          | Subscription missing, cloud provider 403, unavailable FIFO writer, wrapper/profile config missing.                                                                          |
| Tessl local flow          | Local Tessl package shape, scenario staging, native Tessl CLI compatibility, package archive creation, and temp `file:` install behavior without public distribution. | `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --execute --json --robot` for the executed Tessl plugin lint, pack, temp `file:` install, and optional review receipt. Use `--preview` only to plan the lane before producing readiness evidence. Preparatory commands are `./bin/ask evals run <skill-path> --mode smoke or release --json --robot` and `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --json --robot`; scenario preparation stages only by default and requires `--execute` for a temporary Tessl install. They do not satisfy Tessl local proof readiness by themselves.                                                                                                                                           | Native installed `tessl` CLI, stable `/tmp/ask-tessl-*` staged input, temp install workspace under `/tmp/ask-tessl-local-install`, no `npx`, no publish, no registry upload, no live repo source install.                                                                                                                 | Missing project link, local Tessl CLI auth blocker, staged package shape failure, generated scenario draft needing review, pack command failure, temp file-install failure. |
| Tessl external flow       | Durable private Tessl projection plus private Workspace scoring evidence.                                                                                             | First run the explicit project-setup lane `./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace <workspace> --execute --json --robot` with operator authority; it records a candidate-bound project-link receipt. Then use `./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace <workspace> --json --robot`; use `--tessl-live-dry-run` before live service calls when proving shape. The dry-run admission requires current mechanical, security, scenario/scorer, deterministic, `oss-local`, `oss-cloud`, and Tessl-local proof receipts. A non-dry live run additionally requires the completed candidate-bound handoff receipt, the project-link receipt, and the recorded dry-run lane. The live evaluator never repairs, relinks, updates, or creates a project. | Foundry package id from the current canonical owner record; private Tessl package id `<workspace>/<package-name>`; candidate-bound project-link receipt before eval; preserved `tessl eval view --json` artifact; score receipt through `./bin/ask sdk eval tessl-score --view-json <view-json> --skill <skill-path> --preview --json --robot`. | Quota, workspace token/session failure, stale project-link receipt, live score below threshold, non-discriminative baseline, missing final view artifact.                   |

In this table, “current canonical owner record” means the explicit owner
decision for the bounded package lane. It is not inferred from an
`agent-skills` checkout path, a Foundry copy, a Tessl project, or a home-runtime
link.

## Non-Substitution Rules

- Do not skip SDK mechanical validation before runtime proof.
- Do not use generic `./bin/ask evals run --runner codex --model <model>` as
  oss-local proof unless the resulting receipt proves `codex_exec_invoked=true`
  and `codex_profile=oss-local`.
- Do not use `./bin/ask evals run --runner codex` as oss-cloud proof unless the
  resulting receipt proves `codex_exec_invoked=true` and
  `codex_profile=oss-cloud`.
- `codex exec --profile fast` or SDK receipts in the `codex-fast-smoke` lane
  are allowed for quick smoke tasks and checks only; they do not satisfy
  oss-local or oss-cloud promotion evidence and cannot substitute for oss-local
  or oss-cloud promotion evidence.
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
- `foundry_package_id`: the canonical package identity from its explicit owner
  decision, rather than an assumed repository path.
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
- Before a live oss-cloud retry, run
  `python3 Infrastructure/scripts/validation-and-linting/run_oss_cloud_smoke.py --json`.
  The runner accepts only the Desktop-owned FIFO at `~/.codex/.env`, invokes
  the reviewed Configs chain with `oss-cloud` and `deepseek-v4-flash:cloud`,
  and records `auth_source=1password_desktop_fifo` without reading the FIFO.
  The marker child runs from a temporary context-minimal `CODEX_HOME` containing
  only the admitted profile and smoke config, so workstation-wide skills and
  MCPs cannot consume the smoke budget or become cloud evidence.
  A plaintext, symlinked, malformed, unavailable, or unwritten stream is a
  local preflight blocker: it must not start the provider or be reported as a
  provider failure. Use one fresh wrapper invocation for each credentialed
  stage; never reuse a FIFO descriptor across catalog, A, B, and judge.
- Before an A/B plan admits the `oss-cloud` lane, its catalog preflight must
  invoke the official `GET https://ollama.com/api/tags` list-models surface
  through `bash run-auth-backed.sh --env-file ~/.codex/.env --require-env
  OLLAMA_API_KEY -- ...`. The env source is an opaque operator stream: the
  parent process must not open, read, hash, copy, or include its contents in
  commands, exceptions, logs, receipts, or test fixtures. Only the probe child
  receives `OLLAMA_API_KEY`; it sends the credential to the official endpoint
  and emits a redacted result containing the HTTP classification, catalog
  digest, and exact selected-model match. Missing Configs auth, network or timeout denial, HTTP failure, malformed catalog,
  missing model, and duplicate exact matches are typed blockers. There is no
  direct unauthenticated fallback. This read-only catalog request proves only
  profile/catalog admission: it performs no generation, does not invoke Codex,
  and does not prove A/B, judge, provider-generation, or release behavior.
  The parent accepts catalog-probe transport only when the Configs wrapper child returns the
  exact built-in integer exit code `0` for a pass or `2` for a validated typed
  blocker, stderr is empty, and stdout is exactly one JSON object matching the
  closed probe contract for that result class. Boolean, float, string, null,
  integer-subclass, negative, and exits outside `0` or `2` block before stdout
  parsing; invalid transport types are retained only as redacted exit-class
  evidence. Missing or extra fields, duplicate keys, trailing JSON, non-finite
  numbers, wrong primitive types, and contradictions between the result class
  and its network, HTTP, digest, match, secret, generation, provider, or Codex
  fields block admission. A nonzero child exit cannot self-claim a pass.
  Before any comparison or parsing, the parent copies a closed subprocess
  envelope: `returncode` must be an exact built-in integer, and `stdout` and
  `stderr` must be exact built-in strings. Missing or exception-raising
  attributes, subclasses, bytes-like values, coercible objects, mappings,
  tuples, oversized stdout, and NUL or control-framed stdout are typed,
  redacted blockers. Evidence records only fixed transport classifications;
  it never records malformed values, representations, exception text, child
  stdout or stderr, or the opaque env-stream path. Each of the three attribute
  reads contains every `BaseException` raised by that hostile property access,
  including process-control subclasses, but that containment does not extend
  to the runner invocation, JSON parsing, tests, or unrelated caller code.
- A planned or completed A/B v1 runtime gate requires `status=pass` for its
  profile configuration, model catalog, runtime, and catalog facts. The local
  lane keeps its explicit non-secret `auth.status=not_applicable`
  representation; the cloud lane requires `auth.status=pass` through the
  approved opaque-auth boundary. A blocked or not-run receipt remains readable
  with typed failed facts and blockers, but those facts cannot authorize a
  plan, completed run, judge preview, or judge score.
- If Tessl local blocks, preserve the `/tmp/ask-tessl-*` staged evidence and
  fix package shape, project-link setup, plugin pack output, or temp file-install
  setup before live scoring.
- If Tessl external blocks, preserve the live staged package, private package
  identity, project-link state, and final view artifact when available; then
  classify quota, auth, project-link, score, or non-discriminative-baseline
  separately.

## Tessl External Identity Contract

The Tessl external lane is a projection from a selected canonical package into
a durable private Tessl package:

- `/Users/jamiecraik/dev/skills-foundry` retains source-only packages,
  provenance, and licences outside active authoring.
- `agent-skills` implements the Skills SDK and may hold the selected active
  candidate for the bounded lifecycle task; its copy does not change source
  ownership without an explicit authority decision.
- `jscraik` is the single intended Tessl workspace for Skills SDK project
  creation, scenario generation, internal review, eval iteration, private
  registry retention, and later public registry publication decisions.
- Tessl workspace and Tessl project are different identifiers. `jscraik` is the
  workspace; each standalone skill or plugin-owned package is generated, linked,
  repaired, and evaluated as its own Tessl project under that workspace.
- Standalone skill projects use the skill slug, for example
  `jscraik/technical-writer`. Plugin-owned skills use the plugin slug, for
  example `jscraik/skill-factory`, so project eval history stays attached to
  the repository/package identity Tessl shows in the Projects list.
- Every staged Tessl plugin manifest must start with `private: true`. Public
  visibility requires a separate explicit publish lane and must not be inferred
  from project linking, eval success, or workspace selection.
- `foundry_package_id` identifies the canonical skill or plugin package in the
  source location named by its explicit owner decision.
- `tessl_private_package_id` identifies the private Tessl registry/workspace
  package and must match the project marker, normally
  `<workspace>/<project-slug>`.
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
  `.tessl-plugin/plugin.json`, package docs, rules, skills, lint, and
  eval-scenario setup.
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
- `agents/**`: preserve as OpenAI metadata. For skill package projection,
  copy required OpenAI/Codex skill metadata such as `agents/openai.yaml` into
  `skills/<skill-name>/agents/**`; do not treat it as a Tessl runtime rule
  unless a Tessl mapping exists.
- `.codex-plugin/plugin.json`: translate selected identity, summary, display,
  and capability metadata into a Tessl `.tessl-plugin/plugin.json`; do not
  publish this file directly as the Tessl manifest.
- `plugins/marketplace.json`: preserve as OpenAI marketplace/index metadata.
  There is no separate required OpenAI plugin marketplace JSON inside each
  plugin package in the current repo format; marketplace-facing metadata lives
  in `.codex-plugin/plugin.json` and the repo-level plugin index.
- `hooks/**`: omit or block unless the Tessl projection explicitly models and
  validates hook authority.
- `mcp/**` and `apps/**`: omit or block unless the Tessl projection explicitly
  models the server/app contract, auth boundary, and runtime authority.

Tessl package surfaces:

- `.tessl-plugin/plugin.json`: required Tessl registry manifest with
  `workspace/package-name`, semantic version, description, privacy, optional
  `skills`, optional `rules`, and optional `mcpServers` entries. For Skills SDK
  skill projections, `skills` must point at the staged skill tree and
  `rules` must not be used as a replacement for skill references.
- `README.md`: include for private and public registry promotion. Tessl docs
  treat it as Registry UI presentation and not as agent context; agent-facing
  context must live in skills, references, scripts, assets, MCP declarations,
  or generated scenarios. The README must carry a GitHub Badge section for the
  Tessl registry badge when public, name `tessl skill review --optimize` as the
  score-improvement path, and name `tessl review run` as the CI score gate.
- `skills/<skill-name>/SKILL.md`: include validated skill entrypoints in the
  Tessl skill convention. This is the staged projection of the OpenAI/Codex
  skill source, not a replacement source of truth.
- `skills/<skill-name>/references/**`: include safe knowledge capsules, docs,
  and evidence needed by the skill; reject raw local sources, absolute paths,
  symlinks, secrets, and unmodeled generated caches. Do not translate skill
  references into Tessl `rules/`; Tessl's own skill packages use
  `references/` for skill support context.
- `skills/<skill-name>/scripts/**`: include only safe scripts that the skill
  explicitly references and that pass package safety checks.
- `skills/<skill-name>/assets/**`: include only referenced safe files.
- `.mcp.json`: include only when the plugin bundles MCP servers. Its top-level
  `mcpServers` map must declare `stdio` servers with `command` or `http`
  servers with an `http`/`https` URL. This plugin-bundled file is distinct from
  Tessl's consuming-project `.mcp.json`.
- `evals/<case-id>/task.md` and `evals/<case-id>/criteria.json`: generate from
  SDK eval metadata for Tessl package scoring. `scenario.json` is optional for
  fixtures, includes, or setup scripts.
- `.tesslignore`: include at the staged plugin root. It must exclude
  project-local agent context and generated/local evidence such as
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.harness/`, `.agents/`, `.codex/`,
  `.tessl/`, and `dist/`, but it must not ignore manifest entrypoints such as
  `skills`, `rules`, or `docs`.
- `tessl.json`: use as the workspace/project dependency manifest in the
  dedicated Tessl checkout or staged eval payload. Its `name` must be the exact
  Tessl project identity `<workspace>/<project-slug>`, not merely any package
  under the workspace. Do not mutate the foundry repo root with Tessl workspace
  state unless a separate repo policy decision requires it.
- `AGENTS.md`: treat as consuming-workspace or repository instruction context.
  It helps an agent understand how to operate in the checkout, but it is not
  skill reference material or a Tessl runtime rule. Exclude it from staged Tessl
  plugin packages with `.tesslignore` unless a future explicit projection rule
  models agent-instruction files as package content.

The projection result must show this mapping in receipt evidence and pass the
Tessl projection-shape validator before any private or public registry claim is
made.

For a first private Tessl package projection:

1. Derive `foundry_package_id`, source identity, and staged package digest from
   the selected canonical package and record its owner location.
2. Stage a clean private Tessl package under `/tmp/ask-tessl-*`; include
   `.tessl-plugin/plugin.json`, `README.md` for registry presentation, skill
   content, references, and scenarios generated from SDK metadata. The staged
   manifest must use workspace `jscraik` and `private: true`.
3. Run local shape and install checks through
   `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace <workspace> --preview --json --robot`,
   then `--execute` when the operator wants the local native Tessl commands to
   run. This receipt stages the package, runs `tessl plugin lint`, runs
   `tessl plugin pack --output <temp-file>.tgz`, installs the staged package
   with `tessl install file:<staged-path> --agent codex --yes --strict` inside
   a temporary project workspace, and may run `tessl review run` only when
   `--include-review` is explicitly supplied.
4. Diagnose or repair project identity only through the explicit project-setup
   wrapper: `./bin/ask evals prepare-tessl-scenarios <skill-path>
--tessl-workspace <workspace> --execute --json --robot`.
5. Preserve its candidate-bound project-link receipt. The later live evaluator
   treats a missing, stale, or mismatched receipt as a blocker and performs no
   project mutation itself.
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
- workspace selection: `jscraik` for every Skills SDK Tessl project and
  package lane;
- manifest visibility: staged plugin manifests start `private: true`; public
  publication is a separate approved lane;
- private package identity: `tessl_private_package_id`;
- project link state: linked, relinked, created, or blocked;
- publish readiness: not claimed from runtime-lane proof; registry publish or
  upload remains blocked unless a separate approved release lane provides
  evidence;
- eval readiness: final Tessl view artifact scored by the SDK receipt.
