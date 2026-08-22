#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { collectChangedPaths } from "./lib/changed-files.mjs";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const args = new Set(process.argv.slice(2));
const supportedArgs = new Set(["--all", "--staged"]);
const unsupportedArgs = [...args].filter((arg) => !supportedArgs.has(arg));
if (unsupportedArgs.length > 0) {
	console.error(
		`[structural-validation] unsupported argument(s): ${unsupportedArgs.join(", ")}`,
	);
	process.exit(2);
}

if (args.has("--all") && args.has("--staged")) {
	console.error("[structural-validation] --all and --staged are mutually exclusive");
	process.exit(2);
}

const stagedSource = args.has("--staged");
const changedPaths = collectChangedPaths({
	repoRoot,
	modeAll: args.has("--all"),
	modeStaged: stagedSource,
}).filter((path) => path.endsWith(".py"));
const structuralChecks = [
	{
		path: "scripts/validation-and-linting/verify_ask_cli_modularity.py",
		stagedSource: true,
	},
	{
		path: "scripts/validation-and-linting/verify_program_design.py",
		stagedSource: true,
	},
];

for (const check of structuralChecks) {
	const checkArgs = [
		"Infrastructure/scripts/run-infrastructure-python.sh",
		check.path,
		"--changed-files",
		...changedPaths,
	];
	if (stagedSource && check.stagedSource) {
		checkArgs.push("--staged-source");
	}
	const result = spawnSync(
		"bash",
		checkArgs,
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
