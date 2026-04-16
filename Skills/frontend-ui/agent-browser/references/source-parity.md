# Source Parity Notes

## Table of Contents
- [Source inputs](#source-inputs)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)

## Source inputs
This package was refreshed against:
- `https://github.com/EveryInc/compound-engineering-plugin/tree/847ce3f156a5cdf75667d9802e95d68e6b3c53a4/Plugins/compound-engineering/skills/agent-browser`

## Preserved behaviors
- snapshot-first ref workflow as the default browser control model
- command chaining guidance for output-independent multi-step runs
- multiple auth strategies, including browser-imported state, persistent profiles, session names, and auth vault usage
- richer command-surface coverage for downloads, HAR capture, diffs, clipboard, annotated screenshots, and batch execution
- opt-in safety controls such as content boundaries, domain allowlists, action policy files, and output limits
- iOS provider and local-file access notes as advanced execution paths rather than wrapper defaults

## Intentional modernizations
- kept the local skill as a routing-first wrapper instead of replacing it with the donor's single-file command manual
- preserved the repo's progressive-disclosure pattern by moving donor-heavy command details into `Infrastructure/references/`
- added local package governance surfaces (`agents/openai.yaml`, `contract.yaml`, `evals.yaml`) so future refreshes are easier to validate and maintain
- kept explicit redaction and cautious-account handling language in the wrapper because this repo prefers stronger default safety framing than the donor
