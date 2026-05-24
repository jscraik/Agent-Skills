# Skill Validation Reporting Contract

Use this contract when reporting validator status for skills or plugins in Agent Skills Kit.

## Purpose

Make validation reporting deterministic. Reviews should name gates the same way the
repository exposes them, distinguish wrapper checks from standalone scripts, and
avoid claiming that a file-backed validator passed when only a broader wrapper ran.

## Reporting Rules

Use only these result values:

- `pass`
- `fail`
- `blocked`
- `not applicable`

Use these support labels:

- `available`: the gate has a canonical repo command or directly evidenced artifact.
- `not separately supported`: the repo exposes the check only through a wrapper or
  family gate, not as a standalone validator surface.
- `unknown`: local evidence does not prove whether the validator is supported.

## Naming Policy

Prefer the canonical command or wrapper name that the repo actually documents.
Only report a file-backed validator name when that validator is both:

1. discoverable from current local repo evidence, and
2. independently runnable or directly evidenced as its own gate.

If only a wrapper ran, report the wrapper label instead of the internal file name.

## Canonical Gate Labels

| Report label | Canonical evidence surface | Standalone reporting policy |
| --- | --- | --- |
| `strict skill audit` | `./bin/ask skills audit <path> --level strict --json --robot` | first-class gate |
| `skill gate` | `./bin/ask skills validate-skill-gate <path> --json --robot` | first-class gate |
| `progressive disclosure lint` | `bash Infrastructure/scripts/validation-and-linting/lint_progressive_disclosure.sh --mode strict` | first-class gate |
| `OpenAI skill format` | `./bin/ask skills validate-openai-format <path> --mode strict --json --robot` | first-class wrapper gate |
| `OpenClaw` | strict audit output or dedicated local evidence | report only when explicit evidence exists |
| `Plugin Eval` | `Infrastructure/bin/plugin-eval analyze <path> --format markdown` | first-class gate |
| `Snyk dependency screening` | `./bin/ask skills external-review <path> --include-snyk --json --robot` or release eval `security_dependency_screening` artifact | first-class gate for manifest-backed release candidates |
| `smoke evals` | `./bin/ask evals run <path> --mode smoke --json --robot` | first-class gate |
| `release evals` | `./bin/ask evals run <path> --mode release --json --robot` or owned equivalent | first-class gate |
| `package boundary checks` | `./bin/ask skills validate-boundaries <handle-or-path> --json --robot` or owned equivalent | first-class evidence check |
| `sync/projection checks` | `./bin/ask skills prove <handle-or-path> --json --robot` or owned sync proof | first-class evidence check |
| `docs/prose/spelling` | `vale <paths>` execution is the only accepted evidence; repo docs-quality wrappers may orchestrate but do not replace the Vale output requirement | first-class only when Vale (or equivalent canonical docs-quality command) has run and produced output |
| `eval realism` | explicit eval schema fields such as `realistic: true\|false`, strict audit findings, or owned eval-realism validator output | first-class when schema or validator evidence exists |
| `eval observability export` | `Infrastructure/references/eval-observability-otel-contract.md`, local eval artifacts, and explicit repo-owned OTel-style export evidence when configured | advisory by default; first-class only when an eval program explicitly requires observability export |
| `media artifact persistence` | generated artifact path, prompt metadata path, sidecar, and existence check under `.harness/media/` or owned artifact location | first-class only for media/artifact asks |

## Skill Eval Lane Taxonomy

Keep the local skill eval and second-review lanes separate when reporting
readiness. They answer different questions and one lane cannot silently stand in
for another:

| Lane | Canonical command | What it proves | What it does not prove |
| --- | --- | --- | --- |
| local evals | `./bin/ask evals run <path> --mode smoke\|release --json --robot` | dynamic skill behavior, run traces, command/artifact expectations, and release-mode gates | static readability or Tessl best-practice score |
| Plugin Eval | `Infrastructure/bin/plugin-eval analyze <path> --format markdown` or `./bin/ask skills external-review <path> --json --robot` | budget, ergonomics, reviewability, and obvious packaging risks | runtime behavior, trigger realism, Snyk dependency posture, or Tessl quality |
| Tessl lint | `./bin/ask skills external-review <path> --json --robot` | Tessl tile package-shape compatibility for a stable staged local wrapper | direct content quality for the canonical `SKILL.md` source |
| Tessl review | `./bin/ask skills external-review <path> --json --robot` | local best-practice/content review for a copied work-in-progress skill | publishing readiness or registry upload success |
| Snyk dependency screening | `./bin/ask skills external-review <path> --include-snyk --json --robot` or release eval `security_dependency_screening` artifact | high-severity dependency vulnerability screening for supported manifests | prompt/security-policy correctness for pure instruction-only skills |
| OTel-inspired observability | optional local eval observability artifacts or repo-owned export evidence | trace correlation, debugging, dataset creation, and scorer workflow support | skill correctness, deterministic pass/fail, local artifact existence, Braintrust integration, or release readiness unless explicitly required |

