# PRD Compiler Contract (Stable)

This contract is canonical and compiler-safe. Do not deviate.

## 1) Story ID format (canonical)

Use this format everywhere:

```
STORY-001
STORY-002
STORY-003
```

Rules:

- Zero-padded, monotonically increasing
- Never reused
- Never renumbered
- Order in the document does not matter once assigned

This guarantees:

- Safe reordering in the spec
- Safe splitting/merging later
- Stable joins between `.spec/*.md` and `prd.json` and git history

## 2) Exact authoring rule in `.spec/spec-*.md`

### Required story header format

The PRD must use one of these (pick one and standardize):

```md
1) **Story [STORY-001]:** As a <persona>, I want <action> so that <benefit>.
```

or

```md
### STORY-001 — As a <persona>, I want <action> so that <benefit>.
```

Everything downstream keys off `STORY-###`.

## 3) Acceptance criteria contract (machine-readable)

Under each story, only these lines are compiled:

```md
**Acceptance criteria:**
- [ ] <observable behavior>
- [ ] <observable behavior>
```

Rules:

- Must be checkboxes
- Must be observable and testable
- No prose paragraphs mixed in

These become:

```json
"acceptanceCriteria": [
  "<observable behavior>",
  "<observable behavior>"
]
```

## 4) Priority mapping (deterministic)

From the PRD:

```md
**Priority:** Must | Should | Could
```

Compiler mapping (fixed):

| PRD value | JSON value |
| --------- | ---------- |
| Must      | 0          |
| Should    | 1          |
| Could     | 2          |

Lower number = higher priority.

## 5) Canonical `prd.json` schema (execution state)

This is the minimum stable shape the loops rely on:

```json
{
  "projectName": "Feature Name",
  "branchName": "ralph/feature-x",
  "specRef": ".spec/spec-2026-01-13-feature-x.md",
  "finalTests": [],
  "userStories": [
    {
      "id": "STORY-001",
      "title": "As a user, I want … so that …",
      "priority": 0,
      "acceptanceCriteria": [
        "..."
      ],
      "tests": [],
      "status": "open",
      "passes": false,
      "startedAt": null,
      "completedAt": null,
      "attempts": 0,
      "lastError": null
    }
  ]
}
```

## 6) State preservation rule (critical)

When `spec -> prd` recompiles:

Fields that must be preserved by `id`:

- `status`
- `passes`
- `startedAt`
- `completedAt`
- `attempts`
- `lastError`

Fields that are always regenerated from spec:

- `title`
- `priority`
- `acceptanceCriteria`
- `tests`

If a `STORY-###` disappears from the spec:

- Mark it as `"status": "removed"` (do not delete)

## 7) Ralph loop selection logic (deterministic)

Each iteration:

1. Load `prd.json`
2. If any story:

   - `status = in_progress`
   - and `now - startedAt > STALE_SECONDS`
     - reset to `open`
3. Pick next story:

   - `status = open`
   - lowest `priority`
   - lowest numeric story ID as tie-breaker
4. Mark:

```json
status = "in_progress"
startedAt = now
attempts += 1
```

5. Run exactly one story
6. If checks pass:

```json
status = "done"
passes = true
completedAt = now
```

7. If attempts exceed limit:

```json
status = "blocked"
lastError = "<summary>"
```

Loop stops.

## 8) Separation of concerns (clean boundaries)

- Product-manager skill: owns `.spec/spec-*.md`, produces stable `STORY-###`, never touches `prd.json`.
- Compiler (`spec_to_prd`): pure function + state merge, deterministic, testable.
- Ralph loops (Codex / Claude / Copilot): consume only `prd.json`, never interpret prose, never invent scope, only update execution state.
