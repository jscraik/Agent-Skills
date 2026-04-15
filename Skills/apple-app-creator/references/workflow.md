# App Creator workflow

1. Run doctor to verify Xcode, XcodeGen, and CLI tools.
2. Choose mode:
   - `new`: scaffold app
   - `adopt`: apply app-builder workflow into existing project
3. Apply platform defaults:
   - iOS deployment target: `18.0`
   - macOS deployment target: `15.4`
4. Apply git onboarding policy:
   - `--git-init auto|never`
   - `--git-commit prompt|always|never`
5. Print next commands.

Defaults
- Project mode: `new`
- Platform: `ios`
- UI: `swiftui`
- iOS deployment target: `18.0`
- macOS deployment target: `15.4`
- iOS simulator: `auto`
- Git init: `auto`
- Baseline commit: `prompt`

Required dependency
- XcodeGen is required by default for new scaffolding: `brew install xcodegen`

Optional onboarding
- Run `skills/app-builder/Infrastructure/scripts/init.sh` for interactive prompts.
- Use `--no-prompt` with explicit flags for non-interactive flows.

Adopt mode constraints
- Existing-project mode is non-destructive and does not regenerate app sources.

Tooling behavior
- App creator owns scaffold and adoption flow only.
- Auto-commit is skipped for pre-existing dirty repos to avoid sweeping unrelated edits.
