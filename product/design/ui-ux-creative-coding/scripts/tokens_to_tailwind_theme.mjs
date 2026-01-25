#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function flatten(prefix, obj, out) {
  if (obj && typeof obj === "object" && !Array.isArray(obj)) {
    for (const [k, v] of Object.entries(obj)) {
      const next = prefix ? `${prefix}-${k}` : k;
      flatten(next, v, out);
    }
  } else {
    out[prefix] = obj;
  }
}

function main() {
  const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
  const tokensPath = process.argv[2] ? path.resolve(process.cwd(), process.argv[2]) : path.join(root, "assets", "tokens.json");
  const outPath = process.argv[3] ? path.resolve(process.cwd(), process.argv[3]) : path.join(root, "assets", "tailwind-theme.css");

  const tokens = JSON.parse(fs.readFileSync(tokensPath, "utf8"));

  const vars = {};

  if (tokens.colors) {
    const flat = {};
    flatten("", tokens.colors, flat);
    for (const [k, v] of Object.entries(flat)) vars[`--color-${k}`] = v;
  }
  if (tokens.radius) for (const [k, v] of Object.entries(tokens.radius)) vars[`--radius-${k}`] = v;
  if (tokens.shadow) for (const [k, v] of Object.entries(tokens.shadow)) vars[`--shadow-${k}`] = v;

  const motion = tokens.motion ?? {};
  if (motion.durations) for (const [k, v] of Object.entries(motion.durations)) vars[`--dur-${k}`] = v;
  if (motion.easing) for (const [k, v] of Object.entries(motion.easing)) vars[`--ease-${k}`] = v;

  const lines = [];
  lines.push("/* Generated from assets/tokens.json */");
  lines.push('@import "tailwindcss";');
  lines.push("");
  lines.push("@theme {");
  for (const k of Object.keys(vars).sort()) lines.push(`  ${k}: ${vars[k]};`);
  lines.push("}");
  lines.push("");

  fs.writeFileSync(outPath, lines.join("\n"), "utf8");
  console.log(`[tokens_to_tailwind_theme] wrote ${outPath}`);
}

main();
