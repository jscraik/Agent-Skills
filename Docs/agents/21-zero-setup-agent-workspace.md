# Zero-Setup Agent Workspace

The product contract is that customers should be able to drop agents into a
workspace and have those agents set themselves up. The customer should not
need to integrate with the product before the product can become useful.

Agent Skills Kit must therefore optimize for agent self-setup, not customer
assembly. A professional SDK should expose enough typed workspace contract for
agents to discover, bootstrap, validate, and report readiness without bespoke
human glue.

This is a systems-thinking requirement: identify setup blockers, encode the
repeatable unblocking path in code or contract, and explain readiness in terms
of what the agent can prove from inside the workspace.

## Product Rule

Do not design agent-facing capabilities that require Jamie, or any customer,
to manually connect scattered docs, scripts, projections, credentials, and
validation steps before an agent can operate.

The preferred flow is:

1. Agent lands in a workspace.
2. Agent discovers the local contract.
3. Agent bootstraps the minimum required runtime.
4. Agent classifies unavailable capabilities as explicit blockers.
5. Agent validates readiness through repo-owned commands.
6. Agent reports what it can do, what it cannot do, and why.

## Interface Requirements

- Discovery must be machine-readable enough for an agent to select the next
  command without searching prose indefinitely.
- Bootstrap commands must be idempotent and safe to rerun.
- Missing credentials, network access, external tools, and sandbox roots must
  be reported as blockers with exact remediation, not collapsed into generic
  setup failure.
- Generated projections and runtime links must be validated by repo-owned
  commands, not by manual inspection alone.
- Skills should declare their setup and capability requirements in typed
  metadata wherever the repo owns the surface.
- Human-facing docs can explain the system, but agent-facing setup must be
  executable or directly checkable.

## Design Implications

- Prefer one workspace contract command over a list of manual setup steps.
- Prefer stable capability IDs over internal implementation structs.
- Prefer readiness reports that separate ready, degraded, blocked, and not
  applicable capabilities.
- Prefer local self-tests and doctor checks that produce structured output.
- Prefer installation and projection flows that can be resumed after partial
  failure.
- Prefer narrow permission requests tied to a discovered capability instead of
  broad setup instructions.

## Anti-Patterns

- A skill that only works after the customer manually edits several unrelated
  files.
- A setup doc that cannot be checked by a command.
- A runtime projection that can drift without a validator reporting it.
- A workflow that says "configure your environment" without naming the missing
  capability, owner, or exact next action.
- A product surface that assumes the customer is the integrator of last resort.

## Review Rule

When reviewing agent-facing SDK, harness, or skill work, ask whether an agent
dropped into the workspace could discover and perform the setup without the
customer stitching the product together. If not, classify the gap as a product
contract failure, not merely documentation debt.
