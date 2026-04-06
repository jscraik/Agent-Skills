# Contradictions and Cleanup

## Table of Contents
- [Open contradictions](#open-contradictions)
- [Resolved contradictions](#resolved-contradictions)
- [Flag for deletion](#flag-for-deletion)

## Open contradictions
- None.

## Resolved contradictions
- Root `AGENTS.md` and `CLAUDE.md` previously told agents to source `scripts/codex-preflight.sh` and call `preflight_repo`.
  - Verified repo behavior is the CLI form: `bash scripts/codex-preflight.sh --stack auto --mode required`
  - Supported overrides were confirmed from the script help and live execution: `--repo-fragment`, `--bins`, `--paths`
  - See [Tooling Policy](/docs/agents/02-tooling-policy.md) for current preflight command reference.
- Repo instruction examples previously mixed `/Users/jamiecraik/dev/agent-skills` and `/Users/jamiecraik/dev/Agent-Skills`.
  - Canonicalized docs to the verified workspace path: `/Users/jamiecraik/dev/Agent-Skills`
- Root `AGENTS.md` previously referenced stale npm paths:
  - `frontend/react-components/`
  - `utilities/video-transcript-downloader/`
- Canonical paths were verified from lockfiles and documented as:
  - `frontend/stitch-react-components/`
  - `product/content/video-transcript-downloader/`

## Flag for deletion
- Remove stale references to `frontend/react-components/` and `utilities/video-transcript-downloader/` if they appear in downstream docs.
- Remove any remaining references to sourced `preflight_repo` helpers if they reappear in sibling instruction files.
