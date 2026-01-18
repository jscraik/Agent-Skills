# Extended Guidance

   
3. [Selects approach]
   - Option A: Match brand icon (PackagePlus) → Extract paths from lucide-react
   - Option B: Use letter "F" (distinctive, good at small sizes)
   - Decision: Use PackagePlus to match brand identity
   - Style: "Modern" (professional SaaS)
   - Colors: Use brand indigo
   
4. [Extracts icon paths]
   - Reads: node_modules/lucide-react/dist/esm/icons/package-plus.js
   - Extracts SVG paths and converts 24x24 → 32x32
   
5. [Generates with Python script]
   python generate_packageplus_favicon.py --output ./public/
   
6. [Integrates with Next.js]
   Updates app/layout.tsx with metadata.icons
   
7. [Delivers]
   "Created favicon suite matching your PackagePlus brand icon. 
   The favicon now matches your Header logo exactly—check the browser tab preview."
```

### Example 2: Developer Tool

```
User: "Make a favicon for my CLI tool"

Claude:
1. [Discovers existing icons]
   - Searches: rg "Icon|Logo" --type tsx
   - Finds: No existing brand icons, new project
   
2. [Considers personality]
   - Developer audience → technical, minimal
   - CLI context → terminal icon fits well
   
3. [Selects approach]
   - Content: Terminal icon from Lucide (extract actual paths)
   - Style: "Minimal" (dark, understated)
   - Effects: Subtle shadow, slight noise
   
4. [Extracts Terminal icon paths]
   - Reads: node_modules/lucide-react/dist/esm/icons/terminal.js
   - Converts paths to favicon coordinate system
   
5. [Opens HTML generator for preview]
   Shows user the terminal icon in minimal style
   
6. [Adjusts based on feedback]
   User: "Can we make it more techy?"
   → Switches to "Neon" style with cyan glow
   
7. [Generates final suite]
   Downloads all sizes, integrates with project
```

### Example 3: Playful Consumer App

```
User: "I need a fun favicon with a rocket for my startup"

Claude:
1. [Selects approach]
   - Content: Rocket icon (not emoji for consistency)
   - Style: "Vibrant" (pink→orange, energetic)
   - Effects: Strong shadow, highlight, no noise
   
2. [Previews in context]
   Shows browser tab mockup, bookmark bar
   
3. [Generates]
   Full suite with all sizes
   
4. [Delivers with context]
   "Here's your rocket favicon in vibrant colors. The icon 
   stays crisp even at 16px. I've included the apple-touch-icon
   for when users add to their phone home screen."
```

---

## Anti-Patterns

❌ **Flat, shadowless designs**
```
Problem: Icon looks pasted on, no depth
Fix: Add at least 0.3 shadow intensity
```

❌ **Over-complicated at small sizes**
```
Problem: 16px version is unrecognizable mush
Fix: Test at actual 16px—simplify if needed
```

❌ **Generic blue gradient**
```
Problem: Looks like every other AI-generated icon
Fix: Use brand colors, vary the template
```

❌ **Ignoring the effects stack**
```
Problem: Just background + letter, looks amateur
Fix: Apply shadow + highlight at minimum
```

❌ **Wrong template for context**
```
Problem: Neon style for a healthcare app
Fix: Match template to brand personality
```

❌ **Skipping the preview step**
```
Problem: Looks good at 512px, bad at 16px
Fix: Always check size previews before finalizing
```

❌ **Not testing in context**
```
Problem: Colors clash with browser chrome
Fix: Use context preview (tab, bookmarks)
```

---

## Variation Guidance

**CRITICAL**: Each favicon should feel custom, not templated.

**Vary by app type**:
- Dev tools → Terminal icon, Minimal/Neon style, dark colors
- Consumer apps → Vibrant icons, warm colors, playful shapes
- Enterprise → Letter monogram, Modern/Mono style, brand colors
- Creative tools → Abstract shapes, Glass style, unique gradients

**Vary the effects**:
- Don't always use the same shadow intensity
- Try different corner radii
- Experiment with inner glow for certain styles
- Add noise for organic apps, skip for technical ones

**Vary the content**:
- Not every app needs a letter
- Icons can be more memorable than letters
- Consider the app's core action (send, shield, target)

---

## Quick Reference

### Python CLI
```bash
# Basic
python generate_favicon.py --letter A --output ./public/

# With template
python generate_favicon.py --letter T --style vibrant --output ./public/

# Custom colors
python generate_favicon.py --letter N --bg "#0f172a" --bg2 "#1e293b" \
  --fg "#22d3ee" --output ./public/

# Full control
python generate_favicon.py --letter M \
  --bg "#ec4899" --bg2 "#f97316" --fg "#ffffff" \
  --shadow 0.5 --highlight 0.3 --glow 0.2 --noise 0.05 \
  --radius 0.24 --output ./public/
```

### Available Templates
`modern`, `vibrant`, `minimal`, `glass`, `neon`, `warm`, `forest`, `mono`

### Available Icons
`rocket`, `zap`, `star`, `heart`, `code`, `box`, `compass`, `flame`, `globe`, `layers`, `music`, `send`, `shield`, `sparkles`, `sun`, `target`, `terminal`, `wand`

### Effect Ranges
- Shadow: 0.0–1.0 (default: 0.4)
- Highlight: 0.0–1.0 (default: 0.25)
- Inner Glow: 0.0–1.0 (default: 0.0)
- Noise: 0.0–1.0 (default: 0.0)
- Corner Radius: 0.0–0.5 (default: 0.22)

---

## Remember

**Great favicons are felt, not analyzed.** Users don't consciously notice the drop shadow or the highlight gradient—they just sense that the icon feels professional and polished.

The difference between amateur and professional is:
1. **Layered effects** vs. flat rendering
2. **Considered templates** vs. random colors
3. **Size-appropriate detail** vs. complexity that muddies
4. **Tested in context** vs. only viewed at full size

Use the tools to handle the technical complexity. Focus your energy on choosing the right personality, colors, and content for the specific app.

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.


## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.

## Examples
- See `references/extra.md` for extended examples and notes.

## Procedure
1) Confirm objective.
2) Gather required inputs.
3) Execute steps.
4) Validate output.

## Antipatterns
- Do not add features outside the agreed scope.
