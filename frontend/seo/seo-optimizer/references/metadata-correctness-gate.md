# Metadata Correctness Gate (Fast Pass)

Run this before deeper SEO changes.

## Critical correctness
- No duplicate `title`, `description`, `canonical`, or `robots` tags.
- Metadata must be deterministic (no random or unstable values).
- Canonical URL matches preferred URL; `og:url` matches canonical.
- `og:image` and `twitter:image` use absolute URLs.

## Title + description
- Every page has safe defaults for title and description.
- Titles follow a consistent format and avoid stuffing.
- Descriptions are plain text, not markdown.

## Indexing intent
- `noindex` only for private/duplicate/non-public pages.
- Robots meta matches actual access intent.

## Icons + manifest
- Include at least one favicon and (when relevant) apple-touch-icon.
- Manifest is valid and referenced if used.
- Theme-color is set intentionally.

## Structured data
- JSON-LD must match rendered content.
- Do not fabricate ratings, reviews, prices, or organization details.
