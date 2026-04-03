#!/usr/bin/env node
/**
 * Scaffold a React UI component + Storybook story + implementation spec.
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

const spec = `# ${name} — Component Spec

## Purpose
- Provide a reusable \`${name}\` surface with consistent intent and density variants.
- Keep behavior predictable and styling token-driven.

## Non-goals
- Do not encode business logic directly in this component.
- Do not hardcode brand colors outside the token system.

## API contract
- Component: \`${name}\`
- Props:
  - \`intent\`: \`default | brand | danger\` (default: \`default\`)
  - \`density\`: \`comfortable | compact\` (default: \`comfortable\`)
  - \`className\` and other \`HTMLAttributes<HTMLDivElement>\`

## Anatomy
- Root container uses semantic surface/foreground/border tokens.
- Intent variants map to border tokens.
- Density variants map to spacing tokens.

## Interaction and accessibility
- Preserves native semantics from the chosen root element.
- Supports keyboard interaction through parent-composed handlers.
- Must keep visible focus styles when made interactive by composition.

## Visual tokens
- Surface: \`--semantic-surface\`
- Foreground: \`--semantic-fg\`
- Border: \`--semantic-border\`
- Intent accents: \`--semantic-brand\`, \`--semantic-danger\`

## Storybook coverage
- \`Default\`: baseline rendering
- \`Brand\`: intent token mapping
- \`Danger\`: destructive-state styling
- \`Compact\`: density spacing contract

## Validation checklist
- [ ] Type-check passes for exported props.
- [ ] Stories render without runtime warnings.
- [ ] Token variables resolve in local theme.
- [ ] Intent and density attributes generate expected selectors.
`;

fs.writeFileSync(componentPath, component, "utf8");
fs.writeFileSync(storyPath, story, "utf8");
fs.writeFileSync(specPath, spec, "utf8");

console.log(`[scaffold_component] Created:
- ${componentPath}
- ${storyPath}
- ${specPath}`);
