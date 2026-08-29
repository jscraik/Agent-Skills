import { cn } from "@/lib/utils.js"

export interface SectionProps {
  title: string
  children: React.ReactNode
  className?: string
}

/**
 * Renders a report section with a semantic `h2` heading.
 *
 * `title` and `children` are required. `className` is optional and is merged
 * with the base report-section class when supplied; the section always keeps
 * the semantic heading and its child content.
 */
export function Section({ title, children, className }: SectionProps) {
  return (
    <section className={cn("report-section", className)}>
      <h2>{title}</h2>
      {children}
    </section>
  )
}
