# Complete Meta Tags Reference

Comprehensive guide to all meta tags for SEO, social sharing, and browser behavior.

## Essential Meta Tags

### Document Character Set
```html
<meta charset="utf-8">
```
Always first in `<head>`. UTF-8 supports all languages.

### Viewport
```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```
Required for mobile responsiveness. Never use `user-scalable=no` (accessibility issue).

### Title
```html
<title>Primary Keyword - Secondary | Brand Name</title>
```
- 50-60 characters optimal
- Front-load keywords
- Include brand (usually at end)
- Unique per page

### Description
```html
<meta name="description" content="Compelling description with primary keyword. Explain value and include call-to-action. 150-160 characters.">
```
- 150-160 characters
- Include target keyword naturally
- Compelling call-to-action
- Unique per page

### Canonical URL
```html
<link rel="canonical" href="https://example.com/page/">
```
- Always absolute URL
- Choose one version (www vs non-www, trailing slash)
- Self-referencing is fine
- Prevents duplicate content issues

---

## Robots Meta Tags

### Basic Indexing Control
```html
<!-- Default: index and follow all links -->
<meta name="robots" content="index, follow">

<!-- Don't index but follow links -->
<meta name="robots" content="noindex, follow">

<!-- Index but don't follow links -->
<meta name="robots" content="index, nofollow">

<!-- Don't index, don't follow -->
<meta name="robots" content="noindex, nofollow">
```

### Advanced Directives
```html
<!-- Prevent snippet in search results -->
<meta name="robots" content="nosnippet">

<!-- Prevent image indexing -->
<meta name="robots" content="noimageindex">

<!-- Limit snippet length -->
<meta name="robots" content="max-snippet:150">

<!-- Prevent page caching -->
<meta name="robots" content="noarchive">

<!-- Prevent translation offering -->
<meta name="robots" content="notranslate">

<!-- Combined directives -->
<meta name="robots" content="index, follow, max-snippet:150, max-image-preview:large">
```

### Bot-Specific Directives
```html
<!-- Google-specific -->
<meta name="googlebot" content="index, follow">

<!-- Bing-specific -->
<meta name="bingbot" content="index, follow">
```

---

## Open Graph Tags (Facebook, LinkedIn, Slack, Discord)

### Required Tags
```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://example.com/page/">
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Page description for social sharing.">
<meta property="og:image" content="https://example.com/og-image.png">
```

### Recommended Tags
```html
<meta property="og:site_name" content="Site Name">
<meta property="og:locale" content="en_US">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Description of image">
```

### Article-Specific Tags
```html
<meta property="og:type" content="article">
<meta property="article:published_time" content="2024-01-15T08:00:00Z">
<meta property="article:modified_time" content="2024-01-16T10:30:00Z">
<meta property="article:author" content="https://example.com/authors/name">
<meta property="article:section" content="Technology">
<meta property="article:tag" content="JavaScript">
<meta property="article:tag" content="React">
```

### Product Tags
```html
<meta property="og:type" content="product">
<meta property="product:price:amount" content="29.99">
<meta property="product:price:currency" content="USD">
<meta property="product:availability" content="in stock">
```

### Image Requirements
- **Dimensions**: 1200 x 630 pixels (1.91:1 ratio)
- **Minimum**: 600 x 315 pixels
- **File size**: < 8MB
- **Formats**: PNG, JPEG, GIF
- **URL**: Absolute, HTTPS preferred

---

## Twitter Card Tags

### Summary Card (Small Image)
```html
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@yourbrand">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Page description (200 chars max)">
<meta name="twitter:image" content="https://example.com/image.png">
```

### Summary Large Image (Recommended)
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@yourbrand">
<meta name="twitter:creator" content="@authorhandle">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Page description">
<meta name="twitter:image" content="https://example.com/large-image.png">
<meta name="twitter:image:alt" content="Description of image">
```

### Image Requirements
- **summary**: 120 x 120 to 4096 x 4096 (1:1 displayed)
- **summary_large_image**: 300 x 157 to 4096 x 4096 (2:1 displayed)
- **File size**: < 5MB
- **Formats**: PNG, JPEG, GIF, WEBP

---

## Additional SEO Tags

### Language and Region
```html
<!-- Page language -->
<html lang="en">

<!-- Alternate language versions -->
<link rel="alternate" hreflang="en" href="https://example.com/page/">
<link rel="alternate" hreflang="es" href="https://example.com/es/page/">
<link rel="alternate" hreflang="x-default" href="https://example.com/page/">
```

### Pagination
```html
<!-- For paginated content -->
<link rel="prev" href="https://example.com/page/2/">
<link rel="next" href="https://example.com/page/4/">
```
Note: Google no longer uses these for indexing but they help with crawling.

### Author and Publisher
```html
<meta name="author" content="Author Name">
<link rel="author" href="https://example.com/about/author">
<link rel="publisher" href="https://plus.google.com/+YourPage">
```

---

## Browser and PWA Tags

### Favicon Links
```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.json">
```

### Theme Colors
```html
<!-- Browser theme color -->
<meta name="theme-color" content="#4285f4">

<!-- Dark mode support -->
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">

<!-- Safari/Apple specific -->
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

### App-Like Behavior
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="App Name">
<meta name="mobile-web-app-capable" content="yes">
<meta name="application-name" content="App Name">
```

---

## Security Tags

### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src https:; script-src 'self' 'unsafe-inline'">
```

### Referrer Policy
```html
<meta name="referrer" content="strict-origin-when-cross-origin">
```

Options:
- `no-referrer`: Never send referrer
- `origin`: Send origin only
- `strict-origin-when-cross-origin`: Full URL for same-origin, origin for cross-origin HTTPS, none for HTTP

---

## Complete Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Character encoding -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- SEO essentials -->
  <title>Page Title - Keyword | Brand</title>
  <meta name="description" content="Compelling 150-160 character description with primary keyword and call-to-action.">
  <link rel="canonical" href="https://example.com/page/">
  <meta name="robots" content="index, follow">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://example.com/page/">
  <meta property="og:title" content="Page Title">
  <meta property="og:description" content="Description for social sharing.">
  <meta property="og:image" content="https://example.com/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:site_name" content="Site Name">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@yourbrand">
  <meta name="twitter:title" content="Page Title">
  <meta name="twitter:description" content="Description for Twitter.">
  <meta name="twitter:image" content="https://example.com/twitter-image.png">

  <!-- Favicons -->
  <link rel="icon" href="/favicon.ico" sizes="any">
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
    "description": "Page description"
  }
  </script>
</head>
<body>
  <!-- Content -->
</body>
</html>
```

---

## Validation Tools

- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Facebook Sharing Debugger**: https://developers.facebook.com/tools/debug/
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator
- **LinkedIn Post Inspector**: https://www.linkedin.com/post-inspector/
- **Schema Validator**: https://validator.schema.org/
