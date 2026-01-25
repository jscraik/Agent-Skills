#!/usr/bin/env node
/**
 * Scaffold a React UI component + Storybook story + spec stub.
 *
 * Usage:
 *   node scripts/scaffold_component.mjs Button src/components/ui
 *
 * Notes:
 * - Keeps dependencies minimal (no clsx/cva required).
 * - You can refactor into your preferred patterns after scaffolding.
 */

import fs from "node:fs";
import path from "node:path";

function die(msg) {
  console.error(`[scaffold_component] ERROR: ${msg}`);
  process.exit(2);
}

const [name, outDir] = process.argv.slice(2);
if (!name || !outDir) {
  console.error("Usage: node scripts/scaffold_component.mjs <ComponentName> <outputDir>");
  process.exit(2);
}

if (!/^[A-Z][A-Za-z0-9]*$/.test(name)) {
  die("ComponentName must be PascalCase (e.g., Button, SettingsPanel).");
}

const absDir = path.resolve(process.cwd(), outDir);
fs.mkdirSync(absDir, { recursive: true });

const componentPath = path.join(absDir, `${name}.tsx`);
const storyPath = path.join(absDir, `${name}.stories.tsx`);
const specPath = path.join(absDir, `${name}.spec.md`);

if (fs.existsSync(componentPath) || fs.existsSync(storyPath) || fs.existsSync(specPath)) {
  die(`One or more files already exist in ${absDir} for ${name}.`);
}

const component = `import * as React from "react";

function cx(...parts: Array<string | undefined | null | false>) {
  return parts.filter(Boolean).join(" ");
}

export type ${name}Props = React.HTMLAttributes<HTMLDivElement> & {
  /**
   * Visual intent (map to tokens).
   * Add/remove intents as your system evolves.
   */
  intent?: "default" | "brand" | "danger";
  /**
   * Density affects spacing + type.
   */
  density?: "comfortable" | "compact";
};

export function ${name}({
  intent = "default",
  density = "comfortable",
  className,
  ...props
}: ${name}Props) {
  return (
    <div
      data-intent={intent}
      data-density={density}
      className={cx(
        // Base
        "rounded-md border px-4 py-3 text-sm",
        // Tokens (replace with your Tailwind v4 @theme tokens / CSS vars)
        "bg-[color:var(--semantic-surface)] text-[color:var(--semantic-fg)] border-[color:var(--semantic-border)]",
        // State styling examples
        "data-[intent=brand]:border-[color:var(--semantic-brand)]",
        "data-[intent=danger]:border-[color:var(--semantic-danger)]",
        "data-[density=compact]:px-3 data-[density=compact]:py-2",
        className
      )}
      {...props}
    />
  );
}
`;

const story = `import type { Meta, StoryObj } from "@storybook/react";
import { ${name} } from "./${name}";

const meta = {
  title: "UI/${name}",
  component: ${name},
  args: {
    intent: "default",
    density: "comfortable",
    children: "${name} content",
  },
} satisfies Meta<typeof ${name}>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Brand: Story = { args: { intent: "brand" } };

export const Danger: Story = { args: { intent: "danger" } };

export const Compact: Story = { args: { density: "compact" } };
`;

const spec = `# ${name} — Component Spec (stub)

Copy/paste the template from:
- assets/component-spec.md

Then fill in:
- purpose + non-goals
- anatomy/slots
- states + keyboard/focus
- tokens + motion
- Storybook coverage
`;

fs.writeFileSync(componentPath, component, "utf8");
fs.writeFileSync(storyPath, story, "utf8");
fs.writeFileSync(specPath, spec, "utf8");

console.log(`[scaffold_component] Created:
- ${componentPath}
- ${storyPath}
- ${specPath}`);
