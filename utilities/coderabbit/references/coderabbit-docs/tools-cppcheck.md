---
source: https://docs.coderabbit.ai/tools/cppcheck
---

# Cppcheck

## Files
Cppcheck will run on files with the following extensions:

- `.cpp`

- `.cxx`

- `.cc`

- `.c`

- `.tpp`

- `.txx`

## Configuration
CodeRabbit will use the following settings based on the profile selected:
### Chill

`--disable=warning,style,information,portability,unusedFunction
`
### Assertive

`--disable=warning,style,information
`
CodeRabbit will use the default settings based on the profile selected if no config file is found.
## When we skip Cppcheck
CodeRabbit will skip running Cppcheck when:

- Cppcheck is already running in GitHub workflows.

## Filtered categories
The following categories are automatically filtered out in **Chill** mode:

- `normalCheckLevelMaxBranches` - too many branches

- `toomanyconfigs` - too many configurations

- `missingIncludeSystem` - missing system includes

- `missingInclude` - missing includes

- `unmatchedSuppression` - unmatched suppressions

## Profile behavior
In **Chill** mode:

- Disables: `warning`, `style`, `information`, `portability`, `unusedFunction`

- Suppresses the filtered categories listed above

- Only reports findings with severity “warning” or “error”

- Filters out the noisy categories listed above

In **Assertive** mode:

- Disables: `warning`, `style`, `information`

- Reports all findings regardless of category

- Does not suppress any categories

## Include directory discovery
Cppcheck automatically discovers top-level directories containing header files (`.h`, `.hpp`, `.hxx`, `.hh`) and adds them as include directories. This discovery is limited to a maximum depth of 5 levels to avoid scanning very large repositories.
## Links

- Cppcheck Configuration

Clang-Tidydetekt
