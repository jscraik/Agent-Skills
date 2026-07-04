#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { relative, resolve } from "node:path";
import ts from "typescript";
import { collectChangedPaths } from "./lib/changed-files.mjs";

const SOURCE_EXTENSIONS = /\.(ts|tsx|js|jsx|mts|cts)$/;
const TYPE_DECLARATION = /\.d\.ts$/;
const TEST_SOURCE = /([./](?:__tests__|test|tests)[./]|\.test\.|\.spec\.)/;
const PROD_SOURCE_PREFIX = "src/";
const BASELINE_PATH = "contracts/code-quality-debt-baseline.json";
const MAX_FILE_LINES = 400;
const MAX_FUNCTION_LINES = 80;
const MAX_COMPLEXITY = 10;
const MAX_TEST_FILE_LINES = 1_200;
const LEGACY_PRODUCTION_FILE_LINE_ALLOWLIST = new Set([
	// Existing monolithic contract surface; keep narrow while contract types are split down.
	"src/lib/contract/types-core.ts",
]);
const LEGACY_TEST_FILE_LINE_ALLOWLIST = new Set([
	"src/commands/branch-protect.test.ts",
	"src/commands/init.test.ts",
	// Temporary while prompt-context recovery cases are being split out; remove when this file is below MAX_TEST_FILE_LINES.
	"src/commands/next.test.ts",
	"src/cli-dispatch.test.ts",
	"src/lib/architecture/module-boundaries.test.ts",
	"src/lib/cli/command-registry.test.ts",
]);

const args = new Set(process.argv.slice(2));
const repoRoot = resolve(process.cwd());
const modeAll = args.has("--all");
const modeStaged = args.has("--staged");
const json = args.has("--json");

function isProductionSource(path) {
	return (
		path.startsWith(PROD_SOURCE_PREFIX) &&
		SOURCE_EXTENSIONS.test(path) &&
		!TYPE_DECLARATION.test(path) &&
		!TEST_SOURCE.test(path) &&
		existsSync(resolve(repoRoot, path))
	);
}

function isTestSource(path) {
	return (
		path.startsWith(PROD_SOURCE_PREFIX) &&
		SOURCE_EXTENSIONS.test(path) &&
		TEST_SOURCE.test(path) &&
		existsSync(resolve(repoRoot, path))
	);
}

function getScriptKind(path) {
	if (path.endsWith(".tsx")) {
		return ts.ScriptKind.TSX;
	}
	if (path.endsWith(".jsx")) {
		return ts.ScriptKind.JSX;
	}
	if (path.endsWith(".js")) {
		return ts.ScriptKind.JS;
	}

	if (path.endsWith(".mts") || path.endsWith(".cts")) {
		return ts.ScriptKind.TS;
	}

	return ts.ScriptKind.TS;
}

function lineFor(sourceFile, position) {
	return sourceFile.getLineAndCharacterOfPosition(position).line + 1;
}

function functionName(node) {
	if ("name" in node && node.name && ts.isIdentifier(node.name)) {
		return node.name.text;
	}
	const parent = node.parent;
	if (
		ts.isVariableDeclaration(parent) &&
		parent.name &&
		ts.isIdentifier(parent.name)
	) {
		return parent.name.text;
	}
	if (
		ts.isPropertyAssignment(parent) &&
		parent.name &&
		ts.isIdentifier(parent.name)
	) {
		return parent.name.text;
	}
	return "<anonymous>";
}

function countLogicalLines(sourceText) {
	if (sourceText.length === 0) {
		return 0;
	}
	return sourceText.replace(/\r?\n$/, "").split(/\r?\n/).length;
}

function isFunctionLike(node) {
	return (
		ts.isFunctionDeclaration(node) ||
		ts.isFunctionExpression(node) ||
		ts.isArrowFunction(node) ||
		ts.isMethodDeclaration(node) ||
		ts.isConstructorDeclaration(node) ||
		ts.isGetAccessorDeclaration(node) ||
		ts.isSetAccessorDeclaration(node)
	);
}

function nodeComplexityIncrement(node) {
	if (
		ts.isIfStatement(node) ||
		ts.isForStatement(node) ||
		ts.isForInStatement(node) ||
		ts.isForOfStatement(node) ||
		ts.isWhileStatement(node) ||
		ts.isDoStatement(node) ||
		ts.isCaseClause(node) ||
		ts.isDefaultClause(node) ||
		ts.isConditionalExpression(node) ||
		ts.isCatchClause(node)
	) {
		return 1;
	}
	if (
		ts.isBinaryExpression(node) &&
		(node.operatorToken.kind === ts.SyntaxKind.AmpersandAmpersandToken ||
			node.operatorToken.kind === ts.SyntaxKind.BarBarToken)
	) {
		return 1;
	}
	return 0;
}

function functionComplexity(node) {
	let complexity = 1;
	function visit(child) {
		if (child !== node && isFunctionLike(child)) {
			return;
		}
		complexity += nodeComplexityIncrement(child);
		ts.forEachChild(child, visit);
	}
	ts.forEachChild(node, visit);
	return complexity;
}

function debtIdForFinding(finding) {
	if (finding.kind === "file_lines") {
		return `oversized_file:${finding.path}`;
	}
	if (finding.kind === "function_lines") {
		return `oversized_function:${finding.path}:${finding.symbol}`;
	}
	if (finding.kind === "function_complexity") {
		return `high_complexity_function:${finding.path}:${finding.symbol}`;
	}
	return null;
}

