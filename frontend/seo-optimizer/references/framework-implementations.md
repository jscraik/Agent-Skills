# Framework-Specific SEO Implementations

Complete implementation guides for popular frameworks.

## Next.js (App Router - v13+)

### Metadata API

The recommended approach for Next.js App Router.

#### Static Metadata

```typescript
// app/page.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Title | Brand',
  description: 'Page description for search engines and social.',
  keywords: ['keyword1', 'keyword2', 'keyword3'],
  authors: [{ name: 'Author Name' }],
  creator: 'Creator Name',
  publisher: 'Publisher Name',

  // Canonical URL
  alternates: {
    canonical: 'https://example.com/page',
    languages: {
      'en-US': 'https://example.com/en-US/page',
      'es-ES': 'https://example.com/es-ES/page',
    },
  },

  // Open Graph
  openGraph: {
    title: 'Page Title',
    description: 'Description for social sharing',
    url: 'https://example.com/page',
    siteName: 'Site Name',
    images: [
      {
        url: 'https://example.com/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Image description',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },

  // Twitter
  twitter: {
    card: 'summary_large_image',
    title: 'Page Title',
    description: 'Description for Twitter',
    site: '@sitehandle',
    creator: '@creatorhandle',
    images: ['https://example.com/twitter-image.png'],
  },

  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },

  // Verification
  verification: {
    google: 'google-site-verification-code',
    yandex: 'yandex-verification-code',
  },
}
```

#### Dynamic Metadata

```typescript
// app/blog/[slug]/page.tsx
import { Metadata } from 'next'

type Props = {
  params: { slug: string }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPost(params.slug)

  return {
    title: `${post.title} | Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author.name],
      images: [post.featuredImage],
    },
  }
}
```

#### Layout Metadata with Template

```typescript
// app/layout.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),
  title: {
    default: 'Site Name',
    template: '%s | Site Name', // Applied to child pages
  },
  description: 'Default site description',
  openGraph: {
    title: {
      default: 'Site Name',
      template: '%s | Site Name',
    },
    siteName: 'Site Name',
  },
}
```

### Structured Data in Next.js

```typescript
// app/page.tsx
export default function Page() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Company Name',
    url: 'https://example.com',
    logo: 'https://example.com/logo.png',
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {/* Page content */}
    </>
  )
}
```

### Sitemap Generation

```typescript
// app/sitemap.ts
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 1,
    },
    {
      url: 'https://example.com/about',
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: 'https://example.com/blog',
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.5,
    },
  ]
}

