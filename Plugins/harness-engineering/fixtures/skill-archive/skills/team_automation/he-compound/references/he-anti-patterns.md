# CE Compound Anti-patterns

Read when: you need the full anti-pattern catalog with corrective actions.

| Anti-pattern | Why it harms workflow quality | Corrective action |
|---|---|---|
| Treating `he-compound` as a substitute for all CE stages | Blurs boundaries and weakens stage-specific quality gates | Route to the correct downstream CE stage once mode is selected |
| Skipping upstream artifact validation | Carries hidden defects into later stages | Resume from the earliest incomplete or untrusted stage |
| Capturing unverified fixes as durable learnings | Pollutes the knowledge base with unstable guidance | Require solved and verified evidence before learning capture |
| Broadening `he-compound-refresh` without evidence | Creates maintenance churn and weak signal-to-noise | Recommend narrow, evidence-backed refresh scope only |
| Allowing helpers to write intermediate files in full mode | Breaks one-file-write contract and creates artifact sprawl | Helpers return text only; orchestrator writes final document |
| Creating a second solution doc for the same problem/root cause/solution | Increases drift risk and retrieval ambiguity | Refresh the high-overlap existing doc and add `last_updated` |
| Collapsing orchestration + learning capture into generic advice | Loses deterministic flow and clear outputs | Keep explicit mode split and output contract per mode |
| Fabricating stage evidence or cross-references | Undermines trust in workflow state and knowledge artifacts | Label assumptions and anchor claims to artifacts or verified context |
| Skipping the compound step after review | Misses institutional memory compounding | Capture the durable learning before closing the workflow |
| Lava flow acceptance (dead code/doc accumulation) | Increases cognitive load and stale guidance | Capture precise remediation and narrow follow-up maintenance |
| Documentation decay | Makes docs untrusted and avoided | Refresh selectively when evidence signals drift |
| Project Brain miss when `.harness/` exists | Splits knowledge across systems and loses discoverability | Dual-write and sync to Local Memory MCP per integration guide |
