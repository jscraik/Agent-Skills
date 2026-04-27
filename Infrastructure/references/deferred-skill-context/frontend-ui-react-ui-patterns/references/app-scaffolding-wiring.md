# React App Scaffolding and Wiring

Use this when creating a new React feature or layout shell.

## Baseline wiring
- Router: follow the repo router (React Router, TanStack Router, or Next).
- Providers: add theme, data, and auth providers at the root layout.
- Layout: create a shell with header, content, and optional sidebar.

## Minimal layout shell (example)

```tsx
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
    </div>
  );
}
```

## Route map (example)

```ts
export const routes = {
  home: "/",
  settings: "/settings",
  items: "/items",
};
```

Keep route and layout changes consistent with repo conventions.
