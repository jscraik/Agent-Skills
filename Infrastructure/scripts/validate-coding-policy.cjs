#!/usr/bin/env node
const { execFileSync } = require("node:child_process");
const { existsSync, readFileSync } = require("node:fs");
const { join, normalize, sep } = require("node:path");

const repoRoot = process.cwd();
const policyPath = join(repoRoot, "coding-policy.json");
const schemaPath = join(repoRoot, "contracts/coding-policy.schema.json");
const MAX_CHANGED_FILES = 200;
const MAX_ROUTE_PATH_LENGTH = 512;
const MAX_ROUTE_SEGMENTS = 64;
const MAX_CLI_DIAGNOSTIC_CHARS = 240;
const expectedModules = new Map([
	["foundations", "codestyle/01-foundations.md"],
	["docs-config-release", "codestyle/04-docs-config-and-release.md"],
	["quality-security-ops", "codestyle/05-quality-security-ops.md"],
	["python", "codestyle/07-python.md"],
	["typescript", "codestyle/08-typescript.md"],
	["shell", "codestyle/10-shell-bash-zsh.md"],
	["package-managers", "codestyle/11-package-managers-pnpm-npm.md"],
	["git-workflow", "codestyle/13-git-workflow.md"],
	["security", "codestyle/16-security.md"],
	["testing", "codestyle/17-testing.md"],
	["development-workflow", "codestyle/19-development-workflow.md"],
]);
const expectedModuleIds = new Set(expectedModules.keys());
const expectedModulePaths = new Set(expectedModules.values());
const expectedSourceRules = new Set([
	"boy-scout",
	"ci-safety",
	"code-formatting",
	"commit-conventions",
	"context-artifacts",
	"context-writing-style",
	"dependency-management",
	"error-handling",
	"file-hygiene",
	"no-secrets",
	"plugin-evals",
	"rule-frontmatter",
	"script-as-black-box",
	"script-delegation",
	"skill-authoring",
	"stateful-artifacts",
	"sync-before-work",
	"testing-standards",
]);

function parseArgs(argv) {
	const options = {
		json: false,
		changedFiles: [],
		gitBase: null,
		gitChanged: false,
		routeRequested: false,
	};
	const errors = [];
	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		if (arg === "--json") {
			options.json = true;
			continue;
		}
		if (arg === "--git-changed") {
			options.routeRequested = true;
			options.gitChanged = true;
			continue;
		}
		if (arg === "--git-base") {
			const next = argv[index + 1];
			if (next === undefined) {
				errors.push("--git-base requires a ref");
				continue;
			}
			options.routeRequested = true;
			options.gitBase = next;
			index += 1;
			continue;
		}
		if (arg === "--changed-file") {
			const next = argv[index + 1];
			if (next === undefined) {
				errors.push("--changed-file requires a path");
				continue;
			}
			options.routeRequested = true;
			options.changedFiles.push(next);
			index += 1;
			continue;
		}
		if (arg === "--changed-files") {
			options.routeRequested = true;
			const remaining = argv.slice(index + 1);
			if (remaining[0] === "--") {
				options.changedFiles.push(...remaining.slice(1));
			} else {
				options.changedFiles.push(...remaining);
			}
			break;
		}
		if (arg === "--") {
			options.routeRequested = true;
			options.changedFiles.push(...argv.slice(index + 1));
			break;
		}
		errors.push("unknown argument <redacted>");
	}
	if (
		options.routeRequested &&
		!options.gitChanged &&
		options.gitBase === null &&
		options.changedFiles.length === 0
	) {
		errors.push("--changed-files requires at least one path");
	}
	return { options, errors };
}

function sanitizeCliDiagnosticText(
	value,
	maxLength = MAX_CLI_DIAGNOSTIC_CHARS,
) {
	const sanitized = stripCliDiagnosticControls(String(value))
		.replace(/\s+/g, " ")
		.trim()
		.replace(
			/\b([A-Z0-9_]*(?:TOKEN|KEY|SECRET|PASSWORD)[A-Z0-9_]*=)\S+/gi,
			"$1<redacted>",
		)
		.replace(/\b(Bearer|Basic)\s+\S+/gi, "$1 <redacted>");
	if (sanitized.length === 0) return "<empty>";
	if (sanitized.length > maxLength) {
		return `${sanitized.slice(0, maxLength - 3)}...`;
	}
	return sanitized;
}

