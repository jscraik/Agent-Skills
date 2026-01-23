# Framework-Specific Workflows

## Next.js

### App Router (Next.js 13+)

**Route detection**:
- Pages: `app/**/page.{tsx,ts,jsx,js}`
- Route groups: Ignore `(group)` folders
- Root: `app/page.tsx` → `/`

**OG image integration**:

```tsx
// app/page.tsx
export const metadata = {
  title: 'Home',
  description: 'Welcome to our site',
  openGraph: {
    title: 'Home',
    description: 'Welcome to our site',
    images: ['/og/home.png'],
    url: 'https://example.com',
    siteName: 'Example Site',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Home',
    description: 'Welcome to our site',
    images: ['/og/home.png'],
  },
}
```

**Dynamic routes**:

For dynamic routes like `app/blog/[slug]/page.tsx`:
- Generate OG image per slug if limited number
- Or use Next.js Image Generation API for dynamic content

**Next.js OG Image Generation** (alternative for dynamic content):

```tsx
// app/api/og/route.tsx
import { ImageResponse } from 'next/og'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const title = searchParams.get('title')

  return new ImageResponse(
    (
      <div style={{ /* ... */ }}>
        {title}
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

**When to use static vs dynamic**:
- Static: Known routes, brand consistency desired
- Dynamic: User-generated content, many routes

### Pages Router (Next.js 12 and earlier)

**Route detection**:
- Pages: `pages/**/*.{tsx,ts,jsx,js}`
- Ignore: `pages/_app.tsx`, `pages/_document.tsx`, `pages/api/**`
- Index: `pages/index.tsx` → `/`

**OG image integration**:

```tsx
// pages/index.tsx
import Head from 'next/head'

export default function Home() {
  return (
    <>
      <Head>
        <title>Home</title>
        <meta property="og:title" content="Home" />
        <meta property="og:description" content="Welcome to our site" />
        <meta property="og:image" content="https://example.com/og/home.png" />
        <meta property="og:url" content="https://example.com" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:image" content="https://example.com/og/home.png" />
      </Head>
      {/* Page content */}
    </>
  )
}
```

**Using next-seo**:

```tsx
import { NextSeo } from 'next-seo'

export default function Home() {
  return (
    <>
      <NextSeo
        title="Home"
        description="Welcome to our site"
        openGraph={{
          url: 'https://example.com',
          title: 'Home',
          description: 'Welcome to our site',
          images: [
            {
              url: 'https://example.com/og/home.png',
              width: 1200,
              height: 630,
              alt: 'Home page preview',
            },
          ],
          siteName: 'Example Site',
        }}
        twitter={{
          cardType: 'summary_large_image',
        }}
      />
      {/* Page content */}
    </>
  )
}
```

## Astro

**Route detection**:
- Pages: `src/pages/**/*.{astro,md,mdx}`
- Index: `src/pages/index.astro` → `/`

**OG image integration**:

```astro
---
// src/pages/index.astro
const title = 'Home'
const description = 'Welcome to our site'
const ogImage = new URL('/og/home.png', Astro.site)
---
<html>
  <head>
    <title>{title}</title>
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:image" content={ogImage} />
    <meta property="og:url" content={Astro.url} />
    <meta property="og:type" content="website" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:image" content={ogImage} />
  </head>
  <body>
    <!-- Page content -->
  </body>
</html>
```

**Using layout component**:

```astro
---
// src/layouts/BaseLayout.astro
const { title, description, ogImage = '/og/default.png' } = Astro.props
const ogImageUrl = new URL(ogImage, Astro.site)
---
<html>
  <head>
    <title>{title}</title>
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:image" content={ogImageUrl} />
    <meta property="og:url" content={Astro.url} />
    <meta property="og:type" content="website" />
    <meta name="twitter:card" content="summary_large_image" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**Markdown/MDX pages**:

```mdx
---
# src/pages/blog/post.mdx
title: 'Blog Post Title'
description: 'Post description'
ogImage: '/og/blog-post.png'
---

# Blog Post Title

Content here...
```

## React Router / React SPA

**Route detection**:
- Analyze route configuration in app
- Common patterns:
  - `src/routes.tsx`
  - `src/App.tsx`
  - Route components

**Example route config**:

```tsx
// src/routes.tsx
export const routes = [
  { path: '/', element: <Home /> },
  { path: '/about', element: <About /> },
  { path: '/blog/:slug', element: <BlogPost /> },
]
```

**OG image integration**:

Since SPAs often have a single `index.html`, use React Helmet for per-route meta tags:

```tsx
// src/pages/Home.tsx
import { Helmet } from 'react-helmet-async'

export default function Home() {
  return (
    <>
      <Helmet>
        <title>Home</title>
        <meta property="og:title" content="Home" />
        <meta property="og:description" content="Welcome to our site" />
        <meta property="og:image" content="https://example.com/og/home.png" />
        <meta property="og:url" content="https://example.com" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
      </Helmet>
      {/* Page content */}
    </>
  )
}
```

