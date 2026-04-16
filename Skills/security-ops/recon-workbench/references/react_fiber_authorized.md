# React Fiber Inspection (Authorized Use Only)

Purpose: Provide a permissioned, evidence-first workflow to inspect React component trees and map components to rendered output for targets you own or are authorized to analyze.

## Scope and guardrails (non-negotiable)
- Only analyze targets you own or have explicit written authorization to inspect.
- Do not extract or reproduce proprietary source code or assets without permission.
- No circumvention, no DRM bypass, no access to private user data.
- Record evidence paths for every claim; mark gaps as hypotheses.

## Evidence capture (authorized targets only)
- Capture **React component tree** using React Developer Tools.
- Capture **DOM snapshots** and **computed styles** for the same elements.
- Record **props to rendered output** examples for multiple instances of the same component.
- Store artifacts under `data/runs/<target>/<session>/<run>/raw/...` (legacy `runs/...` supported).

## Component grouping (safe version)
- Group component instances by **component identity** as exposed by React DevTools.
- Keep only the minimal props needed to explain visual output.
- Avoid collecting user data or sensitive props; redact before storage.

## Verification loop (allowed)
- Re-render reconstructed components in a local sandbox.
- Compare HTML output to captured DOM snapshots.
- If mismatched, record diffs and iterate; stop after a fixed number of retries.

## Failure cases (document as limits)
- Animations: DOM snapshots may not reflect intended props.
- Internal state: open/closed UI states may not be inferable from props alone.
- When verification fails: snapshot as static HTML and mark as non-functional.

## Reporting
- Explicitly state authorization and scope.
- Cite artifact paths for tree, props, DOM, and diffs.
- Flag any reconstructed component as “approximate” unless verification passes.
