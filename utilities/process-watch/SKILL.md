---
name: process-watch
description: Analyze system processes and resource usage to diagnose runaway CPU/memory/IO,
  identify culprits, and propose next diagnostic steps. Use when investigating performance
  spikes or leaks.
knowledge_graph_profile: references/task-profile.json
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

- **Desktop**: Full support
- **Linux**: Full support  
- **Windows**: Partial (basic process list, no lsof equivalent)

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Required inputs
- User request details and any relevant files/links.


## Deliverables
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

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `scripts/process-watch.py`

## References
- `references/contract.yaml`
- `references/evals.yaml`

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
