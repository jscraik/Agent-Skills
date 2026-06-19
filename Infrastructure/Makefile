.PHONY: hooks-pre-commit hooks-commit-msg hooks-pre-push

hooks-pre-commit:
	@bash ../scripts/hooks/pre-commit.sh

hooks-commit-msg:
	@if [ -z "$(HOOK_COMMIT_MSG_FILE)" ]; then \
		echo "Error: HOOK_COMMIT_MSG_FILE is required"; \
		exit 2; \
	fi
	@bash ../scripts/hooks/commit-msg.sh "$(HOOK_COMMIT_MSG_FILE)"

hooks-pre-push:
	@bash ../scripts/hooks/pre-push.sh
