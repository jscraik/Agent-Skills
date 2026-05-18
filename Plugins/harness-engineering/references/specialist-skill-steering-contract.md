# Specialist Skill Steering Contract

Use this contract when a Harness Engineering stage needs domain expertise that
already exists in the available skill tree. The goal is to improve the current
HE artifact with the best available specialist context without turning the
pipeline into broad skill enumeration or route drift.

## Core Rule

Choose the best available skill for the evidence-backed domain need.

Do not hard-code a favorite specialist. Do not use CLI skills merely because the
word "command" appears. CLI, frontend, security, backend, mobile, data,
workflow, review, plugin, skill, and product strategy skills are all candidates
only when the current slice proves that their knowledge area materially improves
the brainstorm, spec, plan, work, review, or eval.

Apply `Infrastructure/references/openai-style-plugin-design-contract.md` when
the specialist choice changes side-effect class, context loading, validation
gates, or user steering. Specialist selection is a progressive-disclosure step:
resolve the narrowest useful capability, use only the relevant contract, and
record how it strengthened the current HE artifact.

## When to Use

Use specialist steering when the current HE stage has a concrete knowledge gap
that affects one of:

- acceptance criteria;
- implementation sequencing;
- validation gates;
- rollback or migration safety;
- user-facing workflow quality;
- agent-native discoverability;
- security, privacy, or operational risk;
- plugin or skill package correctness;
- domain-specific review or eval quality.

Examples:

- CLI behavior needs command tree, JSON contract, exit-code, dry-run, or
  agent-safe error handling expertise.
- Changed-scope review needs behavior-preserving simplification evidence; route
  to the external `simplify` / `agent-ops:simplify` skill as a specialist lens
  from `he-code-review` instead of copying simplification rules into HE.
- Frontend work needs interaction states, responsive behavior, accessibility, or
  visual verification.
- Security-sensitive work needs threat-model or validation review.
- Plugin or skill work needs package, manifest, browseability, eval, or
  progressive-disclosure expertise.
- Backend/API/data work needs typed boundary, migration, reliability, or data
  integrity expertise.
- Linear/governance work needs execution-state, issue-shape, or anti-noise
  expertise.

## Candidate Resolution

Prefer the live skill router and catalog over memory or guesses:

```text
./bin/ask skills route --json --top-k 5 --considered-limit 20 "<domain-specific intent>"
./bin/ask skills goal --json --top-k 5 --considered-limit 20 "<domain-specific intent>"
./bin/ask skills resolve <candidate-handle> --json
./bin/ask skills explain <candidate-handle> --json
```

Use `route` or `goal` when the domain is known but the handle is unknown. Use
`resolve` when a likely handle is known. Use `explain` or `resolve` to verify the
final selected handle before loading the specialist.

Routing output is advisory evidence, not authority. The selected specialist must
still match the proven domain, the stage need, and the approved scope. If routing
returns `unresolved_ambiguity`, do not guess. Use the ambiguity set as evidence
and apply `interactive-steering-contract.md` when the specialist choice would
materially change artifact quality, scope, sequencing, or validation gates. In
autonomous/headless mode, record `specialist_skill_status:
autonomous_assumption` or `specialist_skill_status: ambiguous` and proceed
conservatively without treating any specialist as authoritative.

If router output contains low-confidence or unrelated candidates, discard them
explicitly. Do not accept a candidate only because it appeared in
`selected_candidates`.

Use `./bin/ask skills list --json` only as a bounded inventory fallback when
route/goal cannot identify a candidate; filter locally by a narrow domain word or
category and do not dump the entire skill tree into context.

Select at most:

- one primary specialist skill; and
- one supporting specialist only when the slice clearly spans two domains.

If no suitable specialist exists, record `specialist_skill_status: none_found`
and continue with the HE stage.

## Selection Criteria

Pick the candidate that best satisfies all of:

- matches the proven domain, not a loose keyword;
- strengthens the current HE stage output;
- has a narrow enough scope to avoid context bloat;
- can add concrete acceptance, validation, sequencing, or risk evidence;
- does not override the selected HE lifecycle stage;
- does not expand the approved Linear/reframe/slice scope.

If two candidates remain equally valid and the choice changes artifact quality,
scope, or validation gates, apply `interactive-steering-contract.md` and ask
once. In autonomous/headless mode, record the conservative assumption instead.

Reject candidates when:

- the evidence is only keyword overlap;
- router confidence is low and no domain evidence supports the match;
- the candidate would pull the HE stage into a different lifecycle stage;
- the candidate would require broad context loading without clear artifact
  improvement;
- the candidate is useful in general but not needed for the current slice.

## Stage Use

- `he-brainstorm`: use a specialist only to improve option quality, rejection
  reasons, and survivor evidence.
- `he-spec`: use a specialist to sharpen acceptance criteria, behavioral
  boundaries, validation expectations, and non-goals.
- `he-plan`: use a specialist to improve sequencing, validation gates, rollback,
  risk handling, and implementation-unit boundaries.
- `he-work`: use a specialist only when implementing the approved slice in that
  domain; do not let the specialist reopen scope.
- `he-code-review`: use a specialist as a review lens for domain-specific risks
  or missing proof. When changed-scope simplification is the need, select the
  external `simplify` skill through this contract and keep HE responsible for
  traceability, risk, and review verdict.
- `he-eval-report`: use a specialist as an eval lens when closure depends on
  domain-specific proof.

## Trace Fields

When structured output is used, include:

```yaml
specialist_skill_status: used|none_found|ambiguous|autonomous_assumption|blocked
specialist_skill_primary: "<resolved skill handle or not_applicable>"
specialist_skill_supporting: "<resolved skill handle or not_applicable>"
candidate_command: "<route|goal|resolve|explain|list fallback>"
candidate_decision_status: "<resolved|unresolved_ambiguity|discarded|not_applicable>"
selection_evidence: "<repo/spec/plan/Linear evidence that justified selection>"
discarded_candidates: "<low-confidence or unrelated candidates discarded, if any>"
applied_to: "<brainstorm|spec|plan|work|review|eval>"
scope_guardrail: "<what the specialist must not expand>"
```

## Anti-Patterns

- Listing every available skill as context.
- Selecting a specialist from keyword overlap alone.
- Using a broad router skill when a narrow specialist is available.
- Letting a specialist skill replace the HE lifecycle route.
- Expanding the approved execution slice because the specialist suggests more.
- Asking the user to choose a specialist before the agent resolves obvious
  candidates.
- Treating CLI examples as privileged defaults.