function stripCliDiagnosticControls(value) {
	let stripped = "";
	for (const character of value) {
		const codePoint = character.codePointAt(0);
		stripped +=
			codePoint !== undefined && (codePoint <= 31 || codePoint === 127)
				? " "
				: character;
	}
	return stripped;
}

function writeStaticStderr(lines) {
	for (const line of lines) {
		process.stderr.write(`${line}\n`);
	}
}

function validationFailurePayload(errors) {
	return {
		schemaVersion: "coding-policy-validation/v1",
		status: "fail",
		errors: errors.map((error) => sanitizeCliDiagnosticText(error)),
	};
}

function writeStaticValidationFailure(options, errors) {
	writeStaticStderr([
		"coding-policy: failed",
		"- policy validation failed; use --json for diagnostics",
	]);
	if (options.json) {
		process.stdout.write(
			`${JSON.stringify(validationFailurePayload(errors), null, 2)}\n`,
		);
	}
}

function writeStaticFailure(options, stderrLines, errors) {
	writeStaticStderr(stderrLines);
	if (options?.json) {
		process.stdout.write(
			`${JSON.stringify(validationFailurePayload(errors), null, 2)}\n`,
		);
	}
}

function requireSafeGitRef(ref, optionName) {
	if (typeof ref !== "string" || ref.trim().length === 0) {
		throw new Error(`${optionName} requires a non-empty ref`);
	}
	if (!/^[A-Za-z0-9._/@-]+$/.test(ref) || ref.startsWith("-")) {
		throw new Error(
			`${optionName} must contain only letters, numbers, dot, slash, underscore, at-sign, or dash`,
		);
	}
	if (
		ref.includes("..") ||
		ref.includes("@{") ||
		ref.endsWith(".") ||
		ref.includes("//") ||
		ref.includes("/.")
	) {
		throw new Error(`${optionName} must be a plain git ref`);
	}
	return ref;
}

function gitBaseChangedFiles(baseRef) {
	const base = requireSafeGitRef(baseRef, "--git-base");
	const output = execFileSync(
		"git",
		["diff", "--name-status", "--diff-filter=ACDMRTUXB", `${base}...HEAD`],
		{
			cwd: repoRoot,
			encoding: "utf8",
			stdio: ["ignore", "pipe", "pipe"],
		},
	);
	return parseGitNameStatus(output);
}

function gitChangedFiles() {
	const files = [];
	for (const args of [
		["diff", "--name-status", "--diff-filter=ACDMRTUXB"],
		["diff", "--cached", "--name-status", "--diff-filter=ACDMRTUXB"],
		["ls-files", "--others", "--exclude-standard"],
	]) {
		const output = execFileSync("git", args, {
			cwd: repoRoot,
			encoding: "utf8",
			stdio: ["ignore", "pipe", "pipe"],
		});
		files.push(
			...(args[0] === "ls-files"
				? output
						.split(/\r?\n/)
						.map((line) => line.trim())
						.filter((line) => line.length > 0)
				: parseGitNameStatus(output)),
		);
	}
	return uniqueStrings(files);
}

function parseGitNameStatus(output) {
	const files = [];
	for (const line of output.split(/\r?\n/)) {
		const columns = line
			.trim()
			.split("\t")
			.map((column) => column.trim())
			.filter((column) => column.length > 0);
		if (columns.length < 2) continue;
		const status = columns[0];
		if (/^[RC]/.test(status) && columns.length >= 3) {
			files.push(columns[1], columns[2]);
			continue;
		}
		files.push(columns[1]);
	}
	return files;
}

function readPolicyJson() {
	return JSON.parse(readFileSync(policyPath, "utf8"));
}

function readSchemaJson() {
	return JSON.parse(readFileSync(schemaPath, "utf8"));
}

