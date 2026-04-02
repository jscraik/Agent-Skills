---
source: https://docs.coderabbit.ai/tools/betterleaks
---

# Betterleaks

CodeRabbit's guide to Betterleaks, an improved secret scanner based on Gitleaks.

Betterleaks is a secret scanner built on top of Gitleaks. It offers enhanced secret detection compared to the original Gitleaks tool.

## Files

Betterleaks runs on changed files in the pull request, regardless of file type.

## Configuration

Betterleaks is configured using the `gitleaks` key in your `.coderabbit.yaml` file. The key name is preserved for backward compatibility, existing configurations continue to work without any changes.

```
reviews:
  tools:
    gitleaks:
      enabled: true
```

Betterleaks supports the following config files:

- `betterleaks.toml`
- `gitleaks.toml` (backwards compatibility)

## When we skip Betterleaks

CodeRabbit will skip running Betterleaks when:

- Gitleaks (or a compatible secret scanner) is already running in GitHub workflows.

## Notes

- Betterleaks runs on the changed files in the pull request (not just specific file types).
- Betterleaks uses `--no-git` flag, so it scans files directly rather than scanning git history.
- The configuration key in `.coderabbit.yaml` remains `gitleaks` for backward compatibility. No changes to your existing configuration are required.
