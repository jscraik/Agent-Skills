---
schema_version: 1
artifact_id: phoenix-oss-eval-observability-workflow-2026-07-08
artifact_type: research-workflow
canonical_slug: phoenix-oss-eval-observability-workflow
title: Phoenix OSS Eval Observability Workflow
harness_stage: research
date: 2026-07-08
status: active
---

# Phoenix OSS Eval Observability Workflow

## BLUF

Use Phoenix open source as the observer layer for local and cloud OSS eval
activity, but keep Agent Skills Kit receipts as the promotion source of truth.
Phoenix should make traces, spans, experiments, datasets, and annotations easy
to inspect; it must not replace the existing lane gates for SDK mechanical
validation, `oss-local`, `oss-cloud`, Tessl local proof, Tessl external
scoring, or handoff readiness.

Current local setup status:

- Docker CLI is available on the operator workstation.
- Docker daemon is running.
- Phoenix is running as container `evals-phoenix-phoenix-1` from
  `arizephoenix/phoenix:latest`.
- Phoenix UI responds on `http://localhost:6006` with server version
  `17.12.0`.
- Ports `6006` and `4317` are bound by Docker to the Phoenix container.
- Phoenix uses Docker volume `evals-phoenix_phoenix-data` mounted at
  `/mnt/data`; `PHOENIX_ALLOWED_SANDBOX_PROVIDERS=NONE`.
- The Phoenix docs index was fetched to a temporary file for current page
  discovery.
- The current container's original Compose file no longer exists, so the
  repository-owned service definition is now
  `Infrastructure/config/observability/compose.phoenix.yaml`.

## Product Decision

The attached Arize docs are Phoenix open-source docs, not Arize AX docs. Use:

- Phoenix server and UI for local trace inspection.
- `arize-phoenix-otel` and OpenInference instrumentation when Python code makes
  model calls directly.
- Phoenix Client datasets and experiments only after a repo receipt has a stable
  case/output shape worth mirroring.
- Phoenix MCP or CLI as optional inspection aids, not as mutation authority for
  Agent Skills Kit promotion.

Do not add Arize AX dependencies, AX auth variables, or cloud-only assumptions
for this lane unless the operator explicitly asks for AX.

## Source Findings

| Source | Finding | Workflow impact |
| --- | --- | --- |
| Phoenix configuration docs | Phoenix exposes UI and OTLP HTTP collector on `6006`; OTLP gRPC collector on `4317`; `PHOENIX_WORKING_DIR` and `PHOENIX_SQL_DATABASE_URL` control durable storage. | Local setup should start Phoenix on `6006` and `4317` with a persistent working directory or SQLite database before recording any trace evidence. |
| Phoenix Docker docs | A local container can run with `docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest`; compose examples support SQLite or Postgres persistence. | First workstation proof is a sidecar Phoenix service. Production-style persistence can wait until the local workflow proves useful. |
| Phoenix integrations docs | Phoenix supports coding-agent workflows through CLI, docs MCP, direct Phoenix MCP, and skills; it also has tracing integrations for OpenAI Agents SDK, OpenAI SDKs, MCP, TypeScript, and Python frameworks. | Use docs MCP for lookup and direct Phoenix MCP only after a Phoenix instance exists and credentials are intentionally scoped. |
| Phoenix Python SDK docs | `arize-phoenix-client`, `arize-phoenix-otel`, `arize-phoenix-evals`, and OpenInference are modular; `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_BASE_URL`, `PHOENIX_API_KEY`, and `PHOENIX_PROJECT_NAME` are the main environment knobs. | Instrument Python wrappers with OTLP and project names; do not force eval logic to depend on Phoenix if local receipts already prove the gate. |
| Phoenix OpenAI Agents tracing docs | `phoenix.otel.register(project_name=..., auto_instrument=True)` connects OpenAI Agents SDK traces to Phoenix. | Useful for future agent-runner wrappers; not directly sufficient for `codex exec --profile oss-local\|oss-cloud` unless the invoked process emits OTLP spans. |
| Skills SDK runtime lane contract | `oss-local` and `oss-cloud` proof must be `codex exec --profile <lane>` or SDK receipts proving `codex_exec_invoked=true` and the expected `codex_profile`. | Phoenix traces are supporting observability. Promotion still requires repo receipts with the exact profile proof fields. |
| Prior OSS-profile memory | The durable OSS judge route was changed away from direct provider calls and toward `codex exec --profile oss-local\|oss-cloud`, with receipts proving `judge_command_argv`, `codex_profile`, and `codex_exec_invoked`. | Preserve the profile route. Do not reintroduce direct Ollama or cloud-provider shortcuts just to get prettier traces. |

