# Structured Data Schemas Reference

Complete JSON-LD examples for common Schema.org types that enable rich search results.

## Organization Schema

For company/brand information. Appears in knowledge panels.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "legalName": "Company Name Inc.",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png",
    "width": 600,
    "height": 60
  },
  "description": "Brief company description",
  "foundingDate": "2020-01-01",
  "founders": [
    {
      "@type": "Person",
      "name": "Founder Name"
    }
  ],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "San Francisco",
    "addressRegion": "CA",
    "postalCode": "94105",
    "addressCountry": "US"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-555-555-5555",
    "contactType": "customer service",
    "availableLanguage": ["English"]
  },
  "sameAs": [
    "https://twitter.com/company",
    "https://linkedin.com/company/company",
    "https://github.com/company"
  ]
}
```

---

## WebSite Schema

For site-wide search functionality.

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Site Name",
  "url": "https://example.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

---

## Article Schema

For blog posts, news articles, and editorial content.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title (Max 110 characters)",
  "description": "Brief article summary",
  "image": [
    "https://example.com/article-image-16x9.jpg",
    "https://example.com/article-image-4x3.jpg",
    "https://example.com/article-image-1x1.jpg"
  ],
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-01-16T10:30:00+00:00",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://example.com/authors/author-name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Publisher Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/article-url"
  }
}
```

### BlogPosting (Alternative)

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Blog Post Title",
  "description": "Blog post summary",
  "articleBody": "Full article text can go here...",
  "wordCount": 1500,
  "keywords": ["keyword1", "keyword2", "keyword3"]
  // ... plus all Article fields
}
```

---

## Product Schema

For e-commerce product pages. Enables rich results with price, availability.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "image": [
    "https://example.com/product-1.jpg",
    "https://example.com/product-2.jpg"
  ],
  "sku": "SKU12345",
  "mpn": "MPN12345",
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "29.99",
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "seller": {
      "@type": "Organization",
      "name": "Seller Name"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "89"
  },
  "review": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Reviewer Name"
      },
      "datePublished": "2024-01-10",
      "reviewBody": "This product is excellent...",
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5"
      }
    }
  ]
}
```

### Availability Options
- `https://schema.org/InStock`
- `https://schema.org/OutOfStock`
- `https://schema.org/PreOrder`
- `https://schema.org/BackOrder`
- `https://schema.org/Discontinued`

---

## SoftwareApplication Schema

For apps, SaaS products, software downloads.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "App Name",
  "description": "App description",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web, iOS, Android",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "2500"
  },
  "screenshot": "https://example.com/screenshot.png",
  "featureList": "Feature 1, Feature 2, Feature 3"
}
```

### Application Categories
- `BusinessApplication`
- `DeveloperApplication`
- `EducationalApplication`
- `GameApplication`
- `HealthApplication`
- `FinanceApplication`
- `SocialNetworkingApplication`

---

## FAQPage Schema

For FAQ sections. Enables expandable Q&A in search results.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is your return policy?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We offer a 30-day money-back guarantee. Simply contact our support team to initiate a return."
      }
    },
    {
      "@type": "Question",
      "name": "How do I contact support?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You can reach our support team via email at support@example.com or through our live chat available 24/7."
      }
    },
    {
      "@type": "Question",
      "name": "Do you offer free shipping?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, we offer free shipping on all orders over $50 within the United States."
      }
    }
  ]
}
```

---

## HowTo Schema

For step-by-step guides. Shows numbered steps in search results.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Set Up Your Account",
  "description": "Complete guide to setting up your account in 5 minutes",
  "totalTime": "PT5M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": "0"
  },
  "supply": [],
  "tool": [],
  "step": [
    {
      "@type": "HowToStep",
      "name": "Create an account",
      "text": "Visit our signup page and enter your email address.",
      "url": "https://example.com/signup",
      "image": "https://example.com/step1.png"
    },
    {
      "@type": "HowToStep",
      "name": "Verify your email",
      "text": "Check your inbox and click the verification link.",
      "image": "https://example.com/step2.png"
    },
    {
      "@type": "HowToStep",
      "name": "Complete your profile",
      "text": "Add your name and profile photo.",
      "image": "https://example.com/step3.png"
    }
  ]
}
```

---

## BreadcrumbList Schema

For navigation breadcrumbs. Shows path in search results.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Products",
      "item": "https://example.com/products"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Category",
      "item": "https://example.com/products/category"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "Product Name"
    }
  ]
}
```

---

## LocalBusiness Schema

For businesses with physical locations.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Business Name",
  "description": "Business description",
  "image": "https://example.com/storefront.jpg",
  "url": "https://example.com",
  "telephone": "+1-555-555-5555",
  "email": "contact@example.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "San Francisco",
    "addressRegion": "CA",
    "postalCode": "94105",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "18:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": "Saturday",
      "opens": "10:00",
      "closes": "16:00"
    }
  ],
  "priceRange": "$$",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "156"
  }
}
```

---

## Event Schema

For events, conferences, webinars.

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Annual Developer Conference",
  "description": "Join us for our annual developer conference...",
  "image": "https://example.com/event-image.jpg",
  "startDate": "2024-06-15T09:00:00-07:00",
  "endDate": "2024-06-17T17:00:00-07:00",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Convention Center",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "456 Event Drive",
      "addressLocality": "San Francisco",
      "addressRegion": "CA",
      "postalCode": "94102",
      "addressCountry": "US"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "Company Name",
    "url": "https://example.com"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/tickets",
    "price": "299",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "validFrom": "2024-01-01T00:00:00-08:00"
  },
  "performer": {
    "@type": "Person",
    "name": "Keynote Speaker"
  }
}
```

### Virtual Event
```json
{
  "@type": "Event",
  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
  "location": {
    "@type": "VirtualLocation",
    "url": "https://example.com/webinar"
  }
}
```

---

## Combining Multiple Schemas

Use `@graph` to include multiple related schemas:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Company Name",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png"
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com",
      "name": "Site Name",
      "publisher": {
        "@id": "https://example.com/#organization"
      }
    },
    {
      "@type": "WebPage",
      "@id": "https://example.com/page/#webpage",
      "url": "https://example.com/page/",
      "name": "Page Title",
      "isPartOf": {
        "@id": "https://example.com/#website"
      }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://example.com"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Page",
          "item": "https://example.com/page/"
        }
      ]
    }
  ]
}
```

---

## Validation

Always validate structured data before deploying:

1. **Google Rich Results Test**: https://search.google.com/test/rich-results
2. **Schema.org Validator**: https://validator.schema.org/
3. **Google Search Console**: Monitor structured data in the Enhancements section

### Common Errors
- Missing required properties
- Invalid date formats (use ISO 8601)
- Invalid URLs (must be absolute)
- Missing `@context`
- Incorrect `@type` spelling