**Important**: For SPAs, social crawlers often can't execute JavaScript, so:
1. Use SSR/SSG if possible (Next.js, Gatsby, Astro)
2. Or use prerendering service (prerender.io, rendertron)
3. Or server-side redirects for social crawlers

**Static fallback** (public/index.html):

```html
<!-- public/index.html -->
<head>
  <!-- Default OG tags for homepage -->
  <meta property="og:title" content="Example Site" />
  <meta property="og:description" content="Welcome to our site" />
  <meta property="og:image" content="https://example.com/og/home.png" />
  <meta property="og:url" content="https://example.com" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
</head>
```

## Gatsby

**Route detection**:
- Pages: `src/pages/**/*.{jsx,js,tsx,ts}`
- Programmatic routes: Check `gatsby-node.js`

**OG image integration**:

Using React Helmet:

```tsx
// src/pages/index.tsx
import { Helmet } from 'react-helmet'

export default function Home() {
  return (
    <>
      <Helmet>
        <title>Home</title>
        <meta property="og:title" content="Home" />
        <meta property="og:description" content="Welcome to our site" />
        <meta property="og:image" content="https://example.com/og/home.png" />
        <meta property="og:url" content="https://example.com" />
        <meta property="og:type" content="website" />
      </Helmet>
      {/* Page content */}
    </>
  )
}
```

Using gatsby-plugin-react-helmet:

```js
// gatsby-config.js
module.exports = {
  plugins: ['gatsby-plugin-react-helmet'],
}
```

**SEO component pattern**:

```tsx
// src/components/SEO.tsx
import { Helmet } from 'react-helmet'

interface SEOProps {
  title: string
  description: string
  ogImage?: string
  url?: string
}

export default function SEO({ title, description, ogImage = '/og/default.png', url }: SEOProps) {
  const siteUrl = 'https://example.com'
  const ogImageUrl = `${siteUrl}${ogImage}`
  const pageUrl = url ? `${siteUrl}${url}` : siteUrl

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImageUrl} />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:type" content="website" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:image" content={ogImageUrl} />
    </Helmet>
  )
}
```

## Static HTML Sites

**Route detection**:
- HTML files in root or structured directories
- Common patterns:
  - `index.html` → `/`
  - `about.html` → `/about`
  - `blog/post.html` → `/blog/post`

**OG image integration**:

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Home</title>

  <!-- Open Graph -->
  <meta property="og:title" content="Home">
  <meta property="og:description" content="Welcome to our site">
  <meta property="og:image" content="https://example.com/og/home.png">
  <meta property="og:url" content="https://example.com">
  <meta property="og:type" content="website">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://example.com/og/home.png">
</head>
<body>
  <!-- Page content -->
</body>
</html>
```

**Template approach**:

For multiple pages, use a build tool or templating:

```js
// build-meta.js
const fs = require('fs')

const pages = [
  { path: 'index.html', title: 'Home', description: 'Welcome', ogImage: '/og/home.png' },
  { path: 'about.html', title: 'About', description: 'About us', ogImage: '/og/about.png' },
]

pages.forEach(page => {
  let html = fs.readFileSync(`templates/${page.path}`, 'utf8')

  html = html.replace('{{title}}', page.title)
  html = html.replace('{{description}}', page.description)
  html = html.replace('{{ogImage}}', `https://example.com${page.ogImage}`)

  fs.writeFileSync(`dist/${page.path}`, html)
})
```

## Workflow Summary

### 1. Analyze codebase
```bash
python scripts/analyze_codebase.py /path/to/project
```

This creates `og-analysis.json` with:
- Detected framework
- Found routes
- Extracted brand (colors, fonts, logo)

### 2. Review analysis
```bash
cat og-analysis.json
```

Verify:
- All routes were found
- Brand colors/fonts extracted correctly
- Page types categorized appropriately

### 3. Generate OG images
```bash
python scripts/generate_og_images.py /path/to/project
```

This creates images in `public/og/`

### 4. Integrate with framework

Follow framework-specific guidance above to add meta tags.

### 5. Test

Use platform preview tools:
- https://www.opengraph.xyz/
- https://www.linkedin.com/post-inspector/
- Facebook Sharing Debugger

### 6. Deploy

Ensure:
- OG images are in `public/` or static directory
- Images are served over HTTPS
- Absolute URLs used in meta tags
- Images are publicly accessible

## Troubleshooting

### Routes not detected

**Check**:
- Is framework correctly detected?
- Are pages in standard locations?
- Are naming conventions followed?

**Solution**: Manually specify routes in analysis.json

### Brand not extracted

**Check**:
- Do Tailwind/CSS config files exist?
- Are colors defined in standard formats?

**Solution**: Manually add colors to analysis.json

### Images not generated

**Check**:
- Is Playwright installed? (`playwright install chromium`)
- Are Python dependencies installed?
- Any error messages?

**Solution**: Check error logs, install missing deps

### Meta tags not working

**Check**:
- Are absolute URLs used?
- Is site deployed and accessible?
- Are images publicly accessible?

**Solution**: Use platform debug tools to see what they detect
