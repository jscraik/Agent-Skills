# HE Brainstorm Media Prompt Metadata

## Bespoke Framing

- skill name: he-brainstorm
- original state: synthetic eval drift and implicit brainstorm boundaries
- target state: evidence-gated ambiguity routing
- main weakness: eval cases omitted realistic declarations and several prompts
  lacked concrete task context; the entrypoint also hid anti-triggers, safety,
  and failure handling behind terse prose.
- main improvement: validator-clean eval realism plus explicit stage routing,
  safety boundaries, failure handling, output contract, and confidence semantics.
- validation evidence: strict audit pass, strict-audit security gate pass,
  OpenClaw pass through strict audit, direct `skill_gate.py` blocked after final
  patch by the Codex usage-limit approval guard, OpenAI format lint pass,
  progressive disclosure lint pass, markdownlint pass, Vale pass, lychee pass,
  Plugin Eval B/91 with invoke/deferred-cost warnings.
- artifact impact: edited canonical `SKILL.md`, `references/evals.yaml`, and
  wrapped markdown reference files; no review PNG persisted.
- confidence movement: 78% -> 88% capped by blocked post-patch smoke evals.

## `$imagegen` Prompt Output Contract

$imagegen

Use case: skill-specific technical infographic
Asset type: review artifact / X technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"HE Brainstorm: From Synthetic Eval Drift -> Evidence-Gated Ambiguity Routing"

Subtitle:
"A bespoke transformation map for he-brainstorm"

Context:
Review of the he-brainstorm Harness Engineering skill package. The patch fixed
validator-visible eval realism drift, tightened brainstorm routing boundaries,
added explicit failure and confidence behavior, and cleaned markdown reference
lint while preserving legacy validator headings.

Before state:

- missing `realistic` eval declarations
- synthetic eval prompts without concrete task context
- implicit anti-triggers and safety boundaries
- markdown reference line-length slop
- deferred context cost still heavy

After state:

- realistic eval declarations with concrete repo/artifact context
- strict audit and OpenAI format gates pass; `skill_gate.py` had passed before
  the final routing patch and was blocked afterward by the usage-limit guard
- explicit stage handoff, safety, failure, output, and confidence contract
- markdownlint-clean references
- remaining deferred-cost warning documented instead of hidden

Evidence shown:

- strict audit: pass
- OpenClaw: pass
- `skill_gate.py`: blocked after final patch
- OpenAI format lint: pass
- progressive disclosure lint: pass
- markdownlint/Vale/lychee: pass
- Plugin Eval: pass with invoke/deferred-cost warnings
- smoke evals: blocked after final patch by Codex usage-limit guard
- media persistence: blocked

Composition:
Create a dense but readable engineering poster with a central ambiguity-router
diagram. Left panel shows "synthetic eval drift" and implicit boundaries.
Center shows the he-brainstorm package anatomy: SKILL.md, evals.yaml,
references, command handle, Skill Factory gates. Right panel shows
"evidence-gated ambiguity routing" with stage handoff paths to he-spec,
he-plan, he-work, he-review, and done. Bottom evidence strip shows the real
validation statuses above, with direct `skill_gate.py`, smoke evals, release
evals, and media persistence marked blocked. Include a small residual-risk box
for invoke/deferred context cost.

Style:
Warm off-white technical-paper reference poster with dark ink, charcoal,
restrained amber, green, and red. Clear labelled zones, leader lines, crisp
engineering typography, no fake dashboard chrome.

Constraints:

- no fake dashboards
- no invented metrics
- no fake logos
- no generic "Codex Harness Skill" title
- no claims not supported by the review
- leave clean zones for deterministic overlay text
- use readable labels, not tiny filler text

Deterministic overlay text to add separately:

- he-brainstorm
- From Synthetic Eval Drift -> Evidence-Gated Ambiguity Routing
- Concrete evals, explicit handoff, validation-bound confidence
- strict audit pass; Plugin Eval B/91 warnings; smoke blocked by usage limit
