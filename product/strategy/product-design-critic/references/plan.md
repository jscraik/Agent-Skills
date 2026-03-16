# Plan for Product Design Critic

## Goal
Ship a standalone skill that improves product design judgment with explicit hierarchy, trust, and governance critique rather than visual-only feedback.

## Build steps
1. Scaffold `product/strategy/product-design-critic` with `init_skill.py`.
2. Author a production-ready `SKILL.md` from the approved spec.
3. Add supporting references for design principles, critique rubric, and interface polish.
4. Align `references/contract.yaml` and `references/evals.yaml` with trigger boundaries.
5. Run validators and fix issues until all core gates pass.

## Validation checklist
- `quick_validate.py`
- `skill_gate.py`
- `analyze_skill.py`
- `openclaw_skill_guard.py --mode both`
- `run_skill_evals.py`
