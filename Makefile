# Optional harness helpers for agent-skills
# Run `make help` to see available targets.

.PHONY: help setup hooks status sync validate diagnose docs-lint check ci env-check

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: hooks ## Configure local git hooks

hooks: ## Install pre-commit/commit-msg/pre-push hooks
	node scripts/setup-git-hooks.js

status: ## Quick repository status
	./scripts/status.sh

sync: ## Sync skills and regenerate index
	bash scripts/sync_skills.sh

validate: ## Run repository validation suite
	bash scripts/validate_all.sh

diagnose: ## Diagnose all skills
	python3 scripts/diagnose_skill.py --all

docs-lint: ## Run docs lint checks
	python3 scripts/docs_lint.py --mode warn --config docs-policy.json

check: validate diagnose ## Run core validation + diagnostics

ci: check docs-lint ## Run CI-equivalent local checks

env-check: ## Validate environment for optional harness tooling
	./scripts/check-environment.sh
