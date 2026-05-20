$imagegen

Use case: skill-review technical infographic
Asset type: review artifact / technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Goal Board Drift -> Runtime-Reconciled Goal Governance"

Subtitle:
"A bespoke transformation map for goal-governor"

Context:
The goal-governor skill was reviewed and patched as a Codex governance skill. The patch aligned the skill with local Codex goal-runtime evidence, package contracts, eval prompts, board validator behavior, and Skill Factory gates while preserving validator-required legacy headings.

Before state:

* Native goal state and board state could drift without enough explicit reconciliation.
* Eval prompts and examples were flagged as weak or synthetic by Skill Factory checks.
* The board validator had a high-complexity YAML fallback and lacked native metadata checks before the current hardening work.

After state:

* Native goal identity, objective edits, budget-limited status, timestamps, and board receipts are reconciled before continuation.
* Skill package contracts, evals, references, and validator tests are aligned with the revised behavior.
* Validation evidence is explicit: strict audit, skill gate, OpenAI skill format, package boundary checks, deterministic tests, and Plugin Eval.

Evidence shown:

* strict audit: pass, with warning-level eval/example realism notes
* skill gate: pass, with warning-level eval/example realism notes
* OpenAI skill format: pass
* package boundary checks: pass
* deterministic checks: pass
* Plugin Eval: 77/100, grade C, residual deferred-cost failure
* smoke evals: fail, isolated runner output did not satisfy goal-governor acceptance regexes
* media persistence: fallback-only, no image generation tool available

Composition:
Create a dense but readable engineering poster. Left side: "Drift Risks" with three stacked panels for native goal status, repo board state, and stale receipts pulling apart. Center: "Governor Reconciliation" with a state-machine spine connecting goal_id, objective, budget_limited, timestamps, verifier freshness, and Judge/PM completion audit. Right side: "Validated Package" with compact check chips for strict audit, skill gate, OpenAI format, boundary check, deterministic tests, and Plugin Eval residual risk. Use a bottom evidence strip with pass, blocked, and residual-risk labels.

Style:
Professional engineering poster, crisp diagrammatic layout, restrained graphite, teal, amber, and red status accents, accessible contrast, no decorative fluff.

Constraints:

* no fake dashboards
* no invented metrics
* no fake logos
* no unsupported claims
* no generic title
* leave clean zones for deterministic overlay text
* use readable labels, not tiny filler text

Deterministic overlay text to add separately:

* goal-governor
* From Goal Board Drift -> Runtime-Reconciled Goal Governance
* Native goal state and repo board receipts reconcile before continuation
* strict audit pass | skill gate pass | OpenAI format pass | smoke eval blocked | Plugin Eval residual cost risk
* blocked by required runtime validation
