# SEO Analysis Checklist

Comprehensive checklist for auditing web application SEO. Use this to systematically evaluate and improve SEO.

## Quick Assessment (5 minutes)

### Homepage Check
- [ ] Title tag present and under 60 characters
- [ ] Meta description present and 150-160 characters
- [ ] Viewport meta tag present
- [ ] H1 tag present (only one per page)
- [ ] Open Graph image visible when sharing

### Technical Basics
- [ ] Site loads over HTTPS
- [ ] robots.txt exists and accessible
- [ ] sitemap.xml exists and accessible
- [ ] No console errors on load
- [ ] Mobile responsive

---

## Complete Audit

### 1. Crawlability & Indexing

#### robots.txt Analysis
```
Check: /robots.txt
```
- [ ] File exists and is accessible
- [ ] Not blocking important pages accidentally
- [ ] Sitemap URL is specified
- [ ] No syntax errors
- [ ] Development/staging pages blocked

**Common issues**:
- Blocking CSS/JS files (hurts rendering)
- Blocking entire site (`Disallow: /`)
- Missing sitemap reference

#### XML Sitemap
```
Check: /sitemap.xml or /sitemap-index.xml
```
- [ ] Sitemap exists and parses correctly
- [ ] All important pages included
- [ ] No noindex pages in sitemap
- [ ] No 404 or redirect URLs
- [ ] lastmod dates are accurate
- [ ] Sitemap size < 50MB, < 50,000 URLs

#### Indexing Status
- [ ] Check Google Search Console coverage
- [ ] Review "Excluded" pages
- [ ] Identify crawl errors
- [ ] Check for duplicate content issues

---

### 2. Page-Level Meta Tags

#### For Each Important Page

**Title Tag**
- [ ] Present in `<head>`
- [ ] 50-60 characters
- [ ] Contains primary keyword
- [ ] Unique across site
- [ ] Includes brand name
- [ ] No truncation in search results

**Meta Description**
- [ ] Present in `<head>`
- [ ] 150-160 characters
- [ ] Compelling call-to-action
- [ ] Contains primary keyword
- [ ] Unique across site
- [ ] Accurately describes page content

**Canonical URL**
- [ ] Present on every page
- [ ] Absolute URL (not relative)
- [ ] Self-referencing on unique pages
- [ ] Consistent trailing slash usage
- [ ] HTTPS version specified

**Robots Meta**
- [ ] Present if needed (index/noindex)
- [ ] No conflicting directives
- [ ] noindex on thin/duplicate content

---

### 3. Open Graph & Social

#### Open Graph Tags
- [ ] `og:type` present
- [ ] `og:url` matches canonical
- [ ] `og:title` present (can differ from title)
- [ ] `og:description` present
- [ ] `og:image` present
- [ ] `og:image` is 1200x630 pixels
- [ ] `og:site_name` present

#### Twitter Cards
- [ ] `twitter:card` present
- [ ] `twitter:title` present
- [ ] `twitter:description` present
- [ ] `twitter:image` present
- [ ] Image meets minimum requirements

#### Testing
- [ ] Facebook Sharing Debugger passes
- [ ] Twitter Card Validator passes
- [ ] LinkedIn Post Inspector passes

---

### 4. Structured Data

#### Organization/WebSite Schema
- [ ] Present on homepage
- [ ] Valid JSON-LD format
- [ ] Accurate business information
- [ ] Logo URL accessible
- [ ] Social profiles linked (sameAs)

#### Page-Specific Schema
- [ ] Article schema on blog posts
- [ ] Product schema on product pages
- [ ] FAQPage schema where applicable
- [ ] BreadcrumbList on hierarchical pages
- [ ] LocalBusiness for physical locations

#### Validation
- [ ] Google Rich Results Test passes
- [ ] Schema.org validator passes
- [ ] No warnings or errors
- [ ] Required properties present

---

### 5. Content & Semantic Structure

#### Heading Hierarchy
- [ ] Single H1 per page
- [ ] H1 contains primary keyword
- [ ] Logical heading order (H1 → H2 → H3)
- [ ] No skipped heading levels
- [ ] Headings describe content sections

#### Images
- [ ] All images have alt text
- [ ] Alt text is descriptive (not keyword-stuffed)
- [ ] Decorative images have empty alt=""
- [ ] Image filenames are descriptive
- [ ] Images are optimized (WebP, compressed)
- [ ] Lazy loading on below-fold images

