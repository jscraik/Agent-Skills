# Worst-case Playbooks (Escalation Ladders)

Summary from `docs/reference/WORST_CASE_PLAYBOOKS.md`.

## Shared ladder
1) Baseline observation
2) Stimulus scenarios
3) Diff baseline vs stimulus
4) OS/browser instrumentation (Instruments, Web Inspector, traces)
5) Authorized debug artifacts only
6) Stop if protections block non-circumventive observation

Best practices:
- Keep baseline/stimulus inputs identical except the intentional change.
- Stop after two successive low-signal escalations.

## macOS apps
- Map bundle structure (Frameworks, Resources, Info.plist).
- Prefer OS-level instrumentation; avoid disabling protections.
- Use LLDB only on authorized debug builds.

## iOS Simulator
- Use simctl screenshots/video, Web Inspector, Instruments.
- If encrypted, stop and request debug builds/symbols.
- Pin simulator runtime/device for repeatable captures.

## Web/React apps
- If no sourcemaps: observe behavior; capture HAR + Playwright trace.
- Document blocked proxy attempts; redact secrets before sharing.
- Use React DevTools + bundle text search when available.

## OSS repos
- Use hotspots + dependency graphs + tests.
- Add Semgrep/CodeQL for worst-case static coverage.
