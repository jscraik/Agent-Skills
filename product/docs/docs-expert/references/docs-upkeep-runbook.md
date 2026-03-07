# Docs Upkeep Runbook (Short)

Use this when maintaining docs over time.

## Versioning

- Add a visible "Last updated" date to top-level docs.
- Use semantic versioning for public API docs and note breaking changes.
- Keep a changelog for major docs when behavior changes.

## Deprecation

- Mark deprecated sections with a date and replacement link.
- Keep deprecated content for at least one release cycle.
- Remove only after migration guidance is published.

## Ownership

- Assign a clear doc owner per major doc.
- Require owner approval for structural changes.
- Review docs at least once per release.

## Brand and visibility drift checks

- Re-verify brand source-of-truth paths before major doc refreshes.
- For public repos, review topics, social preview, and repository description when README meaningfully changes.
- Reconfirm CODEOWNERS, SECURITY, and SUPPORT links remain valid.

## AI-doc consistency checks

- Keep agent-facing docs aligned with canonical human docs.
- If optional `llms.txt` exists, refresh it when core docs/commands change.
- Mark optional AI-only files clearly so maintainers do not mistake them for canonical policy docs.

## Metrics loop (Docs ROI)

Use this to track whether docs are working.

- Support deflection: track tickets or questions that docs should prevent.
- Onboarding time: measure time-to-first-success for new users.
- FAQ deflection: measure repeated questions before and after doc updates.
- Search success: track search terms that lead to page exits or "no results".
