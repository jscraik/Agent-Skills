---
name: seo-optimizer
description: Transform your web application from invisible to discoverable. This skill
  analyzes your codebase and implements comprehensive SEO optimizations that help
  search engines and social platforms understand, index, and surface your content..
  Use when Use this skill when the task matches its description and triggers..
metadata:
  short-description: Transform your web application from invisible to discoverable.
    This skill ana...
---

# SEO Optimizer
Avoid skipping validation steps or inventing results.

Transform your web application from invisible to discoverable. This skill analyzes your codebase and implements comprehensive SEO optimizations that help search engines and social platforms understand, index, and surface your content.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

- `## Outputs`

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## Scope and triggers
- This skill applies to SEO audits and optimization tasks. The current request is out of scope.

## Deliverables
- None (out of scope).

## Required inputs
- None (out of scope).
```

## Philosophy: SEO as Semantic Communication

SEO is not about gaming algorithms—it's about **clearly communicating what your content IS** to machines (search engines, social platforms, AI crawlers) so they can properly understand and surface it.

**Before optimizing, ask**:
- What is this page actually about? (not what keywords we want to rank for)
- Who is the intended audience and what are they searching for?
- What unique value does this content provide?
- How should machines categorize and understand this content?

**Core Principles**:

1. **Accuracy Over Optimization**: Describe what IS, not what you wish would rank
2. **User Intent First**: Match content to what searchers actually want
3. **Semantic Clarity**: Use structured data to make meaning machine-readable
4. **Progressive Enhancement**: Basic SEO for all pages, rich optimization for key pages
5. **Framework-Native**: Use each framework's idioms, not generic hacks

**The SEO Hierarchy** (prioritize in order):
```
1. Content Quality      ← Foundation: Valuable, accurate, unique content
2. Technical Access     ← Can crawlers find and index your pages?
3. Semantic Structure   ← Do machines understand your content's meaning?
4. Meta Optimization    ← Are your titles/descriptions compelling?
5. Structured Data      ← JSON-LD for rich search results
6. Performance          ← Core Web Vitals affect rankings
```

---

## Codebase Analysis Workflow

**ALWAYS analyze before implementing.** Different codebases need different approaches.

### Step 1: Discover Framework and Structure

Identify the framework and routing pattern:
- **Next.js**: Look for `next.config.js`, `app/` or `pages/` directory
- **Astro**: Look for `astro.config.mjs`, `src/pages/`
- **React Router**: Look for route configuration, `react-router-dom`
- **Gatsby**: Look for `gatsby-config.js`, `gatsby-node.js`
- **Static HTML**: Look for `.html` files in root or `public/`

### Step 2: Audit Current SEO State

Check for existing implementations:
- [ ] Meta tags in `<head>` (title, description, viewport)
- [ ] Open Graph tags (`og:title`, `og:image`, etc.)
- [ ] Twitter Card tags (`twitter:card`, `twitter:image`)
- [ ] Structured data (`<script type="application/ld+json">`)
- [ ] Sitemap (`sitemap.xml` or generation config)
- [ ] Robots.txt file
- [ ] Canonical URLs
- [ ] Alt text on images
- [ ] Metadata correctness gate (duplicates, canonical/og alignment, deterministic values). See `references/metadata-correctness-gate.md`.

### Step 3: Identify Page Types

Different pages need different SEO approaches:

| Page Type | Priority | Key Optimizations |
|-----------|----------|-------------------|
| Landing/Home | Critical | Brand keywords, comprehensive structured data |
| Product/Service | High | Product schema, reviews, pricing |
| Blog/Article | High | Article schema, author, publish date |
| Documentation | Medium | HowTo/FAQ schema, breadcrumbs |
| About/Contact | Medium | Organization schema, local business |
| Legal/Privacy | Low | Basic meta only, often noindex |

### Step 4: Generate Implementation Plan

Based on analysis, prioritize:
1. **Quick wins**: Missing meta tags, viewport, basic structure
2. **High impact**: Structured data for key pages, sitemap
3. **Refinement**: Performance, advanced schema, social optimization

See `references/analysis-checklist.md` for detailed audit procedures.

---

## Meta Tags Implementation

### Essential Meta Tags (Every Page)

```html
<!-- Required -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{Page Title} | {Site Name}</title>
<meta name="description" content="{150-160 char description}">

