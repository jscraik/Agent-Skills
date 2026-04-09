# Harness Development Makefile
# Run `make help` to see available commands

.PHONY: help install setup preflight hooks hooks-pre-commit hooks-pre-push secrets-staged docs-style-changed related-tests semgrep-changed diagrams-check dev build lint docs-lint fmt typecheck test check audit secrets security clean reset ci diagrams env-check

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
	@bash ./scripts/codex-preflight.sh

hooks: ## Setup git hooks
	node scripts/setup-git-hooks.js

hooks-pre-commit: ## Run local pre-commit gates before creating a commit
	pnpm lint
	pnpm docs:lint
	pnpm typecheck
	$(MAKE) secrets-staged
	$(MAKE) docs-style-changed
	$(MAKE) related-tests

hooks-pre-push: ## Run local pre-push governance gates before pushing
	pnpm exec tsx src/cli.ts docs-gate --mode required --json
	@bash ./scripts/check-diagram-freshness.sh
	pnpm exec tsx src/cli.ts tooling-audit --path . --json
	@bash ./scripts/check-environment.sh
	$(MAKE) semgrep-changed
	pnpm test
	pnpm build
	pnpm audit

secrets-staged: ## Scan staged content for secrets before committing
	pnpm run secrets:staged

docs-style-changed: ## Run Vale on staged authoritative docs only
	pnpm run docs:style:changed

related-tests: ## Run Vitest related mode for staged src implementation files
	pnpm run test:related

semgrep-changed: ## Run narrow Semgrep rules against changed src implementation files
	pnpm run semgrep:changed

diagrams-check: ## Refresh architecture diagrams when sensitive paths change and fail on drift
	@bash ./scripts/check-diagram-freshness.sh

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
	@bash ./scripts/refresh-diagram-context.sh --force

# === Environment ===

env-check: ## Check environment policy envelope
	@bash ./scripts/check-environment.sh
