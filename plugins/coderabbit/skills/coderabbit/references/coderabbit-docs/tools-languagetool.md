---
source: https://docs.coderabbit.ai/tools/languagetool
---

# LanguageTool

## Files
LanguageTool will run on files with the following extensions:

- `.md`

- `.mdx`

- `.markdown`

- `.txt`

The following files are excluded:

- `CMakeLists.txt`

- `requirements.txt`

## Configuration
LanguageTool’s style and grammar check depends on the language selected in CodeRabbit’s configuration. You can set the language by setting the `language` field in your project’s `.coderabbit.yaml` file or setting the “Review Language” field in CodeRabbit’s settings page.
LanguageTool only runs when the hosted LanguageTool service credentials are available in the CodeRabbit environment.
CodeRabbit allows further configuring LanguageTool by setting specific rules and categories to be enabled/disabled. This can be done under the `reviews.tools.languagetool` field in your project’s `.coderabbit.yaml` file or setting the various options under “Reviews → Tools → LanguageTool” in CodeRabbit’s settings page. The following options are available:

- `enabled` - Enable or disable LanguageTool.

- `enabled_rules` - Enable specific rules.

- `disabled_rules` - Disable specific rules.

- `enabled_categories` - Enable specific categories.

- `disabled_categories` - Disable specific categories.

- `enabled_only`- Enable only the rules and categories of IDs are specified with ‘enabledRules’ or ‘enabledCategories’.

- `level` - Set the level of feedback to be provided by LanguageTool. The following levels are available:

- `default` - Provides feedback on common issues.

- `picky` - Provides feedback on more issues, rules that you might only find useful when checking formal text.

## Default disabled categories and rules
The following categories are disabled by default:

- `TYPOS` - Typo detection

- `TYPOGRAPHY` - Typography issues

- `CASING` - Casing issues

The following rules are disabled by default:

- `EN_UNPAIRED_BRACKETS` - Unpaired brackets

- `EN_UNPAIRED_QUOTES` - Unpaired quotes

## Profile behavior
In **Chill** mode, LanguageTool filters out noisy rule patterns:

- `QB_NEW_EN*` - Experimental “There might be a mistake here” rules that generate many false positives

In **Assertive** mode, CodeRabbit still filters the noisy `QB_NEW_EN*` rules, but reports the remaining findings.
## Links

- LanguageTool Rules
