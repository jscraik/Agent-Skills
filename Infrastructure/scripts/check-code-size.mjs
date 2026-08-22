#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const structuralChecks = [
	"scripts/validation-and-linting/verify_ask_cli_modularity.py",
	"scripts/validation-and-linting/verify_program_design.py",
];

for (const check of structuralChecks) {
	const result = spawnSync(
		"bash",
		["Infrastructure/scripts/run-infrastructure-python.sh", check],
		{ cwd: repoRoot, stdio: "inherit" },
	);
	if (result.error) {
		console.error(`[structural-validation] ${result.error.message}`);
		process.exit(1);
	}
	if (result.status !== 0) {
		process.exit(result.status ?? 1);
	}
}