function readBaselineDebtIds() {
	const baselineFile = resolve(repoRoot, BASELINE_PATH);
	if (!existsSync(baselineFile)) return new Set();
	let parsed;
	try {
		parsed = JSON.parse(readFileSync(baselineFile, "utf8"));
	} catch (error) {
		console.error(
			`[check-code-size] failed to parse ${BASELINE_PATH}: ${error.message}`,
		);
		return new Set();
	}
	const entries = Array.isArray(parsed.entries) ? parsed.entries : [];
	return new Set(
		entries
			.map((entry) => (typeof entry.id === "string" ? entry.id : null))
			.filter(Boolean),
	);
}

function checkFile(path) {
	const absolutePath = resolve(repoRoot, path);
	const sourceText = readFileSync(absolutePath, "utf8");
	const sourceFile = ts.createSourceFile(
		path,
		sourceText,
		ts.ScriptTarget.Latest,
		true,
		getScriptKind(path),
	);
	const findings = [];

	const fileLines = countLogicalLines(sourceText);
	if (
		fileLines > MAX_FILE_LINES &&
		!LEGACY_PRODUCTION_FILE_LINE_ALLOWLIST.has(path)
	) {
		findings.push({
			kind: "file_lines",
			path,
			line: 1,
			actual: fileLines,
			max: MAX_FILE_LINES,
			message: `file has ${fileLines} lines; max is ${MAX_FILE_LINES}`,
		});
	}

	function visit(node) {
		if (isFunctionLike(node)) {
			const startLine = lineFor(sourceFile, node.getStart(sourceFile));
			const endLine = lineFor(sourceFile, node.getEnd());
			const span = endLine - startLine + 1;
			if (span > MAX_FUNCTION_LINES) {
				findings.push({
					kind: "function_lines",
					path,
					line: startLine,
					symbol: functionName(node),
					actual: span,
					max: MAX_FUNCTION_LINES,
					message: `${functionName(node)} has ${span} lines; max is ${MAX_FUNCTION_LINES}`,
				});
			}
			const complexity = functionComplexity(node);
			if (complexity > MAX_COMPLEXITY) {
				findings.push({
					kind: "function_complexity",
					path,
					line: startLine,
					symbol: functionName(node),
					actual: complexity,
					max: MAX_COMPLEXITY,
					message: `${functionName(node)} has complexity ${complexity}; max is ${MAX_COMPLEXITY}`,
				});
			}
		}
		ts.forEachChild(node, visit);
	}

	visit(sourceFile);
	return {
		findings,
	};
}

const changedPaths = collectChangedPaths({ repoRoot, modeAll, modeStaged });
const files = changedPaths
	.filter(isProductionSource)
	.sort((a, b) => a.localeCompare(b));
const testFiles = changedPaths
	.filter(isTestSource)
	.sort((a, b) => a.localeCompare(b));

if (files.length === 0 && !json) {
	console.info("[check-code-size] no changed production source files.");
}

const baselineDebtIds = readBaselineDebtIds();
const findings = [];
for (const path of files) {
	const result = checkFile(path);
	findings.push(...result.findings);
}
let checkedTestFiles = 0;
for (const path of testFiles) {
	if (LEGACY_TEST_FILE_LINE_ALLOWLIST.has(path)) {
		if (!json)
			console.info(
				`[check-code-size] skipped legacy oversized test file: ${path}`,
			);
		continue;
	}
	checkedTestFiles += 1;
	const fileLines = countLogicalLines(
		readFileSync(resolve(repoRoot, path), "utf8"),
	);
	if (fileLines > MAX_TEST_FILE_LINES) {
		findings.push({
			kind: "test_file_lines",
			path,
			line: 1,
			actual: fileLines,
			max: MAX_TEST_FILE_LINES,
			message: `test file has ${fileLines} lines; max is ${MAX_TEST_FILE_LINES}`,
		});
	}
}

const unbaselinedFindings = findings.filter((finding) => {
	const debtId = debtIdForFinding(finding);
	return debtId === null || !baselineDebtIds.has(debtId);
});

if (unbaselinedFindings.length > 0) {
	if (json) {
		console.info(
			JSON.stringify(
				{
					schemaVersion: "quality-size/v1",
					status: "fail",
					checkedProductionFiles: files.length,
					checkedTestFiles,
					findings: unbaselinedFindings,
				},
				null,
				2,
			),
		);
	} else {
		console.error("[check-code-size] code size limits exceeded:");
		for (const finding of unbaselinedFindings) {
			console.error(
				`  ${relative(repoRoot, resolve(repoRoot, finding.path))}:${finding.line} ${finding.message}`,
			);
		}
	}
	process.exitCode = 1;
} else if (json) {
	console.info(
		JSON.stringify(
			{
				schemaVersion: "quality-size/v1",
				status: "pass",
				checkedProductionFiles: files.length,
				checkedTestFiles,
				findings: [],
				baselinedFindings: findings.length,
			},
			null,
			2,
		),
	);
} else {
	console.info(
		`[check-code-size] checked ${files.length} production file(s), reviewed ${checkedTestFiles} test file(s); size and complexity limits passed (${findings.length} baselined finding(s) suppressed).`,
	);
}
