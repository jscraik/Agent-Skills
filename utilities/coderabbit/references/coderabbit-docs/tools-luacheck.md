---
source: https://docs.coderabbit.ai/tools/luacheck
---

# Luacheck

## Supported Files
Luacheck will run on files with the following extensions:

- `.lua`

## Configuration
Luacheck supports the following configuration files:

- `.luacheckrc`

- `luacheckrc`

- `.luacheckrc.lua`

- `luacheckrc.lua`

Luacheck does not require configuration to run. If no configuration file is found, it will use default settings.
## When we skip LuaCheck
CodeRabbit will skip running LuaCheck when:

- LuaCheck is already running in GitHub workflows.

## Ignored rules
The following LuaCheck rules are automatically ignored:

- `W113` - accessing undefined variable

- `W611` - line too long

- `W112` - line contains only whitespace

- `W631` - line that ends with whitespace

## Profile behavior
In **Chill** mode, LuaCheck only reports errors (not warnings).
In **Assertive** mode, LuaCheck reports both errors and warnings.
## Features
Luacheck can detect:

- Usage of undefined global variables

- Unused variables and values

- Accessing uninitialized variables

- Unreachable code

- And many more issues

## Links

- Luacheck GitHub Repository

- Luacheck Documentation
