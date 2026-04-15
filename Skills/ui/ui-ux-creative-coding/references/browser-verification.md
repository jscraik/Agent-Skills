# Browser Verification Pass (agent-browser)

Use this when you need deterministic UI verification from a running dev server or Storybook. Ask before installing any new CLI dependency. If `agent-browser` is already installed, run a snapshot/screenshot pass.

## Suggested flow
1) Start the UI (Vite or Storybook).
2) Open the target URL.
3) Snapshot interactive elements.
4) Capture screenshots for review or Argos.

## Example commands
```bash
agent-browser open "http://localhost:5173"
agent-browser wait --load networkidle
agent-browser snapshot -i -c -d 6 --json > Infrastructure/artifacts/agent-browser/snapshot.json
agent-browser screenshot Infrastructure/artifacts/agent-browser/light.png
agent-browser set media dark
agent-browser screenshot Infrastructure/artifacts/agent-browser/dark.png
agent-browser close
```
