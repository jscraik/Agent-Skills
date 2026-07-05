#!/usr/bin/env node
import { execFileSync } from "node:child_process";

function runGit(repoRoot, args, { allowFailure = false } = {}) {
	try {
		return execFileSync("git", args, {
			cwd: repoRoot,
			encoding: "utf8",
			stdio: ["ignore", "pipe", "ignore"],
		});
	} catch (error) {
		if (allowFailure) {
			return "";
		}
		const detail = error instanceof Error ? `: ${error.message}` : "";
		throw new Error(`git ${args.join(" ")} failed${detail}`);
	}
}

function splitGitPaths(output) {
	return output.split(/\r?\n/).filter(Boolean);
}

function resolveBranchDiffBase(repoRoot) {
	const candidates = ["origin/main", "main"];
	for (const ref of candidates) {
		const base = runGit(repoRoot, ["merge-base", "HEAD", ref], {
			allowFailure: true,
		}).trim();
		if (base) {
			return base;
		}
	}

	return runGit(repoRoot, ["rev-parse", "--verify", "HEAD^"], {
		allowFailure: true,
	}).trim();
}

/**
 * Collects the same changed-file set used by local quality gates.
 *
 * The default mode includes staged, unstaged, and branch-vs-main files so agents
 * cannot accidentally pass a narrow check after touching related files earlier
 * in the branch.
 *
 * @param {{
 *   repoRoot: string;
 *   modeAll?: boolean;
 *   modeStaged?: boolean;
 * }} options
 * @returns {string[]}
 */
export function collectChangedPaths({
	repoRoot,
	modeAll = false,
	modeStaged = false,
}) {
	if (modeAll) {
		return splitGitPaths(runGit(repoRoot, ["ls-files"]));
	}

	const paths = new Set();
	const diffModes = modeStaged
		? [["diff", "--cached", "--name-only", "--diff-filter=ACMR"]]
		: [
				["diff", "--cached", "--name-only", "--diff-filter=ACMR"],
				["diff", "--name-only", "--diff-filter=ACMR"],
				["ls-files", "--others", "--exclude-standard"],
			];

	for (const gitArgs of diffModes) {
		for (const path of splitGitPaths(runGit(repoRoot, gitArgs))) {
			paths.add(path);
		}
	}

	if (!modeStaged) {
		const base = resolveBranchDiffBase(repoRoot);
		if (base) {
			for (const path of splitGitPaths(
				runGit(repoRoot, [
					"diff",
					"--name-only",
					"--diff-filter=ACMR",
					`${base}...HEAD`,
				]),
			)) {
				paths.add(path);
			}
		} else {
			for (const path of splitGitPaths(runGit(repoRoot, ["ls-files"]))) {
				paths.add(path);
			}
		}
	}

	return [...paths];
}
