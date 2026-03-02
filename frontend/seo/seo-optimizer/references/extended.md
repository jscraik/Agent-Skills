# Extended guidance

## Anti-Patterns to Avoid

❌ **Keyword Stuffing**
```html
<!-- BAD -->
<title>Best Shoes | Buy Shoes | Cheap Shoes | Shoes Online | Shoe Store</title>

<!-- GOOD -->
<title>Running Shoes for Marathon Training | SportShop</title>
```
Why bad: Search engines penalize unnatural keyword repetition. Users don't click spammy titles.

❌ **Duplicate Descriptions**
Using the same meta description across multiple pages.
Why bad: Misses opportunity for page-specific relevance. Google may ignore and auto-generate.

❌ **Description/Content Mismatch**
Writing descriptions for keywords rather than actual content.
Why bad: High bounce rates signal low quality. Users feel deceived.

❌ **Missing Alt Text**
```html
<!-- BAD -->
<img src="product.jpg">

<!-- GOOD -->
<img src="product.jpg" alt="Blue Nike Air Max running shoe, side view">
```
Why bad: Accessibility violation. Missed image search opportunity.

❌ **Blocking Crawlers Unintentionally**
```txt
# Accidentally blocking everything
User-agent: *
Disallow: /
```
Why bad: Complete deindexing. Check robots.txt carefully.

❌ **Ignoring Mobile**
Not having responsive design or small-screen considerations.
Why bad: most traffic is small-screen and responsive issues hurt rankings.

❌ **Over-Optimization**
Adding structured data for content that doesn't exist.
Why bad: Schema violations can result in penalties. Trust erosion.

❌ **Generic Auto-Generated Content**
```html
<!-- BAD: Template without customization -->
<meta name="description" content="Welcome to our website. We offer great products and services.">
```
Why bad: Provides no value. Won't rank. Won't get clicks.

---

## Variation Guidance

**IMPORTANT**: SEO implementation should vary based on context.

**Vary based on**:
- **Industry**: E-commerce needs Product schema; SaaS needs Software schema
- **Content type**: Blog posts vs landing pages vs documentation
- **Audience**: B2B vs B2C affects tone and keywords
- **Competition**: Highly competitive niches need more sophisticated optimization
- **Framework**: Use native patterns (Next.js metadata API vs manual tags)

**Avoid converging on**:
- Same title format for all page types
- Generic descriptions that could apply to any site
- Identical structured data without page-specific content
- One-size-fits-all sitemap configuration

---

## Framework Quick Reference

See `references/framework-implementations.md` for Next.js (App Router + Pages Router) and Astro examples.

---

## Scripts
- `python scripts/analyze_seo.py <path-to-project>` — SEO audit (state, gaps, recommendations, structured data opportunities).
- `python scripts/generate_sitemap.py <path-to-project> --domain https://example.com` — generate sitemap.xml.

---

## Examples
1) "Audit my Astro docs site and propose SEO fixes (titles, descriptions, sitemap)."
2) "Add JSON-LD for product pages in Next.js App Router with a reusable helper."

## Remember

**SEO is semantic communication, not algorithm manipulation.**

The best SEO:
- Accurately describes what content IS
- Helps machines understand meaning through structured data
- Prioritizes user value over keyword optimization
- Uses framework-native patterns
- Implements progressively based on page importance

Focus on making your content findable and understandable. The rankings follow from genuine value clearly communicated.

**Claude is capable of comprehensive SEO analysis and implementation. These guidelines illuminate the path—they don't fence it.**

---

## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `scripts/analyze_seo.py`
- `scripts/generate_sitemap.py`

---

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `scripts/analyze_seo.py`
- `scripts/generate_sitemap.py`
