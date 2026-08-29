export interface QuoteBlockProps {
  quote: string
  attribution: string
  role?: string
}

/**
 * Renders a quoted observation with attribution.
 *
 * `quote` and `attribution` are required and rendered verbatim. `role` is
 * optional; when supplied it is appended after the attribution, and when
 * omitted no role punctuation or placeholder is rendered.
 */
export function QuoteBlock({ quote, attribution, role }: QuoteBlockProps) {
  return (
    <div className="quote-block">
      <p className="quote-text">{quote}</p>
      <p className="quote-attribution">
        — {attribution}
        {role && <span className="text-muted">, {role}</span>}
      </p>
    </div>
  )
}
