# OG Image Best Practices

## Design Philosophy

### 1. Brand Extension, Not Decoration

OG images should feel like a natural preview of your site, not a generic social card slapped on top.

**Good**: Uses site's actual colors, fonts, and design language
**Bad**: Generic gradient background with standard fonts

### 2. Context-Appropriate

Different page types deserve different treatments.

**Landing page**: Bold, minimal, value proposition
**Blog post**: Title + excerpt, publication context
**Product**: Product name + key benefit
**Documentation**: Clean, organized, topic-focused

### 3. Authentic Content

Use actual page metadata, not placeholders.

**Good**: Real page title and description
**Bad**: "Lorem ipsum" or generic "Blog Post" text

## Visual Design

### Typography

**Headlines**:
- 48-72px for main title
- Bold weight (700-800)
- Max 2-3 lines
- Leave breathing room

**Body text**:
- 24-32px for descriptions
- Regular/medium weight (400-500)
- Max 2 lines
- High contrast

**Font pairing**:
- Use site's actual fonts when possible
- Fallback to system fonts for reliability
- Avoid more than 2 font families

### Color

**Background strategies**:

1. **Solid brand color**
   - Simple, recognizable
   - Works well if brand has strong color
   - Ensure text contrast

2. **Subtle gradient**
   - Add visual interest
   - Keep subtle (not rainbow)
   - Use brand colors

3. **Light background with color accent**
   - Clean, professional
   - Color for emphasis
   - Works for corporate sites

**Avoid**:
- Too many colors competing
- Low contrast text
- Overly bright/saturated backgrounds

### Layout

**Alignment options**:

1. **Centered**: Clean, symmetrical
   - Good for: Landing pages, about pages
   - Message feels balanced, authoritative

2. **Left-aligned**: Modern, readable
   - Good for: Articles, documentation
   - Feels natural for text-heavy content

3. **Split**: Visual + text
   - Good for: Products, features
   - Balances visual and text content

**Spacing**:
- Generous padding (60-80px minimum)
- Whitespace is your friend
- Don't fill every pixel

### Visual Elements

**Logo placement**:
- Top left or center (if brand-focused)
- Bottom left (if content-focused)
- Keep reasonably sized (40-100px height)

**Icons/graphics**:
- Use sparingly
- Support the message, don't distract
- Match brand style

**Decorative elements**:
- Subtle shapes or patterns
- Background only
- Don't compete with content

## Content Strategy

### Title Treatment

**Do**:
- Use actual page title
- Edit for length if needed (maintain meaning)
- Emphasize key words with weight/color
- Make it scannable

**Don't**:
- Truncate with "..."
- Use all caps (unless brand style)
- Cram long titles at small size
- Use vague titles

### Description

**When to include**:
- Articles: Yes (provides context)
- Products: Yes (key benefit)
- Landing: Optional (title may be enough)
- Documentation: Yes (scope/topic)

**Best practices**:
- 1-2 sentences max
- Complement title, don't repeat
- Increase value of preview
- Edit for clarity

### Metadata to Use

Pull from page metadata:
- `title`: Primary heading
- `description`: Supporting text
- `author`: For articles/blogs
- `date`: For news/articles
- `category`: For organization

## Technical Excellence

### Performance

**File size**:
- Target: <100KB
- Maximum: 200KB
- Use PNG compression tools
- JPEG at 80-90% quality

**Optimization**:
- Use sharp contrasts (compresses well)
- Avoid gradients with banding
- Limit transparency (use JPEG if possible)

### Accessibility

**Alt text**:
- Describe image content
- Don't just repeat title
- Be concise but informative

```html
<!-- Good -->
<meta property="og:image:alt" content="Product dashboard showing analytics graphs and metrics" />

<!-- Bad -->
<meta property="og:image:alt" content="OG image" />
```

### Consistency

**Across pages**:
- Same brand elements (logo, colors, fonts)
- Consistent layout approach per page type
- Predictable structure

**But also variation**:
- Different content per page
- Adapted layout for page type
- Contextually appropriate

## Page Type Patterns

### Landing Page

**Focus**: Value proposition
**Layout**: Centered, bold
**Elements**: Title, optional description, logo
**Tone**: Confident, clear

Example structure:
```
[Centered]
[Logo (optional)]
[Large bold title]
[Short description]
```

### Article/Blog Post

