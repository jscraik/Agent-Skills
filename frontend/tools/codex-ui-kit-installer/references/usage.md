# Usage reference

## Install kit into a repo
```bash
scripts/install_kit.sh --repo /path/to/repo
```

## Install kit + prompts
```bash
scripts/install_kit.sh --repo /path/to/repo --install-prompts
```

## Dry run (no changes)
```bash
scripts/install_kit.sh --repo /path/to/repo --dry-run
```

## Verify expected files (no changes)
```bash
scripts/install_kit.sh --repo /path/to/repo --verify
```

## Overwrite existing files
```bash
scripts/install_kit.sh --repo /path/to/repo --force
```

## Install prompts to a custom directory
```bash
scripts/install_kit.sh --repo /path/to/repo --install-prompts --prompts-dir /path/to/prompts
```

## Verify install (files, exec bits, simctl availability)
```bash
scripts/verify_ui_kit.sh /path/to/repo
```

## Open a web app in iOS Simulator (iPad 13" Safari)
```bash
bin/ios-web --profile ipad_13 --port 5173 --path / --snap ./artifacts/ipad13.png
```

## Use Xcode-beta toolchain
```bash
bin/ios-web --developer-dir /Applications/Xcode-beta.app/Contents/Developer --port 5173
```

## List available simulators
```bash
bin/ios-web --list-profiles
```

## Storybook preset (iPad 13", port 6006)
```bash
bin/ios-web-storybook --path /
```

## OpenAI widget preset (iPad 13", port 5173)
```bash
bin/ios-web-openai --path /
```

## List resolutions / available devices
```bash
bin/ios-web --list-profiles
bin/ios-web --print-resolution
```
