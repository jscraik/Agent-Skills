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
4) OS/browser instrumentation (browser devtools, traces)
5) Authorized debug artifacts (symbols, debug builds) only
6) Stop if protections prevent further non-circumventive observation

## Browser/React apps
- If no sourcemaps: shift from "read code" -> "observe behavior".
- Capture HAR + Playwright trace to build endpoint/feature maps.
- If proxying is blocked: document observable domains/attempts and stop.

## OSS repos
- Use hotspots + dependency graphs + tests as architecture documentation.
- Add Semgrep/CodeQL for "worst-case" static coverage.