`ask skills external-review` is local-first despite the name. It runs internal
strict audit plus local second-review tools, never invokes `npx`, and never
publishes or uploads a skill. Snyk is the only lane that may contact an external
service, and it runs only when explicitly requested in local review or when the
release-eval policy requires dependency screening for a manifest-backed
candidate.

## Special Cases

### `openai_skill.py`

- If only `./bin/ask skills validate-openai-format` or `lint_openai_skill_format.sh` ran, report `OpenAI skill format`.
- Do not additionally report `openai_skill.py` as `pass`.
- If a standalone `openai_skill.py` command is not documented and was not run,
  either omit it or report `openai_skill.py` as `not separately supported`.

### `skill_gate.py`

- Report `skill_gate.py` only when the direct script was run or a direct artifact
  proves its result.
- If the first-class wrapper `./bin/ask skills validate-skill-gate` ran, report
  `skill gate` unless the direct script itself was also independently evidenced.
- If it exists only as a legacy or optional direct script and was not run, report
  `skill_gate.py` as `blocked` with the reason `not run`, or omit it when the
  table is focused on active canonical gates.
- Do not treat strict audit or another wrapper pass as proof that `skill_gate.py`
  itself passed.

### `docs/prose/spelling`

- Passing format or progressive-disclosure lint is not enough.
- Only report `pass` when a dedicated docs-quality command actually ran.
- If no canonical docs-quality command is identified, report `blocked` with the
  exact missing-tool or missing-command reason.

### `eval realism`

- Prefer explicit schema-backed evidence such as `realistic` (with values `true` or `false`),
  `why_realistic`, `expected_behavior`, and `anti_overfit_notes`.
- Natural-language markers are fallback evidence only.
- Synthetic examples, trigger-word-only prompts, internal test-case phrasing, or
  prompts that would not plausibly be sent by a user should be reported as
  `fail` when the skill claims release readiness.
- When evals exist and no explicit realism schema field or validator evidence
  is available, report `eval realism` as `blocked` with reason
  `missing realism evidence surface`; do not omit the row for release-readiness
  claims.
- Plugin Eval success does not override strict-audit or eval-realism failures.

### `Snyk dependency screening`

Use Snyk when any of these are true:

- the candidate has supported dependency manifests, such as `package.json`,
  `pyproject.toml`, `requirements.txt`, `Gemfile`, `go.mod`, or lockfiles
- the report claims release readiness for a manifest-backed skill or plugin
  package
- dependency files, installer scripts, generated package surfaces, or plugin
  runtime dependencies changed
- local evidence must match the CircleCI/Snyk security-screening lane
- the user explicitly asks for Snyk, dependency vulnerability screening, or
  external security advisory evidence

Do not run Snyk by default for pure `SKILL.md`-first instruction-only
candidates with no supported dependency manifest. Report those as `not
applicable` unless the user explicitly asks for the advisory lane.

- Required for release-readiness claims on manifest-backed skill or plugin
  packages.
- Report `not applicable` only when no supported dependency manifest exists
  under the candidate package.
- For manifest-backed candidates, `not_applicable`,
  `blocked_no_supported_projects`, `blocked_missing_binary`, `blocked_auth`,
  `timeout`, `advisory`, or `error` prevents release readiness.
- Use the high-severity threshold so local release evals and CI enforce the same
  dependency-screening bar.

### `Tessl lint` and `Tessl review`

- Tessl lint expects a Tessl `tile.json` package. Canonical repo skills are
  `SKILL.md`-first directories, so a direct `tessl skill lint <skill-dir>`
  failure about missing `tile.json` is a packaging-shape blocker, not a content
  finding.
- The canonical repo command creates a stable local `tile.json` wrapper
  around a copied `SKILL.md` before running Tessl lint. Report this as `Tessl
  lint` and describe it as a stable `<tempdir>/ask-tessl-evals/<skill-path>-<sha12>`
  tile package-shape check that preserves `tile.json`, `tessl.json`, copied
  skill files, and included references for evidence.
