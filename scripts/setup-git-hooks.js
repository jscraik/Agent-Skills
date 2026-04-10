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

function readLegacyLocalHooksPath() {
	return tryRead("git", ["config", "--local", "--get", "core.hooksPath"]);
}

function clearLegacyLocalHooksPath(configuredPath) {
	if (!configuredPath) {
		return;
	}

	console.info(`Removing legacy local core.hooksPath: ${configuredPath}`);
	execFileSync("git", ["config", "--local", "--unset", "core.hooksPath"], {
		stdio: "ignore",
	});
}

function restoreLegacyLocalHooksPath(configuredPath) {
	if (!configuredPath) {
		return;
	}
	execFileSync("git", ["config", "--local", "core.hooksPath", configuredPath], {
		stdio: "ignore",
	});
}

function main() {
	const legacyHooksPath = readLegacyLocalHooksPath();
	clearLegacyLocalHooksPath(legacyHooksPath);

	try {
		execFileSync("prek", ["install"], { stdio: "inherit" });
		console.info("Installed canonical prek hooks");
	} catch (error) {
		try {
			restoreLegacyLocalHooksPath(legacyHooksPath);
		} catch {
			console.error("Error: failed to restore previous core.hooksPath after hook install failure.");
		}

		if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
			console.error("Error: `prek` is not available; hook installation failed.");
			console.error("Install `prek` and re-run scripts/setup-git-hooks.js.");
		} else {
			console.error("Error: `prek install` failed.");
		}
		process.exit(1);
	}
}

main();