## Workflow Design

### Lane 0: Phoenix Local Service

Goal: make a local collector and UI available before modifying eval runners.

Command shape:

```bash
docker run --rm \
  --name agent-skills-phoenix \
  -p 6006:6006 \
  -p 4317:4317 \
  -e PHOENIX_WORKING_DIR=/mnt/data \
  -v phoenix_data:/mnt/data \
  arizephoenix/phoenix:latest
```

Expected evidence:

- `http://localhost:6006` loads.
- `curl -fsS http://localhost:6006` returns a page response.
- No trace or eval claim is made yet.

Previous blocker:

- `docker info --format "{{.ServerVersion}}"` returned
  `Cannot connect to the Docker daemon`.

Current service proof:

- `docker info --format "{{.ServerVersion}}"` returned `29.5.3`.
- `docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}"`
  showed `evals-phoenix-phoenix-1` using `arizephoenix/phoenix:latest` with
  `127.0.0.1:6006->6006/tcp` and `127.0.0.1:4317->4317/tcp`.
- `curl -fsS -I http://localhost:6006` returned `HTTP/1.1 200 OK` and
  `x-phoenix-server-version: 17.12.0`.
- `docker inspect evals-phoenix-phoenix-1 --format "{{json .Config.Env}}"`
  showed `PHOENIX_WORKING_DIR=/mnt/data` and
  `PHOENIX_ALLOWED_SANDBOX_PROVIDERS=NONE`.

### Lane 1: Receipt-First Eval Mirror

Goal: make existing Agent Skills Kit eval outputs visible in Phoenix without
changing promotion authority.

Source receipts to mirror:

- `./bin/ask skills package verify <skill-path> --json --robot`
- `./bin/ask skills audit <skill-path> --level strict --json --robot`
- `./bin/ask sdk eval scenario-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-quality <skill-path> --preview --json --robot`
- `./bin/ask sdk eval scorer-calibration <skill-path> --preview --json --robot`
- `./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-local --json --robot`
- `./bin/ask sdk eval run <skill-path> --runner internal --mode smoke --codex-profile oss-cloud --json --robot`
- `./bin/ask sdk eval tessl-local-proof --skill <skill-path> --workspace jscraik --execute --json --robot`
- `./bin/ask sdk eval handoff-readiness --skill <skill-path> --preview --json --robot`

Phoenix mapping:

| Repo receipt field | Phoenix concept | Notes |
| --- | --- | --- |
| `trace_id` | trace/span attribute | Preserve exact repo trace id for round-trip lookup. |
| `skill_path` / package id | project/session metadata | Use `agent-skills/<skill-slug>` project naming. |
| `mode`, `runner`, `codex_profile` | span attributes | Required for separating local and cloud OSS truth. |
| `cases[]` | experiment examples or span events | Mirror only stable case-level outputs. |
| `status`, `blocker_class` | evaluation annotation | Keep `blocked` distinct from `fail`. |
| `eval_closeout_path` / receipt path | span attribute | Phoenix points back to repo-owned evidence. |

### Durable workstation service

For a Mac Studio with an always-attached external SSD, keep the Compose contract
in the repository and put only Phoenix's mutable SQLite working directory on
the SSD. The Compose file requires the operator to name the mounted data root,
so it cannot silently fall back to an internal-disk directory:

```bash
export ASK_PHOENIX_DATA_DIR=/Volumes/ExternalSSD/jamiecraik-codex-storage/phoenix/data
test -d /Volumes/ExternalSSD
mkdir -p "$ASK_PHOENIX_DATA_DIR"
docker compose -f Infrastructure/config/observability/compose.phoenix.yaml config --quiet
docker compose -f Infrastructure/config/observability/compose.phoenix.yaml up -d
./bin/ask sdk observability phoenix-status --base-url http://localhost:6006 --json --robot
```

