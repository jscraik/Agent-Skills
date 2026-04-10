<!-- GENERATED PROJECTION: source=plugins/arscontexta/references/operational-spec.md; DO NOT EDIT PROJECTION COPY. -->

# arscontexta Operational Spec

## Table of Contents
- [Scope](#scope)
- [Plugin Contract](#plugin-contract)
- [Metadata](#metadata)
- [Plugin Registry](#plugin-registry)
- [Capability Map](#capability-map)
- [Idempotency](#idempotency)
- [Invariants](#invariants)
- [Transition Table](#transition-table)
- [Diagram](#diagram)
- [Dry-Run Simulation](#dry-run-simulation)
- [Transition Tracing](#transition-tracing)
- [Logs](#logs)

## Scope
Operational spec for the packaged `arscontexta` plugin. This package provides Codex-facing skills and prompt surfaces for Ars Contexta setup, routing, and workflow dispatch.

## Plugin Contract
```yaml
plugin_id: arscontexta
capabilities:
  - package_validate
  - route_request
  - skill_dispatch
result_status:
  - SUCCESS
  - FAILURE
  - RETRYABLE
errors:
  - VALIDATION_ERROR
  - BLOCKED_DEPENDENCY
  - POLICY_FAIL
  - SYSTEM_ERROR
  - PLUGIN_TIMEOUT
  - PLUGIN_FAILURE
```

## Metadata
```yaml
metadata:
  owner: agent-skills
  max_duration: "validation <= 30s; routed skill work depends on selected surface"
  escalation: "escalate when package surfaces, routing rules, or validation contract drift"
  plugin_scope:
    - arscontexta_setup
    - arscontexta_routing
    - codex_skill_dispatch
```

## Plugin Registry
```yaml
plugin_registry:
  arscontexta:
    plugin_id: arscontexta
    capabilities:
      - package_validate
      - route_request
      - skill_dispatch
```

## Capability Map
```yaml
capability_map:
  package_validate:
    plugin_id: arscontexta
    description: "Validate required plugin surfaces and package metadata."
  route_request:
    plugin_id: arscontexta
    description: "Resolve incoming requests to the packaged Ars Contexta surfaces."
  skill_dispatch:
    plugin_id: arscontexta
    description: "Dispatch packaged skills or prompts for the selected Ars Contexta task."
```

## Idempotency
- validation is idempotent for unchanged package contents.
- routing is deterministic for the same `(S,E,G)` tuple.
- repeated dispatch requests should preserve the same target surface selection when inputs are unchanged.

## Invariants
- failure states are terminal.
- success state is terminal.
- `.codex-plugin/plugin.json`, `README.md`, `LICENSE`, and `references/operational-spec.md` must remain present.

## Transition Table
| S | E | G | A | P | R | N |
| --- | --- | --- | --- | --- | --- | --- |
| PACKAGE_DEFINED | validate_requested | required package files exist | validate package surfaces | `arscontexta.package_validate` | SUCCESS | PACKAGE_READY |
| PACKAGE_DEFINED | validate_requested | required package files are missing | record package validation failure | `arscontexta.package_validate` | FAILURE:VALIDATION_ERROR | FAIL_VALIDATION |
| PACKAGE_READY | request_received | request resolves to a packaged Ars Contexta surface | dispatch packaged skill or prompt | `arscontexta.route_request` | SUCCESS | WORK_ACTIVE |
| PACKAGE_READY | request_received | request does not resolve to a packaged Ars Contexta surface | record routing failure | `arscontexta.route_request` | FAILURE:VALIDATION_ERROR | FAIL_VALIDATION |
| WORK_ACTIVE | work_completed | selected packaged surface completes without plugin error | finalize result | `arscontexta.skill_dispatch` | SUCCESS | SUCCESS |
| WORK_ACTIVE | work_failed | selected packaged surface fails or times out | record runtime failure | `arscontexta.skill_dispatch` | FAILURE:PLUGIN_FAILURE | FAIL_PLUGIN |

## Diagram
```mermaid
stateDiagram-v2
    PACKAGE_DEFINED --> PACKAGE_READY: validate_requested
    PACKAGE_DEFINED --> FAIL_VALIDATION: validate_requested
    PACKAGE_READY --> WORK_ACTIVE: request_received
    PACKAGE_READY --> FAIL_VALIDATION: request_received
    WORK_ACTIVE --> SUCCESS: work_completed
    WORK_ACTIVE --> FAIL_PLUGIN: work_failed
```

## Dry-Run Simulation
```text
1. Match S and E against the transition table.
2. Evaluate guards in row order.
3. Emit A, P, R, and N for the first true guard.
4. If no guard resolves true, return FAILURE:VALIDATION_ERROR to FAIL_VALIDATION.
```

## Transition Tracing
Transition code format:
- `TC::<from_state>::<event>::<to_state>`

## Logs
```yaml
logs:
  workflow_id: "<uuid>"
  plugin_id: "arscontexta"
  capability: "<capability name>"
  transition_code: "TC::<from_state>::<event>::<to_state>"
  from_state: "<state>"
  to_state: "<state>"
  correlation_id: "<trace or request id>"
  result: "SUCCESS | FAILURE:<error> | RETRYABLE:<error>"
```
