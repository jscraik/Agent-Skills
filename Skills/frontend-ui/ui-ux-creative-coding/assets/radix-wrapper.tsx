import * as React from "react";

// =============================================================================
// TYPES
// =============================================================================

/**
 * Generic type for component props that accept a className.
 * Uses `unknown` instead of `{}` for better type safety (avoids allowing any non-nullish value).
 */
export type PropsWithClassName<P = unknown> = P & {
  readonly className?: string;
};

/**
 * Polymorphic component props - allows component to render as different elements
 * via the `as` prop while maintaining type safety.
 *
 * @example
 * <Text as="h1">Heading</Text>
 * <Text as={Link} to="/">Link</Text>
 */
export type PolymorphicProps<
  E extends React.ElementType = React.ElementType,
  P = unknown,
> = PropsWithClassName<P> & {
  readonly as?: E;
};

/**
 * Full polymorphic component props including inherited HTML attributes.
 * Omits conflicting props from the base element (className, etc.).
 */
export type PolymorphicComponentProps<
  E extends React.ElementType,
  P = unknown,
> = PolymorphicProps<E, P> &
  Omit<React.ComponentPropsWithoutRef<E>, keyof PolymorphicProps<E, P>>;

/**
 * Props for components with visual variants.
 */
export type VariantProps<
  V extends Record<string, readonly string[] | string[]>,
> = {
  readonly [K in keyof V]?: V[K] extends readonly string[]
    ? V[K][number]
    : V[K] extends string[]
      ? V[K][number]
      : never;
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Joins CSS class names, filtering out falsy values.
 *
 * If your repo has `clsx` or `tailwind-merge`, use those instead.
 * This minimal version has no dependencies but won't intelligently
 * merge conflicting Tailwind classes.
 *
 * @param parts - Class name parts (strings, null, undefined, false)
 * @returns Joined class string
 */
export function cn(
  ...parts: ReadonlyArray<string | undefined | null | false | 0 | "">
): string {
  return parts.filter(Boolean).join(" ");
}

/**
 * Type guard to check if a value is a valid React element with className.
 */
export function isReactElementWithClassName(
  child: unknown,
): child is React.ReactElement<PropsWithClassName> {
  return (
    React.isValidElement(child) &&
    typeof child.props === "object" &&
    child.props !== null &&
    "className" in child.props
  );
}

// =============================================================================
// POLYMORPHIC COMPONENT HELPER
// =============================================================================

/**
 * Hook for polymorphic components that provides proper ref forwarding
 * and type-safe element rendering.
 *
 * @example
 * const Component = React.forwardRef(function Component<E extends React.ElementType = 'div'>(
 *   { as, ...props }: PolymorphicComponentProps<E>,
 *   ref: React.Ref<Element>
 * ) {
 *   const Component = usePolymorphicComponent(as || 'div');
 *   return <Component ref={ref} {...props} />;
 * });
 */
export function usePolymorphicComponent<E extends React.ElementType>(
  as: E,
): E {
  return as;
}

// =============================================================================
// EXAMPLE: TYPED WRAPPER COMPONENTS
// =============================================================================

/**
 * Props for the Text component - demonstrates polymorphic patterns.
 */
type TextSize = "xs" | "sm" | "base" | "lg" | "xl";
type TextWeight = "normal" | "medium" | "semibold" | "bold";

interface TextOwnProps {
  readonly size?: TextSize;
  readonly weight?: TextWeight;
  readonly muted?: boolean;
}

/**
 * Polymorphic Text component - can render as any HTML element or component.
 *
 * @example
 * <Text>Default paragraph</Text>
 * <Text as="h1" size="xl" weight="bold">Heading</Text>
 * <Text as="label" size="sm" muted>Subtle label</Text>
 */
export const Text = React.forwardRef(function Text<
  E extends React.ElementType = "p",
>(
  {
    as,
    size = "base",
    weight = "normal",
    muted = false,
    className,
    children,
    ...props
  }: PolymorphicComponentProps<E, TextOwnProps>,
  ref: React.Ref<E extends keyof HTMLElementTagNameMap ? HTMLElementTagNameMap[E] : unknown>,
) {
  const Component = usePolymorphicComponent(as || "p");

  const sizeClasses: Record<TextSize, string> = {
    xs: "text-xs",
    sm: "text-sm",
    base: "text-base",
    lg: "text-lg",
    xl: "text-xl",
  };

  const weightClasses: Record<TextWeight, string> = {
    normal: "font-normal",
    medium: "font-medium",
    semibold: "font-semibold",
    bold: "font-bold",
  };

  return (
    <Component
      ref={ref}
      className={cn(
        sizeClasses[size],
        weightClasses[weight],
        muted && "text-gray-500",
        className,
      )}
      {...props}
    >
      {children}
    </Component>
  );
});

// =============================================================================
// RADIX UI WRAPPER PATTERNS
// =============================================================================

/**
 * Standardized focus ring classes for interactive elements.
 * Use with Radix primitives to ensure consistent focus states.
 */
export const focusRingClasses =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2" as const;

/**
 * Standardized disabled state classes.
 */
export const disabledClasses =
  "disabled:pointer-events-none disabled:opacity-50" as const;

/**
 * Base props for Radix primitive wrappers.
 */
export interface RadixWrapperProps {
  readonly className?: string;
  readonly children?: React.ReactNode;
}

/**
 * Helper to create type-safe wrapper props for Radix components.
 * Preserves all original props while adding className support.
 */
export type WithRadixProps<
  P extends Record<string, unknown>,
> = P & RadixWrapperProps;

// =============================================================================
// EXPORTS
// =============================================================================

/**
 * Pattern: wrap Radix primitives with thin components.
 * - Preserve behavior and a11y from Radix.
 * - Standardize className, focus rings, and state styling with data-attrs.
 * - Avoid inventing new interaction models.
 *
 * Example usage with this wrapper:
 *   <button className={cn(
 *     "inline-flex items-center justify-center rounded-md px-3 py-2 text-sm",
 *     "bg-white text-gray-900 border border-gray-200 shadow-sm",
 *     focusRingClasses,
 *     "data-[state=open]:bg-gray-50",
 *     className
 *   )} />
 */
