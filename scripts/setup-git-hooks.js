#!/usr/bin/env node
/**
 * Install canonical prek-managed git hooks for this repository.
 */

import { execFileSync } from "node:child_process";

function tryRead(command, args) {
	try {
		return execFileSync(command, args, {
			encoding: "utf8",
			stdio: ["ignore", "pipe", "ignore"],
		}).trim();
	} catch {
		return "";
	}
}

function clearLegacyLocalHooksPath() {
	const configuredPath = tryRead("git", ["config", "--local", "--get", "core.hooksPath"]);
	if (!configuredPath) {
		return;
	}

	console.info(`Removing legacy local core.hooksPath: ${configuredPath}`);
	execFileSync("git", ["config", "--local", "--unset", "core.hooksPath"], {
		stdio: "ignore",
	});
}

function main() {
	clearLegacyLocalHooksPath();

	try {
		execFileSync("prek", ["install"], { stdio: "inherit" });
		console.info("Installed canonical prek hooks");
	} catch {
		console.warn("Warning: `prek` is not available; skipping hook installation.");
		console.warn("Run `prek install` after bootstrapping the repo toolchain.");
	}
}

main();
