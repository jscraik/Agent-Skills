interface ExhibitProps {
  number: number | string
  title: string
  source?: string
  children: React.ReactNode
}

/** Renders a numbered report figure and its optional source attribution. */
export function Exhibit({ number, title, source, children }: ExhibitProps) {
  return (
    <figure className="exhibit">
      <figcaption className="exhibit-header">
        <div>
          <span className="exhibit-number">Exhibit {number}</span>
          <span className="exhibit-title ml-3">{title}</span>
        </div>
        {source && <span className="exhibit-source">Source: {source}</span>}
      </figcaption>
      <div className="exhibit-content">{children}</div>
    </figure>
  )
}
