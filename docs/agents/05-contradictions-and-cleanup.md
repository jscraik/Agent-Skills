# Contradictions and Cleanup

## Table of Contents
- [Open contradictions](#open-contradictions)
- [Resolved contradictions](#resolved-contradictions)
- [Flag for deletion](#flag-for-deletion)

## Open contradictions
- None.

## Resolved contradictions
- Root `AGENTS.md` previously referenced stale npm paths:
  - `frontend/react-components/`
  - `utilities/video-transcript-downloader/`
- Canonical paths were verified from lockfiles and documented as:
  - `frontend/stitch-react-components/`
  - `product/content/video-transcript-downloader/`

## Flag for deletion
- Remove stale references to `frontend/react-components/` and `utilities/video-transcript-downloader/` if they appear in downstream docs.
