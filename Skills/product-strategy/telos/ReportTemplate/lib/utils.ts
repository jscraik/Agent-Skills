import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/** Merges conditional Tailwind class values. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
