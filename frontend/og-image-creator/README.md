# OG Image Creator Skill

Smart Open Graph image generation that studies your codebase, understands routes and brand identity, then creates contextually appropriate images using Playwright and your existing design system.

## What This Skill Does

When you ask Claude to "create og images" or "generate social cards", this skill:

1. **Analyzes your codebase** to detect framework, routes, and extract brand identity (colors, fonts, logo)
2. **Categorizes pages** by type (landing, article, product, documentation, etc.)
3. **Generates context-appropriate OG images** using your actual brand elements
4. **Provides framework-specific integration guidance** for Next.js, Astro, React, etc.

## Philosophy

**Authentic over template**: OG images should feel like a natural extension of your brand, not generic social cards. The skill studies your codebase first to understand your design language, then creates images that match.

## Quick Start

The skill provides two main scripts:

### 1. Analyze Codebase
```bash
python scripts/analyze_codebase.py /path/to/project
```

Outputs `og-analysis.json` with:
- Detected framework
- Found routes
- Extracted brand (colors, fonts, logo)
- Page categorization

### 2. Generate OG Images
```bash
python scripts/generate_og_images.py /path/to/project
```

Creates OG images in `public/og/` directory based on the analysis.

## Structure

```
og-image-creator/
├── SKILL.md                          # Main skill instructions
├── scripts/
│   ├── analyze_codebase.py          # Route discovery & brand extraction
│   └── generate_og_images.py         # OG image generation
└── references/
    ├── og-specifications.md          # OG image standards & meta tags
    ├── best-practices.md             # Design & content best practices
    └── framework-workflows.md        # Framework-specific integration
```

## Features

- **Framework-agnostic**: Works with Next.js, Astro, React, Gatsby, static HTML, and more
- **Smart route detection**: Auto-discovers routes based on framework conventions
- **Brand extraction**: Pulls colors, fonts, and logo from existing codebase
- **Context-aware layouts**: Different designs for different page types
- **Playwright-powered**: Generates high-quality 1200x630px images
- **Framework-specific guidance**: Integration examples for each framework

## Requirements

```bash
# Python
pip install playwright

# Install Chromium
playwright install chromium
```

## Skill Quality Score

**107/100** (Analyzed by skill-creator-plus)

- ✅ Strong philosophical foundation
- ✅ Comprehensive anti-pattern guidance
- ✅ Variation encouragement
- ✅ Well-organized and actionable

## When to Use

Trigger this skill when:
- "create og images"
- "generate social cards"
- "add open graph images"
- Building a new site that needs OG images
- Updating existing OG images to match rebrand

## Example Usage

```
User: "Create OG images for my Next.js site"

Claude:
1. Analyzes your Next.js project structure
2. Finds all routes in app/ or pages/ directory
3. Extracts brand colors from tailwind.config.js
4. Finds logo in public/
5. Generates contextually appropriate OG images for each route
6. Provides Next.js-specific code to integrate the images
```

## Philosophy Highlights

**Before generating, ask**:
- What is the brand identity?
- What routes exist and their purposes?
- What components/assets can be reused?
- What page types need different treatments?

**Anti-patterns to avoid**:
- Generic templates that ignore brand
- Same design for all pages
- Placeholder content
- Overcrowded layouts
- Ignoring existing components

**Variation is key**:
- Different layouts for different page types
- Contextually appropriate designs
- Avoid converging on a single "favorite" template
