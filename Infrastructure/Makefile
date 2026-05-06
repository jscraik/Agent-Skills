.PHONY: hooks-pre-commit hooks-commit-msg hooks-pre-push

hooks-pre-commit:
	$(MAKE) -C .. hooks-pre-commit

hooks-commit-msg:
	@if [ -z "$(HOOK_COMMIT_MSG_FILE)" ]; then \
		echo "Error: HOOK_COMMIT_MSG_FILE is required"; \
		exit 2; \
	fi
	@repo_root="$$(git -C "$(CURDIR)/.." rev-parse --show-toplevel)"; \
	hook_file="$(HOOK_COMMIT_MSG_FILE)"; \
	case "$$hook_file" in \
	/*) ;; \
	*) hook_file="$(CURDIR)/../$$hook_file" ;; \
	esac; \
	if [ ! -f "$$hook_file" ] && [ "$$(basename "$$hook_file")" = "COMMIT_EDITMSG" ]; then \
		hook_file="$$(git -C "$$repo_root" rev-parse --path-format=absolute --git-path COMMIT_EDITMSG)"; \
	fi; \
	if [ ! -f "$$hook_file" ]; then \
		echo "Error: commit message file not found: $$hook_file"; \
		exit 2; \
	fi; \
	$(MAKE) -C "$$repo_root" hooks-commit-msg HOOK_COMMIT_MSG_FILE="$$hook_file"

hooks-pre-push:
	$(MAKE) -C .. hooks-pre-push
