---
description: Select the authorised skill installation or transitional recovery route
---

# /sync-skills

Resolve the intended package, consumer and authority before changing projections
or runtime links. Missing discovery does not authorise relinking to this checkout.

## When to use

- Classify a request to sync skills or make a skill available.
- Diagnose missing discovery or a possibly stale runtime link.
- Recover an existing transitional consumer within explicit mutation scope.

---

## Steps

1. Read the [approved lifecycle](/Docs/agents/14-path-ownership-boundaries.md#approved-lifecycle).
   New managed installations require SDK checks and a checked private Tessl
   version. Verified OpenAI plugins and system skills use their provider-managed
   routes. If the required route is unavailable, report the gap; do not use
   direct-source installation or checkout relinking as a substitute.
2. For transitional recovery, name the existing consumer, approved source,
   exact workspace/home targets and recovery authority. Preserve its working
   state. A link into another checkout is not inherently a failure.
3. Only when workspace projection refresh is explicitly authorised, run:

```bash
./bin/ask skills sync --scope workspace --json --robot
```

4. User sync is a separate mutation, not the next automatic step. Run it only
   when the authorised recovery explicitly selects the home targets and this
   checkout as their replacement source; otherwise skip it:

```bash
./bin/ask skills sync --scope user --json --robot
```

5. Inspect discovery for the selected consumer:

```bash
./bin/ask skills list --json --robot
./bin/ask skills load-preview --json --robot
```

6. For affected home links, inspect their actual destinations:

```bash
ls -la ~/.agents/skills ~/.codex/skills
```

## Checks

1. Confirm expected results:
   - Only authorised, selected mutations ran; skipped mutations are not failures.
   - Any recovery link matches its approved target, not necessarily this checkout.
   - Managed installation proves the selected checked registry identity,
     discovery and required behaviour; listing files alone is not readiness.
   - Preserve and report any `WARN` or `REFUSED` result; do not bypass its gate.

2. If skill count is 0 or a link is missing, run diagnostics:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo closeout --changed --json --robot
```

3. Follow [consumer-specific recovery proof](/Docs/agents/17-skill-management.md#user-runtime-links).
   Report any discovery or behaviour gap without widening mutation authority.

---

## Invariants (do not break)

- Edit the recorded canonical source, not generated runtime projections.
- `.agents/skills/**` is a generated runtime projection in this repo.
- Home runtime targets follow the approved installed-version or provider route.
  Do not force them to resolve into the active checkout.

## Error codes

| Symptom | Error | Fix |
|---------|-------|-----|
| Runtime link points at another checkout | Diagnose ownership first | Compare with the approved target; do not relink automatically |
| Managed install route unavailable | Capability gap | Preserve runtime state and report the missing SDK/Tessl capability |
| Skill list is stale after sync | `VALIDATION_ERROR` | Run repo doctor and inspect runtime link output |
| `./bin/ask` is unavailable | `SYSTEM_ERROR` | Run `bash scripts/bootstrap-ask.sh --json`, then `python3 bin/ask repo status --json` |
| Sync output includes `REFUSED` | `POLICY_FAIL` | Stop and fix the named ownership or projection blocker |
