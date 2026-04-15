# Extended guidance

### Drop Shadow
Creates depth and lift. Essential for polished look.

| Intensity | Effect | Use When |
|-----------|--------|----------|
| 0.2–0.3 | Subtle | Minimal designs, light backgrounds |
| 0.4–0.5 | Balanced | Most apps (default) |
| 0.6+ | Strong | Dark backgrounds, high contrast |

### Highlight
Top-lit gradient that adds dimensionality.

| Intensity | Effect | Use When |
|-----------|--------|----------|
| 0.15–0.25 | Gentle | Subtle polish |
| 0.3–0.4 | Pronounced | Glass, vibrant styles |
| 0.5+ | Strong | Glossy, skeuomorphic look |

### Inner Glow
Radial lighting from center, creates depth.

| Intensity | Effect | Use When |
|-----------|--------|----------|
| 0.2–0.3 | Soft ambient | Glass style |
| 0.4–0.5 | Noticeable | Neon, futuristic |
| 0.6+ | Strong | Glowing effect |

### Noise/Grain
Subtle texture that prevents banding and adds organic feel.

| Intensity | Effect | Use When |
|-----------|--------|----------|
| 0.03–0.05 | Barely visible | Anti-banding only |
| 0.06–0.08 | Subtle texture | Organic, natural feel |
| 0.1+ | Visible grain | Vintage, film aesthetic |

### Corner Radius
Shape of the icon background.

| Value | Shape | Platform |
|-------|-------|----------|
| 0.15–0.18 | Squircle | rounded |
| 0.20–0.24 | Rounded | Modern default |
| 0.30+ | Very round | Playful, bubble |
| 0.50 | Circle | Circular icons |

---

## Output structure, integration, and workflows

See `Infrastructure/references/extra.md` for:
- The standard output file suite
- Framework integration examples (Next.js/HTML/PWA)
- Workflow examples and extended guidance

## Anti-patterns
- Using emojis or raster logos without SVG cleanup.
- Shipping only one size or omitting apple-touch-icon.
- Ignoring brand color/contrast readability at 16px.

---

## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.