The service is pinned to the observed Phoenix `17.12.0` image digest, binds both ports to localhost, and
disables external UI resources and Phoenix sandbox providers. If the SSD is not
mounted, the required environment variable or bind mount must block startup;
do not create the same path on the internal disk as a fallback.

To migrate an existing Docker volume, stop the old container, copy while the
SQLite database is quiescent, and keep the old volume intact until the new
service reports the same trace count. The current source volume is
`evals-phoenix_phoenix-data`; no migration command may remove it. A suitable
copy shape is:

```bash
docker stop evals-phoenix-phoenix-1
docker run --rm \
  -v evals-phoenix_phoenix-data:/from:ro \
  -v "$ASK_PHOENIX_DATA_DIR":/to \
  alpine:3.20 sh -c 'cp -a /from/. /to/'
docker compose -f Infrastructure/config/observability/compose.phoenix.yaml up -d
./bin/ask sdk observability phoenix-status --base-url http://localhost:6006 --json --robot
```

Do not remove the stopped container or source volume during this verification
window. If the SSD is ever disconnected, stop Phoenix before unmounting it to
avoid SQLite corruption.

### Lane 2: Instrumented OSS Runner Spans

Goal: emit one Phoenix trace around each internal eval run while preserving the
existing `codex exec --profile` invocation.

Trace shape:

- root span: `skills-sdk.eval-run`
- attributes: `skill_path`, `mode`, `runner`, `codex_profile`,
  `codex_exec_invoked`, `trace_id`, `receipt_path`
- child span per selected case: case id, case status, blocker class, duration,
  output artifact path
- child span for `codex exec --profile`: command argv redacted for secrets,
  profile name retained, cwd retained only if repo-relative or temp-safe

Hard rule: traces must not include raw prompts, secrets, local absolute paths,
or full model outputs unless a separate redaction policy explicitly allows them.

The v1 trace contract uses one immutable receipt digest as the trace ID seed.
It emits nested profile-preflight, scenario-selection, scenario,
deterministic-evaluator, generation, judge-score, and receipt-validation spans.
For provider-backed work, `codex_profile` is accepted only when derived from an
executed `codex exec --profile <lane>` argv. `execution_profile` continues to
describe sandbox/write/approval constraints, while `judge_profile` describes
the scoring configuration. Neither can satisfy the runtime-profile proof.

Individual `oss-local` and `oss-cloud` evals are separate traces. An A/B packet
is one comparison trace containing ordered `oss-local` then `oss-cloud`
generation spans, allowing comparison without merging their lane truth.

### Lane 3: Phoenix Experiments For Compare/Trend

Goal: use Phoenix experiments only when the data is stable enough to compare
runs across time.

Good first dataset:

- one skill: `Skills/agent-ops/improve-agent-native`
- one bounded suite: current smoke or release scenario set
- examples: case id, user-facing task, expected signal summary, lane
- outputs: structured final result from the repo receipt, not raw transcript
- evaluators: status match, blocker-class classifier, expected-signal pass

Do not start with Tessl live outputs. Start with SDK internal receipts and add
Tessl view artifacts later after `tessl-score` receipts exist.

## Implemented Integration

The first integration slice is now implemented in the repo-owned `ask` facade:

* `./bin/ask sdk observability phoenix-status --base-url http://localhost:6006 --json --robot`
  checks the Phoenix OSS service without mutating repo state.
* `./bin/ask sdk observability phoenix-mirror --receipt <receipt.json> --preview --json --robot`
  previews a redacted Phoenix-ready JSONL projection from an SDK eval,
  closeout, or observability receipt.
* `./bin/ask sdk observability phoenix-mirror --receipt <receipt.json> --out <events.jsonl> --write --json --robot`
  writes the explicit JSONL mirror artifact.

The mirror preserves lane metadata such as `runner`, `mode`, `package_id`,
`package_digest`, `codex_profile`, and `codex_exec_invoked` when those fields
exist in the source receipt. It does not copy raw prompt, transcript, message,
tool-call, stdout, stderr, or model-output fields.

The mirror now enforces these deterministic guardrails before writing output:

