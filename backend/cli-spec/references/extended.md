# Extended guidance

### TypeScript/Node (tsx + yargs)
```bash
npm i yargs
npm i -D tsx typescript
```

```ts
import yargs from \"yargs\";
import { hideBin } from \"yargs/helpers\";

yargs(hideBin(process.argv))
  .command(
    \"run\",
    \"Plan only; no side effects\",
    (y) => y.option(\"json\", { type: \"boolean\", default: false }),
    (args) => {
      if (args.json) {
        process.stdout.write(JSON.stringify({ schema: \"mycmd.run.v1\" }));
      } else {
        process.stdout.write(\"Plan preview\\n\");
      }
    }
  )
  .strict()
  .help()
  .parse();
```

## Notes

- Prefer recommending a parsing library (language-specific) only when asked; otherwise keep this skill language-agnostic.
- If the request is "design parameters", do not drift into implementation.

## Scope and triggers
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Required inputs
- User request details and any relevant files/links.


## Deliverables
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

- Redact secrets/sensitive data by default.

## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.

- Fail fast on first failed gate.

## Philosophy
- Favor clarity, explicit tradeoffs, and verifiable outputs.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.

- Redact secrets/sensitive data by default.

---

## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.

