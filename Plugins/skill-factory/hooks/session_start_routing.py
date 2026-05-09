#!/usr/bin/env python3
"""SessionStart context for Skill Factory authors."""

from __future__ import annotations

import json


CONTEXT = """Skill Factory routing context:
- Author and change canonical sources under Plugins/skill-factory/skills, not runtime projections.
- Route creation and scaffolding to skill-creator; route audit, hardening, and benchmark work to skill-builder.
- Route installation, listing, and browseability checks to skill-installer.
- Route evidence folding, dedupe, pruning, and retirement work to skill-refactor.
- Route reusable workflow capture to skillify.
- Use route_skillset.py with --skill-set skill-factory when validating routed skill behavior."""


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
