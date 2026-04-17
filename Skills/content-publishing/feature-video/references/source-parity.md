# Source Parity Notes

## Table of Contents
- [Source inputs](#source-inputs)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)

## Source inputs
This package was refreshed against:
- `https://github.com/EveryInc/compound-engineering-plugin/tree/847ce3f156a5cdf75667d9802e95d68e6b3c53a4/Plugins/compound-engineering/skills/feature-video`

## Preserved behaviors
- browser PR walkthrough as the strongest concrete production path
- record-only fallback when no PR exists yet
- upload-only resume from an existing `.mp4`
- optional draft-PR creation to continue the flow
- base URL defaulting to `http://localhost:3000`
- explicit GitHub auth, upload validation, and cleanup safeguards
- requirement that uploaded PR videos resolve to native `user-attachments/assets/` GitHub URLs

## Intentional modernizations
- kept the local skill as a concise router rather than replacing it with the donor's single-file browser-upload workflow
- preserved broader production paths for `stitch-remotion`, `remotion`, and existing-artifact packaging
- moved donor operational detail into `Infrastructure/references/browser-pr-walkthrough.md` so `SKILL.md` stays short and routing-first
- added lightweight local package governance surfaces (`contract.yaml`, `evals.yaml`) for validation and future maintenance
