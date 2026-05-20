#!/usr/bin/env python3
"""SessionStart context for Skill Factory authors."""

from __future__ import annotations

import json


CONTEXT = """Skill Factory routing context:
- Author plugin lanes under Plugins/skill-factory/skills and attach skill-creator/skill-installer extras under skills-system/*/references/skill-factory.
- Route creation and scaffolding through the Codex .system skill-creator plus attached Skill Factory references.
- Route installation, listing, and browseability checks through the Codex .system skill-installer plus attached Skill Factory references.
- Route audit, hardening, and benchmark work to skill-builder.
- Route evidence folding, dedupe, pruning, and retirement work to skill-refactor.
- Route reusable workflow capture to skillify.
- Run the first-principles factory gate before create, harden, refactor, or skillify work.
- Identify the user outcome, copied assumption, smallest effective mechanism,
  artifact decision, and proof needed.
- Prefer IMPROVE_EXISTING, DOCS_ONLY, or DO_NOT_BUILD when a new skill would
  only copy a template or increase context load.
- Use route_skillset.py with --skill-set skill-factory when validating routed skill behavior.
- Prevent regressions with check_plugin_active_archive_links.py and check_skill_factory_system_overlays.py."""


def main() -> None:
    print(
        json.dumps(
            {
                "continue": True,
                "suppressOutput": True,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": CONTEXT,
                },
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
