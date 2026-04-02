---
source: https://docs.coderabbit.ai/tools/eslint
---

# ESLint

## Files
ESLint will run on files with the following extensions: `.js`, `.ts`, `.cjs`, `.mjs`, `.d.cts`, `.d.mts`, `.jsx`, `.tsx`, `.css`, `.vue`, `.svelte`, `.astro`, `.graphql`, `.gql`, `.mdx`
## Configuration

- ESLint configuration is read from the repository and is used as is. No additional configuration is required.

- Please ensure that all ESLint dependencies are defined in your `package.json` file(s).

- Yarn and PNPM workspaces are supported.

- Private ESLint plugins or configurations are not supported at the moment. Please reach out to support if you would like us to add support for this.

- For `@typescript-eslint`, linting with type information is not supported at the moment. The type checking rules are disabled.

- For `eslint-plugin-import`, the following rules are disabled:

- `import/no-unresolved`

- For the `eslint-plugin-n`, the following rules are disabled:

- `n/no-missing-import`

- `n/no-missing-require`

- For the `eslint-plugin-node`, the following rules are disabled:

- `node/no-missing-import`

- `node/no-missing-require`

To enable or disable ESLint, use your `.coderabbit.yaml` file or the CodeRabbit web UI:
- .coderabbit.yaml
- Web UI
.coderabbit.yaml

`reviews:
 tools:
 eslint:
 enabled: true
`Go to **Reviews → Tools → ESLint** in your organization or repository settings and toggle ESLint `on` or `off`.
## Security policy and restrictions
ESLint runs in a sandbox. CodeRabbit scans ESLint config files before any `npm`/`yarn`/`pnpm` installs and only permits a curated allow-list of plugins.

- CodeRabbit extracts referenced plugins from configs (the `plugins` array, `extends: "plugin:..."`, `eslint-plugin-...` mentions).

- If any plugin outside the allow-list is referenced, CodeRabbit skips ESLint for the run.

- CodeRabbit does not install or execute arbitrary third-party plugins from the repository.

The following plugins are currently allowed, grouped by category:
CategoryPluginsTypeScript / Stylistic`@typescript-eslint`, `@stylistic`Import / Module`import`, `simple-import-sort`, `unused-imports`, `n`, `node`React ecosystem`react`, `react-hooks`, `react-native`, `jsx-a11y`, `next`Testing`jest`, `vitest`, `testing-library`, `cypress`, `playwright`, `mocha`Frameworks`vue`, `nuxt`, `angular`, `@angular-eslint`, `@angular-eslint/template`, `svelte`, `astro`, `solid`, `qwik`, `turbo`, `hydrogen`, `storybook`Code quality`sonarjs`, `security`, `unicorn`, `promise`, `regexp`, `compat`, `jsdoc`, `deprecation`, `lodash`, `boundaries`, `perfectionist`, `eslint-comments`Formatting`prettier`, `tailwindcss`Other`mdx`
## When CodeRabbit skips ESLint
CodeRabbit will skip running ESLint when:

- The config references a plugin not in the allow-list.

- The config can’t be parsed or is otherwise unsafe.

- No `package.json` can be found for the relevant project.

- No ESLint config file can be found.

## What’s next

## All supported toolsBrowse the complete list of linters, security analyzers, and CI/CD integrations available in CodeRabbit.

## Tools referenceExplore detailed specifications and capabilities of all available CodeRabbit tools.

## Configuration referenceFull reference for all available options, including how to enable, disable, and tune individual tools.

ember-template-lintFlake8
