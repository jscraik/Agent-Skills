#!/usr/bin/env bash
set -euo pipefail

QUIET=0
FORCE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
	case "$1" in
		--quiet)
			QUIET=1
			shift
			;;
		--force)
			FORCE=1
			shift
			;;
		--dry-run)
			DRY_RUN=1
			shift
			;;
		*)
			echo "Unknown option: $1" >&2
			exit 2
			;;
	esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAM_DIR="$ROOT_DIR/.diagram"
CONTEXT_DIR="$ROOT_DIR/AI/context"
DIAGRAM_CONTEXT_DIR="$DIAGRAM_DIR/context"
CONTEXT_FILE="$CONTEXT_DIR/diagram-context.md"
META_FILE="$DIAGRAM_CONTEXT_DIR/diagram-context.meta.json"
LOG_FILE="$DIAGRAM_CONTEXT_DIR/refresh.log"
MIN_SECONDS="${DIAGRAM_REFRESH_MIN_SECONDS:-1800}"
MAX_FILES="${DIAGRAM_REFRESH_MAX_FILES:-10000}"
DEFAULT_DIAGRAM_PATTERNS="src/**/*.ts,scripts/**/*.js,scripts/**/*.cjs,scripts/**/*.mjs,e2e/**/*.ts"
DEFAULT_EXCLUDE_PATTERNS="node_modules/**,.git/**,dist/**,artifacts/**,.tmp-diagram-refresh-*/**,.diagram/**,**/*.test.*,**/*.spec.*"
DIAGRAM_PATTERNS="${DIAGRAM_REFRESH_PATTERNS:-$DEFAULT_DIAGRAM_PATTERNS}"
EXCLUDE_PATTERNS="${DIAGRAM_REFRESH_EXCLUDE_PATTERNS:-$DEFAULT_EXCLUDE_PATTERNS}"
NOW_EPOCH="$(date +%s)"

mkdir -p "$DIAGRAM_DIR" "$DIAGRAM_CONTEXT_DIR" "$CONTEXT_DIR"

log() {
	local message="$1"
	printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$message" >> "$LOG_FILE"
	if [[ "$QUIET" -ne 1 ]]; then
		printf '%s\n' "$message"
	fi
}

if [[ "$DRY_RUN" -eq 1 ]]; then
	log "dry-run: would refresh diagrams into $DIAGRAM_DIR and context at $CONTEXT_FILE"
	exit 0
fi

if [[ "$FORCE" -ne 1 && -f "$META_FILE" ]]; then
	last_epoch="$(jq -r '.last_generated_epoch // 0' "$META_FILE" 2>/dev/null || echo 0)"
	if [[ "$last_epoch" =~ ^[0-9]+$ ]]; then
		age=$((NOW_EPOCH - last_epoch))
		if (( age < MIN_SECONDS )); then
			log "skip: cooldown active (${age}s < ${MIN_SECONDS}s)"
			exit 0
		fi
	fi
fi

if ! pnpm --dir "$ROOT_DIR" exec diagram --version >/dev/null 2>&1; then
	log "error: diagram CLI is not available"
	exit 1
fi

TMP_DIR="$(mktemp -d "$DIAGRAM_CONTEXT_DIR/tmp-refresh-XXXXXX")"
TMP_OUTPUT_DIR=".diagram/context/$(basename "$TMP_DIR")/diagrams"
DIAGRAM_GENERATE_ARGS=(
	generate-all
	.
	--output-dir "$TMP_OUTPUT_DIR"
	--patterns "$DIAGRAM_PATTERNS"
	--exclude "$EXCLUDE_PATTERNS"
	--max-files "$MAX_FILES"
	--deterministic
)
trap 'rm -rf "$TMP_DIR"' EXIT

pushd "$ROOT_DIR" >/dev/null
if [[ "$QUIET" -eq 1 ]]; then
	diagram_stderr="$TMP_DIR/diagram-generate.stderr"
	set +e
	pnpm exec diagram "${DIAGRAM_GENERATE_ARGS[@]}" >/dev/null 2>"$diagram_stderr"
	status=$?
	set -e
	if [[ "$status" -ne 0 ]]; then
		popd >/dev/null
		if [[ -s "$diagram_stderr" ]]; then
			cat "$diagram_stderr" >&2
		else
			echo "error: diagram generate-all failed with exit $status before writing stderr to $diagram_stderr" >&2
		fi
		exit "$status"
	fi
