# Skill Builder Discovery Interview

## Request user input mini-templates

## Inputs

Round 1 question:

What should this skill help you do?

What exact skill path or package should this work improve?

Which finding, failing score, or gate should I fix first?

Why this matters: skill-builder must patch canonical source and keep one focused failing gate visible.

Am I allowed to edit the canonical skill source, or should I only review and report?

## Copy paste payload examples

Ambiguous target:

What exact skill path or package should this work improve?

Ambiguous canonical source:

Which canonical source/path should I edit before changing files? Edit canonical sources, not runtime projections: use the plugin source under `Plugins/**/skills/**` and do not edit generated `.agents/**` projections. See `./Docs/agents/14-path-ownership-boundaries.md`.

Ambiguous evidence:

Which finding or score should we fix first?

## Round 6: Confirmation

## Skill Summary

Target path:

Failing eval/score:

Allowed edits:

Validation command:

Does this capture the skill-builder work well enough for me to implement?

Anything to add or change before I implement it?
