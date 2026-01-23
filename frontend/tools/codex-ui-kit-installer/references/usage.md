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

## Verify install (files, exec bits)
```bash
scripts/verify_ui_kit.sh /path/to/repo
```