- Tessl review is the local best-practice/content reviewer for the skill copy.
  Report it separately from Tessl lint. The accepted Tessl review floor is a
  score of `95`; lower scores block release or completion claims for Tessl.
- Do not use Tessl lint or review evidence to imply that a skill was published,
  registered, uploaded, or accepted by a registry.
- If Tessl reports missing files or links outside the staged tile, preserve
  those findings as package self-containment issues.
- Plugin Eval remains a budget and ergonomics guardrail: `B+` or better with
  zero failures is acceptable when strict audit, evals, and Tessl gates pass.

### `media artifact persistence`

- Use only for requests that require generated media or concrete artifacts.
- Report `pass` only when artifact existence and persistence are directly
  evidenced by path, sidecar, and command/tool output.
- If generation succeeds but the artifact path is not discoverable, report
  `blocked`, not `pass`.
- If generation is available and the user requested an artifact, prompt text
  alone is a `fail`.
- If generation is unavailable, report `blocked` with the exact unavailable
  tool, approval, output-path, or policy reason.
- If generation availability is `unknown`, report artifact persistence as
  `blocked`; do not treat an unchecked tool surface as a fallback success.

### `eval observability export`

- OTel-inspired local trace export is opt-in eval observability, not a default
  readiness gate. Braintrust is an inspiration source for the local package
  pattern, not an integration target in this contract.
- Local eval artifacts remain the canonical evidence source:
  `codex_events.jsonl`, `stdout.txt`, `stderr.txt`, `result.json`,
  scorecards, summaries, and release manifests.
- Report `not applicable` or omit the lane when the eval program did not
  request observability export.
- Report `blocked` when local export was requested but network, collector,
  endpoint, package, or policy approval was missing. Do not require or mention
  Braintrust credentials unless a separate Braintrust integration was explicitly
  requested.
- Report `pass` only when export completion is directly evidenced and the
  exported data is redacted according to
  `Infrastructure/references/eval-observability-otel-contract.md`.
- Do not mark the underlying skill eval as failed only because local OTel-style
  export failed. Classify exporter failure as `blocked_eval_observability`
  unless the named test case is specifically testing exporter behavior.
- Do not export raw prompts, completions, stdout, stderr, secrets, private URLs,
  credentials, or full file contents by default.

### `package boundary checks`

- A clean pass may still carry operational risk.
- Use `pass with risk` only in prose commentary, not in the result column.
- The result column must stay `pass`; put the residual risk in `Notes`.

## Evidence Policy

Each reported gate should include:

- exact command or artifact path
- result
- short note describing what was and was not proven

Evidence must not over-claim:

- source existence does not prove runtime availability
- wrapper success does not prove a nested script passed
- projection existence does not prove canonical ownership
- Plugin Eval success does not prove strict audit, eval realism, media
  persistence, docs/prose/spelling, or runtime visibility
- generated prompt text does not prove a generated media artifact exists
- generated artifact churn does not prove semantic source changes
- external docs prove external behavior only; they do not prove local repo
  implementation, local runtime visibility, or prior session behavior
- session evidence proves observed local behavior only; it does not prove current
  external API or library semantics

## Readiness Decision

Report an overall readiness decision whenever claiming a skill is acceptable,
release-ready, or fully hardened.

### Gate Result Values

Use only these result values for individual gate reporting:

- `pass`
- `fail`
- `blocked`
- `not applicable`

### Readiness Decision Enum

The overall readiness state uses a separate `readiness_decision` enum (distinct from gate `result`):

- `pass`: every required gate is `pass` or `not applicable` with a reason
- `fail`: one or more required gates is `fail`
- `blocked`: one or more required gates is `blocked`
- `unverified`: a required gate was not run or lacks evidence

Evaluation order is deterministic and MUST use this precedence:
`fail` > `blocked` > `unverified` > `pass`.
When multiple conditions are true, choose the highest-precedence state.

Note: Parsers and contract validators should treat `readiness_decision` (not gate `result`) as the source of overall readiness states. The value `unverified` is not allowed as a gate `result`.

Include the controlling gate and reason. Do not narratively override the
decision with a higher-confidence summary.

## Preferred Table Shape

| Validator | Available | Result | Evidence | Notes |
| --- | ---: | --- | --- | --- |

Recommended `Available` values:

- `yes`
- `no`
- `not separately supported`
- `unknown`

## Future Upgrade Path

If the repository wants fully deterministic reporting for legacy direct scripts,
promote them into first-class `./bin/ask` commands or a single documented
validation wrapper. Prefer those promoted command labels over internal file
names.
