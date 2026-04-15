# Harness Development Makefile
# Run `make help` to see available commands

.PHONY: help install setup preflight hooks hooks-pre-commit hooks-commit-msg hooks-pre-push secrets-staged docs-style-changed related-tests semgrep-changed diagrams-check dev build lint docs-lint fmt typecheck test check audit secrets security clean reset ci diagrams env-check

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# === Setup ===

install: ## Install dependencies
	pnpm install

setup: install hooks ## Full setup: install deps and configure git hooks

preflight: ## Run repository preflight checks (required local-memory gate by default)
	@bash ./Infrastructure/scripts/codex-preflight.sh

hooks: ## Setup git hooks
	node Infrastructure/scripts/setup-git-hooks.js

hooks-pre-commit: ## Run local pre-commit gates before creating a commit
	bash Infrastructure/scripts/validate_all.sh --ephemeral

hooks-commit-msg: ## Validate commit message policy (use HOOK_COMMIT_MSG or HOOK_COMMIT_MSG_FILE=/path)
	@tmp_file="$$(mktemp)"; \
	trap 'rm -f "$$tmp_file"' EXIT; \
	if [ -n "$${HOOK_COMMIT_MSG:-}" ]; then \
		printf '%s\n' "$${HOOK_COMMIT_MSG}" > "$$tmp_file"; \
	elif [ -n "$${HOOK_COMMIT_MSG_FILE:-}" ]; then \
		test -r "$${HOOK_COMMIT_MSG_FILE}" || { echo "Cannot read $$HOOK_COMMIT_MSG_FILE" >&2; exit 2; }; \
		cp "$${HOOK_COMMIT_MSG_FILE}" "$$tmp_file"; \
	elif [ -n "$${MSG_FILE:-}" ]; then \
		test -r "$${MSG_FILE}" || { echo "Cannot read $$MSG_FILE" >&2; exit 2; }; \
		cp "$${MSG_FILE}" "$$tmp_file"; \
	else \
		echo "Usage: HOOK_COMMIT_MSG=\"feat: test\" make hooks-commit-msg or make hooks-commit-msg HOOK_COMMIT_MSG_FILE=/path/to/commit-msg" >&2; \
		exit 2; \
	fi; \
	node Infrastructure/scripts/validate-commit-msg.js "$$tmp_file"

hooks-pre-push: ## Run local pre-push governance gates before pushing
	bash Infrastructure/scripts/validate_skill_authoring_family.sh
	python3 Infrastructure/scripts/diagnose_skill.py --all

secrets-staged: ## Scan staged content for secrets before committing
	pnpm run secrets:staged

docs-style-changed: ## Run Vale on staged authoritative docs only
	pnpm run docs:style:changed

related-tests: ## Run Vitest related mode for staged src implementation files
	pnpm run test:related

semgrep-changed: ## Run narrow Semgrep rules against changed src implementation files
	pnpm run semgrep:changed

diagrams-check: ## Refresh architecture diagrams when sensitive paths change and fail on drift
	@bash ./Infrastructure/scripts/check-diagram-freshness.sh

# === Development ===

dev: ## Start development server
	pnpm dev

build: ## Build for production
	@if [ -f "package.json" ]; then pnpm build; else echo "Skipping build (no package.json)"; fi

# === Quality ===

lint: ## Run linter
	@if [ -f "package.json" ]; then pnpm lint; else echo "Skipping lint (no package.json)"; fi

docs-lint: ## Lint markdown/docs
	@if [ -f "package.json" ]; then pnpm docs:lint; else echo "Skipping docs:lint (no package.json)"; fi

fmt: ## Format code
	@if [ -f "package.json" ]; then pnpm fmt; else echo "Skipping fmt (no package.json)"; fi

typecheck: ## Run TypeScript type checking
	@if [ -f "package.json" ]; then pnpm typecheck; else echo "Skipping typecheck (no package.json)"; fi

test: ## Run tests
	@if [ -f "package.json" ]; then pnpm test; else echo "Skipping test (no package.json)"; fi

check: ## Run all required quality gates
	@if [ -f "package.json" ]; then pnpm check; else echo "Skipping check (no package.json)"; fi

# === Security ===

audit: ## Run security audit
	@if [ -f "package.json" ]; then pnpm audit; else echo "Skipping audit (no package.json)"; fi

secrets: ## Scan for secrets with gitleaks
	@gitleaks detect --source . --verbose || (echo "Install gitleaks: brew install gitleaks" && exit 1)

security: audit secrets ## Run all security checks

# === Maintenance ===

clean: ## Clean build artifacts and caches
	rm -rf dist coverage artifacts .test-traces* .traces
	rm -rf node_modules/.cache

reset: clean ## Full reset: clean and reinstall
	pnpm install

# === CI ===

ci: ## Run CI-equivalent local checks
	@# Skills/config repos don't have application code
	if [ -f "package.json" ]; then \
		pnpm check; \
	else \
		echo "Skipping pnpm check (skills/config repository - no application code)"; \
		$(MAKE) preflight; \
		$(MAKE) env-check; \
		$(MAKE) lint; \
		$(MAKE) docs-lint; \
		$(MAKE) security; \
	fi

# === Diagrams ===

diagrams: ## Generate architecture diagrams
	@bash ./Infrastructure/scripts/refresh-diagram-context.sh --force

# === Environment ===

env-check: ## Check environment policy envelope
	@bash ./Infrastructure/scripts/check-environment.sh
