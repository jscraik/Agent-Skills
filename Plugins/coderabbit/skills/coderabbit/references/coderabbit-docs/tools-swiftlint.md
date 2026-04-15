---
source: https://docs.coderabbit.ai/tools/swiftlint
---

# SwiftLint

## Files
SwiftLint will run on files with the following extensions:

- `.swift`

## Configuration
SwiftLint supports the following config files:

- User-defined config file set at `reviews.tools.swiftlint.config_file` in your project’s `.coderabbit.yaml` file or setting the “Reviews → Tools → SwiftLint → Config File” field in CodeRabbit’s settings page.

- `.swiftlint.yaml`

- `.swiftlint.yml`

CodeRabbit will use the default settings if no config file is found.
## When we skip SwiftLint
CodeRabbit will skip running SwiftLint when:

- SwiftLint is already running in GitHub workflows.

- The config file specifies a SwiftLint version greater than the version used by CodeRabbit.

## Ignored rules
The following SwiftLint rules are automatically ignored (style rules with very low acceptance):

- `trailing_whitespace`

- `line_length`

- `comment_spacing`

- `vertical_whitespace`

## Links

- SwiftLint Configuration
