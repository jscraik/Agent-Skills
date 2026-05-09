#!/usr/bin/env python3
"""SessionStart context for Plugin Factory authors."""

from __future__ import annotations

import json


CONTEXT = """Plugin Factory bundled hook contract:
- Prefer plugin-bundled hooks at hooks/hooks.json and declare them in plugin.json as "./hooks/hooks.json".
- Codex hook config uses a top-level hooks object; each matcher group uses a hooks array.
- Command hooks use timeout in seconds. Do not generate timeoutSec.
- Plugin-owned commands should reference ${PLUGIN_ROOT} or ${PLUGIN_DATA}; avoid local absolute paths.
- Prompt, agent, and async hooks are not runtime-supported for plugin hooks yet; scaffold command hooks for behavior.
- plugin_hooks must be enabled alongside plugins and hooks before bundled plugin hooks load.
- Run plugin_builder.pyw validate before handing off a plugin package."""


def main() -> None:
    print(
        json.dumps(
            {
                "continue": True,
                "suppressOutput": True,
                "hookSpecificOutput": {
                    "additionalContext": CONTEXT,
                },
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
