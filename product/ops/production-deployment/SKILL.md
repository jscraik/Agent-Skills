---
name: production-deployment
description: Deploy and manage production services across various platforms with automated verification and rollback safety.
metadata:
  skill-type: team_automation
---

# Production Deployment

Automate the deployment of software services to production environments with a focus on safety, observability, and reproducible infrastructure.

## Standards snapshot (March 2026)
- Always verify deployment status through health checks or automated probes before completing a rollout.
- Infrastructure should be defined as code wherever possible.
- Rollback criteria must be established before the deployment begins.
- Use incremental rollout strategies (e.g., rolling updates or blue/green) to minimize downtime.

## Philosophy
- Production safety is paramount; speed comes second.
- Deployments should be repeatable, predictable, and fully automated.
- Observability and alerting are core components of any deployment process.

## When to use
- Deploying a new service to production.
- Updating an existing production service.
- Scaling production resources or migrating to new environments.

## When not to use
- Deploying to development or sandbox environments with no production parity.
- Manual infrastructure adjustments or "hotfixes" without corresponding code changes.
- High-level architectural discussions without a deployment-ready artifact.

## Required inputs

### Platform
- [ ] Target cloud provider or platform (e.g., AWS, Azure, Google Cloud, Vercel, Fly.io, etc.).

### Environment & Target
- [ ] Target environment(s) (e.g., Production, Staging, Preview).
- [ ] Region(s) or cluster names.

### Infrastructure & Resources
- [ ] Resource definitions (e.g., instance types, memory/CPU allocations).
- [ ] Networking requirements (e.g., VPC, Subnets, Load Balancer settings).

### Secrets & Credentials
- [ ] Service account or IAM role requirements.
- [ ] API keys or deployment tokens.

### Deployment Strategy
- [ ] Strategy choice (e.g., Blue/Green, Rolling, Canary).
- [ ] Rollback criteria and health check definitions.

## Deliverables
- Automated deployment scripts or configuration files.
- Verified deployment status report.
- Infrastructure as Code (IaC) updates (if applicable).
- Rollback plan or automated rollback triggers.

## Constraints
- Never commit secrets or sensitive credentials to source control.
- Do not skip health checks or automated verification steps.
- Do not deploy if the rollback mechanism is not functional or defined.

## Failure mode
- If the deployment platform is not specified, the skill cannot proceed with implementation-grade work.
- If required secrets are unavailable, the skill must fail safely rather than attempting a partial deployment.

## Workflow
1. Identify the target platform, environment, and deployment artifacts.
2. Validate the infrastructure configuration and deployment strategy.
3. Prepare the deployment environment and verify prerequisites.
4. Execute the deployment using the chosen strategy.
5. Perform automated health checks and verification probes.
6. Confirm successful rollout or trigger an automated rollback if health checks fail.

## Implementation lanes
- Standard CI/CD Rollout:
  - Trigger deployment from CI pipeline.
  - Apply configuration and update resources.
  - Monitor health and verify status.
- Zero-Downtime Migration:
  - Provision parallel infrastructure.
  - Gradually shift traffic to new environment.
  - Decommission old infrastructure after successful verification.

## Tooling and references
- Use platform-specific documentation (e.g., AWS CLI, Terraform, kubectl).
- Use local references for deployment contracts and verification probes.

## Validation
- Confirm all target resources are healthy and responding as expected.
- Verify that observability and alerting are active for the new deployment.
- Confirm the deployment history is updated and traceable.

## Anti-patterns
- Deploying without a rollback plan.
- Manually editing production resources outside of the automated workflow.
- Skipping health checks to "speed up" the rollout.

## Examples
- Deploy this Next.js app to Vercel production.
- Update the ECS service with the latest Docker image using a rolling update strategy.

## See Also

| Skill | When to use together |
|---|---|
| [[release]] | Orchestrate the release flow before deployment |
| [[1password]] | Inject deployment secrets via 1Password CLI |
| [[cloudflare-deploy]] | Deploy specifically to the Cloudflare platform |
| [[workers-mcp]] | Deploy MCP servers as production-ready workers |

**Topic map:** [[ops-engineering]]

## Remember
A successful deployment is one that is verified to be working correctly, not just one that finished running its scripts.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
