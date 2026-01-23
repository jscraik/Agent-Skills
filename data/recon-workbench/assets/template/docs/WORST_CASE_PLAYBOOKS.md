# Worst-case Playbooks (Escalation Ladders)

Use these when the target is low-signal:
- stripped symbols / heavily optimized native builds
- hardened runtime / reduced introspection
- minified web bundles with no sourcemaps
- TLS interception blocked (pinning / policy)

## Shared escalation ladder
1) Baseline observation
2) Stimulus scenario(s)
3) Diff baseline vs stimulus
4) OS/browser instrumentation (Instruments, Web Inspector, traces)
5) Authorized debug artifacts (symbols, debug builds) only
6) Stop if protections prevent further non-circumventive observation

## macOS apps (Mach-O / .app)
- Always: map app bundle structure (Frameworks, Resources, Info.plist).
- If static is thin: infer capabilities from:
  - linked frameworks + entitlements + strings
  - runtime observation via Instruments + unified logs
- Avoid "fight the protections": prefer OS-level instrumentation.

## iOS Simulator
- Use simctl screenshot/video for state evidence.
- Use Safari Web Inspector for web content (WKWebView).
- Use Xcode/Instruments for native behavior.
  Note: Web Inspector inspects web content; it does not provide native Swift call stacks.

## Browser/React apps
- If no sourcemaps: shift from "read code" -> "observe behavior".
- Capture HAR + Playwright trace to build endpoint/feature maps.
- If proxying is blocked: document observable domains/attempts and stop.

## OSS repos
- Use hotspots + dependency graphs + tests as architecture documentation.
- Add Semgrep/CodeQL for "worst-case" static coverage.
