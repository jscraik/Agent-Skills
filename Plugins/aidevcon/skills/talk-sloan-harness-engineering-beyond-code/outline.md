# Outline - Harness Engineering Beyond Code

## Speaker

Rob Sloan

## Redaction Note

This outline preserves the talk's useful concepts while omitting runtime mechanics, mutable online dependencies, sensitive-data flows, and operational instructions that could create security-review findings.

## Thesis

The talk argues that successful agent work depends on harnessing the context around the code: product goals, design intent, constraints, and acceptance criteria. Live connections to product tools are safety-redacted.

## Concept Map

1. Harness engineering beyond source code
2. Context packets for agents
3. Product and design intent
4. Reviewable acceptance criteria
5. Clear ownership of context

## Safe Application

1. Draft static context packets and acceptance criteria.
2. Recommend sanitized exports and human review before agent use.
3. Do not connect to or read live product tools from this skill.

## Not Covered

- Executable commands, scripts, manifests, workflow files, or setup steps.
- Live-system access patterns or mutable online dependency details.
- Sensitive values, credentials, private data, or operational abuse examples.
