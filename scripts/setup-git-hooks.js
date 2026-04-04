#!/usr/bin/env node
/**
 * Setup git hooks for this configuration-first repository.
 *
 * This repo has no root package manager, so we install hooks directly:
 *   - pre-commit: bash scripts/validate_all.sh --ephemeral
 *   - commit-msg: node scripts/validate-commit-msg.js "$1"
 *   - pre-push:   python3 scripts/diagnose_skill.py --all
 */

import { chmodSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const REPO_ROOT = process.cwd();
const HOOKS_DIR = resolve(REPO_ROOT, ".git", "hooks");

const HOOKS = {
	"pre-commit": `#!/bin/sh
if [ "$SKIP_SIMPLE_GIT_HOOKS" = "1" ]; then
  echo "[INFO] SKIP_SIMPLE_GIT_HOOKS=1, skipping pre-commit."
  exit 0
fi
bash scripts/validate_all.sh --ephemeral
`,
	"commit-msg": `#!/bin/sh
if [ "$SKIP_SIMPLE_GIT_HOOKS" = "1" ]; then
  echo "[INFO] SKIP_SIMPLE_GIT_HOOKS=1, skipping commit-msg."
  exit 0
fi
node scripts/validate-commit-msg.js "$1"
`,
	"pre-push": `#!/bin/sh
if [ "$SKIP_SIMPLE_GIT_HOOKS" = "1" ]; then
  echo "[INFO] SKIP_SIMPLE_GIT_HOOKS=1, skipping pre-push."
  exit 0
fi
python3 scripts/diagnose_skill.py --all
`,
};

function main() {
	if (!existsSync(resolve(REPO_ROOT, ".git"))) {
		console.error("Error: .git directory not found.");
		console.error("Run this script from the repository root.");
		process.exit(1);
	}

	mkdirSync(HOOKS_DIR, { recursive: true });

	for (const [hookName, content] of Object.entries(HOOKS)) {
		const hookPath = resolve(HOOKS_DIR, hookName);
		writeFileSync(hookPath, content);
		chmodSync(hookPath, 0o755);
		console.info(`✓ Installed ${hookName} hook`);
	}

	console.info("\n✓ Git hooks installed for agent-skills");
}

main();