else
	if ! pnpm exec diagram --version >/dev/null 2>&1; then
		log "error: diagram CLI is not available"
		exit 1
	fi
	pnpm exec diagram "${DIAGRAM_GENERATE_ARGS[@]}"
fi
popd >/dev/null

if ! ls "$TMP_DIR/diagrams"/*.mmd >/dev/null 2>&1; then
	log "error: no .mmd files produced"
	exit 1
fi

MANIFEST_PATH="$TMP_DIR/diagrams/manifest.json"
ROOT_DIR="$ROOT_DIR" TMP_DIR="$TMP_DIR" MANIFEST_PATH="$MANIFEST_PATH" node <<'NODE'
const { createHash } = require("node:crypto");
const { readdirSync, readFileSync, writeFileSync } = require("node:fs");
const { basename, join } = require("node:path");

const rootDir = process.env.ROOT_DIR;
const tmpDir = process.env.TMP_DIR;
const manifestPath = process.env.MANIFEST_PATH;

if (!rootDir || !tmpDir || !manifestPath) {
  throw new Error("diagram manifest generation requires ROOT_DIR, TMP_DIR, and MANIFEST_PATH");
}

const diagramsDir = join(tmpDir, "diagrams");
const ensureTrailingNewline = (content) =>
  content.endsWith("\n") ? content : `${content}\n`;
const sourceManifest = (() => {
  try {
    return JSON.parse(readFileSync(manifestPath, "utf8"));
  } catch {
    return {};
  }
})();
const stableId = (prefix, value) => {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 48) || prefix;
  const digest = createHash("sha1").update(value).digest("hex").slice(0, 8);
  return `${prefix}_${slug}_${digest}`;
};
const stableRawIdentity = (rawId) =>
  rawId
    .replace(/(?:[_-](?:[a-f0-9]{6,}|[0-9]{4,})){1,2}$/i, "")
    .replace(/(?:[_-][0-9]+)+$/i, "")
    .toLowerCase();
const projectDisplayName = (() => {
  try {
    const packageJson = JSON.parse(readFileSync(join(rootDir, "package.json"), "utf8"));
    if (typeof packageJson.name === "string" && packageJson.name.trim()) {
      return packageJson.name
        .replace(/^@[^/]+\//, "")
        .replace(/[-_]+/g, " ")
        .trim();
    }
  } catch {
    // Fall back to the checkout folder for repositories without package metadata.
  }
  return basename(rootDir).replace(/[-_]+/g, " ").trim() || "repository";
})();
const normalizeProjectReferences = (content) =>
  content
    .replace(
      /^\s*title\s+"System Context \u2014 .+"$/m,
      `  title "System Context \u2014 ${projectDisplayName}"`,
    )
    .replace(
      /^\s*System\(mainSystem,\s*".+?",\s*"The system being documented"\)$/m,
      `  System(mainSystem, "${projectDisplayName}", "The system being documented")`,
    );

const normalizeMemoryNodeLabel = (value) =>
  stableRawIdentity(value.replace(/^[^A-Za-z0-9]+/, "")).replace(/_/g, "-");
const parseMermaidSubgraphNode = (line) => {
  const nodeMatch = line.match(/^(\s{4})([A-Za-z_][A-Za-z0-9_]*)(\[.+\])$/);
  if (!nodeMatch) {
    return null;
  }
  return {
    indent: nodeMatch[1],
    rawId: nodeMatch[2],
    suffix: nodeMatch[3],
    label: nodeMatch[3].match(/"([^"]+)"/)?.[1] ?? nodeMatch[2],
  };
};

const declaredMemoryNodeIds = (lines) => {
  const declaredNodeIds = new Set();
  const memoryNodeIdsByLabel = new Map();
  for (const line of lines) {
    const node = parseMermaidSubgraphNode(line);
    if (!node) {
      continue;
    }
    declaredNodeIds.add(node.rawId);
    const label = node.label;
    if (label.startsWith("📚 ")) {
      memoryNodeIdsByLabel.set(normalizeMemoryNodeLabel(label), node.rawId);
    }
  }
  return { declaredNodeIds, memoryNodeIdsByLabel };
};

const rewriteMemoryRetrieveEdges = (lines) => {
  const { declaredNodeIds, memoryNodeIdsByLabel } = declaredMemoryNodeIds(lines);
  for (const [lineIndex, line] of lines.entries()) {
    const edgeMatch = line.match(/^\s{2}([A-Za-z_][A-Za-z0-9_]*)(\s+-->\|retrieves from\|\s+)([A-Za-z_][A-Za-z0-9_]*)(.*)$/);
	  if (
	    !edgeMatch ||
	    (declaredNodeIds.has(edgeMatch[1]) && declaredNodeIds.has(edgeMatch[3]))
	  ) {
	    continue;
	  }
	  const sourceReplacementId = declaredNodeIds.has(edgeMatch[1])
	    ? edgeMatch[1]
	    : memoryNodeIdsByLabel.get(normalizeMemoryNodeLabel(edgeMatch[1]));
    const targetReplacementId =
      declaredNodeIds.has(edgeMatch[3])
        ? edgeMatch[3]
        : memoryNodeIdsByLabel.get(normalizeMemoryNodeLabel(edgeMatch[3]));
    if (sourceReplacementId && targetReplacementId) {
      lines[lineIndex] = `  ${sourceReplacementId}${edgeMatch[2]}${targetReplacementId}${edgeMatch[4]}`;
    }
  }
};

const dedupeSubgraphNodeIds = (content, diagramName) => {
  const lines = content.trimEnd().split(/\r?\n/);
  const nodes = [];
  let currentSubgraph = null;
  let subgraphIndex = 0;

  for (const [lineIndex, line] of lines.entries()) {
    const subgraphMatch = line.match(/^  subgraph (\S+)\["(.+)"\]$/);
    if (subgraphMatch) {
      currentSubgraph = {
        rawId: subgraphMatch[1],
        label: subgraphMatch[2],
        index: subgraphIndex,
      };
      subgraphIndex += 1;
      continue;
    }

    if (line === "  end") {
      currentSubgraph = null;
      continue;
    }

    const node = parseMermaidSubgraphNode(line);
    if (node && currentSubgraph) {
      nodes.push({
        lineIndex,
        indent: node.indent,
        rawId: node.rawId,
        suffix: node.suffix,
        label: node.label,
        subgraph: currentSubgraph,
      });
    }
  }

  const counts = new Map();
  for (const node of nodes) {
    counts.set(node.rawId, (counts.get(node.rawId) ?? 0) + 1);
  }

  const duplicateIds = new Set(
    [...counts.entries()]
      .filter(([, count]) => count > 1)
      .map(([rawId]) => rawId),
  );
  const seen = new Map();
  const rewrittenIds = new Map();
  for (const node of nodes) {
    if (!duplicateIds.has(node.rawId)) {
      continue;
    }
    const occurrence = (seen.get(node.rawId) ?? 0) + 1;
    seen.set(node.rawId, occurrence);
    const scopedId = stableId(
      "node",
      [
        diagramName,
        node.subgraph.label,
        stableRawIdentity(node.subgraph.rawId),
        node.label,
        stableRawIdentity(node.rawId),
        String(node.subgraph.index),
        String(occurrence),
      ].join("/"),
    );
    lines[node.lineIndex] = `${node.indent}${scopedId}${node.suffix}`;
    const ids = rewrittenIds.get(node.rawId) ?? [];
    ids.push(scopedId);
    rewrittenIds.set(node.rawId, ids);
  }

  for (const [lineIndex, line] of lines.entries()) {
    const classMatch = line.match(/^(\s*class\s+)([A-Za-z_][A-Za-z0-9_,]*)(\s+\S+.*)$/);
    if (!classMatch) {
      continue;
    }
    const classIds = classMatch[2]
      .split(",")
      .map((id) => id.trim())
      .filter((id) => id.length > 0)
      .flatMap((id) => rewrittenIds.get(id) ?? [id]);
    lines[lineIndex] = `${classMatch[1]}${[...new Set(classIds)].join(",")}${classMatch[3]}`;
  }

	  rewriteMemoryRetrieveEdges(lines);

  return ensureTrailingNewline(lines.join("\n"));
};

const parseArchitecture = (content) => {
  const lines = content.trimEnd().split(/\r?\n/);
  const subgraphs = [];
  let currentSubgraph = null;

  for (const line of lines) {
    const subgraphMatch = line.match(/^  subgraph (\S+)\["(.+)"\]$/);
    if (subgraphMatch) {
      currentSubgraph = {
        rawId: subgraphMatch[1],
        label: subgraphMatch[2],
        nodes: [],
      };
      subgraphs.push(currentSubgraph);
      continue;
    }

    if (line === "  end") {
      currentSubgraph = null;
      continue;
    }

    const nodeMatch = line.match(/^    (\S+)\["(.+)"\]$/);
    if (nodeMatch && currentSubgraph) {
      currentSubgraph.nodes.push({
        rawId: nodeMatch[1],
        label: nodeMatch[2],
      });
    }
  }

  return subgraphs;
};

const buildArchitecture = (subgraphs) => {
  const nodeMap = new Map();
  const lines = ["graph TD"];
  const sortedSubgraphs = [...subgraphs].sort((left, right) =>
    left.label.localeCompare(right.label) ||
    stableRawIdentity(left.rawId).localeCompare(stableRawIdentity(right.rawId)),
  );

  for (const subgraph of sortedSubgraphs) {
    const subgraphId = stableId(
      "sg",
      `${subgraph.label}/${stableRawIdentity(subgraph.rawId)}`,
    );
    lines.push(`  subgraph ${subgraphId}["${subgraph.label}"]`);
    const sortedNodes = [...subgraph.nodes].sort((left, right) =>
      left.label.localeCompare(right.label) ||
      stableRawIdentity(left.rawId).localeCompare(stableRawIdentity(right.rawId)),
    );
    for (const node of sortedNodes) {
      const nodeId = stableId(
        "node",
        `${subgraph.label}/${node.label}/${stableRawIdentity(node.rawId)}`,
      );
      nodeMap.set(node.rawId, { canonicalId: nodeId, label: node.label });
      lines.push(`    ${nodeId}["${node.label}"]`);
    }
    lines.push("  end");
  }

  return {
    content: ensureTrailingNewline(lines.join("\n")),
    nodeMap,
  };
};

const buildDependency = (content, nodeMap) => {
  const lines = content.trimEnd().split(/\r?\n/);
  if (lines.length === 0) {
    return ensureTrailingNewline(content);
  }

  const externalNodeMap = new Map();
  const targetNodeEntries = new Map();
  const dependencyEdges = new Map();
  const styleEntries = new Map();

  for (const line of lines.slice(1)) {
    const edgeMatch = line.match(/^  (\S+)\["(.+)"\] --> (\S+)$/);
    if (edgeMatch) {
      const [, rawSourceId, sourceLabel, rawTargetId] = edgeMatch;
      const target = nodeMap.get(rawTargetId) ?? {
        canonicalId: stableId("node", rawTargetId),
        label: rawTargetId,
      };
      targetNodeEntries.set(target.canonicalId, {
        line: "  " + target.canonicalId + "[\"" + target.label + "\"]",
        sortKey: target.label,
      });
      const sourceCanonicalId =
        externalNodeMap.get(rawSourceId) ?? stableId("ext", sourceLabel);
      externalNodeMap.set(rawSourceId, sourceCanonicalId);
      const line = `  ${sourceCanonicalId}["${sourceLabel}"] --> ${target.canonicalId}`;
      dependencyEdges.set(line, {
        line,
        sortKey: `${sourceLabel}::${target.label}`,
      });
      continue;
    }

    const styleMatch = line.match(/^  style (\S+) (.+)$/);
    if (styleMatch) {
      const [, rawNodeId, styleSpec] = styleMatch;
      const canonicalId = externalNodeMap.get(rawNodeId);
      if (canonicalId) {
        const line = `  style ${canonicalId} ${styleSpec}`;
        styleEntries.set(line, {
          line,
          sortKey: canonicalId,
        });
      }
    }
  }

  const findDependencyNode = (labelPrefix) => {
    for (const [canonicalId, entry] of targetNodeEntries.entries()) {
      if (entry.sortKey.startsWith(labelPrefix)) {
        return { canonicalId, label: entry.sortKey };
      }
    }
    return undefined;
  };
  const presetResolver = findDependencyNode("preset_resolver_");
  const presetSourceLoaders = findDependencyNode("preset_source_loaders_");
  if (presetResolver && presetSourceLoaders) {
    for (const node of [presetResolver, presetSourceLoaders]) {
      targetNodeEntries.set(node.canonicalId, {
        line: "  " + node.canonicalId + "[\"" + node.label + "\"]",
        sortKey: node.label,
      });
    }
    const line =
      "  " + presetResolver.canonicalId + " --> " + presetSourceLoaders.canonicalId;
    dependencyEdges.set(line, {
      line,
      sortKey: presetResolver.label + "::" + presetSourceLoaders.label,
    });
  }

  return ensureTrailingNewline(
    [
      "graph LR",
      ...[...targetNodeEntries.values()]
        .sort((left, right) => left.sortKey.localeCompare(right.sortKey) || left.line.localeCompare(right.line))
        .map((entry) => entry.line),
      ...[...dependencyEdges.values()]
        .sort((left, right) => left.sortKey.localeCompare(right.sortKey) || left.line.localeCompare(right.line))
        .map((entry) => entry.line),
      ...[...styleEntries.values()]
        .sort((left, right) => left.sortKey.localeCompare(right.sortKey) || left.line.localeCompare(right.line))
        .map((entry) => entry.line),
    ].join("\n"),
  );
};

const diagramFiles = readdirSync(diagramsDir).filter((entry) => entry.endsWith(".mmd"));
const architecturePath = join(diagramsDir, "architecture.mmd");
const dependencyPath = join(diagramsDir, "dependency.mmd");

if (diagramFiles.includes("architecture.mmd")) {
  const architectureContent = readFileSync(architecturePath, "utf8");
  const { content: canonicalArchitecture, nodeMap } = buildArchitecture(
    parseArchitecture(architectureContent),
  );
  writeFileSync(architecturePath, canonicalArchitecture);

  if (diagramFiles.includes("dependency.mmd")) {
    const dependencyContent = readFileSync(dependencyPath, "utf8");
    writeFileSync(dependencyPath, buildDependency(dependencyContent, nodeMap));
  }
}

if (diagramFiles.includes("class.mmd")) {
  const classPath = join(diagramsDir, "class.mmd");
  let classContent = readFileSync(classPath, "utf8");
  const loaderMatch = classContent.match(
    /class\s+(\S+)\s*\{\s*\n\s*\+src\/lib\/contract\/loader\.ts\s*\n\s*\}/m,
  );
  const loaderClassId =
    loaderMatch?.[1] ?? stableId("contract_loader", "src/lib/contract/loader.ts");
  if (!loaderMatch) {
    classContent = `${classContent.trimEnd()}\n  class ${loaderClassId} {\n    +src/lib/contract/loader.ts\n  }\n`;
  }
  const validatorMatch = classContent.match(
    /class\s+(\S+)\s*\{\s*\n\s*\+src\/lib\/contract\/validator\.ts\s*\n\s*\}/m,
  );
  const validatorClassId =
    validatorMatch?.[1] ?? stableId("contract_validator", "src/lib/contract/validator.ts");
  if (!validatorMatch) {
    classContent = `${classContent.trimEnd()}\n  class ${validatorClassId} {\n    +src/lib/contract/validator.ts\n  }\n`;
  }
  const validateContractEdge = new RegExp(
    `^\\s*${loaderClassId}\\s+-->\\s+${validatorClassId}\\s*:\\s*validateContract\\s*$`,
    "m",
  );
  if (!validateContractEdge.test(classContent)) {
    classContent = `${classContent.trimEnd()}\n  ${loaderClassId} --> ${validatorClassId} : validateContract\n`;
  }
	writeFileSync(classPath, ensureTrailingNewline(classContent.trimEnd()));
}

if (diagramFiles.includes("c4context.mmd")) {
  const c4ContextPath = join(diagramsDir, "c4context.mmd");
  let c4ContextContent = readFileSync(c4ContextPath, "utf8");
  const replaceRequired = (source, pattern, replacement, label) => {
    if (!pattern.test(source)) {
      throw new Error(`c4context.mmd missing expected pattern: ${label}`);
    }
    return source.replace(pattern, replacement);
  };

  c4ContextContent = replaceRequired(
    c4ContextContent,
    /title "System Context — .*"/,
    'title "System Context — Coding Harness"',
    "title",
  );
  c4ContextContent = replaceRequired(
    c4ContextContent,
    /System\(mainSystem, "[^"]+", "[^"]+"\)/,
    'System(mainSystem, "Coding Harness", "Control plane for agentic development")',
    "main system",
  );
  c4ContextContent = replaceRequired(
    c4ContextContent,
    /System_Ext\((ext_\d+), "Version Control", "[^"]+"\)/,
    (_match, extId) =>
      `System_Ext(${extId}, "Version Control", "@octokit/rest, @octokit/request-error, @octokit/plugin-retry, @octokit/plugin-throttling")`,
    "version control dependency list",
  );
  writeFileSync(c4ContextPath, ensureTrailingNewline(c4ContextContent.trimEnd()));
}

for (const file of diagramFiles) {
	if (file === "architecture.mmd" || file === "dependency.mmd") {
		continue;
  }
  const filePath = join(diagramsDir, file);
  writeFileSync(
    filePath,
    dedupeSubgraphNodeIds(
      normalizeProjectReferences(readFileSync(filePath, "utf8").trimEnd()),
      file,
    ),
  );
}

const diagrams = readdirSync(diagramsDir)
  .filter((file) => file.endsWith(".mmd"))
  .sort()
	.map((file) => {
		const content = readFileSync(join(diagramsDir, file), "utf8");
		return {
			type: file.replace(/\.mmd$/, ""),
			file,
			outputPath: `.diagram/${file}`,
			lines: content.split(/\r?\n/).length,
			bytes: Buffer.byteLength(content),
			isPlaceholder:
				/placeholder/i.test(content) ||
				/not enough/i.test(content) ||
				/limited to/i.test(content),
		};
	});

writeFileSync(
	manifestPath,
	`${JSON.stringify(
		{
			...sourceManifest,
			generatedAt: new Date().toISOString(),
			rootPath: ".",
			diagramDir: ".diagram",
			diagrams,
		},
		null,
		"\t",
	)}\n`,
);
NODE

TMP_CONTEXT="$TMP_DIR/diagram-context.md"
SOURCE_FOCUS_FILE="$TMP_DIR/source-focus.txt"

{
	base_ref="$(git -C "$ROOT_DIR" merge-base HEAD origin/main 2>/dev/null || true)"
	if [[ -n "$base_ref" ]]; then
		git -C "$ROOT_DIR" diff --name-only --diff-filter=ACMR "$base_ref"...HEAD -- src scripts docs/agents/linear-templates package.json tsconfig.json .diagramrc 2>/dev/null || true
	else
		git -C "$ROOT_DIR" diff --name-only --diff-filter=ACMR HEAD -- src scripts docs/agents/linear-templates package.json tsconfig.json .diagramrc 2>/dev/null || true
	fi
} | awk '
	$0 ~ /^src\// && $0 !~ /\.(test|spec)\.(ts|js)$/ { print }
	$0 ~ /^docs\/agents\/linear-templates\// { print }
	$0 ~ /^scripts\/refresh-diagram-context\.sh$/ { print }
	$0 ~ /^scripts\/check-diagram-freshness\.sh$/ { print }
	$0 ~ /^scripts\/lib\/normalize-mermaid-artifact\.cjs$/ { print }
	$0 == "package.json" || $0 == "tsconfig.json" || $0 == ".diagramrc" { print }
' | sort -u > "$SOURCE_FOCUS_FILE"

{
	echo "# Diagram Context Pack"
	echo
	echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
	echo
	echo "## Table of Contents"
	echo
	echo "- [How to use this pack](#how-to-use-this-pack)"
	for file in "$TMP_DIR"/diagrams/*.mmd; do
		name="$(basename "$file" .mmd)"
		echo "- [${name}](#${name})"
	done
	echo
	echo "## How to use this pack"
	echo
	echo "- Start here for compact architecture, dependency, database, and ERD context before opening raw source files."
	echo "- Use .diagram/manifest.json to choose a focused Mermaid file when this combined pack is too large."
	echo '- For TypeScript implementation detail in this checkout, run `bash scripts/harness-cli.sh source-outline <path> --json` first, then unwrap one symbol with `--symbol <name>`. Downstream repositories can use `harness source-outline <path>`.'
	echo
	if [[ -s "$SOURCE_FOCUS_FILE" ]]; then
		echo "## Changed source focus"
		echo
		echo "- These architecture-sensitive paths changed on the current branch and may be compacted out of Mermaid diagrams."
		while IFS= read -r source_path; do
			[[ -n "$source_path" ]] || continue
			printf -- '- `%s`\n' "$source_path"
		done < "$SOURCE_FOCUS_FILE"
		echo
	fi
	for file in "$TMP_DIR"/diagrams/*.mmd; do
		name="$(basename "$file" .mmd)"
		echo "## ${name}"
		echo
		echo '```mermaid'
		cat "$file"
		echo
		echo '```'
		echo
	done
} > "$TMP_CONTEXT"

if [[ -f "$CONTEXT_FILE" ]] && \
	cmp -s \
		<(awk '!/^Generated: /' "$TMP_CONTEXT") \
		<(awk '!/^Generated: /' "$CONTEXT_FILE"); then
	existing_generated_line="$(awk '/^Generated: / { print; exit }' "$CONTEXT_FILE")"
	if [[ -n "$existing_generated_line" ]]; then
		awk -v generated_line="$existing_generated_line" '
			/^Generated: / {
				print generated_line
				next
			}
			{ print }
		' "$TMP_CONTEXT" > "$TMP_CONTEXT.preserve-generated"
		mv "$TMP_CONTEXT.preserve-generated" "$TMP_CONTEXT"
	fi
fi

if [[ -f "$CONTEXT_FILE" ]]; then
	set +e
	node - "$TMP_CONTEXT" "$CONTEXT_FILE" "$ROOT_DIR" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");
const { normalizeDiagramContextLines } = require(path.join(
	process.argv[4],
	"scripts/lib/normalize-mermaid-artifact.cjs",
));

const readNormalized = (filePath) =>
	normalizeDiagramContextLines(fs.readFileSync(filePath, "utf8").split(/\r?\n/));

process.exit(readNormalized(process.argv[2]) === readNormalized(process.argv[3]) ? 0 : 1);
NODE
	normalize_status=$?
	set -e
	if [[ "$normalize_status" -eq 0 ]]; then
		:
	elif [[ "$normalize_status" -ne 1 ]]; then
		log "error: diagram context normalize comparison failed"
		exit "$normalize_status"
	fi
fi

CONTEXT_SHA="$(shasum -a 256 "$TMP_CONTEXT" | awk '{print $1}')"
GIT_HEAD="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
DIAGRAM_COUNT="$(find "$TMP_DIR/diagrams" -maxdepth 1 -type f -name '*.mmd' | wc -l | tr -d ' ')"
CHANGED=true

if [[ -f "$CONTEXT_FILE" ]] && cmp -s "$TMP_CONTEXT" "$CONTEXT_FILE"; then
	CHANGED=false
fi

if [[ -f "$DIAGRAM_DIR/manifest.json" ]] && ! cmp -s "$TMP_DIR/diagrams/manifest.json" "$DIAGRAM_DIR/manifest.json"; then
	CHANGED=true
fi

rm -f "$DIAGRAM_DIR"/*.mmd
cp "$TMP_DIR"/diagrams/*.mmd "$DIAGRAM_DIR/"
cp "$TMP_DIR/diagrams/manifest.json" "$DIAGRAM_DIR/manifest.json"
cp "$TMP_CONTEXT" "$CONTEXT_FILE"

jq --tab -n \
	--arg generated_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
	--arg git_head "$GIT_HEAD" \
	--arg context_sha256 "$CONTEXT_SHA" \
	--argjson diagram_count "$DIAGRAM_COUNT" \
	--argjson last_generated_epoch "$NOW_EPOCH" \
	--argjson min_interval_seconds "$MIN_SECONDS" \
	--arg changed "$CHANGED" \
	'{
		schema_version: 1,
		generated_at: $generated_at,
		git_head: $git_head,
		context_sha256: $context_sha256,
		diagram_count: $diagram_count,
		last_generated_epoch: $last_generated_epoch,
		min_interval_seconds: $min_interval_seconds,
		changed: ($changed == "true")
	}' > "$META_FILE"

log "ok: refreshed ${DIAGRAM_COUNT} diagrams (changed=${CHANGED})"
