# Skills SDK Authoring Contract

## Purpose

`references/contract.yaml: authoring_contract` is the deterministic admission
contract for a package that selects the
`skills-sdk.gold-standard.v1` rubric profile. It validates authoring structure
and its bindings to controlled scenarios. It does not claim that a package is
runtime-ready, externally evaluated, published, or behaviorally proved merely
because package verification passes.

Run the read-only admission check with:

```bash
./bin/ask skills package verify <skill-path> --json --robot
```

A failed field returns a typed `authoring_*` blocker in the package receipt.

## Canonical Rules And Their Enforcement

| Rule                           | Contract surface                                                       | Deterministic enforcement                                                                                                                                                                                 | Evidence lane still required                                                      |
| ------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| One primary job                | `primary_job.outcome`, `primary_job.refusal_boundary`                  | Both non-empty                                                                                                                                                                                            | Controlled scenarios prove the outcome/refusal behavior.                          |
| Declare invocation mode        | `invocation.mode`, `rationale`, `context_load`, `load_control`         | Mode must match frontmatter `disable-model-invocation`.                                                                                                                                                   | Runtime activation proves routing and operator load.                              |
| Important rules state why      | `critical_rules[].rationale_source`, `rationale_text`                  | The rationale must occur exactly once in the named level-two SKILL.md section, outside fenced examples.                                                                                                   | Scenarios prove that the rationale changes behavior.                              |
| Separate steps from references | `reference_routes[]`                                                   | Each route is package-local, non-symlinked, mentioned in executable SKILL.md text, has `read_when`, and maps to controlled scenarios.                                                                     | Package/reference quality and scenario use.                                       |
| Keep the entrypoint minimal    | `entrypoint.max_lines`, `section_roles`, `reject_duplicate_paragraphs` | The entrypoint remains within the 360-line split budget; every direct section has an operational role; duplicate headings and non-trivial paragraphs block.                                               | Quality review still judges prose usefulness.                                     |
| Stable steering vocabulary     | `steering_terms[]`                                                     | Terms are unique, defined, and used in executable SKILL.md text.                                                                                                                                          | Scenarios prove consistent use under pressure.                                    |
| Split overloaded phases        | `phase_model`                                                          | A declared `single` model cannot hide explicit phase headings. A `phased` model must declare every ordered phase heading, entry condition, exit artifact, and scenario binding.                           | Phase scenarios prove ordering and gate behavior.                                 |
| Unambiguous critical language  | `decision_boundaries[]`                                                | Unique scope, authority, side-effect, stop-condition, and evidence-claim statements must occur in executable SKILL.md text, use typed outcomes, and bind to scenarios.                                    | Behavior runs prove the final action obeys the boundary.                          |
| No silent fallback             | `critical_rules` and `blocker_matrix`                                  | `no-silent-fallback` is required. Inputs and evidence always need scenario-bound typed blockers. Tool, credential, and permission exceptions need an in-skill statement, rationale, and scenario binding. | Pressure/negative scenarios prove refusal behavior.                               |
| Outputs are contracts          | `output_contract`                                                      | Required outcome, evidence, validation, residual-risk, artifact-location, and provenance fields must be declared.                                                                                         | Scenario output checks prove the returned artifact shape.                         |
| Test behavior                  | `behavior_proof`                                                       | An exact one-case smoke command template, selected scenario IDs, and observable fields are required.                                                                                                      | Run the declared smoke case; package verification never substitutes for this run. |
| Prune with deletion tests      | `mutation_targets[].removal_test`                                      | Every critical-rule or reference-route target needs its own exact controlled scenario set and a stated removal effect that names the target.                                                              | The mapped scenario is the deletion/regression proof.                             |
| Rerun the smallest proof       | `focused_proof`                                                        | Must equal the exact package-bound scenario-quality preview command.                                                                                                                                      | Run the affected behavioral case before widening.                                 |
| Do not call prose alone ready  | `readiness_evidence`                                                   | Structural, package, behavioral, and runtime lanes must be declared, with the no-ready statement in SKILL.md.                                                                                             | Current lane receipts decide readiness.                                           |

## Failure Boundaries

The validator fails closed if controlled `references/evals.yaml` cannot be
read, decoded as UTF-8, or parsed. It returns ordinary structured authoring
blockers rather than treating missing scenario IDs as evidence. It also rejects
scenario claim IDs, traversal and symlink reference routes, duplicate or nested
heading rationale laundering, and arbitrary proof commands.

## Authoring Order

1. Write the smallest `SKILL.md` entrypoint for the one primary job.
2. Add the authoring contract and bind each critical decision to existing
   controlled cases.
3. Run package verification and the scenario-quality preview.
4. Run the declared one-case behavioral proof after changing behavior.
5. Only make a readiness claim when the selected runtime or external lanes have
   their own current receipts.
