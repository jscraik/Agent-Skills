# Contradictions and Cleanup

## Table of Contents

- [Open contradictions](#open-contradictions)
- [Resolved contradictions](#resolved-contradictions)
- [Flag for deletion](#flag-for-deletion)

## Open contradictions

- `CONTRIBUTING.md` still lists root-level `npm run check` as a required
  pre-merge gate, while [Tooling and Command Policy](/Docs/agents/02-tooling-policy.md)
  says the repository root has no package manager install step and package
  commands belong only to verified package roots. Keep the no-root-package
  contract unless a future package-root migration explicitly changes it.

## Resolved contradictions

- Root `AGENTS.md` previously mixed root-level repo guidance with detailed
  `ask`, robot-mode, skill-management, and browser-preview instructions.
  - Resolved by keeping only project-wide essentials in root `AGENTS.md`.
  - Moved command behavior to [Agent Operating Contract](/docs/agents/16-agent-operating-contract.md).
  - Moved skill lifecycle details to [Skill Management](/docs/agents/17-skill-management.md).
  - Moved browser fallback guidance to [Browser and Local Preview](/docs/agents/18-browser-and-local-preview.md).
- Root `AGENTS.md` and `AGENTS.md` previously told agents to source `Infrastructure/scripts/codex-preflight/codex-preflight.sh` and call `preflight_repo`.
  - Verified repo behavior is the CLI form: `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required`
  - Supported overrides were confirmed from the script help and live execution: `--repo-fragment`, `--bins`, `--paths`
  - See [Tooling Policy](/Docs/agents/02-tooling-policy.md) for current preflight command reference.
- Repo instruction examples previously mixed `/Users/jamiecraik/dev/agent-skills` and `/Users/jamiecraik/dev/Agent-Skills`.
  - Canonicalized docs to the verified workspace path: `/Users/jamiecraik/dev/Agent-Skills`
- Root `AGENTS.md` previously referenced stale npm paths:
  - `frontend/react-components/`
  - `Skills/video-transcript-downloader/`
- Canonical paths were verified from lockfiles and documented as:
  - `Skills/content-publishing/video-transcript-downloader/`
  - `Skills/frontend-ui/ui-ux-creative-coding/`

## Flag for deletion

- Remove root-level package-manager claims such as `npm run check` or `pnpm
check` from repo-wide policy docs unless a root `package.json` and lockfile
  exist and are verified.
- Remove repeated copies of `ask` command tables from root instruction surfaces;
  link to [Agent Operating Contract](/docs/agents/16-agent-operating-contract.md)
  instead.
- Remove generic browser-preview snippets from root instruction surfaces; link
  to [Browser and Local Preview](/docs/agents/18-browser-and-local-preview.md)
  instead.
- Remove stale references to `frontend/react-components/` and `Skills/video-transcript-downloader/` if they appear in downstream docs.
- Remove any remaining references to sourced `preflight_repo` helpers if they reappear in sibling instruction files.
