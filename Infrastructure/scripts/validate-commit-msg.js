#!/usr/bin/env node
/**
 * Commit message validation hook
 *
 * Validates commit messages follow governance requirements:
 * - Conventional commit format (feat|fix|chore|docs|refactor|test|style)
 * - Subject line <= 72 chars
 * - Blank line between subject and body/trailers
 * - Co-authored-by trailer on agent branches
 */

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const COMMIT_MSG_FILE = process.argv[2];
const CONVENTIONAL_COMMIT_REGEX =
	/^(feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert)(\(.+\))?!?:\s.+/;
const CO_AUTHOR_LINE_REGEX = /^Co-authored-by:\s*.+$/gim;
const CODEX_CO_AUTHOR_REGEX =
	/^Co-authored-by:\s*Codex <noreply@openai\.com>\s*$/im;

function main() {
	if (!COMMIT_MSG_FILE) {
		console.error("Usage: validate-commit-msg.js <commit-msg-file>");
		process.exit(1);
	}

	let commitMsg;
	try {
		commitMsg = readFileSync(COMMIT_MSG_FILE, "utf-8");
	} catch (e) {
		console.error(`Failed to read commit message file: ${e.message}`);
		process.exit(1);
	}

	const errors = [];
	const lines = commitMsg
		.split(/\r?\n/)
		.filter((line) => !line.startsWith("#"));
	const firstLineIndex = lines.findIndex((line) => line.trim().length > 0);
	const firstLine = firstLineIndex >= 0 ? lines[firstLineIndex].trim() : "";

	// Check 1: Subject exists and follows conventional commit format
	if (!firstLine) {
		errors.push("Commit message subject is required");
	} else if (!CONVENTIONAL_COMMIT_REGEX.test(firstLine)) {
		errors.push(
			"Subject must follow conventional commit format: type(scope)!: description",
		);
	}

	// Check 2: Subject length
	if (firstLine && firstLine.length > 72) {
		errors.push(`Subject exceeds 72 characters (${firstLine.length} chars)`);
	}

	// Check 3: Body/trailers must be separated by a blank line
	const hasAdditionalContent = lines
		.slice(Math.max(firstLineIndex + 1, 0))
		.some((line) => line.trim().length > 0);
	if (hasAdditionalContent && lines[firstLineIndex + 1]?.trim() !== "") {
		errors.push(
			"Add a blank line between the subject and the rest of the commit message",
		);
	}

	// Check 4: Co-authorship for agent branches (enforced)
	const coAuthorLines = commitMsg.match(CO_AUTHOR_LINE_REGEX) ?? [];
	const branchName = getBranchName();
	const isAgentBranch = /codex|claude|agent/i.test(branchName);

	if (isAgentBranch && coAuthorLines.length !== 1) {
		errors.push(
			"Agent branches require exactly one Co-authored-by trailer for auditability",
		);
	}
	if (isAgentBranch && !CODEX_CO_AUTHOR_REGEX.test(commitMsg)) {
		errors.push(
			"Agent branches must include: Co-authored-by: Codex <noreply@openai.com>",
		);
	}

	// Output results
	if (errors.length > 0) {
		console.error("\n❌ Commit message validation failed:\n");
		for (const error of errors) {
			console.error(`  ✗ ${error}`);
		}
		console.error(
			"\nCommit message format example:\n  feat(scope): add new feature\n\n  Why this change is needed and what it impacts.\n\n  Co-authored-by: Codex <noreply@openai.com>",
		);
		process.exit(1);
	}
	process.exit(0);
}

function getBranchName() {
	try {
		// Using execFileSync for safety - no shell interpolation
		const output = execFileSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], {
			encoding: "utf-8",
			stdio: ["pipe", "pipe", "pipe"],
		});
		return output.trim();
	} catch {
		return "";
	}
}

main();
		