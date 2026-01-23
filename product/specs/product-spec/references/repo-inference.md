# Repo Inference Rules (Deterministic)

Purpose: infer project types consistently using stack files, directory names, and README keywords. Use these signals before selecting personas.

## Priority order
1) Stack files (highest confidence)
2) Directory names
3) README keywords

If signals conflict, include the broader persona set and record an Evidence gap.

## Stack file signals
- Web app: `package.json`, `vite.config.*`, `next.config.*`, `astro.config.*`, `svelte.config.*`
- Backend/API: `Dockerfile`, `docker-compose.yml`, `go.mod`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `pom.xml`, `build.gradle`, `Cargo.toml`
- CLI/devtools: `bin/`, `cmd/`, `cli/`, `Click`, `Typer`, `Cobra`, `clap`, `argparse`, `commander`
- Data/ML: `notebooks/`, `data/`, `ml/`, `model/`, `pipelines/`, `torch`, `tensorflow`, `jax`, `sklearn`, `mlflow`, `wandb`
- Infra/DevOps: `terraform/`, `pulumi/`, `helm/`, `k8s/`, `ansible/`, `.github/workflows/`, `cloudformation`

## Directory name signals
- `apps/`, `web/`, `frontend/` -> Web app
- `services/`, `api/`, `server/` -> Backend/API
- `cli/`, `tools/`, `scripts/` -> CLI/devtools
- `ml/`, `data/`, `pipelines/` -> Data/ML
- `infra/`, `ops/`, `platform/` -> Infra/DevOps

## README keyword signals
- Web app: "UI", "frontend", "SPA", "browser", "React", "Vite"
- Backend/API: "API", "service", "endpoint", "database"
- CLI/devtools: "CLI", "command line", "terminal", "devtool"
- Data/ML: "model", "training", "dataset", "inference", "pipeline"
- Infra/DevOps: "deploy", "infra", "Kubernetes", "CI/CD"