// Dynamic sitemap with database content
export default async function sitemap(): MetadataRoute.Sitemap {
  const posts = await getPosts()

  const postUrls = posts.map((post) => ({
    url: `https://example.com/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }))

  return [
    { url: 'https://example.com', lastModified: new Date(), priority: 1 },
    ...postUrls,
  ]
}
```

### Robots.txt

```typescript
// app/robots.ts
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/admin/', '/api/', '/private/'],
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

---

## Next.js (Pages Router)

### Using next/head

```tsx
// pages/index.tsx
import Head from 'next/head'

export default function HomePage() {
  return (
    <>
      <Head>
        <title>Page Title | Brand</title>
        <meta name="description" content="Page description" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="canonical" href="https://example.com/" />

        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://example.com/" />
        <meta property="og:title" content="Page Title" />
        <meta property="og:description" content="Page description" />
        <meta property="og:image" content="https://example.com/og-image.png" />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Page Title" />
        <meta name="twitter:description" content="Page description" />
        <meta name="twitter:image" content="https://example.com/twitter-image.png" />
      </Head>

      {/* Page content */}
    </>
  )
}
```

### Reusable SEO Component

```tsx
// components/SEO.tsx
import Head from 'next/head'

interface SEOProps {
  title: string
  description: string
  canonical?: string
  ogImage?: string
  ogType?: string
  noindex?: boolean
}

export function SEO({
  title,
  description,
  canonical,
  ogImage = '/default-og.png',
  ogType = 'website',
  noindex = false,
}: SEOProps) {
  const fullTitle = `${title} | Brand`
  const siteUrl = 'https://example.com'
  const canonicalUrl = canonical ? `${siteUrl}${canonical}` : undefined
  const imageUrl = ogImage.startsWith('http') ? ogImage : `${siteUrl}${ogImage}`

  return (
    <Head>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}
      {noindex && <meta name="robots" content="noindex, nofollow" />}

      <meta property="og:type" content={ogType} />
      {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={imageUrl} />
      <meta property="og:site_name" content="Brand" />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={imageUrl} />
    </Head>
  )
}
```

---

## Astro

### Layout with SEO Props

```astro
---
// src/layouts/Layout.astro
interface Props {
  title: string;
  description: string;
  canonical?: string;
  ogImage?: string;
  ogType?: string;
  article?: {
    publishedTime: string;
    modifiedTime?: string;
    author?: string;
    tags?: string[];
  };
}

const {
  title,
  description,
  canonical = Astro.url.href,
  ogImage = '/og-default.png',
  ogType = 'website',
  article,
} = Astro.props;

const siteUrl = import.meta.env.SITE || 'https://example.com';
const fullImageUrl = ogImage.startsWith('http') ? ogImage : `${siteUrl}${ogImage}`;
---

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />

  <title>{title} | Brand</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={canonical} />

  <!-- Open Graph -->
  <meta property="og:type" content={ogType} />
  <meta property="og:url" content={canonical} />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:image" content={fullImageUrl} />
  <meta property="og:site_name" content="Brand" />

  {article && (
    <>
      <meta property="article:published_time" content={article.publishedTime} />
      {article.modifiedTime && (
        <meta property="article:modified_time" content={article.modifiedTime} />
      )}
      {article.author && (
        <meta property="article:author" content={article.author} />
      )}
      {article.tags?.map((tag) => (
        <meta property="article:tag" content={tag} />
      ))}
    </>
  )}

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={title} />
  <meta name="twitter:description" content={description} />
  <meta name="twitter:image" content={fullImageUrl} />

  <!-- Favicons -->
  <link rel="icon" href="/favicon.ico" />
  <link rel="icon" href="/icon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

  <slot name="head" />
</head>
<body>
  <slot />
</body>
</html>
```

### Using the Layout

```astro
---
// src/pages/index.astro
import Layout from '../layouts/Layout.astro';
---

<Layout
  title="Home"
  description="Welcome to our site. We help you do amazing things."
  ogImage="/og-home.png"
>
  <main>
    <h1>Welcome</h1>
  </main>
</Layout>
```

### Astro Sitemap Integration

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin/'),
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
    }),
  ],
});
```

### Structured Data Component

```astro
---
// src/components/JsonLd.astro
interface Props {
  data: Record<string, any>;
}

const { data } = Astro.props;
const jsonLd = {
  '@context': 'https://schema.org',
  ...data,
};
---

<script type="application/ld+json" set:html={JSON.stringify(jsonLd)} />
```

```astro
---
// Usage in page
import JsonLd from '../components/JsonLd.astro';
---

<JsonLd data={{
  '@type': 'Organization',
  name: 'Company Name',
  url: 'https://example.com',
}} />
```

---

## React (with react-helmet-async)

### Setup

```tsx
// src/main.tsx
import { HelmetProvider } from 'react-helmet-async';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <HelmetProvider>
    <App />
  </HelmetProvider>
);
```

### SEO Component

```tsx
// src/components/SEO.tsx
import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title: string;
  description: string;
  canonical?: string;
  ogImage?: string;
  ogType?: string;
  noindex?: boolean;
}

export function SEO({
  title,
  description,
  canonical,
  ogImage = '/og-default.png',
  ogType = 'website',
  noindex = false,
}: SEOProps) {
  const siteUrl = import.meta.env.VITE_SITE_URL || 'https://example.com';
  const fullTitle = `${title} | Brand`;
  const canonicalUrl = canonical ? `${siteUrl}${canonical}` : undefined;
  const imageUrl = ogImage.startsWith('http') ? ogImage : `${siteUrl}${ogImage}`;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}
      {noindex && <meta name="robots" content="noindex, nofollow" />}

      <meta property="og:type" content={ogType} />
      {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={imageUrl} />
      <meta property="og:site_name" content="Brand" />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={imageUrl} />
    </Helmet>
  );
}
```

### Usage

```tsx
// src/pages/Home.tsx
import { SEO } from '../components/SEO';

export function HomePage() {
  return (
    <>
      <SEO
        title="Home"
        description="Welcome to our site."
        canonical="/"
        ogImage="/og-home.png"
      />
      <main>
        <h1>Welcome</h1>
      </main>
    </>
  );
}
```

---

## Gatsby

### gatsby-plugin-react-helmet

```javascript
// gatsby-config.js
module.exports = {
  siteMetadata: {
    title: 'Site Name',
    description: 'Site description',
    siteUrl: 'https://example.com',
    author: '@twitterhandle',
  },
  plugins: [
    'gatsby-plugin-react-helmet',
    'gatsby-plugin-sitemap',
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        host: 'https://example.com',
        sitemap: 'https://example.com/sitemap.xml',
        policy: [{ userAgent: '*', allow: '/' }],
      },
    },
  ],
};
```

### SEO Component for Gatsby

```tsx
// src/components/SEO.tsx
import { useStaticQuery, graphql } from 'gatsby';
import { Helmet } from 'react-helmet';

interface SEOProps {
  title: string;
  description?: string;
  pathname?: string;
  image?: string;
  article?: boolean;
}

export function SEO({ title, description, pathname, image, article = false }: SEOProps) {
  const { site } = useStaticQuery(graphql`
    query {
      site {
        siteMetadata {
          title
          description
          siteUrl
          author
        }
      }
    }
  `);

  const { siteUrl, defaultDescription, author } = site.siteMetadata;
  const seo = {
    title,
    description: description || defaultDescription,
    url: `${siteUrl}${pathname || ''}`,
    image: image ? `${siteUrl}${image}` : `${siteUrl}/og-default.png`,
  };

  return (
    <Helmet>
      <title>{`${seo.title} | ${site.siteMetadata.title}`}</title>
      <meta name="description" content={seo.description} />
      <link rel="canonical" href={seo.url} />

      <meta property="og:type" content={article ? 'article' : 'website'} />
      <meta property="og:url" content={seo.url} />
      <meta property="og:title" content={seo.title} />
      <meta property="og:description" content={seo.description} />
      <meta property="og:image" content={seo.image} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content={author} />
      <meta name="twitter:title" content={seo.title} />
      <meta name="twitter:description" content={seo.description} />
      <meta name="twitter:image" content={seo.image} />
    </Helmet>
  );
}
```

---

## Static HTML

### Template File

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- SEO Essentials -->
  <title>Page Title | Brand</title>
  <meta name="description" content="Page description here.">
  <link rel="canonical" href="https://example.com/page/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://example.com/page/">
  <meta property="og:title" content="Page Title">
  <meta property="og:description" content="Description for social sharing.">
  <meta property="og:image" content="https://example.com/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="Brand">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@brand">
  <meta name="twitter:title" content="Page Title">
  <meta name="twitter:description" content="Description for Twitter.">
  <meta name="twitter:image" content="https://example.com/twitter-image.png">

  <!-- Favicons -->
  <link rel="icon" href="/favicon.ico">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  <!-- Theme -->
  <meta name="theme-color" content="#4285f4">

  <!-- Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Page Title",
    "description": "Page description",
    "url": "https://example.com/page/"
  }
  </script>
</head>
<body>
  <!-- Content -->
</body>
</html>
```

### sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/about/</loc>
    <lastmod>2024-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://example.com/contact/</loc>
    <lastmod>2024-01-05</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>
```

### robots.txt

```txt
User-agent: *
Allow: /

Disallow: /admin/
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
```
