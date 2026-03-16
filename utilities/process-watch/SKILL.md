---
name: process-watch
description: Analyze system processes and resource usage to diagnose runaway CPU/memory/IO, identify culprits, and propose next diagnostic steps. Use when investigating performance spikes or leaks.
---

# Process Watch

Diagnose process-level resource issues with the bundled process-watch workflow instead of relying on a single `top` snapshot.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Workflow](#workflow)
- [Anti-patterns](#anti-patterns)
- [Validation](#validation)
- [Examples](#examples)
- [References](#references)

## Standards snapshot
- Prefer evidence across CPU, memory, I/O, network, and process hierarchy before naming a culprit.
- Capture enough context to explain what is happening now and what to inspect next.
- Treat kill operations as explicit user-directed actions, not default remediation.
- Keep platform differences explicit, especially where Windows support is partial.

## When to use
- The user is investigating runaway CPU, memory growth, disk churn, or suspicious background work.
- A port, process, or system resource spike needs process-level attribution.
- The user needs a quick watch loop or summary of top offenders before deeper debugging.

## Required inputs
- The symptom or target:
  - high CPU;
  - memory leak suspicion;
  - port collision;
  - disk churn;
  - network-heavy process.
- Optional PID, process name, or port number.
- Whether the task is diagnostic only or includes an explicit request to terminate a process.

## Deliverables
- A clear shortlist of suspected culprit processes.
- Process evidence such as CPU, memory, network, file handles, or children.
- Safe next-step guidance based on the observed signal.

## Philosophy
- Diagnose before acting.
- Prefer multi-signal evidence over a single noisy metric.
- Keep remediation proportional to the user’s request and system risk.

## Failure mode
- If the issue is broader system tuning or app-level profiling rather than process inspection, route to a more specific debugging or performance workflow.
- If the user wants destructive process termination without confirming target context, pause and make the impact explicit.
- If the platform lacks the requested visibility, say what is unavailable rather than pretending the signal exists.

## Constraints
- Redact secrets, environment variables, and sensitive command-line arguments by default in outputs.
- Do not kill or force-kill processes unless the user explicitly requests it.
- Keep guidance scoped to local process diagnostics rather than unrelated system administration work.

## Workflow
1. Start with a summary or top view to identify likely offenders.
2. Narrow into the specific process using PID, name, or port where possible.
3. Inspect the strongest relevant details:
   - CPU and memory;
   - network connections;
   - open files;
   - child processes;
   - port bindings.
4. Decide whether the evidence suggests:
   - a transient spike;
   - a stable heavy process;
   - a likely leak;
   - or a collision or runaway background task.
5. Recommend the smallest safe next step.

## Anti-patterns
- Declaring a root cause from one `top` snapshot.
- Killing processes reflexively when diagnostics are still incomplete.
- Ignoring child-process trees, open ports, or I/O when CPU alone is inconclusive.

## Validation
- Fail fast: stop at the first unavailable command or unsupported platform capability and report that gap.
- Verify the observed process identity matches the user’s target before recommending termination or escalation.
- Cross-check at least two useful signals when accusing a process of runaway behavior.

## Examples
```bash
# What's eating CPU?
process-watch top --type cpu

# What is listening on port 3000?
process-watch ports --port 3000

# Inspect a specific process
process-watch info 1234

# Watch with threshold alerts
process-watch watch --interval 2 --alert-cpu 90 --alert-mem 85
```

## References
- Script: `scripts/process-watch.py`
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`

## See Also

| Skill | When to use together |
|---|---|
| [[systematic-debugging]] | Use alongside process-watch for root-cause diagnosis |
| [[codex-home-audit]] | Check process health during a Codex home audit |
| [[fix-mise]] | Diagnose mise shim CPU/memory issues via process-watch |
| [[verification-before-completion]] | Confirm processes are healthy before marking work done |

**Topic map:** [[mobile-native]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
