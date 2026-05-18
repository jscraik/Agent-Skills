# From Heavy Plan Entrypoint -> Traceable Plan Contract

Use case: skill-review technical infographic
Asset type: review artifact / Harness Engineering skill hardening explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Heavy Plan Entrypoint -> Traceable Plan Contract"

Subtitle:
"A bespoke transformation map for he-plan"

Context:
The he-plan skill was reviewed as a Harness Engineering planning workflow. The patch compressed its always-loaded entrypoint, preserved planning-only safety boundaries, made eval prompts concrete, added explicit eval realism metadata, and kept detailed planning-depth, handoff, test, and visual guidance deferred in references.

Before state:

* Active entrypoint was structurally valid but heavy.
* All eval trigger cases lacked explicit realistic true/false metadata.
* Several eval prompts were synthetic or malformed, weakening validation realism.

After state:

* Compact planning contract with explicit status fields, handoff state, traceability, validation, rollback, and non-mutation boundaries.
* Realistic eval metadata and concrete HE planning scenarios remove strict audit and skill gate warnings.
* Plugin Eval improved from 91/B with heavy invoke cost to 95/A with moderate invoke cost; deferred-cost warning remains.

Evidence shown:

* strict audit: pass
* skill gate: pass
* OpenAI skill format: pass
* OpenClaw: pass via strict audit
* Plugin Eval: 91/B -> 95/A, invoke cost 2063 heavy -> 1716 moderate, deferred-cost warning remains
* package boundary checks: pass
* proof: reachable_without_outcome_proof
* smoke evals: blocked by 30s timeout
* media persistence: generation-blocked

Composition:
Create a precise engineering poster with three lanes. Left lane shows "Before" as a heavy plan entrypoint, missing eval-realism tags, and synthetic eval cards. Center lane shows "Patch" as focused edits to SKILL.md and evals.yaml, with traceability, plan-only boundaries, handoff state, and validation gates. Right lane shows "After" as a traceable plan contract: selected slice, plan IDs, acceptance IDs, validation, rollback, Linear/spec/plan/PR matrix, and post-plan handoff. Include an evidence strip with only the statuses listed above.

Style:
Professional engineering poster, dense but readable, restrained colour palette, crisp diagrammatic layout, high contrast labels, no decorative dashboard chrome.

Constraints:

* no fake dashboards
* no invented metrics
* no fake logos
* no unsupported claims
* no generic title unless accurate
* leave clean zones for deterministic overlay text
* use readable labels, not tiny filler text

Deterministic overlay text to add separately:

* he-plan
* From Heavy Plan Entrypoint -> Traceable Plan Contract
* Compact plan contract plus realistic eval metadata
* strict audit pass / skill gate pass / OpenAI format pass / Plugin Eval 95A / smoke blocked
* optimal within available evidence
