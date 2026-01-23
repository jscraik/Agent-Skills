# Adversarial Review Personas (Adaptive Coverage)

Purpose: map project types to the right software-engineering personas for adversarial review. Use inference from repo contents to select coverage. Record assumptions and evidence gaps when unsure.

## Core persona pool (always available)
- PM (Product Manager)
- UX (Designer)
- FE (Frontend Engineer)
- BE (Backend Engineer)
- Security
- Reliability/SRE
- Data/ML
- Platform/Infra

## Optional personas (triggered by project type)
- QA/Test
- DevEx/Tooling

## Project type inference (stack + dirs + README)

Use all three signals; pick the highest-confidence project types. If ambiguous, include the broader set and mark an Evidence gap. See `references/repo-inference.md` for deterministic rules.

### Tech stack file signals
- Web app: `package.json`, `vite.config.*`, `next.config.*`, `astro.config.*`, `svelte.config.*`
- Backend/API: `Dockerfile`, `docker-compose.yml`, `go.mod`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `pom.xml`, `build.gradle`, `Cargo.toml`
- CLI/devtools: `bin/`, `cmd/`, `cli/`, `Click`, `Typer`, `Cobra`, `clap`, `argparse`, `commander`
- Data/ML: `notebooks/`, `data/`, `ml/`, `model/`, `pipelines/`, `requirements-ml.txt`, `torch`, `tensorflow`, `jax`, `sklearn`, `mlflow`, `wandb`
- Infra/DevOps: `terraform/`, `pulumi/`, `helm/`, `k8s/`, `ansible/`, `.github/workflows/`, `cloudformation`

### Directory name signals
- `apps/`, `web/`, `frontend/` -> Web app
- `services/`, `api/`, `server/` -> Backend/API
- `cli/`, `tools/`, `scripts/` -> CLI/devtools
- `ml/`, `data/`, `pipelines/` -> Data/ML
- `infra/`, `ops/`, `platform/` -> Infra/DevOps

### README keyword signals
- Web app: "UI", "frontend", "SPA", "browser", "React", "Vite"
- Backend/API: "API", "service", "endpoint", "database"
- CLI/devtools: "CLI", "command line", "terminal", "devtool"
- Data/ML: "model", "training", "dataset", "inference", "pipeline"
- Infra/DevOps: "deploy", "infra", "Kubernetes", "CI/CD"

## Persona coverage matrix

### Web apps
- Core: PM, UX, FE, BE, Security, Reliability/SRE, Data/ML, Platform/Infra
- Optional: QA/Test (UI), DevEx/Tooling (build tooling/CI)

### Backend services/APIs
- Core: PM, UX (if user-facing), BE, Security, Reliability/SRE, Data/ML (if data-heavy), Platform/Infra
- Optional: QA/Test (contracts), DevEx/Tooling (CI/CD, SDKs)

### CLI/devtools
- Core: PM, UX (terminal UX), FE (CLI UX), BE (core logic), Security, Reliability/SRE
- Optional: DevEx/Tooling (primary), QA/Test (golden tests)

### Data/ML/AI pipelines
- Core: PM, UX (if surfaced), BE, Data/ML (primary), Security, Reliability/SRE, Platform/Infra
- Optional: QA/Test (data validation), DevEx/Tooling (repro/CI)

### Infrastructure/DevOps
- Core: PM, Security, Reliability/SRE, Platform/Infra
- Optional: DevEx/Tooling (primary), QA/Test (infra tests)

## Selection rules (apply in order)
1) Infer project types from stack + dirs + README keywords.
2) Start with the persona set for each inferred project type.
3) Union the personas; include optional ones only when triggered.
4) If evidence is weak or conflicting, include the broader set and add an Evidence gap entry.
5) Use the persona order in the adversarial review section: PM -> UX -> FE -> BE -> Security -> Reliability/SRE -> Data/ML -> Platform/Infra -> QA/Test -> DevEx/Tooling.

## Evidence and gaps
- Every persona section ends with `Evidence:` or `Evidence gap:`.
- Add to Evidence Gaps section if persona selection was uncertain.
