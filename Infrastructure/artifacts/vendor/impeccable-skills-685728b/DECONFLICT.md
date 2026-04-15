# Deconflict Report

## Summary
- Upstream skills scanned: `21`
- Exact local name collisions: `1`
- High-overlap capability clusters: `frontend design`, `design audit`, `design critique`, `layout/polish`, `design-system extraction`, `performance hardening`
- Recommendation: keep this tree quarantined; promote only through selective wrapper or uplift work

## Exact collision
| Upstream skill | Local surface | Decision | Notes |
|---|---|---|---|
| `frontend-design` | `frontend/ui/frontend-design` | keep quarantined | Same top-level name, but the local skill is already a repo-adapted compatibility wrapper with richer graph wiring and references. |

## High-overlap skills
| Upstream skill | Closest local skill(s) | Risk | Suggested action |
|---|---|---|---|
| `audit` | `frontend/ui/baseline-ui`, `product/strategy/product-design-critic` | high | Uplift scoring/report structure selectively; do not import raw. |
| `critique` | `product/strategy/product-design-critic` | high | Compare rubric/reference material only. |
| `arrange` | `frontend/ui/frontend-ui-design`, `frontend/ui/ui-ux-creative-coding` | high | Treat as layout-focused doctrine, not a standalone canonical skill. |
| `polish` | `frontend/ui/frontend-ui-design`, `frontend/ui/ui-ux-creative-coding` | high | Preserve as upstream reference if needed; avoid generic routing duplication. |
| `typeset` | `frontend/ui/frontend-ui-design` | medium | Consider typography guidance uplift into local UI skills. |
| `extract` | `frontend/ui/design-system`, `frontend/stitch-react-components` | high | Reuse design-system extraction heuristics selectively. |
| `optimize` | `frontend/ui/baseline-ui` | high | Fold any missing performance checklist items into the existing audit skill. |
| `harden` | `product/Infrastructure/ops/ce-deepen-spec`, `product/Infrastructure/ops/ce-deepen-plan`, `frontend/ui/baseline-ui` | medium | Keep as doctrine only unless a frontend-hardening wrapper is intentionally created. |
| `normalize` | `frontend/ui/design-system`, `frontend/ui/frontend-ui-design` | high | Compare for design-system drift checks; do not import raw. |
| `onboard` | `product/strategy/brainstorming`, `product/strategy/project-improver` | medium | Possible future wrapper if onboarding becomes a recurring standalone lane. |

## Likely net-new but broad
| Upstream skill | Assessment | Notes |
|---|---|---|
| `adapt` | interesting but broad | Responsive/cross-context adaptation is useful, but current naming is too generic for direct canonical import. |
| `animate` | useful doctrine | Could feed motion guidance for local UI skills without becoming a separate router surface immediately. |
| `bolder` | novel but style-specific | Candidate for optional aesthetic-mode wrapper, not a default canonical skill. |
| `clarify` | useful but overlaps with broader product/docs skills | Better as UX-writing uplift unless a strong frontend-copy workflow emerges. |
| `colorize` | novel but style-specific | Keep quarantined until there is repeated demand for color-direction work. |
| `delight` | useful but overlapping with motion/polish | Likely reference material, not first-pass canonical surface. |
| `distill` | useful but overlapping with design simplification work | Potential future wrapper if simplification requests recur often enough. |
| `overdrive` | distinctive and high-risk | Strong candidate for a future experimental wrapper because it already includes a mandatory approval step. |
| `quieter` | novel aesthetic modifier | Could become a paired mode with `bolder`, but not yet justified as canonical. |
| `teach-impeccable` | setup-oriented and potentially reusable | Most likely standalone promotion candidate if you want a project design-context bootstrapper. |

## Artifact-uplift scan targets
1. Compare `critique/reference/*` to local critique rubric/reference surfaces.
2. Compare `frontend-design/reference/*` to the local `frontend-design` wrapper references.
3. Review `teach-impeccable` as a possible design-context bootstrap pattern for local frontend workflows.
4. Review `overdrive` for its explicit pre-build proposal gate and browser-iteration discipline.

## Recommendation
- Do not sync or surface these skills directly.
- Use the quarantine as an upstream review pack.
- Promote only selected capabilities through explicit local wrapper work with repo taxonomy, evals, and graph wiring.
