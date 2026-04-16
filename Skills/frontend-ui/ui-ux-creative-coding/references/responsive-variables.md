# Responsive variables (UI Collective distilled)

Use this when creating responsive design systems with modes.

## Core setup
- Create a **Responsive** collection with modes (Desktop / Mobile, Tablet optional).
- Define **device size variables** aligned to product constraints.

## Typography scaling
- Define font size + line height variables by heading/body levels.
- Maintain readable scaling across breakpoints (avoid arbitrary shrink).

## Jumper variables (spacing)
- Use **jumper variables** to map desktop spacing → mobile spacing.
- Keep the set **small and intentional**; add only when needed.

## Component variants
- Most components **do not** need mobile variants.
- Only create mobile‑specific variants when **structure changes** (e.g., nav).

## Checklist
- Are modes defined and enabled for key collections?
- Are spacing mappings based on real audits?
- Do only structural components have mobile variants?
