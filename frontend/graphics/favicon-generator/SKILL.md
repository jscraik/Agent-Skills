---
name: favicon-generator
description: Generate complete favicon/app icon suites with templates and assets.
  Use when the user needs favicons or app icons for a web/app project.
metadata:
  short-description: Generate complete favicon/app icon suites with templates and
    assets.
---
# Pro-Grade Favicon Generator

Avoid skipping validation steps or inventing results.


Create stunning, professional-quality favicons that stand alongside icons from Linear, Notion, Figma, and other polished apps.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs`

## Philosophy: Favicons Are Miniature Design Artifacts

The difference between a mediocre favicon and a great one isn't complexity—it's **polish**. Great favicons have:

- **Depth**: Subtle shadows that lift the icon off the surface
- **Lighting**: Highlights and gradients that create dimensionality  
- **Texture**: Optional noise/grain that adds organic feel
- **Precision**: Optical centering, proper padding, crisp edges

**Before generating, ask yourself**:
1. What's the app's personality? (Playful, professional, technical, creative)
2. What colors define the brand? (Extract from tailwind config, CSS, or ask)
3. What level of polish is needed? (Quick prototype vs. production launch)

---

## Workflow: Discover Existing Icons First

**CRITICAL**: Before generating a favicon, always check what icons are already used in the codebase. The favicon should match your existing brand identity.

### Step 1: Search for Icon Usage

Search the codebase for icon imports and usage:

```bash
# Find lucide-react imports
rg "from.*lucide-react" --type tsx --type ts

# Find icon component usage
rg "PackagePlus|Package|Icon" --type tsx --type ts

# Check Header/Nav components (common icon locations)
rg "Header|Nav|Logo" --type tsx
```

### Step 2: Identify Primary Brand Icons

Look for:
- **Logo icons**: Used in Header, navigation, or branding components
- **Most frequently used icons**: Appear in multiple places
- **Icon libraries**: lucide-react, react-icons, custom SVG components

Example discovery:
```
Found in Header.tsx: PackagePlus from lucide-react
Found in HomePage.tsx: PackagePlus, Package
Primary brand icon: PackagePlus (used in logo/branding)
```

### Step 3: Extract Icon Paths

If using lucide-react or similar libraries:

1. **Locate icon definition**:
   ```bash
   cat node_modules/lucide-react/dist/esm/icons/package-plus.js
   ```

2. **Extract SVG paths** from the icon definition:
   - Lucide icons use 24x24 viewBox
   - Paths are defined as arrays: `["path", { d: "M..." }]`
   - Copy the exact `d` attributes from each path

3. **Use cairosvg for accurate rendering** (recommended):
   ```bash
   pip install cairosvg
   brew install cairo  # required native library
   ```

   **Why cairosvg?** Pillow cannot render SVG bezier curves and arcs. Lucide icons
   use arc commands (`a2 2 0 0 0...`) that only a proper SVG renderer can draw.

### Step 4: Match Favicon to Brand Icon

- **Same icon**: Use the exact icon from your brand (e.g., PackagePlus → PackagePlus favicon)
- **Same colors**: Extract brand colors from Tailwind config or CSS variables
- **Same style**: Match the visual style (minimal, vibrant, etc.)

### Example: PackagePlus Favicon with cairosvg

```python
import cairosvg
from PIL import Image
from io import BytesIO

# Actual Lucide PackagePlus paths (from node_modules/lucide-react/dist/esm/icons/package-plus.js)
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f97316"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" rx="{radius}" fill="url(#bg)"/>
  <g transform="translate({offset}, {offset}) scale({scale})" 
     stroke="#ffffff" stroke-width="2" fill="none" 
     stroke-linecap="round" stroke-linejoin="round">
    <!-- Exact Lucide PackagePlus paths -->
    <path d="M16 16h6"/>
    <path d="M19 13v6"/>
    <path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l2-1.14"/>
    <path d="m7.5 4.27 9 5.15"/>
    <polyline points="3.29 7 12 12 20.71 7"/>
    <line x1="12" x2="12" y1="22" y2="12"/>
  </g>
