# DialKit Live Tuning

Generate DialKit configurations for React + Motion projects so users can tune parameters in real time and feel differences instantly.

---

## Table of Contents
- [When to Use](#when-to-use)
- [Live Tuning Principle](#live-tuning-principle)
- [Modes](#modes)
- [Setup Check](#setup-check)
- [Control Patterns](#control-patterns)
- [Output Format](#output-format)

## When to Use

Trigger on:
- `dialkit`, `sliders`, `dials`, `controls`, `tune`, `tweak`
- “let me adjust this live”
- “add a control panel”
- “help me compare many parameter combinations”

## Live Tuning Principle

Expose key parameters (duration, spring, spacing, blur, scale, offsets, etc.) so they can be changed while interacting with the real UI.

Benefits:
- faster intuition building
- better feel calibration
- easier exploration of unexpected combinations

## Modes

### 1) Direct Mode
User names properties and context. Generate config immediately.

### 2) Guided Mode
If ambiguous, ask up to 3 short questions:
1. Which component or interaction?
2. Which property families? (visual, position, animation, interaction)
3. Is this for single-state tuning or multi-variant exploration?

### 3) Exploration Mode
Add controls that generate/rank multiple randomized variants when user wants broader depth exploration.

## Setup Check

If editing a codebase, verify:
1. `dialkit` and `motion` installed
2. root `DialRoot` exists

Install snippet:
```bash
npm install dialkit motion
```

Root setup:
```tsx
import { DialRoot } from 'dialkit'
import 'dialkit/styles.css'

<DialRoot position="top-right" />
```

## Control Patterns

Reference full schema: [references/config-patterns.json](references/config-patterns.json)

### Sliders
```tsx
blur: [0, 0, 100]
scale: [1, 0.5, 2]
opacity: [1, 0, 1]
```

### Spring (default to time mode)
```tsx
spring: {
  type: 'spring',
  visualDuration: 0.3,
  bounce: 0.2,
}
```

### Folders / grouped controls
```tsx
shadow: {
  offsetY: [8, 0, 24],
  blur: [16, 0, 48],
  opacity: [0.2, 0, 1],
}
```

### Actions
```tsx
reset: { type: 'action' },
randomize: { type: 'action', label: 'Randomize' },
```

### Exploration controls
```tsx
variantCount: [6, 2, 24],
columns: [3, 1, 6],
randomSeed: [1, 1, 9999],
```

## Output Format

Always return copy-paste-ready code with:
1. imports
2. `useDialKit` config
3. clear parameter application in `style`/`animate`/`transition`
4. optional `onAction` handlers

Template:
```tsx
import { useDialKit } from 'dialkit'
import { motion } from 'motion/react'

function ComponentName() {
  const params = useDialKit('ComponentName', {
    scale: [1, 0.5, 2],
    blur: [0, 0, 100],
    spring: { type: 'spring', visualDuration: 0.3, bounce: 0.2 },
  })

  return (
    <motion.div
      style={{ filter: `blur(${params.blur}px)` }}
      animate={{ scale: params.scale }}
      transition={params.spring}
    />
  )
}
```

If the user asks for breadth/depth ideation, pair this with [conceptual-range.md](conceptual-range.md) or [conceptual-depth.md](conceptual-depth.md).
