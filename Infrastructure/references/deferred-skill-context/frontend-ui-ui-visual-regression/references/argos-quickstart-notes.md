# Argos quickstart notes (user-provided)

## Playwright
- Install SDK: `@argos-ci/playwright`
- Configure Argos in Playwright config
- Capture screenshots via Argos helpers

## React Router
- Uses Playwright SDK (same as Playwright quickstart)

## Storybook (Vitest)
- Install: `@argos-ci/storybook`
- Add `argosVitestPlugin` to Vitest/Vite config alongside `storybookTest`
- Capture screenshots via test run; optional `argosScreenshot` in play function
- Screenshots output: `./screenshots`
- Add `./screenshots` to `.gitignore`

## Storybook (Test Runner)
- Install: `@argos-ci/cli`, `@argos-ci/storybook`, `@storybook/test-runner`
- Add `test-storybook` script with `NODE_OPTIONS=--experimental-vm-modules`
- Add `.storybook/test-runner.ts` with `argosScreenshot`
- Screenshots output: `./screenshots`
- Add `./screenshots` to `.gitignore`
- CI example includes build, run test runner, upload via `argos upload`

## Argos CLI
- Install: `@argos-ci/cli`
- Configure `ARGOS_TOKEN` (env var preferred)
- Upload: `argos upload ./screenshots`
- Debug: `DEBUG=@argos-ci/core`

## Node SDK
- Install: `@argos-ci/core`
- Upload via `upload({ root: "./screenshots" })`
- API reference: `https://js-sdk-reference.argos-ci.com`

## Baseline build (CI mode)
- Argos selects a baseline build by finding the most recent candidate build that:
  - has the same build name,
  - has all framework tests passed,
  - is auto-approved, manually approved, or orphan,
  - and whose commit is an ancestor of the merge base between the triggered build commit and the baseline branch.
- Baseline branch:
  - PR builds: base branch of the PR.
  - Push builds: default baseline branch configured in Argos project settings.
- Default baseline branch is the repo default branch (configurable).
- Auto-approved branches can be configured (default is baseline branch).
- Custom baseline via env:
  - `ARGOS_REFERENCE_BRANCH`
  - `ARGOS_REFERENCE_COMMIT`
- Orphan builds occur when no prior screenshots exist.

## Diff algorithm (overview)
- Deterministic pixel diffing (not AI).
- Compares rendered screenshots and ARIA snapshots.
- Uses odiff library; multi-pass thresholds, pixel clustering, diff mask/score.
- Flakiness is treated as technical debt; stabilize fonts/animations/time/layout.

## Build modes
- CI mode (default): compare against baseline build derived from Git history; PR checks fail on diffs until approved.
- Monitoring mode (opt-in): compares against latest approved build; Git history ignored; enable via `mode: "monitoring"` in SDK/CLI.

## Review & approval flow (CI mode)
- Diffs fail the PR check until reviewed in Argos.
- Reviewers approve intended changes or request fixes.
- Once approved, Argos updates the build status for the PR.

## Additional guides
- CI pipelines: `https://github.com/argos-ci/docs/tree/0d3d4cf18b3930663f5e21ab718de79431ba3064/docs/learn/guides/ci-pipelines`
- Visual coverage: `https://github.com/argos-ci/docs/tree/0d3d4cf18b3930663f5e21ab718de79431ba3064/docs/learn/guides/visual-coverage`
- Reliability: `https://github.com/argos-ci/docs/tree/0d3d4cf18b3930663f5e21ab718de79431ba3064/docs/learn/reliability`

## Common pitfalls (stability)
- Fonts: load deterministic fonts and avoid system fallback differences.
- Animations/transitions: disable or freeze; ensure deterministic timing.
- Async layout shifts: wait for stable rendering before capture.
- Time/locale: pin timezone and locale.
- Network data: mock or fixture responses to avoid drift.

## Playwright stabilization snippets (examples)

Disable animations (page-level CSS injection):
```ts
await page.addStyleTag({
  content: `
    *, *::before, *::after {
      animation: none !important;
      transition: none !important;
    }
  `,
});
```

Wait for fonts to load:
```ts
await page.evaluate(() => document.fonts?.ready);
```

