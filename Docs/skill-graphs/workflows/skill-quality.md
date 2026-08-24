# SQW: Skill Quality Workflow

Validates skill structure against industry benchmarks and runs optional LLM evals.

---

## ABBREVIATION MAP

| Abbr | Meaning                 |
| ---- | ----------------------- |
| SQ   | Skill quality           |
| T1   | Tier-1 (structure gate) |
| T2   | Tier-2 (eval gate)      |
| SG   | Structure gate          |
| EB   | Eval baseline           |
| BM   | Benchmark               |
| EVAL | LLM evaluation          |
| WD   | Workflow dispatch       |
| PR   | Pull request            |

---

## TRIGGER MATRIX

| EVENT | PATHS                                                                                                                  | MODE              | JOBS    |
| ----- | ---------------------------------------------------------------------------------------------------------------------- | ----------------- | ------- |
| PR    | `**/SKILL.md`, `**/evals.yaml`, `**/contract.yaml`, `Infrastructure/scripts/**`, `Infrastructure/templates/evals.yaml` | Auto              | T1 only |
| WD    | Manual                                                                                                                 | `run_evals=false` | T1 only |
| WD    | Manual                                                                                                                 | `run_evals=true`  | T1 → T2 |

---

## JOB PIPELINE

```mermaid
flowchart LR
    A[PR/WD] --> B{T1/SG}
    B -->|PASS| C[Upload BM]
    B -->|FAIL| X[EXIT 1]

    WD -->|run_evals=true| D{T2/EB}
    D -->|PASS| E[Build Dashboard]
    E --> F[Upload Reports]
    D -->|FAIL| X

    subgraph "Tier-1: Structure"
        B
    end

    subgraph "Tier-2: Evals"
        D
        E
    end
```

---

## TIER-1: STRUCTURE GATE (SG)

| CHECK    | COMMAND                                                                        |
| -------- | ------------------------------------------------------------------------------ |
| Checkout | `actions/checkout@v6` (full)                                                   |
| Python   | `3.12`                                                                         |
| GH CLI   | `Infrastructure/scripts/lifecycle-and-sync/ensure-gh-cli.sh`                   |
| Deps     | `pip install pyyaml`                                                           |
| Validate | `run_repo_skill_quality.py --root . --baseline-file ... --benchmark-mode warn` |
| Upload   | `Infrastructure/artifacts/industry-benchmark-latest.json`                      |

### SG Flags

```bash
python Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py \
  --root . \
  --baseline-file Skills/skill-builder/Infrastructure/references/skill-quality-baseline.json \
  --benchmark-mode warn \
  --benchmark-config Skills/skill-builder/Infrastructure/references/benchmark-policy.json \
  --benchmark-output-json Infrastructure/artifacts/industry-benchmark-latest.json \
  --format text
```

---

## TIER-2: EVAL BASELINE (EB)

| CONDITION | `github.event_name == 'workflow_dispatch' && inputs.run_evals == 'true'` |
| NEEDS | `[structure-gate]` (must pass) |

### EB Flags

```bash
python Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py \
  --root . \
  --run-evals \
  --dual-run \
  --capture-jsonl \
  --tier2-mode "${{ inputs.tier2_mode }}" \
  --benchmark-mode warn \
  --benchmark-config Skills/skill-builder/Infrastructure/references/benchmark-policy.json \
  --benchmark-output-json Infrastructure/artifacts/industry-benchmark-latest.json \
  --format text
```

### Dashboard Build

```bash
python Skills/skill-builder/Infrastructure/scripts/build_skill_eval_dashboard.py \
  --reports-root .tmp/agent-skills-artifacts/skills \
  --out-json .tmp/agent-skills-artifacts/skills/dashboard.json \
  --out-md .tmp/agent-skills-artifacts/skills/dashboard.md
```

### EB Outputs

| ARTIFACT  | PATH                                                      |
| --------- | --------------------------------------------------------- |
| Reports   | `.tmp/agent-skills-artifacts/skills/**`                    |
| Benchmark | `Infrastructure/artifacts/industry-benchmark-latest.json` |

---

## INPUTS (WD Only)

| INPUT        | TYPE   | DEFAULT | DESCRIPTION                                      |
| ------------ | ------ | ------- | ------------------------------------------------ |
| `run_evals`  | bool   | `false` | Run LLM evals (requires codex/codex CLIs + auth) |
| `tier2_mode` | string | `warn`  | Tier-2 handling: `warn` \| `strict` \| `skip`    |

---

## PERMISSIONS

```yaml
permissions:
  contents: read
```

---

## DEPENDENCIES

| COMPONENT | SOURCE                                                                       |
| --------- | ---------------------------------------------------------------------------- |
| Baseline  | `Skills/skill-builder/Infrastructure/references/skill-quality-baseline.json` |
| BM Policy | `Skills/skill-builder/Infrastructure/references/benchmark-policy.json`       |
| Script    | `Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py`      |
| Dashboard | `Skills/skill-builder/Infrastructure/scripts/build_skill_eval_dashboard.py`  |
| Helper    | `Infrastructure/scripts/lifecycle-and-sync/ensure-gh-cli.sh`                 |

---

## COMMANDS

```bash
# Validate structure only (local)
python Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py \
  --root . \
  --baseline-file Skills/skill-builder/Infrastructure/references/skill-quality-baseline.json \
  --benchmark-mode warn \
  --format text

# Run full evals (requires codex/codex auth)
python Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py \
  --root . \
  --run-evals \
  --dual-run \
  --capture-jsonl \
  --tier2-mode warn \
  --format text

# Build dashboard manually
python Skills/skill-builder/Infrastructure/scripts/build_skill_eval_dashboard.py \
  --reports-root .tmp/agent-skills-artifacts/skills \
  --out-json .tmp/agent-skills-artifacts/skills/dashboard.json \
  --out-md .tmp/agent-skills-artifacts/skills/dashboard.md
```

---

## CI REFERENCE

Workflow: `.github/workflows/skill-quality.yml`

---

## RELATED

- [Skill builder scripts](/Skills/skill-builder/scripts)
- [Benchmark policy](/Skills/skill-builder/Infrastructure/references/benchmark-policy.json)
- [Skill quality baseline](/Skills/skill-builder/Infrastructure/references/skill-quality-baseline.json)
