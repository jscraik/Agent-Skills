---
name: test-xcode
description: Run or plan simulator-based verification for iOS and macOS apps using existing CLI-first Xcode workflows. Use when a user needs build, test, launch, or screenshot evidence for Apple app changes rather than initial scaffolding.
metadata:
  skill-type: product_verification
---

# Test Xcode

## Table of Contents
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [See also](#see-also)

## When to use

Use this skill when:
- Apple-platform changes need simulator or CLI verification;
- the user wants build, test, launch, or screenshot evidence for an iOS or macOS app;
- an existing Xcode project should be exercised through repeatable command-line workflows.

Do not use this skill when:
- the project still needs initial scaffolding or toolkit installation;
- the task is about generic Swift or UI code review without runtime verification;
- no simulator or project context is available and the user only wants planning guidance.

## Required inputs

- project path;
- scheme or target context;
- platform:
  - iOS,
  - macOS,
  - or both;
- desired verification depth:
  - build,
  - test,
  - launch,
  - screenshots,
  - or a combination.

## Deliverables

- an executed or planned Xcode verification flow;
- key commands used for diagnose, build, test, or run;
- failure evidence with the first broken gate;
- screenshots or logs when requested and available.

## Failure mode

- If the repo lacks repeatable CLI build surfaces, stop and route to `xcode-makefiles` or `apple-app-builder` first.
- If the scheme, simulator, or platform is ambiguous, resolve that before launching builds.
- If simulator or signing constraints block execution, return the smallest unblock path instead of broad troubleshooting.

## Philosophy

- Verification should stay CLI-first and reproducible.
- Diagnose before optimism: toolchain and simulator checks come before long test runs.
- Apple app QA is only useful if the build/run surface can be repeated by another agent.

## Workflow

1. Confirm project path, scheme, and platform.
2. Identify the existing verification surface:
   - repo-native `make` targets,
   - Xcode scripts,
   - or direct `xcodebuild` flow.
3. Run the smallest reliable gate first:
   - diagnose,
   - build,
   - then test or run.
4. If runtime verification matters, boot the intended simulator and capture the evidence needed.
5. Summarize the first failing step or the completed verification bundle.

## Validation

- Verify the project path and scheme before execution.
- Verify each completed gate with command output or captured artifacts.
- Verify screenshots and logs exist when requested.

## Gotchas

- Apple-platform verification often fails at the simulator or signing layer before it fails at the app layer, so diagnose output matters more than intuition.
- Repos with custom wrappers may hide the real verification entrypoint behind `make`, `just`, or helper scripts; prefer the repo-native path once found.

## Anti-patterns

- Jumping straight to a full test run before diagnosing the toolchain.
- Treating a one-off GUI success as equivalent to repeatable CLI verification.
- Mixing setup/install work into a verification-only task without calling that out.

## See Also

| Skill | When to use together |
|---|---|
| [[xcode-makefiles]] | Install or upgrade the CLI-first Xcode build toolkit |
| [[apple-app-creator]] | Scaffold a new Apple app project before runtime verification |

**Topic map:** [[mobile-native]]
