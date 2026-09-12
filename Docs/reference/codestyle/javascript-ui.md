# JavaScript And UI Standards

Applies to the matching changed surface. Use repository commands and lockfiles
for the actual toolchain; unrelated technology sections do not add checks.

## 3. Node.js Standards

- Packages MUST target the repo baseline Node version (pinned).
- JS/TS packages MUST use ESM (`"type": "module"`); avoid CJS unless a pack explicitly permits it.
- Prefer Node standard capabilities where appropriate (test runner for small libs is allowed).
- JSON imports MUST use import attributes where runtime requires it:

  ```ts
  import data from "./foo.json" with { type: "json" };
  ```

---

## 4. JavaScript / TypeScript

### Type discipline

* Explicit types at all public API boundaries (functions, modules, React props).
* `strict: true` with:

  * `noUncheckedIndexedAccess`
  * `exactOptionalPropertyTypes`
  * `useUnknownInCatchVariables`
* `any` is forbidden everywhere. Use concrete types or `unknown` + narrowing.

### Banned patterns (CI errors)

| ❌ DON'T                                                  | ✅ DO                                     |
| -------------------------------------------------------- | ---------------------------------------- |
| `: any`, `as any`, `Promise<any>`, `Record<string, any>` | concrete types or `unknown` + validation |
| `value as unknown as T`                                  | type guards or schema validation         |
| `// @ts-ignore`, `// @ts-nocheck`                        | `// @ts-expect-error -- reason + ticket` |
| unsafe `as SomeType` without runtime guard               | guard function or schema validator       |
| eslint-disable                                            | fix the owning source                    |

### Type-checked linting (mandatory)

* ESLint MUST be type-aware for TS code.
* The following MUST be errors:

  * `@typescript-eslint/no-explicit-any`
  * `@typescript-eslint/no-unsafe-assignment`
  * `@typescript-eslint/no-unsafe-member-access`
  * `@typescript-eslint/no-unsafe-argument`
  * `@typescript-eslint/no-unsafe-return`
  * `@typescript-eslint/no-unsafe-type-assertion`
  * `@typescript-eslint/no-unnecessary-type-assertion`
  * `@typescript-eslint/ban-ts-comment`

### Known `any` sources

* `JSON.parse()` and `Response.json()` return `any` in TS.
* Boundary mitigation MUST use schema validation (Zod/Valibot) or a typed parser helper.

### Modules & imports

* ESM only (`module: "NodeNext"`, `moduleResolution: "NodeNext"`).
* `verbatimModuleSyntax: true`, `moduleDetection: "force"`.

### Async & cancellation

* Prefer `async/await`.
* Exported async APIs that perform I/O or long work MUST accept `AbortSignal`.

### Formatting & lint split

* **Biome** is the formatter and primary lint for style.
* **ESLint v9 flat config** is required for policy/architecture/security rules.
* Avoid duplicate coverage (Biome formats; ESLint governs policy).

### Testing

* Tests co-located (`__tests__` or `*.test.ts`).
* Vitest is default for browser/client.
* Node test runner allowed for small pure Node libs.
* Snapshots only for intentionally stable serialized outputs.

---

## 5. React Standards

* Components MUST be accessible-by-default (semantic elements first; ARIA only when needed).
* Public components MUST document props and behavior (doc comment or docs site entry).
* Hooks MUST follow the Rules of Hooks; side effects only in `useEffect`/`useLayoutEffect`.
* Prefer controlled components; uncontrolled only when justified.
* Avoid global mutable state; state should be local, passed, or via a chosen state layer.

**React exports**

* Prefer named exports for components/hooks.
* Index barrels MUST NOT cause circular dependencies.

**Testing**

* Component behavior tests MUST focus on user-visible behavior (labels/roles/text), not implementation details.
* Prefer interaction tests over DOM snapshots.

---

## 6. Vite Standards

* Environment variables MUST be explicit, typed, and documented.
* Only variables intended for client exposure may be prefixed for Vite client use; secrets MUST NOT enter client bundles.
* Build modes MUST be reproducible; avoid mode-dependent behavior that changes runtime semantics without tests.
* Prefer explicit `define`/`resolve.alias` governance rather than ad-hoc path hacks.

---

## 7. Tailwind Standards

* Tailwind usage MUST be consistent across the repo (single policy).
* Class ordering MUST be enforced by the chosen linter/formatter (repo-defined).
* Avoid “magic numbers” when theme tokens exist.
* Conditional class composition MUST be readable (prefer a utility like `clsx`/`cva` if adopted by the repo pack).
* Accessibility:

  * Focus states MUST be visible.
  * Color-only signaling is forbidden.

---

## 8. Storybook Standards

* Storybook SHOULD exist for reusable UI libraries and component packs.
* The a11y addon and interaction testing SHOULD be enabled where applicable.
* Stories MUST avoid hidden network calls; use deterministic fixtures.
* Visual regression (if used) MUST run in CI with stable baselines.

---
