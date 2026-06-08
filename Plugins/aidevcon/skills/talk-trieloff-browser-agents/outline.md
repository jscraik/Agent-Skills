# Outline -- Building AI agents in the browser, for the browser, of the browser

**Speaker:** Lars Trieloff (Adobe)

## Thesis

Browser-native agents treat the browser as more than a UI: it can become part of the runtime and containment boundary for agent work, provided integration is explicit, permissioned, and reviewable.

## Concept Map

1. Browser-native agents
2. Browser as runtime and containment boundary
3. Local versus cloud execution tradeoffs
4. Harness constraints for agent power
5. Explicit product APIs and documented integration surfaces
6. Visible consent, credential isolation, and auditable actions

## Safe Application

- Design integrations through documented APIs.
- Keep permissions narrow and user-visible.
- Isolate credentials from model-visible context.
- Make actions reviewable and reversible.
- Prefer auditable event boundaries over hidden app control.

## Not Included

Concrete setup commands, app-modification mechanics, runtime endpoint details, credential/token paths, and live-demo control flows are not included in this published bundle.
