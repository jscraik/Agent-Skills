# RPGW: Recursive Promotion Gate Workflow

Validates promotion decision artifacts for compliance before merge.

---

## ABBREVIATION MAP

| Abbr | Meaning |
|------|---------|
| RPGW | Recursive promotion gate workflow |
| PD | Promotion decision |
| IJ | Iteration journal |
| RUN | Run artifact |
| VAL | Validation |
| CO | Changed-only |

---

## TRIGGER MATRIX

| EVENT | PATHS | MODE |
|-------|-------|------|
| PR | `**/promotion_decision.json`, `**/iteration_journal.jsonl`, `**/run.json`, `lessons/**`, `recursive-loop-approvers.{yaml,sig}`, `human_promote_recursive_run.sh`, `validate_recursive_promotions.sh`, `validate_recursive_promotion.py`, workflow self | CO |
| WDsp | Same paths | Full |

---

## JOB PIPELINE

```mermaid
flowchart TB
    A[PR/WDsp] --\u003e B[Checkout Full]
    B --\u003e C[Python 3.12]
    C --\u003e D{Event?}
    D --\u003e|PR| E[Validate Changed]
    D --\u003e|WDsp| F[Validate All]
    E --\u003e G[Upload Report]
    F --\u003e G

    style E fill:#e1f5e1
    style F fill:#e1f5e1
    style G fill:#fff3e1
```

---

## PERMISSIONS

```yaml
permissions:
  contents: read
```

---

## JOB: VALIDATE PROMOTION ARTIFACTS

| CONFIG | VALUE |
|--------|-------|
| Runner | `ubuntu-latest` |
| Checkout | Full history (`fetch-depth: 0`) |
| Python | `3.12` |

### PR Mode (Changed-Only)

```bash
bash Infrastructure/scripts/validate_recursive_promotions.sh \
  --changed-only \
  --base-sha "${{ github.event.pull_request.base.sha }}" \
  --head-sha "${{ github.event.pull_request.head.sha }}" \
  --report-json Infrastructure/artifacts/skill-graphs/pilot/promotion-validation-report.json \
  --strict-runs
```

### WDsp Mode (Full)

```bash
bash Infrastructure/scripts/validate_recursive_promotions.sh \
  --report-json Infrastructure/artifacts/skill-graphs/pilot/promotion-validation-report.json \
  --strict-runs
```

### Flags

| FLAG | DESCRIPTION |
|------|-------------|
| `--changed-only` | Validate only changed files in git range |
| `--base-sha` | Base commit for comparison |
| `--head-sha` | Head commit for comparison |
| `--report-json` | Output validation report path |
| `--strict-runs` | Enforce strict run parity checks |

---

## ARTIFACTS

| NAME | PATH | CONDITION |
|------|------|-----------|
| `recursive-promotion-validation` | `Infrastructure/artifacts/skill-graphs/pilot/promotion-validation-report.json` | `always()` |

---

## LOCAL COMMANDS

```bash
# Validate changed (PR simulation)
bash Infrastructure/scripts/validate_recursive_promotions.sh \
  --changed-only \
  --base-sha HEAD~1 \
  --head-sha HEAD \
  --report-json promotion-validation-report.json \
  --strict-runs

# Validate all
bash Infrastructure/scripts/validate_recursive_promotions.sh \
  --report-json promotion-validation-report.json \
  --strict-runs

# With custom runs root
bash Infrastructure/scripts/validate_recursive_promotions.sh \
  --runs-root Infrastructure/artifacts/skill-graphs/runs \
  --report-json promotion-validation-report.json \
  --strict-runs
```

---

## CI REFERENCE

Workflow: `.github/workflows/recursive-promotion-gate.yml`

---

## RELATED

- [Promotion gate workflow](/docs/skill-graphs/workflows/promotion-gate.md)
- [Validate script](/Infrastructure/scripts/validate_recursive_promotions.sh)
- [Human promote script](/Infrastructure/scripts/human_promote_recursive_run.sh)
- [Validation logic](/Skills/skill-builder/Infrastructure/scripts/validate_recursive_promotion.py)
