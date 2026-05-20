# Harness Assurance Testing

Read when: the target repo has harness-style validation, workflow contracts,
agent-facing gates, .harness, harness.contract.json, or artifact closeout
claims.

## Core Rule

Broad gates are necessary, but exact behavior still needs direct proof. Run the
smallest production path that exercises the changed code before claiming the
change is verified.

## Assurance Layers

| Layer | Use When | Required Proof |
|---|---|---|
| Unit | Pure helpers, command logic, registry metadata, validators. | Targeted unit test for the changed file or function. |
| Boundary | Input limits, invalid states, refusal paths, policy gates. | Assert the named blocker or policy class, not only that an error happened. |
| Mock integration | GitHub, Linear, CircleCI, CodeRabbit, Snyk, filesystem, automation, or outbound boundaries. | Fixture-backed adapter or command test with machine-readable output assertions. |
| End-to-end | Full scenario crosses command, artifact, and external-system boundaries. | Repo e2e command or a blocked reason when credentials/services are unavailable. |
| Security | Unsafe commands, path traversal, secret exposure, branch protection, or policy refusal. | Targeted security proof that the unsafe sample is refused with a named reason. |
| Load/stress | High-volume discovery, artifact writes, overload, throughput, or degradation behavior. | Bounded-duration or numeric-threshold proof; use deep gates when runtime behavior changes. |
| Lifecycle closeout | PR/body/Linear/artifact/handoff claims or route-driving artifacts. | File-backed artifact proof and explicit pass/fail/blocked classification. |

## Exact Behavior Checks

- Prefer invoking the production function, class, CLI command, shell script,
  validator, or route directly.
- If no existing test covers the path, create a temporary local reproduction
  harness only when repo policy allows it; keep it gitignored and invoke
  production code rather than copying implementation.
- If exact proof cannot run, name the missing credential, service, unsafe side
  effect, sandbox permission, or generated state; then run the nearest
  meaningful validation.

## Changed-Code Ratchets

For harness TypeScript repos, look for changed-source ratchets such as:

- related tests for changed production src files;
- public API docstring checks;
- file size or complexity checks;
- codestyle wrappers that include the ratchets.

Missing related tests are a blocker when the repo declares that contract.

## Reporting

Use exact command evidence:

- Command: pnpm run test:related -> pass (covered changed src files)
- Command: pnpm audit -> blocked (network ENOTFOUND in sandbox)

Do not flatten blocked, partial, and not-applicable states into success.
