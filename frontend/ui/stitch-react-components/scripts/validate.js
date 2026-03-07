/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import swc from '@swc/core';
import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_TARGET_DIR = path.resolve(process.cwd(), 'examples');

function walkFiles(targetPath) {
  const items = [];

  const visit = (currentPath) => {
    const stat = fs.statSync(currentPath);
    if (stat.isFile()) {
      if (/\.(tsx?|jsx?)$/i.test(currentPath)) {
        items.push(currentPath);
      }
      return;
    }

    if (!stat.isDirectory()) {
      return;
    }

    for (const entry of fs.readdirSync(currentPath, { withFileTypes: true })) {
      const nextPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        visit(nextPath);
      } else if (entry.isFile() && /\.(tsx?|jsx?)$/i.test(entry.name)) {
        items.push(nextPath);
      }
    }
  };

  visit(targetPath);
  return items;
}

async function validateComponent(filePath) {
  let hasInterface = false;
  const tailwindIssues = [];

  const code = fs.readFileSync(filePath, 'utf-8');
  const filename = path.basename(filePath);

  try {
    const ast = await swc.parse(code, { syntax: 'typescript', tsx: true });

    const walk = (node) => {
      if (!node || typeof node !== 'object') {
        return;
      }

      if (node.type === 'TsInterfaceDeclaration' && node.id?.value?.endsWith('Props')) {
        hasInterface = true;
      }
      if (node.type === 'JSXAttribute' && node.name?.name === 'className') {
        if (node.value?.value && /#[0-9A-Fa-f]{6}/.test(node.value.value)) {
          tailwindIssues.push(node.value.value);
        }
      }

      for (const key in node) {
        const child = node[key];
        if (Array.isArray(child)) {
          for (const item of child) {
            walk(item);
          }
          continue;
        }
        walk(child);
      }
    };

    walk(ast);

    console.log(`--- Validation for: ${filename} ---`);
    if (hasInterface) {
      console.log('✅ Props declaration found.');
    } else {
      console.error("❌ MISSING: Props interface (must end in 'Props').");
    }

    if (tailwindIssues.length === 0) {
      console.log('✅ No hardcoded hex values found.');
    } else {
      console.error(`❌ STYLE: Found ${tailwindIssues.length} hardcoded hex codes.`);
      tailwindIssues.forEach((hex) => console.error(`   - ${hex}`));
    }

    if (hasInterface && tailwindIssues.length === 0) {
      return { ok: true, file: filePath };
    }

    return { ok: false, file: filePath };
  } catch (err) {
    console.error('❌ PARSE ERROR:', err.message);
    return { ok: false, file: filePath, error: err };
  }
}

async function main() {
  const rawTargets = process.argv.slice(2);
  let targets = [];

  if (rawTargets.length === 0) {
    if (!fs.existsSync(DEFAULT_TARGET_DIR)) {
      console.error(`❌ No targets provided and default path does not exist: ${DEFAULT_TARGET_DIR}`);
      process.exit(1);
    }
    targets = walkFiles(DEFAULT_TARGET_DIR);
  } else {
    for (const target of rawTargets) {
      if (!fs.existsSync(target)) {
        console.error(`❌ Not found: ${target}`);
        process.exit(1);
      }
      targets.push(...walkFiles(target));
    }
  }

  if (targets.length === 0) {
    console.error('❌ No component files found to validate.');
    process.exit(1);
  }

  const results = [];
  for (const filePath of targets) {
    const result = await validateComponent(filePath);
    results.push(result);
  }

  const okCount = results.filter((result) => result.ok).length;
  const failCount = results.length - okCount;

  if (failCount === 0) {
    console.log(`\n✨ COMPONENT VALID: ${okCount} file(s) passed.`);
    process.exit(0);
  }

  console.error(`\n🚫 VALIDATION FAILED: ${okCount} passed, ${failCount} failed.`);
  for (const result of results) {
    if (!result.ok) {
      console.error(`- ${result.file}`);
    }
  }
  process.exit(1);
}

main();
