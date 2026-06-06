# PU-011 Adversarial Review: Contract Runtime
## Findings

1. **High** - The no-Any ban can be satisfied while the live robot envelope still uses Any.
   - **Evidence:** Spec FR-001/FR-004 and AC-011/AC-012 at line 121-125 and line 243-263 scope the AST check to typed_contracts.py plus future contract, schema, and artifact files. The actual public envelope module is Infrastructure/scripts/lib/ask/envelope.py:73-85, where CallResult.metadata, CallResult.data, and CallResult.telemetry are still typed as dict[str, Any].
   - **Problem:** The spec names robot envelopes as an in-scope typed surface, but the filename scope does not include the real envelope implementation. A change can leave the public --json --robot envelope loose and still pass PU-011.
   - **Impact:** The typed-artifact gate can report success while the top-level robot contract still allows untyped drift in the public envelope.
   - **Recommended fix:** Expand the no-Any scope to include Infrastructure/scripts/lib/ask/envelope.py and any other public output-envelope modules, or replace the filename glob with a package-level inclusion rule for all emitted robot/public contract modules.

2. **High** - Pydantic and JSON Schema are not pinned to one authoritative source of truth.
   - **Evidence:** Spec FR-002, FR-006, FR-009, and FR-027 at line 122-129 and line 147 require both validators but do not define which layer wins on optionality, additionalProperties, or nullability. The current implementation already diverges: Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py:1-109 models cleanup/file actions and lockfile changes differently from Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json:1-84, Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json:1-51, and Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json:1-32.
   - **Problem:** The spec says the implementation should validate against both layers, but it never requires a parity check or a canonical generation direction. That leaves room for one layer to accept payloads the other rejects, especially around cleanup file_action.additionalProperties, lockfile change required fields, and receipt-shaped fields that only exist on one side.
   - **Impact:** AC-002 through AC-005 can pass while real command output still disagrees between the runtime Pydantic model and the published schema, which turns the gate into a false-green check.
   - **Recommended fix:** Add an explicit model/schema parity test or generate one layer from the other, and state in the spec which layer is authoritative for required fields, optional fields, nullability, and extra-key handling.

3. **Medium** - The validation scope can miss public envelope/output changes and still look complete.
   - **Evidence:** FR-021 and FR-023 at line 141-143 and line 143 use ideally and nearest existing scope mechanism language, while the changed-file trigger list omits Infrastructure/scripts/lib/ask/envelope.py and other wrapper output surfaces. The live robot envelope behavior is exercised in Infrastructure/tests/test_ask_repo_surface.py:29-42, which asserts top-level status, metadata.command, trace_id, and nested data fields.
   - **Problem:** The spec scopes PU-011 to schemas, SDK contract modules, SDK command modules, SDK tests, SDK specs/plans, and HTML artifacts, but it does not clearly include the wrapper envelope modules that actually emit the public JSON envelope. That means a change to the envelope or output wrapper can bypass the PU-011 gate.
   - **Impact:** The gate can stay green while the top-level robot response shape regresses on real --json --robot output.
   - **Recommended fix:** Name one exact validation entrypoint, make unknown validation scopes fail closed, and include all public envelope/output modules in the changed-file trigger set.

4. **Medium** - Manifest/frontmatter typing is underspecified across source and projection contracts.
   - **Evidence:** FR-001, FR-010, FR-012, FR-013, and FR-030 at line 121, line 130, line 132-133, and line 150 say the slice covers SkillManifestFrontmatter and manifest/frontmatter, but the current source fixture and schema split live in Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md:1-10 and Infrastructure/config/schemas/skills-sdk/manifest-source.v1.schema.json:1-24.
   - **Problem:** The spec never says whether SKILL.md source frontmatter and manifest-source metadata are the same contract, which fields are required for each artifact class, or how source-only versus projection-only fields are distinguished.
   - **Impact:** An implementation can validate the wrong layer, accept incomplete source frontmatter, or reject legitimate projection-only metadata while still satisfying the current acceptance language.
   - **Recommended fix:** Split source-frontmatter and manifest-projection into separate typed contracts with explicit required/optional fields and artifact-class-specific fixtures.

## Residual Risks
- Markdown and HTML parsing details are still partly heuristic in the spec, so edge cases around heading equivalence and DOM extraction could still produce false positives or false negatives.
- I did not execute the full repo validation lane; this review is based on current repo evidence and the spec text.

## Verdict
changes_requested

WROTE: .harness/review-artifacts/pu-011-adversarial-contract-runtime.md
