# Architecture Testing Limitations and Extensions

## Current Capabilities

diagram-cli architecture testing provides **import-pattern validation**:
- `must_not_import_from` - Block imports from patterns
- `may_import_from` - Whitelist allowed imports
- `must_import_from` - Require imports from patterns

## Known Limitations

The current implementation is **intentionally basic** and focuses on:
- Static import analysis
- Pattern-based matching
- Violation counting with baselines

### What it does NOT detect

| Missing Feature | Why It Matters |
|-----------------|----------------|
| Dependency directionality | Cannot enforce "imports flow inward" rules |
| API surface analysis | Cannot detect what's exposed vs internal |
| Abstraction level detection | Cannot verify layer abstraction compliance |
| Circular dependency depth | Cannot limit cycle length |
| Stability metrics | Cannot enforce "stable depends on volatile" |
| Semantic coupling | Cannot detect implicit dependencies |

## When to Use Alternatives

For more sophisticated architecture constraints, consider:

### dependency-cruiser

```bash
npm install --save-dev dependency-cruiser
```

Features:
- Dependency direction enforcement
- Circular dependency detection with depth
- Module boundary analysis
- Stability metrics (abstractness, distance from main)
- Orphan detection

### ArchUnit (Java/TypeScript)

For TypeScript:
```bash
npm install --save-dev @betterer/archunit
```

Features:
- Layered architecture rules
- Naming convention enforcement
- Slicing architecture support

### SonarQube / SonarLint

Features:
- Cognitive complexity
- Coupling between objects
- Lack of cohesion detection

## Future Improvements (Backlog)

The following enhancements are planned for diagram-cli:

| Priority | Feature | Description |
|----------|---------|-------------|
| P1 | Dependency directionality | Enforce "imports must flow downward" in layers |
| P1 | API surface analysis | Detect and constrain public vs private exports |
| P2 | Circular depth limits | Block cycles exceeding depth threshold |
| P2 | Stability scoring | Prevent stable modules from depending on volatile ones |
| P3 | Semantic coupling | Detect implicit relationships via naming/usage |

## Supplementing diagram-cli

Current recommended approach:

1. Use **diagram-cli test** for import boundary enforcement (fast, simple)
2. Use **dependency-cruiser** for sophisticated constraint types
3. Use **diagram generate** for visual architecture review
4. Use **diagram workflow pr** for change impact analysis

### Example: Combined setup

```json
// package.json
{
  "scripts": {
    "test:arch": "diagram test .",
    "test:deps": "depcruise --config .dependency-cruiser.js src",
    "test:all": "npm run test:arch && npm run test:deps"
  }
}
```

## Contributing

If you need more sophisticated patterns, contributions are welcome. The rule engine is extensible via `src/rules/types/`:

1. Create new rule type extending `base.js`
2. Register in `src/rules/factory.js`
3. Add schema in `src/schema/rules-schema.js`
4. Document in `docs/architecture-testing.md`