#### Links
- [ ] Internal links use descriptive anchor text
- [ ] No broken internal links
- [ ] External links to authoritative sources
- [ ] Outbound links use rel="noopener" when needed
- [ ] Sponsored/affiliate links use rel="sponsored"

---

### 6. Technical Performance

#### Core Web Vitals
- [ ] LCP < 2.5 seconds
- [ ] INP < 200 milliseconds
- [ ] CLS < 0.1

#### Page Speed
- [ ] Time to First Byte < 600ms
- [ ] First Contentful Paint < 1.8s
- [ ] Total page weight < 3MB
- [ ] JavaScript bundle size reasonable

#### Mobile
- [ ] Mobile-responsive design
- [ ] Text readable without zooming
- [ ] Tap targets adequately sized (48x48 CSS pixels)
- [ ] No horizontal scrolling
- [ ] Content same on mobile and desktop

---

### 7. URL Structure

#### URL Best Practices
- [ ] URLs are descriptive and readable
- [ ] Lowercase URLs only
- [ ] Hyphens for word separation (not underscores)
- [ ] No special characters or encoding
- [ ] Reasonable length (< 100 characters)
- [ ] Consistent trailing slash policy

#### Redirects
- [ ] www/non-www redirects properly
- [ ] HTTP → HTTPS redirects work
- [ ] No redirect chains (max 1 hop)
- [ ] Old URLs redirect to new locations
- [ ] 301 for permanent, 302 for temporary

---

### 8. International SEO (if applicable)

- [ ] hreflang tags for language variants
- [ ] x-default for default language
- [ ] Bidirectional hreflang links
- [ ] Consistent language/region targeting
- [ ] Content genuinely localized

---

## Framework-Specific Checks

### Next.js
- [ ] Using Metadata API (App Router) or next/head (Pages)
- [ ] generateMetadata for dynamic pages
- [ ] sitemap.ts or sitemap.xml present
- [ ] robots.ts or robots.txt present
- [ ] next-sitemap or built-in sitemap configured

### Astro
- [ ] SEO props passed to Layout
- [ ] @astrojs/sitemap integration
- [ ] Static build optimizations enabled
- [ ] Proper use of client directives

### React SPA
- [ ] Server-side rendering or pre-rendering
- [ ] react-helmet-async configured
- [ ] Pre-rendering for SEO-critical pages
- [ ] Dynamic routes pre-rendered

---

## Priority Matrix

### Critical (Fix Immediately)
- Missing title tags
- Blocking crawlers accidentally
- Broken canonical tags
- noindex on important pages
- Site-wide HTTPS issues

### High (Fix This Week)
- Missing meta descriptions
- Missing Open Graph tags
- No structured data on key pages
- Missing sitemap
- Core Web Vitals failing

### Medium (Plan for Next Sprint)
- Image alt text gaps
- Heading structure issues
- Internal linking improvements
- URL structure cleanup
- Schema expansion

### Low (Ongoing Optimization)
- Title/description refinement
- Additional schema types
- A/B testing meta tags
- Content expansion
- Link building

---

## Audit Report Template

```markdown
# SEO Audit Report: [Site Name]
Date: [Date]
Auditor: Claude

## Executive Summary
[2-3 sentences on overall SEO health]

## Score: [X]/100

### Category Breakdown
- Crawlability: [X]/20
- Meta Tags: [X]/20
- Structured Data: [X]/20
- Content Quality: [X]/20
- Technical Performance: [X]/20

## Critical Issues
1. [Issue]: [Impact and recommendation]
2. [Issue]: [Impact and recommendation]

## High Priority Recommendations
1. [Recommendation]
2. [Recommendation]

## Quick Wins
1. [Easy fix with high impact]
2. [Easy fix with high impact]

## Page-by-Page Analysis
[Detailed findings per page]

## Next Steps
1. [Action item with priority]
2. [Action item with priority]
```

---

## Tools for Testing

### Free Tools
- **Google Search Console**: Index coverage, performance
- **Google PageSpeed Insights**: Core Web Vitals
- **Google Rich Results Test**: Structured data
- **Facebook Sharing Debugger**: OG tags
- **Twitter Card Validator**: Twitter cards

### Browser Extensions
- **Lighthouse**: Chrome DevTools
- **SEO Meta in 1 Click**: Quick meta overview
- **Detailed SEO Extension**: Comprehensive analysis

### Command Line
```bash
# Check robots.txt
curl -I https://example.com/robots.txt

# Check sitemap
curl -s https://example.com/sitemap.xml | head -50

# Check headers
curl -I https://example.com
```
