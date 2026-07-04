#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { relative, resolve } from "node:path";
import ts from "typescript";
import { collectChangedPaths } from "./lib/changed-files.mjs";

const SOURCE_EXTENSIONS = /\.(ts|tsx|js|jsx|mts|cts)$/;
const TEST_OR_TYPE_DECLARATION =
	/(\.d\.ts|[./](?:__tests__|test|tests)[./]|\.test\.|\.spec\.)/;
const PROD_SOURCE_PREFIX = "src/";

const args = new Set(process.argv.slice(2));
const repoRoot = resolve(process.cwd());
const modeAll = args.has("--all");
const modeStaged = args.has("--staged");
const coverageThreshold = Number.parseFloat(
	process.env.DOCSTRING_COVERAGE_THRESHOLD ?? "80",
);
if (
	!Number.isFinite(coverageThreshold) ||
	coverageThreshold < 0 ||
	coverageThreshold > 100
) {
	console.error(
		`[check-public-api-docs] invalid DOCSTRING_COVERAGE_THRESHOLD: ${String(process.env.DOCSTRING_COVERAGE_THRESHOLD ?? "80")}`,
	);
	process.exit(1);
}

function isProductionSource(path) {
	return (
		path.startsWith(PROD_SOURCE_PREFIX) &&
		SOURCE_EXTENSIONS.test(path) &&
		!TEST_OR_TYPE_DECLARATION.test(path) &&
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
	return ts.ScriptKind.TS;
}

function hasExportModifier(node) {
	return Boolean(
		node.modifiers?.some(
			(modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword,
		),
	);
}

function hasJSDoc(sourceText, node) {
	const ranges =
		ts.getLeadingCommentRanges(sourceText, node.getFullStart()) ?? [];
	return ranges.some((range) =>
		sourceText.slice(range.pos, range.end).trimStart().startsWith("/**"),
	);
}

function runGit(args, { allowFailure = false } = {}) {
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

function addDiffLines(output, changedLines) {
	for (const line of output.split(/\r?\n/)) {
		const match = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@/.exec(line);
		if (!match) {
			continue;
		}
		const start = Number.parseInt(match[1], 10);
		const count = match[2] ? Number.parseInt(match[2], 10) : 1;
		if (count === 0) {
			changedLines.add(Math.max(1, start));
			continue;
		}
		for (let offset = 0; offset < count; offset += 1) {
			changedLines.add(start + offset);
		}
	}
}

function resolveBranchDiffBase() {
	for (const ref of ["origin/main", "main"]) {
		const base = runGit(["merge-base", "HEAD", ref], {
			allowFailure: true,
		}).trim();
		if (base) {
			return base;
		}
	}
	return runGit(["rev-parse", "--verify", "HEAD^"], {
		allowFailure: true,
	}).trim();
}

function changedLinesFor(path, sourceFile) {
	if (modeAll) {
		return null;
	}

	const changedLines = new Set();
	const diffModes = modeStaged
		? [["diff", "--cached", "--unified=0", "--", path]]
		: [
				["diff", "--cached", "--unified=0", "--", path],
				["diff", "--unified=0", "--", path],
			];

	for (const gitArgs of diffModes) {
		addDiffLines(
			runGit(gitArgs, {
				allowFailure: true,
			}),
			changedLines,
		);
	}

	if (!modeStaged) {
		const base = resolveBranchDiffBase();
		if (base) {
			addDiffLines(
				runGit(["diff", "--unified=0", `${base}...HEAD`, "--", path], {
					allowFailure: true,
				}),
				changedLines,
			);
		}
	}

	const tracked = runGit(["ls-files", "--error-unmatch", path], {
		allowFailure: true,
	}).trim();
	if (!tracked) {
		const finalLine =
			sourceFile.getLineAndCharacterOfPosition(sourceFile.end).line + 1;
		for (let line = 1; line <= finalLine; line += 1) {
			changedLines.add(line);
		}
	}

	return changedLines;
}

function lineFor(sourceFile, node) {
	return (
		sourceFile.getLineAndCharacterOfPosition(node.getStart(sourceFile)).line + 1
	);
}

function endLineFor(sourceFile, node) {
	return sourceFile.getLineAndCharacterOfPosition(node.getEnd()).line + 1;
}

function fullStartLineFor(sourceFile, node) {
	return sourceFile.getLineAndCharacterOfPosition(node.getFullStart()).line + 1;
}

function lineRangeTouches(changedLines, startLine, endLine) {
	if (!changedLines) {
		return true;
	}
	for (let line = startLine; line <= endLine; line += 1) {
		if (changedLines.has(line)) {
			return true;
		}
	}
	return false;
}

function declarationName(node) {
	if ("name" in node && node.name && ts.isIdentifier(node.name)) {
		return node.name.text;
	}
	return "<anonymous export>";
}

function exportedVariableFunctionDeclarations(statement) {
	if (!ts.isVariableStatement(statement) || !hasExportModifier(statement)) {
		return [];
	}

	return statement.declarationList.declarations.filter((declaration) => {
		const initializer = declaration.initializer;
		return (
			initializer &&
			(ts.isArrowFunction(initializer) ||
				ts.isFunctionExpression(initializer) ||
				ts.isClassExpression(initializer))
		);
	});
}

function variableFunctionDeclarationTarget(statement, declaration) {
	const initializer = declaration.initializer;
	if (
		!initializer ||
		!(
			ts.isArrowFunction(initializer) ||
			ts.isFunctionExpression(initializer) ||
			ts.isClassExpression(initializer)
		)
	) {
		return null;
	}
	return {
		docNode: statement,
		node: declaration,
		name: ts.isIdentifier(declaration.name)
			? declaration.name.text
			: "<destructured function>",
	};
}

function collectFunctionDocTargets(sourceFile) {
	const targets = [];

	function visit(node) {
		if (
			ts.isFunctionDeclaration(node) ||
			ts.isMethodDeclaration(node) ||
			ts.isConstructorDeclaration(node) ||
			ts.isGetAccessorDeclaration(node) ||
			ts.isSetAccessorDeclaration(node)
		) {
			targets.push({
				docNode: node,
				node,
				name: declarationName(node),
			});
		}

		if (ts.isVariableStatement(node)) {
			for (const declaration of node.declarationList.declarations) {
				const target = variableFunctionDeclarationTarget(node, declaration);
				if (target) {
					targets.push(target);
				}
			}
		}

		ts.forEachChild(node, visit);
	}

	visit(sourceFile);
	return targets;
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
	const changedLines = changedLinesFor(path, sourceFile);
	const touchedFunctionTargets = collectFunctionDocTargets(sourceFile).filter(
		(target) =>
			lineRangeTouches(
				changedLines,
				fullStartLineFor(sourceFile, target.docNode),
				endLineFor(sourceFile, target.node),
			),
	);

	for (const statement of sourceFile.statements) {
		if (
			(ts.isFunctionDeclaration(statement) ||
				ts.isClassDeclaration(statement) ||
				ts.isInterfaceDeclaration(statement) ||
				ts.isTypeAliasDeclaration(statement) ||
				ts.isEnumDeclaration(statement)) &&
			hasExportModifier(statement) &&
			!hasJSDoc(sourceText, statement)
		) {
			findings.push({
				path,
				line: lineFor(sourceFile, statement),
				name: declarationName(statement),
			});
		}

		for (const declaration of exportedVariableFunctionDeclarations(statement)) {
			if (!hasJSDoc(sourceText, statement)) {
				const name = ts.isIdentifier(declaration.name)
					? declaration.name.text
					: "<destructured export>";
				findings.push({
					path,
					line: lineFor(sourceFile, declaration),
					name,
				});
			}
		}
	}

	const documentedTouchedFunctions = touchedFunctionTargets.filter((target) =>
		hasJSDoc(sourceText, target.docNode),
	);
	const coverage =
		touchedFunctionTargets.length === 0
			? 100
			: (documentedTouchedFunctions.length / touchedFunctionTargets.length) *
				100;
	const coverageFindings =
		touchedFunctionTargets.length > 0 && coverage < coverageThreshold
			? touchedFunctionTargets
					.filter((target) => !hasJSDoc(sourceText, target.docNode))
					.map((target) => ({
						path,
						line: lineFor(sourceFile, target.node),
						name: target.name,
					}))
			: [];

	return {
		coverage,
		coverageFindings,
		documentedTouchedFunctions: documentedTouchedFunctions.length,
		findings,
		touchedFunctionCount: touchedFunctionTargets.length,
	};
}

const files = collectChangedPaths({ repoRoot, modeAll, modeStaged })
	.filter(isProductionSource)
	.sort((a, b) => a.localeCompare(b));

if (files.length === 0) {
	console.info("[check-public-api-docs] no changed production source files.");
	process.exit(0);
}

const results = files.map(checkFile);
const findings = results.flatMap((result) => result.findings);
const coverageFindings = results.flatMap((result) => result.coverageFindings);
if (findings.length > 0) {
	console.error(
		"[check-public-api-docs] exported public API declarations need JSDoc:",
	);
	for (const finding of findings) {
		console.error(
			`  ${relative(repoRoot, resolve(repoRoot, finding.path))}:${finding.line} ${finding.name}`,
		);
	}
	process.exit(1);
}

if (coverageFindings.length > 0) {
	const touchedFunctionCount = results.reduce(
		(total, result) => total + result.touchedFunctionCount,
		0,
	);
	const documentedTouchedFunctions = results.reduce(
		(total, result) => total + result.documentedTouchedFunctions,
		0,
	);
	const coverage =
		touchedFunctionCount === 0
			? 100
			: (documentedTouchedFunctions / touchedFunctionCount) * 100;
	console.error(
		`[check-public-api-docs] touched function JSDoc coverage ratchet failed; aggregate coverage is ${coverage.toFixed(2)}%, and each changed production file must meet ${coverageThreshold.toFixed(2)}%:`,
	);
	for (const finding of coverageFindings) {
		console.error(
			`  ${relative(repoRoot, resolve(repoRoot, finding.path))}:${finding.line} ${finding.name}`,
		);
	}
	process.exit(1);
}

console.info(
	`[check-public-api-docs] checked ${files.length} file(s); exported public API docs present.`,
);
