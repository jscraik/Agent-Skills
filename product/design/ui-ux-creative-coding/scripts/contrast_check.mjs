#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function hexToRgb(hex) {
  const m = /^#([0-9a-fA-F]{6})$/.exec(hex);
  if (!m) throw new Error(`Not a 6-digit hex: ${hex}`);
  const s = m[1];
  return [
    parseInt(s.slice(0, 2), 16),
    parseInt(s.slice(2, 4), 16),
    parseInt(s.slice(4, 6), 16)
  ];
}

function srgbToLin(c) {
  const v = c / 255;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
}

function relLum(hex) {
  const [r, g, b] = hexToRgb(hex);
  const R = srgbToLin(r);
  const G = srgbToLin(g);
  const B = srgbToLin(b);
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

function contrast(a, b) {
  const L1 = relLum(a);
  const L2 = relLum(b);
  const hi = Math.max(L1, L2);
  const lo = Math.min(L1, L2);
  return (hi + 0.05) / (lo + 0.05);
}

function getNested(obj, pathArr) {
  let cur = obj;
  for (const p of pathArr) {
    if (!cur || typeof cur !== "object" || !(p in cur)) return undefined;
    cur = cur[p];
  }
  return cur;
}

function resolveColor(value, tokens) {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`Missing color value: ${value}`);
  }

  if (/^#[0-9a-fA-F]{6}$/.test(value)) return value;

  const varMatch = /^var\((--[A-Za-z0-9-_]+)\)$/.exec(value);
  if (varMatch) {
    const varName = varMatch[1];
    const path = varName.replace(/^--colors?-/, "").split("-");
    const resolved = getNested(tokens.colors ?? {}, path);
    if (!resolved) throw new Error(`Unresolved token reference: ${value}`);
    return resolveColor(resolved, tokens);
  }

  throw new Error(`Unsupported color format: ${value}`);
}

function getTokenColor(tokens, pathArr, semanticKey) {
  const fromColors = getNested(tokens.colors ?? {}, pathArr);
  if (fromColors) return resolveColor(fromColors, tokens);

  if (semanticKey) {
    const fromSemantic = getNested(tokens.semantic ?? {}, [semanticKey]);
    if (fromSemantic) return resolveColor(fromSemantic, tokens);
  }

  throw new Error(`Missing color token: ${pathArr.join(".")}`);
}

function main() {
  const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
  const tokens = JSON.parse(fs.readFileSync(path.join(root, "assets", "tokens.json"), "utf8"));

  const pairs = [
    { fg: ["fg"], bg: ["bg"], label: "Body text on bg (AA >= 4.5)", semanticFg: "fg", semanticBg: "bg" },
    { fg: ["fg"], bg: ["surface"], label: "Body text on surface (AA >= 4.5)", semanticFg: "fg", semanticBg: "surface" },
    { fg: ["brand", "600"], bg: ["bg"], label: "Brand 600 on bg (AA >= 4.5)", semanticBg: "bg" },
    { fg: ["danger", "600"], bg: ["bg"], label: "Danger 600 on bg (AA >= 4.5)", semanticBg: "bg" }
  ];

  let ok = true;
  for (const p of pairs) {
    try {
      const fg = getTokenColor(tokens, p.fg, p.semanticFg);
      const bg = getTokenColor(tokens, p.bg, p.semanticBg);
      const ratio = contrast(fg, bg);
      const pass = ratio >= 4.5;
      console.log(`${p.label}: ${fg} on ${bg} => ${ratio.toFixed(2)} ${pass ? "OK" : "FAIL"}`);
      ok = ok && pass;
    } catch (e) {
      console.error(`${p.label}: ERROR: ${e.message}`);
      ok = false;
    }
  }
  process.exit(ok ? 0 : 2);
}

main();
