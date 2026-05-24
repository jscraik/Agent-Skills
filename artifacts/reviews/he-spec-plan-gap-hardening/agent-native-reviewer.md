## Agent-Native Architecture Review

### Summary
Harness Engineering has broad stage coverage and strong artifact-shape contracts, but the current surfaces still leave three high-risk agent-native gaps: runtime observability is effectively dark, scope-authority downgrade controls are not encoded in spec/plan contracts, and closure/report templates bias toward permissive defaults instead of fail-closed authority checks. The result is that agents can produce local artifacts while missing the same runtime/state certainty humans expect, especially for full-scope execution, closure safety, and persistent handoff continuity.

### Capability Map

| UI Action / Workflow Expectation | Location | Agent Surface | In Prompt / Contract? | Priority | Status |
|---|---|---|---|---|---|
| Route request to one HE stage deterministically | Plugins/harness-engineering/references/routing-map.json | he-router | Yes | Must | Partial (high false non-HE routing observed) |
| Produce durable spec with acceptance IDs and traceability | references/skills/he-spec/spec-artifact-contract.md | he-spec | Yes | Must | Partial (no explicit scope-authority/downscope guard) |
| Produce executable plan with rollback/validation | references/skills/he-plan/plan-artifact-contract.md | he-plan | Yes | Must | Partial (no explicit user authority confirmation fields) |
| Execute bounded code slice with proof | skills/he-work/SKILL.md | he-work | Yes | Must | Partial (no mandatory runtime/session persistence receipts) |
| Produce closure-grade eval report | references/skills/he-eval-report/eval-report-template.md | he-eval-report | Yes | Must | At risk (unsafe template defaults) |
| Verify runtime skill invocation telemetry | /private/tmp/he-session-collector-14d-bundle/skill-invocation-summary.json | session collector + HE analytics | No effective data | Must | Failed (no usable invocation telemetry) |

### Findings

#### Critical (Must Fix)
1. **Runtime observability gap blocks agent-native parity proof** -- `/private/tmp/he-session-collector-14d-bundle/skill-invocation-summary.json:2-6`, `/private/tmp/he-session-collector-14d-bundle/skill-refactor-handoffs.json` (aggregate evidence)
Description: invocation telemetry is `analytics_status: unavailable_or_legacy` with `invocation_count: 0`, while the handoff corpus still reports 1,075 records and high recurring failures (environment-blocker 1046, routing-mismatch 146). Agents cannot prove which HE stage was actually invoked in runtime, so closure and persistence claims are unverifiable.
Fix: add a mandatory runtime invocation receipt contract (`run_id`, `resolved_skill`, `resolved_source_path`, `session_id`, `timestamp`, `route_decision`) emitted by each HE stage and validated by a strict collector schema gate. Block HE closure recommendations when this receipt is missing.

2. **No encoded downscope-authority tripwire in HE spec/plan contracts** -- `/Users/jamiecraik/dev/coding-harness/.harness/implementation-notes/2026-05-21-full-implementation-downscope-steering-admission.md:28-41,58-75,79-83`, `Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md:26-55`, `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md:32-54`
Description: a known full-implementation downscope failure pattern exists (explicitly documented as missing deterministic tripwire), but HE spec/plan artifact contracts do not require explicit fields that bind scope reductions to user approval evidence.
Fix: extend both spec and plan contracts with required authority fields: `requested_scope`, `delivered_scope`, `scope_delta`, `scope_delta_reason`, `scope_delta_authorized_by`, `scope_delta_authorization_evidence`, and `full_implementation_status`. Add lint checks that fail if `scope_delta != none` without explicit authorization evidence.

3. **Eval template defaults can silently greenlight unsafe closure posture** -- `Plugins/harness-engineering/references/skills/he-eval-report/eval-report-template.md:120-124,137-142,204,219`
Description: template defaults prefill side-effect validator as `exempt/high`, `Blocks Completion: no`, drift as `Unknown`, and recommendation classification as `Blocked`/follow-up `Do Not Create` placeholders. In practice this mixes permissive and stale placeholders and invites report completion without real authority validation.
Fix: remove permissive defaults; require explicit value entry with `[REQUIRED]` placeholders and schema validation that rejects unchanged placeholders. Add fail-closed rules: if any protected-action evidence is absent, validator decision must be `not-run` and closure recommendation cannot be `Complete` or `Complete with follow-up`.

