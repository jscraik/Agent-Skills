---
source: https://docs.coderabbit.ai/tools/tflint
---

# TFLint

## Files
TFLint runs only on files with the following extension:

- `.tf`

## Configuration

- If the repository does not include `.tflint.hcl`, CodeRabbit runs TFLint with its safe defaults.

- If the repository does include `.tflint.hcl`, CodeRabbit writes and uses a safe override config that enables only the bundled `terraform` ruleset.

- A repository `.tflint.hcl` is not required.

## Security policy and restrictions

- CodeRabbit recognizes the following plugin names as approved when inspecting `.tflint.hcl`.

- **terraform** — bundled with TFLint (tflint-ruleset-terraform)

- **aws** — tflint-ruleset-aws

- **google** — tflint-ruleset-google

- **azurerm** — tflint-ruleset-azurerm

## When we skip TFLint
CodeRabbit skips TFLint when:

- TFLint is disabled in your CodeRabbit configuration.

- No `.tf` files are in the pull request.

- TFLint is already running in GitHub workflows.

## Links

- TFLint GitHub Repository

- TFLint Documentation
