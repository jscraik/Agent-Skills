# Supplemental Icons: Communication

Last verified: 2026-01-01

```tsx
export function IconEmail({ className = "size-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" strokeWidth="2"/>
      <path d="M2 6L12 13L22 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function IconPhone({ className = "size-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 16.92V19.92C22 20.5 21.5 21 20.92 21C10.42 21 2 12.58 2 2.08C2 1.5 2.5 1 3.08 1H6.08C6.66 1 7.17 1.5 7.23 2.08C7.35 3.19 7.59 4.27 7.95 5.3C8.09 5.71 7.99 6.17 7.66 6.5L5.84 8.32C7.38 11.37 9.63 13.62 12.68 15.16L14.5 13.34C14.83 13.01 15.29 12.91 15.7 13.05C16.73 13.41 17.81 13.65 18.92 13.77C19.5 13.83 20 14.34 20 14.92V17.92C20 18.5 19.5 19 18.92 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function IconComment({ className = "size-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
```