#### Warnings (Should Fix)
1. **he-work contract emphasizes bounded edits but does not require persistence receipts** -- `Plugins/harness-engineering/skills/he-work/SKILL.md:66-80`
Description: output template captures changed files and validation but not session continuity/state identity (no required `session_id`, artifact ledger key, or resume token). This weakens multi-turn/runtime persistence and cross-agent handoff reliability.
Recommendation: add required output fields: `session_id`, `artifact_chain_key`, `resume_token`, `authority_source`, `scope_hash`, and `runtime_visibility_evidence`. Add validator to reject he-work outputs without these fields.

2. **Routing map lacks explicit coding/testing persona lens routing cues** -- `Plugins/harness-engineering/references/routing-map.json:13-260`
Description: routing rules cover stage aliases but do not include explicit signals for coding persona and testing persona overlays requested by HE hardening goals.
Recommendation: add deterministic routing rules or handoff metadata for persona overlays (`coding-persona`, `testing-persona`) that attach to `he-spec`, `he-plan`, and `he-work` outputs, with a required `persona_lens_applied` field.

3. **Spec/plan contracts mention testing decisions but do not enforce persona-backed test strategy depth** -- `spec-artifact-contract.md:173-184`, `plan-artifact-contract.md:115-120`
Description: contracts require testing sections but do not force explicit test authority boundaries (what must be tested by agent vs human, and what is simulation-only).
Recommendation: add required subsections: `testing_authority_boundary`, `agent-executable tests`, `human-required checks`, and `runtime proof expectations`.

#### Observations
1. **HE data suggests environment blockers dominate, but closure surfaces currently classify implementation quality without mandatory environment ownership routing** -- bundle aggregate counts from `skill-refactor-handoffs.json` (environment-blocker 1046; approval_required/network/missing_file top blockers). Suggest adding blocker-owner mapping (`repo`, `runtime`, `permissions`, `external service`) as a required field in plan/eval artifacts.
2. **he-work already links to coding/testing literature lenses** -- `Plugins/harness-engineering/skills/he-work/SKILL.md:93-94`; this is a good base to expand into spec/plan/eval contracts for consistent persona-layer propagation.
3. **A meaningful fraction of records are non-HE routed (`route_to_he=false` in 417/1075 rows)** -- handoff dataset indicates a routing quality opportunity, not just implementation quality issues.

### Hardening Targets (Concrete Patch Set)
1. Add `scope-authority` schema and lints to:
   - `Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md`
   - `Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md`
   - New validator: `Plugins/harness-engineering/scripts/check_scope_authority.py`
2. Add runtime persistence receipt fields and validator to:
   - `Plugins/harness-engineering/skills/he-work/SKILL.md` output template
   - `Plugins/harness-engineering/references/skills/he-eval-report/eval-report-schema.json`
3. Remove permissive defaults and require explicit side-effect/drift decisions in:
   - `Plugins/harness-engineering/references/skills/he-eval-report/eval-report-template.md`
4. Add persona overlay mapping and emitted evidence fields in:
   - `Plugins/harness-engineering/references/routing-map.json`
   - `Plugins/harness-engineering/skills/he-spec/SKILL.md`
   - `Plugins/harness-engineering/skills/he-plan/SKILL.md`
   - `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`

### What's Working Well
- HE has strong stage decomposition and explicit mutation boundaries, especially in `he-work` and `he-router`.
- Spec and plan contracts already enforce durable IDs, traceability, and rollback posture.
- Eval-report contract is structurally rich and ready for strict fail-closed upgrades without redesign.

### Score
- **3/6 high-priority capabilities are fully agent-accessible**
- **Verdict:** NEEDS WORK

WROTE: /Users/jamiecraik/dev/agent-skills/artifacts/reviews/he-spec-plan-gap-hardening/agent-native-reviewer.md
