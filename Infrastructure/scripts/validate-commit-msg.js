#!/usr/bin/env node
/**
 * Commit message validation hook
 *
 * Validates commit messages follow governance requirements:
 * - Conventional commit format (feat|fix|chore|docs|refactor|test|style)
 * - Co-authorship for AI-generated code
 * - PR template completion reminder for agent branches
 */

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const COMMIT_MSG_FILE = process.argv[2];
const CONVENTIONAL_COMMIT_REGEX =
	/^(feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert)(\(.+\))?!?:\s.+/;
const CO_AUTHOR_REGEX = /Co-Authored-By:\s*.+/i;

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
	const warnings = [];
	const lines = commitMsg
		.split("\n")
		.filter((line) => line && !line.startsWith("#"));

	// Check 1: Conventional commit format
	const firstLine = lines[0];
	if (!CONVENTIONAL_COMMIT_REGEX.test(firstLine)) {
		errors.push(
			"First line must follow conventional commit format: type(scope)!: description",
		);
	}

	// Check 2: First line length
	if (firstLine && firstLine.length > 72) {
		errors.push(`First line exceeds 72 characters (${firstLine.length} chars)`);
	}

	// Check 3: Body paragraphs separated by blank line
	if (lines.length > 1 && lines[1] !== "") {
		warnings.push(
			"Body should be separated from subject by a blank line for readability",
		);
	}

	// Check 4: Co-authorship for AI-assisted commits (warn only)
	const hasCoAuthor = CO_AUTHOR_REGEX.test(commitMsg);
	const branchName = getBranchName();
	const isAgentBranch = /codex|claude|agent/i.test(branchName);

	if (isAgentBranch && !hasCoAuthor) {
		warnings.push(
			"AI-assisted commit detected. Consider adding Co-Authored-By for transparency.",
		);
	}

	// Check 5: PR template reminder for agent branches
	// Note: PR template sections are enforced by PR review workflow, not commit hook
	// Agent branches should follow: Summary, Checklist, Testing, Review artifacts, Notes

	// Output results
	if (errors.length > 0) {
		console.error("\n❌ Commit message validation failed:\n");
		for (const error of errors) {
			console.error(`  ✗ ${error}`);
		}
		console.error(
			"\nCommit message format example:\n  feat(scope): add new feature\n\n  Detailed description here.\n\n  Co-Authored-By: Your Name <email@example.com>",
		);
		process.exit(1);
	}

	if (warnings.length > 0) {
		console.info("\n⚠️  Commit message warnings:\n");
		for (const warning of warnings) {
			console.info(`  • ${warning}`);
		}
		console.info("");
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
