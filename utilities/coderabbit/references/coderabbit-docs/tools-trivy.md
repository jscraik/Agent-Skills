---
source: https://docs.coderabbit.ai/tools/trivy
---

# Trivy

## Files
Trivy runs only on files matching these patterns:

- **Terraform**: `*.tf`, `*.tf.json`, `*.tofu`, `*.tofu.json`

- **Docker**: `Dockerfile`, `Dockerfile.*`, `*.dockerfile`

- **Kubernetes**: `k8s/**/*.yaml`, `k8s/**/*.yml`, `kubernetes/**/*.yaml`, `kubernetes/**/*.yml`, `manifests/**/*.yaml`, `manifests/**/*.yml`

- **Helm**: `helm/**/*.yaml`, `helm/**/*.yml`, `charts/**/*.yaml`, `charts/**/*.yml`, `Chart.yaml`, `values.yaml`, `values.yml`

- **CloudFormation**: `*.template.json`, `*.template.yaml`, `*.template.yml`, `cloudformation/**/*.json`, `cloudformation/**/*.yaml`, `cloudformation/**/*.yml`

- **Azure ARM**: `azuredeploy.json`, `azuredeploy.parameters.json`, `arm/**/*.json`

- **Docker Compose**: `docker-compose.yaml`, `docker-compose.yml`, `compose.yaml`, `compose.yml`

Non-IaC files (e.g. GitHub workflows, `package.json`) are excluded.
## Configuration

- CodeRabbit will read and use the repo’s `trivy.yaml` config file.

## Profile behavior

- **Chill**: `--severity CRITICAL,HIGH`

- **Assertive**: `--severity CRITICAL,HIGH,MEDIUM,LOW,UNKNOWN`

## Links

- Trivy GitHub Repository

- Trivy Documentation
