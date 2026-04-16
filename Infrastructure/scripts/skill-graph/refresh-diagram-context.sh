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
CONTEXT_DIR="$DIAGRAM_DIR/context"
CONTEXT_FILE="$CONTEXT_DIR/diagram-context.md"
META_FILE="$CONTEXT_DIR/diagram-context.meta.json"
LOG_FILE="$CONTEXT_DIR/refresh.log"
MIN_SECONDS="${DIAGRAM_REFRESH_MIN_SECONDS:-1800}"
MAX_FILES="${DIAGRAM_REFRESH_MAX_FILES:-1000}"
NOW_EPOCH="$(date +%s)"

mkdir -p "$DIAGRAM_DIR" "$CONTEXT_DIR"

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

if ! command -v diagram >/dev/null 2>&1; then
	log "error: diagram CLI is not available"
	exit 1
fi

TRUNC_DIR=".tmp-diagram-refresh-XXXXXX"
TMP_DIR="$(mktemp -d "$ROOT_DIR/${TRUNC_DIR}")"
TMP_BASENAME="$(basename "$TMP_DIR")"
EXCLUDE_PATTERNS="node_modules/**,.git/**,dist/**,${TMP_BASENAME}/**"
trap 'rm -rf "$TMP_DIR"' EXIT

pushd "$ROOT_DIR" >/dev/null
if [[ "$QUIET" -eq 1 ]]; then
	pnpm exec diagram all . --output-dir "$TMP_BASENAME/diagrams" --exclude "$EXCLUDE_PATTERNS" --max-files "$MAX_FILES" >/dev/null 2>&1
else
	pnpm exec diagram all . --output-dir "$TMP_BASENAME/diagrams" --exclude "$EXCLUDE_PATTERNS" --max-files "$MAX_FILES"
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
const { join } = require("node:path");

const rootDir = process.env.ROOT_DIR;
const tmpDir = process.env.TMP_DIR;
const manifestPath = process.env.MANIFEST_PATH;

if (!rootDir || !tmpDir || !manifestPath) {
  throw new Error("diagram manifest generation requires ROOT_DIR, TMP_DIR, and MANIFEST_PATH");
}

const diagramsDir = join(tmpDir, "diagrams");
const ensureTrailingNewline = (content) =>
  content.endsWith("\n") ? content : `${content}\n`;
const stableId = (prefix, value) => {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 48) || prefix;
  const digest = createHash("sha1").update(value).digest("hex").slice(0, 8);
  return `${prefix}_${slug}_${digest}`;
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
    left.label.localeCompare(right.label),
  );

  for (const subgraph of sortedSubgraphs) {
    const subgraphId = stableId("sg", subgraph.label);
    lines.push(`  subgraph ${subgraphId}["${subgraph.label}"]`);
    const sortedNodes = [...subgraph.nodes].sort((left, right) =>
      left.label.localeCompare(right.label),
    );
    for (const node of sortedNodes) {
      const nodeId = stableId("node", `${subgraph.label}/${node.label}`);
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
  const dependencyEdges = [];
  const styleEntries = [];

  for (const line of lines.slice(1)) {
    const edgeMatch = line.match(/^  (\S+)\["(.+)"\] --> (\S+)$/);
    if (edgeMatch) {
      const [, rawSourceId, sourceLabel, rawTargetId] = edgeMatch;
      const target = nodeMap.get(rawTargetId) ?? {
        canonicalId: stableId("node", rawTargetId),
        label: rawTargetId,
      };
      const sourceCanonicalId =
        externalNodeMap.get(rawSourceId) ?? stableId("ext", sourceLabel);
      externalNodeMap.set(rawSourceId, sourceCanonicalId);
      dependencyEdges.push({
        line: `  ${sourceCanonicalId}["${sourceLabel}"] --> ${target.canonicalId}`,
        sortKey: `${sourceLabel}::${target.label}`,
      });
      continue;
    }

    const styleMatch = line.match(/^  style (\S+) (.+)$/);
    if (styleMatch) {
      const [, rawNodeId, styleSpec] = styleMatch;
      const canonicalId = externalNodeMap.get(rawNodeId);
      if (canonicalId) {
        styleEntries.push({
          line: `  style ${canonicalId} ${styleSpec}`,
          sortKey: canonicalId,
        });
      }
    }
  }

  return ensureTrailingNewline(
    [
      "graph LR",
      ...dependencyEdges
        .sort((left, right) => left.sortKey.localeCompare(right.sortKey))
        .map((entry) => entry.line),
      ...styleEntries
        .sort((left, right) => left.sortKey.localeCompare(right.sortKey))
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

for (const file of diagramFiles) {
  if (file === "architecture.mmd" || file === "dependency.mmd") {
    continue;
  }
  const filePath = join(diagramsDir, file);
  writeFileSync(filePath, ensureTrailingNewline(readFileSync(filePath, "utf8").trimEnd()));
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
			generatedAt: new Date().toISOString(),
			rootPath: rootDir,
			diagramDir: ".diagram",
			diagrams,
		},
		null,
		2,
	)}\n`,
);
NODE

TMP_CONTEXT="$TMP_DIR/diagram-context.md"
{
	echo "# Diagram Context Pack"
	echo
	echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
	echo
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

CONTEXT_SHA="$(shasum -a 256 "$TMP_CONTEXT" | awk '{print $1}')"
GIT_HEAD="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
DIAGRAM_COUNT="$(ls "$TMP_DIR/diagrams"/*.mmd | wc -l | tr -d ' ')"
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
