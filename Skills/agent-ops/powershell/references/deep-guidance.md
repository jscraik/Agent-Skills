# PowerShell Deep Guidance

Read when: You are building production automation modules or high-risk mutating cmdlets.

## Cmdlet behavior
- Implement `SupportsShouldProcess` for state changes.
- Keep output object-based for pipeline composition.

## Automation safety
- Avoid interactive prompts in automation contexts.
- Use explicit parameter validation attributes.
