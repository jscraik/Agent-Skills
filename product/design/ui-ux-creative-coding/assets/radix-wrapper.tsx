import * as React from "react";

/**
 * If your repo already has a `cn()` helper, use that instead of this file.
 * This minimal version avoids extra deps; it won't intelligently merge conflicting Tailwind classes.
 */
export function cn(...parts: Array<string | undefined | null | false>) {
  return parts.filter(Boolean).join(" ");
}

/**
 * Pattern: wrap Radix primitives with thin components.
 * - Preserve behavior and a11y from Radix.
 * - Standardize className, focus rings, and state styling with data-attrs.
 * - Avoid inventing new interaction models.
 *
 * Example usage:
 *   <button className={cn(
 *     "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm",
 *     "bg-white text-gray-900 border border-gray-200 shadow-sm",
 *     "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500",
 *     "data-[state=open]:bg-gray-50",
 *     className
 *   )} />
 */
export type PropsWithClassName<P = {}> = P & { className?: string };