Wait for stable layout (basic):
```ts
await page.waitForLoadState("networkidle");
await page.waitForTimeout(100);
```

## Playwright baseline screenshot helper (example)
```ts
import { argosScreenshot } from "@argos-ci/playwright";

// Use stable, semantic names for snapshots (component + state + viewport).
await argosScreenshot(page, "button/primary/default/desktop");
```

## Naming convention (recommended)
- Format: `component/variant/state/viewport`
- Examples:
  - `button/primary/default/desktop`
  - `modal/confirmation/open/compact`

## Storybook story naming → snapshot naming (guide)
- Prefer `title` + `storyName` as base, then append viewport.
- Example mapping:
  - Storybook: `Buttons/Primary` + `Default`
  - Snapshot: `buttons/primary/default/desktop`

## Viewport matrix (recommended)
- Desktop: `1440x900`
- Tablet: `768x1024`
- Mobile: `375x812`

## Accessibility snapshots (note)
- Argos compares ARIA snapshots alongside rendered screenshots (via Playwright).
- Use ARIA snapshots to catch semantic/accessibility regressions in addition to visual diffs.

## CI env variables (checklist)
- `ARGOS_TOKEN` (required unless using GitHub Actions integration that supplies it).
- `CI` (used by SDKs to enable uploads in CI-only).
- `ARGOS_REFERENCE_BRANCH` (optional custom baseline branch).
- `ARGOS_REFERENCE_COMMIT` (optional custom baseline commit).

## Secrets management (1Password CLI)
- Prefer 1Password secret references over plaintext `.env` values:
  - Example: `ARGOS_TOKEN=op://<vault>/<item>/credential`
- Use `op run -- <command>` to inject at runtime.
- Use `op inject -i <template> -o <config>` if a config file must be materialized.

## CI example (1Password + Argos CLI)
```sh
export ARGOS_TOKEN="op://<vault>/<item>/credential"
op run -- argos upload ./screenshots
```

## CI example (Playwright reporter + 1Password)
```ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  reporter: [
    ["dot"],
    [
      "@argos-ci/playwright/reporter",
      {
        uploadToArgos: !!process.env.CI,
        token: process.env.ARGOS_TOKEN,
      },
    ],
  ],
});
```
```sh
export ARGOS_TOKEN="op://<vault>/<item>/credential"
op run -- npx playwright test
```

## CI example (Storybook Vitest + 1Password)
```ts
import { defineConfig } from "vitest/config";
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";
import { argosVitestPlugin } from "@argos-ci/storybook/vitest-plugin";

export default defineConfig({
  test: {
    projects: [
      {
        extends: true,
        plugins: [
          storybookTest({ configDir: ".storybook" }),
          argosVitestPlugin({
            uploadToArgos: !!process.env.CI,
            token: process.env.ARGOS_TOKEN,
          }),
        ],
      },
    ],
  },
});
```
```sh
export ARGOS_TOKEN="op://<vault>/<item>/credential"
op run -- npx vitest --project storybook
```

## CI example (Storybook Test Runner + 1Password)
```ts
import type { TestRunnerConfig } from "@storybook/test-runner";
import { argosScreenshot } from "@argos-ci/storybook/test-runner";

const config: TestRunnerConfig = {
  async postVisit(page, context) {
    await argosScreenshot(page, context);
  },
};

export default config;
```
```sh
export ARGOS_TOKEN="op://<vault>/<item>/credential"
op run -- npm run test-storybook
```

## GitHub Actions (1Password CLI example)
```yml
steps:
  - uses: actions/checkout@v4
  - uses: 1password/load-secrets-action@v2
    with:
      export-env: true
    env:
      OP_CONNECT_HOST: ${{ secrets.OP_CONNECT_HOST }}
      OP_CONNECT_TOKEN: ${{ secrets.OP_CONNECT_TOKEN }}
      ARGOS_TOKEN: op://<vault>/<item>/credential
  - name: Run visual tests
    run: |
      op run -- npx playwright test
```

Note: wrap the actual visual test command with `op run` so secrets resolve at execution time.

## Token sourcing priority (recommended)
1. 1Password secret reference via `op run` (CI + local).
2. CI secrets manager/environment variables (if 1Password is unavailable).
3. Local developer env for ad-hoc testing (avoid committing `.env`).
