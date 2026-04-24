#!/usr/bin/env node

const fs = require("node:fs/promises");
const path = require("node:path");

const DEFAULT_URL =
  "https://developers.openai.com/api/docs/guides/latest-model.md";
const DEFAULT_BASE_URL = "https://developers.openai.com";

function parseArgs(argv) {
  const args = {
    source: process.env.LATEST_MODEL_URL || DEFAULT_URL,
    baseUrl: process.env.LATEST_MODEL_BASE_URL || DEFAULT_BASE_URL,
  };

  const requireValue = (flagName, index) => {
    const value = argv[index + 1];
    if (!value || value.startsWith("-")) {
      throw new Error(`${flagName} requires a value`);
    }
    return value;
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--source" || arg === "--url") {
      args.source = requireValue(arg, i);
      i += 1;
    } else if (arg === "--base-url") {
      args.baseUrl = requireValue(arg, i);
      i += 1;
    }
  }

  return args;
}

async function readSource(source, options = {}) {
  const { signal, timeoutMs = 30000 } = options;
  if (source.startsWith("file://")) {
    return fs.readFile(new URL(source), "utf8");
  }

  if (!/^https?:\/\//.test(source)) {
    return fs.readFile(path.resolve(source), "utf8");
  }

  const timeoutController = new AbortController();
  const timeoutHandle = setTimeout(() => {
    timeoutController.abort();
  }, timeoutMs);
  const onAbort = () => timeoutController.abort();
  if (signal) {
    if (signal.aborted) {
      onAbort();
    } else {
      signal.addEventListener("abort", onAbort, { once: true });
    }
  }

  try {
    const response = await fetch(source, {
      headers: { accept: "text/markdown,text/plain,*/*" },
      signal: timeoutController.signal,
    });

    if (!response.ok) {
      throw new Error(`failed to fetch ${source}: ${response.status}`);
    }

    return response.text();
  } catch (error) {
    if (timeoutController.signal.aborted && !signal?.aborted) {
      throw new Error(`failed to fetch ${source}: timed out after ${timeoutMs}ms`, {
        cause: error,
      });
    }
    throw error;
  } finally {
    clearTimeout(timeoutHandle);
    signal?.removeEventListener("abort", onAbort);
  }
}

function parseIndentedInfo(lines, startIndex) {
  const info = {};

  for (let i = startIndex + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line.trim()) {
      continue;
    }

    const match = line.match(/^ {2}([A-Za-z][A-Za-z0-9_-]*):\s*(.+?)\s*$/);
    if (!match) {
      break;
    }

    info[match[1]] = match[2].replace(/^["']|["']$/g, "");
  }

  return info;
}

function parseFlatInfo(block) {
  const info = {};

  for (const line of block.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.+?)\s*$/);
    if (match) {
      info[match[1]] = match[2].replace(/^["']|["']$/g, "");
    }
  }

  return info;
}

function extractLatestModelInfo(markdown) {
  const lines = markdown.split(/\r?\n/);
  const latestModelInfoIndex = lines.findIndex((line) =>
    /^latestModelInfo:\s*$/.test(line)
  );

  if (latestModelInfoIndex >= 0) {
    return parseIndentedInfo(lines, latestModelInfoIndex);
  }

  const commentMatch = markdown.match(
    /<!--\s*latestModelInfo\s*\n([\s\S]*?)\n\s*-->/m
  );
  if (commentMatch) {
    return parseFlatInfo(commentMatch[1]);
  }

  return undefined;
}

function modelToSkillSlug(model) {
  return model.trim().replace(/\./g, "p");
}

function absoluteUrl(baseUrl, value) {
  try {
    return new URL(value, baseUrl).toString();
  } catch (error) {
    throw new Error(
      `absoluteUrl failed to resolve value "${value}" against base "${baseUrl}"`,
      { cause: error }
    );
  }
}

function normalizeInfo(info, baseUrl) {
  const model = info?.model?.trim();
  const migrationGuide = info?.migrationGuide?.trim();
  const promptingGuide = info?.promptingGuide?.trim();

  if (!model || !migrationGuide || !promptingGuide) {
    throw new Error(
      "latestModelInfo must include model, migrationGuide, and promptingGuide"
    );
  }

  return {
    model,
    modelSlug: modelToSkillSlug(model),
    migrationGuideUrl: absoluteUrl(baseUrl, migrationGuide),
    promptingGuideUrl: absoluteUrl(baseUrl, promptingGuide),
  };
}

async function main() {
  const { source, baseUrl } = parseArgs(process.argv);
  const markdown = await readSource(source);
  const info = extractLatestModelInfo(markdown);

  if (!info) {
    throw new Error(`latestModelInfo block not found in ${source}`);
  }

  process.stdout.write(
    `${JSON.stringify(normalizeInfo(info, baseUrl), null, 2)}\n`
  );
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