<!-- Recommended -->
<link rel="canonical" href="{full canonical URL}">
<meta name="robots" content="index, follow">
```

### Title Tag Best Practices

**Format**: `{Primary Content} | {Brand}` or `{Primary Content} - {Brand}`

**Guidelines**:
- 50-60 characters (Google truncates at ~60)
- Front-load important keywords
- Unique for every page
- Accurately describe page content
- Include brand for recognition (usually at end)

See `references/meta-tags-complete.md` for full title patterns by page type.

### Meta Description Best Practices

**Guidelines**:
- 150-160 characters (Google may truncate at ~155)
- Include a call to action when appropriate
- Accurately summarize page content
- Unique for every page
- Include primary keyword naturally

See `references/meta-tags-complete.md` for full do/don't guidance.

### Open Graph Tags (Social Sharing)

```html
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical URL}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{1200x630 image URL}">
<meta property="og:site_name" content="{Site Name}">
```

### Twitter Card Tags

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@{handle}">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image URL}">
```

See `references/meta-tags-complete.md` for comprehensive tag reference.

---

## Structured Data (JSON-LD)

Structured data enables rich search results (star ratings, prices, FAQs, etc.).

### When to Use Which Schema

| Content Type | Schema | Rich Result |
|--------------|--------|-------------|
| Organization info | Organization | Knowledge panel |
| Products | Product | Price, availability, reviews |
| Articles/Blog | Article | Headline, image, date |
| How-to guides | HowTo | Step-by-step in search |
| FAQs | FAQPage | Expandable Q&A |
| Events | Event | Date, location, tickets |
| Recipes | Recipe | Image, time, ratings |
| Local business | LocalBusiness | Maps, hours, contact |
| Breadcrumbs | BreadcrumbList | Navigation path |

### Implementation Pattern

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/company",
    "https://linkedin.com/company/company"
  ]
}
</script>
```

### Multiple Schemas Per Page

Use `@graph` to combine schemas:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", ... },
    { "@type": "WebSite", ... },
    { "@type": "BreadcrumbList", ... }
  ]
}
```

See `references/structured-data-schemas.md` for complete schema examples.

---

## Technical SEO

### Sitemap Generation

**XML Sitemap Requirements**:
- Include all indexable pages
- Exclude noindex pages, redirects, error pages
- Update `<lastmod>` when content changes
- Submit to Google Search Console

**Framework implementations**: See `references/framework-implementations.md`

### Robots.txt

**Standard Template**:
```txt
User-agent: *
Allow: /

# Block admin/private areas
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Point to sitemap
Sitemap: https://yourdomain.com/sitemap.xml
```

### Canonical URLs

**Always set canonical URLs to**:
- Prevent duplicate content issues
- Consolidate link equity
- Specify preferred URL version

**Handle**:
- www vs non-www
- http vs https
- Trailing slashes
- Query parameters

### Performance (Core Web Vitals)
Core Web Vitals affect rankings. Monitor:
| Metric | Target | What It Measures |
|--------|--------|------------------|
| LCP | < 2.5s | Largest Contentful Paint (loading) |
| INP | < 200ms | Interaction to Next Paint (interactivity) |
| CLS | < 0.1 | Cumulative Layout Shift (visual stability) |
**Quick wins**:
- Optimize images (WebP, lazy loading, proper sizing)
- Minimize JavaScript bundles
- Use efficient fonts (display: swap)
- Implement proper caching
---
## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.
## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
## Scripts
- `scripts/analyze_seo.py`
- `scripts/generate_sitemap.py`
## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.
