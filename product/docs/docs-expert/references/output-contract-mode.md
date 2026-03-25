# Output contract mode

## Table of Contents
- [When to use](#when-to-use)
- [Canonical modes](#canonical-modes)
- [Agent-operator interface](#agent-operator-interface)
- [Schema versioning policy](#schema-versioning-policy)
- [Deterministic error envelope](#deterministic-error-envelope)
- [Compatibility policy](#compatibility-policy)

## When to use

Use this mode when the user wants canonical output contracts for agent-facing commands, validators, reporters, or automation entry points.

Typical triggers:
- define a stable `--json` surface;
- separate machine-readable output from human-readable output;
- normalize success and error envelopes across commands;
- document compatibility expectations for future fields.

## Canonical modes

Default policy:
- machine-readable mode is the default for agent-facing commands unless the user explicitly requests otherwise;
- human-readable mode is explicit and optimized for operators, not parsers;
- human-readable output is not the compatibility surface unless the user explicitly makes it one.

Recommended machine-readable top-level fields:
- `schema_version`
- `tool`
- `generated_at`
- `status` or `decision`
- `exit_code`
- payload-specific fields

## Agent-operator interface

When the command is designed for agent operators:
- make machine-readable output the default;
- support an explicit human-readable mode for operators;
- provide a token-dense quick-start mode with no args when that helps agents discover the surface quickly;
- map command taxonomy to user intent rather than internal subsystems;
- make errors teach the next correct usage.

Recommended robot-mode quick-start fields:
- command groups by intent
- the default machine-readable mode
- the explicit human-readable mode
- the shortest valid next command for each common intent

Recommended error behavior:
- explain why the command failed;
- show the next correct invocation shape;
- keep the envelope deterministic even when the message is instructional.

## Schema versioning policy

Recommended policy:
- require `schema_version` in every machine-readable response;
- additive fields are allowed in minor revisions;
- removing required fields or changing field meaning requires a major schema bump;
- human-readable wording changes do not require a schema bump unless human mode is contract-bound.

## Deterministic error envelope

Error envelopes should be deterministic and stable.

Recommended fields:
- `schema_version`
- `tool`
- `generated_at`
- `status`
- `exit_code`
- `errors`

Recommended `errors[]` item shape:
- `code`
- `message`
- `severity`
- optional `evidence`
- optional `remediation`

## Compatibility policy

Compatibility defaults:
- future fields may be added without breaking existing consumers;
- existing field names and meanings must not drift silently;
- required fields must remain present within the same major schema line;
- parsers should ignore unknown fields;
- docs should call out any field with unstable or best-effort semantics.
