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
| `smoke evals` | `./bin/ask evals run <path> --mode smoke --json --robot` | first-class gate |
| `release evals` | `./bin/ask evals run <path> --mode release --json --robot` or owned equivalent | first-class gate |
| `package boundary checks` | `./bin/ask skills validate-boundaries <handle-or-path> --json --robot` or owned equivalent | first-class evidence check |
| `sync/projection checks` | `./bin/ask skills prove <handle-or-path> --json --robot` or owned sync proof | first-class evidence check |
| `docs/prose/spelling` | `vale <paths>` when installed, or another documented repo docs-quality wrapper | first-class only when a canonical docs-quality command actually ran |

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
