#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function error(msg) {
  console.error(`[skill_lint] ERROR: ${msg}`);
  process.exit(2);
}

const file = process.argv[2];
if (!file) {
  console.error("Usage: scripts/skill_lint.mjs path/to/SKILL.md");
  process.exit(2);
}

const p = path.resolve(process.cwd(), file);
if (!fs.existsSync(p)) error(`File not found: ${p}`);

const text = fs.readFileSync(p, "utf8");

// Find the first two frontmatter markers
const lines = text.split(/\r?\n/);
let first = -1;
let second = -1;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].trim() === "---") {
    if (first === -1) first = i;
    else {
      second = i;
      break;
    }
  }
}
if (first !== 0 || second === -1) error("Missing YAML front matter (must start with --- and end with ---).");

const fm = lines.slice(first + 1, second).join("\n");

// Reject block scalars for critical single-line fields
if (/^\s*name:\s*[>|]/m.test(fm)) error("Frontmatter 'name' must be single-line (no > or |).");
if (/^\s*description:\s*[>|]/m.test(fm)) error("Frontmatter 'description' must be single-line (no > or |).");
if (/^\s*short-description:\s*[>|]/m.test(fm)) error("Frontmatter 'metadata.short-description' must be single-line (no > or |).");

function getValue(key) {
  const m = fm.match(new RegExp(`^\\s*${key}:\\s*(.+)\\s*$`, "m"));
  return m ? m[1].trim() : null;
}

let name = getValue("name");
let description = getValue("description");
let shortDescription = getValue("short-description");

if (!name) error("Missing required frontmatter: name");
if (!description) error("Missing required frontmatter: description");
// Not required by Codex, but required by this repo's lint to encourage good UX in skill pickers.
if (!shortDescription) error("Missing recommended frontmatter: metadata.short-description");

function stripQuotes(s) {
  return s.replace(/^[\'"]|[\'"]$/g, "");
}

name = stripQuotes(name);
description = stripQuotes(description);
shortDescription = stripQuotes(shortDescription);

if (name.includes("\n")) error("name contains newline.");
if (description.includes("\n")) error("description contains newline.");
if (shortDescription.includes("\n")) error("short-description contains newline.");

if (name.length > 100) error(`name too long: ${name.length} (max 100).`);
if (description.length > 500) error(`description too long: ${description.length} (max 500).`);
if (shortDescription.length > 160) error(`short-description too long: ${shortDescription.length} (max 160).`);

console.log("[skill_lint] OK");
