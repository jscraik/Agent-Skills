---
name: process-watch
description: "Analyze system processes and resource usage to diagnose runaway processes. Use when investigating CPU/memory/IO spikes."
---

# Process Watch

Comprehensive system process monitoring. Goes beyond basic `top` to show:
- CPU & memory usage
- Disk I/O per process
- Network connections
- Open files & handles
- Port bindings
- Process trees

## Commands

### List processes
```bash
process-watch list [--sort cpu|mem|disk|name] [--limit 20]
```

### Top resource consumers
```bash
process-watch top [--type cpu|mem|disk|net] [--limit 10]
```

### Process details
```bash
process-watch info <pid>
# Shows: CPU, memory, open files, network connections, children, environment
```

### Find by name
```bash
process-watch find <name>
# e.g., process-watch find chrome
```

### Port bindings
```bash
process-watch ports [--port 3000]
# What's listening on which port?
```

### Network connections
```bash
process-watch net [--pid <pid>] [--established]
```

### Kill process
```bash
process-watch kill <pid> [--force]
process-watch kill --name "chrome" [--force]
```

### Watch mode
```bash
process-watch watch [--interval 2] [--alert-cpu 80] [--alert-mem 90]
# Continuous monitoring with threshold alerts
```

### System summary
```bash
process-watch summary
# Quick overview: load, memory, disk, top processes
```

## Examples

```bash
# What's eating my CPU?
process-watch top --type cpu

# What's on port 3000?
process-watch ports --port 3000

# Details on a specific process
process-watch info 1234

# Kill all Chrome processes
process-watch kill --name chrome

# Watch with alerts
process-watch watch --alert-cpu 90 --alert-mem 85
```

## Platform Support

- **macOS**: Full support
- **Linux**: Full support  
- **Windows**: Partial (basic process list, no lsof equivalent)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.

- Encourage variation: adapt steps for different contexts and enable creative exploration.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.
- If context differs, customize steps to fit the situation.

## Antipatterns
- Do not add features outside the agreed scope.