* source receipts must be eval closeout, eval run, or observability receipts;
* source receipts with raw prompt, transcript, message, tool-call, stdout,
  stderr, or output fields are blocked instead of silently mirrored;
* mirrored rows must be redacted allowlisted objects with stable event types
  and required root fields;
* `oss-local` and `oss-cloud` rows must prove `codex_exec_invoked=true`;
* write mode requires an explicit `.jsonl` output path that does not overwrite
  the source receipt.

## Next Integration Slices

1. Validate the v1 nested OTLP trace path with a live deterministic eval by
   setting `ASK_PHOENIX_EVAL_TRACE=1`; default remains off.
2. Add a report command that prints lane-separated status:
   `sdk-mechanical`, `oss-local`, `oss-cloud`, `tessl-local`,
   `tessl-external`, and `phoenix-observed`.
3. Only after the local mirror and explicit trace flag work, consider
   installing Phoenix Docs MCP or Phoenix MCP for operator-driven inspection.

## Validation Plan

Current proof from this investigation:

- Command: `curl -fsSL https://arizeai-433a7140.mintlify.site/llms.txt -o <temporary-doc-index>` -> pass
- Command: `docker info --format "{{.ServerVersion}}"` -> blocked because the Docker daemon is not running.
- Command: `lsof -nP -iTCP:6006 -sTCP:LISTEN` -> pass with no listener.
- Command: `lsof -nP -iTCP:4317 -sTCP:LISTEN` -> pass with no listener.
- Command: `codex --version` -> pass with `codex-cli 0.142.5`.

Current implemented proof after Docker started:

- Command: `docker info --format "{{.ServerVersion}}"` -> pass with `29.5.3`.
- Command: `docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}"` -> pass and found `evals-phoenix-phoenix-1` using `arizephoenix/phoenix:latest`.
- Command: `curl -fsS -I http://localhost:6006` -> pass with `HTTP/1.1 200 OK` and `x-phoenix-server-version: 17.12.0`.
- Command: `docker inspect evals-phoenix-phoenix-1 --format "{{json .Config.Env}}"` -> pass and confirmed `PHOENIX_PORT=6006`, `PHOENIX_GRPC_PORT=4317`, and `PHOENIX_WORKING_DIR=/mnt/data`.
- Command: `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_skills_sdk_phoenix_observability.py tests/test_skills_sdk_eval_runner.py` -> pass with 48 tests.
- Command: `./bin/ask sdk observability phoenix-status --base-url http://localhost:6006 --json --robot` -> pass with Phoenix server version `17.12.0`.
- Command: `./bin/ask sdk observability phoenix-mirror --receipt Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/eval-run-receipt.json --preview --json --robot` -> pass and previewed 2 redacted rows.
- Command: `./bin/ask sdk observability phoenix-mirror --receipt Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/eval-run-receipt.json --out <temporary-jsonl-output> --write --json --robot` -> pass and wrote 2 redacted rows.

Future implementation proof:

- Unit test: a sample `workflow-closeout.json` converts to redacted
  Phoenix-safe events with lane, profile, status, and receipt path retained.
- Unit test: `blocked` receipts remain blocked in the mirror and never become
  failed or passed experiment rows.
- Unit test: `oss-local` and `oss-cloud` mirrored rows require
  `codex_exec_invoked=true` and matching `codex_profile`.
- Local smoke: with Docker running, Phoenix UI responds on `6006` and a
  redacted sample trace appears under a project named
  `agent-skills/<skill-slug>`.
- Package-isolated trace smoke: use `uv run --no-project --with arize-phoenix-otel --with opentelemetry-sdk --with opentelemetry-exporter-otlp-proto-http python <smoke-script>`
  rather than mutating the repo or Infrastructure Python environments.

## Decision Boundary

This artifact now claims:

- Phoenix is running locally at `http://localhost:6006` during this closeout.
- A repo-owned command can check Phoenix status.
- A repo-owned command can preview and write a redacted eval receipt mirror.

This artifact does not claim:

- A current live OSS eval has been emitted as OTLP spans into Phoenix.
- `oss-local` or `oss-cloud` behavior is passing today.
- Tessl local or external proof is green.
- Phoenix evidence replaces repo-owned SDK receipts.
