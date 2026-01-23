#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function usage() {
  console.log("Usage: node web_playwright_trace.mjs --url <url> --out <dir> [--wait-ms <n>] [--timeout-ms <n>] [--headless true|false]");
}

function getArg(name, argv) {
  const idx = argv.indexOf(name);
  if (idx === -1) return null;
  return argv[idx + 1] ?? null;
}

const argv = process.argv.slice(2);
if (argv.includes("-h") || argv.includes("--help")) {
  usage();
  process.exit(0);
}

const url = getArg("--url", argv);
const out = getArg("--out", argv);
const waitMs = Number(getArg("--wait-ms", argv) || "3000");
const timeoutMs = Number(getArg("--timeout-ms", argv) || "30000");
const headlessRaw = getArg("--headless", argv);
const headless = headlessRaw === null ? true : headlessRaw === "true";

if (!url || !out) {
  usage();
  process.exit(2);
}

if (!Number.isFinite(waitMs) || waitMs < 0) {
  console.error("Invalid --wait-ms");
  process.exit(2);
}
if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
  console.error("Invalid --timeout-ms");
  process.exit(2);
}

fs.mkdirSync(out, { recursive: true });
const tracePath = path.join(out, "trace.zip");

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch (err) {
  console.error("Playwright is not installed. Install with: npm install -D playwright && npx playwright install");
  process.exit(2);
}

const browser = await chromium.launch({ headless });
const context = await browser.newContext();
await context.tracing.start({ screenshots: true, snapshots: true, sources: true });
const page = await context.newPage();
await page.goto(url, { waitUntil: "load", timeout: timeoutMs });
await page.waitForTimeout(waitMs);
await context.tracing.stop({ path: tracePath });
await context.close();
await browser.close();

fs.writeFileSync(path.join(out, "status.txt"), "OK\n");
console.log(tracePath);
