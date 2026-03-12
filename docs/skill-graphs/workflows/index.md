# Skill Graph Workflows

## Quality & Promotion

- [Promotion gate workflow](/docs/skill-graphs/workflows/promotion-gate.md) — 8-gate promotion check with state machine
- [Reviewer rubric](/docs/skill-graphs/workflows/reviewer-rubric.md) — 5-dimension scoring matrix with hard fail conditions
- [Recursive promotion gate](/docs/skill-graphs/workflows/recursive-promotion-gate.md) — PR vs WDsp modes with strict parity
- [Skill quality](/docs/skill-graphs/workflows/skill-quality.md) — T1/T2 validation jobs with conditional triggers
- [Recursive skill shadow](/docs/skill-graphs/workflows/recursive-skill-shadow.md) — Weekly shadow cycles with pilot profiles

## Security & Governance

- [Security scan](/docs/skill-graphs/workflows/security-scan.md) — Gitleaks, Semgrep, Trivy, artifact pre-check
- [Governance security gates](/docs/skill-graphs/workflows/gov-security-gates.md) — Compliance validation script

## CI/CD & Automation

- [PR pipeline](/docs/skill-graphs/workflows/pr-pipeline.md) — 3-job sequential validation (template, preflight, validate)
- [CI tests](/docs/skill-graphs/workflows/ci-tests.md) — Fast smoke tests (docs + skill diagnostics)
- [Docs governance](/docs/skill-graphs/workflows/docs-governance.md) — Mode-aware linting (warn/block)
- [Benchmark policy refresh](/docs/skill-graphs/workflows/benchmark-policy-refresh.md) — Weekly automated policy baseline PR

## Code Quality

- [CodeQL](/docs/skill-graphs/workflows/codeql.md) — Matrix analysis (javascript, python) with SARIF upload
- [Greptile review](/docs/skill-graphs/workflows/greptile-review.md) — AI bot integration with neutral check run

- Back to [Skill Graphs](/docs/skill-graphs)
