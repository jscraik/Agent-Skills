---
name: threejs-builder
description: Build and validate simple, performant Three.js web apps using modern ES module patterns. Use this when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.
metadata:
  skill-type: scaffolding_templates

---

# Three.js Builder

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Start with the smallest runnable scene and prove it works before adding visual complexity.
- Favor performance, cleanup, and integration safety over flashy but brittle demos.
- Treat resize behavior, lifecycle cleanup, and asset loading discipline as part of the definition of done.

## When to use
- Build a minimal Three.js scene, animation, or interaction for a web UI or technical demo.
- Add lightweight 3D or motion accents inside an existing web app.
- Review a small Three.js implementation for correctness, integration fit, or performance basics.

## When not to use
- Full game-engine or complex 3D application design.
- Pure visual concepting with no implementation target.
- Heavy scene pipelines better served by a specialized graphics or game workflow.

## Required inputs
- What the scene should show.
- Required interactions, if any.
- Target environment: standalone HTML, Vite, React, or an existing codebase.
- Performance and device constraints.
- Whether external assets or models are allowed.

## Deliverables
- A minimal working scene or integration plan.
- Notes on where the code belongs and how it should be wired into the project.
- Verification guidance covering runtime behavior, cleanup, and performance basics.

## Philosophy
- Build the scene graph deliberately.
- Earn complexity in stages: render first, interact second, polish last.
- A small scene that loads fast and cleans up correctly beats a more ambitious but unstable prototype.

## Workflow
1. Lock the rendering target and the smallest useful scene.
2. Build a working scene with camera, renderer, and one core object.
3. Add interaction or animation only after the base render loop is stable.
4. Reuse geometry, materials, and loaders where possible.
5. Confirm resize handling, disposal, and lifecycle cleanup before adding polish.
6. Add visual refinement only if it survives the project’s performance budget.

## Verification
- Confirm the scene renders without missing imports or runtime errors.
- Confirm resize handling keeps camera and renderer in sync.
- Confirm animation loops and event listeners clean up properly in framework integrations.
- Confirm asset loading failures have a sane fallback or visible failure mode.

## Validation
- Verify the guidance reaches a working first frame before layering on polish.
- Verify cleanup and resize behavior are covered in the implementation notes.
- Reference skill `references/` material or `assets/` templates when they provide integration patterns worth reusing.

## Constraints
- Do not introduce secrets, tokens, or private endpoints into demos or examples.
- Prefer pinned or repo-managed dependencies over floating CDN versions when the host project already has a package workflow.
- Keep examples minimal and portable unless the user explicitly asks for a stylized showcase.

## Anti-patterns
- Starting with a giant scene graph before the first frame renders.
- Ignoring cleanup in React or other component lifecycles.
- Treating performance problems as acceptable because the scene is "just a demo."
- Pulling in heavy helper stacks when core Three.js solves the problem cleanly.

## Examples
- "Build a rotating product cube with proper cleanup in React."
- "Add a lightweight Three.js accent scene to an existing landing page."

## See Also

| Skill | When to use together |
|---|---|
| [[ui-ux-creative-coding]] | Orchestrate Three.js alongside React motion for rich UI |
| [[frontend-ui-design]] | Provide the design context Three.js scene should match |
| [[visual-explainer]] | Embed Three.js scenes in HTML explainer pages |
| [[agentation]] | Automate Three.js scene interactions for testing |

**Topic map:** [[frontend-ui]]

## Remember
- The first milestone is a correct frame on screen.
- The second milestone is a stable, cleanly integrated scene.
- Everything after that is polish.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## Failure mode
- If the scene goal, asset inputs, or runtime constraints are unclear, stop, report the blocker, and fall back to a minimal scene plan before writing Three.js code.
