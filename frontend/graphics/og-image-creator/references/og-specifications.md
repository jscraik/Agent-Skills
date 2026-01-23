# Open Graph Image Specifications

## Standard Dimensions

**Recommended**: 1200 x 630 pixels (1.91:1 ratio)

This is the standard size supported by all major platforms:
- Facebook
- Twitter/X
- LinkedIn
- Slack
- Discord

**Minimum**: 600 x 314 pixels
**Maximum**: 8MB file size (but aim for <200KB)

## Image Formats

**Recommended**: PNG
- Better quality for text
- Supports transparency (though not used in OG context)
- Widely supported

**Alternative**: JPG
- Smaller file size
- Good for photo-heavy images
- 80-90% quality recommended

**Avoid**: GIF (limited to first frame), WebP (limited support)

## Meta Tags

### Essential Tags

```html
<!-- Required -->
<meta property="og:title" content="Page Title" />
<meta property="og:image" content="https://example.com/og-image.png" />
<meta property="og:url" content="https://example.com/page" />
<meta property="og:type" content="website" />

<!-- Highly recommended -->
<meta property="og:description" content="Page description" />
<meta property="og:site_name" content="Site Name" />

<!-- Image details -->
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Description of image content" />
```

### Twitter-Specific Tags

```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://example.com/og-image.png" />
<meta name="twitter:title" content="Page Title" />
<meta name="twitter:description" content="Page description" />
```

**Important**: Twitter requires absolute URLs for images.

## Design Best Practices

### Safe Zone

Keep important content within the **safe zone** to account for platform overlays:
- **Top**: 60px padding
- **Bottom**: 60px padding
- **Left/Right**: 80px padding

Some platforms overlay logos, play buttons, or other UI elements.

### Text Readability

**Font sizes**:
- Headline: 48-72px
- Subheading: 28-36px
- Body text: 20-28px

**Contrast**:
- Ensure sufficient contrast (WCAG AA minimum: 4.5:1)
- Text should be readable when scaled down to thumbnail size

**Font weights**:
- Use bold (700+) for headlines
- Regular (400) or medium (500) for body text

### Visual Hierarchy

**Focus on 1-2 key elements**:
- Primary: Page title or main message
- Secondary: Supporting text or visual

**Avoid**:
- Too much text (max 2-3 lines for headline)
- Cluttered layouts
- Small text or icons

### Color

**Background**:
- Solid color: Simple, brand-aligned
- Gradient: Subtle, not distracting
- Image: Low opacity or darkened for text contrast

**Text**:
- High contrast with background
- Use brand colors for accents, not all text

## Testing

### Validation Tools

1. **OpenGraph.xyz**: https://www.opengraph.xyz/
   - Real-time preview across platforms
   - Validates meta tags
   - Shows how image appears in feeds

2. **LinkedIn Post Inspector**: https://www.linkedin.com/post-inspector/
   - LinkedIn-specific preview
   - Shows cache status
   - Force refresh cache

3. **Facebook Sharing Debugger**: https://developers.facebook.com/tools/debug/
   - Facebook preview
   - Cache clearing
   - Shows detected meta tags

4. **Twitter Card Validator**: https://cards-dev.twitter.com/validator
   - Twitter-specific preview
   - Requires login

### Testing Checklist

- [ ] Image appears correctly on all platforms
- [ ] Text is readable when scaled down
- [ ] No important content is cut off
- [ ] File size is reasonable (<200KB)
- [ ] All meta tags are present
- [ ] Absolute URLs are used
- [ ] Image serves over HTTPS

## Platform-Specific Quirks

### Facebook
- Caches aggressively (use debugger to force refresh)
- Minimum 200x200px
- Prefers 1200x630px
- Max 8MB

### Twitter/X
- Requires `twitter:card` set to `summary_large_image`
- Falls back to OG tags if Twitter tags missing
- Minimum 300x157px
- Prefers 1200x675px (but 1200x630 works fine)
- Max 5MB

### LinkedIn
- Prefers 1200x627px (but 1200x630 works fine)
- Minimum 1200x628px (strictly enforced)
- Max 5MB
- Caches for ~7 days

### Slack
- Uses OG tags
- Shows preview automatically for links
- Respects 1200x630px standard

### Discord
- Uses OG tags
- Embeds automatically
- Supports 1200x630px

## Common Issues

### Image Not Showing

**Causes**:
1. Using relative URL instead of absolute
2. Image not accessible (404, auth required)
3. No HTTPS (some platforms require it)
4. File too large
5. Platform cache (image updated but old version shows)

**Solutions**:
- Use absolute URLs: `https://example.com/og-image.png`
- Verify image is publicly accessible
- Ensure HTTPS
- Compress image (<200KB)
- Clear platform cache using debug tools

### Wrong Image Showing

**Cause**: Platform cached old image

**Solution**: Use platform-specific cache clearing tools

### Image Cut Off

**Cause**: Content too close to edges

**Solution**: Use safe zone padding (60px top/bottom, 80px left/right)

## Dynamic vs Static

### Static Images (Recommended for Brand Consistency)
- Pre-generated for each route
- Full design control
- Faster loading
- Consistent brand appearance
- **Use this approach for most sites**

### Dynamic Images (Next.js OG, Vercel OG)
- Generated on-demand
- Good for user-generated content
- Less design control
- Can look generic if not carefully designed
- **Use for dynamic content (user profiles, articles, etc.)**

For brand consistency, static images generated from your actual components and brand assets are preferred.
