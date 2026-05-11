<!-- markdownlint-disable MD013 -->

# HE Compound Infographic Prompt

Generated: 2026-05-10

## Bespoke Framing

- Skill name: `he-compound`
- Original state: eval-realism drift and hidden lifecycle boundaries
- Target state: evidence-bound compound routing
- Main weakness: `evals.yaml` declared realistic trigger cases without enough concrete task context; the entrypoint also hid key failure, safety, handoff, and confidence contracts inside legacy prose.
- Main improvement: the patch adds explicit compound-mode boundaries, failure handling, handoff rules, confidence reporting, source-prompt/repeated-failure behavior, and concrete eval context while keeping legacy validator headings.
- Validation evidence: strict audit pass; `skill_gate.py` pass with no findings; OpenClaw pass with 0 critical/0 warn/2 info; OpenAI skill format lint pass; progressive disclosure lint pass; markdownlint pass; Vale pass; lychee offline pass; Plugin Eval 95/A with deferred-cost warning; smoke eval blocked by Codex usage quota after 4 passes; release eval blocked by the same quota.
- Artifact impact: `Plugins/harness-engineering/skills/he-compound/SKILL.md`, `references/evals.yaml`, and `assets/resolution-template.md` changed; runtime projection `.agents/**` was not edited; review media metadata is under `.harness/media/`.
- Confidence movement: 78% initial -> 88% final defensible confidence, capped by smoke/release live-runner quota and runtime outcome-proof gaps.

## `$imagegen` Prompt

$imagegen

Use case: skill-specific technical infographic
Asset type: review artifact / X technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"HE Compound: From Eval Drift and Hidden Boundaries -> Evidence-Bound Routing"

Subtitle:
"A bespoke transformation map for he-compound"

Context:
The he-compound skill was reviewed and patched as a compound Harness Engineering workflow. The patch tightened canonical ownership, validator-compatible legacy headings, source-prompt coverage, repeated-failure reconstruction, failure handling, human approval boundaries, and evidence-bound output. The eval fixture realism warnings were fixed, entrypoint invoke cost was reduced, and smoke/release runtime validation remains blocked by Codex usage quota.

Before state:

- eval cases declared realistic without enough concrete task context
- safety, failure, handoff, and confidence contracts were too implicit
- invoke cost was heavy and repeated guidance inflated the entrypoint
- smoke/release outcome proof depended on live Codex runner quota

After state:

- concrete eval contexts and explicit realistic declarations
- compact validator-compatible entrypoint with `Philosophy`, `Validation`, and `Gotchas`
- evidence-bound output contract for lifecycle state, source-prompt coverage, repeated failures, solution capture, Project Brain, and handoff
- Plugin Eval invoke cost reduced to moderate; deferred eval cost remains a documented warning

Evidence shown:

- strict audit: pass
- `skill_gate.py`: pass, no findings
- OpenClaw: pass, 0 critical / 0 warn / 2 info
- `openai_skill.py`: blocked, no local script found
- OpenAI skill format lint: pass
- progressive disclosure lint: pass
- Plugin Eval: pass, 95/A, deferred-cost warning
- smoke evals: blocked by Codex usage quota after 4 passing cases
- release evals: blocked by Codex usage quota
- media persistence: blocked for repository PNG copy because the active image tool reports no cache path before generation

Composition:
Use an execution/orchestration skill layout. Center panel: "compound lifecycle router" with lanes for repo evidence, Linear/PR state, session evidence, Project Brain, source-prompt baseline, repeated-failure evidence, and `.harness/solutions/**`. Left before panel shows eval drift, hidden boundaries, and heavy invoke cost. Right after panel shows explicit failure handling, handoff routing, confidence reporting, and validator-compatible headings. Bottom evidence strip uses pass/blocked/warn chips matching the validation statuses above. Include a small residual-risk box: "runtime outcome proof still needs live runner quota after May 12, 2026 6:11 PM." Leave clean zones for deterministic overlay text.

Style:
Warm off-white technical-paper reference poster; restrained charcoal, amber, green, and red; dense but readable engineering diagram; clean typography zones; leader lines; no fake dashboards; no fake logos; no invented metrics; no sci-fi styling; no glowing orbs; no generic abstract blobs; no tiny unreadable filler text.

Constraints:

- no fake dashboards
- no invented metrics
- no fake logos
- no generic "Codex Harness Skill" title
- no claims not supported by the review
- leave clean zones for deterministic overlay text
- use readable labels, not tiny filler text

Deterministic overlay text to add separately:

- he-compound
- HE Compound: From Eval Drift and Hidden Boundaries -> Evidence-Bound Routing
- Explicit lifecycle routing, source-prompt coverage, repeated-failure memory, and validator-compatible evidence gates
- Evidence: strict audit pass; skill_gate pass; OpenClaw pass; Plugin Eval 95/A warning; smoke/release blocked by quota
