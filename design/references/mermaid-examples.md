# Mermaid Diagram Examples

## State Diagram Example (stateful component)

```mermaid
stateDiagram-v2
    [*] --> ORDERBOOK_OK: amount entered
    ORDERBOOK_OK --> ORDERBOOK_OK: orderbook fresh + canFill
    ORDERBOOK_OK --> CHECKING: orderbook stale + HAS cached estimate
    ORDERBOOK_OK --> CHECKING: orderbook stale + NO cached estimate
    ORDERBOOK_OK --> CHECKING: orderbook canFill=false
    CHECKING --> CONFIRMED: canFill=true / show estimate
    CHECKING --> INSUFFICIENT: canFill=false / show warning
    CONFIRMED --> CHECKING: periodic re-check (10s)
    INSUFFICIENT --> CHECKING: periodic re-check (10s)
    CONFIRMED --> IDLE: amount changes / market changes
    INSUFFICIENT --> IDLE: amount changes / market changes
    IDLE --> [*]
```

## Export Requirement

To export diagrams for review/sharing:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mmd -o diagram.png --theme dark --scale 1.5 --backgroundColor '#111827'
```

Keep the Mermaid source in the spec even after exporting. Adjust input/output names as needed.