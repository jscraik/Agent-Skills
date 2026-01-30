# Motion Guidelines (Emil Kowalski — text extract, Jan 2026)

## Duration guidelines

| Element Type | Duration |
| --- | --- |
| Micro-interactions | 100–150ms |
| Standard UI (tooltips, dropdowns) | 150–250ms |
| Modals, drawers | 200–300ms |

## Rules
- UI animations should stay under **300ms**.
- Larger elements animate **slower** than smaller ones.
- Exit animations can be **~20% faster** than entrance.
- Match duration to distance — longer travel = longer duration.

## Easing decision flowchart
```
Is the element entering or exiting the viewport?
├─ Yes → ease-out
└─ No
   ├─ Is it moving/morphing on screen?
   │  └─ Yes → ease-in-out
   └─ Is it a hover change?
      ├─ Yes → ease
      └─ Is it constant motion?
         ├─ Yes → linear
         └─ Default → ease-out
```