**Focus**: Title and context
**Layout**: Left-aligned, organized
**Elements**: Category/date, title, excerpt, logo
**Tone**: Informative, inviting

Example structure:
```
[Top: "Article" or category]
[Title - large]
[Excerpt - medium]
[Bottom: Logo or author]
```

### Product Page

**Focus**: Product name and benefit
**Layout**: Split or centered
**Elements**: Product name, key benefit, visual if available
**Tone**: Clear, benefit-focused

Example structure:
```
[Left: Product name, benefit]
[Right: Product visual (optional)]
```

### Documentation

**Focus**: Topic and clarity
**Layout**: Clean, organized
**Elements**: "Documentation" label, topic, description
**Tone**: Professional, helpful

Example structure:
```
[Top: "Documentation"]
[Topic - large]
[Description - structured]
```

### About/Company

**Focus**: Brand and identity
**Layout**: Centered, brand-forward
**Elements**: Logo prominent, company name, tagline
**Tone**: Professional, welcoming

Example structure:
```
[Centered]
[Logo - large]
[Company name]
[Tagline]
```

## Workflow Best Practices

### 1. Analyze First

Don't jump to generation. Understand:
- What framework/structure exists
- What routes need images
- What brand assets are available
- What design patterns are in use

### 2. Extract Brand

Pull from actual codebase:
- Colors from CSS/Tailwind config
- Fonts from stylesheets
- Logo from assets
- Design patterns from components

### 3. Categorize Routes

Different page types need different approaches:
- Landing vs article vs product
- Marketing vs documentation
- Static vs dynamic content

### 4. Generate Contextually

For each route:
- Use appropriate layout for page type
- Pull actual metadata
- Apply brand consistently
- Vary appropriately

### 5. Review and Refine

Don't just generate and forget:
- Preview in actual social platforms
- Check readability at thumbnail size
- Verify brand alignment
- Test sharing experience

## Common Mistakes

### Design Mistakes

❌ **Template convergence**: All images look identical
→ Vary layout by page type

❌ **Over-design**: Too many elements, colors, effects
→ Simplify, focus on 1-2 elements

❌ **Tiny text**: Unreadable when scaled
→ Use large, bold typography

❌ **Brand disconnect**: Looks nothing like the site
→ Extract and use actual brand elements

### Technical Mistakes

❌ **Relative URLs**: Image doesn't load
→ Use absolute URLs

❌ **Huge file sizes**: Slow to load
→ Optimize images (<200KB)

❌ **Missing meta tags**: No preview shows
→ Include all essential OG tags

❌ **Not testing**: Issues discovered after launch
→ Test with platform preview tools

### Process Mistakes

❌ **Manual creation**: Not scalable
→ Script the generation process

❌ **One-size-fits-all**: Same image for all pages
→ Generate per-route with context

❌ **Ignoring existing assets**: Starting from scratch
→ Reuse components and brand elements

❌ **No maintenance plan**: Images become outdated
→ Make generation reproducible and updatable

## Quality Checklist

Before finalizing OG images:

**Design**:
- [ ] Uses actual brand colors and fonts
- [ ] Typography is readable at thumbnail size
- [ ] Layout is appropriate for page type
- [ ] Content uses actual metadata, not placeholders
- [ ] Visual hierarchy is clear
- [ ] Sufficient whitespace and padding
- [ ] High contrast for readability

**Technical**:
- [ ] 1200x630px dimensions
- [ ] File size <200KB
- [ ] PNG or high-quality JPEG
- [ ] Absolute URLs in meta tags
- [ ] All essential OG tags present
- [ ] Alt text provided
- [ ] Accessible over HTTPS

**Content**:
- [ ] Title is accurate and clear
- [ ] Description adds value
- [ ] No lorem ipsum or placeholders
- [ ] Context-appropriate for page type
- [ ] Brand elements present (logo, etc.)

**Testing**:
- [ ] Previewed on Facebook/LinkedIn/Twitter
- [ ] Readable at small sizes
- [ ] No content cut off
- [ ] Cache cleared on platforms
- [ ] Actually appears when sharing

## Progressive Enhancement

Start simple, enhance as needed:

1. **MVP**: Basic title + brand color + logo
2. **Enhanced**: Add descriptions, better typography
3. **Polished**: Page-type-specific layouts
4. **Advanced**: Custom graphics, illustrations

Don't over-engineer on first pass. Get working images, then refine.
