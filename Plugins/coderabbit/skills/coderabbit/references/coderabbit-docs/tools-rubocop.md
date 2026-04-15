---
source: https://docs.coderabbit.ai/tools/rubocop
---

# RuboCop

## Files
RuboCop will run on the following files and extensions:

- `.rb`

- `.arb`

- `.axlsx`

- `.builder`

- `.fcgi`

- `.gemfile`

- `.gemspec`

- `.god`

- `.jb`

- `.jbuilder`

- `.mspec`

- `.opal`

- `.pluginspec`

- `.podspec`

- `.rabl`

- `.rake`

- `.rbuild`

- `.rbw`

- `.rbx`

- `.ru`

- `.ruby`

- `.schema`

- `.spec`

- `.thor`

- `.watchr`

- `.irbrc`

- `.pryrc`

- `.simplecov`

- `buildfile`

- `Appraisals`

- `Berksfile`

- `Brewfile`

- `Buildfile`

- `Capfile`

- `Cheffile`

- `Dangerfile`

- `Deliverfile`

- `Fastfile`

- `Fastfile`

- `Gemfile`

- `Guardfile`

- `Jarfile`

- `Mavenfile`

- `Podfile`

- `Puppetfile`

- `Rakefile`

- `rakefile`

- `Schemafile`

- `Snapfile`

- `Steepfile`

- `Thorfile`

- `Vagabondfile`

- `Vagrantfile`

## Configuration
RuboCop uses a YAML style configuration file. We look for the following files anywhere in the repository:

- `.rubocop.yml`

- `.rubocop.yaml`

CodeRabbit will use the default settings based on the profile selected if no config file is found.
## What CodeRabbit runs
We run RuboCop inside a locked-down sandbox with an explicit `--config` that we generate or wrap. We do not load repository-specified Ruby plugins beyond a minimal safe set.
## Security policy and restrictions

- We skip RuboCop if the config (`.rubocop.yml`/`.rubocop.yaml`) includes unsafe `require` entries.

- Only a small, standardized `require` list is allowed. Custom gems/plugins loaded via `require` are blocked.

- The following `require` entries are currently allowed:

- `rubocop`

- `rubocop-performance`

- `rubocop-rails`

- `rubocop-rspec`

- `rubocop-minitest`

- `rubocop-rake`

- `rubocop-sequel`

- `rubocop-capybara`

- `rubocop-factory_bot`

- `rubocop-i18n`

- `rubocop-packaging`

- `rubocop-sorbet`

- `rubocop-thread_safety`

- `rubocop-graphql`

- `standard`

## When we skip RuboCop
CodeRabbit will skip running RuboCop when:

- The config contains `require` with disallowed entries.

- The config cannot be validated or parsed safely.

- RuboCop is already running in GitHub workflows.

## Links

- RuboCop Configuration
