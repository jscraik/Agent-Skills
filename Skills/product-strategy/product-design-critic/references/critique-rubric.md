# Critique Rubric

Use this rubric to structure product critique with clear tradeoffs.

## 1) Job fit
- Question: Does the flow clearly help the user complete the intended job now?
- Strong signal: user intent, risk, and blocking friction are explicit.
- Weak signal: recommendations stay visual and never address the decision moment.

## 2) Surface model
- Question: Is ownership clear between primary, supporting, and ambient surfaces?
- Strong signal: action happens in one place; context supports without interrupting.
- Weak signal: multiple equal-weight containers compete for control.

## 3) Hierarchy and action clarity
- Question: Can a user identify the primary object and primary action in one glance?
- Strong signal: clear visual priority with progressive disclosure.
- Weak signal: everything is visible, everything looks urgent.

## 4) Trust and governance
- Question: Does the interface show who acts, what changes, and what can be reversed?
- Strong signal: permissions, consequences, and undo/review are explicit.
- Weak signal: trust-critical info is hidden in tertiary UI.

## 5) State quality
- Question: Are non-happy-path states robust and legible?
- Strong signal: graceful empty/loading/error/interrupted/revoked behavior.
- Weak signal: only success state is detailed.

## 6) Recommendation quality
- Question: Is the recommendation opinionated with tradeoffs?
- Strong signal: clear choice, clear downside, clear rationale.
- Weak signal: long list of equivalent options without a call.

## Quick scoring (optional)
- Score each category 1-5.
- Any score <= 2 in trust/governance or state quality blocks signoff.
- Prioritize fixes that improve user confidence and decision safety first.
