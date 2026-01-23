# iOS / macOS probes (safe, non-circumventing)

## Static inventory (preferred)
- `file`, `otool -hv`, `otool -L`, `nm`, `strings`
- `codesign -dvv` for entitlements and signature metadata
- Bundle inventory: `Info.plist`, embedded frameworks, resources

## Dynamic observation (authorized only)
- Xcode Simulator for iOS targets (preferred for repeatability)
- Xcode logs and system logs (read-only observation)
- LLDB for debug builds you control; avoid attaching to protected apps without explicit authorization

## Notes
- Prefer simulator and debug builds over device-level inspection.
- Do not attempt jailbreak-based or bypass techniques in this workflow.
- If protections block observation, stop and request authorized builds or symbols.
