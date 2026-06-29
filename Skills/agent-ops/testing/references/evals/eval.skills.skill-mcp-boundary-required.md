# eval.skills.skill-mcp-boundary-required: Skill MCP Boundary Required

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.skill-mcp-boundary-required.md

Knowledge claim: Skills prepare the agent while MCP and tools provide connectivity, so the SDK must keep procedure, tool access, and permission evidence separate.
Behavior under test: The Skills SDK gate refuses to hide MCP/tool dependencies inside skill prose.
Failure mode: A skill package is accepted even though its runtime dependencies and permissions are not declared.
Expected agent move: Require explicit MCP/tool dependency declaration, permission manifest, and a later observed-behavior check.
Skill lift before failure: The Skills SDK accepts prose-hidden MCP dependencies.
Skill lift after behavior: The Skills SDK requires explicit dependency and permission evidence.
Observable delta: The answer names skill procedure, MCP connectivity, declared permissions, and observed behavior as separate checks.

Given: A proposed skill teaches a workflow that depends on a database MCP server and shell scripts, but the package records those dependencies only in prose and has no explicit tool, MCP, or permission boundary.
Should: The agent blocks SDK readiness until the skill separates procedural guidance from MCP/tool connectivity and records declared capabilities that can be compared with observed behavior.
Expected failure: The agent treats the workflow prose as enough to authorize runtime tool and MCP access.

Bad answer patterns:
- The agent accepts workflow prose as permission evidence.
- The agent merges skill readiness with MCP server availability.

Good answer patterns:
- The agent requires explicit dependency and permission boundaries.
- The agent keeps skill guidance proof separate from runtime connectivity proof.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