function normalizeRepoPath(relativePath) {
	if (typeof relativePath !== "string" || relativePath.trim().length === 0) {
		return "";
	}
	const normalized = normalize(relativePath)
		.replace(/\\/g, "/")
		.replace(/^\.\//, "");
	return normalized === "." ? "" : normalized;
}

function hasParentSegment(relativePath) {
	return relativePath.split(/[\\/]+/).includes("..");
}

function isInsideRepo(relativePath) {
	if (typeof relativePath !== "string") return false;
	const normalized = normalizeRepoPath(relativePath);
	return (
		normalized.length > 0 &&
		!hasParentSegment(relativePath) &&
		!/^[A-Za-z]:\//.test(normalized) &&
		!normalized.startsWith("..") &&
		!normalized.startsWith(sep) &&
		!normalized.startsWith("/")
	);
}

function requireString(value, path, errors) {
	if (typeof value !== "string" || value.trim().length === 0) {
		errors.push(`${path} must be a non-empty string`);
	}
}

function isObject(value) {
	return value !== null && typeof value === "object" && !Array.isArray(value);
}

function requireObject(value, path, errors) {
	if (!isObject(value)) {
		errors.push(`${path} must be an object`);
		return false;
	}
	return true;
}

function requireOnlyKeys(value, allowedKeys, path, errors) {
	if (!requireObject(value, path, errors)) return;
	const allowed = new Set(allowedKeys);
	for (const key of Object.keys(value)) {
		if (!allowed.has(key)) {
			errors.push(`${path} additional property ${key} is not allowed`);
		}
	}
	for (const key of allowedKeys) {
		if (!(key in value)) {
			errors.push(`${path}.${key} is required`);
		}
	}
}

function requireUniqueStrings(values, path, errors) {
	const seen = new Set();
	for (const [index, value] of values.entries()) {
		requireString(value, `${path}[${index}]`, errors);
		if (typeof value !== "string") continue;
		if (seen.has(value)) {
			errors.push(`${path} duplicates ${value}`);
			continue;
		}
		seen.add(value);
	}
}

function requireRepoRelativePattern(pattern, path, errors) {
	requireString(pattern, path, errors);
	if (typeof pattern !== "string") return;
	if (!isInsideRepo(pattern)) {
		errors.push(`${path} must be repo-relative`);
	}
	if (pattern.includes("\\")) {
		errors.push(`${path} must use forward slashes`);
	}
	if (pattern.includes("//")) {
		errors.push(`${path} must not contain empty path segments`);
	}
	validateRoutePathShape(pattern, path, errors);
	for (const segment of normalizeRepoPath(pattern).split("/")) {
		if (segment.includes("**") && segment !== "**") {
			errors.push(`${path} must use ** only as a full path segment`);
		}
	}
}

function validateRoutePathShape(relativePath, path, errors) {
	const normalized = normalizeRepoPath(relativePath);
	if (normalized.length > MAX_ROUTE_PATH_LENGTH) {
		errors.push(`${path} must be at most ${MAX_ROUTE_PATH_LENGTH} characters`);
	}
	if (normalized.split("/").length > MAX_ROUTE_SEGMENTS) {
		errors.push(`${path} must have at most ${MAX_ROUTE_SEGMENTS} segments`);
	}
}

function matchesPattern(relativePath, pattern) {
	const patternSegments = normalizeRepoPath(pattern).split("/");
	const pathSegments = normalizeRepoPath(relativePath).split("/");
	let patternIndex = 0;
	let pathIndex = 0;
	let globstarIndex = -1;
	let globstarPathIndex = 0;
	const maxSteps = (patternSegments.length + 1) * (pathSegments.length + 1);
	let steps = 0;
	while (pathIndex < pathSegments.length) {
		steps += 1;
		if (steps > maxSteps) {
			return false;
		}
		const patternSegment = patternSegments[patternIndex];
		if (patternSegment === "**") {
			globstarIndex = patternIndex;
			globstarPathIndex = pathIndex;
			patternIndex += 1;
			continue;
		}
		if (
			patternSegment !== undefined &&
			matchSegment(patternSegment, pathSegments[pathIndex])
		) {
			patternIndex += 1;
			pathIndex += 1;
			continue;
		}
		if (globstarIndex >= 0) {
			patternIndex = globstarIndex + 1;
			globstarPathIndex += 1;
			pathIndex = globstarPathIndex;
			continue;
		}
		return false;
	}
	return patternSegments
		.slice(patternIndex)
		.every((segment) => segment === "**");
}

function matchSegment(patternSegment, pathSegment) {
	if (patternSegment === "*") return true;
	const parts = patternSegment.split("*");
	if (parts.length === 1) return patternSegment === pathSegment;
	let cursor = 0;
	const first = parts[0] ?? "";
	if (first.length > 0) {
		if (!pathSegment.startsWith(first)) return false;
		cursor = first.length;
	}
	for (let index = 1; index < parts.length; index += 1) {
		const part = parts[index] ?? "";
		if (part.length === 0) continue;
		const found = pathSegment.indexOf(part, cursor);
		if (found === -1) return false;
		cursor = found + part.length;
	}
	const last = parts.at(-1) ?? "";
	return last.length === 0 || pathSegment.endsWith(last);
}

function uniqueStrings(values) {
	return Array.from(new Set(values));
}

function buildPolicyRoute(policy, changedFiles) {
	const normalizedChangedFiles = uniqueStrings(
		changedFiles.map(normalizeRepoPath).filter((file) => file.length > 0),
	);
	const routedModules = [];
	for (const module of policy.policyModules) {
		const matchedFiles = normalizedChangedFiles.filter((file) =>
			module.changedFilePatterns.some((pattern) =>
				matchesPattern(file, pattern),
			),
		);
		if (matchedFiles.length === 0) continue;
		routedModules.push({
			id: module.id,
			path: module.path,
			changedFilePatterns: module.changedFilePatterns,
			sourceRules: module.sourceRules,
			requiredGates: module.requiredGates,
			matchedFiles,
		});
	}
	return {
		schemaVersion: "coding-policy-route/v1",
		policySchemaVersion: policy.schemaVersion,
		authority: policy.authority,
		entrypoints: policy.entrypoints,
		changedFiles: normalizedChangedFiles,
		policyModules: routedModules,
		requiredGates: uniqueStrings(
			routedModules.flatMap((module) => module.requiredGates),
		),
		claimBoundaries: policy.claimBoundaries,
	};
}

function validatePolicy(policy, schema) {
	const errors = [];
	requireOnlyKeys(
		policy,
		[
			"$schema",
			"schemaVersion",
			"authority",
			"entrypoints",
			"policyModules",
			"claimBoundaries",
		],
		"coding-policy",
		errors,
	);
	if (!isObject(policy)) return errors;
	if (policy.$schema !== "./contracts/coding-policy.schema.json") {
		errors.push("$schema must be ./contracts/coding-policy.schema.json");
	}
	if (schema?.additionalProperties !== false) {
		errors.push("schema root must disallow additional properties");
	}
	if (schema?.$defs?.policyModule?.additionalProperties !== false) {
		errors.push("schema policyModule must disallow additional properties");
	}
	if (
		schema?.$defs?.policyModule?.properties?.sourceRules?.uniqueItems !== true
	) {
		errors.push("schema policyModule.sourceRules must be unique");
	}
	if (
		schema?.$defs?.policyModule?.properties?.requiredGates?.uniqueItems !== true
	) {
		errors.push("schema policyModule.requiredGates must be unique");
	}
	if (
		schema?.$defs?.policyModule?.properties?.changedFilePatterns
			?.uniqueItems !== true
	) {
		errors.push("schema policyModule.changedFilePatterns must be unique");
	}
	if (
		!Array.isArray(schema?.$defs?.policyModule?.required) ||
		!schema.$defs.policyModule.required.includes("changedFilePatterns")
	) {
		errors.push("schema policyModule.changedFilePatterns must be required");
	}
	if (
		schema?.$defs?.policyModule?.properties?.changedFilePatterns?.minItems !== 1
	) {
		errors.push("schema policyModule.changedFilePatterns must be non-empty");
	}
	if (
		schema?.$defs?.policyModule?.properties?.changedFilePatterns?.items
			?.type !== "string"
	) {
		errors.push(
			"schema policyModule.changedFilePatterns items must be strings",
		);
	}
	if (policy?.schemaVersion !== "harness-coding-policy/v1") {
		errors.push("schemaVersion must be harness-coding-policy/v1");
	}
	if (policy?.authority !== "canonical") {
		errors.push("authority must be canonical");
	}
	requireOnlyKeys(
		policy.entrypoints,
		["human", "machine", "modules"],
		"entrypoints",
		errors,
	);
	if (policy?.entrypoints?.human !== "CODESTYLE.md") {
		errors.push("entrypoints.human must be CODESTYLE.md");
	}
	if (policy?.entrypoints?.machine !== "coding-policy.json") {
		errors.push("entrypoints.machine must be coding-policy.json");
	}
	if (policy?.entrypoints?.modules !== "codestyle/README.md") {
		errors.push("entrypoints.modules must be codestyle/README.md");
	}
	if (
		!Array.isArray(policy?.policyModules) ||
		policy.policyModules.length === 0
	) {
		errors.push("policyModules must be a non-empty array");
		return errors;
	}

	const seenIds = new Set();
	for (const [index, module] of policy.policyModules.entries()) {
		const prefix = `policyModules[${index}]`;
		requireOnlyKeys(
			module,
			["id", "path", "changedFilePatterns", "sourceRules", "requiredGates"],
			prefix,
			errors,
		);
		requireString(module?.id, `${prefix}.id`, errors);
		requireString(module?.path, `${prefix}.path`, errors);
		if (!expectedModuleIds.has(module?.id)) {
			errors.push(`${prefix}.id is not a known policy module`);
		}
		if (!expectedModulePaths.has(module?.path)) {
			errors.push(`${prefix}.path is not a known policy module path`);
		}
		const expectedPath = expectedModules.get(module?.id);
		if (expectedPath !== undefined && module?.path !== expectedPath) {
			errors.push(
				`${prefix}.path must be ${expectedPath} for module ${module.id}`,
			);
		}
		if (seenIds.has(module?.id)) {
			errors.push(`${prefix}.id duplicates ${module.id}`);
		}
		seenIds.add(module?.id);
		if (!isInsideRepo(module?.path ?? "")) {
			errors.push(`${prefix}.path must be repo-relative`);
		} else if (!existsSync(join(repoRoot, module.path))) {
			errors.push(`${prefix}.path does not exist: ${module.path}`);
		}
		if (
			!Array.isArray(module?.changedFilePatterns) ||
			module.changedFilePatterns.length === 0
		) {
			errors.push(`${prefix}.changedFilePatterns must be a non-empty array`);
		} else {
			requireUniqueStrings(
				module.changedFilePatterns,
				`${prefix}.changedFilePatterns`,
				errors,
			);
			for (const [
				patternIndex,
				pattern,
			] of module.changedFilePatterns.entries()) {
				requireRepoRelativePattern(
					pattern,
					`${prefix}.changedFilePatterns[${patternIndex}]`,
					errors,
				);
			}
		}
		if (
			!Array.isArray(module?.sourceRules) ||
			module.sourceRules.length === 0
		) {
			errors.push(`${prefix}.sourceRules must be a non-empty array`);
		} else {
			requireUniqueStrings(module.sourceRules, `${prefix}.sourceRules`, errors);
			for (const rule of module.sourceRules) {
				if (!expectedSourceRules.has(rule)) {
					errors.push(`${prefix}.sourceRules contains unknown rule ${rule}`);
				}
			}
		}
		if (
			!Array.isArray(module?.requiredGates) ||
			module.requiredGates.length === 0
		) {
			errors.push(`${prefix}.requiredGates must be a non-empty array`);
		} else {
			requireUniqueStrings(
				module.requiredGates,
				`${prefix}.requiredGates`,
				errors,
			);
		}
	}
	for (const id of expectedModuleIds) {
		if (!seenIds.has(id)) {
			errors.push(`policyModules missing required module ${id}`);
		}
	}
	if (
		!Array.isArray(policy?.claimBoundaries) ||
		policy.claimBoundaries.length === 0
	) {
		errors.push("claimBoundaries must be a non-empty array");
	} else {
		for (const [index, boundary] of policy.claimBoundaries.entries()) {
			requireString(boundary, `claimBoundaries[${index}]`, errors);
		}
	}
	return errors;
}

const parsedArgs = parseArgs(process.argv.slice(2));
if (parsedArgs.errors.length > 0) {
	writeStaticFailure(
		parsedArgs.options,
		["coding-policy: failed", "- invalid command line arguments"],
		parsedArgs.errors,
	);
	process.exit(1);
}

if (!existsSync(policyPath)) {
	writeStaticFailure(
		parsedArgs.options,
		["coding-policy: missing coding-policy.json"],
		["coding-policy.json is missing"],
	);
	process.exit(1);
}
if (!existsSync(schemaPath)) {
	writeStaticFailure(
		parsedArgs.options,
		["coding-policy: missing contracts/coding-policy.schema.json"],
		["contracts/coding-policy.schema.json is missing"],
	);
	process.exit(1);
}

let policy;
let schema;
try {
	policy = readPolicyJson();
} catch {
	writeStaticFailure(
		parsedArgs.options,
		["coding-policy: failed to parse coding-policy.json"],
		["coding-policy.json could not be parsed as JSON"],
	);
	process.exit(1);
}

try {
	schema = readSchemaJson();
} catch {
	writeStaticFailure(
		parsedArgs.options,
		["coding-policy: failed to parse contracts/coding-policy.schema.json"],
		["contracts/coding-policy.schema.json could not be parsed as JSON"],
	);
	process.exit(1);
}

if (parsedArgs.options.gitChanged) {
	try {
		parsedArgs.options.changedFiles.push(...gitChangedFiles());
	} catch {
		writeStaticFailure(
			parsedArgs.options,
			[
				"coding-policy: failed",
				"- --git-changed failed to read git changed files",
			],
			["--git-changed failed to read git changed files"],
		);
		process.exit(1);
	}
	parsedArgs.options.changedFiles = uniqueStrings(
		parsedArgs.options.changedFiles,
	);
}
if (parsedArgs.options.gitBase !== null) {
	try {
		parsedArgs.options.changedFiles.push(
			...gitBaseChangedFiles(parsedArgs.options.gitBase),
		);
	} catch {
		writeStaticFailure(
			parsedArgs.options,
			[
				"coding-policy: failed",
				"- --git-base failed to read git changed files",
			],
			["--git-base failed to read git changed files"],
		);
		process.exit(1);
	}
	parsedArgs.options.changedFiles = uniqueStrings(
		parsedArgs.options.changedFiles,
	);
}
if (
	parsedArgs.options.routeRequested &&
	parsedArgs.options.changedFiles.length === 0
) {
	writeStaticFailure(
		parsedArgs.options,
		[
			"coding-policy: failed",
			"- route requests require at least one changed file",
		],
		["route requests require at least one changed file"],
	);
	process.exit(1);
}

const errors = validatePolicy(policy, schema);
if (parsedArgs.options.changedFiles.length > MAX_CHANGED_FILES) {
	errors.push(`changedFiles must include at most ${MAX_CHANGED_FILES} paths`);
}
for (const [index, changedFile] of parsedArgs.options.changedFiles.entries()) {
	if (!isInsideRepo(changedFile)) {
		errors.push(`changedFiles[${index}] must be repo-relative`);
	}
	validateRoutePathShape(changedFile, `changedFiles[${index}]`, errors);
}
if (errors.length > 0) {
	writeStaticValidationFailure(parsedArgs.options, errors);
	process.exit(1);
}

if (parsedArgs.options.json) {
	const payload =
		parsedArgs.options.changedFiles.length > 0
			? buildPolicyRoute(policy, parsedArgs.options.changedFiles)
			: {
					schemaVersion: "coding-policy-validation/v1",
					status: "pass",
					policySchemaVersion: policy.schemaVersion,
					authority: policy.authority,
					policyModules: policy.policyModules.length,
					claimBoundaries: policy.claimBoundaries.length,
				};
	process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
} else {
	console.log(
		"coding-policy: pass (" +
			policy.policyModules.length +
			" modules, " +
			policy.claimBoundaries.length +
			" claim boundaries)",
	);
	if (parsedArgs.options.changedFiles.length > 0) {
		const route = buildPolicyRoute(policy, parsedArgs.options.changedFiles);
		console.log(
			"coding-policy: route (" +
				route.policyModules.length +
				" modules, " +
				route.requiredGates.length +
				" required gates)",
		);
	}
}
