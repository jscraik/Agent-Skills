---
name: powershell
description: PowerShell cmdlet conventions for this project. Apply when writing or reviewing any .ps1 or module file.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Cmdlet Naming](#cmdlet-naming)
- [Parameter Design](#parameter-design)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for PowerShell script and module authoring/review.
- Use when automation safety and cmdlet consistency matter.

## Required inputs

- Script/module scope.
- Execution environment (local/CI/runner).
- Safety requirements (`WhatIf`, confirmation, permissions).

## Deliverables

- Consistent PowerShell cmdlets.
- Safe parameter and output patterns.
- Notes on automation behavior changes.

## Cmdlet Naming

- Use approved verbs with `Verb-Noun` naming.
- Keep nouns singular and domain-specific.
- Avoid aliases in scripts intended for automation.

## Parameter Design

- Use clear PascalCase parameter names.
- Use `[switch]` for flags instead of boolean string parameters.
- Support `-WhatIf` / `-Confirm` for mutating operations.

## Examples

```powershell
function Get-UserProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Username
    )

    process {
        [PSCustomObject]@{ Username = $Username }
    }
}
```

## Failure mode

- If a command mutates state without confirmation controls, stop and add safety switches.

## Gotchas

- `Write-Host` should not be used for pipeline data output.

## References and assets

- Open deep guidance: `references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
