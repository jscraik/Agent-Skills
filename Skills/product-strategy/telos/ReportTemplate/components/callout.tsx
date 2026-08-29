interface CalloutProps {
  label?: string
  children: React.ReactNode
}

/** Renders a highlighted takeaway with an optional label. */
export function Callout({ label = "Key Takeaway", children }: CalloutProps) {
  return (
    <div className="callout">
      <div className="callout-label">{label}</div>
      <div className="callout-content">{children}</div>
    </div>
  )
}
