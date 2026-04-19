.PHONY: hooks-pre-commit hooks-commit-msg hooks-pre-push

hooks-pre-commit:
	$(MAKE) -C .. hooks-pre-commit

hooks-commit-msg:
	@if [ -z "$(HOOK_COMMIT_MSG_FILE)" ]; then \
		echo "Error: HOOK_COMMIT_MSG_FILE is required"; \
		exit 2; \
	fi
	@hook_file="$(HOOK_COMMIT_MSG_FILE)"; \
	case "$$hook_file" in \
	/*) ;; \
	*) hook_file="$(CURDIR)/../$$hook_file" ;; \
	esac; \
	$(MAKE) -C .. hooks-commit-msg HOOK_COMMIT_MSG_FILE="$$hook_file"

hooks-pre-push:
	$(MAKE) -C .. hooks-pre-push
