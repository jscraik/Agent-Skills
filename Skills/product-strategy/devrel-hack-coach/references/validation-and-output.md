# Validation And Output

## Coaching Output Fields

Every coaching response must expose these fields in plain language:

- `schema_version`: use `devrel-hack-coach-output/v1`.
- `phase`: current workflow phase.
- `gate_state`: what is complete and what is still missing.
- `next_prompt_or_artifact`: one next question or the next artifact.
- `grounded_state`: decisions already supplied by the user.
- `boundary_status`: whether the request stayed inside hackathon coaching.

## Package Validation Lane

Use repository wrappers for package checks:

```sh
./bin/ask skills package verify Skills/product-strategy/devrel-hack-coach --json --robot
./bin/ask sdk eval scenario-quality Skills/product-strategy/devrel-hack-coach --preview --json --robot
```

These commands prove package and scenario gates only. They do not prove OSS,
Tessl, registry, PR, or runtime readiness.
