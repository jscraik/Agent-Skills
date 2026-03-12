# CTW: CI Tests Workflow

Fast smoke tests for docs and skills.

---

## ABBREVIATION MAP

| Abbr | Meaning |
|------|---------|
| CTW | CI tests workflow |
| DL | Docs lint |
| SD | Skill diagnostics |

---

## TRIGGER MATRIX

| EVENT | BRANCH |
|-------|--------|
| Push | `main` |
| PR | Any |

---

## JOB PIPELINE

```mermaid
flowchart TB
    A[Push/PR] --> B[Docs Test]
    A --> C[Skill Diagnostics]

    style B fill:#e1f5e1
    style C fill:#e1f5e1
```

---

## PERMISSIONS

```yaml
permissions:
  contents: read
```

---

## JOB: DOCS TEST

| CONFIG | VALUE |
|--------|-------|
| Runner | `ubuntu-latest` |
| Python | `3.11` |
| Command | `python3 scripts/docs_lint.py --mode warn --config docs-policy.json` |

---

## JOB: SKILL DIAGNOSTICS

| CONFIG | VALUE |
|--------|-------|
| Runner | `ubuntu-latest` |
| Python | `3.11` |
| Command | `python3 scripts/diagnose_skill.py --all` |

---

## LOCAL COMMANDS

```bash
# Docs lint
python3 scripts/docs_lint.py --mode warn --config docs-policy.json

# Skill diagnostics
python3 scripts/diagnose_skill.py --all
```

---

## CI REFERENCE

Workflow: `.github/workflows/ci-tests.yml`

---

## RELATED

- [Docs lint script](/scripts/docs_lint.py)
- [Skill diagnostics](/scripts/diagnose_skill.py)