</svg>"""

def render_lucide_icon(size):
    # Lucide uses 24x24, scale to fit in favicon with padding
    scale = (size * 0.7) / 24
    offset = size * 0.15
    radius = int(size * 0.22)

    svg = SVG_TEMPLATE.format(size=size, scale=scale, offset=offset, radius=radius)
    png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
    return Image.open(BytesIO(png_data)).convert('RGBA')
```

### Why This Matters

- **Consistency**: Favicon matches your app's visual identity
- **Brand recognition**: Users recognize your icon across contexts
- **Professionalism**: Shows attention to detail and design coherence
- **Avoids mismatch**: Prevents generating a favicon that doesn't match your actual logo

---

### The Effects Stack

Professional favicons are built in **layers**, not drawn flat:

```
┌─────────────────────────────────────┐
│  Layer 6: Content (letter/icon)    │ ← With its own shadow
│  Layer 5: Noise texture            │ ← Subtle grain for organic feel
│  Layer 4: Highlight gradient       │ ← Top-lit shine effect
│  Layer 3: Inner glow               │ ← Ambient light/shadow
│  Layer 2: Background               │ ← Gradient or solid
│  Layer 1: Drop shadow              │ ← Depth and lift
└─────────────────────────────────────┘
```

Each layer is subtle. Combined, they create polish that's felt rather than seen.

---

## Generation Tools

This skill provides two complementary tools:

### Tool 1: Interactive HTML Generator
**File**: `scripts/generate_favicon_pro.html`

Open in browser for real-time preview and customization:
- 8 professional design templates
- 18 Lucide icons + letter/emoji modes
- Live effect adjustment (shadow, glow, highlight, noise)
- All sizes preview (16px to 512px)
- Context preview (browser tab, bookmarks)
- Bulk download

**Best for**: Quick iteration, visual exploration, client demos

### Tool 2: Python CLI Pipeline  
**File**: `scripts/generate_favicon.py`

Command-line generation with Pillow:
```bash
# Using a template
python generate_favicon.py --letter A --style vibrant --output ./public/

# Custom colors
python generate_favicon.py --letter T --bg "#22c55e" --bg2 "#14b8a6" --output ./favicons/

# Full control
python generate_favicon.py --letter N --bg "#0f172a" --fg "#22d3ee" \
  --shadow 0.6 --glow 0.5 --noise 0.04 --output ./icons/
```

**Best for**: CI/CD integration, batch generation, precise control

---

## Design Templates

Choose a template that matches the app's personality:

| Template | Colors | Character | Best For |
|----------|--------|-----------|----------|
| **Modern** | Indigo → Purple | Clean, trustworthy | SaaS, productivity |
| **Vibrant** | Pink → Orange | Energetic, bold | Consumer apps, social |
| **Minimal** | Near-black | Understated, technical | Dev tools, utilities |
| **Glass** | Blue → Cyan | Airy, modern | Dashboards, analytics |
| **Neon** | Dark + Cyan glow | Futuristic, edgy | Gaming, creative tools |
| **Warm** | Amber → Red | Friendly, approachable | Food, lifestyle, community |
| **Forest** | Green → Teal | Natural, sustainable | Health, environment, finance |
| **Mono** | White + Black | Minimal, adaptable | Any (works in any context) |

### Template Selection Guide

```
App personality assessment:
├── Professional/Enterprise → Minimal, Modern, Mono
├── Consumer/Fun → Vibrant, Warm, Neon
├── Technical/Developer → Minimal, Glass, Neon
├── Health/Wellness → Forest, Warm
└── Creative/Design → Vibrant, Glass, Modern
```

---

## Content Types

### 1. Letter/Monogram (Default)
Single letter or two-letter combination from app name.

```
"TaskFlow" → "T" or "TF"
"Acme Corp" → "A" or "AC"
```

**Typography considerations**:
- Single letters work better at small sizes
- Choose distinctive letters (avoid O, I which lack character)
- Font weight matters—bold reads better at 16px

### 2. Icons (Lucide Integration)
18 curated Lucide icons for common app types:

| Icon | Use Case |
|------|----------|
| `rocket` | Startups, launch, speed |
| `zap` | Performance, automation |
| `star` | Favorites, ratings, premium |
| `heart` | Health, favorites, social |
| `code` | Developer tools, IDEs |
| `box` | Packages, containers, storage |
| `compass` | Navigation, exploration |
| `flame` | Trending, hot, energy |
| `globe` | International, web, browser |
| `layers` | Design, stacks, organization |
| `music` | Audio, media, entertainment |
| `send` | Messaging, communication |
| `shield` | Security, protection, trust |
| `sparkles` | AI, magic, premium |
| `sun` | Light mode, energy, positivity |
| `target` | Goals, focus, precision |
| `terminal` | CLI, developer, technical |
| `wand` | Magic, automation, creative |

### 3. Emoji
Native emoji for playful, informal apps.

```
🚀 → Launch, speed, startups
💡 → Ideas, innovation
🔥 → Trending, hot
✨ → Premium, magic
```

**Note**: Emoji rendering varies by OS—test on multiple platforms.

---

## Effects Reference

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.
